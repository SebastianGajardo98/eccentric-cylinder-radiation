"""Write the documented mesh selection only after all required checks pass."""

import json

import pandas as pd

from study_data import MESH as DIRECTORY, ROOT


def main():
    na, nb = 96, 128
    qualification = pd.read_csv(DIRECTORY/f"qualification_{na}_{nb}_comparisons.csv")
    cases = pd.read_csv(DIRECTORY/f"qualification_{na}_{nb}_cases.csv")
    support = pd.read_csv(DIRECTORY/f"support_{na}_{nb}_comparisons.csv")
    worst = pd.read_csv(DIRECTORY/"worst_case_comparisons.csv")
    assert qualification.passes.all(), "A study point fails the selection criteria."
    further = worst[worst.coarse == "inner_refined"].iloc[0]
    assert bool(further.passes), "The selected mesh fails the further-refinement check."
    integration = support[support.check == "integration"]
    assert integration.passes.astype(str).eq("True").all(), "Integration tolerance has not stabilized."
    assert cases.energy_imbalance_relative.max() < 1e-7, "Energy residual is too high."
    assert cases.reciprocity_relative_max.max() < 1e-7, "Reciprocity residual is too high."
    selected = {
        "n_outer": na, "n_inner": nb, "integration_tolerance": 1e-8,
        "baseline": {"R_m": 1.0, "r_m": 0.4, "d_m": 0.3, "temperature_outer_c": 30,
                     "temperature_inner_c": 200, "emissivity_outer": 0.6, "emissivity_inner": 0.8},
        "criteria": {"profile_change_percent_max": 0.5, "max_deviation_change_pp_max": 0.1,
                     "peak_to_peak_change_pp_max": 0.1},
        "reference_mesh": {"n_outer": 192, "n_inner": 256},
        "additional_reference_mesh_at_e_0_9": {"n_outer": 384, "n_inner": 256},
        "qualified_geometry_points": qualification[["point", "r", "d", "e"]].to_dict("records"),
        "temperature_scaling_checked_c": [60, 200, 400],
        "maximum_profile_change_percent": float(qualification.profile_change_percent.max()),
        "maximum_max_deviation_change_pp": float(qualification.max_deviation_change_pp.max()),
        "maximum_peak_to_peak_change_pp": float(qualification.peak_to_peak_change_pp.max()),
        "solver_sha256": cases.solver_sha256.iloc[0],
        "scope": "Specified geometry points, fixed emissivities 0.6/0.8. Other combinations remain available for exploration and require separate convergence assessment.",
        "interpretation": "Finite-mesh differences, not rigorous absolute error bounds.",
    }
    (DIRECTORY/"selected.json").write_text(json.dumps(selected, indent=2), encoding="utf-8")
    baseline = cases[(cases.point == "baseline") & (cases.mesh == "candidate")].iloc[0]
    lines = [
        "# Working parameters and discretization selection", "",
        "## Working parameters", "",
        "| Parameter | Baseline | Reason |", "| --- | --- | --- |",
        "| Outer radius R | 1 m | Prescribed by the assignment |",
        "| Outer temperature T_A | 30 C | Prescribed by the assignment |",
        "| Inner radius r | 0.4 m | Leaves room to vary radius and offset independently |",
        "| Offset d | 0.3 m | e = 0.5; minimum gap 0.3 m, maximum gap 0.9 m |",
        "| Inner temperature T_B | 200 C | A working hot-cylinder case above T_A |",
        "| Emissivities epsilon_A / epsilon_B | 0.6 / 0.8 | Explicit gray-surface working assumptions, allowing diffuse reflections; no particular material is claimed |", "",
        "Final one-parameter sweeps: e = 0, 0.15, 0.30, 0.45, 0.60, 0.75, 0.90 at r = 0.4 m; r = 0.2, 0.3, 0.4, 0.5, 0.6 m at fixed d = 0.3 m; T_B = 60 to 400 C at baseline geometry. Fix both emissivities throughout. The minimum gap among these geometry points is 0.06 m. The concentric point is a numerical boundary check and a useful starting point for the eccentricity sweep.", "",
        *(ROOT / "docs" / "COMPARISON.md").read_text(encoding="utf-8").splitlines(), "",
        "## Independent baseline refinement", "",
        "**Code:** [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `independent`, runs the surface and integration-tolerance cases using [`radiation.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/radiation.py).", "",
        "The outer surface was refined through 24, 48, 96 and 192 segments with the inner surface held at 128. The inner surface was refined through 16, 32, 64 and 128 segments with the outer surface held at 192. This separates their effects; both surfaces were not simply increased together.", "",
        "| Refinement | D_max change (percentage points) | D_pp change (percentage points) |",
        "| --- | ---: | ---: |",
    ]
    independent = pd.read_csv(DIRECTORY/"independent_comparisons.csv")
    for _, row in independent[independent.study != "integration"].iterrows():
        lines.append(f"| {row.coarse} to {row.fine} | {row.max_deviation_change_pp:.6f} | {row.peak_to_peak_change_pp:.6f} |")
    lines += ["", "The inner 16-to-32 refinement fails the 0.1 percentage-point criterion. Finer meshes stabilize. Although the baseline alone permits smaller grids, the choice must also cover the larger offsets in part (b).", "",
              "## Qualification across the study points", "",
              "Accept changes below 0.5% in the maximum difference of interpolated flux profiles, and below 0.1 percentage points in both D_max and D_pp. Normalize profile differences by the refined grid's mean inner flux. Periodic interpolation uses a shared 4096-angle grid and segment averages; it is a comparison method, not an exact pointwise solution.", "",
              "Each of the 12 distinct geometry points was compared at 96/128 and 192/256 segments. All pass the three criteria.", "",
              "**Code:** [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `qualify`, runs these arrangements and compares both meshes using `compare`.", "",
              "| Study point | e | Profile change (%) | D_max change (pp) | D_pp change (pp) |", "| --- | ---: | ---: | ---: | ---: |"]
    for _, row in qualification.iterrows():
        lines.append(f"| {row.point} | {row.e:.3f} | {row.profile_change_percent:.6f} | {row.max_deviation_change_pp:.6f} | {row.peak_to_peak_change_pp:.6f} |")
    lines += ["", "## Why the inner grid was increased from 64 to 128", "",
              "At e = 0.9, the coarser 96/64 mesh passes comparison with 192/128. Its D_pp nevertheless differs from the additional 384/256 reference by 0.102032 percentage points, just above the threshold. Increasing the inner grid to 128 reduces the difference to 0.059172 percentage points and the profile difference to 0.056176%. This additional check avoids relying on a marginal first comparison.", "",
              "**Code:** [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `worst_case`, runs these additional resolutions at the same smallest-gap arrangement.", "",
              "## Integration and temperature checks", "",
              "At 96/64 baseline resolution, tightening source integration from 1e-6 through 1e-9 changes the nonuniformity metrics by less than 2e-9 percentage points between successive tolerances. At the selected 96/128 resolution, a 1e-8 versus 1e-9 check was also run at the baseline and at e = 0.9.", ""]
    for _, row in integration.iterrows():
        lines.append(f"- {row.point}: profile change {row.profile_change_percent:.3e}%; D_pp change {row.peak_to_peak_change_pp:.3e} percentage points.")
    lines += ["", "Temperature checks at 60, 200 and 400 C, for both baseline and e = 0.9 geometry, leave the normalized nonuniformity unchanged to approximately 2e-12 percentage points. This agrees with the linear fixed-emissivity model: temperature scales absolute flux through the difference in fourth powers. It does not justify temperature-independent results if material emissivity varies with temperature.", "",
              f"Across the selected-mesh qualification and reference cases, the maximum relative enclosure energy imbalance is {cases.energy_imbalance_relative.max():.3e}, maximum row-closure residual is {cases.closure_max.max():.3e}, and maximum scaled reciprocity residual is {cases.reciprocity_relative_max.max():.3e}.", "",
              "## Decision based on the refinement evidence", "",
              "Use **96 equal angular segments on cylinder A and 128 on cylinder B**, with source-arc integration tolerance **1e-8**, for the documented final parameter-study points. This is a recommended study setting; the interactive app keeps Preview and Custom resolutions available.", "",
              "**Code:** [`finalize_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/finalize_discretization.py) checks the recorded evidence and saves the selected settings. [`plot_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/plot_discretization.py) draws the selection-evidence figure.", "",
              "## Selected-mesh baseline result", "",
              f"- Mean inner flux: {baseline.mean_inner_flux_w_m2:.6f} W/m^2.",
              f"- D_max: {baseline.max_deviation_percent:.6f}%.",
              f"- D_pp: {baseline.peak_to_peak_percent:.6f}%.",
              f"- Heat from B per unit length: {baseline.heat_inner_w_m:.6f} W/m.", "",
              "## Scope and reproducibility", "",
              "The selection is supported at the specified geometry points with emissivities 0.6/0.8. It is not a rigorous error bound, a proof for all continuous intermediate values, or qualification of arbitrary radius/offset/emissivity combinations. The site remains interactive; user-selected cases outside the documented points can be checked using independent refinement.", "",
              "The numerical scope follows the requested assignment requirements. The interpretation of all three required parameter studies is presented in PARAMETERS.md.", "",
              "Run the following from the repository directory (local caches in tmp/ make repeat runs faster):", "",
              "```powershell", "python scripts/run_discretization.py --stage independent",
              "python scripts/run_discretization.py --stage worst-case",
              "python scripts/run_discretization.py --stage qualify --outer 96 --inner 128",
              "python scripts/run_discretization.py --stage support --outer 96 --inner 128",
              "python scripts/finalize_discretization.py", "python scripts/plot_discretization.py", "```", "",
              "Raw case tables, angular profiles, comparison tables, source fingerprints, and selected settings are stored in results/discretization/. The completed parameter studies use this selected mesh; see PARAMETERS.md and REPORT.md."]
    (ROOT / "docs" / "DISCRETIZATION.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(json.dumps(selected, indent=2))


if __name__ == "__main__":
    main()
