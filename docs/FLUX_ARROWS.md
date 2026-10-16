# Reading the surface-flux arrows

The arrows visualize the assignment's local net heat-flux density on cylinder B. They start on the surface and follow its normal. The default four directions are exactly right, top, left and bottom; optional additional arrows retain these four axes. Arrow values are reconstructed by periodic linear interpolation between the calculated segment averages. They are approximate display values, not new pointwise solver results. The circumference colors and angular chart retain the original segment averages.

At length contrast 1, arrow length is proportional to the selected quantity; the display scale is shown above the drawing. Higher contrast settings are explicitly labeled visual emphasis, not proportional physical lengths.

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

Every arrow should not be stretched to touch cylinder A. In that construction its length would encode the local distance to A, regardless of the calculated flux. Here all arrows use one common scale. The smallest and largest physical segment flux values appear below the diagram. The close-up labels show the reconstructed cardinal values and their signed deviation from the mean.

The app opens with a full-width **Cylinder B detail** view, four thick arrows and length contrast 6 to make small differences visible at normal browser sizes. The angular chart is available in its own expander below the diagram. In **Flux arrow display**, adjust **Arrow length contrast (1 = proportional to q)** to switch between emphasis and proportional lengths. The net-flux drawing uses the signed mapping `abs(q_mean) * sign(q) * (abs(q)/abs(q_mean))**contrast` on the reconstructed arrow values before fitting the common display scale. This preserves the flux ordering, its sign, and equal arrows for a uniform field; it exaggerates spatial variations without creating false inward arrows. There is no individual-arrow clipping. The setting has no effect on the signed-deviation view.

Whenever contrast is greater than 1, the diagram states that lengths are not proportional to q and omits the linear W/m^2 arrow key. Color, numerical min/max, the angular graph, and all exported numerical results retain the physical q values. The dashed reference still corresponds to the actual mean because the length mapping fixes q = q_mean. Set contrast back to 1 for quantitative comparisons by arrow length.

Emphasis is defined around each case's own mean. For fixed geometry and emissivities the emphasized lengths retain temperature scaling, but arbitrary geometry cases with different means must not be compared quantitatively by emphasized lengths. Use contrast 1, actual flux colors, or numerical values for those comparisons.

Choose Enclosure to retain both cylinders, or Cylinder B detail for a larger view centered on the inner surface. The visible-arrow setting only changes the display sampling; it does not change the solver's discretization. In the illustrated case with B offset to the right, flux is lower on the right and higher on the left, while top and bottom agree by symmetry. Cardinal labels are computed from the solution rather than assigned assumed minimum/maximum values.

A single-case view fits one common arrow scale to that view. It never rescales or truncates individual arrows. In enclosure view the global minimum gap limits the arrow length so glyphs stay inside A; the detail view removes that geometric restriction.

All cases in parameter playback use one shared drawing scale, one shared detail-view extent, and one shared color scale. At contrast 1, arrow lengths can be compared quantitatively across playback frames, including temperature changes. Emphasized lengths instead highlight spatial variation within each frame. Separate single-case views can have different fitted scales: read the reference key rather than comparing screen lengths across them.

The physical solver, numerical results, selected discretization and existing analytical-comparison scope are unchanged by this visualization.
