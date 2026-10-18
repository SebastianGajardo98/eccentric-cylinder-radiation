# Influence of radius, center distance and temperature

All cases use N_A = 96, N_B = 128, source integration tolerance 1e-8, R = 1 m, T_A = 30 C, epsilon_A = 0.6 and epsilon_B = 0.8. Only the named parameter changes within each study. All reported q values are segment averages.

## Center distance d

At fixed r = 0.4 m and T_B = 200 °C, increasing d from 0.00 to 0.54 m increases maximum relative deviation from approximately zero to 13.933%. The peak-to-peak range reaches 21.358%, while mean flux changes from 1558.02 to 1521.27 W/m². The concentric point is a numerical reference; the other points are eccentric cases. For these gray-surface parameters, the narrow-gap side loses less net heat per area than the wide-gap side. A has uniform temperature but nonuniform radiosity because it also reflects the nonuniform irradiation from B. In these cases the near side of B receives more returning irradiation, reducing its net outward flux through q = epsilon_B (sigma T_B^4 - G_B). This is a coupled enclosure result, rather than a universal rule based on distance alone.

| r (m) | d (m) | T_B (C) | Mean q (W/m^2) | Max deviation (%) | Peak-to-peak (%) | Q'_B (W/m) |
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

At fixed d = 0.3 m and T_B = 200 °C, increasing r from 0.2 to 0.6 m increases maximum relative deviation from 1.948% to 8.181%. Mean flux decreases from 1703.45 to 1420.67 W/m². The total heat per unit length changes from 2140.62 to 5355.81 W/m because the circumference also changes. Holding d fixed makes normalized eccentricity increase from 0.375 to 0.750; the minimum gap decreases from 0.50 to 0.10 m. These conclusions describe radius variation at fixed center distance, not at fixed normalized eccentricity.

| r (m) | d (m) | T_B (C) | Mean q (W/m^2) | Max deviation (%) | Peak-to-peak (%) | Q'_B (W/m) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.2 | 0.3 | 200 | 1703.454772 | 1.948488 | 3.490679 | 2140.624399 |
| 0.3 | 0.3 | 200 | 1622.909791 | 3.233448 | 5.696237 | 3059.112885 |
| 0.4 | 0.3 | 200 | 1549.473679 | 4.734188 | 8.206598 | 3894.252103 |
| 0.5 | 0.3 | 200 | 1482.288631 | 6.421594 | 10.968284 | 4656.747072 |
| 0.6 | 0.3 | 200 | 1420.672289 | 8.180997 | 13.827983 | 5355.808353 |

![Inner radius r results](../results/studies/radius_study.png)

## Inner temperature

At fixed r = 0.4 m and d = 0.3 m, raising T_B from 60 to 400 °C increases mean flux from 144.00 to 7320.48 W/m² (a factor of 50.84). Maximum relative deviation remains 4.734188%: its observed range is 1.18e-12 percentage points. With fixed geometry and temperature-independent emissivities, the linear radiosity equations scale absolute flux with the difference of fourth powers of temperature. The normalized angular shape therefore remains unchanged. This does not apply automatically to materials whose emissivity changes with temperature.

| r (m) | d (m) | T_B (C) | Mean q (W/m^2) | Max deviation (%) | Peak-to-peak (%) | Q'_B (W/m) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.4 | 0.3 | 60 | 144.004152 | 4.734188 | 8.206598 | 361.921909 |
| 0.4 | 0.3 | 100 | 406.862619 | 4.734188 | 8.206598 | 1022.557293 |
| 0.4 | 0.3 | 150 | 878.070690 | 4.734188 | 8.206598 | 2206.832344 |
| 0.4 | 0.3 | 200 | 1549.473679 | 4.734188 | 8.206598 | 3894.252103 |
| 0.4 | 0.3 | 300 | 3698.399508 | 4.734188 | 8.206598 | 9295.091780 |
| 0.4 | 0.3 | 400 | 7320.483414 | 4.734188 | 8.206598 | 18398.381531 |

![Inner temperature results](../results/studies/temperature_study.png)

## Numerical consistency

Across the 19 baseline/study cases, maximum relative energy imbalance is 1.690e-12, maximum view-factor closure residual is 5.773e-15, and maximum scaled reciprocity residual is 5.605e-08. These are consistency checks; mesh selection also uses finite-refinement comparisons.

Reproduce with `python run_assignment.py`. Source fingerprints and raw tables are in results/studies/manifest.json, cases.csv and profiles.csv.
