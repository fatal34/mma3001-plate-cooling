# MMA3001: verified plate cooling

A reproducible comparison of **FTCS** and **backward Euler** for one-dimensional transient conduction through a homogeneous plate. The engineering output is the time when the hottest point falls below a specified temperature, together with accuracy, stability and computational-cost evidence.

The topic is approved according to the user's confirmation on 24 October 2026. The confirmed extension ends at midnight at the end of Sunday 25 October 2026, Melbourne time. This repository is prepared with substantial AI assistance, disclosed in [the AI record](notes/ai_use_log.md). Student review, unaided understanding and Moodle submission remain actual student responsibilities.

## Main result

For the illustrative 10 mm plate, alpha = 1e-5 m²/s, initially 100°C with both faces fixed at 20°C, the analytical time to 40°C is **1.649365095 s**.

The final selected FTCS configuration uses **20 intervals, dt = 0.00625 s and r = 0.25**. It predicts **1.645588260 s**, a **0.22899%** crossing-time error. The largest temperature error across five declared positive benchmark times is **0.58896°C**. Its measured median runtime was **2.873 ms**, versus **6.494 ms** for the fastest implicit candidate meeting the same revised development margin. Timings describe this machine/run, not a universal ranking.

The first, faster choice narrowly met the 1°C baseline target but failed the initial larger-span confirmation at **1.18037°C**. That failure is preserved. A transparent revision adds a 0.8°C development margin without relaxing the original 1°C acceptance limit. The final configuration passes a fresh mathematical confirmation with **0.55215°C** temperature error and **0.21375%** cooling-time error. The inspected first confirmation is subsequently development evidence. See [the complete numerical record](results/summary.json), [initial record](results/initial_summary.json) and [revision policy](configs/design_revision.json).

## Deliverables

| Item | Location |
| --- | --- |
| Technical report, 9 main-content pages plus references | [reports/MMA3001_technical_report.pdf](reports/MMA3001_technical_report.pdf) |
| Editable report source | [reports/MMA3001_technical_report.md](reports/MMA3001_technical_report.md) |
| Source and API | [src/heat_project](src/heat_project), [generated HTML](docs/html/index.html) |
| Automated test functions and generated report | [tests](tests), [test report](reports/test_report.html) |
| CSV evidence and summary | [results/tables](results/tables), [summary](results/summary.json) |
| Scientific figures, PNG and vector PDF | [results/figures](results/figures) |
| Editable presentation and speaker script | [presentation](presentation) |
| Full derivation, provenance, rubric audit | [docs](docs) |
| AI disclosure, decisions and interview preparation | [notes](notes) |

## Environment and installation

Use **Python 3.12 or later** with an appropriate wheel-compatible operating system. The recorded run uses Python 3.12.14 on macOS 15.6.1 arm64. NumPy 2.3.5, SciPy 1.18.1 and Matplotlib 3.11.2 are pinned with all required Python dependencies in `requirements.txt`. No GPU, external dataset, paid package or COMSOL installation is required.

