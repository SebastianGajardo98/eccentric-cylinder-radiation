"""Interactive assignment workspace; run with streamlit run streamlit_app.py."""

from dataclasses import replace
from pathlib import Path
import json

import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from radiation import Geometry, calculate_view_factors, solve_radiation
from flux_plot import geometry_chart, arrow_samples

selection_path = Path(__file__).parent / "results" / "discretization" / "selected.json"
selection = json.loads(selection_path.read_text(encoding="utf-8")) if selection_path.exists() else None
recommended_outer = selection["n_outer"] if selection else 96
recommended_inner = selection["n_inner"] if selection else 64

st.set_page_config(page_title="Eccentric cylinder radiation", layout="wide", initial_sidebar_state="expanded")
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


def profile_chart(frame, group=None, quantity="flux_w_m2"):
    label = "Deviation from mean (%)" if quantity == "deviation_percent" else "Net outward flux (W/m²)"
    chart = alt.Chart(frame).mark_line(point=True).encode(
        x=alt.X("angle_deg:Q", title="Inner-cylinder angle (degrees)", scale=alt.Scale(domain=[0, 360])),
        y=alt.Y(f"{quantity}:Q", title=label, scale=alt.Scale(zero=False)),
        tooltip=[alt.Tooltip("angle_deg:Q", format=".1f"), alt.Tooltip(f"{quantity}:Q", title=label, format=".3f")],
    )
    if group:
        chart = chart.encode(color=alt.Color(f"{group}:N", title="Case"))
    return chart.properties(height=360)


def show_flux_comparison(result, reference_result, key):
    """Compare actual flux on an explicit axis independent of wall clearance."""
    _, values = arrow_samples(result, "net", 8)
    directions = ["Right", "Upper right", "Top", "Upper left", "Left", "Lower left", "Bottom", "Lower right"]
    frame = pd.DataFrame({"direction": directions, "flux_w_m2": values})
    reference = None if reference_result is None else reference_result.metrics["mean_inner_flux_w_m2"]
    if reference is not None:
        frame["centered_flux_w_m2"] = reference
        frame["change_w_m2"] = values-reference
    st.subheader("Compare flux with a fixed scale")
    with st.container(horizontal=True):
        for index in [0, 4]:
            change = None if reference is None else float(values[index]-reference)
            if change is not None and abs(change) < 1e-6:
                change = 0.0
            st.metric(f"{directions[index]} side of B", f"{values[index]:.2f} W/m²",
                      delta=None if change is None else f"{change:+.2f} W/m² vs centered",
                      border=True)
    required = max(float(values.max()), 0.0 if reference is None else reference)
    scale_key = f"{key}_comparison_axis_max"
    if scale_key not in st.session_state:
        st.session_state[scale_key] = 3000.0
    current_limit = st.session_state[scale_key] or 3000.0
    with st.expander("Flux comparison scale", expanded=required > current_limit):
        if st.button("Fit comparison scale to this case", key=f"{key}_fit_flux_axis"):
            st.session_state[scale_key] = max(100.0, float(100*np.ceil(1.1*required/100)))
        axis_max = st.number_input("Flux axis maximum (W/m²)", min_value=1.0,
                                   value=None, step=100.0, key=scale_key)
        st.caption("This axis stays fixed when parameters change. Fit it or enter a new maximum explicitly to change the display range.")
    if axis_max is None:
        st.info("Enter a positive flux axis maximum to display the comparison chart.")
        return
    if required > axis_max:
        st.warning("The calculated flux exceeds the selected comparison range. Increase the flux axis maximum or press Fit comparison scale to this case.")
    else:
        base = alt.Chart(frame).encode(
            y=alt.Y("direction:N", sort=directions, title="Position on B"),
            x=alt.X("flux_w_m2:Q", title="Net outward heat flux (W/m²)",
                    scale=alt.Scale(domain=[0, axis_max], nice=False)),
            tooltip=[alt.Tooltip("direction:N", title="Direction"),
                     alt.Tooltip("flux_w_m2:Q", title="Actual q (W/m²)", format=".2f")],
        )
        chart = base.mark_bar(color="#c65a06", size=18)
        if reference is not None:
            ticks = alt.Chart(frame).mark_tick(color="#334155", thickness=3, size=26).encode(
                x=alt.X("centered_flux_w_m2:Q", scale=alt.Scale(domain=[0, axis_max], nice=False)),
                y=alt.Y("direction:N", sort=directions),
                tooltip=[alt.Tooltip("centered_flux_w_m2:Q", title="Centered reference (W/m²)", format=".2f")],
            )
            chart = chart+ticks
        st.altair_chart(chart.properties(height=300), width="stretch")
        st.caption(f"One unchanged scale: 0–{axis_max:,.0f} W/m². Bar length measures flux, independent of the space between cylinders.")
    if reference is not None:
        st.caption(f"Dark marks: numerically calculated centered reference, q = {reference:.2f} W/m², with the same radius, temperatures, emissivities and discretization. Positive changes mean greater flux than when centered.")


