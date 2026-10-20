# Analysis of Radiative Heat Transfer Between Two Infinitely Long Cylinders in an Eccentric Arrangement

Sebastian Alberto Gajardo Lobos · Heat and Mass Transfer (Radiative Heat Transfer)

## Assignment statement

Inside an infinite cylinder A of radius $R = 1$ m, maintained at constant temperature $T_A = 30$ °C, a second, smaller infinite cylinder B of radius $r$, ($r < R$), is placed, which is also maintained on constant temperature $T_B > T_A$. Both cylinders are diffuse-gray bodies with emissivity coefficients $\varepsilon_A$ and $\varepsilon_B$ and the space between them is a vacuum.

If the cylinders are arranged concentrically or if both are black bodies, a heat flux density on the surface of cylinder B is uniform, however, if both cylinders are diffuse-gray bodies and the smaller cylinder B is placed at distance $d$, $0 < d < R - r$ from the centre of cylinder A, heat flux density on the cylinder B is not uniformly distributed.

The task is to analyse the deviation from uniform surface flux density when the cylinder B is placed eccentrically within the cylinder A, using a view factor method.


## The following is required

**(a)** For a selected combination of parameters $r$, $d$, and $T_B$, analyse the effect of discretizing the surfaces of cylinders A and B into equal segments (the number of elements on cylinders A and B need not be equal) on the deviation from uniform surface flux density on cylinder B. The analysis must include the derivation of the appropriate thermodynamic model for radiative heat transfer.

**(b)** Using the same thermodynamic model and the selected discretization, analyse the influence of parameters $r$, $d$, and $T_B$, on the deviation from uniform surface density of cylinder B.

**(c)** Supplement all analyses with appropriate descriptions, diagrams, and commentary, and compare the results with analytical solutions, if find appropriate.

## Objective and numerical scope

Quantify deviation from uniform net heat-flux density on cylinder B using view factors, derive the thermodynamic model, select a surface discretization, and study $r$, $d$ and $T_B$. Descriptions, diagrams, discussion, raw results and the corresponding program code accompany the analyses.

![Geometry and surface segments](../results/studies/geometry_and_segments.png)

Figure: working geometry. The displayed 12/8 segment boundaries illustrate the idea of equal-arc discretization; suitable calculation counts are assessed in the refinement study below.

### Symbols in the diagram

| Symbol | Meaning |
| --- | --- |
| $R$ | Radius of outer cylinder A: the distance from its center to its wall (m). |
| $r$ | Radius of inner cylinder B: the distance from its center to its surface (m). |
| $O_A$, $O_B$ | Center points of cylinders A and B. |
| $d$ | Distance between the two centers, $O_A$ and $O_B$ (m). |
| $T_A$, $T_B$ | Surface temperatures of cylinders A and B. |
| $\theta_B$ | Angular position of a point on B, measured counterclockwise from the right. 0° = right, 90° = top, 180° = left, 270° = bottom. It identifies where the local flux is calculated. |
| $n_A$ | Surface normal on A: a direction perpendicular to its wall, pointing inward into the gap. |
| $n_B$ | Surface normal on B: a direction perpendicular to its surface, pointing outward into the gap. |

The normal arrows show surface orientation. Their lengths do not represent heat-flux magnitude. The angle $\theta_B$ labels a position; it does not indicate cylinder rotation.


## Part (a): thermodynamic model

**Assignment requirement (a)**

> For a selected combination of parameters $r$, $d$, and $T_B$, analyse the effect of discretizing the surfaces of cylinders A and B into equal segments (the number of elements on cylinders A and B need not be equal) on the deviation from uniform surface flux density on cylinder B. The analysis must include the derivation of the appropriate thermodynamic model for radiative heat transfer.

### 1. Physical assumptions and geometry

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

### 2. Surface discretization and units

Divide A and B into $N_A$ and $N_B$ equal angular arcs, allowing different counts on the two surfaces. Retain their exact circular geometry and approximate radiosity as constant on each arc. The angular widths and areas per unit axial length are

$$
\Delta\theta_A=\frac{2\pi}{N_A},\qquad
\Delta\theta_B=\frac{2\pi}{N_B},\qquad
a_A=R\Delta\theta_A,\qquad a_B=r\Delta\theta_B.
\tag{1}
$$

