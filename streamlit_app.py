"""Interactive assignment workspace; run with streamlit run streamlit_app.py."""

from dataclasses import replace
from pathlib import Path

import altair as alt
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import pandas as pd
import streamlit as st

from radiation import Geometry, calculate_view_factors, solve_radiation

st.set_page_config(page_title="Eccentric cylinder radiation", layout="wide")
st.title("Radiation between eccentric cylinders")
st.caption("Heat and Mass Transfer · Sebastian Gajardo Lobos · Steady-state diffuse-gray enclosure")


@st.cache_data(max_entries=100, show_spinner=False)
def cached_factors(geometry, tolerance):
    return calculate_view_factors(geometry, tolerance)


def calculate(geometry, tolerance, thermal):
    return solve_radiation(cached_factors(geometry, tolerance), **thermal)


def flux_table(result):
    model = result.view_factors
    n = model.geometry.n_outer
    mean = result.metrics["mean_inner_flux_w_m2"]
    relative = (result.inner_flux - mean) / mean * 100 if result.metrics["max_deviation_percent"] is not None else np.full(len(result.inner_flux), np.nan)
    return pd.DataFrame({
        "angle_deg": np.degrees(model.angles[n:]),
        "flux_w_m2": result.inner_flux,
        "deviation_percent": relative,
    })


def geometry_chart(result, color_domain=None):
    g = result.view_factors.geometry
    arcs = []
    for i, flux in enumerate(result.inner_flux):
        angles = np.linspace(i * 2 * np.pi / g.n_inner, (i + 1) * 2 * np.pi / g.n_inner, 8)
        arcs.append(np.column_stack([g.d + g.r*np.cos(angles), g.r*np.sin(angles)]))
    theta = np.linspace(0, 2 * np.pi, 361)
    fig, ax = plt.subplots(figsize=(5.5, 5), layout="constrained")
    ax.plot(g.R*np.cos(theta), g.R*np.sin(theta), color="#64748b", linewidth=1.5)
    collection = LineCollection(arcs, cmap="inferno", linewidths=6)
    collection.set_array(result.inner_flux)
    if color_domain is not None:
        collection.set_clim(*color_domain)
    ax.add_collection(collection)
    ax.plot([0, g.d], [0, 0], ":", color="#64748b", linewidth=1)
    ax.scatter([0, g.d], [0, 0], color="#64748b", s=15)
    ax.annotate("A", (0, 0), xytext=(-12, 9), textcoords="offset points")
    ax.annotate("B", (g.d, 0), xytext=(3, 9), textcoords="offset points")
    ax.set(xlim=(-1.1*g.R, 1.1*g.R), ylim=(-1.1*g.R, 1.1*g.R), xlabel="x (m)", ylabel="y (m)")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.15)
    fig.colorbar(collection, ax=ax, shrink=0.75, label="Net outward flux (W/m²)")
    return fig


def profile_chart(frame, group=None):
    chart = alt.Chart(frame).mark_line(point=True).encode(
        x=alt.X("angle_deg:Q", title="Inner-cylinder angle (degrees)", scale=alt.Scale(domain=[0, 360])),
        y=alt.Y("flux_w_m2:Q", title="Net outward flux (W/m²)", scale=alt.Scale(zero=False)),
        tooltip=[alt.Tooltip("angle_deg:Q", format=".1f"), alt.Tooltip("flux_w_m2:Q", format=".3f")],
    )
    if group:
        chart = chart.encode(color=alt.Color(f"{group}:N", title="Case"))
    return chart.properties(height=360)


def show_result(result, color_domain=None):
    metrics = result.metrics
    with st.container(horizontal=True):
        st.metric("Mean inner flux", f"{metrics['mean_inner_flux_w_m2']:.2f} W/m²", border=True)
        deviation = metrics["max_deviation_percent"]
        st.metric("Maximum deviation from mean", "Undefined" if deviation is None else f"{deviation:.3f}%", border=True)
        st.metric("Heat from B per length", f"{metrics['heat_inner_w_m']:.2f} W/m", border=True)
    left, right = st.columns([1, 1.2])
    with left:
        fig = geometry_chart(result, color_domain)
        st.pyplot(fig, width="stretch")
        plt.close(fig)
    with right:
        st.altair_chart(profile_chart(flux_table(result)), width="stretch")
        st.caption("Each plotted flux is a segment average. The connecting line guides the eye. Angle 0° faces the narrowest gap; 180° faces the widest.")
    g = result.view_factors.geometry
    st.caption(f"Minimum gap: {g.R-g.r-g.d:.3f} m · Maximum gap: {g.R-g.r+g.d:.3f} m · Offset d: {g.d:.3f} m")


