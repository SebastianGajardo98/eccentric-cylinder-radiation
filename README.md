# Radiation between infinite eccentric cylinders

A numerical assignment report and interactive Streamlit simulation for Sebastian Alberto Gajardo Lobos, Heat and Mass Transfer (Radiative Heat Transfer), assigned by Nenad Ferdelji on 12 October 2026.

## Read the completed assignment

- [Written report](docs/REPORT.md): model, discretization selection, all three parameter studies, figures, discussion and conclusions.
- [Requirement-to-evidence map](docs/REQUIREMENTS.md).
- [Model and derivation](docs/MODEL.md).
- [Discretization evidence](docs/DISCRETIZATION.md).
- [Parameter-study interpretation and tables](docs/PARAMETERS.md).

A has radius R = 1 m and prescribed temperature 30 C. B is hotter, diffuse-gray and separated from A by vacuum. Its center distance satisfies d < R-r; the centered case is a numerical reference. Signed interactive position controls left/right placement while d remains nonnegative. All analyses concern infinitely long cylinders and prescribed steady states.

## Run the website

```powershell
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

The website opens on Assignment. Its Model, (a) Discretization, (b) Parameter studies and (c) Discussion and conclusions sections use completed recorded results. Part (c) also provides the report, data and code downloads. Interactive simulation is separate: sidebar changes do not modify the reported studies. Eight surface arrows, colors and relative profiles explore local net flux; a fixed-axis directional comparison is available as an optional detail.

## Reproduce all results

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python run_assignment.py
```

The runner performs independent A/B and integration refinement, qualifies the selected 96/128 mesh at all 12 geometry points, runs an additional largest-offset reference, completes all r/d/T_B studies, and exports figures, the written report and a submission package. Local view-factor caches in tmp/ reduce repeat work. The source fingerprint canonicalizes line endings for Windows/Linux compatibility.

Completed part (b) contains seven d values, five radii and six inner temperatures, plus the working baseline. All use the same selected discretization and emissivities 0.6/0.8. Numerical residuals and finite-refinement comparisons are recorded separately. The report-data loader checks source versions, data hashes, parameter isolation, physical geometry, mesh consistency and profile/summary agreement.

## Submission package

```powershell
python build_submission.py
```

The output is `output/eccentric-cylinder-assignment.zip`, also downloadable from the website. It includes this report, figures, raw data, source for every analysis, tests, requirements and a file-hash manifest. No private repository access is needed to read or run the package. The agreed scope excludes comparisons against analytical solutions; these are not unfinished report items.

Scientific figures use Matplotlib; interactive charts use Altair. The numerical model uses NumPy and SciPy. The code does not normalize or symmetrize view-factor rows to hide integration residuals. The selected mesh is qualified at the stated report points; arbitrary exploratory cases can need additional refinement. The website is local when served at localhost; cloud deployment is a separate step.
