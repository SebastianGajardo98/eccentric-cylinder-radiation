# Influence of radius, center distance and temperature

All cases use $N_A = 96$ and $N_B = 128$ segments, integration tolerance $10^{-8}$, $R = 1$ m, $T_A = 30$ °C, $\epsilon_A = 0.6$ and $\epsilon_B = 0.8$. Only the named parameter changes within each study. All reported values of $q$ are segment averages.

**Code:** [`run_parameter_studies.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/run_parameter_studies.py) runs the three studies with the selected settings using [`radiation.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/radiation.py). [`plot_studies.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/plot_studies.py) generates these figures and the written report; [`study_data.py`](https://github.com/SebastianGajardo98/eccentric-cylinder-radiation/blob/main/scripts/study_data.py) checks the recorded data and prepares the commentary.

## Center distance d

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

## Inner radius r

At fixed $d$ = 0.3 m and $T_B$ = 200 °C, increasing $r$ from 0.2 to 0.6 m increases $D_{\max}$ from 1.948% to 8.181%. The mean flux $\bar q_B$ decreases from 1703.45 to 1420.67 W/m², while the heat rate per unit length $Q'_B$ rises from 2140.62 to 5355.81 W/m because the circumference of B grows. With $d$ fixed, the normalized eccentricity $e=d/(R-r)$ rises from 0.375 to 0.750 and the minimum gap narrows from 0.50 to 0.10 m. These results therefore describe radius changes at fixed center distance, not at fixed $e$.

| $r$ (m) | $d$ (m) | $T_B$ (°C) | $\bar q_B$ (W/m²) | $D_{\max}$ (%) | $D_{pp}$ (%) | $Q'_B$ (W/m) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.2 | 0.3 | 200 | 1703.454772 | 1.948488 | 3.490679 | 2140.624399 |
| 0.3 | 0.3 | 200 | 1622.909791 | 3.233448 | 5.696237 | 3059.112885 |
| 0.4 | 0.3 | 200 | 1549.473679 | 4.734188 | 8.206598 | 3894.252103 |
| 0.5 | 0.3 | 200 | 1482.288631 | 6.421594 | 10.968284 | 4656.747072 |
| 0.6 | 0.3 | 200 | 1420.672289 | 8.180997 | 13.827983 | 5355.808353 |

![Inner radius r results](../results/studies/radius_study.png)

## Inner temperature

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

## Numerical consistency

Across the 19 cases, the largest relative energy imbalance is $1.7\times10^{-12}$, the largest view-factor closure residual is $5.8\times10^{-15}$, and the largest scaled reciprocity residual is $5.6\times10^{-8}$. These are consistency checks; the mesh itself was selected by the refinement comparisons.

Reproduce with `python scripts/run_assignment.py`. Source fingerprints and raw tables are in results/studies/manifest.json, cases.csv and profiles.csv.