The $a_i$ have units m² per m of axial length (equivalently m). Flux density $q_i$ has units W/m²; heat rate per axial length $Q'$ has units W/m. These are different quantities, particularly when radius changes. The reported local numerical flux is an arc average, rather than an exact pointwise value.

**Code:** [`radiation.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/radiation.py) defines the circular geometry and equal-arc areas used in (1).

### 3. Derivation of the diffuse-gray energy balance

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

**Code:** In [`radiation.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/radiation.py), `solve_radiation` solves (6), evaluates irradiation with (3), and calculates net flux with (7). `RadiationResult.metrics` evaluates the heat rates and energy balance in (8).

### 4. View factors for infinitely long cylinders

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

**Code:** [`radiation.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/radiation.py), function `calculate_view_factors`, implements the view factors, visibility and adaptive source-arc integration. Integration tolerance is a chosen numerical setting for evaluating this integral, rather than a physical input or another radiation equation.

No row normalization, symmetrization or smoothing is applied to hide integration residuals. For this closed enclosure, checks include:

- Nonnegativity, $F_{ij}\geq 0$ **(a radiation fraction cannot be negative)**.
- Closure, $\sum_jF_{ij}=1$ **(all fractions leaving a patch must add to 1, or 100%, because the enclosure is closed)**.
- Reciprocity, $a_iF_{ij}=a_jF_{ji}$ **(the area-weighted geometrical exchange is consistent in both directions)**.

Passing these checks does not guarantee an accurate flux distribution around B. Accuracy is assessed by refining the surface discretization in the next section.

### 5. Measuring departure from uniform surface flux

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

**Code:** [`radiation.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/radiation.py), property `RadiationResult.metrics`, computes the mean flux, $D_{\max}$ and $D_{pp}$ from the segment-average fluxes.

Uniformity means that the angular flux equals the current surface mean everywhere. Comparing against a separate concentric calculation answers a different question and is not used as the definition of nonuniformity here.

### 6. Temperature dependence and interpretation

With fixed geometry and emissivities, the radiosity system is linear in $\sigma T_A^4$ and $\sigma T_B^4$. A closed isothermal enclosure has zero net flux, so the model implies

$$
q_B(\theta)=\sigma(T_B^4-T_A^4)\,h(\theta; r,d,R,\epsilon_A,\epsilon_B).
\tag{14}
$$

**The function $h$ describes the angular pattern produced by geometry and surface properties. The temperature factor scales its magnitude.**

Changing $T_B$ scales absolute flux but leaves the normalized angular profile unchanged under these assumptions. This model consequence is checked using the six numerical temperature cases in part (b).