From a clone or unzipped repository, on macOS/Linux:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/reproduce.py
```

On Windows, replace `.venv/bin/python` with `.venv\Scripts\python.exe`. The scripts locate the project relative to their own files. Run the documented commands from the repository root. A network connection is needed for initial package installation, but **all numerical experiments then run offline**.

`reproduce.py` runs tests, initial experiments and the documented revision into a separate verification directory, checks numerical agreement with the saved submission, then regenerates figures, API documentation and the report from the preserved submitted evidence. The reference run takes about a minute or a few minutes depending on hardware. A slower machine may take longer. No application or notebook state is required.

To check the submitted code/documentation without regenerating numerical evidence:

```sh
.venv/bin/python scripts/reproduce.py --skip-experiments
```

To reproduce only the numerical evidence into another directory:

```sh
.venv/bin/python scripts/run_experiments.py --output-dir tmp/reproduced_results
.venv/bin/python scripts/apply_design_revision.py --output-dir tmp/reproduced_results
```

Numerical values should agree within round-off for the same settings. Timing distributions and therefore the fastest measured eligible candidate can change with machine load/hardware. Reports and slides in the submitted package describe the saved run. If regenerating on another machine changes the selected candidate or measured runtimes, regenerate all result-dependent report/presentation wording before submitting a new version. `reproduce.py` preserves the submitted record, checks the recorded selected configuration and analytical crossing numerically, and saves fresh machine-dependent timings separately under `tmp/reproduced_results`.

## One configured case

```sh
.venv/bin/python scripts/run_case.py --config configs/baseline.json --output results/single_case
```

This writes `.npz` arrays and a `.json` summary. The baseline file intentionally describes the original finer N=80, dt=0.0005 configuration used for comparison. The selected settings are in `configs/selected.json`.

## Input and output contract

`PlateConfig` takes full thickness `length_m` in metres and constant `diffusivity_m2_s` in m²/s, both finite and positive, plus finite temperatures in °C. The reported cooling study and analytical crossing require **boundary < target < initial**. The underlying mathematical solver also permits equilibrium/heating and zero/negative sine amplitudes for verification; the supplied study does not claim performance for arbitrary such cases.

`SolverConfig` takes integer `intervals >=4`, positive finite `dt_s` and `end_time_s`, `method` (`ftcs` or `backward_euler`), `profile` (`uniform` or `sine`) and FTCS implementation (`loop` or `vectorized`). Normal FTCS rejects r>0.5. `allow_unstable=True` is an explicit diagnostic option. Nonfinite or unsupported inputs raise descriptive errors. The command-line JSON file requires the top-level `plate` and `solver` sections. Within each section, omitted parameters use the documented dataclass defaults; unknown parameter names raise errors. The supplied configuration files state all parameters explicitly.

`solve` returns `x_m` (N+1 positions), `times_s` and `max_temperature_c` (M+1 samples), `temperature_snapshots_c` (S, N+1), `snapshot_times_s` (S), final temperatures (N+1), step count and largest actual diffusion number. Temperatures are °C and times are seconds. An empty snapshot request retains no field snapshots; default retains initial/final. Explicit interior snapshot times may shorten steps. The endpoint is exact, including a shortened last step. `threshold_crossing_time` returns the first interpolated crossing in seconds or `None` if not reached. No failed result is silently converted into a success.

## Numerical approach and validation

The full-thickness heat equation has equal fixed face temperatures, constant properties, no source and no lateral gradients. FTCS updates from the old field simultaneously. Backward Euler solves a tridiagonal system with known boundary terms in the right-hand side. The banded matrix can be reused when r is identical, but `solve_banded` still performs the solve/factorisation at each step.

Verification uses a smooth exact sine solution, a converged odd Fourier series for uniform cooling, an independently written scalar-series crossing audit, a tiny hand-worked implicit system and physical bounds/symmetry checks. Separate spatial and temporal studies avoid conflating discretisation errors. **64 automated tests** cover those checks and input/failure contracts. The runtime sweep compares 29 distinct configurations with unchanged 1°C/2% acceptance limits and a <1% refinement criterion. The revision adds explicit temperature-error headroom and records the first failure.

Analytical agreement verifies the specified mathematical model. **There is no experimental physical validation.** These synthetic properties are not presented as measured aluminium data. Fixed surface temperatures represent ideal controlled thermal contact, not general convection. The threshold is an analysis target, not a certified safe-handling temperature. See [provenance](docs/data_provenance.md) and [derivation](docs/engineering_derivation.md).

## Tests, profiling and documentation

```sh
.venv/bin/python -m pytest --html=reports/test_report.html --self-contained-html --junitxml=reports/test_results.xml
.venv/bin/python scripts/generate_docs.py
.venv/bin/python scripts/make_figures.py
.venv/bin/python scripts/build_report.py
```

`reports/profile.txt` contains actual cumulative profiling of the loop implementation. Runs using an alternative `--output-dir` save their own `profile.txt` there and preserve the submitted profile. The controlled vectorisation comparison preserves grid, time step and outputs, and found zero output difference. Runtime tests warm up the solver, then use repeated batches with a 40 ms target and 20-solve cap, reporting median/range. References, plotting and disk I/O are excluded. Array byte counts measure retained NumPy storage, **not peak process RAM**. Scalar time/max histories use O(M), field work O(N), requested snapshots O(SN). Avoid claiming the whole result consumes only O(N).

## Repository and submission

The actual local development history, including genuine AI-attributed checkpoints through `982b135`, is preserved in [notes/development_history.bundle](notes/development_history.bundle). The connected GitHub publication creates new current commits with explicit AI attribution. Those publication commits are distinct from the preserved development history; no backdating or personal student authorship is fabricated. A clean clone at `114615e` completed the full workflow using a fresh pinned environment, with 64 passing checks and matching selected numerical values. See [the verification record](docs/verification_record.md).

[Submission status](docs/submission_status.md) records the final hosted commit, archive/checksum checks and remaining external steps. After the final commit, `scripts/package_submission.py` creates `dist/MMA3001_repository_clone.zip`, containing a clean clone, its publication history and the preserved local development bundle, plus `dist/submission_manifest.json` with the commit, remote and SHA-256 checksum. These packaging outputs remain outside version-controlled content.

Submit the technical report, final repository clone/archive and accessible GitHub link in Moodle. Verify assessor access if the repository is private. Book and attend the five-minute presentation plus three-minute questions, and upload any slides at least 24 hours before the booked session as directed by the workshop. Creating artifacts does not itself submit them or establish unaided understanding.

## Licence and references

Original project code/documentation use the [MIT licence](LICENSE). Third-party libraries retain their own licences. No university PDFs are redistributed. Primary numerical/API references and course-document citations appear in the report and `docs/engineering_derivation.md`.
