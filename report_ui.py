"""Read-only presentation of completed requirements (a), (b) and (c)."""

import pandas as pd
import streamlit as st

from app_charts import angular_chart, trend_chart
from study_data import DATA, MESH, ROOT, STUDIES, discussion, study_rows


def number_columns():
    return {"r": st.column_config.NumberColumn("r (m)", format="%.2f"),
            "d": st.column_config.NumberColumn("d (m)", format="%.2f"),
            "temperature_inner_c": st.column_config.NumberColumn("T_B (°C)", format="%.0f"),
            "mean_inner_flux_w_m2": st.column_config.NumberColumn("Mean q (W/m²)", format="%.3f"),
            "max_deviation_percent": st.column_config.NumberColumn("Max deviation (%)", format="%.5f"),
            "peak_to_peak_percent": st.column_config.NumberColumn("Peak-to-peak (%)", format="%.5f"),
            "heat_inner_w_m": st.column_config.NumberColumn("Q′_B (W/m)", format="%.3f"),
            "n_outer": st.column_config.NumberColumn("N_A", format="%d"),
            "n_inner": st.column_config.NumberColumn("N_B", format="%d"),
            "tolerance": st.column_config.NumberColumn("Integration tolerance", format="%.0e")}


def numerical_evidence(cases):
    st.dataframe(pd.DataFrame({"Check": ["Maximum relative energy imbalance", "Maximum row-closure residual", "Maximum scaled reciprocity residual"],
        "Value": [f"{cases.energy_imbalance_relative.max():.3e}", f"{cases.closure_max.max():.3e}", f"{cases.reciprocity_relative_max.max():.3e}"]}), hide_index=True, width="stretch")
    st.caption("These check consistency. Convergence of the local flux distribution is assessed separately by mesh refinement.")


def overview():
    st.header("Assignment overview")
    st.write("The objective is to quantify how the net heat-flux density varies around the inner cylinder B when it is eccentric inside A. The report follows the required model, surface-discretization study and three physical-parameter studies.")
    st.write("First define the model, then compare surface refinements to choose a discretization, and finally use it to study radius, center distance and inner temperature. The starting inputs below define the experiment; calculated results are introduced with their supporting analysis.")
    st.table(pd.DataFrame([
        ["(a) Thermodynamic model and derivation", "Model: assumptions, view factors, radiosity and net-flux equations"],
        ["(a) Equal-segment surface refinement", "Discretization: independent A/B refinement and integration checks"],
        ["(a) Select a discretization", "Use the refinement comparisons and accuracy criteria to justify segment counts for part (b)"],
        ["(b) Influence of r, d and T_B", "Change one parameter at a time, keeping the discretization chosen in (a)"],
        ["(c) Descriptions, diagrams and commentary", "Geometry, flux profiles, convergence plots, discussion and conclusions"],
        ["Program code for all analyses", "Conclusions and code: downloadable report, data, figures and complete source package"],
    ], columns=["Requirement", "Purpose of the section"]).set_index("Requirement"))
    st.image(str(DATA / "geometry_and_segments.png"), width="stretch")
    st.caption("Geometry and the idea of equal-arc segmentation. The 12 A arcs and 8 B arcs are illustrative drawing choices; suitable calculation counts will be assessed in (a) Discretization.")
    st.subheader("Starting inputs")
    st.caption("R and T_A are prescribed by the assignment. The other values are chosen inputs for the working case, rather than calculated findings.")
    st.dataframe(pd.DataFrame({"Parameter": ["R", "T_A", "r", "d", "T_B", "ε_A / ε_B"],
        "Value": ["1 m (prescribed)", "30 °C (prescribed)", "0.4 m", "0.3 m", "200 °C", "0.6 / 0.8"]}), hide_index=True)
    st.caption("The geometry and temperatures are prescribed steady states. Interactive movement explores parameter changes; it is not a transient-heating model.")
    st.info("Read Model, then (a) Discretization, then (b) Parameter studies. Interactive simulation is separate from the fixed report results.")


def model_page():
    st.markdown((ROOT / "docs" / "MODEL.md").read_text(encoding="utf-8"))
    st.image(str(DATA / "geometry_and_segments.png"), width="stretch")
    st.caption("The 12/8 arcs illustrate the method. Calculation counts will be assessed in (a) Discretization. The normals point into the vacuum.")