def show_result(result, color_domain=None, scale_results=None, key="simulation", reference_result=None):
    metrics = result.metrics
    with st.container(horizontal=True):
        st.metric("Mean inner flux", f"{metrics['mean_inner_flux_w_m2']:.2f} W/m²", border=True)
        deviation = metrics["max_deviation_percent"]
        st.metric("Maximum deviation from mean", "Undefined" if deviation is None else f"{deviation:.3f}%", border=True)
        st.metric("Heat from B per length", f"{metrics['heat_inner_w_m']:.2f} W/m", border=True)
    st.subheader("Cross-section: cylinder B inside cylinder A")
    with st.expander("Flux arrow display", expanded=False):
        fields = st.columns(2)
        representation_label = fields[0].selectbox("Arrows represent", ["Net heat flux", "Deviation from mean"], key=f"{key}_arrow_mode")
        arrow_count = fields[1].select_slider("Visible arrows (display only)", [4, 8, 12, 16, 24, 32], value=8, key=f"{key}_eight_arrow_count")
        contrast = st.slider("Arrow length contrast (1 = proportional to q)", 1, 10, 1,
                             key=f"{key}_physical_length_contrast", disabled=representation_label != "Net heat flux",
                             help="Values above 1 visually emphasize differences. Colors and the angular chart still show the actual calculated flux.")
        reference = st.toggle("Show mean-flux tip guide (not a cylinder)", value=False,
                              key=f"{key}_mean_tip_guide", disabled=representation_label != "Net heat flux")
    representation = "net" if representation_label == "Net heat flux" else "deviation"
    if representation == "net" and contrast > 1:
        st.caption(f"Lengths emphasize differences (contrast {contrast}); colors and labels show the calculated flux. Set contrast to 1 for proportional lengths.")
    if scale_results is None:
        st.info("Geometry arrows resize to fit the gap. Their screen lengths cannot be compared between positions. Use the fixed-scale flux comparison below.")
    fig = geometry_chart(result, color_domain, representation=representation,
                         detail=False, arrow_count=arrow_count,
                         uniform_reference=reference, scale_results=scale_results,
                         length_contrast=contrast)
    st.pyplot(fig, width="stretch")
    plt.close(fig)
    st.caption("The default eight arrows show the four axes and four diagonals of B. Values are interpolated between segment averages for display; adding arrows does not refine the numerical model.")
    g = result.view_factors.geometry
    st.caption(f"Actual geometry: R = {g.R:.3f} m, r = {g.r:.3f} m, center distance d = {g.d:.3f} m, B position x = {g.center_x:+.3f} m. Both circles share the same length scale. The dotted line joins their centers; the space between the walls is a vacuum.")
    if representation == "net":
        st.write(f"**Flux on B:** minimum **{metrics['min_inner_flux_w_m2']:.2f} W/m²**, maximum **{metrics['max_inner_flux_w_m2']:.2f} W/m²**.")
    show_flux_comparison(result, reference_result, key)
    with st.expander("Angular flux profile — quantify the nonuniformity on B", expanded=True):
        quantity = "flux_w_m2" if representation == "net" else "deviation_percent"
        chart = profile_chart(flux_table(result), quantity=quantity)
        baseline = metrics["mean_inner_flux_w_m2"] if representation == "net" else 0.0
        rule = alt.Chart(pd.DataFrame({quantity: [baseline]})).mark_rule(strokeDash=[5, 4], color="#64748b").encode(y=f"{quantity}:Q")
        st.altair_chart(chart+rule, width="stretch")
        st.caption("Each plotted flux is a segment average. The connecting line guides the eye. Angles stay fixed: 0° right, 90° top, 180° left, 270° bottom.")
    if representation == "net":
        st.caption("Arrows show net surface heat flux normal to B. At contrast 1 their lengths are proportional to q. Colors and the profile reveal small variations without altering the geometry.")
        if reference:
            st.caption("The dashed contour is only a guide to equal arrow lengths at the mean flux; it is not a cylinder wall.")
    else:
        st.caption("Deviation arrows show (local flux − mean flux) / mean flux: outward is above average, inward is below average. An inward deviation arrow does not imply that the net heat flows inward.")
    if scale_results is None:
        st.caption("Geometry arrows share one proportional scale within this frame. That fitted scale changes with clearance; use the fixed-scale comparison for changes between positions.")
    elif representation == "net" and contrast > 1:
        st.caption("Playback shares a drawing scale, but contrast emphasizes variation around each case's own mean. Compare colors and numerical flux values between cases; use contrast 1 for proportional length comparisons.")
    else:
        st.caption("All playback cases share one arrow scale and the fixed outer-cylinder frame, so arrow lengths and cylinder positions can be compared across frames.")
    st.caption(f"Minimum gap: {g.R-g.r-g.d:.3f} m · Maximum gap: {g.R-g.r+g.d:.3f} m · Offset d: {g.d:.3f} m")


