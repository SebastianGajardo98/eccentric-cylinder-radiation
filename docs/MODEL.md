# Thermodynamic model and numerical method

## Assumptions and geometry

The two cylinders are infinitely long, isothermal, opaque, diffuse-gray surfaces. Their gap is a vacuum, with no participating medium, conduction, or convection. Temperatures and emissivities are uniform on each cylinder. Prescribed temperatures mean that there is no transient temperature equation.

The center of A is (0, 0), radius R. The center of B is (d, 0), radius r. The surface of A facing the vacuum has inward normals; B has outward normals. Angles are measured counterclockwise from the positive x-axis about each cylinder's own center. The narrowest gap faces theta_B = 0; the widest faces theta_B = pi.

Divide A and B into N_A and N_B equal angular arcs. Areas per unit axial length are a_A = 2 pi R/N_A and a_B = 2 pi r/N_B. Retain the circular arcs rather than approximating their geometry with polygon chords. Approximate radiosity as constant on each arc.

## Diffuse-gray surface equations

Let J_i be total outgoing radiosity and G_i incoming irradiation, both in W/m^2. An opaque gray surface absorbs epsilon_i G_i and reflects (1-epsilon_i) G_i. Its thermal emission is epsilon_i sigma T_i^4. Thus

    J_i = epsilon_i sigma T_i^4 + (1-epsilon_i) G_i
    G_i = sum_j F_ij J_j
    [I - diag(1-epsilon) F] J = diag(epsilon) sigma T^4
    q_i = J_i - G_i

Positive q means heat leaves that surface into the vacuum. The hotter B should have positive net flux and A negative flux. The heat rates per unit length are Q'_B = sum_(i on B) a_i q_i and Q'_A = sum_(i on A) a_i q_i, in W/m. A closed, steady enclosure requires Q'_A + Q'_B = 0.

These equations follow the standard diffuse-gray surface-to-surface model; see [Ansys S2S theory](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_th/flu_th_sec_rad_surface2surface.html).

## View factors for infinite extrusions

The 3D differential view-factor kernel is cos(theta_i) cos(theta_j)/(pi s^2). Let rho be transverse separation and z relative axial displacement. Projecting each transverse normal onto the connecting 3D direction supplies a factor rho/s for each cosine. Integrating along the infinite axial direction gives

    integral_(-infinity)^infinity rho^2 / [pi (rho^2 + z^2)^2] dz = 1/(2 rho).

Consequently the 2D exchange kernel per unit length is

    a_i F_ij = integral_(arc i) integral_(arc j)
               V(p_i,p_j) cos(beta_i) cos(beta_j)/(2 rho) ds_j ds_i,

where beta refers to the transverse normal and V is one for mutually visible points and zero otherwise. The kernel is symmetric, so a_i F_ij = a_j F_ji. B is convex and has no self-view, while A is concave and can see other portions of itself, including parts of the same finite arc.

## Implemented integration

For a fixed source point, parameterize the emission direction by transverse angle phi relative to its vacuum-facing normal. The differential directional weight after integration over axial direction is cos(phi)/2 dphi for -pi/2 < phi < pi/2. Its integral over the emitting half-plane is exactly one.

Partition the emitting half-plane at bearings to all receiver-arc endpoints and at tangent bearings to the inner cylinder. Inside each resulting interval, the first receiver is unchanged. Use the midpoint ray to identify that receiver through positive ray/circle intersections. The interval weight is exactly

    [sin(phi_upper) - sin(phi_lower)]/2.

Sum the weights for each receiver, then average over the source arc using adaptive Gauss-Kronrod quadrature (`scipy.integrate.quad_vec`, max norm). The result is an arc-averaged view-factor row. Tangent intervals handle the shadow cast by B onto A.

Every direction is assigned to its first intersection with the enclosure: closure follows from the directional integral, not row normalization. Rows are integrated independently; reciprocity residuals expose remaining source-integration errors. No view-factor smoothing, symmetrization, or artificial diagonal correction is performed.

## Error checks and limitations

- The integration tolerance controls source-arc integration and is separate from the radiosity segment count.
- Closure and reciprocity check geometry integration; they do not prove that piecewise-constant radiosity is sufficiently resolved.
- Uniform-temperature equilibrium must give zero flux. Total energy balance checks coupling between view factors and radiosity.
- Compare refined angular profiles to establish segment convergence. Segment-average flux is plotted at segment midpoint angles; it is not an exact pointwise flux.
- Very narrow gaps and very low emissivities can make error and computation requirements more demanding. Check diagnostics for those cases and do not infer accuracy from a successful solve alone.
- The current tests exercise representative cases, not every allowed parameter combination.

For context on why closure and reciprocity matter, see [Ansys radiosity diagnostics](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/ans_the/Hlp_G_THE4_7.html). This implementation uses its own circular geometry integration.

## Nonuniformity measures

    q_mean = sum_(i on B) a_i q_i / sum_(i on B) a_i
    delta_i = (q_i - q_mean)/q_mean
    max_deviation_percent = 100 max_i |delta_i|
    peak_to_peak_percent = 100 (max_i q_i - min_i q_i)/|q_mean|

Relative measures are undefined when the mean net flux is effectively zero; the solver then returns None instead of dividing by zero.

## Temperature study

For fixed geometry and temperature-independent emissivities, the radiosity equations are linear in sigma T_A^4 and sigma T_B^4. Because an isothermal closed enclosure has zero net flux, the inner flux profile has the form

    q_B(theta) = sigma (T_B^4 - T_A^4) h(theta; geometry, emissivities).

Thus changing T_B changes absolute flux, while normalized nonuniformity should remain unchanged under these assumptions (apart from numerical errors). This is a model consequence to examine in part (b); it is not an analytical solution of the eccentric-cylinder view-factor problem.

Analytical comparisons for part (c) remain optional and deferred.
