"""Render the selection evidence from completed numerical studies."""

from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def main():
    directory = Path("results/discretization")
    selected = json.loads((directory/"selected.json").read_text())
    outer, inner = selected["n_outer"], selected["n_inner"]
    cases = pd.read_csv(directory/"independent_cases.csv")
    comparisons = pd.read_csv(directory/f"qualification_{outer}_{inner}_comparisons.csv")
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "svg.hashsalt": "eccentric-cylinder-radiation"})
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.5), layout="constrained")
    rows = cases[cases.case.str.startswith("outer_")].sort_values("n_outer")
    axes[0].plot(rows.n_outer, rows.max_deviation_percent, "o-", color="#b45309")
    axes[0].set(xlabel="Outer segments, N_A", ylabel="Maximum deviation (%)",
                title="Outer refinement\nInner surface fixed at 128 segments")
    rows = pd.concat([cases[cases.case.str.startswith("inner_")], cases[cases.case == "outer_192_128"]]).sort_values("n_inner")
    axes[1].plot(rows.n_inner, rows.max_deviation_percent, "o-", color="#2563eb")
    axes[1].set(xlabel="Inner segments, N_B", ylabel="Maximum deviation (%)",
                title="Inner refinement\nOuter surface fixed at 192 segments")
    rows = comparisons[comparisons.point.str.startswith("eccentricity_")].sort_values("e")
    axes[2].plot(rows.e, rows.max_deviation_change_pp, "o-", label="Maximum-deviation change", color="#2563eb")
    axes[2].plot(rows.e, rows.peak_to_peak_change_pp, "s-", label="Peak-to-peak change", color="#b45309")
    axes[2].axhline(0.1, color="#64748b", linestyle="--", label="Acceptance threshold")
    axes[2].set(xlabel="Normalized eccentricity, e", ylabel="Change (percentage points)",
                title=f"Selected mesh {outer}/{inner}\nCompared with {2*outer}/{2*inner}", ylim=(-0.003, 0.11))
    axes[2].legend(fontsize=8, loc="upper left")
    for ax in axes:
        ax.grid(alpha=0.18)
    fig.savefig(directory/"discretization_selection.png", dpi=180)
    fig.savefig(directory/"discretization_selection.svg", metadata={"Date": None})
    svg_path = directory/"discretization_selection.svg"
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines())+"\n", encoding="utf-8")
    plt.close(fig)


if __name__ == "__main__":
    main()
