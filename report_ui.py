"""Read-only presentation of completed requirements (a), (b) and (c)."""

import pandas as pd
import streamlit as st

from app_charts import angular_chart, trend_chart
from assignment_content import REQUIREMENTS
from study_data import DATA, MESH, ROOT, STUDIES, discussion, study_rows


def number_columns():
    return {"r": st.column_config.NumberColumn("r (m)", format="%.2f"),
            "d": st.column_config.NumberColumn("d (m)", format="%.2f"),
            "temperature_inner_c": st.column_config.NumberColumn("T_B (°C)", format="%.0f"),
            "mean_inner_flux_w_m2": st.column_config.NumberColumn("Mean q on B (W/m²)", format="%.3f"),
            "max_deviation_percent": st.column_config.NumberColumn("D_max (%)", format="%.5f"),
            "peak_to_peak_percent": st.column_config.NumberColumn("D_pp (%)", format="%.5f"),
            "max_deviation_change_pp": st.column_config.NumberColumn("D_max change (pp)", format="%.4f"),
            "peak_to_peak_change_pp": st.column_config.NumberColumn("D_pp change (pp)", format="%.4f"),
            "heat_inner_w_m": st.column_config.NumberColumn("Q′_B (W/m)", format="%.3f"),
            "n_outer": st.column_config.NumberColumn("N_A", format="%d"),
            "n_inner": st.column_config.NumberColumn("N_B", format="%d"),
            "tolerance": st.column_config.NumberColumn("Integration tolerance", format="%.0e")}


def numerical_evidence(cases):
    st.dataframe(pd.DataFrame({"Check": ["Maximum relative energy imbalance", "Maximum row-closure residual", "Maximum scaled reciprocity residual"],
        "Value": [f"{cases.energy_imbalance_relative.max():.3e}", f"{cases.closure_max.max():.3e}", f"{cases.reciprocity_relative_max.max():.3e}"]}), hide_index=True, width="stretch")
    st.caption("These check consistency. Convergence of the local flux distribution is assessed separately by mesh refinement.")


def requirement(part):
    st.markdown(f"**Assignment requirement ({part})**")
    st.markdown("> " + REQUIREMENTS[part])


def assignment_page():
    st.header("Assignment")
    st.markdown((ROOT / "docs" / "ASSIGNMENT.md").read_text(encoding="utf-8"))
    st.caption(r"Temperature notation: $\vartheta_A$ and $\vartheta_B$ in the assignment are written as $T_A$ and $T_B$ elsewhere in the app.")
    st.subheader("The following is required")
    for part, text in REQUIREMENTS.items():
        st.markdown(f"**({part})** {text}")
    st.image(str(DATA / "geometry_and_segments.png"), width="stretch")
    st.caption("Geometry and the idea of equal-arc segmentation. The 12 A arcs and 8 B arcs are illustrative drawing choices; suitable calculation counts will be assessed in (a) Discretization.")
    st.markdown((ROOT / "docs" / "GEOMETRY.md").read_text(encoding="utf-8"))
    st.caption("The geometry and temperatures are prescribed steady states. Interactive movement explores parameter changes; it is not a transient-heating model.")
    st.info("Read (a) Model, then (a) Discretization, then (b) Parameter studies and (c) Discussion and conclusions. Interactive simulation is separate from the fixed report results.")


def model_page():
    st.header("(a) Thermodynamic model")
    requirement("a")
    st.write("This section addresses the model derivation in part (a). The surface-refinement analysis continues in (a) Discretization.")
    st.markdown((ROOT / "docs" / "MODEL.md").read_text(encoding="utf-8").split("\n", 1)[1])
    st.image(str(DATA / "geometry_and_segments.png"), width="stretch")
    st.caption("The 12/8 arcs illustrate the method. Calculation counts will be assessed in (a) Discretization. The normals point into the vacuum.")
    st.markdown((ROOT / "docs" / "GEOMETRY.md").read_text(encoding="utf-8"))


