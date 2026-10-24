# Five-minute demonstration checklist

These are preparation instructions. They do not claim the student has rehearsed, uploaded slides or attended the interview.

## Before the appointment

- Confirm the booked appointment and current Moodle directions. The supplied workshops say slides, if used, should be uploaded at least 24 hours before the appointment.
- Read the report and `notes/learning_guide.md`. Explain the model, boundary conditions, stability, references, selection and limitations unaided.
- Add a truthful personal AI reflection after reviewing/reproducing the project. Codex's substantial authorship must remain disclosed.
- Open the final presentation, README, generated HTML documentation, test report and results locally.
- Open [the hosted repository](https://github.com/fatal34/mma3001-plate-cooling), confirm its final `main` branch and assessor access, and keep it ready for the demonstration.
- Keep a local copy of the report and evidence in case internet access fails.
- Use the exact short example/test commands in the final README. A full experiment sweep is unnecessary during a five-minute demonstration.

## Timing

| Elapsed time | Material | Purpose |
| --- | --- | --- |
| 0:00–0:40 | Slide 1 | Define engineering problem, synthetic inputs and outputs. |
| 0:40–1:20 | Slide 2 | Explain FTCS/BE and fixed-temperature assumptions. |
| 1:20–2:10 | Slide 3 | Show exact references, convergence and a meaningful check. |
| 2:10–3:00 | Slide 4 | Explain measured selection and optimisation. |
| 3:00–3:40 | Slide 5 | Interpret thickness/diffusivity scaling and physical limits. |
| 3:40–5:00 | Slide 6 plus repository | Demonstrate code/docs/tests/history and disclose AI contribution. |

Aim to finish spoken slide narration before the full five minutes. Practice transitions into the repository so switching windows does not consume the last minute.

## Repository walkthrough within the last 80 seconds

1. **About 15 seconds:** show the README purpose, setup and one reproducible execution command. Identify the configurations, source, results, tests and report directories.
2. **About 20 seconds:** open a solver docstring in the generated HTML, then show the actual source line for FTCS or the implicit boundary RHS. Explain intent rather than reading every line.
3. **About 15 seconds:** show the final test report and explain one test's failure target, such as boundary RHS signs or a shortened final step.
4. **About 10 seconds:** show the hosted `main` branch and publication history. The original AI-attributed local development checkpoints are also preserved in `notes/development_history.bundle`; describe only real work and commits.
5. **About 20 seconds:** close with the measured selected setting, one physical-model limitation and the substantial AI disclosure. Explain what you personally reviewed without claiming unaudited work.

## Three-minute question preparation

Review `notes/interview_questions.md`. Be ready to derive the updates, distinguish stability/accuracy/physical validity, explain the odd sine series, justify the selected candidate from real values, and describe actual AI checks. Pause and reason through an unfamiliar question. Do not rely on AI to answer during the interview.

