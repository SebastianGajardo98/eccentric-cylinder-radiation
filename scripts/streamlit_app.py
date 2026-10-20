"""Numerical assignment report and a separate interactive steady-state explorer."""

from dataclasses import asdict
import hashlib
import json

import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from app_charts import angular_chart
from assignment_content import TITLE
from flux_plot import arrow_samples, geometry_chart
from radiation import Geometry, ViewFactors, calculate_view_factors, solve_radiation
from study_data import ROOT, load_studies, source_hash
import report_ui


def select_section(value):
    st.session_state.report_section = value

st.set_page_config(page_title=TITLE, layout="wide", initial_sidebar_state="expanded")
st.title(TITLE)
st.caption("Sebastian Alberto Gajardo Lobos · Heat and Mass Transfer · Numerical view-factor analysis")

# One fixed, fast resolution for the interactive page: about 1.5 s per new geometry on
# a desktop PC. Its D_max is about 0.1 percentage points below the report mesh at the
# starting arrangement and about 1.1 below at the smallest report gap (e = 0.9).
SIMULATION_MESH = (24, 32)
SIMULATION_TOLERANCE = 1e-6
SECTIONS = ["Assignment", "(a) Model", "(a) Discretization", "(b) Parameter studies", "(c) Discussion and conclusions", "Interactive simulation"]
if st.session_state.get("report_section") == "Overview":
    st.session_state.report_section = "Assignment"
elif st.session_state.get("report_section") == "Conclusions and code":
    st.session_state.report_section = "(c) Discussion and conclusions"
elif st.session_state.get("report_section") == "Model":
    st.session_state.report_section = "(a) Model"
with st.sidebar:
    st.subheader("Assignment sections")
    section = st.radio("Navigation", SECTIONS, key="report_section", label_visibility="collapsed")

try:
    selection, cases, profiles, manifest = load_studies()
except (FileNotFoundError, ValueError) as error:
    st.error(f"The completed report data need regeneration: {error}")
    st.code("python scripts/run_assignment.py")
    st.stop()


@st.cache_data(max_entries=80, show_spinner=False)
def cached_factors(geometry, tolerance, fingerprint):
    key = json.dumps([asdict(geometry), tolerance, fingerprint], sort_keys=True)
    cache = ROOT / "tmp" / "view_factor_cache" / (hashlib.sha256(key.encode()).hexdigest()+".npz")
    if cache.exists():
        with np.load(cache) as stored:
            return ViewFactors(geometry, stored["factors"], stored["areas"], stored["angles"], tolerance, float(stored["error"]))
    return calculate_view_factors(geometry, tolerance)


def directional_comparison(result):
    _, values = arrow_samples(result, "net", 8)
    mean = result.metrics["mean_inner_flux_w_m2"]
    directions = ["Right", "Upper right", "Top", "Upper left", "Left", "Lower left", "Bottom", "Lower right"]
    with st.container(horizontal=True):
        for index in (0, 4):
            delta = 100*(values[index]-mean)/abs(mean)
            if abs(delta) < 1e-7:
                delta = 0.0
            st.metric(f"{directions[index]} side", f"{values[index]:.2f} W/m²", delta=f"{delta:+.2f}% vs current mean", border=True)
    if "sim_comparison_axis" not in st.session_state:
        st.session_state.sim_comparison_axis = st.session_state.get("comparison_limit", 3000.0)
    required = max(float(values.max()), mean)
    if st.button("Fit comparison axis", key="fit_sim_axis"):
        st.session_state.sim_comparison_axis = max(100.0, float(100*np.ceil(1.1*required/100)))
    limit = st.number_input("Flux axis maximum (W/m²)", min_value=1.0, value=None, step=100.0, key="sim_comparison_axis")
    st.session_state.comparison_limit = limit
    if limit is None:
        st.info("Enter a positive maximum to display the comparison.")
        return
    if required > limit:
        st.info("The selected axis is too small. Increase its maximum or press Fit comparison axis; the bars are not silently rescaled or truncated.")
        return
    frame = pd.DataFrame({"direction": directions, "flux_w_m2": values, "mean_flux_w_m2": mean})
    bars = alt.Chart(frame).mark_bar(color="#c65a06", size=17).encode(
        x=alt.X("flux_w_m2:Q", title="Net outward flux (W/m²)", scale=alt.Scale(domain=[0, limit], nice=False)),
        y=alt.Y("direction:N", sort=directions, title="Position on B"),
        tooltip=[alt.Tooltip("direction:N"), alt.Tooltip("flux_w_m2:Q", format=".3f")])
    ticks = alt.Chart(frame).mark_tick(color="#64748b", size=26, thickness=3).encode(
        x="mean_flux_w_m2:Q", y=alt.Y("direction:N", sort=directions))
    st.altair_chart((bars+ticks).properties(height=280), width="stretch")
    st.caption(f"Fixed axis: 0–{limit:,.0f} W/m². Dark ticks show the current surface mean, {mean:.2f} W/m². Above/below this mean is the nonuniformity requested in the assignment.")


