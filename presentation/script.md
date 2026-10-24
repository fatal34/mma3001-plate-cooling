# Five-minute presentation script

This script explains the study. It does not claim personal implementation, learning or unaided review that has not occurred. The student should adapt it only after reviewing the actual project. Sources and detailed timing cues are also embedded in the editable PowerPoint speaker notes.

## Slide 1: Cooling time through a flat plate (0:00–0:40)

This study asks how accurately and efficiently two numerical methods can predict the cooling of an idealised plate. The plate starts at 100 degrees Celsius inside, while both faces remain at 20 degrees. The target is when the hottest point reaches 40 degrees. The full thickness is ten millimetres and diffusivity is an illustrative ten to the minus five square metres per second. The output is a temperature field and a cooling time. These synthetic inputs support a controlled numerical comparison. A real cooling process needs justified properties and boundary data.

## Slide 2: Explicit and implicit finite differences (0:40–1:20)

The governing equation describes heat diffusion in one direction. FTCS calculates every new interior temperature from the previous field. Its diffusion number combines diffusivity, step duration and squared grid spacing. The normal explicit runs enforce a limit of one half. Backward Euler instead uses the new field and solves a tridiagonal linear system. Known face temperatures enter the right-hand side with positive signs. Both methods have first-order time and second-order spatial accuracy for smooth solutions. Implicit stability permits large time steps, but those steps can still introduce unacceptable error.

## Slide 3: Verification against exact solutions (1:20–2:10)

Verification starts with an exact sine solution that satisfies the boundary conditions from the beginning. A separate odd-sine series represents uniform cooling. Its converged centre crossing is 1.649365 seconds. The plotted refinement fixes the time step at ten to the minus five seconds and evaluates the smooth solution at point two seconds. The observed spatial orders approach two. A semidiscrete sine reference isolates temporal error, with observed order near one. Tests also check the tiny implicit system, boundaries, symmetry and input rejection. These checks verify the mathematical implementation. They do not establish measured physical accuracy.

## Slide 4: Method selection from measured evidence (2:10–3:00)

The final selected setting uses twenty intervals and an explicit step of 0.00625 seconds. Its maximum benchmark error is 0.589 degrees, crossing error is 0.229 percent and median solver time is 2.873 milliseconds. The first faster choice failed a transfer case at 1.180 degrees. That failure became development evidence and prompted a stricter point eight degree development margin. The acceptance limit stayed at one degree. A fresh confirmation then reached 0.552 degrees and 0.214 percent crossing error without further tuning. This is selection within the measured candidate set on this machine.

## Slide 5: Thickness and diffusivity sensitivity (3:00–3:40)

The sensitivity follows the heat equation's dimensionless time. Cooling time scales with thickness squared divided by diffusivity when the normalised target stays fixed. Doubling the thickness therefore multiplies the time by four. Doubling diffusivity halves it. The numerical ratios follow those predictions. The main physical limitation is the fixed face temperature. Real convection, contact resistance, lateral loss or changing properties could change the result. Independent measurements would be the next step before using the model for a real thermal process.

## Slide 6: Repository demonstration and AI disclosure (3:40–5:00)

The repository contains reproducible commands, documented solvers, generated HTML, tests and saved evidence. Codex authored substantial code, tests, analysis and report drafts. The student remains responsible for reviewing the material and explaining the reasoning independently. The demonstration now follows one result from the README through the source documentation and test report, then shows the genuine repository history.

## Demonstration after slide 6 narration

Follow `walkthrough_checklist.md`: show the README execution command, then a public solver docstring in the generated HTML, the corresponding update/boundary RHS in source, one meaningful passing test and the actual Git history. Use the real hosted main branch if available. Keep the short command ready and avoid running the entire experiment sweep live.

The recorded numerical choice is a revised development decision. The original faster choice failed a larger-temperature-span case. The stricter 0.8 degC development margin did not relax the original 1 degC acceptance limit. The reused failed case became development evidence, followed by a separate fresh mathematical confirmation.
