# Assignment requirements and completed evidence

The scope is the numerical view-factor assignment supplied for Sebastian Alberto Gajardo Lobos, excluding comparison against analytical solutions as requested by the user. The report and website reproduce the full original requirements (a), (b) and (c), with the optional analytical comparison identified as outside the report scope. Assignment introduces all three parts as prose, and each analysis begins with its corresponding full requirement. Part (a) is split into Model and Discretization. The evidence map below is retained as a reference document; it is not displayed as a table on the Assignment page.

| Requirement | Completed evidence | Where to read or reproduce it |
| --- | --- | --- |
| Derive the thermodynamic radiation model | Emission, irradiation, reflection, radiosity linear system, net flux and energy balance; infinite-cylinder view-factor integration | docs/MODEL.md; radiation.py |
| Equal-segment discretization on A and B, counts allowed to differ | Independent A refinement at fixed B, independent B refinement at fixed A, angular profiles and changes in local nonuniformity | (a) Discretization; results/discretization/independent_* |
| Select a discretization | 96 A / 128 B segments, tolerance 1e-8; 12 geometry-point qualification and additional largest-offset reference | docs/DISCRETIZATION.md; results/discretization/selected.json |
| Study r with the same selected mesh | Five radii at fixed center distance, temperature and emissivities; absolute and relative profiles, trend, summary table and discussion | (b) Inner radius r; results/studies/cases.csv and profiles.csv |
| Study d with the same selected mesh | Seven center distances at fixed radius, temperature and emissivities; concentric reference identified separately | (b) Center distance d |
| Study T_B with the same selected mesh | Six temperatures at fixed geometry and emissivities; flux growth and unchanged normalized shape explained | (b) Inner temperature T_B |
| Descriptions, diagrams and commentary | Annotated geometry and segment diagram, convergence evidence, angular profiles, parameter-trend plots, interpretation and limitations | Model, (a), (b), and (c) Discussion and conclusions; docs/REPORT.md |
| Program code for every analysis | Solver, all study runners, plot/report generators, website source, requirements, tests and a file-hash manifest | (c) Discussion and conclusions; downloadable submission ZIP |

## Simplification applied during the review

The interactive simulator remains available, with B inside A, signed left/right motion and eight outward net-flux arrows. The following development options have been retired from the website: artificial arrow-length powers, inward arrows representing deviation rather than actual heat flow, the extra mean-tip circle, provisional implementation-plan pages, and automatic playback that might be mistaken for transient heating. The definition of relative deviation now consistently uses the current B-surface mean. A fixed-scale directional comparison remains an optional detail.

Completed report studies are independent of interactive sidebar settings. Their data loader rejects mixed numerical-source versions, altered data, a changed mesh or an unintended second varying parameter. The report source fingerprint uses canonical line endings so results remain valid on Windows and Linux. Development notes retained in the repository are not part of the submission package.

## Numerical scope

The selected mesh has been checked at the documented geometry points with emissivities 0.6/0.8. Finite differences between refinements are not rigorous exact-solution error bounds. The interactive page may explore other combinations; those are not silently promoted to qualified report results. The professor or candidate remains responsible for reviewing the interpretation and deciding the final submission format.