def discretization_page(selection, cases):
    st.header("(a) Surface discretization")
    st.write("Hold r = 0.4 m, d = 0.3 m, T_B = 200 °C and emissivities 0.6/0.8 fixed. Refine one surface at a time, retaining equal angular arcs on each surface.")
    study = st.segmented_control("Refinement evidence", ["Outer surface A", "Inner surface B", "Integration tolerance"], default="Outer surface A", required=True, key="refinement_evidence")
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
    if group != "integration":
        st.altair_chart(trend_chart(rows, x, label, "max_deviation_percent", "Maximum relative deviation (%)"), width="stretch")
        profiles = []
        for row in rows.itertuples():
            profile = pd.read_csv(MESH / f"independent_{row.case}_profile.csv")
            profile["deviation_percent"] = 100*(profile.flux_w_m2-row.mean_inner_flux_w_m2)/abs(row.mean_inner_flux_w_m2)
            profile["mesh"] = f"{row.n_outer}/{row.n_inner}"
            profiles.append(profile)
        st.altair_chart(angular_chart(pd.concat(profiles), group="mesh"), width="stretch")
    table = comparisons[comparisons.study.eq(group)].rename(columns={"profile_change_percent": "Profile change (%)", "max_deviation_change_pp": "Max-deviation change (pp)", "peak_to_peak_change_pp": "Peak-to-peak change (pp)", "passes": "Meets criteria"})
    case_labels = {row.case: (f"{row.tolerance:.0e}" if group == "integration" else f"{row.n_outer}/{row.n_inner}") for row in all_cases.itertuples()}
    table["coarse"] = table.coarse.map(case_labels)
    table["fine"] = table.fine.map(case_labels)
    comparison_labels = {"coarse": "Looser tolerance" if group == "integration" else "Coarser mesh A/B",
                         "fine": "Tighter tolerance" if group == "integration" else "Finer mesh A/B"}
    st.dataframe(table[["coarse", "fine", "Profile change (%)", "Max-deviation change (pp)", "Peak-to-peak change (pp)", "Meets criteria"]].rename(columns=comparison_labels), hide_index=True, width="stretch")
    st.write({"outer": "Outer refinement progressively stabilizes the local distribution: changing A from 96 to 192 segments changes maximum relative deviation by about 0.0032 percentage points. Selection also considers the larger offsets in part (b).",
              "inner": "The 16-to-32 inner refinement changes the deviation metrics by more than 0.1 percentage points. Finer inner meshes stabilize them. The mean heat flux changes much less, so checking total heat alone would miss insufficient resolution of local nonuniformity.",
              "integration": "Tightening integration changes the nonuniformity metrics by less than 2e-9 percentage points between successive tolerances here. Integration has stabilized; that does not replace refinement of the surface arcs."}[group])
    st.subheader("Selection criteria and qualification")
    st.markdown("- Maximum difference between interpolated angular profiles: **below 0.5%** of the refined mean flux.\n- Change in maximum relative deviation: **below 0.1 percentage points**.\n- Change in peak-to-peak relative range: **below 0.1 percentage points**.")
    st.caption("Profiles are compared by periodic interpolation of segment averages on a common 4096-angle grid. These are finite-refinement differences, not rigorous absolute error bounds.")
    qualification = pd.read_csv(MESH / "qualification_96_128_comparisons.csv")
    with st.container(horizontal=True):
        st.metric("Geometry points checked", str(len(qualification)), border=True)
        st.metric("Largest profile change", f"{qualification.profile_change_percent.max():.4f}%", border=True)
        st.metric("Largest metric change", f"{max(qualification.max_deviation_change_pp.max(), qualification.peak_to_peak_change_pp.max()):.4f} pp", border=True)
    st.write("At each geometry used in part (b), compare 96/128 against 192/256. All 12 points pass. At the largest offset, also compare against 384/256: the coarser 96/64 mesh misses the peak-to-peak criterion (0.102032 pp), while 96/128 passes (0.059172 pp).")
    with st.expander("Qualification table and additional high-offset check"):
        st.dataframe(qualification[["point", "r", "d", "profile_change_percent", "max_deviation_change_pp", "peak_to_peak_change_pp", "passes"]], hide_index=True, width="stretch")
        extra = pd.read_csv(MESH / "worst_case_comparisons.csv")
        st.dataframe(extra[extra.fine.eq("further_refined")], hide_index=True, width="stretch")
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
    st.altair_chart(trend_chart(rows, x, xlabel, "max_deviation_percent", "Maximum relative deviation (%)"), width="stretch")
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
    st.header("Conclusions and program code")
    st.write("Descriptions and commentary for requirement (c) accompany the model and every analysis in (a) and (b). The following conclusions refer to the stated parameter ranges and fixed emissivities.")
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
