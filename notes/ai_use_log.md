# AI contribution and verification record

Prepared 24 October 2026 (Australia/Melbourne). This is an evidence record, not a claim that the student has already learned or independently checked every item.

## Disclosure

The user instructed OpenAI Codex to plan and then create the complete project. Codex and collaborating AI agents authored substantial parts of the numerical implementation, automated tests, experiment/plotting workflow, mathematical explanations, supporting documentation and report. The approximate contribution is **substantial to near-total drafting/implementation assistance across these tasks**, rather than minor editing. An exact percentage is not measured. The model identifier should be taken from the user's actual app/session if needed; it is not invented here.

AI was used to complete a consistent, reproducible numerical study within the user's stated short extension and to organise evidence against the rubric. The original brief expressly allows AI throughout the project while requiring full disclosure, checks, responsible ownership, and independent presentation/interview responses. High AI authorship does not itself demonstrate student understanding or meet the rubric's strongest student-led-work descriptor.

| Activity | AI contribution | Evidence/check route | Student involvement/status |
| --- | --- | --- | --- |
| Rubric review, topic ideas and project plan | AI read supplied material and drafted the plan | Original 15-page brief re-read; six rubric pages checked visually; comparison in `docs/rubric_compliance.md` | User accepted the plan, requested complete implementation, and confirmed teaching-team topic approval. |
| Mathematical model and derivation | AI derived finite differences, exact references, stability and cooling scaling | `docs/engineering_derivation.md`; primary method/API sources; analytical/algebraic benchmark tests in final test report | Student's independent derivation/review has not been established. |
| Solvers and input handling | AI authored substantial source code | Run final tests and analytical checks; inspect `reports/test_report.html` and actual source | Student must review public functions, supported domains and failure handling. |
| Test design and execution | AI authored substantial automated tests and ran checks through tools | Final generated test report, test functions, result tables and clean-run record | Passing AI-generated tests is useful evidence, but not an independent human audit. Student review remains unconfirmed. |
| Analysis and selection | AI generated experiments, figures and evidence-based interpretation | Numerical tables, raw timings, reference convergence and final selection criteria | Student must decide whether the assumptions, tolerances and conclusions are defensible for submission. |
| Report and documentation | AI drafted substantial text and generated artifacts | Page-count/render checks, source-to-table consistency, README reproduction, generated HTML | Student must review and take responsibility for all submitted wording and claims. |
| Presentation preparation | AI supplied explanation prompts and model answers | `notes/learning_guide.md`, `notes/interview_questions.md`, `presentation/` | Actual rehearsal, comprehension and interview performance are unverified. AI cannot answer the interview for the student. |

## What was actually checked in this documentation audit

The original `MMA3001_2026_Project_Brief.pdf` was opened with pdfplumber and all 15 pages extracted/read. Rendered rubric pages 10–15 were inspected individually. The supplied project plan and current mathematical implementation were read. Four primary external pages (Berkeley, SciPy, COMSOL, NASA) were opened to check supporting claims. A separately written scalar-series calculation agreed with the implemented baseline reference root to approximately 8.2e-15 s; see `notes/verification_audit.md` for actual values and limits. This note records those performed actions only; it does not assert that all solver results, tests or the final report were checked before their final evidence exists.

Final execution outcomes and any actual bugs belong in the root final verification record and `reports/test_report.html`. If a defect is found, retain its real description and correction here or in a linked verification log. Do not invent an AI mistake to make the reflection sound critical.

## Limits identified during the audit

1. Earlier planning tolerances and parameters are AI proposals, not course rules, material measurements or industrial standards.
2. Analytical agreement verifies the specified mathematical problem; it cannot establish real cooling-process accuracy without empirical data.
3. Responsible disclosure can be written by an assistant; the student's personal understanding and reflection cannot be truthfully supplied by an assistant.
4. The user confirmed topic approval and an extension until midnight at the end of Sunday 25 October 2026 (Melbourne time). The user-supplied GitHub repository exists, currently public, with authenticated administration/push permission confirmed. Final publication is separately verified in the root execution record. Moodle uploads and interview booking cannot be inferred from artifact creation.
5. A newly created repository cannot honestly represent a longer personal development history. Do not backdate commits or fabricate student branch decisions.

## Student reflection to complete after real review

Record a short factual addendum after carrying out the learning/reproduction exercises. State what you personally ran, derived, changed, accepted or rejected; name any actual misconception corrected; explain what you can now defend unaided and what remains uncertain. Important decisions that remain your responsibility include engineering suitability, use of a synthetic property set, acceptance tolerances, interpretation of the results, licence/publishing choices, final wording and submission. These are pending responsibilities, not claimed student decisions.

Do not turn the model explanations in this repository into first-person claims such as “I independently implemented/verified/learned…” unless those actions actually occurred.

## Actual implementation and experiment corrections

- Independent one-step and deliberate-instability tests exposed default snapshots subdividing the requested integration step. The implementation now defaults to initial/final field storage only; explicit interior snapshot events remain documented step-splitting events.
- Anchoring each segment's times to its event start corrected cumulative time-addition drift and prevented spurious microscopic final steps.
- All 64 automated checks passed in the generated test report. A separate agent recomputed acceptance flags, final selection, profile-table errors, stability settings and the independent scalar analytical root.
- The initial fastest baseline candidate (N=20, dt=0.01 s, maximum error 0.993998 C) failed the first larger-span check at 1.180372 C. The failure remains in `results/initial_summary.json`. The documented revision adds a 0.8 C development margin, selects N=20 and dt=0.00625 s, reclassifies the inspected case as development evidence and evaluates a fresh mathematical confirmation without further retuning. Final confirmation maximum error 0.552150 C and crossing error 0.213748% pass the unchanged absolute targets.
- Report/PPTX/figure checks concern numerical/text/layout consistency. They cannot establish the student's personal understanding, and none is claimed.

## Local artifact-completion audit

The final saved XML test report records **64 passing checks**, zero failures/errors/skips. This documentation agent inspected that saved report without rerunning unchanged tests. The technical PDF was counted as **ten total pages: nine main pages and one references page**, and its section progression was checked against the editable report. The generated API HTML contains every symbol in the package's ten-entry `__all__` list. The root task performed report/figure render review. This agent created the six-slide editable presentation, inspected every final PPTX render, generated the static PDF handout from those renders and inspected all six PDF pages after Poppler rendering. PPTX structural/layout/import/native-chart/workbook validation passed; no native PowerPoint application test is claimed.

Real local commits `271decb` and `e8eea09` record the model/tests and later measured evidence/artifacts. The root task subsequently completed full clean-clone reproduction in a fresh pinned environment: 64 checks passed and the checked numerical results matched exactly. The public hosted publication was cloned and all 79 files matched the prepared project. Consult `docs/verification_record.md` and `docs/submission_status.md` for the precise publication, packaging and evidence boundaries. These are AI/tool checks and do not assert student personal review or understanding.

