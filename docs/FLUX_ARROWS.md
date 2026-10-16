# Reading the surface-flux diagram

## Geometry from the assignment

The main diagram always shows the complete cross-section: cylinder B is inside cylinder A, with both circles drawn at the same physical scale. A has radius R = 1 m and center O_A = (0, 0); B has radius r and center O_B = (x_B, 0), with x_B = +d on the right or -d on the left. The dotted straight line joins the centers. The space between the walls is a vacuum. Moving B changes its position while preserving the circular surfaces and their radii.

Use **Horizontal position of B**: negative moves left, zero centers B, and positive moves right. The control represents x_B/(R-r). The distance d = abs(x_B) and normalized eccentricity e = abs(x_B)/(R-r) remain nonnegative. Angles remain fixed relative to the screen: 0 degrees right, 90 top, 180 left and 270 bottom. Mirroring the position mirrors the flux pattern; the scalar mean and nonuniformity measures stay the same at equal distance.

The parameters satisfy r < R and d < R-r, so the surfaces do not intersect. The concentric case d = 0 is available as a reference. The assignment concerns infinitely long cylinders; this drawing is a transverse cross-section, and heat rates are reported per unit axial length.

## Net heat flux on B

The default eight arrows start on B and follow its outward surface normals, every 45 degrees. They include the four axes and the four diagonals. The arrows summarize local net heat loss per unit surface area, not individual radiation-ray trajectories. Diffuse radiation travels over a range of directions.

At the default length contrast 1, all arrow lengths use one proportional scale. A greater positive q gives a longer outward arrow. A genuinely negative q gives an inward arrow. All enclosure arrows are fitted with one scale that keeps them within A; they are not individually stretched to reach the wall. If the actual flux varies only slightly, the proportional lengths should also vary only slightly.

The colored band on B shows the calculated segment-average flux in W/m^2. The visible angular profile and its mean-flux reference quantify the variation. Minimum, maximum and maximum relative deviation are reported numerically. These displays make small differences readable while retaining the real geometry and proportional default arrow lengths.

Arrow values are reconstructed by periodic linear interpolation between segment averages. They are approximate display values, not additional pointwise solver results. Increasing the visible arrow count does not change or refine the numerical discretization. The circumference colors, angular profile and exports retain the original segment averages.

## Optional display controls

**Flux arrow display** provides the arrow count, the represented quantity, optional length emphasis and an optional mean-flux tip guide. The guide is off by default: the only circular boundaries in the initial diagram are the actual cylinder walls. When enabled, the dashed contour marks where equal arrows at the mean flux would end; it is not another cylinder.

For optional length contrast greater than 1, the signed mapping is `abs(q_mean) * sign(q) * (abs(q)/abs(q_mean))**contrast`, applied before fitting the common drawing scale. It preserves ordering, sign and uniform fields, but exaggerates differences. The drawing explicitly states that lengths are not proportional to q and omits the linear W/m^2 arrow key. Colors, numerical values, angular profiles and solver results remain unchanged. Set contrast to 1 for quantitative comparisons by arrow length.

Optional emphasis is defined around each case's own mean, so emphasized lengths should not be compared quantitatively across geometry cases with different means. Use contrast 1 or compare the actual numerical values and colors.

## Deviation from mean

The optional deviation representation uses `100 * (q - q_mean)/abs(q_mean)` in percent. Outward deviation arrows indicate above-average flux; inward deviation arrows indicate below-average flux. An inward deviation arrow does not imply that the actual net heat flows inward. The color scale is symmetric around zero, and the angular profile uses a zero reference.

Relative deviation is undefined at effectively zero mean flux; no deviation arrows are drawn in that case. Roundoff below 1e-8 percentage points is suppressed so a uniform solution does not show false variations. The length-contrast control does not affect this representation.

## Comparing cases

Parameter playback keeps the outer-cylinder frame, arrow scale and color scale fixed across its cases. At contrast 1, arrow lengths and cylinder positions can be compared between frames. Independently fitted single-case views may use different drawing scales, so read the arrow key before comparing screen lengths between them.

For the illustrated diffuse-gray case with B offset to the right, calculated flux is lower on the right and higher on the left, while top and bottom agree by symmetry. Extrema come from the solution rather than an assumed relation to gap distance.

The physical solver, discretization studies and parameter studies are unchanged by the display controls. A readable diagram complements the required numerical analysis; it does not establish discretization convergence by itself.
