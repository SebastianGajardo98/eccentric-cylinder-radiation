"""Export the assignment's figures and written numerical report."""

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from study_data import DATA, MESH, ROOT, STUDIES, discussion, load_studies, study_rows, summary_markdown


def save_figure(fig, name):
    fig.savefig(DATA / f"{name}.png", dpi=170)
    fig.savefig(DATA / f"{name}.svg", metadata={"Date": None})
    svg = DATA / f"{name}.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n", encoding="utf-8")
    plt.close(fig)


def geometry_diagram():
    fig, ax = plt.subplots(figsize=(8, 6.5), layout="constrained")
    theta = np.linspace(0, 2*np.pi, 721)
    ax.plot(np.cos(theta), np.sin(theta), color="#475569", lw=2)
    ax.plot(.3+.4*np.cos(theta), .4*np.sin(theta), color="#b45309", lw=3)
    ax.scatter(np.cos(np.arange(12)*2*np.pi/12), np.sin(np.arange(12)*2*np.pi/12), s=23, color="#475569")
    ax.scatter(.3+.4*np.cos(np.arange(8)*2*np.pi/8), .4*np.sin(np.arange(8)*2*np.pi/8), s=23, color="#b45309")
    ax.scatter([0, .3], [0, 0], s=23, color="#475569")
    ax.text(0, .045, "$O_A$", ha="center")
    ax.text(.34, -.07, "$O_B$")
    ax.annotate("", (0, -.16), (.3, -.16), arrowprops={"arrowstyle": "<->", "color": "#475569"})
    ax.text(.15, -.23, "$d$", ha="center")
    ax.annotate("", (-1, 0), (0, 0), arrowprops={"arrowstyle": "<->", "color": "#64748b"})
    ax.text(-.55, .05, "$R=1$ m", ha="center")
    ax.annotate("", (.3, .4), (.3, 0), arrowprops={"arrowstyle": "<->", "color": "#64748b"})
    ax.text(.33, .18, "$r$")
    ax.text(-.60, .58, "Cylinder A\n$T_A=30$ °C", ha="center")
    ax.text(.48, -.20, "B\n$T_B>T_A$", ha="center")
    ax.text(-.57, -.47, "Vacuum\nDiffuse-gray walls", ha="center")
    ax.annotate("", (.3, .59), (.3, .4), arrowprops={"arrowstyle": "->", "color": "#b45309", "lw": 2})
    ax.text(.34, .55, "$n_B$")
    ax.annotate("", (0, .80), (0, 1), arrowprops={"arrowstyle": "->", "color": "#475569", "lw": 2})
    ax.text(-.04, .85, "$n_A$", ha="right")
    ax.plot([.3, .7], [0, 0], ":", color="#b45309", lw=1)
    angle = np.linspace(0, np.pi/3, 40)
    ax.plot(.3+.13*np.cos(angle), .13*np.sin(angle), color="#b45309")
    ax.text(.44, .11, "$\\theta_B$")
    ax.set(xlim=(-1.15, 1.15), ylim=(-1.1, 1.1), xlabel="x (m)", ylabel="y (m)", aspect="equal")
    ax.set_title("Cross-section and equal-arc discretization")
    ax.grid(alpha=.12)
    save_figure(fig, "geometry_and_segments")


