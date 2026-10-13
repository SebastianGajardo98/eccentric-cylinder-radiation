# Working parameters and discretization selection

## Decision

Use **96 equal angular segments on cylinder A and 128 on cylinder B**, with source-arc integration tolerance **1e-8**, for the documented final parameter-study points. This is a recommended study setting; the interactive app keeps Preview and Custom resolutions available.

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

## Independent baseline refinement

The outer surface was refined through 24, 48, 96 and 192 segments with the inner surface held at 128. The inner surface was refined through 16, 32, 64 and 128 segments with the outer surface held at 192. This separates their effects; both surfaces were not simply increased together.

| Refinement | Maximum-deviation change (percentage points) | Peak-to-peak change (percentage points) |
| --- | ---: | ---: |
| outer_24_128 to outer_48_128 | 0.051272 | 0.064188 |
| outer_48_128 to outer_96_128 | 0.012871 | 0.016035 |
| outer_96_128 to outer_192_128 | 0.003233 | 0.004028 |
| inner_192_16 to inner_192_32 | 0.140154 | 0.181613 |
| inner_192_32 to inner_192_64 | 0.035871 | 0.046180 |
| inner_192_64 to outer_192_128 | 0.009021 | 0.011595 |

The inner 16-to-32 refinement fails the 0.1 percentage-point criterion. Finer meshes stabilize. Although the baseline alone permits smaller grids, the choice must also cover the larger offsets in part (b).

## Qualification across the study points

Accept changes below 0.5% in the maximum difference of interpolated flux profiles, and below 0.1 percentage points in both maximum relative deviation and peak-to-peak relative range. Normalize profile differences by the refined grid's mean inner flux. Periodic interpolation uses a shared 4096-angle grid and segment averages; it is a comparison method, not an exact pointwise solution.

Each of the 12 distinct geometry points was compared at 96/128 and 192/256 segments. All pass the three criteria.

| Study point | e | Profile change (%) | Max-deviation change (pp) | Peak-to-peak change (pp) |
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

The 96/64 candidate passed the first doubling check. However, at e = 0.9 its peak-to-peak range differs from the additional 384/256 reference by 0.102032 percentage points, just above the threshold. Increasing the inner grid to 128 reduces the difference to 0.059172 percentage points and the profile difference to 0.056176%. This additional check avoids relying on a marginal first comparison.

## Integration and temperature checks

At 96/64 baseline resolution, tightening source integration from 1e-6 through 1e-9 changes the nonuniformity metrics by less than 2e-9 percentage points between successive tolerances. At the selected 96/128 resolution, a 1e-8 versus 1e-9 check was also run at the baseline and at e = 0.9.

- baseline: profile change 1.658e-11%; peak-to-peak change 1.274e-11 percentage points.
- high_eccentricity: profile change 2.629e-10%; peak-to-peak change 2.937e-11 percentage points.

Temperature checks at 60, 200 and 400 C, for both baseline and e = 0.9 geometry, leave the normalized nonuniformity unchanged to approximately 2e-12 percentage points. This agrees with the linear fixed-emissivity model: temperature scales absolute flux through the difference in fourth powers. It does not justify temperature-independent results if material emissivity varies with temperature.

Across the selected-mesh qualification and reference cases, the maximum relative enclosure energy imbalance is 4.470e-12, maximum row-closure residual is 7.883e-15, and maximum scaled reciprocity residual is 5.773e-08.

## Selected-mesh baseline result

- Mean inner flux: 1549.473679 W/m^2.
- Maximum relative deviation: 4.734188%.
- Peak-to-peak relative range: 8.206598%.
- Heat from B per unit length: 3894.252103 W/m.

## Scope and reproducibility

The selection is supported at the specified geometry points with emissivities 0.6/0.8. It is not a rigorous error bound, a proof for all continuous intermediate values, or qualification of arbitrary radius/offset/emissivity combinations. The site remains interactive; user-selected cases outside the documented points can be checked using independent refinement.

No analytical benchmark comparisons were added. Part (c) retains them as an optional later step.

Run the following from the repository directory (local caches in tmp/ make repeat runs faster):

```powershell
python run_discretization.py --stage independent
python run_discretization.py --stage qualify --outer 96 --inner 64
python run_discretization.py --stage worst-case
python run_discretization.py --stage qualify --outer 96 --inner 128
python run_discretization.py --stage support --outer 96 --inner 128
python finalize_discretization.py
python plot_discretization.py
```

Raw case tables, angular profiles, comparison tables, source fingerprints, and selected settings are stored in results/discretization/. The next step is to interpret and present the final parameter-study results using this selected mesh.