**Code:** [`run_parameter_studies.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_parameter_studies.py) runs those six temperatures using the same solver. [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `supporting_checks`, also checks temperature scaling at the starting and largest-offset arrangements.

Local net flux depends on both emission and irradiation from the whole enclosure, including diffuse reflections. It is not determined by local gap distance alone. The narrow-gap and wide-gap trends stated in the report refer to the calculated gray-surface cases.

### 7. Numerical checks and limits

- Closure, reciprocity, nonnegativity and enclosure energy balance check numerical consistency.
- Two physical checks run automatically in the tests: with equal temperatures on A and B, the net heat flux is zero everywhere; and moving B from the right side to the left mirrors its flux profile.
- Independent A/B surface refinement and separate integration-tolerance refinement establish finite-mesh stability for the stated study cases.
- The selected 96/128 mesh was checked only at the 12 arrangements used in this report, with $\epsilon_A=0.6$ and $\epsilon_B=0.8$. Other cases, especially very narrow gaps or different emissivities, may need a finer mesh; obtaining a solution does not by itself show that it is accurate.
- Infinite isothermal cylinders omit end effects, participating media, material temperature dependence and transient energy storage. Interactive motion shows successive prescribed steady states.

**Code:** The physical solver checks are in [`tests/test_solver.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/tests/test_solver.py); the recorded-study and data-integrity checks are in [`tests/test_studies.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/tests/test_studies.py). The surface-refinement evidence is generated by [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py).


## Part (a): discretization selection

**Assignment requirement (a)**

> For a selected combination of parameters $r$, $d$, and $T_B$, analyse the effect of discretizing the surfaces of cylinders A and B into equal segments (the number of elements on cylinders A and B need not be equal) on the deviation from uniform surface flux density on cylinder B. The analysis must include the derivation of the appropriate thermodynamic model for radiative heat transfer.

### Working parameters

| Parameter | Baseline | Reason |
| --- | --- | --- |
| Outer radius $R$ | 1 m | Prescribed by the assignment |
| Outer temperature $T_A$ | 30 °C | Prescribed by the assignment |
| Inner radius $r$ | 0.4 m | Leaves room to vary radius and center distance independently |
| Center distance $d$ | 0.3 m | $e = 0.5$; minimum gap 0.3 m, maximum gap 0.9 m |
| Inner temperature $T_B$ | 200 °C | A working hot-cylinder case above $T_A$ |
| Emissivities $\epsilon_A$ / $\epsilon_B$ | 0.6 / 0.8 | Gray-surface working values that allow diffuse reflections; no particular material is assumed |

Final one-parameter sweeps: $e$ = 0, 0.15, 0.30, 0.45, 0.60, 0.75 and 0.90 at $r$ = 0.4 m; $r$ = 0.2, 0.3, 0.4, 0.5 and 0.6 m at $d$ = 0.3 m; $T_B$ = 60 to 400 °C at the working geometry. Both emissivities stay fixed throughout. The smallest gap among these geometry points is 0.06 m. The concentric point is the uniform-flux reference and the starting point of the eccentricity sweep.

### How results from two calculations are compared

This is a numerical comparison after the radiation equations have been solved. It defines the **Profile change (%)** column; it is separate from the physical model in equations (1)–(14).

Call the first calculation $c$ and the more resolved calculation $f$. For a surface-refinement comparison, $f$ has more segments. For an integration-tolerance comparison, both segment counts stay fixed and $f$ uses the tighter tolerance.

Let $\widetilde q_c$ and $\widetilde q_f$ be the two B-flux curves obtained by straight-line, periodic interpolation of the calculated segment averages at their midpoint angles. Compare them at the same positions, $\theta_k=360^\circ k/4096$, for $k=0,\ldots,4095$:

$$
C_q=100\frac{\displaystyle\max_{k=0,\ldots,4095}
\left|\widetilde q_c(\theta_k)-\widetilde q_f(\theta_k)\right|}
{|\bar q_{B,f}|}.
\tag{C1}
$$

In words: find the largest separation between the two flux curves, divide by the more resolved calculation's mean flux from equation (12), and multiply by 100. This gives **Profile change (%)**.

The 4096 angles are a chosen comparison setting. They add no surface segments or new radiation solutions. Periodic interpolation connects the last angular values back to the first across 360° and 0°.

The other two change columns use the $D_{\max}$ and $D_{pp}$ values from equation (13), calculated from each solution's original segment averages:

$$
\Delta D_{\max}=|D_{\max,c}-D_{\max,f}|,\qquad
\Delta D_{pp}=|D_{pp,c}-D_{pp,f}|.
\tag{C2}
$$

These changes are measured in **percentage points (pp)**. Small changes support stability under refinement; they do not give a guaranteed bound on the error relative to the exact solution.

**Code:** [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `compare`, implements (C1), (C2), the 4096 comparison angles and periodic interpolation. The same function is used for the independent surface checks, integration-tolerance checks, 12-arrangement check and extra smallest-gap check.

### Independent baseline refinement

**Code:** [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `independent`, runs the surface and integration-tolerance cases using [`radiation.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/radiation.py).

The outer surface was refined through 24, 48, 96 and 192 segments with the inner surface held at 128. The inner surface was refined through 16, 32, 64 and 128 segments with the outer surface held at 192. This separates their effects; both surfaces were not simply increased together.

| Refinement (A/B segments) | $D_{\max}$ change (percentage points) | $D_{pp}$ change (percentage points) |
| --- | ---: | ---: |
| 24/128 to 48/128 | 0.051272 | 0.064188 |
| 48/128 to 96/128 | 0.012871 | 0.016035 |
| 96/128 to 192/128 | 0.003233 | 0.004028 |
| 192/16 to 192/32 | 0.140154 | 0.181613 |
| 192/32 to 192/64 | 0.035871 | 0.046180 |
| 192/64 to 192/128 | 0.009021 | 0.011595 |

