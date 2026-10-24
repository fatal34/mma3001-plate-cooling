# Decision record and unresolved responsibilities

All dates use Australia/Melbourne time. The choices below were proposed/implemented by AI under the user's explicit direction to follow the project plan. They are not represented as independently made student decisions.

| Date | Decision | Reason and evidence route | Status/limit |
| --- | --- | --- | --- |
| 24 Oct 2026 | Use idealised one-dimensional slab cooling | Compact mechanical-engineering question with exact solutions and two credible taught numerical methods | User directed implementation of the plan and confirmed teaching-team approval. |
| 24 Oct 2026 | Compare FTCS and backward Euler | Exposes stability, accuracy and computational-cost trade-offs without adding unrelated scope | Actual measured choice is FTCS `N=20`, `dt=0.00625 s`, with 0.588960 C maximum error and 2.87255 ms median solve time. Fastest qualifying BE uses `N=40`, `dt=0.00625 s`, 0.709187 C and 6.49374 ms. |
| 24 Oct 2026 | Use synthetic baseline properties and temperatures | Avoids false material-property or experimental-data claims | Numerical verification only; no real alloy/thermal-process certification. |
| 24 Oct 2026 | Use a smooth sine benchmark before uniform cooling | Separates basic solver correctness from the initial face-temperature jump | Uniform cooling remains a separate engineering test case. |
| 24 Oct 2026 | Use a Fourier-series centre root for reference cooling time | Avoids defining the reference using the same coarse numerical output samples | Actual baseline root is 1.649365094916235 s. Series convergence and an independently written scalar root were checked; see verification audit. |
| 24 Oct 2026 | Use the plan's preliminary error thresholds | Provides a declared selection rule under the user's instruction to follow the plan | These are AI-designed preliminary-study targets rather than independently justified industrial tolerances. The report preserves the original limits and discloses the later tighter development margin. |
| 24 Oct 2026 | Preserve a deliberately unstable FTCS diagnostic | Demonstrates a known failure mode under controlled settings | Normal runs must reject unstable `r`; diagnostic results must remain labelled and unclipped. |
| 24 Oct 2026 | Compare loop and vectorised FTCS | Quantifies an implementation improvement with unchanged mathematics | Actual `N=160`, 640-step comparison records zero output difference and 8.05352 times speedup. This environment-specific measurement differs from changing the grid/time step. |
| 24 Oct 2026 | Keep all numerical claims linked to generated tables | Makes the report auditable and rerunnable | A plot alone or a passing test alone cannot establish engineering validity. |
| 24 Oct 2026 | Disclose substantial AI authorship | Required by the brief and necessary for truthful ownership | Student review and personal learning must be evidenced separately. |
| 24 Oct 2026 | Revise the initially fastest setting after a failed check | Initial baseline error 0.993998 C left little headroom; larger thermal span caused 1.180372 C error | Preserved failure and classified the inspected case as development evidence. Added 0.8 C development ceiling with unchanged 1 C absolute target; see `configs/design_revision.json`. |
| 24 Oct 2026 | Evaluate a fresh final mathematical confirmation | Check the frozen revised setting at another geometry/diffusivity/temperature ratio | Maximum error 0.552150 C and crossing error 0.213748% pass the checked targets. No further retuning; no empirical validation claimed. |

## Student/external actions still required

Actual computational design revision: FTCS N=20, dt=0.01 s initially met the 1 C baseline limit but failed at the larger temperature span. Preserving that evidence, a post-confirmation 0.8 C development margin selects N=20, dt=0.00625 s. The inspected case is development evidence, followed by a fresh mathematical confirmation. See `configs/design_revision.json` and both initial/final summary records. This is an AI-assisted engineering decision, not a fabricated independent student action.

- Teaching-team approval was confirmed by the user; no separate verification of university records is implied, and no message has been sent by the assistant.
- The user confirmed the extension cutoff as midnight at the end of Sunday 25 October 2026, Melbourne time. Aim to finish uploads and checks earlier.
- Review the mathematical assumptions, generated code, test results, computed tables, report and licence. Reproduce a representative run personally.
- Make any student-authored final changes and add a factual personal AI/learning reflection based on actual review.
- The user supplied `https://github.com/fatal34/mma3001-plate-cooling`; authenticated admin/push permission and current public visibility were confirmed. Genuine local commits `271decb` and `e8eea09` preserve actual AI-assisted development. Check the root final publication record for the final hosted `main` commit and archive.
- Submit the 5–10-page main report, accessible repository link and zipped final repository clone via Moodle; retain confirmation.
- Book/attend the required individual five-minute demonstration plus three-minute Q&A and rehearse without AI. If using slides, check the workshop's upload-at-least-24-hours requirement against the current booking directions.

