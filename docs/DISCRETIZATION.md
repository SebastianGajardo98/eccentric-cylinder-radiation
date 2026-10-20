# Working parameters and discretization selection

## Working parameters

| Parameter | Baseline | Reason |
| --- | --- | --- |
| Outer radius $R$ | 1 m | Prescribed by the assignment |
| Outer temperature $T_A$ | 30 °C | Prescribed by the assignment |
| Inner radius $r$ | 0.4 m | Leaves room to vary radius and center distance independently |
| Center distance $d$ | 0.3 m | $e = 0.5$; minimum gap 0.3 m, maximum gap 0.9 m |
| Inner temperature $T_B$ | 200 °C | A working hot-cylinder case above $T_A$ |
| Emissivities $\epsilon_A$ / $\epsilon_B$ | 0.6 / 0.8 | Gray-surface working values that allow diffuse reflections; no particular material is assumed |

Final one-parameter sweeps: $e$ = 0, 0.15, 0.30, 0.45, 0.60, 0.75 and 0.90 at $r$ = 0.4 m; $r$ = 0.2, 0.3, 0.4, 0.5 and 0.6 m at $d$ = 0.3 m; $T_B$ = 60 to 400 °C at the working geometry. Both emissivities stay fixed throughout. The smallest gap among these geometry points is 0.06 m. The concentric point is the uniform-flux reference and the starting point of the eccentricity sweep.

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

| Refinement (A/B segments) | $D_{\max}$ change (percentage points) | $D_{pp}$ change (percentage points) |
| --- | ---: | ---: |
| 24/128 to 48/128 | 0.051272 | 0.064188 |
| 48/128 to 96/128 | 0.012871 | 0.016035 |
| 96/128 to 192/128 | 0.003233 | 0.004028 |
| 192/16 to 192/32 | 0.140154 | 0.181613 |
| 192/32 to 192/64 | 0.035871 | 0.046180 |
| 192/64 to 192/128 | 0.009021 | 0.011595 |

The inner 16-to-32 refinement fails the 0.1 percentage-point criterion. Finer meshes stabilize. Although the baseline alone permits smaller grids, the choice must also cover the larger offsets in part (b).

## Qualification across the study points

Accept changes below 0.5% in the maximum difference of interpolated flux profiles, and below 0.1 percentage points in both $D_{\max}$ and $D_{pp}$. Normalize profile differences by the refined grid's mean inner flux. Periodic interpolation uses a shared 4096-angle grid and segment averages; it is a comparison method, not an exact pointwise solution.

Each of the 12 distinct geometry points was compared at 96/128 and 192/256 segments. All pass the three criteria.

**Code:** [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `qualify`, runs these arrangements and compares both meshes using `compare`.

| $r$ (m) | $d$ (m) | $e$ | Profile change (%) | $D_{\max}$ change (pp) | $D_{pp}$ change (pp) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.40 | 0.30 | 0.500 | 0.005695 | 0.005491 | 0.006929 |
| 0.40 | 0.00 | 0.000 | 0.000000 | 0.000000 | 0.000000 |
| 0.40 | 0.09 | 0.150 | 0.000800 | 0.000787 | 0.001313 |
| 0.40 | 0.18 | 0.300 | 0.002126 | 0.002070 | 0.002994 |
| 0.40 | 0.27 | 0.450 | 0.004494 | 0.004342 | 0.005641 |
| 0.40 | 0.36 | 0.600 | 0.009133 | 0.008783 | 0.010556 |
| 0.40 | 0.45 | 0.750 | 0.019427 | 0.018657 | 0.021227 |
| 0.40 | 0.54 | 0.900 | 0.047166 | 0.045451 | 0.049711 |
| 0.20 | 0.30 | 0.375 | 0.001987 | 0.001891 | 0.002530 |
| 0.30 | 0.30 | 0.429 | 0.003578 | 0.003429 | 0.004453 |
| 0.50 | 0.30 | 0.600 | 0.008398 | 0.008140 | 0.009991 |
| 0.60 | 0.30 | 0.750 | 0.011441 | 0.011134 | 0.013361 |

## Why the inner grid was increased from 64 to 128

At $e = 0.9$, the coarser 96/64 mesh passes comparison with 192/128. Its $D_{pp}$ nevertheless differs from the additional 384/256 reference by 0.102032 percentage points, just above the threshold. Increasing the inner grid to 128 reduces the difference to 0.059172 percentage points and the profile difference to 0.056176%. This additional check avoids relying on a marginal first comparison.

**Code:** [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `worst_case`, runs these additional resolutions at the same smallest-gap arrangement.

## Integration and temperature checks

At 96/64 resolution in the working case, tightening the integration tolerance from $10^{-6}$ to $10^{-9}$ changes the nonuniformity measures by less than $2\times10^{-9}$ percentage points between successive tolerances. At the selected 96/128 resolution, tolerances $10^{-8}$ and $10^{-9}$ were also compared in the working case and at $e = 0.9$.

- Working case: profile change $1.7\times10^{-11}$%; $D_{pp}$ change $1.3\times10^{-11}$ percentage points.
- Largest center distance ($e = 0.9$): profile change $2.6\times10^{-10}$%; $D_{pp}$ change $2.9\times10^{-11}$ percentage points.

Temperature checks at 60, 200 and 400 °C, in the working case and at $e = 0.9$, leave the normalized nonuniformity unchanged to within about $2\times10^{-12}$ percentage points. This agrees with the linear fixed-emissivity model, in which temperature scales the absolute flux through $\sigma(T_B^4-T_A^4)$, equation (14). It would not hold if the emissivity varied with temperature.

Across the selected-mesh qualification and reference cases, the largest relative energy imbalance is $4.5\times10^{-12}$, the largest row-closure residual is $7.9\times10^{-15}$, and the largest scaled reciprocity residual is $5.8\times10^{-8}$.

## Decision based on the refinement evidence

Use **96 equal angular segments on cylinder A and 128 on cylinder B**, with integration tolerance $10^{-8}$, for the documented final parameter-study points. The interactive simulation uses a coarser 24/32 mesh for speed and is not part of the reported results.

**Code:** [`finalize_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/finalize_discretization.py) checks the recorded evidence and saves the selected settings. [`plot_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/plot_discretization.py) draws the selection-evidence figure.

## Selected-mesh baseline result

- Mean flux on B, $\bar q_B$: 1549.473679 W/m².
- $D_{\max}$: 4.734188%.
- $D_{pp}$: 8.206598%.
- Heat from B per unit length, $Q'_B$: 3894.252103 W/m.

## Scope and reproducibility

The selection is supported at the 12 documented geometry points with $\epsilon_A = 0.6$ and $\epsilon_B = 0.8$. The comparisons are differences between meshes, not rigorous error bounds, and they do not qualify other radius, offset or emissivity combinations. The interactive simulation uses a coarser mesh and is for exploration only.

The interpretation of all three parameter studies is presented in PARAMETERS.md.

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