The inner 16-to-32 refinement fails the 0.1 percentage-point criterion. Finer meshes stabilize. Although the baseline alone permits smaller grids, the choice must also cover the larger offsets in part (b).

### Qualification across the study points

Accept changes below 0.5% in the maximum difference of interpolated flux profiles, and below 0.1 percentage points in both $D_{\max}$ and $D_{pp}$. Normalize profile differences by the refined grid's mean inner flux. Periodic interpolation uses a shared 4096-angle grid and segment averages; it is a comparison method, not an exact pointwise solution.

Each of the 12 distinct geometry points was compared at 96/128 and 192/256 segments. All pass the three criteria.

**Code:** [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `qualify`, runs these arrangements and compares both meshes using `compare`.

| $r$ (m) | $d$ (m) | $e$ | Profile change (%) | $D_{\max}$ change (pp) | $D_{pp}$ change (pp) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.40 | 0.30 | 0.500 | 0.005695 | 0.005491 | 0.006929 |
| 0.40 | 0.00 | 0.000 | 0.000000 | 0.000000 | 0.000000 |
| 0.40 | 0.09 | 0.150 | 0.000800 | 0.000787 | 0.001313 |
| 0.40 | 0.18 | 0.300 | 0.002126 | 0.002070 | 0.002994 |
| 0.40 | 0.27 | 0.450 | 0.004494 | 0.004342 | 0.005641 |
| 0.40 | 0.36 | 0.600 | 0.009133 | 0.008783 | 0.010556 |
| 0.40 | 0.45 | 0.750 | 0.019427 | 0.018657 | 0.021227 |
| 0.40 | 0.54 | 0.900 | 0.047166 | 0.045451 | 0.049711 |
| 0.20 | 0.30 | 0.375 | 0.001987 | 0.001891 | 0.002530 |
| 0.30 | 0.30 | 0.429 | 0.003578 | 0.003429 | 0.004453 |
| 0.50 | 0.30 | 0.600 | 0.008398 | 0.008140 | 0.009991 |
| 0.60 | 0.30 | 0.750 | 0.011441 | 0.011134 | 0.013361 |

### Why the inner grid was increased from 64 to 128

At $e = 0.9$, the coarser 96/64 mesh passes comparison with 192/128. Its $D_{pp}$ nevertheless differs from the additional 384/256 reference by 0.102032 percentage points, just above the threshold. Increasing the inner grid to 128 reduces the difference to 0.059172 percentage points and the profile difference to 0.056176%. This additional check avoids relying on a marginal first comparison.

**Code:** [`run_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py), function `worst_case`, runs these additional resolutions at the same smallest-gap arrangement.

### Integration and temperature checks

At 96/64 resolution in the working case, tightening the integration tolerance from $10^{-6}$ to $10^{-9}$ changes the nonuniformity measures by less than $2\times10^{-9}$ percentage points between successive tolerances. At the selected 96/128 resolution, tolerances $10^{-8}$ and $10^{-9}$ were also compared in the working case and at $e = 0.9$.

- Working case: profile change $1.7\times10^{-11}$%; $D_{pp}$ change $1.3\times10^{-11}$ percentage points.
- Largest center distance ($e = 0.9$): profile change $2.6\times10^{-10}$%; $D_{pp}$ change $2.9\times10^{-11}$ percentage points.

Temperature checks at 60, 200 and 400 °C, in the working case and at $e = 0.9$, leave the normalized nonuniformity unchanged to within about $2\times10^{-12}$ percentage points. This agrees with the linear fixed-emissivity model, in which temperature scales the absolute flux through $\sigma(T_B^4-T_A^4)$, equation (14). It would not hold if the emissivity varied with temperature.

Across the selected-mesh qualification and reference cases, the largest relative energy imbalance is $4.5\times10^{-12}$, the largest row-closure residual is $7.9\times10^{-15}$, and the largest scaled reciprocity residual is $5.8\times10^{-8}$.

### Decision based on the refinement evidence

Use **96 equal angular segments on cylinder A and 128 on cylinder B**, with integration tolerance $10^{-8}$, for the documented final parameter-study points. The interactive simulation uses a coarser 24/32 mesh for speed and is not part of the reported results.

**Code:** [`finalize_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/finalize_discretization.py) checks the recorded evidence and saves the selected settings. [`plot_discretization.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/plot_discretization.py) draws the selection-evidence figure.

### Selected-mesh baseline result

- Mean flux on B, $\bar q_B$: 1549.473679 W/m².
- $D_{\max}$: 4.734188%.
- $D_{pp}$: 8.206598%.
- Heat from B per unit length, $Q'_B$: 3894.252103 W/m.

### Scope and reproducibility

The selection is supported at the 12 documented geometry points with $\epsilon_A = 0.6$ and $\epsilon_B = 0.8$. The comparisons are differences between meshes, not rigorous error bounds, and they do not qualify other radius, offset or emissivity combinations. The interactive simulation uses a coarser mesh and is for exploration only.

The interpretation of all three parameter studies is presented in PARAMETERS.md.

Run the following from the repository directory (local caches in tmp/ make repeat runs faster):

```powershell
python scripts/run_discretization.py --stage independent
python scripts/run_discretization.py --stage worst-case
python scripts/run_discretization.py --stage qualify --outer 96 --inner 128
python scripts/run_discretization.py --stage support --outer 96 --inner 128
python scripts/finalize_discretization.py
python scripts/plot_discretization.py
```

Raw case tables, angular profiles, comparison tables, source fingerprints, and selected settings are stored in results/discretization/. The completed parameter studies use this selected mesh; see PARAMETERS.md and REPORT.md.


![Independent mesh selection](../results/discretization/discretization_selection.png)

![Selected-mesh baseline flux](../results/studies/baseline_flux.png)

## Part (b): influence of physical parameters

**Assignment requirement (b)**

> Using the same thermodynamic model and the selected discretization, analyse the influence of parameters $r$, $d$, and $T_B$, on the deviation from uniform surface density of cylinder B.

All cases use $N_A = 96$ and $N_B = 128$ segments, integration tolerance $10^{-8}$, $R = 1$ m, $T_A = 30$ °C, $\epsilon_A = 0.6$ and $\epsilon_B = 0.8$. Only the named parameter changes within each study. All reported values of $q$ are segment averages.

**Code:** [`run_parameter_studies.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_parameter_studies.py) runs the three studies with the selected settings using [`radiation.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/radiation.py). [`plot_studies.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/plot_studies.py) generates these figures and the written report; [`study_data.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/study_data.py) checks the recorded data and prepares the commentary.

### Center distance d

At fixed $r$ = 0.4 m and $T_B$ = 200 °C, increasing $d$ from 0.00 to 0.54 m increases $D_{\max}$ from zero to 13.933% and $D_{pp}$ to 21.358%, while the mean flux $\bar q_B$ changes only from 1558.02 to 1521.27 W/m². The concentric case is the uniform-flux reference; all other points are eccentric. For these gray surfaces, the narrow-gap side of B loses less heat per unit area than the wide-gap side. Although A is isothermal, its radiosity is not uniform, because A also reflects the nonuniform radiation it receives from B. The narrow-gap side of B therefore receives more irradiation $G_i$, and by equation (7), $q_i=\epsilon_B(\sigma T_B^4-G_i)$, a larger irradiation gives a smaller net outward flux. The pattern results from the coupled exchange in the whole enclosure, not from the local gap width alone.

| $r$ (m) | $d$ (m) | $T_B$ (°C) | $\bar q_B$ (W/m²) | $D_{\max}$ (%) | $D_{pp}$ (%) | $Q'_B$ (W/m) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.4 | 0 | 200 | 1558.016783 | 0.000000 | 0.000000 | 3915.723263 |
| 0.4 | 0.09 | 200 | 1557.320269 | 1.138305 | 2.179610 | 3913.972733 |
| 0.4 | 0.18 | 200 | 1555.150222 | 2.459528 | 4.513215 | 3908.518811 |
| 0.4 | 0.27 | 200 | 1551.242856 | 4.089777 | 7.192051 | 3898.698528 |
| 0.4 | 0.36 | 200 | 1545.072639 | 6.237372 | 10.500921 | 3883.191083 |
| 0.4 | 0.45 | 200 | 1535.673935 | 9.281182 | 14.926887 | 3859.569562 |
| 0.4 | 0.54 | 200 | 1521.265304 | 13.933297 | 21.358301 | 3823.356722 |

![Center distance d results](../results/studies/offset_study.png)

### Inner radius r

At fixed $d$ = 0.3 m and $T_B$ = 200 °C, increasing $r$ from 0.2 to 0.6 m increases $D_{\max}$ from 1.948% to 8.181%. The mean flux $\bar q_B$ decreases from 1703.45 to 1420.67 W/m², while the heat rate per unit length $Q'_B$ rises from 2140.62 to 5355.81 W/m because the circumference of B grows. With $d$ fixed, the normalized eccentricity $e=d/(R-r)$ rises from 0.375 to 0.750 and the minimum gap narrows from 0.50 to 0.10 m. These results therefore describe radius changes at fixed center distance, not at fixed $e$.

| $r$ (m) | $d$ (m) | $T_B$ (°C) | $\bar q_B$ (W/m²) | $D_{\max}$ (%) | $D_{pp}$ (%) | $Q'_B$ (W/m) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.2 | 0.3 | 200 | 1703.454772 | 1.948488 | 3.490679 | 2140.624399 |
| 0.3 | 0.3 | 200 | 1622.909791 | 3.233448 | 5.696237 | 3059.112885 |
| 0.4 | 0.3 | 200 | 1549.473679 | 4.734188 | 8.206598 | 3894.252103 |
| 0.5 | 0.3 | 200 | 1482.288631 | 6.421594 | 10.968284 | 4656.747072 |
| 0.6 | 0.3 | 200 | 1420.672289 | 8.180997 | 13.827983 | 5355.808353 |

![Inner radius r results](../results/studies/radius_study.png)

### Inner temperature

At fixed $r$ = 0.4 m and $d$ = 0.3 m, raising $T_B$ from 60 to 400 °C increases the mean flux $\bar q_B$ from 144.00 to 7320.48 W/m², a factor of 50.84. $D_{\max}$ stays at 4.734188%; across the six temperatures it varies by only $1.2\times10^{-12}$ percentage points. With fixed geometry and temperature-independent emissivities, the radiosity equations are linear and the flux scales with $\sigma(T_B^4-T_A^4)$, equation (14). The normalized angular profile is therefore unchanged. This would not hold for materials whose emissivity depends on temperature.

| $r$ (m) | $d$ (m) | $T_B$ (°C) | $\bar q_B$ (W/m²) | $D_{\max}$ (%) | $D_{pp}$ (%) | $Q'_B$ (W/m) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.4 | 0.3 | 60 | 144.004152 | 4.734188 | 8.206598 | 361.921909 |
| 0.4 | 0.3 | 100 | 406.862619 | 4.734188 | 8.206598 | 1022.557293 |
| 0.4 | 0.3 | 150 | 878.070690 | 4.734188 | 8.206598 | 2206.832344 |
| 0.4 | 0.3 | 200 | 1549.473679 | 4.734188 | 8.206598 | 3894.252103 |
| 0.4 | 0.3 | 300 | 3698.399508 | 4.734188 | 8.206598 | 9295.091780 |
| 0.4 | 0.3 | 400 | 7320.483414 | 4.734188 | 8.206598 | 18398.381531 |

![Inner temperature results](../results/studies/temperature_study.png)

### Numerical consistency

Across the 19 cases, the largest relative energy imbalance is $1.7\times10^{-12}$, the largest view-factor closure residual is $5.8\times10^{-15}$, and the largest scaled reciprocity residual is $5.6\times10^{-8}$. These are consistency checks; the mesh itself was selected by the refinement comparisons.

Reproduce with `python scripts/run_assignment.py`. Source fingerprints and raw tables are in results/studies/manifest.json, cases.csv and profiles.csv.


## Part (c): discussion and conclusions

**Assignment requirement (c)**

> Supplement all analyses with appropriate descriptions, diagrams, and commentary, and compare the results with analytical solutions, if find appropriate.

1. The diffuse-gray radiosity model gives a nonuniform flux on B in the eccentric working case: $\bar q_B$ = 1549.473679 W/m², $D_{\max}$ = 4.734188% and $D_{pp}$ = 8.206598%.
2. Independent refinement of the two surfaces is necessary: stable total heat alone does not establish resolution of local nonuniformity. The selected 96/128 mesh passes the documented profile and metric-change criteria at all 12 geometry points, with an additional high-eccentricity check.
3. At the stated fixed emissivities, increasing center distance or increasing radius at fixed center distance increases relative nonuniformity over the studied ranges. The two variations change enclosure geometry in different ways.
4. Increasing prescribed inner temperature increases absolute flux, while normalized nonuniformity remains unchanged under the temperature-independent-emissivity model.
5. Interactive motion displays successive steady states, not physical transient heating. Mirroring B across the y-axis mirrors its flux profile without changing scalar heat-rate or nonuniformity measures.

## Limitations

The finite-mesh criteria are practical differences between meshes, not rigorous bounds on the exact solution. Qualification applies to the listed geometry points and fixed emissivities. Arbitrary near-contact or different-emissivity explorations need their own convergence assessment. Prescribed isothermal infinite cylinders omit end effects, participating media and transient energy storage.

## Code and reproduction

### Guide to the calculation scripts

The links below open the corresponding files on GitHub. The same files are included in the downloadable ZIP, so the calculations can also be inspected and run offline.

| Calculation or output | Script on GitHub | What it does |
| --- | --- | --- |
| Circular geometry, view factors and integration tolerance | [radiation.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/radiation.py) | Defines the surface arcs and normals; `calculate_view_factors` handles visibility, directional intervals and adaptive source-arc integration. |
| Radiosity balance, net flux, energy balance, mean flux, D_max and D_pp | [radiation.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/radiation.py) | `solve_radiation` solves the coupled equations; `RadiationResult.metrics` evaluates the reported measures from the segment-average fluxes. |
| Surface and tolerance refinement, 4096-angle comparisons, 12 arrangements and extra smallest-gap check | [run_discretization.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_discretization.py) | Runs the calculation cases; `compare` implements comparison equations (C1) and (C2). |
| Selecting settings for part (b) | [finalize_discretization.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/finalize_discretization.py) | Checks the recorded evidence and writes the selected settings and discretization report. |
| Radius, center-distance and temperature studies | [run_parameter_studies.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_parameter_studies.py) | Runs the three studies with the selected settings and saves their flux profiles and numerical results. |
| Discretization figure | [plot_discretization.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/plot_discretization.py) | Draws the selection-evidence figure from recorded results. |
| Geometry diagram, study figures and written report | [plot_studies.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/plot_studies.py) | Creates the figures and report from the recorded calculations and model documentation. |
| Report-data checks and parameter-study commentary | [study_data.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/study_data.py) | Checks data integrity and consistency, and prepares the parameter-study descriptions. |
| Website sections and interactive plots | [report_ui.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/report_ui.py), [app_charts.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/app_charts.py) | Present the recorded report results, comparison explanations and interactive charts. |
| Interactive steady-state simulation and surface arrows | [streamlit_app.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/streamlit_app.py), [flux_plot.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/flux_plot.py) | Solve the user-selected case using `radiation.py` and display its flux. Eight arrow values are interpolated from the calculated segment averages; their drawing scale fits the gap. |
| Numerical validation | [tests/test_solver.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/tests/test_solver.py), [tests/test_studies.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/tests/test_studies.py) | Test the solver's physical consistency and the recorded studies' meanings and integrity. |
| Written report as PDF | [build_report_pdf.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/build_report_pdf.py) | Typesets REPORT.md, including its equations and figures, and prints it to REPORT.pdf. |
| Reproducing the complete assignment | [run_assignment.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_assignment.py) | Runs the refinement, selection, parameter-study, figure, report and packaging stages in order. |
| Downloadable submission package | [build_submission.py](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/build_submission.py) | Collects the report, figures, results, source and tests into a ZIP with a file-hash manifest. |


The downloadable submission package contains this report, all figures and tables used here, the numerical module, study runners, website source, tests, requirements and a file-hash manifest. From its root directory:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/run_assignment.py
python -m streamlit run scripts/streamlit_app.py
```

Numerical solver SHA-256: `d7215049ac5fbece16e4a613b32ec29ed5aaaa28056abb09556b794f455d6efb`.
