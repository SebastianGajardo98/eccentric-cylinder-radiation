# Eccentric cylinder radiation

Interactive numerical analysis of radiative heat transfer between two infinitely long, isothermal, diffuse-gray cylinders separated by vacuum.

Assignment: Heat and Mass Transfer (Radiative Heat Transfer), Sebastian Alberto Gajardo Lobos, assigned by Nenad Ferdelji on 12 October 2026.

## Physical problem

The outer cylinder has radius R = 1 m and temperature T_A = 303.15 K (30 degrees Celsius). The inner cylinder has radius 0 < r < R, temperature T_B > T_A, and center offset 0 <= d < R - r. Both surfaces have uniform emissivities 0 < epsilon_A, epsilon_B <= 1. All areas and heat rates are expressed per unit axial length.

The planned visualization animates parameter changes through steady-state solutions. It does not model transient heating: both cylinder temperatures are prescribed by the assignment.

## Numerical model to implement

Discretize both circumferences into equal angular segments, allowing different segment counts on each cylinder. Compute view factors with visibility and blockage by the inner cylinder. The outer concave surface can see itself; the inner convex surface cannot.

For each surface segment i:

- Irradiation: G_i = sum_j F_ij J_j.
- Radiosity: J_i = epsilon_i sigma T_i^4 + (1 - epsilon_i) G_i.
- Net outward heat flux: q_i = J_i - G_i.

Solve the resulting linear radiosity system using temperatures in kelvin. Use sigma = 5.670374419e-8 W/(m^2 K^4).

## Validation before visualization

1. Check nonnegative view factors, enclosure closure sum_j F_ij = 1, and area reciprocity A_i F_ij = A_j F_ji. Report numerical residuals rather than masking errors with arbitrary normalization.
2. Check total enclosure energy balance sum_i A_i q_i = 0.
3. With equal temperatures, all net heat fluxes must vanish.
4. For concentric cylinders, compare the uniform inner flux against:

   q_B = sigma (T_B^4 - T_A^4) / [1/epsilon_B + (r/R)(1/epsilon_A - 1)].

5. For two black surfaces, compare q_B = sigma (T_B^4 - T_A^4), independent of eccentricity.
6. Refine segment counts and view-factor integration accuracy independently. Check convergence of the angular flux profile, its area-weighted mean, and extrema.

Define relative flux deviation as (q_B(theta) - mean(q_B)) / mean(q_B), where the mean is area weighted. Report maximum absolute relative deviation and peak-to-peak range. Treat nearly zero mean flux separately.

## Planned Streamlit interface

- Geometry and local flux: cylinder cross-section colored by surface flux, angular flux curve, parameter controls, and optional parameter-sweep playback.
- Discretization: convergence plots with separate inner and outer segment counts.
- Parameter studies: radius, eccentricity, temperature, and emissivity comparisons.
- Model and validation: derivation, assumptions, benchmark comparisons, numerical residuals, and downloadable results.

Keep the numerical solver separate from Streamlit so its physics can be tested independently. Cache geometry-dependent view factors for temperature and emissivity changes.

## Status

Project initialized. Solver and Streamlit application are not implemented yet.

The intended deployment is Streamlit Community Cloud connected to this GitHub repository.
