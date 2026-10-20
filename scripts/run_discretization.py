"""Reproducible independent refinement and mesh qualification for part (a).

Usage: python scripts/run_discretization.py --stage independent
       python scripts/run_discretization.py --stage qualify --outer 96 --inner 128

Computational caches are local to tmp/; all physical outputs include parameters,
diagnostics and source fingerprints.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
import hashlib
import json
import time

import numpy as np
import pandas as pd

from radiation import Geometry, ViewFactors, calculate_view_factors, solve_radiation
from study_data import MESH as OUTPUT, ROOT, SCRIPTS, source_hash

CACHE = ROOT / "tmp" / "view_factor_cache"
THERMAL = dict(temperature_outer_k=303.15, temperature_inner_k=473.15,
               emissivity_outer=0.6, emissivity_inner=0.8)
PROFILE_LIMIT = 0.5
METRIC_LIMIT = 0.1


def load_view_factors(g, tol):
    """Return view factors for this geometry, reusing the local cache when possible."""
    key = json.dumps([asdict(g), tol, source_hash()], sort_keys=True)
    cache = CACHE / (hashlib.sha256(key.encode()).hexdigest() + ".npz")
    cache.parent.mkdir(parents=True, exist_ok=True)
    # Reuse an older cache only when its raw-byte fingerprint matches the
    # current source exactly. The new key canonicalizes line endings.
    if not cache.exists():
        raw_hash = hashlib.sha256((SCRIPTS / "radiation.py").read_bytes()).hexdigest()
        legacy_key = json.dumps([asdict(g), tol, raw_hash], sort_keys=True)
        legacy = cache.parent / (hashlib.sha256(legacy_key.encode()).hexdigest()+".npz")
        if legacy.exists():
            cache.write_bytes(legacy.read_bytes())
    cached = cache.exists()
    if cached:
        with np.load(cache) as saved:
            model = ViewFactors(g, saved["factors"], saved["areas"], saved["angles"], tol, float(saved["error"]))
    else:
        model = calculate_view_factors(g, tol)
        np.savez_compressed(cache, factors=model.factors, areas=model.areas,
                            angles=model.angles, error=model.estimated_integration_error)
    return model, cached


def run_case(spec):
    g = Geometry(r=spec["r"], d=spec["d"], n_outer=spec["n_outer"], n_inner=spec["n_inner"])
    tol = spec.get("tolerance", 1e-8)
    fingerprint = source_hash()
    start = time.perf_counter()
    model, cached = load_view_factors(g, tol)
    thermal = dict(THERMAL, temperature_inner_k=spec.get("temperature_inner_k", 473.15))
    result = solve_radiation(model, **thermal)
    record = {**spec, "tolerance": tol, "R": 1.0, **thermal,
              **result.metrics, **model.diagnostics,
              "elapsed_seconds": time.perf_counter()-start, "cached": cached,
              "solver_sha256": fingerprint}
    angles = np.degrees(model.angles[g.n_outer:])
    return record, angles, result.inner_flux


def execute(specs, prefix, workers):
    results = {}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        pending = {pool.submit(run_case, spec): spec for spec in specs}
        for future in as_completed(pending):
            record, angles, flux = future.result()
            case = record["case"]
            results[case] = (record, angles, flux)
            pd.DataFrame({"angle_deg": angles, "flux_w_m2": flux}).to_csv(OUTPUT/f"{prefix}_{case}_profile.csv", index=False)
            pd.DataFrame([x[0] for x in results.values()]).to_csv(OUTPUT/f"{prefix}_cases.csv", index=False)
            print(json.dumps({"completed": case, "elapsed_s": round(record["elapsed_seconds"], 2),
                              "max_deviation_percent": record["max_deviation_percent"],
                              "peak_to_peak_percent": record["peak_to_peak_percent"],
                              "energy_residual": record["energy_imbalance_relative"]}), flush=True)
    return results


def compare(coarse, fine):
    a, theta_a, flux_a = coarse
    b, theta_b, flux_b = fine
    theta = np.linspace(0, 360, 4096, endpoint=False)
    error = np.max(np.abs(np.interp(theta, theta_a, flux_a, period=360)-np.interp(theta, theta_b, flux_b, period=360)))
    row = {"coarse": a["case"], "fine": b["case"],
           "profile_change_percent": float(100*error/abs(b["mean_inner_flux_w_m2"])),
           "mean_change_percent": float(100*abs(a["mean_inner_flux_w_m2"]-b["mean_inner_flux_w_m2"])/abs(b["mean_inner_flux_w_m2"])),
           "max_deviation_change_pp": abs(a["max_deviation_percent"]-b["max_deviation_percent"]),
           "peak_to_peak_change_pp": abs(a["peak_to_peak_percent"]-b["peak_to_peak_percent"])}
    row["passes"] = (row["profile_change_percent"] < PROFILE_LIMIT
                     and row["max_deviation_change_pp"] < METRIC_LIMIT
                     and row["peak_to_peak_change_pp"] < METRIC_LIMIT)
    return row


def independent(workers):
    specs = []
    for outer in (24, 48, 96, 192):
        specs.append(dict(case=f"outer_{outer}_128", r=0.4, d=0.3, n_outer=outer, n_inner=128))
    for inner in (16, 32, 64, 128):
        # Reuse the same (192,128) result, rather than compute it twice.
        if inner != 128:
            specs.append(dict(case=f"inner_192_{inner}", r=0.4, d=0.3, n_outer=192, n_inner=inner))
    for power in (6, 7, 8, 9):
        specs.append(dict(case=f"tolerance_{power}", r=0.4, d=0.3, n_outer=96, n_inner=64, tolerance=10.0**(-power)))
    results = execute(specs, "independent", workers)
    groups = {"outer": [f"outer_{n}_128" for n in (24, 48, 96, 192)],
              "inner": [f"inner_192_{n}" for n in (16, 32, 64)] + ["outer_192_128"],
              "integration": [f"tolerance_{p}" for p in (6, 7, 8, 9)]}
    comparisons = []
    for group, cases in groups.items():
        for coarse, fine in zip(cases[:-1], cases[1:]):
            comparisons.append(dict(study=group, **compare(results[coarse], results[fine])))
    pd.DataFrame(comparisons).to_csv(OUTPUT/"independent_comparisons.csv", index=False)
    print(pd.DataFrame(comparisons).to_string(index=False), flush=True)


def qualify(outer, inner, workers):
    points = [("baseline", 0.4, 0.3)]
    points += [(f"eccentricity_{index}", 0.4, float(e)*0.6) for index, e in enumerate(np.linspace(0, 0.9, 7))]
    points += [(f"radius_{index}", float(r), 0.3) for index, r in enumerate(np.linspace(0.2, 0.6, 5)) if not np.isclose(r, 0.4)]
    specs = []
    for name, r, d in points:
        for label, na, nb in [("candidate", outer, inner), ("refined", 2*outer, 2*inner)]:
            specs.append(dict(case=f"{name}_{label}", point=name, mesh=label, r=r, d=d, n_outer=na, n_inner=nb))
    prefix = f"qualification_{outer}_{inner}"
    results = execute(specs, prefix, workers)
    comparisons = []
    for name, r, d in points:
        comparisons.append(dict(point=name, r=r, d=d, e=d/(1-r),
                                **compare(results[f"{name}_candidate"], results[f"{name}_refined"])))
    table = pd.DataFrame(comparisons)
    table.to_csv(OUTPUT/f"{prefix}_comparisons.csv", index=False)
    print(table.to_string(index=False), flush=True)
    print("ALL PASS:", bool(table.passes.all()), flush=True)


def worst_case(workers):
    specs = [dict(case=name, r=0.4, d=0.54, n_outer=na, n_inner=nb)
             for name, na, nb in [("coarse", 96, 64), ("outer_refined", 192, 64),
                                 ("inner_refined", 96, 128), ("both_refined", 192, 128),
                                 ("further_refined", 384, 256)]]
    results = execute(specs, "worst_case", workers)
    pairs = [("coarse", "outer_refined"), ("coarse", "inner_refined"),
             ("coarse", "both_refined"), ("coarse", "further_refined"),
             ("both_refined", "further_refined"), ("outer_refined", "further_refined"),
             ("inner_refined", "further_refined")]
    table = pd.DataFrame([dict(comparison=a+" vs "+b, **compare(results[a], results[b])) for a, b in pairs])
    table.to_csv(OUTPUT/"worst_case_comparisons.csv", index=False)
    print(table.to_string(index=False), flush=True)


def supporting_checks(outer, inner, workers):
    specs = []
    for name, d in [("baseline", 0.3), ("high_eccentricity", 0.54)]:
        for celsius in (60, 200, 400):
            specs.append(dict(case=f"{name}_temperature_{celsius}", r=0.4, d=d,
                              n_outer=outer, n_inner=inner, temperature_inner_k=celsius+273.15))
        for power in (8, 9):
            specs.append(dict(case=f"{name}_integration_{power}", r=0.4, d=d,
                              n_outer=outer, n_inner=inner, tolerance=10.0**(-power)))
    prefix = f"support_{outer}_{inner}"
    results = execute(specs, prefix, workers)
    rows = []
    for name in ("baseline", "high_eccentricity"):
        rows.append(dict(check="integration", point=name,
                         **compare(results[f"{name}_integration_8"], results[f"{name}_integration_9"])))
        group = [results[f"{name}_temperature_{t}"][0] for t in (60, 200, 400)]
        rows.append(dict(check="temperature_scaling", point=name,
                         max_deviation_range_pp=np.ptp([r["max_deviation_percent"] for r in group]),
                         peak_to_peak_range_pp=np.ptp([r["peak_to_peak_percent"] for r in group])))
    pd.DataFrame(rows).to_csv(OUTPUT/f"{prefix}_comparisons.csv", index=False)
    print(pd.DataFrame(rows).to_string(index=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["independent", "qualify", "worst-case", "support"], required=True)
    parser.add_argument("--outer", type=int, default=96)
    parser.add_argument("--inner", type=int, default=64)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    if args.stage == "independent":
        independent(args.workers)
    elif args.stage == "qualify":
        qualify(args.outer, args.inner, args.workers)
    elif args.stage == "worst-case":
        worst_case(args.workers)
    else:
        supporting_checks(args.outer, args.inner, args.workers)
