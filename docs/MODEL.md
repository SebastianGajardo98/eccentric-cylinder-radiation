# Thermodynamic model and numerical method

## 1. Physical assumptions and geometry

| Term | Plain meaning |
| --- | --- |
| Infinitely long | We exclude effects near the ends of the cylinders. |
| Isothermal | Every location on a given cylinder has the same temperature. A and B can have different temperatures. |
| Prescribed temperature | The temperature is a specified input and is maintained at that value. |
| Opaque | Radiation cannot pass through the cylinder wall. |
| Diffuse | Emission and reflection follow a diffuse angular distribution, rather than mirror-like reflection. |
| Gray | Emissivity is treated as independent of radiation wavelength. |
| Uniform emissivity | A given cylinder has the same emissivity everywhere around its surface. |
| Temperature-independent emissivity | We keep emissivity unchanged when temperature changes. |

Cylinder A has prescribed radius $R=1$ m and temperature $T_A=303.15$ K (30 °C). Cylinder B has radius $0<r<R$ and prescribed $T_B>T_A$. Both surfaces are infinitely long, isothermal, opaque, diffuse-gray bodies with uniform, temperature-independent emissivities. The gap is a vacuum: only surface-to-surface radiation is included. There is no transient temperature equation because both temperatures are prescribed.

The center of A is $O_A=(0,0)$. The center of B is $O_B=(x_B,0)$, where $x_B=+d$ on the right or $-d$ on the left. The center distance $d=|x_B|$ satisfies $0<d<R-r$ for eccentric cases. The concentric case $d=0$ is retained as a numerical reference. Normalized eccentricity is $e=d/(R-r)$. Angles on B are measured counterclockwise from the fixed positive x-axis: 0° right, 90° top, 180° left and 270° bottom. Mirroring the position mirrors the flux profile without changing scalar heat rates or nonuniformity measures.

## 2. Surface discretization and units

Divide A and B into $N_A$ and $N_B$ equal angular arcs, allowing different counts on the two surfaces. Retain their exact circular geometry and approximate radiosity as constant on each arc. The angular widths and areas per unit axial length are

$$
\Delta\theta_A=\frac{2\pi}{N_A},\qquad
\Delta\theta_B=\frac{2\pi}{N_B},\qquad
a_A=R\Delta\theta_A,\qquad a_B=r\Delta\theta_B.
\tag{1}
$$

The $a_i$ have units m² per m of axial length (equivalently m). Flux density $q_i$ has units W/m²; heat rate per axial length $Q'$ has units W/m. These are different quantities, particularly when radius changes. The reported local numerical flux is an arc average, rather than an exact pointwise value.

## 3. Derivation of the diffuse-gray energy balance

For an opaque gray surface, absorptivity equals emissivity. Of the irradiation $G_i$ arriving at arc $i$, the absorbed fraction is $\epsilon_i G_i$ and the reflected fraction is $(1-\epsilon_i)G_i$. Thermal emission is $\epsilon_i\sigma T_i^4$, where $\sigma=5.670374419\times10^{-8}$ W/(m² K⁴). Temperatures in this expression are in kelvin.

The total outgoing radiosity is therefore

$$
J_i=
\underbrace{\epsilon_i\sigma T_i^4}_{\text{emitted by the surface}}
+\underbrace{(1-\epsilon_i)G_i}_{\text{reflected incoming radiation}}.
\tag{2}
$$

The view factor $F_{ij}$ is the fraction of diffuse radiation leaving arc $i$ that reaches arc $j$, accounting for visibility and obstruction by B. Reciprocity gives the incident-radiation relation

$$
G_i=\sum_jF_{ij}J_j.
\tag{3}
$$

Substituting (3) into (2):

$$
J_i=\epsilon_i\sigma T_i^4
+(1-\epsilon_i)\underbrace{\sum_jF_{ij}J_j}_{G_i}.
\tag{4}
$$

Rearranging (4):

$$
J_i-(1-\epsilon_i)\sum_jF_{ij}J_j=\epsilon_i\sigma T_i^4.
\tag{5}
$$

