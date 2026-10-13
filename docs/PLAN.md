# Implementation and assignment plan

Analytical comparisons in part (c) are optional, following the professor's clarification. They are deferred. Numerical consistency checks are part of implementation, not a commitment to include analytical comparisons in the submission.

## Part (a): model and discretization

1. Derive the diffuse-gray radiosity equations and infinite-cylinder view-factor method (see MODEL.md).
2. Use a provisional example: R = 1 m, r = 0.4 m, d = 0.3 m, T_A = 30 C, T_B = 200 C, epsilon_A = 0.6, epsilon_B = 0.8. These are working choices, not professor-specified values.
3. First hold geometry and thermal parameters fixed and tighten the source integration tolerance independently of the surface segment counts.
4. Refine equal-angle surface segments: initially (N_A, N_B) = (12, 8), (24, 16), (48, 32), (96, 64). Study independent outer/inner refinement if the combined sequence does not make their individual effects clear.
5. Report angular flux, area-weighted mean, minimum, maximum, maximum relative deviation, peak-to-peak relative range, reciprocity, and energy balance.
6. Compare profiles on a shared angular grid. A relative profile change below 0.5% and changes of the nonuniformity metrics below 0.1 percentage points are provisional criteria, to be evaluated rather than assumed.
7. Select segment counts only after examining these results. Use the selected counts for part (b).

## Part (b): physical parameter studies

- Eccentricity: vary normalized offset e = d/(R-r) from 0 to 0.9 at fixed r, temperature, and emissivities. Physical gap remains positive.
- Radius: vary r/R from 0.2 to 0.6 at fixed d = 0.3 m for the provisional example; verify d < R-r for each case. A second study at fixed e can distinguish size effects from changes in normalized offset.
- Temperature: vary T_B from 60 C to 400 C at fixed geometry and emissivities. Compare both absolute flux and normalized nonuniformity; temperature may change their scales differently.
- Keep epsilon_A and epsilon_B explicitly recorded. Optional emissivity studies can explain reflections but are outside the required r, d, T_B sweep.
- Include several full angular profiles as well as summary trends. Report numerical error checks for every case; refine difficult near-contact geometries if needed.

## Part (c): diagrams and discussion

- Show cylinder cross-section, offset, radii, angle convention, surface segmentation, and local flux colors.
- Explain narrow/wide gaps and the effect of diffuse reflections on the angular flux profile.
- Include convergence plots and reproducible parameter-study tables.
- Interpret temperature dependence using the linear radiosity model.
- Optional later: compare concentric and black-body cases with analytical solutions. No analytical comparison is required to proceed with implementation.

## Delivery sequence

1. Numerical module with public interfaces `calculate_view_factors(Geometry, tolerance)` and `solve_radiation(view_factors, temperatures, emissivities)`.
2. Tests at these two user-approved interfaces: visibility, closure, reciprocity, equilibrium, and enclosure energy balance. These do not establish accuracy for every possible geometry.
3. Streamlit prototype with geometry, angular flux, diagnostics, and downloadable data.
4. Run and interpret convergence studies; select the final discretization.
5. Run the required physical parameter studies and add animation through steady-state cases.
6. Prepare final discussion and optional analytical comparisons, then deploy with Streamlit Community Cloud.

The interactive app supports exploration; the final submission still needs a written derivation and commentary answering the assignment.
