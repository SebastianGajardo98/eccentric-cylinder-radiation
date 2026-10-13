# Eccentric cylinder radiation

Interactive numerical analysis of radiative heat transfer between two infinitely long, isothermal, diffuse-gray cylinders separated by vacuum.

Assignment: Heat and Mass Transfer (Radiative Heat Transfer), Sebastian Alberto Gajardo Lobos, assigned by Nenad Ferdelji on 12 October 2026.

## Physical problem

The outer cylinder has radius R = 1 m and temperature T_A = 303.15 K (30 degrees Celsius). The inner cylinder has radius 0 < r < R, temperature T_B > T_A, and center offset 0 <= d < R - r. Both surfaces have uniform emissivities 0 < epsilon_A, epsilon_B <= 1. All areas and heat rates are expressed per unit axial length.

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

- Geometry and local flux: cylinder cross-section colored by surface flux, angular flux curve, parameter controls, and optional parameter-sweep playback.
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

The sidebar uses a Calculate button to submit parameter changes. Geometry-dependent view factors are cached; temperature and emissivity changes reuse them. Convergence and parameter studies run only when requested. The parameter workspace supports playback through calculated steady-state cases.

See [the assignment plan](docs/PLAN.md) and [the model derivation](docs/MODEL.md). Working parameters and initial segment counts are provisional until convergence is assessed.

[First implementation results](docs/FIRST_RESULTS.md) include a reproducible refinement study. Run `python run_example.py` to regenerate its data.

The view-factor matrix export orders outer segments first, then inner segments, with zero-based index labels. Full parameter and flux exports include physical parameters and diagnostics.

## Status and remaining work

Implemented: circular-arc view factors with inner-cylinder obstruction, diffuse-gray radiosity solver, representative physical consistency tests, a Streamlit prototype, convergence controls, parameter sweeps, and steady-state playback. GitHub Actions runs the numerical checks.

Remaining: select the final discretization from convergence evidence, interpret the required parameter studies, polish the presentation and final report, decide whether to include analytical comparisons, and deploy the app.

The intended deployment is Streamlit Community Cloud connected to this GitHub repository.
