# Eccentric cylinder radiation

Interactive numerical analysis of radiative heat transfer between two infinitely long, isothermal, diffuse-gray cylinders separated by vacuum.

Assignment: Heat and Mass Transfer (Radiative Heat Transfer), Sebastian Alberto Gajardo Lobos, assigned by Nenad Ferdelji on 12 October 2026.

## Physical problem

The outer cylinder has radius R = 1 m and temperature T_A = 303.15 K (30 degrees Celsius). The inner cylinder has radius 0 < r < R, temperature T_B > T_A, and center offset 0 <= d < R - r. Both surfaces have uniform emissivities 0 < epsilon_A, epsilon_B <= 1. All areas and heat rates are expressed per unit axial length.

The horizontal-position slider moves B left or right through the concentric position. Its signed value is x_B/(R-r); d = abs(x_B) remains the center distance. Geometry(side="left") places B at (-d, 0), while the default side="right" places it at (+d, 0). View factors and surface flux are calculated at that position. The eccentricity study retains the selected side, and CSV exports include both d and the signed center coordinate.

The planned visualization animates parameter changes through steady-state solutions. It does not model transient heating: both cylinder temperatures are prescribed by the assignment.

## Numerical model

Discretize both circumferences into equal angular segments, allowing different segment counts on each cylinder. Compute view factors with visibility and blockage by the inner cylinder. The outer concave surface can see itself; the inner convex surface cannot.

For each surface segment i:

- Irradiation: G_i = sum_j F_ij J_j.
- Radiosity: J_i = epsilon_i sigma T_i^4 + (1 - epsilon_i) G_i.
- Net outward heat flux: q_i = J_i - G_i.

Solve the resulting linear radiosity system using temperatures in kelvin. Use sigma = 5.670374419e-8 W/(m^2 K^4).

## Numerical validation

1. Check nonnegative view factors, enclosure closure sum_j F_ij = 1, and area reciprocity A_i F_ij = A_j F_ji. Report numerical residuals rather than masking errors with arbitrary normalization.
2. Check total enclosure energy balance sum_i A_i q_i = 0.
3. With equal temperatures, all net heat fluxes must vanish.
4. Refine segment counts and source-arc integration tolerance independently. Check convergence of the angular flux profile, its area-weighted mean, and extrema.

Analytical comparisons for assignment part (c) are optional and deferred, following the professor's clarification. Possible later benchmarks are:

- For concentric cylinders, compare the uniform inner flux against:

   q_B = sigma (T_B^4 - T_A^4) / [1/epsilon_B + (r/R)(1/epsilon_A - 1)].

- For two black surfaces, compare q_B = sigma (T_B^4 - T_A^4), independent of eccentricity.

Define relative flux deviation as (q_B(theta) - mean(q_B)) / mean(q_B), where the mean is area weighted. Report maximum absolute relative deviation and peak-to-peak range. Treat nearly zero mean flux separately.

## Streamlit prototype

- Geometry and local flux: cylinder cross-section with surface-normal flux arrows, flux colors, a uniform mean-flux reference, angular flux curve, parameter controls, and parameter-sweep playback. A signed deviation view highlights departures from uniform flux; a detail view enlarges B.
- Discretization: convergence plots with separate inner and outer segment counts.
- Parameter studies: radius, eccentricity, temperature, and emissivity comparisons.
- Model and plan: derivation, assumptions, numerical residuals, and downloadable results. Analytical comparisons remain a later option.

Keep the numerical solver separate from Streamlit so its physics can be tested independently. Cache geometry-dependent view factors for temperature and emissivity changes.

## Run locally

Requires Python 3.12 or newer. From the repository directory:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m streamlit run streamlit_app.py
```

The sidebar updates automatically when you change a control. Turn off Update automatically to batch changes with Calculate. Preview uses 24/16 segments for faster exploration; Study uses the reviewed 96/128 mesh; Custom lets you set both counts independently. Geometry-dependent view factors are cached; temperature and emissivity changes reuse them. Convergence and parameter studies run only when requested. The parameter workspace supports playback through calculated steady-state cases.

See [the assignment plan](docs/PLAN.md), [the model derivation](docs/MODEL.md), and [the completed discretization selection](docs/DISCRETIZATION.md). The recommended study mesh is 96 outer / 128 inner segments at source integration tolerance 1e-8, qualified at the documented geometry points with emissivities 0.6/0.8. Other user-selected cases remain available for exploration and can be assessed using the convergence controls.

[First implementation results](docs/FIRST_RESULTS.md) include a reproducible refinement study. Run `python run_example.py` to regenerate its data.

Independent refinement, qualification, temperature-scaling checks, and a further high-eccentricity reference are reproduced with `run_discretization.py`. Commands and raw results are documented in docs/DISCRETIZATION.md. `results/discretization/selected.json` records the recommended settings and their scope.

[Reading the flux arrows](docs/FLUX_ARROWS.md) explains the net-flux and signed-deviation views. The visible-arrow count affects the diagram only. Single-case diagrams fit their scale; playback locks the scale across all cases. Arrow glyphs represent net surface flux, not individual radiation rays.

Arrow length contrast defaults to 1 (proportional to q). Higher values emphasize variations visually and are clearly labeled as nonproportional; physical flux colors, min/max values, plots, and exports stay unchanged. Arrows are not forced to terminate on the outer wall because their lengths would then describe gap distance rather than flux.

The view-factor matrix export orders outer segments first, then inner segments, with zero-based index labels. Full parameter and flux exports include physical parameters and diagnostics.

## Status and remaining work

Implemented: circular-arc view factors with inner-cylinder obstruction, diffuse-gray radiosity solver, representative physical consistency tests, a Streamlit prototype, convergence controls, parameter sweeps, and steady-state playback. GitHub Actions runs the numerical checks.

Completed: working-parameter review and selection of the 96/128 study discretization from independent refinement and study-point qualification.

Remaining: interpret and present the required parameter studies, polish the final report, decide whether to include analytical comparisons, and deploy the app.

The intended deployment is Streamlit Community Cloud connected to this GitHub repository.
