## How results from two calculations are compared

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
