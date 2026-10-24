# Personal review and learning guide

This guide helps the student review the AI-assisted project before submission and the individual interview. It is not a record that these activities have already been completed. Work through the explanations without AI, check the actual repository outputs, and record what you personally did in `notes/ai_use_log.md`.

## 1. Explain the engineering problem in ordinary language

Describe a flat slab initially hot inside, with both faces suddenly held at a colder specified temperature. Heat diffuses through the thickness. The desired outputs are the temperature field and when its hottest point drops below a selected target. The project compares numerical methods for that mathematical calculation and chooses a configuration using accuracy/cost evidence.

Explain why a hot component's conduction timescale matters, and why the present result is a preliminary controlled-boundary comparison. The faces are **held** at `T_b`; ordinary cooling into room air would require a different convection boundary model. The parameters are synthetic; there is no measured real plate here. Show the full thickness `L` on a sketch and identify the centre `L/2`.

Check yourself: Can you give the units and meaning of every baseline parameter without reading a script? Why is “cooling to 40 degC” an analysis threshold rather than a demonstrated safe-handling rule?

## 2. Re-derive the two updates on paper

Starting with `T_t = alpha T_xx`, replace time and space derivatives with finite differences. Obtain

`new_i = old_i + r(old_(i-1) - 2 old_i + old_(i+1))`, where `r = alpha h/dx²`.

Explain why the old array must remain unchanged until every interior update is formed. Then move the new-time terms of backward Euler into a tridiagonal matrix. On a tiny grid, write its rows and move both face terms to the RHS with **positive** signs. Explain what changes when the final step duration is shorter.

Check yourself: Why does halving `dx` require quartering the maximum stable explicit `dt`? Can you explain where each of the three diagonals is stored in the banded array? Read the corresponding source and compare it with your paper derivation.

## 3. Understand stability, accuracy and physical validity separately

Derive or follow the Fourier-mode factor `1 - 4r sin²(phi/2)`. The alternating grid mode grows for `r=0.6`; a visibly smooth initial field may not immediately reveal that. Backward Euler's factor is `1/(1+4r sin²(phi/2))`, so it damps these modes for any positive step. Large steps still change the cooling curve inaccurately.

A converged numerical solution can solve an unrealistic boundary model extremely accurately. Analytical agreement supports correct implementation; empirical physical validation requires independent real-world evidence appropriate to the intended use. This project provides the former and physical consistency checks, without claiming the latter.

Check yourself: Can you name one stable-but-inaccurate run, one unsupported physical assumption, and one test that would detect a specific implementation bug? Use actual final outputs where relevant.

## 4. Check the analytical references independently

Differentiate the sine solution in `docs/engineering_derivation.md` and verify both the PDE and boundary conditions. Recompute the constant initial profile's sine coefficients using the integral given there. Explain why only odd modes remain and why the centre series alternates in sign.

Open the saved reference-convergence evidence. Identify the actual positive comparison times, mode counts, maximum `K` vs `2K` difference, scalar-root tolerance and reference cooling time. Do not merely repeat a reference number without understanding how it was found. Explain why comparing a truncated series to the discontinuous initial state at `t=0` is a weak numerical check.

## 5. Reproduce representative evidence

Use the **exact commands in the final README**, in a fresh environment or clean project copy. Run the automated tests; open the generated test report; run a short supported cooling example and inspect its output. Regenerate the core tables/figures if time permits. Record your own actual command outcomes and any deviations rather than claiming the assistant's prior runs as your work.

Pick three meaningful tests from `tests/` and explain which fault each would detect. At minimum inspect the tiny implicit system, fixed boundaries/shortened step, and exact-sine/refinement test. Explain what a passing test does not establish.

## 6. Follow a result from input to conclusion

Choose the selected configuration in the final summary/table. Locate its method, `N`, `dt`, actual diffusion number, temperature maximum error, crossing time, crossing error, refinement change, physical checks and median runtime. Compare those values with the declared limits. Follow one plotted point back to its saved table row.

Explain why the selected run was preferred and what happens if the tolerance or machine changes. A ranking among a small measured candidate set is not a proof of a universal optimal method. Timings depend on environment; input/output and plotting must not be mixed into solver timing without disclosure.

Check yourself: Which method actually won? Which plausible method/setting lost, and why? What numerical limitation remains even in the winning case? Answers must come from the final measured outputs, not from assumptions in this guide.

## 7. Explain engineering sensitivity

Use `tau = alpha t/L²`. For the same normalised temperature target, the dimensionless crossing is fixed, so `t` scales as `L²/alpha`. Predict the effect of doubled thickness and diffusivity before opening the sensitivity plot. Then compare the actual numerical ratios with those predictions and explain any small numerical differences.

Ask what the simulation has omitted: finite convection resistance, lateral heat loss, temperature-dependent properties, contact resistance, internal heating or phase change. Do not add these features without rederiving boundary/reference models and obtaining appropriate data.

## 8. Write the personal reflection after doing the work

Be precise about substantial AI contribution. State what you personally reviewed/reproduced and which decisions you now endorse. Identify any actual misunderstanding or defect you found; if none was found, state the limitations you checked rather than inventing an error. Explain how AI accelerated drafting and how you prevented fluent explanations from becoming unchecked claims.

For the interview, rehearse a five-minute explanation followed by three minutes of unaided questions. Open the README, source docstring, generated HTML, test report and key results locally. Keep the full experiment sweep out of the live demo if it would consume the allotted time.

