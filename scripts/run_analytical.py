"""Compare the selected-mesh solver with the closed-form limits in part (c).

The assignment states that the flux on B is uniform for concentric cylinders and
for black surfaces. Both limits, and the whole-body view factors at every center
distance, have closed-form values; equations (A1)-(A4) are in docs/ANALYTICAL.md.
The eccentric diffuse-gray case has no closed form.

Usage: python scripts/run_analytical.py
"""

import json

import numpy as np
import pandas as pd

from radiation import SIGMA, Geometry, solve_radiation
from run_discretization import load_view_factors
from study_data import ANALYTICAL, MESH, source_hash

T_A, T_B = 303.15, 473.15
CONCENTRIC_EMISSIVITIES = [(0.6, 0.8), (0.3, 0.9), (0.9, 0.3), (0.1, 0.1)]


def concentric_flux(r, emissivity_outer, emissivity_inner, R=1.0):
    """Equation (A4): uniform net flux on B between concentric diffuse-gray cylinders."""
    return SIGMA*(T_B**4-T_A**4)/(1/emissivity_inner + r/R*(1/emissivity_outer-1))


def whole_body_factors(model):
    """Area-weighted sums of the arc factors, for comparison with equation (A1)."""
    n = model.geometry.n_outer
    a, factors = model.areas, model.factors
    from_a = a[:n] @ factors[:n] / a[:n].sum()
    from_b = a[n:] @ factors[n:] / a[n:].sum()
    return {"F_BA": float(from_b[:n].sum()), "F_AB": float(from_a[n:].sum()), "F_AA": float(from_a[:n].sum())}


def comparison(check, point, quantity, analytical, numerical, **conditions):
    difference = numerical-analytical
    return {"check": check, "point": point["point"], "r": point["r"], "d": point["d"], **conditions,
            "quantity": quantity, "analytical": analytical, "numerical": numerical, "difference": difference,
            "relative_difference": abs(difference)/abs(analytical) if analytical else np.nan}


def main():
    selected = json.loads((MESH / "selected.json").read_text(encoding="utf-8"))
    if selected["solver_sha256"] != source_hash():
        raise ValueError("Re-run the discretization qualification before the analytical comparison.")
    mesh = {"n_outer": selected["n_outer"], "n_inner": selected["n_inner"]}
    tolerance = selected["integration_tolerance"]
    rows = []
    for point in selected["qualified_geometry_points"]:
        model, _ = load_view_factors(Geometry(r=point["r"], d=point["d"], **mesh), tolerance)
        factors = whole_body_factors(model)
        for name, exact in (("F_BA", 1.0), ("F_AB", point["r"]), ("F_AA", 1-point["r"])):  # R = 1 m
            rows.append(comparison("view_factors", point, name, exact, factors[name]))
        black = solve_radiation(model, T_A, T_B, 1.0, 1.0).metrics
        conditions = {"emissivity_outer": 1.0, "emissivity_inner": 1.0}
        rows.append(comparison("black_body", point, "mean_inner_flux_w_m2", SIGMA*(T_B**4-T_A**4),
                               black["mean_inner_flux_w_m2"], **conditions))
        rows.append(comparison("black_body", point, "max_deviation_percent", 0.0, black["max_deviation_percent"], **conditions))
        if point["d"] == 0:
            for emissivity_outer, emissivity_inner in CONCENTRIC_EMISSIVITIES:
                gray = solve_radiation(model, T_A, T_B, emissivity_outer, emissivity_inner).metrics
                conditions = {"emissivity_outer": emissivity_outer, "emissivity_inner": emissivity_inner}
                rows.append(comparison("concentric_gray", point, "mean_inner_flux_w_m2",
                                       concentric_flux(point["r"], emissivity_outer, emissivity_inner),
                                       gray["mean_inner_flux_w_m2"], **conditions))
                rows.append(comparison("concentric_gray", point, "max_deviation_percent", 0.0,
                                       gray["max_deviation_percent"], **conditions))
    table = pd.DataFrame(rows).assign(temperature_outer_k=T_A, temperature_inner_k=T_B, tolerance=tolerance,
                                      solver_sha256=source_hash(), **mesh)
    ANALYTICAL.mkdir(parents=True, exist_ok=True)
    table.to_csv(ANALYTICAL / "comparison.csv", index=False, lineterminator="\n")
    flux = table[table.quantity.eq("mean_inner_flux_w_m2")]
    print(f"{len(table)} comparisons; largest relative flux difference {flux.relative_difference.max():.3e}.", flush=True)


if __name__ == "__main__":
    main()
