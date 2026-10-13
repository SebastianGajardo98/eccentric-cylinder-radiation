"""Reproduce a first convergence study without Streamlit.

Run: python run_example.py
Outputs provisional study data to results/example/. No final mesh selection
is assumed; the output is evidence to discuss before part (b).
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd

from radiation import Geometry, calculate_view_factors, solve_radiation


def main():
    directory = Path("results/example")
    directory.mkdir(parents=True, exist_ok=True)
    thermal = {"temperature_outer_k": 303.15, "temperature_inner_k": 473.15,
               "emissivity_outer": 0.6, "emissivity_inner": 0.8}
    records = []
    previous_profile = None
    for outer, inner in [(12, 8), (24, 16), (48, 32), (96, 64)]:
        geometry = Geometry(n_outer=outer, n_inner=inner)
        model = calculate_view_factors(geometry, 1e-8)
        result = solve_radiation(model, **thermal)
        angles = np.degrees(model.angles[outer:])
        profile = pd.DataFrame({"angle_deg": angles, "flux_w_m2": result.inner_flux})
        profile.to_csv(directory / f"profile_{outer}_{inner}.csv", index=False)
        shared = np.linspace(0, 360, 720, endpoint=False)
        sampled = np.interp(shared, angles, result.inner_flux, period=360)
        record = {"n_outer": outer, "n_inner": inner, **result.metrics, **model.diagnostics}
        if previous_profile is not None:
            record["profile_change_percent"] = float(100 * np.max(np.abs(sampled-previous_profile)) / abs(result.metrics["mean_inner_flux_w_m2"]))
            record["deviation_change_pp"] = abs(result.metrics["max_deviation_percent"] - records[-1]["max_deviation_percent"])
        records.append(record)
        previous_profile = sampled
        print(json.dumps(record), flush=True)
    pd.DataFrame(records).to_csv(directory / "convergence.csv", index=False)
    metadata = {"R_m": 1.0, "r_m": 0.4, "d_m": 0.3, "integration_tolerance": 1e-8, **thermal,
                "status": "Provisional example; final discretization not yet selected.",
                "profile_comparison": "Periodic linear interpolation of segment-average flux to 720 angles."}
    (directory / "parameters.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
