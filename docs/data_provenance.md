# Data, parameters and source provenance

## Status and intended use

This is a synthetic numerical-method study of one-dimensional cooling. It contains **no measured temperatures, no experimental raw dataset and no identified commercial material**. The engineering output estimates a mathematical threshold under prescribed assumptions. The threshold is an analysis target; it is not a certified handling temperature, process specification or validated manufacturing recommendation.

## Parameter register

| Parameter | Baseline value | Units | Provenance and meaning |
| --- | ---: | --- | --- |
| Full thickness `L` | 0.010 | m | Synthetic illustrative geometry proposed in the project plan. Both faces bound `0 <= x <= L`. |
| Thermal diffusivity `alpha` | 0.000010 | m²/s | Synthetic constant; not a measured/sourced aluminium property. Used directly, without an inconsistent independent `k`, `rho`, `cp` input set. |
| Interior initial temperature `T_i` | 100 | degC | Synthetic uniform interior condition for cooling experiments. |
| Face temperature `T_b` | 20 | degC | Synthetic ideal controlled Dirichlet condition on both faces for `t >= 0`. |
| Analysis target `T_target` | 40 | degC | Synthetic target strictly between `T_b` and `T_i`. |
| Smooth benchmark amplitude | `T_i - T_b` | degC | Exact sine initial condition used for implementation verification; not the uniform-cooling case. |
| Grid, time step and horizon | See `configs/` and result tables | intervals, s, s | Computational study settings, not physical measurements. Actual shortened step durations must be used consistently. |
| Sensitivity factors | 0.5, 1, 2 | dimensionless | Design choices in the plan, applied one physical parameter at a time. |

The factor sweeps imply illustrative `L` values 0.005–0.020 m and `alpha` values 5e-6–2e-5 m²/s. A reported confirmation case may use a different supported thickness, diffusivity or temperature ratio; its exact values must be recorded in the final configuration/table rather than inferred from this register. Mathematical support for arbitrary finite positive properties does not amount to engineering validation across those values.

## Generated evidence

`results/tables/` should retain the actual experiment configurations, analytical-reference checks, temperature errors, cooling-time errors, refinement, timing repeats, performance comparison, stability demonstration, sensitivity and confirmation results. `results/figures/` should be regenerated from the same workflow. Final evidence paths and exact commands are documented in the root `README.md` and technical report.

Files in those directories are computed simulation outputs. Timing values are measurements of the specific execution environment, subject to system load; temperature and crossing values are numerical estimates under the model. Estimated array storage is distinct from measured process memory. Include environment metadata and units with each output.

There is no private or personal dataset to redact. No dataset licence is required for student-designed numerical inputs. Repository code licensing does not transfer ownership of the original university PDFs, which should not be republished without permission. Cite the teaching documents but keep their supplied copies outside the shareable repository.

## Source register

| Source | Role in this project | Scope of reliance |
| --- | --- | --- |
| MMA3001_2026_Project_Brief.pdf, 15 pages, supplied by user | Assessment requirements and all six rubric rows | pp. 1–7 scope and workflow; pp. 8–9 submissions/interview; pp. 10–15 rubric. Original read in full during the project audit. |
| MMA3001 Workshop 11 - slides.pdf and Workshop 12 - slides.pdf, supplied by user | Course connection and project/presentation guidance | Use the plan's page references; any later Moodle directions are unverified. |
| `output/planning/MMA3001_project_plan.md` | User-approved direction for topic, proposed experiments and preliminary tolerances | An AI-generated plan, not official course rules or evidence of topic approval. |
| [Per-Olof Persson, Berkeley finite-difference PDE notes](https://persson.berkeley.edu/math228b/html/finite_difference_methods_for_PDEs.html) | Primary academic context for finite differences, stability and convergence | Algebra for this project is derived in `docs/engineering_derivation.md`. |
| [SciPy `solve_banded` reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_banded.html) | Banded storage and solver API contract | Live documentation may have a different version from the recorded installed environment. Record actual installed versions. |
| [COMSOL finite-slab benchmark](https://doc.comsol.com/6.4/doc/com.comsol.help.models.heat.heat_conduction_in_slab/heat_conduction_in_slab.html) | Example of analytical slab verification and the initial-boundary jump | This project does not reproduce a COMSOL run or adopt its numerical outputs as experimental data. |
| [NASA modelling and simulation FAQ](https://public.ksc.nasa.gov/mns/faq/) | Distinction between verification, validation and intended use | No NASA verification endorsement or experimental validation is implied. |

The four external primary pages above were opened and checked on 24 October 2026. Mathematical formulas in this repository are derived for this problem; copied code, data or results from these pages are not claimed.

