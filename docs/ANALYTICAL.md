## Comparison with analytical solutions

The assignment states that the flux density on B is uniform when the cylinders are concentric or when both are black bodies. Both limits have closed-form solutions, and so do the whole-body view factors at every center distance. They give exact references for the model in (a). The eccentric diffuse-gray case has no closed-form solution, which is why the view-factor method is needed there.

**Whole-body view factors.** B is convex and completely surrounded by A, so all radiation leaving B reaches A. Reciprocity with the areas per unit length $2\pi R$ and $2\pi r$, followed by closure for A, gives

$$
F_{BA}=1,\qquad F_{AB}=\frac{r}{R},\qquad F_{AA}=1-\frac{r}{R}.
\tag{A1}
$$

These values hold for every center distance $d$. The numerical whole-body factors are area-weighted sums of the arc factors, for example $F_{AB}=\sum_{i\in A}a_i\sum_{j\in B}F_{ij}\,/\sum_{i\in A}a_i$.

**Black surfaces.** With $\epsilon_A=\epsilon_B=1$, equation (2) gives $J_i=\sigma T_i^4$. Every arc on B sees only A, so $\sum_{j\in A}F_{ij}=1$ and equation (3) gives $G_i=\sigma T_A^4$. Equation (7) then gives

$$
q_i=\sigma\left(T_B^4-T_A^4\right)\qquad\text{for every arc } i \text{ on B, at any } d.
\tag{A2}
$$

**Concentric gray cylinders.** At $d=0$ the enclosure is rotationally symmetric, so $J$, $G$ and $q$ are uniform on each cylinder. Eliminating $G$ between (2) and (7) gives, for each surface,

$$
J=\sigma T^4-\frac{1-\epsilon}{\epsilon}\,q.
\tag{A3}
$$

All radiation leaving B reaches A, so $G_B=J_A$ and $q_B=J_B-J_A$. The energy balance (8) gives $2\pi R\,q_A=-2\pi r\,q_B$. Substituting (A3) for both surfaces gives the two-surface enclosure result for long concentric cylinders:

$$
q_B=\frac{\sigma\left(T_B^4-T_A^4\right)}{\dfrac{1}{\epsilon_B}+\dfrac{r}{R}\left(\dfrac{1}{\epsilon_A}-1\right)}.
\tag{A4}
$$

Unlike (A2), this result depends on both emissivities through the repeated reflections between the cylinders.

**What the comparison tests.** The exact solutions (A2) and (A4) are uniform, and piecewise-constant radiosity represents a uniform solution exactly. Agreement is therefore expected at round-off and integration-tolerance level for any segment counts. The comparison verifies the derivation, the linear system (6), the net flux (7) and the view factors, including the tangent directions that bound B's shadow on A. It does not measure the angular resolution of the eccentric gray profile; that has no closed-form solution and is assessed by the refinement study in (a).

All comparisons use the selected 96/128 discretization, integration tolerance 1e-8, $T_A=30$ °C and $T_B=200$ °C. The black-body and view-factor checks cover all 12 arrangements qualified in (a). The concentric check uses $r=0.4$ m with four emissivity pairs, including the report values 0.6/0.8.

**Code:** [`run_analytical.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_analytical.py) evaluates (A1), (A2) and (A4), solves the same cases with [`radiation.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/radiation.py), and records the differences in `results/analytical/comparison.csv`.
