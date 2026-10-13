# First implementation results

These are provisional implementation results, not the completed assignment.

## Surface discretization example

R = 1 m, r = 0.4 m, d = 0.3 m, T_A = 30 C, T_B = 200 C, epsilon_A = 0.6, epsilon_B = 0.8. Source integration tolerance is 1e-8.

| Outer / inner segments | Mean B flux (W/m^2) | Maximum relative deviation (%) | Profile change from previous (%) |
| --- | ---: | ---: | ---: |
| 12 / 8 | 1549.7550 | 3.86066 | - |
| 24 / 16 | 1549.5421 | 4.49138 | 0.64393 |
| 48 / 32 | 1549.4876 | 4.67677 | 0.18875 |
| 96 / 64 | 1549.4738 | 4.72518 | 0.04926 |

Profile changes use periodic linear interpolation of segment averages onto a common 720-angle grid, normalized by the finer case's mean flux. The deviation change from 48/32 to 96/64 is about 0.04841 percentage points.

The mean flux is much less sensitive to this refinement than the nonuniformity measure. Judging convergence only by total heat would understate the surface resolution needed for the assignment's central question.

The final refinement satisfies the provisional combined-grid criteria in PLAN.md for this example. Before choosing the final grid, still examine independent surface refinement and integration tolerance refinement, and consider difficult parameter-study cases. This convergence result is not an error bound or evidence that the same counts are sufficient for every geometry.

The relative energy imbalance across these examples is below 2e-13; maximum row-closure residual is below 6e-15. Reciprocity residual divided by the largest segment area is below 8e-10. These diagnostics check numerical consistency, independently of convergence of the piecewise-constant radiosity approximation.

Raw files are in [results/example](../results/example). Reproduce them with:

```powershell
python run_example.py
```

## Interface and solver checks

- 13 solver tests pass: representative view-factor closure, reciprocity, visibility, concave arc self-view, convex cylinder zero self-view, equilibrium, energy balance, and invalid-input handling.
- A headless smoke check loaded all four Streamlit workspaces, ran two convergence cases, ran six temperature cases, and advanced playback without exceptions.
- In the six-temperature smoke check (60 to 400 C, 24/16 segments), maximum relative deviation stayed at approximately 4.49138% while absolute flux changed. This is consistent with the temperature scaling derived in MODEL.md. A final part (b) study should use the selected discretization.
- No analytical benchmark comparison was performed. This remains an optional later step for part (c).

## Next work

Review the working physical parameters, establish and document the selected discretization, run the full required physical parameter studies, and develop the written interpretation. The prototype is ready for local review; cloud deployment is still pending.