def summary_row(result):
    g = result.view_factors.geometry
    return {"n_outer": g.n_outer, "n_inner": g.n_inner, "r_m": g.r, "d_m": g.d,
            "integration_tolerance": result.view_factors.integration_tolerance,
            **result.metrics, **result.view_factors.diagnostics}


with st.sidebar:
    st.subheader("Physical parameters")
    st.caption("Outer radius 1 m · Outer temperature 30 °C")
    with st.form("parameters"):
        radius = st.slider("Inner radius r (m)", 0.1, 0.8, 0.4, 0.05)
        eccentricity = st.slider("Normalized eccentricity e", 0.0, 0.95, 0.5, 0.05,
                                 help="e = d/(R-r). Zero is concentric; one is contact.")
        temperature = st.slider("Inner temperature (°C)", 31.0, 600.0, 200.0, 1.0)
        epsilon_a = st.slider("Outer emissivity", 0.05, 1.0, 0.6, 0.05)
        epsilon_b = st.slider("Inner emissivity", 0.05, 1.0, 0.8, 0.05)
        n_outer = st.select_slider("Outer segments", [8, 12, 24, 48, 96, 192], value=24)
        n_inner = st.select_slider("Inner segments", [8, 16, 32, 64, 128], value=16)
        tolerance = st.select_slider("Integration tolerance", [1e-6, 1e-7, 1e-8, 1e-9], value=1e-8,
                                     format_func=lambda x: f"{x:.0e}")
        st.form_submit_button("Calculate", type="primary", width="stretch")
    st.caption("Working values are provisional. Surface segment convergence has not yet been established.")

g = Geometry(r=radius, d=eccentricity * (1-radius), n_outer=n_outer, n_inner=n_inner)
thermal = {"temperature_outer_k": 303.15, "temperature_inner_k": temperature + 273.15,
           "emissivity_outer": epsilon_a, "emissivity_inner": epsilon_b}
signature = (g, tolerance, tuple(thermal.values()))
view = st.segmented_control("Assignment workspace", ["Simulation", "Discretization (a)", "Parameters (b)", "Model and plan (c)"], default="Simulation")

if view == "Model and plan (c)":
    st.info("Analytical comparisons for part (c) are optional and deferred. Numerical consistency checks remain part of the solver.")
    document = st.selectbox("Document", ["Implementation plan", "Thermodynamic model"])
    name = "PLAN.md" if document == "Implementation plan" else "MODEL.md"
    st.markdown((Path(__file__).parent / "docs" / name).read_text(encoding="utf-8"))
    st.stop()

if view == "Simulation":
    with st.spinner("Integrating view factors and solving radiosity…"):
        result = calculate(g, tolerance, thermal)
    show_result(result)
    with st.expander("Numerical checks and exports"):
        st.json({**result.view_factors.diagnostics, "energy_imbalance_w_m": result.metrics["energy_imbalance_w_m"],
                 "energy_imbalance_relative": result.metrics["energy_imbalance_relative"]})
        relative_error = result.metrics["energy_imbalance_relative"]
        if result.view_factors.diagnostics["reciprocity_relative_max"] > 1e-5 or (relative_error is not None and relative_error > 1e-5):
            st.warning("Numerical residuals are elevated. Tighten integration tolerance before interpreting small flux differences.")
        export = flux_table(result).assign(**summary_row(result), **thermal)
        st.download_button("Download inner flux and parameters (CSV)", export.to_csv(index=False), "inner_flux.csv", "text/csv")
        st.download_button("Download view-factor matrix (CSV)", pd.DataFrame(result.view_factors.factors).to_csv(index=False), "view_factors.csv", "text/csv")