Equation (5) is written for every surface arc $i$. The equations are **coupled** because the outgoing radiation from one arc depends on radiation leaving other arcs. Radiation leaving B reaches A; some can be reflected back toward B and reflected again. These repeated exchanges link the unknown radiosities, so they must be solved together.

The equations are **linear in the unknown radiosities** $J_j$: these unknowns appear only to the first power, multiplied by known coefficients. The prescribed temperatures $T_i$ are known inputs, even though they appear to the fourth power.

**Matrix form**

Collecting (5) for all surface arcs gives (6). Here $I$ is the identity matrix, $F$ contains the view factors, $\mathcal E=\operatorname{diag}(\epsilon_i)$ stores the emissivities on its diagonal, and $\mathbf J$ is the list of unknown radiosities:

$$
\left[I-(I-\mathcal E)F\right]\mathbf J
=\mathcal E\sigma\mathbf T^4.
\tag{6}
$$

After solving (6), irradiation follows from (3), and the net outward flux is

$$
q_i=\epsilon_i(\sigma T_i^4-G_i)=J_i-G_i.
\tag{7}
$$

Positive $q_i$ means net heat leaves the body; the hotter B has positive net outward flux. Cylinder A absorbs the net heat transferred from B. Using areas per unit axial length,

$$
Q'_B=\sum_{i\in B}a_iq_i,\qquad
Q'_A=\sum_{i\in A}a_iq_i,\qquad Q'_A+Q'_B=0.
\tag{8}
$$