def study_figures(cases, profiles):
    colors = plt.get_cmap("tab10")
    for study, (title, xlabel, _, _) in STUDIES.items():
        rows = study_rows(cases, study)
        fig, axes = plt.subplots(2, 2, figsize=(12, 8.2), layout="constrained")
        fig.suptitle(title+" — selected mesh 96/128, fixed emissivities 0.6/0.8", fontsize=13)
        axes[0, 0].plot(rows.parameter_value, rows.mean_inner_flux_w_m2, "o-", color="#b45309")
        axes[0, 0].set(xlabel=xlabel, ylabel="Mean net flux (W/m²)", ylim=(0, 1.1*rows.mean_inner_flux_w_m2.max()))
        axes[0, 1].plot(rows.parameter_value, rows.max_deviation_percent, "o-", label="Maximum absolute deviation")
        axes[0, 1].plot(rows.parameter_value, rows.peak_to_peak_percent, "s-", label="Peak-to-peak range")
        axes[0, 1].set(xlabel=xlabel, ylabel="Relative nonuniformity (%)", ylim=(0, max(1, 1.12*rows.peak_to_peak_percent.max())))
        axes[0, 1].legend(fontsize=8)
        for index, row in enumerate(rows.itertuples()):
            frame = profiles[profiles.case.eq(row.case)]
            label = f"{row.parameter_value:g}" + (" °C" if study == "temperature" else " m")
            axes[1, 0].plot(frame.angle_deg, frame.flux_w_m2, color=colors(index), label=label)
            axes[1, 1].plot(frame.angle_deg, frame.deviation_percent, color=colors(index), label=label)
        axes[1, 0].set(xlabel="Angle on B (degrees)", ylabel="Net flux (W/m²)", xlim=(0, 360))
        axes[1, 1].set(xlabel="Angle on B (degrees)", ylabel="Deviation from own mean (%)", xlim=(0, 360))
        axes[1, 1].axhline(0, ls="--", color="#64748b", lw=1)
        axes[1, 1].legend(fontsize=8, ncols=2, loc="lower center")
        if study == "temperature":
            axes[1, 1].set_title("Normalized profiles coincide", fontsize=10)
        for ax in axes.flat:
            ax.grid(alpha=.18)
        save_figure(fig, study+"_study")
    baseline = profiles[profiles.case.eq("baseline")]
    mean = cases[cases.case.eq("baseline")].iloc[0].mean_inner_flux_w_m2
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
    axes[0].plot(baseline.angle_deg, baseline.flux_w_m2, color="#b45309")
    axes[0].axhline(mean, color="#64748b", ls="--", label="Area-weighted mean")
    axes[0].set(ylabel="Net flux (W/m²)")
    axes[0].legend(fontsize=9)
    axes[1].plot(baseline.angle_deg, baseline.deviation_percent, color="#2563eb")
    axes[1].axhline(0, color="#64748b", ls="--")
    axes[1].set(ylabel="Deviation from mean (%)")
    for ax in axes:
        ax.set(xlabel="Angle on B (degrees)", xlim=(0, 360))
        ax.grid(alpha=.18)
    save_figure(fig, "baseline_flux")