def discretization_page(selection, cases):
    st.header("(a) Surface discretization")
    requirement("a")
    st.subheader("Working parameters for part (a)")
    st.write("The assignment fixes the radius of A and the temperature of A. We choose the remaining physical inputs for the refinement study and hold them fixed while changing the surface segment counts.")
    st.table(pd.DataFrame({"Parameter": ["R", "T_A", "r", "d", "T_B", "ε_A / ε_B"],
        "Value": ["1 m", "30 °C", "0.4 m", "0.3 m", "200 °C", "0.6 / 0.8"],
        "Source": ["Prescribed by the assignment", "Prescribed by the assignment", "Chosen for this study", "Chosen for this study", "Chosen for this study", "Chosen surface properties"]}).set_index("Parameter"))
    st.subheader("Check each surface at the starting arrangement")
    st.write("Keep the physical inputs above fixed. First check A and B separately by adding equal surface segments to one cylinder at a time. The third view checks the integration tolerance with both segment counts fixed.")
    study = st.segmented_control("Refinement evidence", ["Outer surface A", "Inner surface B", "Integration tolerance"], default="Outer surface A", required=True, key="refinement_evidence")
    st.write("In all three views, the mean flux, nonuniformity measures and flux profiles refer to cylinder B. The selected view identifies which surface is refined or whether the integration tolerance changes.")
    all_cases = pd.read_csv(MESH / "independent_cases.csv")
    comparisons = pd.read_csv(MESH / "independent_comparisons.csv")
    if study == "Outer surface A":
        rows = all_cases[all_cases.case.str.startswith("outer_")].sort_values("n_outer")
        group, x, label = "outer", "n_outer", "Segments on A (N_A)"
        st.write("N_B is fixed at 128. Increase N_A through 24, 48, 96 and 192.")
    elif study == "Inner surface B":
        rows = pd.concat([all_cases[all_cases.case.str.startswith("inner_")], all_cases[all_cases.case.eq("outer_192_128")]]).sort_values("n_inner")
        group, x, label = "inner", "n_inner", "Segments on B (N_B)"
        st.write("N_A is fixed at 192. Increase N_B through 16, 32, 64 and 128.")
    else:
        rows = all_cases[all_cases.case.str.startswith("tolerance_")].sort_values("tolerance", ascending=False)
        group, x, label = "integration", "tolerance", "Source integration tolerance"
        st.write("N_A = 96 and N_B = 64 remain fixed while the integration tolerance tightens from 1e-6 to 1e-9. This separates integration error from surface-discretization error.")
    cols = ["n_outer", "n_inner", "tolerance", "mean_inner_flux_w_m2", "max_deviation_percent", "peak_to_peak_percent"]
    st.dataframe(rows[cols], column_config=number_columns(), hide_index=True, width="stretch")
    st.caption(r"From equation (13): $D_{\max}$ is the largest percentage departure from B's mean flux; $D_{pp}$ is the maximum-to-minimum flux difference expressed as a percentage of that mean.")
    if group != "integration":
        st.altair_chart(trend_chart(rows, x, label, "max_deviation_percent", "D_max (%)"), width="stretch")
        profiles = []
        for row in rows.itertuples():
            profile = pd.read_csv(MESH / f"independent_{row.case}_profile.csv")
            profile["deviation_percent"] = 100*(profile.flux_w_m2-row.mean_inner_flux_w_m2)/abs(row.mean_inner_flux_w_m2)
            profile["mesh"] = f"{row.n_outer}/{row.n_inner}"
            profiles.append(profile)
        st.altair_chart(angular_chart(pd.concat(profiles), group="mesh"), width="stretch")
        st.caption("The legend lists segments on A / segments on B. All four profiles are shown with different colors and line styles; close agreement can make them nearly overlap.")
    table = comparisons[comparisons.study.eq(group)].rename(columns={"profile_change_percent": "Profile change (%)", "max_deviation_change_pp": "D_max change (pp)", "peak_to_peak_change_pp": "D_pp change (pp)", "passes": "Changes small enough?"})
    case_labels = {row.case: (f"{row.tolerance:.0e}" if group == "integration" else f"{row.n_outer}/{row.n_inner}") for row in all_cases.itertuples()}
    table["coarse"] = table.coarse.map(case_labels)
    table["fine"] = table.fine.map(case_labels)
    comparison_labels = {"coarse": "Looser tolerance" if group == "integration" else "Fewer segments (A/B)",
                         "fine": "Tighter tolerance" if group == "integration" else "More segments (A/B)"}
    if group == "integration":
        st.subheader("Does a smaller integration tolerance change the results?")
        st.write("We compare two calculations with different integration tolerances. Small differences suggest that requesting tighter integration has little effect on the results.")
    else:
        st.subheader("Does adding more segments change the results?")
        st.write("We compare two calculations with different segment counts. Small differences suggest that adding more segments has little effect on the results.")
    st.dataframe(table[["coarse", "fine", "Profile change (%)", "D_max change (pp)", "D_pp change (pp)", "Changes small enough?"]].rename(columns=comparison_labels), hide_index=True, width="stretch")
    st.caption(r"$D_{\max}$ change and $D_{pp}$ change are absolute differences between the two calculations, in percentage points (pp). A checked box means the profile change is below 0.5% and both measure changes are below 0.1 pp.")
    st.write({"outer": "Outer refinement progressively stabilizes the local distribution: changing A from 96 to 192 segments changes D_max by about 0.0032 percentage points. Selection also considers the larger offsets in part (b).",
              "inner": "The 16-to-32 inner refinement changes D_max and D_pp by more than 0.1 percentage points. Finer inner meshes stabilize them. The mean heat flux changes much less, so checking total heat alone would miss insufficient resolution of local nonuniformity.",
              "integration": "Tightening integration changes D_max and D_pp by less than 2e-9 percentage points between successive tolerances here. Integration has stabilized; that does not replace refinement of the surface arcs."}[group])
    st.subheader("Selection criteria")
    st.markdown(r"- Maximum difference between interpolated angular profiles: **below 0.5%** of the refined mean flux." + "\n" + r"- Change in $D_{\max}$: **below 0.1 percentage points**." + "\n" + r"- Change in $D_{pp}$: **below 0.1 percentage points**.")
    st.caption("We compare both flux curves at the same angular positions, estimating values between the calculated segment averages. Small differences show agreement between two calculations; they do not guarantee the exact error.")
    with st.expander("How are the flux curves compared?"):
        st.write("Different segment counts give values at different midpoint angles. Interpolation estimates values between neighbouring positions so that both curves can be compared at the same 4096 angles. The comparison wraps around the circle, connecting 360° back to 0°; this is called periodic interpolation.")
        st.write("These 4096 angles are comparison positions, not additional surface segments. We report the differences between two numerical calculations, rather than a guaranteed bound on their distance from the exact solution.")
    st.subheader("Check the segment counts across 12 cylinder arrangements")
    st.write("Each arrangement specifies the radius of B and its distance from the center of A. We check 12 different arrangements used in part (b), including the starting arrangement.")
    st.write("At every arrangement, compare 96 segments on A and 128 on B with 192 on A and 256 on B. Both surfaces are refined together in this check. The three cards below summarize all 12 comparisons and stay the same whichever view is selected above.")
    qualification = pd.read_csv(MESH / "qualification_96_128_comparisons.csv")
    with st.container(horizontal=True):
        st.metric("Cylinder arrangements checked", str(len(qualification)), border=True)
        st.metric("Largest profile change", f"{qualification.profile_change_percent.max():.4f}%", border=True)
        st.metric("Largest D_max or D_pp change", f"{max(qualification.max_deviation_change_pp.max(), qualification.peak_to_peak_change_pp.max()):.4f} pp", border=True)
    st.write("All 12 arrangements pass the selection criteria. The largest changes shown above occur at the largest center distance, where the gap is smallest.")
    with st.expander("Results for all 12 cylinder arrangements"):
        st.dataframe(qualification[["point", "r", "d", "profile_change_percent", "max_deviation_change_pp", "peak_to_peak_change_pp", "passes"]], column_config=number_columns(), hide_index=True, width="stretch")
    st.subheader("Extra check at the smallest gap")
    st.write("At the largest center distance, also compare with 384 segments on A and 256 on B. This additional comparison is separate from the three cards above. The 96/64 setting misses the D_pp-change limit (0.102032 pp), while 96/128 passes (0.059172 pp). This supports using 128 segments on B for part (b).")
    with st.expander("Results of the extra check"):
        extra = pd.read_csv(MESH / "worst_case_comparisons.csv")
        st.dataframe(extra[extra.fine.eq("further_refined")], column_config=number_columns(), hide_index=True, width="stretch")
    st.image(str(MESH / "discretization_selection.png"), width="stretch")
    st.subheader("Discretization selected for part (b)")
    st.success(f"Based on the refinement comparisons above: N_A = {selection['n_outer']}, N_B = {selection['n_inner']}, integration tolerance = 1e-8.")
    st.subheader("Selected-mesh working result")
    baseline = cases[cases.case.eq("baseline")]
    st.dataframe(baseline[["mean_inner_flux_w_m2", "max_deviation_percent", "peak_to_peak_percent", "heat_inner_w_m"]], column_config=number_columns(), hide_index=True, width="stretch")
    st.image(str(DATA / "baseline_flux.png"), width="stretch")
    st.caption("Calculated segment averages at their midpoint angles; connecting lines guide the eye. The selected mesh is used unchanged in all three required parameter studies.")
    st.download_button("Download refinement comparisons (CSV)", comparisons.to_csv(index=False), "refinement_comparisons.csv", "text/csv")


