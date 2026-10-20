# Reading the interactive simulation

The complete cross-section always shows cylinder B inside cylinder A, at the same physical scale. Positive position moves B right, negative position moves B left, and zero is concentric. The distance d is the absolute center displacement; the signed slider controls x_B/(R-r).

Eight outward arrows indicate net surface heat loss normal to B, in four axial directions and four diagonals. Arrow values are periodically interpolated between calculated segment averages. The colored band and angular profile retain the actual segment averages. Adding display arrows would not refine the numerical model.

Every arrow in a frame uses one proportional scale. To remain inside A, that scale fits the available gap. Moving B nearer to a wall therefore shrinks the drawing scale, even on a far side where the calculated flux increases. Screen arrow lengths must not be compared between independently fitted positions. The figure and caption identify this limitation.

The primary quantitative display is the signed relative deviation from the current area-weighted mean of B. A positive deviation means above the current mean, and a negative deviation means below it; all eight actual net-flux arrows remain outward for the hotter inner cylinder.

For absolute comparisons between positions, expand **Compare eight directions on a fixed flux scale**. Its W/m^2 axis stays fixed while B moves. It changes only when the user explicitly edits the axis maximum or presses **Fit comparison axis**. The reference ticks and side-value deltas use the current B mean, consistently with the assignment's definition of nonuniformity. Values above the chosen range are not silently truncated or rescaled.

The interactive page opens with the Preview mesh, 48 A / 64 B segments, which takes about half the time of the selected report mesh, 96 A / 128 B. Selected reproduces the report mesh; Custom changes numerical settings. Interactive settings do not alter the completed studies in (a) and (b). CSV downloads identify the current physical parameters, mesh, integration tolerance and numerical-source fingerprint.

No transient temperature evolution is modeled: every control change solves another prescribed steady state.
