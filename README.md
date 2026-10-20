# Analysis of Radiative Heat Transfer Between Two Infinitely Long Cylinders in an Eccentric Arrangement

## Read the completed assignment

- Written report ([PDF](docs/REPORT.pdf) or [Markdown](docs/REPORT.md)): model, discretization selection, all three parameter studies, figures, discussion and conclusions.
- [Requirement-to-evidence map](docs/REQUIREMENTS.md).
- [Model and derivation](docs/MODEL.md).
- [Discretization evidence](docs/DISCRETIZATION.md).
- [Parameter-study interpretation and tables](docs/PARAMETERS.md).

A has radius R = 1 m and prescribed temperature 30 C. B is hotter, diffuse-gray and separated from A by vacuum. Its center distance satisfies d < R-r; the centered case is a numerical reference. Signed interactive position controls left/right placement while d remains nonnegative. All analyses concern infinitely long cylinders and prescribed steady states.

## Repository layout

| Folder | Contents |
| --- | --- |
| `scripts/` | Solver (`radiation.py`), study runners, figure and report generators, and the Streamlit website (`streamlit_app.py`). |
| `docs/` | Model derivation, discretization evidence, parameter studies and the written report. |
| `results/` | Recorded refinement and parameter-study data and figures. |
| `tests/` | Solver, recorded-data and website tests. |

## Run the website

```powershell
python -m pip install -r requirements.txt
python -m streamlit run scripts/streamlit_app.py
```

The website opens on Assignment with the original description and full requirements (a), (b) and (c). Each analysis begins with its corresponding requirement. Part (a) is split into Model and Discretization; part (b) contains the parameter studies; part (c) provides the discussion, conclusions and report, data and code downloads. Interactive simulation is separate: sidebar changes do not modify the reported studies. It uses a fixed, fast 24/32 mesh; the report results use the qualified 96/128 mesh. Eight surface arrows, colors and relative profiles explore local net flux; a fixed-axis directional comparison is available as an optional detail.

## Reproduce all results

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/run_assignment.py
```

The runner performs independent A/B and integration refinement, qualifies the selected 96/128 mesh at all 12 geometry points, runs an additional largest-offset reference, completes all r/d/T_B studies, and exports figures, the written report (Markdown and PDF) and a submission package. The PDF step uses headless Chrome or Edge and downloads KaTeX for the equations. Local view-factor caches in tmp/ reduce repeat work. The source fingerprint canonicalizes line endings for Windows/Linux compatibility.

Completed part (b) contains seven d values, five radii and six inner temperatures, plus the working baseline. All use the same selected discretization and emissivities 0.6/0.8. Numerical residuals and finite-refinement comparisons are recorded separately. The report-data loader checks source versions, data hashes, parameter isolation, physical geometry, mesh consistency and profile/summary agreement.

## Submission package

```powershell
python scripts/build_submission.py
```

The output is `output/eccentric-cylinder-assignment.zip`, also downloadable from the website. It includes this report, figures, raw data, source for every analysis, tests, requirements and a file-hash manifest, and can be read and run offline.

Scientific figures use Matplotlib; interactive charts use Altair. The numerical model uses NumPy and SciPy. The code does not normalize or symmetrize view-factor rows to hide integration residuals. The selected mesh is qualified at the stated report points; arbitrary exploratory cases can need additional refinement. To deploy on Streamlit Community Cloud, set the main file path to `scripts/streamlit_app.py`.