def parameters_page(cases, profiles):
    st.header("(b) Influence of r, d and T_B")
    requirement("b")
    st.subheader("Study setup")
    st.write("All results below use the selected 96/128 discretization and tolerance 1e-8. R = 1 m, T_A = 30 °C and ε_A/ε_B = 0.6/0.8 remain fixed. Each study changes one named parameter.")
    labels = {"Center distance d": "offset", "Inner radius r": "radius", "Inner temperature T_B": "temperature"}
    selected = st.segmented_control("Required parameter study", list(labels), default="Center distance d", required=True, key="required_parameter")
    study = labels[selected]
    rows = study_rows(cases, study)
    _, xlabel, x, _ = STUDIES[study]
    st.info({"offset": "Change d = 0 to 0.54 m; fix r = 0.4 m and T_B = 200 °C. d = 0 is the concentric reference.",
             "radius": "Change r = 0.2 to 0.6 m; fix d = 0.3 m and T_B = 200 °C. The surfaces remain separated.",
             "temperature": "Change T_B = 60 to 400 °C; fix r = 0.4 m and d = 0.3 m."}[study])
    st.subheader("Effect on nonuniformity")
    st.altair_chart(trend_chart(rows, x, xlabel, "max_deviation_percent", "D_max (%)"), width="stretch")
    st.write(discussion(cases, study))
    st.subheader("Angular distribution on B")
    quantity = st.segmented_control("Profile quantity", ["Deviation from mean (%)", "Net flux (W/m²)"], default="Deviation from mean (%)", required=True, key=f"{study}_profile_quantity")
    frame = profiles[profiles.study.eq(study)].copy()
    units = "°C" if study == "temperature" else "m"
    frame["label"] = frame.parameter_value.map(lambda p: f"{p:g} {units}")
    st.altair_chart(angular_chart(frame, "deviation_percent" if quantity.startswith("Deviation") else "flux_w_m2", "label"), width="stretch")
    st.caption("0° is right, 90° top, 180° left and 270° bottom. Profiles use all 128 calculated B-segment averages.")
    if study == "temperature":
        st.caption("Relative profiles coincide under the fixed-emissivity assumptions.")
    st.subheader("Absolute heat-flux density")
    st.altair_chart(trend_chart(rows, x, xlabel, "mean_inner_flux_w_m2", "Mean q on B (W/m²)"), width="stretch")
    st.dataframe(rows[["r", "d", "temperature_inner_c", "mean_inner_flux_w_m2", "max_deviation_percent", "peak_to_peak_percent", "heat_inner_w_m"]], column_config=number_columns(), hide_index=True, width="stretch")
    st.caption("q is heat per surface area (W/m²); Q′_B is total heat per axial length (W/m). Changing radius also changes emitting circumference, so these quantities need not have the same trend.")
    with st.expander("Numerical checks for these cases"):
        numerical_evidence(rows)
    with st.expander("Exportable figure with all four views"):
        st.image(str(DATA / f"{study}_study.png"), width="stretch")
        st.download_button("Download figure (PNG)", (DATA / f"{study}_study.png").read_bytes(), f"{study}_study.png", "image/png")
    st.download_button("Download this study (CSV)", rows.to_csv(index=False), f"{study}_cases.csv", "text/csv")
    st.download_button("Download angular profiles (CSV)", frame.drop(columns="label").to_csv(index=False), f"{study}_profiles.csv", "text/csv")