def write_reports(selection, cases, profiles, manifest):
    baseline = cases[cases.case.eq("baseline")].iloc[0]
    sections = ["# Influence of radius, center distance and temperature", "",
        "All cases use N_A = 96, N_B = 128, source integration tolerance 1e-8, R = 1 m, T_A = 30 C, epsilon_A = 0.6 and epsilon_B = 0.8. Only the named parameter changes within each study. All reported q values are segment averages.", ""]
    for study, (title, _, _, _) in STUDIES.items():
        rows = study_rows(cases, study)
        sections += [f"## {title}", "", discussion(cases, study), "", summary_markdown(rows), "",
                     f"![{title} results](../results/studies/{study}_study.png)", ""]
    sections += ["## Numerical consistency", "",
        f"Across the 19 baseline/study cases, maximum relative energy imbalance is {cases.energy_imbalance_relative.max():.3e}, maximum view-factor closure residual is {cases.closure_max.max():.3e}, and maximum scaled reciprocity residual is {cases.reciprocity_relative_max.max():.3e}. These are consistency checks; mesh selection also uses finite-refinement comparisons.", "",
        "Reproduce with `python run_assignment.py`. Source fingerprints and raw tables are in results/studies/manifest.json, cases.csv and profiles.csv.", ""]
    parameters = "\n".join(sections)
    (ROOT / "docs" / "PARAMETERS.md").write_text(parameters, encoding="utf-8")
    model = (ROOT / "docs" / "MODEL.md").read_text(encoding="utf-8")
    selection_text = (ROOT / "docs" / "DISCRETIZATION.md").read_text(encoding="utf-8")
    def report_section(text, heading):
        body = text.split("\n", 1)[1].replace("\n## ", "\n### ")
        return heading+"\n"+body
    report = ["# Radiative heat transfer between eccentric cylinders", "",
        "Sebastian Alberto Gajardo Lobos · Heat and Mass Transfer (Radiative Heat Transfer)", "",
        "## Assignment statement", "",
        (ROOT / "docs" / "ASSIGNMENT.md").read_text(encoding="utf-8"), "",
        r"Temperature notation: $\vartheta_A$ and $\vartheta_B$ in the assignment are written as $T_A$ and $T_B$ in the report.", "",
        "## Objective and numerical scope", "",
        "Quantify deviation from uniform net heat-flux density on cylinder B using view factors, derive the thermodynamic model, select a surface discretization, and study r, d and T_B. Descriptions, diagrams, discussion, raw results and the corresponding program code accompany the analyses. The agreed submission scope does not include comparison against analytical solutions.", "",
        "![Geometry and surface segments](../results/studies/geometry_and_segments.png)", "",
        "Figure: working geometry. The displayed 12/8 segment boundaries illustrate the idea of equal-arc discretization; suitable calculation counts are assessed in the refinement study below.", "",
        (ROOT / "docs" / "GEOMETRY.md").read_text(encoding="utf-8"), "",
        report_section(model, "## Part (a): thermodynamic model"), "",
        report_section(selection_text, "## Part (a): discretization selection"), "",
        "![Independent mesh selection](../results/discretization/discretization_selection.png)", "",
        "![Selected-mesh baseline flux](../results/studies/baseline_flux.png)", "",
        report_section(parameters, "## Part (b): influence of physical parameters"), "",
        "## Part (c): discussion and conclusions", "",
        f"1. The diffuse-gray radiosity model produces a nonuniform q profile in the eccentric baseline: mean q = {baseline.mean_inner_flux_w_m2:.6f} W/m², maximum relative deviation = {baseline.max_deviation_percent:.6f}% and peak-to-peak range = {baseline.peak_to_peak_percent:.6f}%.",
        "2. Independent refinement of the two surfaces is necessary: stable total heat alone does not establish resolution of local nonuniformity. The selected 96/128 mesh passes the documented profile and metric-change criteria at all 12 geometry points, with an additional high-eccentricity check.",
        "3. At the stated fixed emissivities, increasing center distance or increasing radius at fixed center distance increases relative nonuniformity over the studied ranges. The two variations change enclosure geometry in different ways.",
        "4. Increasing prescribed inner temperature increases absolute flux, while normalized nonuniformity remains unchanged under the temperature-independent-emissivity model.",
        "5. Interactive motion and playback display successive steady states, not physical transient heating. Mirroring B across the y-axis mirrors its flux profile without changing scalar heat-rate or nonuniformity measures.", "",
        "## Limitations", "",
        "The finite-mesh criteria are practical differences between meshes, not rigorous bounds on the exact solution. Qualification applies to the listed geometry points and fixed emissivities. Arbitrary near-contact or different-emissivity explorations need their own convergence assessment. Prescribed isothermal infinite cylinders omit end effects, participating media and transient energy storage.", "",
        "## Code and reproduction", "",
        "The downloadable submission package contains this report, all figures and tables used here, the numerical module, study runners, website source, tests, requirements and a file-hash manifest. From its root directory:", "",
        "```powershell", "python -m pip install -r requirements-dev.txt", "python -m pytest -q",
        "python run_assignment.py", "python -m streamlit run streamlit_app.py", "```", "",
        f"Numerical solver SHA-256: `{manifest['solver_sha256']}`.", ""]
    (ROOT / "docs" / "REPORT.md").write_text("\n".join(report), encoding="utf-8")


def main():
    selected, cases, profiles, manifest = load_studies()
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "svg.hashsalt": "eccentric-cylinder-radiation"})
    geometry_diagram()
    study_figures(cases, profiles)
    write_reports(selected, cases, profiles, manifest)
    print("Exported geometry, baseline and three parameter-study figures, and the written report.")


if __name__ == "__main__":
    main()
