# Working parameters and discretization selection

## Working parameters

| Parameter | Baseline | Reason |
| --- | --- | --- |
| Outer radius R | 1 m | Prescribed by the assignment |
| Outer temperature T_A | 30 C | Prescribed by the assignment |
| Inner radius r | 0.4 m | Leaves room to vary radius and offset independently |
| Offset d | 0.3 m | e = 0.5; minimum gap 0.3 m, maximum gap 0.9 m |
| Inner temperature T_B | 200 C | A working hot-cylinder case above T_A |
| Emissivities epsilon_A / epsilon_B | 0.6 / 0.8 | Explicit gray-surface working assumptions, allowing diffuse reflections; no particular material is claimed |

Final one-parameter sweeps: e = 0, 0.15, 0.30, 0.45, 0.60, 0.75, 0.90 at r = 0.4 m; r = 0.2, 0.3, 0.4, 0.5, 0.6 m at fixed d = 0.3 m; T_B = 60 to 400 C at baseline geometry. Fix both emissivities throughout. The minimum gap among these geometry points is 0.06 m. The concentric point is a numerical boundary check and a useful starting point for the eccentricity sweep.

## How results from two calculations are compared

This is a numerical comparison after the radiation equations have been solved. It defines the **Profile change (%)** column; it is separate from the physical model in equations (1)–(14).

Call the first calculation $c$ and the more resolved calculation $f$. For a surface-refinement comparison, $f$ has more segments. For an integration-tolerance comparison, both segment counts stay fixed and $f$ uses the tighter tolerance.

Let $\widetilde q_c$ and $\widetilde q_f$ be the two B-flux curves obtained by straight-line, periodic interpolation of the calculated segment averages at their midpoint angles. Compare them at the same positions, $\theta_k=360^\circ k/4096$, for $k=0,\ldots,4095$:

$$
C_q=100\frac{\displaystyle\max_{k=0,\ldots,4095}
\left|\widetilde q_c(\theta_k)-\widetilde q_f(\theta_k)\right|}
{|\bar q_{B,f}|}.
\tag{C1}
$$

In words: find the largest separation between the two flux curves, divide by the more resolved calculation's mean flux from equation (12), and multiply by 100. This gives **Profile change (%)**.

The 4096 angles are a chosen comparison setting. They add no surface segments or new radiation solutions. Periodic interpolation connects the last angular values back to the first across 360° and 0°.

The other two change columns use the $D_{\max}$ and $D_{pp}$ values from equation (13), calculated from each solution's original segment averages:

$$
\Delta D_{\max}=|D_{\max,c}-D_{\max,f}|,\qquad
\Delta D_{pp}=|D_{pp,c}-D_{pp,f}|.
\tag{C2}
$$

These changes are measured in **percentage points (pp)**. Small changes support stability under refinement; they do not give a guaranteed bound on the error relative to the exact solution.