Diffuse-gray radiosity and irradiation are described in the [COMSOL surface-radiation theory reference](https://doc.comsol.com/6.3/doc/com.comsol.help.heat/heat_ug_theory.07.051.html). The sign convention here is positive outward.

## 4. View factors for infinitely long cylinders

**Symbols in equations (9) and (10)**

| Symbol | Meaning |
| --- | --- |
| $i$, $j$ | Labels for the emitting arc and receiving arc. |
| $p_i$, $p_j$ | Points on the emitting arc $i$ and receiving arc $j$. |
| $\rho$ | Distance between the two points in the cross-section (m). |
| $z$ | Separation between the points along the cylinder axis, perpendicular to the cross-section (m). |
| $\beta_i$, $\beta_j$ | Orientation: angles in the cross-section between the connecting line and the surface normals pointing into the vacuum. |
| $V(p_i,p_j)$ | Visibility: 1 when the points have an unobstructed connection and face each other; 0 otherwise. |
| $a_i$ | Area of arc $i$ per unit axial length (m²/m). |
| $F_{ij}$ | Fraction of diffuse radiation leaving arc $i$ that directly reaches arc $j$. |
| $ds_i$, $ds_j$ | Infinitesimal (arbitrarily small) arc-length elements on arcs $i$ and $j$ (m), summed by the double integral. |

The three-dimensional diffuse exchange kernel is $\cos\theta_i\cos\theta_j/(\pi s^2)$, where $s$ is the full distance between the points and $s^2=\rho^2+z^2$. Each projection of a transverse surface normal contributes $\rho/s$. Integration over the infinite axial direction yields the following result. Equation (9) accounts for receiving points along the entire cylinder length when calculating the view factor.

$$
\int_{-\infty}^{\infty}
\frac{\rho^2}{\pi(\rho^2+z^2)^2}\,dz=\frac{1}{2\rho}.
\tag{9}
$$

Using (9), the view-factor exchange per unit axial length is

$$
a_iF_{ij}=\int_{\mathrm{arc}\ i}\int_{\mathrm{arc}\ j}
V(p_i,p_j)\frac{\cos\beta_i\cos\beta_j}{2\rho}\,ds_j\,ds_i.
\tag{10}
$$

Cylinder A has inward-facing vacuum normals; B has outward-facing normals. The kernel is symmetric, giving reciprocity $a_iF_{ij}=a_jF_{ji}$. B is convex and has no self-view. A is concave and can see other parts of itself, including part of the same finite arc.

Equation (11) is used to **calculate contributions from ranges of directions** at a fixed source point when evaluating (10).

For a source point, let $\phi$ be emission direction relative to its vacuum-facing normal. Integrating the axial direction gives the directional weight $\cos\phi/2$ on $-\pi/2<\phi<\pi/2$. Divide this emitting half-plane at bearings to receiver-arc endpoints and tangent directions to B. The first receiver is unchanged within each resulting interval. Its weight is evaluated exactly as

$$
\int_{\phi_1}^{\phi_2}\frac{\cos\phi}{2}\,d\phi
=\frac{\sin\phi_2-\sin\phi_1}{2}.
\tag{11}
$$

A midpoint ray identifies the first intersected receiver in each interval. Tangent directions account for the shadow cast by B. Average the resulting directional factors over each source arc using adaptive Gauss-Kronrod quadrature (`scipy.integrate.quad_vec`, maximum norm). The integration tolerance controls this numerical integration and is assessed separately from the surface segment counts in the discretization study.

No row normalization, symmetrization or smoothing is applied to hide integration residuals. For this closed enclosure, checks include:

- Nonnegativity, $F_{ij}\geq 0$ **(a radiation fraction cannot be negative)**.
- Closure, $\sum_jF_{ij}=1$ **(all fractions leaving a patch must add to 1, or 100%, because the enclosure is closed)**.
- Reciprocity, $a_iF_{ij}=a_jF_{ji}$ **(the area-weighted geometrical exchange is consistent in both directions)**.

Passing these checks does not guarantee an accurate flux distribution around B. Accuracy is assessed by refining the surface discretization in the next section.

## 5. Measuring departure from uniform surface flux

Equation (12) first calculates the mean flux around B, $\bar q_B$. It is area-weighted, meaning larger surface pieces contribute proportionally more.

Then it calculates each segment's percentage departure from that mean:

$$
\bar q_B=\frac{\sum_{i\in B}a_iq_i}{\sum_{i\in B}a_i},\qquad
\delta_i=100\frac{q_i-\bar q_B}{|\bar q_B|}.
\tag{12}
$$

Here, B is divided into equal-area arcs, so its area-weighted mean is the ordinary average of the segment fluxes.

The two reported relative nonuniformity measures are

$$
D_{\max}=\max_{i\in B}|\delta_i|,\qquad
D_{pp}=100\frac{q_{\max}-q_{\min}}{|\bar q_B|}.
\tag{13}
$$

Both are percentages. Differences between these metrics on two meshes are expressed in **percentage points**. Relative nonuniformity is undefined at effectively zero mean flux. Assignment cases use $T_B>T_A$ and have positive mean flux.

Uniformity means that the angular flux equals the current surface mean everywhere. Comparing against a separate concentric calculation answers a different question and is not used as the definition of nonuniformity here.

## 6. Temperature dependence and interpretation

With fixed geometry and emissivities, the radiosity system is linear in $\sigma T_A^4$ and $\sigma T_B^4$. A closed isothermal enclosure has zero net flux, so the model implies

$$
q_B(\theta)=\sigma(T_B^4-T_A^4)\,h(\theta; r,d,R,\epsilon_A,\epsilon_B).
\tag{14}
$$

Changing $T_B$ scales absolute flux but leaves the normalized angular profile unchanged under these assumptions. This model consequence is checked using the six numerical temperature cases in part (b).

Local net flux depends on both emission and irradiation from the whole enclosure, including diffuse reflections. It is not determined by local gap distance alone. The narrow-gap and wide-gap trends stated in the report refer to the calculated gray-surface cases.

## 7. Numerical checks and limits

- Closure, reciprocity, nonnegativity and enclosure energy balance check numerical consistency.
- Equal-temperature equilibrium and left/right reflection symmetry are tested at the public solver interfaces.
- Independent A/B surface refinement and separate integration-tolerance refinement establish finite-mesh stability for the stated study cases.
- Very narrow gaps, other radii or different emissivities can require additional refinement. A successful solve is not an accuracy guarantee for arbitrary inputs.
- Infinite isothermal cylinders omit end effects, participating media, material temperature dependence and transient energy storage. Interactive motion shows successive prescribed steady states.
