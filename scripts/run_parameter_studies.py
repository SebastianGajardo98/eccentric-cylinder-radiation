"""Generate all three required part (b) studies with the selected mesh."""

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import platform

import numpy as np
import pandas as pd
import scipy

from run_discretization import run_case
from study_data import DATA, MESH, SCRIPTS, load_studies, source_hash, text_hash


def main(workers=3):
    selected = json.loads((MESH / "selected.json").read_text(encoding="utf-8"))
    if selected["solver_sha256"] != source_hash():
        raise ValueError("Re-run the discretization qualification before generating part (b).")
    base = dict(r=0.4, d=0.3, n_outer=selected["n_outer"], n_inner=selected["n_inner"],
                tolerance=selected["integration_tolerance"])
    specs = [dict(base, case="baseline", study="baseline", parameter_value=0.0)]
    specs += [dict(base, case=f"offset_{i}", study="offset", d=float(e)*0.6,
                   parameter_value=float(e)*0.6) for i, e in enumerate(np.linspace(0, 0.9, 7))]
    specs += [dict(base, case=f"radius_{i}", study="radius", r=float(r),
                   parameter_value=float(r)) for i, r in enumerate(np.linspace(0.2, 0.6, 5))]
    specs += [dict(base, case=f"temperature_{t}", study="temperature", temperature_inner_k=t+273.15,
                   parameter_value=float(t)) for t in (60, 100, 150, 200, 300, 400)]
    records, profiles = [], []
    DATA.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for record, angles, flux in pool.map(run_case, specs):
            record.update(temperature_inner_c=record["temperature_inner_k"]-273.15,
                          e=record["d"]/(record["R"]-record["r"]),
                          minimum_gap_m=record["R"]-record["r"]-record["d"])
            records.append(record)
            profiles.append(pd.DataFrame({"case": record["case"], "study": record["study"],
                "parameter_value": record["parameter_value"], "angle_deg": angles, "flux_w_m2": flux,
                "deviation_percent": 100*(flux-record["mean_inner_flux_w_m2"])/abs(record["mean_inner_flux_w_m2"])}))
            print(f"Completed {record['case']}: deviation {record['max_deviation_percent']:.6f}%", flush=True)
    pd.DataFrame(records).to_csv(DATA / "cases.csv", index=False, lineterminator="\n")
    pd.concat(profiles, ignore_index=True).to_csv(DATA / "profiles.csv", index=False, lineterminator="\n")
    manifest = {
        "solver_sha256": source_hash(), "generator_sha256": hashlib.sha256((SCRIPTS / "run_parameter_studies.py").read_text(encoding="utf-8").encode("utf-8")).hexdigest(),
        "n_outer": selected["n_outer"], "n_inner": selected["n_inner"],
        "integration_tolerance": selected["integration_tolerance"], "case_count": len(records),
        "temperature_inner_c": [60, 100, 150, 200, 300, 400],
        "emissivities": {"outer": 0.6, "inner": 0.8},
        "data_sha256": {p: text_hash(DATA / p) for p in ("cases.csv", "profiles.csv")},
        "text_hash_format": "SHA-256 of UTF-8 text with canonical LF line endings",
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "pandas": pd.__version__},
        "scope": "Three one-parameter studies at the qualified geometry points; all cases use the same selected mesh.",
    }
    (DATA / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    load_studies()
    print("All 19 cases and their profiles passed the report-data checks.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=3)
    main(parser.parse_args().workers)
