# Documentation-agent verification audit

These checks were actually performed on 24 October 2026. They supplement, rather than replace, the final automated test report and full reproduction record. Checks were performed by AI through tools; they are not represented as the student's own manual verification.

## Requirement and mathematical checks

- Opened the original 15-page project brief with pdfplumber and read every page, including all four performance bands of all six rubric rows.
- Inspected the rendered rubric pages 10–15 individually to check extraction order and wording.
- Read the supplied project plan and current source files `model.py`, `solvers.py`, `reference.py`, `metrics.py`.
- Checked positive implicit boundary contributions and the banded diagonal arrangement against the derived matrix.
- Checked the Fourier-tail formula analytically: with `f(q)=exp(-a q²)/q` on odd indices, the decreasing-series bound is `f(q)+(1/2) integral_q^infinity f(z) dz = f(q)+E1(a q²)/4`, before multiplying by `4 abs(DeltaT)/pi`.
- Opened primary Berkeley, SciPy, COMSOL and NASA source pages listed in `docs/data_provenance.md`.

## Independent baseline centre-root calculation

Using the project `.venv` interpreter, evaluated the dimensionless centre temperature directly with Python `math.exp` and a 100-term scalar sum, then bracketed its target ratio of 0.25 on `0.05 <= tau <= 0.5` with SciPy `brentq`, `xtol=1e-14`. This scalar expression did not call the project's Fourier temperature implementation. It still shares the mathematical sine-series model and the SciPy root routine, so this is an additional implementation check rather than an independent physical dataset.

| Quantity | Actual calculated value |
| --- | ---: |
| Direct scalar dimensionless root `tau` | 0.16493650949162267 |
| Direct scalar full-series crossing `t = tau L²/alpha` | 1.6493650949162266 s |
| Project `reference_cooling_time(PlateConfig())` | 1.6493650949162348 s |
| Absolute difference | approximately 8.2e-15 s |
| First-mode logarithmic approximation | 1.649365841057121 s |

The agreement checks the baseline centre-root implementation to floating-point accuracy at this target. It does not establish all other parameter cases, early-time fields, solver accuracy or empirical plate-cooling accuracy. Final result tables are the canonical source for the report's numerical claims.

## Final local artifact inspection

Without rerunning unchanged code tests, inspected the saved `reports/test_results.xml`: **64 tests, zero failures, zero errors, zero skips**. Inspected the final report with pdfplumber: **ten pages**, with sections 1–9 on main pages 1–9 and “References and computational evidence” on page 10. Read the editable report and confirmed its primary output units, approximate **45,600 basic selected-stencil operations** (`5 * 19 * 480`, excluding other overhead), preserved failed initial check and final confirmation.

Checked `docs/html/heat_project.html` contains all ten public exports: `PlateConfig`, `SolverConfig`, `SimulationResult`, `solve`, `sine_temperature`, `uniform_temperature`, `reference_temperature`, `reference_cooling_time`, `temperature_errors`, `threshold_crossing_time`. Checked root README includes setup, commands, contracts, data status, limitations, actual numerical choice and submission responsibilities. Read `docs/submission_status.md`; topic approval/cutoff are confirmed, while Moodle/booking/personal understanding are correctly left as external responsibilities.

This agent authored the presentation using Artifact Tool. The final PowerPoint passed packaged integrity, layout, font policy, first-party import and native-chart/workbook checks. All six final slides were rendered after reimporting that final PowerPoint and inspected individually. The PDF handout was assembled from the final slide renders, rendered with Poppler and all six resulting pages inspected. The native PDF exporter lacked a bundled font module, so no native-vector slide PDF export is claimed. The PowerPoint retains native editable tables and charts; chart workbook literals use 12 significant digits for Excel precision portability, while canonical CSVs preserve full precision. No native PowerPoint application test is claimed.

Local Git history inspected here contains authentic commits `271decb` and `e8eea09`. The root task subsequently completed clean-environment/clean-clone reproduction and checked the public hosted files against the prepared project. The exact results and publication/packaging boundaries are in `docs/verification_record.md`. Original local history is retained in `notes/development_history.bundle`; current API publication commits are separately identified.

