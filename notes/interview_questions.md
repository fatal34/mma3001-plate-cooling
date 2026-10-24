# Interview practice: explanations to understand and verify

These are model explanations for study, not a script claiming personal work already completed. Replace references to measured outputs with the actual values in the final `results/tables/` and report when rehearsing. The brief requires unaided answers in the presentation/interview.

1. **What engineering system is represented?** A homogeneous slab with conduction only across its full thickness and both faces held at a colder prescribed temperature. The question is the hottest-point threshold time and its numerical accuracy/cost. Constant properties, no internal source and negligible lateral gradients make it a controlled mathematical case. It is not empirically validated free cooling in air.

2. **What are the primary inputs and outputs?** Geometry `L` in m, diffusivity `alpha` in m²/s, temperatures in degC, intervals `N`, time step/horizon in s, method and initial-profile choice. Outputs include position/time arrays, temperature field with documented axes, first hottest-point threshold crossing or not-reached status, and saved error/performance metrics. Explain actual shapes and validation from the final public API.

3. **Where does diffusivity come from?** `alpha=k/(rho cp)` expresses conductivity divided by volumetric heat capacity and has units m²/s. Here `alpha=1e-5` is an illustrative synthetic input, not a measured alloy value. Real engineering prediction would require justified properties and their temperature range.

4. **Derive FTCS and explain its limit.** Forward time plus central second-space differences gives `T_i^(n+1)=T_i^n+r(T_(i-1)^n-2T_i^n+T_(i+1)^n)`, `r=alpha h/dx²`. Its modal amplification is `1-4r sin²(phi/2)`. Keeping `r<=0.5` avoids growth of all grid modes in the standard condition. Halving spacing quarters the allowed step.

5. **Why does backward Euler use a matrix?** Its spatial derivatives use the unknown new field. Collecting terms gives diagonal `1+2r` and adjacent diagonals `-r`. Known face values move to the RHS as `+rT_b`. A tridiagonal/banded solve avoids a wasteful dense system. Its stable amplification does not remove time-discretisation error.

6. **How do you know the code is implemented correctly?** Show the actual exact-sine error, tiny-system/residual and boundary tests, reference-series convergence, refinement, symmetry/bounds and controlled unstable diagnostic. Each targets a different error. Test agreement alone cannot rule out shared assumptions or prove real-world accuracy. Give actual final test outcomes instead of claiming an unrun check.

7. **Why use two initial conditions?** The smooth sine has an exact solution with compatible boundaries and helps isolate implementation/time-space errors. Uniform hot interior with instant cold faces represents the cooling question but has an initial-boundary jump. Keeping them distinct avoids confusing initial singularity effects with a broken solver.

8. **How is the exact cooling reference calculated?** The constant interior expands into odd sine modes. At the centre their sine values are `(-1)^m`. Solve the converged dimensionless series for the target ratio using a bracketed root. Check mode count convergence at the root and positive comparison times. The one-mode logarithmic estimate is a useful approximation/bracket aid, not the entire reference.

9. **How is the numerical threshold calculated?** Find the first pair whose maximum field values bracket the target, interpolate in time, and return not-reached if no pair exists. Use even `N` so the centre is a node for symmetric cooling. Time/refinement changes quantify crossing and interpolation error. Read the actual returned status/API contract before answering.

10. **What do stable, converged, accurate and validated mean?** Stable means disturbances remain controlled in the mathematical setting. Converged means refinement approaches a limiting/exact model solution. Accurate means error is sufficiently small for a declared metric/tolerance. Physical validation means the model adequately represents independent real behaviour for the intended use. This project gives mathematical verification and consistency evidence, while acknowledging absent empirical validation.

11. **How did you separate spatial and temporal error?** In a smooth sine case the exact semidiscrete decay uses the discrete Laplacian eigenvalue. Comparing time stepping to that solution isolates temporal error; comparing it with the continuous solution isolates spatial error. Alternatively control the other error and demonstrate its insignificance. A fixed `r` couples `h` to `dx²` and by itself is combined refinement.

12. **How was the method selected?** Explain the declared maximum temperature-error, threshold-error, physical and further-refinement limits; show the eligible candidate table and actual fastest measured eligible setting. Quote measured runtime/error and confirmation results from the final table. State that this is selection within a tested set on one environment, not a universal solver ranking.

13. **What optimisation improved the code?** Loop and vectorised FTCS implement the same numerical update; compare actual output agreement and repeated solver timings. Explain why NumPy avoids per-element interpreter overhead and why total runtime still grows with nodes and steps. State the actual measured speedup and timing spread, rather than promising a generic improvement.

14. **What are the runtime and memory trends?** For `N` intervals and `M` steps, FTCS and tridiagonal BE require order `NM` arithmetic; step state and banded matrix are order `N`. Retaining all fields costs order `NM` storage. With explicit stable steps at a fixed horizon, `M` grows like `N²`, so total work can grow like `N³`. Stored-array bytes differ from peak process memory. Use actual output settings when describing measured storage.

15. **Which physical parameters matter most?** For identical normalised temperatures, the exact model time scales as `L²/alpha`; doubling thickness multiplies time by four and doubling diffusivity halves it. Show the actual sensitivity ratios and acknowledge fixed-face assumptions. Boundary heat-transfer behaviour could dominate a real plate but was not measured here.

16. **What could fail?** Unstable explicit steps, incorrect implicit boundary signs, in-place old-state updates, mishandled final steps, unsupported/non-finite inputs, unconverged early-time Fourier sums, an unbracketed threshold or misleading performance comparisons. Explain the relevant actual safeguards/tests and at least one remaining physical limitation.

17. **What did AI do?** AI substantially authored code, tests, analysis, documentation and report under the user's full-project instruction. Identify your own actual review/reproduction, derivations and decisions separately. Disclose what you have not independently checked. Do not claim independent implementation or personal learning that has not occurred.

18. **What would you do next?** First strengthen model validation with justified properties, realistic face boundary data and independent temperature measurements. A convection-boundary extension or higher-order time method is useful only when its engineering purpose, numerical reference and accuracy/robustness tests are clear. Adding complexity alone is not evidence of improvement.