def summary_row(result):
    g = result.view_factors.geometry
    return {"n_outer": g.n_outer, "n_inner": g.n_inner, "r_m": g.r, "d_m": g.d,
            "center_b_x_m": g.center_x, "position_side": g.side,
            "integration_tolerance": result.view_factors.integration_tolerance,
            **result.metrics, **result.view_factors.diagnostics}


with st.sidebar:
    st.subheader("Physical parameters")
    st.caption("Outer radius 1 m · Outer temperature 30 °C")
    automatic = st.toggle("Update automatically", value=True,
                          help="Update after each control change. Turn off to batch changes with Calculate.")
    quality = st.segmented_control("Resolution", ["Preview", "Study", "Custom"], default="Preview")
    controls = st.container() if automatic else st.form("parameters")
    with controls:
        radius = st.slider("Inner radius r (m)", 0.1, 0.8, 0.4, 0.05, key="radius")
        if "horizontal_position" not in st.session_state:
            st.session_state.horizontal_position = st.session_state.get("eccentricity", 0.5)
        position = st.slider("Horizontal position of B", -0.95, 0.95, step=0.05,
                             help="Negative = left, zero = centered, positive = right. This is x_B/(R-r); absolute value 1 would mean contact.",
                             key="horizontal_position")
        st.caption(f"Left ← 0 → Right · Normalized eccentricity e = {abs(position):.2f}")
        temperature = st.slider("Inner temperature (°C)", 31.0, 600.0, 200.0, 1.0, key="temperature")
        epsilon_a = st.slider("Outer emissivity", 0.05, 1.0, 0.6, 0.05, key="epsilon_a")
        epsilon_b = st.slider("Inner emissivity", 0.05, 1.0, 0.8, 0.05, key="epsilon_b")
        if quality == "Custom":
            n_outer = int(st.number_input("Outer segments", min_value=4, max_value=512, value=recommended_outer, step=1, key="custom_outer"))
            n_inner = int(st.number_input("Inner segments", min_value=4, max_value=512, value=recommended_inner, step=1, key="custom_inner"))
        elif quality == "Study":
            n_outer, n_inner = recommended_outer, recommended_inner
        else:
            n_outer, n_inner = 24, 16
        tolerance = st.select_slider("Integration tolerance", [1e-6, 1e-7, 1e-8, 1e-9], value=1e-8,
                                     format_func=lambda x: f"{x:.0e}")
        if not automatic:
            st.form_submit_button("Calculate", type="primary", width="stretch")
    st.caption(f"{n_outer} outer / {n_inner} inner segments. Discretization is the number of arcs used to resolve each surface.")
    if quality == "Preview":
        st.caption("Preview favors speed. Choose Study for the recommended discretization, or Custom to set both counts independently.")
    elif quality == "Study":
        st.caption("Recommended for the documented study cases; other parameter combinations may need their own convergence check." if selection else "Study discretization is currently being reviewed.")

