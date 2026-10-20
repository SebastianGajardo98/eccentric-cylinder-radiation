"""Read and validate the completed assignment studies, independently of the UI."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
DATA = ROOT / "results" / "studies"
MESH = ROOT / "results" / "discretization"
STUDIES = {
    "offset": ("Center distance d", "d (m)", "d", 7),
    "radius": ("Inner radius r", "r (m)", "r", 5),
    "temperature": ("Inner temperature", "T_B (°C)", "temperature_inner_c", 6),
}


def source_hash():
    # Universal-newline reading makes the same source fingerprint portable
    # between Windows CRLF checkouts and Linux/Streamlit Cloud LF checkouts.
    return hashlib.sha256((SCRIPTS / "radiation.py").read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def text_hash(path):
    """Portable integrity check for text data checked out on Windows or Linux."""
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def load_studies():
    """Reject missing, mixed-version or incompletely generated report data."""
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    selection = json.loads((MESH / "selected.json").read_text(encoding="utf-8"))
    if manifest["solver_sha256"] != source_hash() or selection["solver_sha256"] != source_hash():
        raise ValueError("Study results do not match radiation.py. Run python scripts/run_assignment.py.")
    for name, digest in manifest["data_sha256"].items():
        if text_hash(DATA / name) != digest:
            raise ValueError(f"Study data are incomplete or changed: {name}.")
    cases = pd.read_csv(DATA / "cases.csv")
    profiles = pd.read_csv(DATA / "profiles.csv")
    if not cases.case.is_unique or len(cases) != 19:
        raise ValueError("Expected one baseline and 18 parameter-study cases.")
    if not cases.solver_sha256.eq(source_hash()).all():
        raise ValueError("Mixed numerical solver versions in study cases.")
    baseline = cases[cases.case.eq("baseline")]
    if (len(baseline) != 1 or not np.isclose(baseline.iloc[0].r, .4)
            or not np.isclose(baseline.iloc[0].d, .3) or not np.isclose(baseline.iloc[0].temperature_inner_c, 200)):
        raise ValueError("The baseline must use the stated fixed working case.")
    if not (cases.n_outer.eq(selection["n_outer"]).all()
            and cases.n_inner.eq(selection["n_inner"]).all()
            and np.allclose(cases.tolerance, selection["integration_tolerance"], rtol=0, atol=0)):
        raise ValueError("Part (b) must use the selected part (a) discretization.")
    for study, (_, _, _, count) in STUDIES.items():
        rows = cases[cases.study.eq(study)].sort_values("parameter_value")
        if len(rows) != count:
            raise ValueError(f"Incomplete {study} study.")
        fixed = ("r", "temperature_inner_c") if study == "offset" else (
            ("d", "temperature_inner_c") if study == "radius" else ("r", "d"))
        if any(rows[column].nunique() != 1 for column in fixed):
            raise ValueError(f"The {study} study changes more than one physical parameter.")
        expected_fixed = {"r": 0.4, "d": 0.3, "temperature_inner_c": 200}
        if any(not np.allclose(rows[column], expected_fixed[column]) for column in fixed):
            raise ValueError(f"The {study} study does not use the stated working case.")
        expected_values = {"offset": np.linspace(0, .9, 7)*.6,
                           "radius": np.linspace(.2, .6, 5),
                           "temperature": [60, 100, 150, 200, 300, 400]}[study]
        if not np.allclose(rows.parameter_value, expected_values):
            raise ValueError(f"The {study} study does not use the stated parameter range.")
        if not np.allclose(rows.parameter_value, rows[STUDIES[study][2]]):
            raise ValueError(f"The {study} study axis disagrees with the physical parameters.")
    if not (cases.emissivity_outer.eq(0.6).all() and cases.emissivity_inner.eq(0.8).all()
            and np.allclose(cases.temperature_outer_k, 303.15) and np.allclose(cases.R, 1.0)
            and (cases.temperature_inner_k > cases.temperature_outer_k).all()):
        raise ValueError("Recorded studies must retain the stated emissivities and outer temperature.")
    if not ((cases.r > 0).all() and (cases.d >= 0).all() and (cases.r + cases.d < cases.R).all()):
        raise ValueError("A recorded geometry intersects the outer wall.")
    if (cases.energy_imbalance_relative.max() >= 1e-7 or cases.closure_max.max() >= 1e-10
            or cases.reciprocity_relative_max.max() >= 1e-7):
        raise ValueError("Recorded numerical consistency residuals exceed the report thresholds.")
    if set(profiles.case) != set(cases.case):
        raise ValueError("A case is missing its angular profile.")
    for row in cases.itertuples():
        if not any(np.isclose(row.r, p["r"]) and np.isclose(row.d, p["d"]) for p in selection["qualified_geometry_points"]):
            raise ValueError(f"A reported geometry is outside the mesh qualification: {row.case}.")
        profile = profiles[profiles.case.eq(row.case)]
        if len(profile) != row.n_inner or not np.isfinite(profile.flux_w_m2).all():
            raise ValueError(f"Incomplete angular profile: {row.case}.")
        if not np.isclose(profile.flux_w_m2.mean(), row.mean_inner_flux_w_m2, rtol=1e-10):
            raise ValueError(f"Profile and summary disagree: {row.case}.")
    return selection, cases, profiles, manifest


# Reader-facing CSV downloads keep the physical inputs, mesh and results. Integrity
# fingerprints and solver diagnostics stay in the recorded files under results/.
DOWNLOAD_COLUMNS = {
    "r": "r (m)", "d": "d (m)", "e": "e = d/(R-r)", "minimum_gap_m": "minimum gap (m)",
    "temperature_outer_c": "T_A (C)", "temperature_inner_c": "T_B (C)",
    "emissivity_outer": "eps_A", "emissivity_inner": "eps_B", "n_outer": "N_A", "n_inner": "N_B",
    "mean_inner_flux_w_m2": "q_B mean (W/m2)", "min_inner_flux_w_m2": "q_B min (W/m2)",
    "max_inner_flux_w_m2": "q_B max (W/m2)", "max_deviation_percent": "D_max (%)",
    "peak_to_peak_percent": "D_pp (%)", "heat_inner_w_m": "Q'_B (W/m)",
}
STUDY_NAMES = {"baseline": "working case", "offset": "center distance d",
               "radius": "inner radius r", "temperature": "inner temperature T_B"}
PROFILE_PARAMETER = {"offset": "d (m)", "radius": "r (m)", "temperature": "T_B (C)"}


def download_cases(rows):
    """Case table for download: one row per case, readable column names."""
    rows = rows.assign(temperature_outer_c=rows.temperature_outer_k-273.15)
    table = rows[list(DOWNLOAD_COLUMNS)].rename(columns=DOWNLOAD_COLUMNS)
    exact = ["r (m)", "d (m)", "e = d/(R-r)", "minimum gap (m)", "T_A (C)", "T_B (C)",
             "q_B mean (W/m2)", "q_B min (W/m2)", "q_B max (W/m2)", "Q'_B (W/m)"]
    table[exact] = table[exact].round(6)
    # Below 1e-9 percent the nonuniformity is round-off; adding 0.0 avoids -0.0.
    table[["D_max (%)", "D_pp (%)"]] = table[["D_max (%)", "D_pp (%)"]].round(9)+0.0
    if rows.study.nunique() > 1:
        table.insert(0, "study", rows.study.map(STUDY_NAMES))
    return table


def download_profiles(frame, study):
    """Angular profiles of one study for download."""
    return pd.DataFrame({PROFILE_PARAMETER[study]: frame.parameter_value.round(6),
                         "angle on B (deg)": frame.angle_deg, "q_B (W/m2)": frame.flux_w_m2.round(6),
                         # Adding 0.0 turns -0.0 into 0.0 after rounding away round-off.
                         "deviation from mean (%)": frame.deviation_percent.round(9)+0.0})


def download_comparisons(comparisons, cases):
    """Refinement comparisons for download, with meshes and tolerances instead of case names."""
    labels = {row.case: f"{row.tolerance:.0e}" if row.case.startswith("tolerance_") else f"{row.n_outer}/{row.n_inner}"
              for row in cases.itertuples()}
    refined = {"outer": "segments on A", "inner": "segments on B", "integration": "integration tolerance"}
    return pd.DataFrame({"refined setting": comparisons.study.map(refined),
                         "coarser (A/B or tolerance)": comparisons.coarse.map(labels),
                         "finer (A/B or tolerance)": comparisons.fine.map(labels),
                         "profile change (%)": comparisons.profile_change_percent,
                         "mean flux change (%)": comparisons.mean_change_percent,
                         "D_max change (pp)": comparisons.max_deviation_change_pp,
                         "D_pp change (pp)": comparisons.peak_to_peak_change_pp,
                         "within limits": comparisons.passes})


def study_rows(cases, study):
    return cases[cases.study.eq(study)].sort_values("parameter_value").copy()


# Typeset symbols for report prose; Streamlit and the PDF builder both render $...$.
D_MAX, D_PP = r"$D_{\max}$", r"$D_{pp}$"


def scientific(value):
    """Typeset a small number such as 1.2e-12 as 1.2 x 10^-12."""
    mantissa, exponent = f"{value:.1e}".split("e")
    return rf"${mantissa}\times10^{{{int(exponent)}}}$"


def summary_markdown(rows):
    columns = ["r", "d", "temperature_inner_c", "mean_inner_flux_w_m2",
               "max_deviation_percent", "peak_to_peak_percent", "heat_inner_w_m"]
    lines = [rf"| $r$ (m) | $d$ (m) | $T_B$ (°C) | $\bar q_B$ (W/m²) | {D_MAX} (%) | {D_PP} (%) | $Q'_B$ (W/m) |",
             "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for _, row in rows.iterrows():
        lines.append("| " + " | ".join(f"{row[c]:.6f}" if c not in columns[:3] else f"{row[c]:g}" for c in columns) + " |")
    return "\n".join(lines)


def discussion(cases, study):
    rows = study_rows(cases, study)
    a, b = rows.iloc[0], rows.iloc[-1]
    if study == "offset":
        return (rf"At fixed $r$ = 0.4 m and $T_B$ = 200 °C, increasing $d$ from {a.d:.2f} to {b.d:.2f} m "
                rf"increases {D_MAX} from zero to {b.max_deviation_percent:.3f}% and {D_PP} to {b.peak_to_peak_percent:.3f}%, "
                rf"while the mean flux $\bar q_B$ changes only from {a.mean_inner_flux_w_m2:.2f} to {b.mean_inner_flux_w_m2:.2f} W/m². "
                "The concentric case is the uniform-flux reference; all other points are eccentric. "
                "For these gray surfaces, the narrow-gap side of B loses less heat per unit area than the wide-gap side. "
                "Although A is isothermal, its radiosity is not uniform, because A also reflects the nonuniform radiation it receives from B. "
                r"The narrow-gap side of B therefore receives more irradiation $G_i$, and by equation (7), $q_i=\epsilon_B(\sigma T_B^4-G_i)$, "
                "a larger irradiation gives a smaller net outward flux. "
                "The pattern results from the coupled exchange in the whole enclosure, not from the local gap width alone.")
    if study == "radius":
        return (rf"At fixed $d$ = 0.3 m and $T_B$ = 200 °C, increasing $r$ from {a.r:.1f} to {b.r:.1f} m "
                rf"increases {D_MAX} from {a.max_deviation_percent:.3f}% to {b.max_deviation_percent:.3f}%. "
                rf"The mean flux $\bar q_B$ decreases from {a.mean_inner_flux_w_m2:.2f} to {b.mean_inner_flux_w_m2:.2f} W/m², "
                rf"while the heat rate per unit length $Q'_B$ rises from {a.heat_inner_w_m:.2f} to {b.heat_inner_w_m:.2f} W/m because the circumference of B grows. "
                r"With $d$ fixed, the normalized eccentricity $e=d/(R-r)$ rises from 0.375 to 0.750 and the minimum gap narrows from 0.50 to 0.10 m. "
                r"These results therefore describe radius changes at fixed center distance, not at fixed $e$.")
    return (rf"At fixed $r$ = 0.4 m and $d$ = 0.3 m, raising $T_B$ from {a.temperature_inner_c:g} to {b.temperature_inner_c:g} °C "
            rf"increases the mean flux $\bar q_B$ from {a.mean_inner_flux_w_m2:.2f} to {b.mean_inner_flux_w_m2:.2f} W/m², "
            f"a factor of {b.mean_inner_flux_w_m2/a.mean_inner_flux_w_m2:.2f}. "
            f"{D_MAX} stays at {a.max_deviation_percent:.6f}%; across the six temperatures it varies by only "
            f"{scientific(rows.max_deviation_percent.max()-rows.max_deviation_percent.min())} percentage points. "
            r"With fixed geometry and temperature-independent emissivities, the radiosity equations are linear and the flux scales with $\sigma(T_B^4-T_A^4)$, equation (14). "
            "The normalized angular profile is therefore unchanged. This would not hold for materials whose emissivity depends on temperature.")