elif view == "Discretization (a)":
    st.subheader("Hold physics fixed and refine the numerical model")
    st.write("Refine the segments and integration tolerance separately. A small energy residual alone does not establish surface discretization convergence.")
    mode = st.selectbox("Refinement", ["Both surfaces", "Outer surface only", "Inner surface only", "Integration tolerance only"])
    levels = st.slider("Refinement levels", 2, 4, 3)
    study_signature = (signature, mode, levels)
    if st.button("Run convergence study", type="primary"):
        records, profiles = [], []
        previous = None
        progress = st.progress(0, text="Calculating refinement cases")
        for index in range(levels):
            if mode == "Integration tolerance only":
                case_g, case_tol = g, 10.0 ** (-6-index)
            else:
                case_g = replace(g, n_outer=g.n_outer * (2**index if mode != "Inner surface only" else 1),
                                 n_inner=g.n_inner * (2**index if mode != "Outer surface only" else 1))
                case_tol = tolerance
            if case_g.n_outer + case_g.n_inner > 640:
                st.error("This refinement exceeds the prototype's 640-segment limit. Reduce initial counts or refinement levels.")
                st.stop()
            result = calculate(case_g, case_tol, thermal)
            row = summary_row(result)
            frame = flux_table(result)
            shared = np.linspace(0, 360, 720, endpoint=False)
            sampled = np.interp(shared, frame.angle_deg, frame.flux_w_m2, period=360)
            if previous is not None:
                row["profile_change_percent"] = float(100*np.max(np.abs(sampled-previous)) / abs(result.metrics["mean_inner_flux_w_m2"]))
                row["deviation_change_pp"] = abs(result.metrics["max_deviation_percent"] - records[-1]["max_deviation_percent"])
            records.append(row)
            profiles.append(frame.assign(case=f"{case_g.n_outer}/{case_g.n_inner}, tol {case_tol:.0e}"))
            previous = sampled
            progress.progress((index+1)/levels)
        st.session_state.convergence = (study_signature, pd.DataFrame(records), pd.concat(profiles, ignore_index=True))
        progress.empty()
    saved = st.session_state.get("convergence")
    if saved and saved[0] == study_signature:
        table, profiles = saved[1:]
        st.altair_chart(profile_chart(profiles, "case"), width="stretch")
        st.dataframe(table, hide_index=True)
        st.caption("Profile changes compare periodic interpolation of segment averages on a shared angular grid. The first case has no predecessor. Final discretization must be chosen after reviewing successive changes.")
        st.download_button("Download convergence table", table.assign(**thermal).to_csv(index=False), "convergence.csv", "text/csv")
        st.download_button("Download convergence profiles", profiles.to_csv(index=False), "convergence_profiles.csv", "text/csv")

elif view == "Parameters (b)":
    st.subheader("Change one physical parameter")
    parameter = st.selectbox("Sweep", ["Normalized eccentricity", "Inner radius at fixed d", "Inner temperature"])
    st.caption("Uses the current surface segment counts. Establish their convergence in part (a) before using these results in the final report.")
    sweep_signature = (signature, parameter)
    if st.button("Run parameter study", type="primary"):
        records, profiles, cases = [], [], []
        values = np.linspace(0, 0.9, 7) if parameter == "Normalized eccentricity" else (
            np.linspace(0.2, 0.6, 5) if parameter == "Inner radius at fixed d" else np.linspace(60, 400, 6))
        if parameter == "Inner radius at fixed d" and np.any(values + g.d >= g.R):
            st.error("Some radius cases would touch or intersect the outer cylinder at the current fixed d. Reduce eccentricity before running this sweep.")
            st.stop()
        progress = st.progress(0, text="Calculating parameter cases")
        for index, value in enumerate(values):
            case_g, case_thermal = g, thermal.copy()
            if parameter == "Normalized eccentricity":
                case_g = replace(g, d=float(value) * (g.R-g.r))
            elif parameter == "Inner radius at fixed d":
                case_g = replace(g, r=float(value))
            else:
                case_thermal["temperature_inner_k"] = float(value) + 273.15
            result = calculate(case_g, tolerance, case_thermal)
            records.append({"sweep_value": value, **summary_row(result), **case_thermal})
            profiles.append(flux_table(result).assign(case=f"{value:.3g}"))
            cases.append(result)
            progress.progress((index+1)/len(values))
        st.session_state.sweep = (sweep_signature, parameter, values, pd.DataFrame(records), pd.concat(profiles, ignore_index=True), cases)
        st.session_state.playback_frame = 0
        progress.empty()
    saved = st.session_state.get("sweep")
    if saved and saved[0] == sweep_signature:
        _, parameter, values, table, profiles, cases = saved
        st.altair_chart(profile_chart(profiles, "case"), width="stretch")
        st.altair_chart(alt.Chart(table).mark_line(point=True).encode(
            x=alt.X("sweep_value:Q", title=parameter),
            y=alt.Y("max_deviation_percent:Q", title="Maximum deviation (%)", scale=alt.Scale(zero=False)),
            tooltip=["sweep_value", "max_deviation_percent"],
        ), width="stretch")
        st.dataframe(table, hide_index=True)
        st.download_button("Download parameter table", table.to_csv(index=False), "parameter_study.csv", "text/csv")
        st.download_button("Download angular profiles", profiles.to_csv(index=False), "parameter_profiles.csv", "text/csv")
        st.subheader("Play through steady-state cases")
        st.caption("Playback changes the prescribed parameter. It does not represent elapsed physical time. The color scale is fixed across these frames.")

        @st.fragment(run_every=1.0)
        def playback():
            playing = st.toggle("Play", key="playback_playing")
            if playing:
                st.session_state.playback_frame = (st.session_state.get("playback_frame", 0)+1) % len(cases)
            index = st.slider("Case", 0, len(cases)-1, key="playback_frame")
            st.write(f"{parameter}: **{values[index]:.3g}**")
            color_domain = [min(float(x.inner_flux.min()) for x in cases), max(float(x.inner_flux.max()) for x in cases)]
            show_result(cases[index], color_domain)

        playback()