g = Geometry(r=radius, d=abs(position) * (1-radius),
             side="left" if position < 0 else "right", n_outer=n_outer, n_inner=n_inner)
thermal = {"temperature_outer_k": 303.15, "temperature_inner_k": temperature + 273.15,
           "emissivity_outer": epsilon_a, "emissivity_inner": epsilon_b}
signature = (g, tolerance, tuple(thermal.values()))
view = st.segmented_control("Assignment workspace", ["Simulation", "Discretization (a)", "Parameters (b)", "Model and plan (c)"], default="Simulation")

if view == "Model and plan (c)":
    st.info("Analytical comparisons for part (c) are optional and deferred. Numerical consistency checks remain part of the solver.")
    documents = {"Implementation plan": "PLAN.md", "Thermodynamic model": "MODEL.md", "Reading the flux arrows": "FLUX_ARROWS.md"}
    if selection:
        documents["Discretization selection"] = "DISCRETIZATION.md"
    document = st.selectbox("Document", list(documents))
    name = documents[document]
    if name == "DISCRETIZATION.md":
        st.image(str(selection_path.parent / "discretization_selection.png"), caption="Independent refinement and selected-mesh qualification", width="stretch")
    st.markdown((Path(__file__).parent / "docs" / name).read_text(encoding="utf-8"))
    st.stop()

if view == "Simulation":
    with st.spinner("Integrating view factors and solving radiosity…"):
        result = calculate(g, tolerance, thermal)
        centered = calculate(replace(g, d=0.0, side="right"), tolerance, thermal)
    show_result(result, reference_result=centered)
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
    if selection:
        st.info(f"Study recommendation: {recommended_outer} outer / {recommended_inner} inner segments, tolerance {selection['integration_tolerance']:.0e}. The selection report is available in Model and plan (c). You can still choose any custom counts.")
        with st.expander("Completed mesh-selection evidence"):
            st.image(str(selection_path.parent / "discretization_selection.png"), width="stretch")
            evidence = pd.read_csv(selection_path.parent / f"qualification_{recommended_outer}_{recommended_inner}_comparisons.csv")
            st.dataframe(evidence, hide_index=True)
            st.download_button("Download completed mesh qualification", evidence.to_csv(index=False), "mesh_qualification.csv", "text/csv")
    mode = st.selectbox("Refinement", ["Both surfaces", "Outer surface only", "Inner surface only", "Integration tolerance only"])
    levels = st.slider("Refinement levels", 2, 4, 2)
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
            shared = np.linspace(0, 360, 4096, endpoint=False)
            sampled = np.interp(shared, frame.angle_deg, frame.flux_w_m2, period=360)
            if previous is not None:
                row["profile_change_percent"] = float(100*np.max(np.abs(sampled-previous)) / abs(result.metrics["mean_inner_flux_w_m2"]))
                row["deviation_change_pp"] = abs(result.metrics["max_deviation_percent"] - records[-1]["max_deviation_percent"])
                row["peak_to_peak_change_pp"] = abs(result.metrics["peak_to_peak_percent"] - records[-1]["peak_to_peak_percent"])
                row["meets_change_criteria"] = row["profile_change_percent"] < 0.5 and row["deviation_change_pp"] < 0.1 and row["peak_to_peak_change_pp"] < 0.1
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
            show_result(cases[index], color_domain, scale_results=cases, key="playback")

        playback()