if section == "Assignment":
    report_ui.assignment_page()
elif section == "(a) Model":
    report_ui.model_page()
elif section == "(a) Discretization":
    report_ui.discretization_page(selection, cases)
elif section == "(b) Parameter studies":
    report_ui.parameters_page(cases, profiles)
elif section == "(c) Discussion and conclusions":
    report_ui.conclusions_page(selection, cases, manifest)
else:
    st.header("Interactive steady-state simulation")
    st.write("Explore how geometry and prescribed temperature change the flux on B. The completed report results in (a) and (b) keep their documented fixed parameters.")
    settings = st.session_state.get("sim_inputs", {"r": .4, "position": .5, "temperature": 200.0, "epsilon_a": .6, "epsilon_b": .8})
    with st.sidebar:
        st.subheader("Physical parameters")
        radius = st.slider("Inner radius r (m)", .1, .8, settings["r"], .05, key="sim_radius")
        position = st.slider("Move B left / right", -.95, .95, settings["position"], .05, key="sim_position", help="Negative is left, zero is concentric, positive is right. The value is x_B/(R-r); d is always the positive center distance.")
        st.caption(f"d = {abs(position)*(1-radius):.3f} m · e = {abs(position):.2f}")
        temperature = st.slider("Inner temperature T_B (°C)", 31.0, 600.0, settings["temperature"], 1.0, key="sim_temperature")
        epsilon_a = st.slider("Outer emissivity ε_A", .05, 1.0, settings["epsilon_a"], .05, key="sim_epsilon_a")
        epsilon_b = st.slider("Inner emissivity ε_B", .05, 1.0, settings["epsilon_b"], .05, key="sim_epsilon_b")
    st.session_state.sim_inputs = {"r": radius, "position": position, "temperature": temperature, "epsilon_a": epsilon_a, "epsilon_b": epsilon_b}
    (na, nb), tolerance = SIMULATION_MESH, SIMULATION_TOLERANCE
    geometry = Geometry(r=radius, d=abs(position)*(1-radius), side="left" if position < 0 else "right", n_outer=na, n_inner=nb)
    thermal = {"temperature_outer_k": 303.15, "temperature_inner_k": temperature+273.15, "emissivity_outer": epsilon_a, "emissivity_inner": epsilon_b}
    with st.spinner("Calculating circular-arc view factors and surface flux…"):
        factors = cached_factors(geometry, tolerance, source_hash())
        result = solve_radiation(factors, **thermal)
    report_ui.source_note("Calculates the current view factors, radiosity and flux; equations (1)–(13) are explained in (a) Model", "radiation.py")
    metrics = result.metrics
    with st.container(horizontal=True):
        st.metric("Mean q on B", f"{metrics['mean_inner_flux_w_m2']:.2f} W/m²", border=True)
        st.metric("D_max", f"{metrics['max_deviation_percent']:.3f}%", border=True)
        st.metric("D_pp", f"{metrics['peak_to_peak_percent']:.3f}%", border=True)
    st.caption(f"Calculated with {na} equal segments on A and {nb} on B so that each change takes only a moment. The report tables use the finer, qualified {selection['n_outer']}/{selection['n_inner']} mesh, so D_max and D_pp here are slightly lower: by about 0.1 percentage points at the starting arrangement and up to about one point at the smallest gaps.")
    figure = geometry_chart(result, representation="net", detail=False, arrow_count=8, uniform_reference=False, length_contrast=1)
    st.pyplot(figure, width="stretch")
    plt.close(figure)
    st.caption(f"A and B share the same physical scale. Center distance d = {geometry.d:.3f} m; B center x = {geometry.center_x:+.3f} m. Minimum gap = {1-radius-geometry.d:.3f} m. The eight outward arrows interpolate local net flux between segment averages; they are not individual radiation rays.")
    st.caption("Arrow lengths fit the available gap and therefore rescale between positions. Use numerical values and the fixed-scale comparison below for changes between positions.")
    report_ui.source_note("Interpolates the eight directional arrow values and draws the geometry", "flux_plot.py")
    frame = pd.DataFrame({"angle_deg": np.degrees(factors.angles[na:]), "flux_w_m2": result.inner_flux,
                          "deviation_percent": 100*(result.inner_flux-metrics["mean_inner_flux_w_m2"])/abs(metrics["mean_inner_flux_w_m2"])})
    st.subheader("Deviation from uniform surface flux")
    quantity = st.segmented_control("Angular profile", ["Deviation from mean (%)", "Net flux (W/m²)"], default="Deviation from mean (%)", required=True, key="sim_profile_quantity")
    field = "deviation_percent" if quantity.startswith("Deviation") else "flux_w_m2"
    chart = angular_chart(frame, field)
    baseline = 0.0 if field == "deviation_percent" else metrics["mean_inner_flux_w_m2"]
    rule = alt.Chart(pd.DataFrame({field: [baseline]})).mark_rule(strokeDash=[5, 4], color="#64748b").encode(y=f"{field}:Q")
    st.altair_chart(chart+rule, width="stretch")
    st.caption("0° right · 90° top · 180° left · 270° bottom. Each calculated value is a segment average; connecting lines guide the eye.")
    report_ui.source_note("Displays the calculated angular profiles; the 4096-angle setting is used only in the report's refinement comparisons", "app_charts.py", "streamlit_app.py")
    with st.expander("Compare eight directions on a fixed flux scale"):
        directional_comparison(result)
    with st.expander("Numerical checks and current simulation data"):
        st.write(f"Q′_B = {metrics['heat_inner_w_m']:.3f} W/m; Q′_A = {metrics['heat_outer_w_m']:.3f} W/m.")
        st.json({**factors.diagnostics, "relative_energy_imbalance": metrics["energy_imbalance_relative"]})
        if factors.diagnostics["reciprocity_relative_max"] > 1e-5 or (metrics["energy_imbalance_relative"] or 0) > 1e-5:
            st.warning("Numerical residuals are elevated for this arrangement; treat small flux differences with caution.")
        export = pd.DataFrame({"angle on B (deg)": frame.angle_deg, "q_B (W/m2)": frame.flux_w_m2.round(6),
                               "deviation from mean (%)": frame.deviation_percent.round(9)+0.0})
        export = export.assign(**{"r (m)": radius, "d (m)": round(geometry.d, 6), "x_B (m)": round(geometry.center_x, 6),
                                  "T_A (C)": 30.0, "T_B (C)": temperature, "eps_A": epsilon_a, "eps_B": epsilon_b, "N_A": na, "N_B": nb})
        st.download_button("Download this simulation (CSV)", export.to_csv(index=False), "simulation_profile.csv", "text/csv")
        segments = [f"A{i+1}" for i in range(na)] + [f"B{i+1}" for i in range(nb)]
        matrix = pd.DataFrame(factors.factors, index=pd.Index(segments, name="from (row) / to (column)"), columns=segments)
        st.download_button("Download view factors (CSV)", matrix.to_csv(), "view_factors.csv", "text/csv")
        st.caption(f"View factors: each row is an emitting segment and each column a receiving segment. "
                   f"A1–A{na} and B1–B{nb} are numbered counterclockwise from 0° (the right side).")
    st.caption(f"This page is for exploration. The report results use the {selection['n_outer']}/{selection['n_inner']} mesh, qualified at the documented report points with ε_A/ε_B = 0.6/0.8.")

if section != "Interactive simulation":
    following = SECTIONS[SECTIONS.index(section)+1]
    label = "Explore interactively" if following == "Interactive simulation" else f"Next: {following}"
    st.button(label, on_click=select_section, args=(following,), key="next_section")

# A section change is a new reading destination; ordinary widget reruns keep position.
previous_section = st.session_state.get("last_rendered_section", section)
st.session_state.last_rendered_section = section
if previous_section != section:
    st.session_state.navigation_count = st.session_state.get("navigation_count", 0) + 1
    st.html(
        f'<script data-navigation="{st.session_state.navigation_count}">'
        'document.querySelector(\'[data-testid="stMain"]\')'
        '?.scrollTo({top: 0, left: 0, behavior: "instant"});'
        '</script>',
        unsafe_allow_javascript=True,
    )