**Code:** [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `compare`, implements (C1), (C2), the 4096 comparison angles and periodic interpolation. The same function is used for the independent surface checks, integration-tolerance checks, 12-arrangement check and extra smallest-gap check.

## Independent baseline refinement

**Code:** [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `independent`, runs the surface and integration-tolerance cases using [`radiation.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/radiation.py).

The outer surface was refined through 24, 48, 96 and 192 segments with the inner surface held at 128. The inner surface was refined through 16, 32, 64 and 128 segments with the outer surface held at 192. This separates their effects; both surfaces were not simply increased together.

| Refinement | D_max change (percentage points) | D_pp change (percentage points) |
| --- | ---: | ---: |
| outer_24_128 to outer_48_128 | 0.051272 | 0.064188 |
| outer_48_128 to outer_96_128 | 0.012871 | 0.016035 |
| outer_96_128 to outer_192_128 | 0.003233 | 0.004028 |
| inner_192_16 to inner_192_32 | 0.140154 | 0.181613 |
| inner_192_32 to inner_192_64 | 0.035871 | 0.046180 |
| inner_192_64 to outer_192_128 | 0.009021 | 0.011595 |

The inner 16-to-32 refinement fails the 0.1 percentage-point criterion. Finer meshes stabilize. Although the baseline alone permits smaller grids, the choice must also cover the larger offsets in part (b).

## Qualification across the study points

Accept changes below 0.5% in the maximum difference of interpolated flux profiles, and below 0.1 percentage points in both D_max and D_pp. Normalize profile differences by the refined grid's mean inner flux. Periodic interpolation uses a shared 4096-angle grid and segment averages; it is a comparison method, not an exact pointwise solution.

Each of the 12 distinct geometry points was compared at 96/128 and 192/256 segments. All pass the three criteria.

**Code:** [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `qualify`, runs these arrangements and compares both meshes using `compare`.

| Study point | e | Profile change (%) | D_max change (pp) | D_pp change (pp) |
| --- | ---: | ---: | ---: | ---: |
| baseline | 0.500 | 0.005695 | 0.005491 | 0.006929 |
| eccentricity_0 | 0.000 | 0.000000 | 0.000000 | 0.000000 |
| eccentricity_1 | 0.150 | 0.000800 | 0.000787 | 0.001313 |
| eccentricity_2 | 0.300 | 0.002126 | 0.002070 | 0.002994 |
| eccentricity_3 | 0.450 | 0.004494 | 0.004342 | 0.005641 |
| eccentricity_4 | 0.600 | 0.009133 | 0.008783 | 0.010556 |
| eccentricity_5 | 0.750 | 0.019427 | 0.018657 | 0.021227 |
| eccentricity_6 | 0.900 | 0.047166 | 0.045451 | 0.049711 |
| radius_0 | 0.375 | 0.001987 | 0.001891 | 0.002530 |
| radius_1 | 0.429 | 0.003578 | 0.003429 | 0.004453 |
| radius_3 | 0.600 | 0.008398 | 0.008140 | 0.009991 |
| radius_4 | 0.750 | 0.011441 | 0.011134 | 0.013361 |

## Why the inner grid was increased from 64 to 128

At e = 0.9, the coarser 96/64 mesh passes comparison with 192/128. Its D_pp nevertheless differs from the additional 384/256 reference by 0.102032 percentage points, just above the threshold. Increasing the inner grid to 128 reduces the difference to 0.059172 percentage points and the profile difference to 0.056176%. This additional check avoids relying on a marginal first comparison.

**Code:** [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `worst_case`, runs these additional resolutions at the same smallest-gap arrangement.

## Integration and temperature checks

At 96/64 baseline resolution, tightening source integration from 1e-6 through 1e-9 changes the nonuniformity metrics by less than 2e-9 percentage points between successive tolerances. At the selected 96/128 resolution, a 1e-8 versus 1e-9 check was also run at the baseline and at e = 0.9.

- baseline: profile change 1.658e-11%; D_pp change 1.274e-11 percentage points.
- high_eccentricity: profile change 2.629e-10%; D_pp change 2.937e-11 percentage points.

Temperature checks at 60, 200 and 400 C, for both baseline and e = 0.9 geometry, leave the normalized nonuniformity unchanged to approximately 2e-12 percentage points. This agrees with the linear fixed-emissivity model: temperature scales absolute flux through the difference in fourth powers. It does not justify temperature-independent results if material emissivity varies with temperature.

Across the selected-mesh qualification and reference cases, the maximum relative enclosure energy imbalance is 4.470e-12, maximum row-closure residual is 7.883e-15, and maximum scaled reciprocity residual is 5.773e-08.

## Decision based on the refinement evidence

Use **96 equal angular segments on cylinder A and 128 on cylinder B**, with source-arc integration tolerance **1e-8**, for the documented final parameter-study points. The interactive simulation uses a coarser 24/32 mesh for speed and is not part of the reported results.

**Code:** [`finalize_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/finalize_discretization.py) checks the recorded evidence and saves the selected settings. [`plot_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/plot_discretization.py) draws the selection-evidence figure.

## Selected-mesh baseline result

- Mean inner flux: 1549.473679 W/m^2.
- D_max: 4.734188%.
- D_pp: 8.206598%.
- Heat from B per unit length: 3894.252103 W/m.

## Scope and reproducibility

The selection is supported at the specified geometry points with emissivities 0.6/0.8. It is not a rigorous error bound, a proof for all continuous intermediate values, or qualification of arbitrary radius/offset/emissivity combinations. The site remains interactive; user-selected cases outside the documented points can be checked using independent refinement.

The numerical scope follows the requested assignment requirements. The interpretation of all three required parameter studies is presented in PARAMETERS.md.

Run the following from the repository directory (local caches in tmp/ make repeat runs faster):

```powershell
python scripts/run_discretization.py --stage independent
python scripts/run_discretization.py --stage worst-case
python scripts/run_discretization.py --stage qualify --outer 96 --inner 128
python scripts/run_discretization.py --stage support --outer 96 --inner 128
python scripts/finalize_discretization.py
python scripts/plot_discretization.py
```

Raw case tables, angular profiles, comparison tables, source fingerprints, and selected settings are stored in results/discretization/. The completed parameter studies use this selected mesh; see PARAMETERS.md and REPORT.md.
