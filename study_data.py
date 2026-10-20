"""Read and validate the completed assignment studies, independently of the UI."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
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
    return hashlib.sha256((ROOT / "radiation.py").read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def text_hash(path):
    """Portable integrity check for text data checked out on Windows or Linux."""
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def load_studies():
    """Reject missing, mixed-version or incompletely generated report data."""
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    selection = json.loads((MESH / "selected.json").read_text(encoding="utf-8"))
    if manifest["solver_sha256"] != source_hash() or selection["solver_sha256"] != source_hash():
        raise ValueError("Study results do not match radiation.py. Run python run_assignment.py.")
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


def study_rows(cases, study):
    return cases[cases.study.eq(study)].sort_values("parameter_value").copy()


def summary_markdown(rows):
    columns = ["r", "d", "temperature_inner_c", "mean_inner_flux_w_m2",
               "max_deviation_percent", "peak_to_peak_percent", "heat_inner_w_m"]
    lines = ["| r (m) | d (m) | T_B (C) | Mean q (W/m^2) | D_max (%) | D_pp (%) | Q'_B (W/m) |",
             "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for _, row in rows.iterrows():
        lines.append("| " + " | ".join(f"{row[c]:.6f}" if c not in columns[:3] else f"{row[c]:g}" for c in columns) + " |")
    return "\n".join(lines)


def discussion(cases, study):
    rows = study_rows(cases, study)
    a, b = rows.iloc[0], rows.iloc[-1]
    if study == "offset":
        return (f"At fixed r = 0.4 m and T_B = 200 °C, increasing d from {a.d:.2f} to {b.d:.2f} m "
                f"increases D_max from approximately zero to {b.max_deviation_percent:.3f}%. "
                f"D_pp reaches {b.peak_to_peak_percent:.3f}%, while mean flux changes "
                f"from {a.mean_inner_flux_w_m2:.2f} to {b.mean_inner_flux_w_m2:.2f} W/m². "
                "The concentric point is a numerical reference; the other points are eccentric cases. "
                "For these gray-surface parameters, the narrow-gap side loses less net heat per area than the wide-gap side. "
                "A has uniform temperature but nonuniform radiosity because it also reflects the nonuniform irradiation from B. "
                "In these cases the near side of B receives more returning irradiation, reducing its net outward flux through q = epsilon_B (sigma T_B^4 - G_B). "
                "This is a coupled enclosure result, rather than a universal rule based on distance alone.")
    if study == "radius":
        return (f"At fixed d = 0.3 m and T_B = 200 °C, increasing r from {a.r:.1f} to {b.r:.1f} m "
                f"increases D_max from {a.max_deviation_percent:.3f}% to {b.max_deviation_percent:.3f}%. "
                f"Mean flux decreases from {a.mean_inner_flux_w_m2:.2f} to {b.mean_inner_flux_w_m2:.2f} W/m². "
                f"The total heat per unit length changes from {a.heat_inner_w_m:.2f} to {b.heat_inner_w_m:.2f} W/m because the circumference also changes. "
                "Holding d fixed makes normalized eccentricity increase from 0.375 to 0.750; the minimum gap decreases from 0.50 to 0.10 m. "
                "These conclusions describe radius variation at fixed center distance, not at fixed normalized eccentricity.")
    return (f"At fixed r = 0.4 m and d = 0.3 m, raising T_B from {a.temperature_inner_c:g} to {b.temperature_inner_c:g} °C "
            f"increases mean flux from {a.mean_inner_flux_w_m2:.2f} to {b.mean_inner_flux_w_m2:.2f} W/m² "
            f"(a factor of {b.mean_inner_flux_w_m2/a.mean_inner_flux_w_m2:.2f}). "
            f"D_max remains {a.max_deviation_percent:.6f}%: its observed range is "
            f"{rows.max_deviation_percent.max()-rows.max_deviation_percent.min():.2e} percentage points. "
            "With fixed geometry and temperature-independent emissivities, the linear radiosity equations scale absolute flux with the difference of fourth powers of temperature. "
            "The normalized angular shape therefore remains unchanged. This does not apply automatically to materials whose emissivity changes with temperature.")