def conclusions_page(selection, cases, manifest):
    st.header("(c) Discussion and conclusions")
    requirement("c")
    st.write("Part (c) brings together the interpretation of the calculations. Its descriptions, diagrams and commentary also accompany the analyses in (a) and (b). The conclusions below refer to the stated parameter ranges and fixed emissivities.")
    for study in STUDIES:
        st.subheader(STUDIES[study][0])
        st.write(discussion(cases, study))
    st.subheader("Numerical reliability and scope")
    st.write("The 96/128 mesh satisfies the documented finite-refinement criteria at all 12 geometry points, including an additional high-offset reference. These checks establish consistency and stability for the listed cases; arbitrary near-contact or different-emissivity explorations need their own convergence review.")
    numerical_evidence(cases)
    st.subheader("Submission files")
    st.write("The package includes the written model and report, all study tables and figures, the source for every analysis, tests, requirements, and reproduction instructions. It can be read and run without access to the private GitHub repository.")
    from build_submission import build_package
    st.download_button("Download complete submission (ZIP)", build_package(), "eccentric-cylinder-assignment.zip", "application/zip", type="primary")
    st.download_button("Download written report (Markdown)", (ROOT / "docs" / "REPORT.md").read_text(encoding="utf-8"), "REPORT.md", "text/markdown")
    st.download_button("Download all parameter results (CSV)", (DATA / "cases.csv").read_bytes(), "parameter_studies.csv", "text/csv")
    st.code("python -m pip install -r requirements-dev.txt\npython -m pytest -q\npython run_assignment.py\npython -m streamlit run streamlit_app.py", language="powershell")
    with st.expander("Numerical source and provenance"):
        st.code((ROOT / "radiation.py").read_text(encoding="utf-8"), language="python")
        st.caption("View factors retain circular arcs and visibility. The solver does not normalize or symmetrize the computed factor matrix to hide numerical residuals.")
        st.json(manifest)
