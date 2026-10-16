# Reading the surface-flux arrows

The arrows visualize the assignment's local net heat-flux density on cylinder B. Each arrow is attached to a sampled surface segment midpoint and points along the local surface normal. Arrow length is proportional to the selected quantity; the display scale is shown above the drawing.

## Net heat flux

- A longer outward arrow means greater net heat loss per unit surface area, in W/m^2.
- For a genuinely negative net flux the arrow points inward. The assignment's hotter inner cylinder normally gives outward net flux.
- The dashed contour marks the tips of equal-length arrows representing the current area-weighted mean flux. Actual tips outside that contour are above the mean; tips inside are below the mean.
- The matching angular graph includes a dashed mean-flux line.

This is a surface-flux representation, not a ray-tracing animation. Diffuse radiation travels over a range of directions; these arrows summarize its net exchange at the surface.

## Deviation from mean

The displayed field is 100 (q_i - q_mean)/abs(q_mean), in percent. For the positive mean flux in the assignment this is the same relative deviation used in the numerical studies.

- An outward deviation arrow means above-average flux.
- An inward deviation arrow means below-average flux, even when the actual net flux is still outward.
- Red/blue colors distinguish positive/negative deviation, with a symmetric color scale centered on zero.
- The angular graph shows the same percentages with a dashed zero reference.
- Relative deviation is undefined at effectively zero mean flux. No deviation arrows are drawn in that case.
- Numerical roundoff below 1e-8 percentage points is suppressed in the arrow diagram so a uniform solution does not show false nonuniformity.

This view makes small variations easier to inspect without presenting magnified deviations as physical heat-flow reversal.

## Display and comparison

Choose Enclosure to retain both cylinders, or Cylinder B detail for a larger view of the inner surface. The visible-arrow setting samples the already calculated segment fluxes; it does not change the solver's discretization.

A single-case view fits one common arrow scale to that view. It never rescales or truncates individual arrows. In enclosure view the global minimum gap limits the arrow length so glyphs stay inside A; the detail view removes that geometric restriction.

All cases in parameter playback use one shared arrow scale, one shared detail-view extent, and one shared color scale. Thus arrow lengths can be compared across playback frames, including temperature changes. Separate single-case views can have different fitted scales: read the reference key rather than comparing screen lengths across them.

The physical solver, numerical results, selected discretization and existing analytical-comparison scope are unchanged by this visualization.
