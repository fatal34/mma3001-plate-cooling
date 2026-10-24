# Verification and reproduction record

Recorded 24 October 2026, Australia/Melbourne. These are checks performed by AI through tools. They do not establish student personal review, understanding, Moodle submission or interview attendance.

## Clean environment and clean Git clone

A clean clone at **`114615e399c7e53cf99a735964656d250307ce02`** ran the full `scripts/reproduce.py` workflow using a newly created Python environment installed from the pinned `requirements.txt`. The workflow completed with **exit code 0**. The fresh environment and clone were located under `tmp/clean_env` and `tmp/clean_copy_final`; these temporary directories are not required for running the delivered project.

The saved clean-run test XML records **64 tests, zero failures, zero errors and zero skips**. Its suite time is **9.031 s**; the terminal reports `64 passed in 9.03s`. This is the test-suite duration, not the duration of the complete experiment/documentation workflow. The clean-run HTML/XML reports are retained in canonical `reports/test_report.html` and `reports/test_results.xml`; `reports/clean_reproduction.log` records the actual workflow output. Temporary originals remain in `tmp/clean_reproduction_final.log` and the clean clone.

The workflow executed the initial experiments and transparent design revision into separate reproduced-result storage. It checked the recorded selected configuration, regenerated all six PNG/PDF figure pairs, generated complete package/module HTML documentation and regenerated the technical PDF with **nine main-content pages plus one references page**. Existing saved study results and their report wording retain the original measured run; fresh machine-dependent timing evidence stays separate.

| Checked quantity | Recorded value | Clean reproduction | Absolute difference |
| --- | ---: | ---: | ---: |
| Analytical reference crossing | 1.6493650949162348 s | 1.6493650949162348 s | 0 |
| Selected FTCS maximum benchmark error | 0.5889600321622765 C | 0.5889600321622765 C | 0 |
| Selected FTCS crossing | 1.645588259786538 s | 1.645588259786538 s | 0 |

The selected configuration is `N=20`, `dt=0.00625 s`, `r=0.25`. Reproduction matched its method/grid/step row uniquely. The workflow's numerical checks allow at most `1e-9` difference in the checked crossing/error values. Timings and the fastest measured candidate can vary between runs; exact timing reproduction is not claimed.

The submitted `reports/profile.txt` remained byte-for-byte unchanged during clean reproduction. Both copies have SHA-256:

`f0e2310f29257ec5b1d130fa781e27c528074cbf94bee2f3a4972bb561a8b2e3`.

## Numerical and decision evidence

The implementation has exact-sine and converged Fourier-series references, a separately written scalar centre-root check, a hand-worked tiny implicit system and linear residual, boundary/symmetry/bounds checks, independent time/space refinement and explicit failure-contract tests. The reference, error and timing results are retained in `results/tables/` and `results/summary.json`.

The initially fastest baseline setting (`N=20`, `dt=0.01 s`) recorded maximum error **0.993997761 C**, then failed its first larger-temperature-span check at **1.180372342 C**. The preserved initial record remains in `results/initial_summary.json`. A documented post hoc **0.8 C development ceiling** preserves the original **1 C absolute acceptance limit** and selects `dt=0.00625 s`. The inspected failed case becomes development evidence. The frozen revised setting reaches **0.552150030 C** maximum error and **0.213748382%** crossing error in a fresh mathematical confirmation, without further retuning. None of these checks is empirical physical validation.

## Artifact and documentation QA

- The technical report contains nine main pages and one reference page, with all requested report topics. Rendered report and scientific figures were visually reviewed. Its input/output contract states formats, units and array meanings. Its performance section labels retained-array storage and the approximate **45,600 basic selected-stencil operations** (`5 * 19 * 480`) separately from timing/other overhead.
- Generated HTML includes the package's ten public exports and full pages for `model`, `solvers`, `reference` and `metrics`. Public source functions/classes have consistent documented parameters, returns and exceptions. HTML regeneration completed in the clean workflow.
- The editable presentation contains six slides, three native tables, two native charts with embedded workbook snapshots, and six speaker-note parts with timing and sources. Packaged integrity, layout, chosen-font policy, first-party reimport and native-chart/workbook checks passed. Each final slide was rendered after reimport and visually inspected.
- The slide PDF is a static handout assembled from final PowerPoint renders. All six PDF pages were rendered with Poppler and inspected. The native PDF exporter lacked a bundled font module, so native-vector slide export is not claimed. No native PowerPoint application test is claimed.
- Chart workbook values use 12 significant digits to remain portable within spreadsheet precision limits. Original CSV numerical evidence retains full precision.

## Development history and publication boundary

Actual local development commits are preserved through **`982b135540d4d3d6750bf509c775a24918e5c17a`** in `notes/development_history.bundle`. The bundle includes genuine checkpoints for model/tests (`271decb`), measured evidence/artifacts (`e8eea09`), clean-reproduction preservation (`114615e`) and preservation of the repository's original initial commit (`982b135`). These commits describe actual AI-assisted work; no backdated development or personal student authorship is claimed.

The bundle's recorded main head is `982b135540d4d3d6750bf509c775a24918e5c17a`; its SHA-256 is:

`9933219375f89632115908026dc22a2fb0eae4f6d1b23539ad22d6b276fb1b6c`.

The user supplied the public repository `https://github.com/fatal34/mma3001-plate-cooling`, and the authenticated connection verified administration/push permission. The terminal Git client lacked publication credentials. Publication therefore uses the connected GitHub API and creates **new current AI-attributed publication commits**, separately from the bundled local development graph.

## Hosted publication and clone packaging

The public `main` branch was published at **`8079411f74ac57b2e1f229ede7cea3762b7f24c5`** and cloned afresh over HTTPS. All **79 published tracked files** matched the prepared local files byte-for-byte. All **21 code, configuration and dependency files** matched the clean clone that completed the full reproduction workflow. The GitHub connection also fetched the published README successfully. Publication preserved the user's initial repository commit as its parent.

`scripts/package_submission.py` ran successfully from the published clone. It created a further clean clone, checked the required artifacts, verified ZIP integrity and confirmed that `.git/HEAD` was included. The original development bundle was retained. The final handoff archive is rebuilt from hosted `main` after the verification-documentation update; the exact final release commit, SHA-256 and size are recorded in the separately delivered `dist/submission_manifest.json`. Keeping the manifest outside its own archive avoids a circular checksum. The final documentation update does not change the tested numerical implementation or saved results.

Moodle upload, booking, attendance and student personal understanding remain external responsibilities.
