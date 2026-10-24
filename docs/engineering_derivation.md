# Mathematical derivation and verification limits

This note derives the model used in this project. Symbols use **full slab thickness** `L`; a half-thickness convention would change the factors of four. Numerical results belong in `results/tables/` and the technical report; no measured runtime or computed error is asserted here.

## Engineering model

Consider a homogeneous slab occupying `0 <= x <= L`, with lateral dimensions sufficiently large to neglect lateral temperature gradients. With constant thermal conductivity `k`, density `rho`, heat capacity `cp`, no internal generation and no material movement, a control-volume energy balance gives

\[
\rho c_p T_t = k T_{xx},\qquad
T_t=\alpha T_{xx},\qquad \alpha=\frac{k}{\rho c_p}.
\]

Here `alpha` has units `m²/s`; temperatures and temperature differences use `degC`. Only temperature differences and derivatives enter this constant-property model, so an additive change between Celsius and kelvin does not change the calculation. It would matter in omitted radiative heat transfer.

The faces are prescribed at `T_b` for `t >= 0`. The uniform-cooling interior is initially `T_i > T_b`. At the initial faces the implementation imposes `T_b`, while the interior is `T_i`. This is an intentional initial/boundary incompatibility: a uniform hot slab whose surface temperature drops instantly has a singular initial gradient. The study checks positive-time fields rather than treating a truncated Fourier representation at `t=0` as exact throughout the closed interval. COMSOL's finite-slab example discusses the same issue and a smoothed alternative. [COMSOL finite-slab benchmark](https://doc.comsol.com/6.4/doc/com.comsol.help.models.heat.heat_conduction_in_slab/heat_conduction_in_slab.html).

The boundary condition represents ideal controlled face temperatures. It does not, by itself, represent a plate cooling by convection into air. A convection model would use a heat-transfer coefficient and Robin boundary conditions; it would require different reference equations and empirical validation.

## Finite differences

Let `N` be the number of intervals, `dx = L/N`, `x_i = i dx`, and `h` the actual duration of an individual step. A shortened final step must use its own `h`, not the requested nominal `dt`. Define `r = alpha h/dx²`.

Taylor expansion about `x_i` yields

\[
\frac{T_{i-1}-2T_i+T_{i+1}}{\Delta x^2}
=T_{xx}+\frac{\Delta x^2}{12}T_{xxxx}+O(\Delta x^4).
\]

Combining this with a forward time difference gives FTCS:

\[
T_i^{n+1}=(1-2r)T_i^n+rT_{i-1}^n+rT_{i+1}^n.
\]

All right-hand values must come from the old field. Updating that field in place from left to right changes the scheme. For `0 <= r <= 1/2`, the coefficients are nonnegative and sum to one, supporting a discrete maximum principle under fixed boundary values. The usual smooth-solution global discretisation error is `O(h + dx²)` over a fixed time interval; the initial jump means this smooth estimate should not be blindly applied at arbitrarily small times. These approximation and stability principles are consistent with [Berkeley numerical PDE notes](https://persson.berkeley.edu/math228b/html/finite_difference_methods_for_PDEs.html).

Backward Euler evaluates diffusion at the new time:

\[
-r T_{i-1}^{n+1}+(1+2r)T_i^{n+1}-rT_{i+1}^{n+1}=T_i^n.
\]

For the interior vector `u = (T_1,...,T_(N-1))`, the system is

\[
A u^{n+1}=u^n+r T_b e_1+r T_b e_{N-1},\quad
A=\operatorname{tridiag}(-r,1+2r,-r).
\]

The **positive** boundary terms arise by moving `-r T_b` from the left to the right. For a one-interior-node derivation both boundary contributions would act on the same entry; the supported project grids are larger. When unequal prescribed face values are considered mathematically, replace the first contribution by `r T_left` and the last by `r T_right`. Unequal boundaries are outside this project's supported input contract.

With a tridiagonal system, dense storage and a dense solver are unnecessary. The three rows passed to `scipy.linalg.solve_banded((1,1), ab, rhs)` hold the upper, main and lower diagonals according to `ab[1+i-j,j] = A[i,j]`. The unused band endpoints are zero. See the [SciPy band-storage contract](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_banded.html). Matrix construction and any factorisation must use the actual `r` of the step.

## Stability from a Fourier error mode

For a mode `e_i^n = G^n exp(j i phi)`, substituting into FTCS gives

\[
G_F=1-4r\sin^2(\phi/2).
\]

The grid-independent sufficient condition `|G_F| <= 1` for all modes is `0 <= r <= 1/2`. Near the alternating mode (`phi ≈ pi`), `r=0.6` gives `G_F ≈ -1.4`: perturbations grow and alternate sign. A small perturbation deliberately excites that failure; clipping the bad temperatures would hide it. A particular finite Dirichlet grid has a slightly different extremal mode bound, but the implementation deliberately uses the familiar conservative `r <= 0.5` rule.

Backward Euler gives

\[
G_B=\frac{1}{1+4r\sin^2(\phi/2)}.
\]

For `r >= 0`, `0 < G_B <= 1`; the homogeneous linear problem is unconditionally stable. Large `h` can still produce an inaccurate cooling curve. Stability controls growth of numerical disturbances; it is not an error tolerance or evidence of physical validity.

## Exact smooth verification case

Set `u = T - T_b`. With amplitude `A_0 = T_i - T_b`, use

\[
u(x,t)=A_0\sin(\pi x/L)\exp[-\alpha(\pi/L)^2t].
\]

Differentiating gives `u_t = -alpha(pi/L)² u` and `u_xx = -(pi/L)²u`, hence the heat equation is satisfied. Sine is zero at both faces. At `t=0` the same sine defines the initial condition, so there is no initial boundary jump. This benchmark tests indexing, decay, step duration, boundary handling and error measurement. It is a different initial condition from uniform cooling.

For this single discrete sine mode, the discrete Laplacian eigenvalue is

\[
\lambda_h=-\frac{4\alpha}{\Delta x^2}\sin^2\left(\frac{\pi}{2N}\right).
\]

The exact-in-time **semidiscrete** amplitude is `exp(lambda_h t)`. Comparing to this reference isolates time discretisation at a fixed grid. Comparing the semidiscrete reference to the continuous sine solution isolates spatial discretisation. For multiple steps, FTCS multiplies amplitudes by `prod(1 + h_k lambda_h)`; backward Euler uses `prod(1 - h_k lambda_h)^(-1)`. These provide additional algebraic checks independent of a full field loop.

## Fourier reference for the uniform initial interior

Expand `u(x,0) = DeltaT = T_i - T_b` on `0 < x < L` in sine eigenfunctions. Orthogonality gives

\[
b_n=\frac{2}{L}\int_0^L\Delta T\sin(n\pi x/L)\,dx
=\frac{2\Delta T}{n\pi}[1-(-1)^n].
\]

Even coefficients vanish; odd coefficients are `4 DeltaT/(n pi)`. Thus for `t > 0`,

\[
T(x,t)=T_b+\frac{4\Delta T}{\pi}
\sum_{m=0}^{\infty}\frac{\sin[(2m+1)\pi x/L]}{2m+1}
\exp\left[-\alpha\left(\frac{(2m+1)\pi}{L}\right)^2t\right].
\]

Check the implemented truncated series with both `K` and `2K` modes at every positive comparison time; record the largest difference in `results/tables/`. Agreement only establishes that the chosen truncations agree, so use decay/tail reasoning as well: each omitted term is bounded in magnitude by `4 DeltaT exp[-c(2m+1)²]/[pi(2m+1)]`, `c=alpha pi²t/L²`. This decays rapidly at the chosen positive times. Do not apply the positive-time implementation to `t=0` without defining its separate initial-state convention.

## Centre cooling threshold

For equal cold faces and a uniform initial interior, symmetry and diffusion leave the centre as the hottest point at positive time. An even `N` includes it as a node. At `x=L/2`, `sin[(2m+1)pi/2]=(-1)^m`. Let

\[
\theta_* =\frac{T_{target}-T_b}{T_i-T_b},\quad
\tau=\frac{\alpha t}{L^2}.
\]

The exact reference threshold is the unique positive root of

\[
f(\tau)=\frac{4}{\pi}\sum_{m=0}^{\infty}
\frac{(-1)^m}{2m+1}e^{-(2m+1)^2\pi^2\tau}-\theta_*=0.
\]

The cooling case requires `0 < theta_* < 1`. Use a bracketed scalar root with an initial lower endpoint whose centre temperature remains above the target and an upper time below it. The implementation can safely use `t=0` as the lower endpoint because its reference function returns the prescribed initial state there instead of evaluating a truncated series. Increase the upper bound if needed; check convergence of the series at the positive root and make the scalar-root tolerance much smaller than the solver's threshold tolerance. A first-mode estimate,

\[
t_*\approx\frac{L^2}{\alpha\pi^2}
\log\left[\frac{4}{\pi\theta_*}\right],
\]

is useful for a starting bracket but is not the full-series reference. No numeric root is invented here: use the recorded root in the final experiment output.

Numerical threshold detection uses `max_i T_i^n` and linearly interpolates the first bracketing pair of output states. If `m_n > target >= m_(n+1)`,

\[
t_{cross}=t_n+(t_{n+1}-t_n)
\frac{m_n-T_{target}}{m_n-m_{n+1}}.
\]

This adds interpolation error, which must be checked by time refinement. If the simulated horizon never reaches the target, return a clear not-reached result rather than the end time. With the same `theta_*`, the dimensionless root is unchanged, giving the exact model scaling `t_* proportional to L²/alpha`. Doubling thickness therefore multiplies the model time by four; doubling diffusivity divides it by two. These are analytic scaling predictions, distinct from the measured numerical sensitivity table.

## Metrics, convergence and limits

Temperature maximum error is `max(abs(T_num - T_ref))` in `degC`; nodal RMSE is `sqrt(mean((T_num - T_ref)²))`, also in `degC`. Compare the same locations and times. Crossing relative error is `100 abs(t_num - t_ref)/t_ref` percent. An observed order from a twofold refinement is `p = log(E_coarse/E_fine)/log(2)`, meaningful only when the relevant error dominates and both errors are resolved above roundoff/reference noise.

Holding `r` fixed makes `h` scale as `dx²`: that is coupled refinement, rather than independent evidence of spatial order. Use a controlled small time step or the semidiscrete reference for a spatial study. Use a fixed grid and its semidiscrete solution to isolate temporal order. Physical invariants to check include face values, mirror symmetry, absence of overshoot for stable cooling, and decreasing peak temperature. Full heat content need not be conserved: energy leaves through the prescribed cold faces.

The plan's acceptance targets (`<=1 degC` maximum positive-time benchmark error, `<=2%` threshold error, physical constraints and `<1%` threshold change under refinement) are preliminary-study design targets, not course standards, safety limits or experimental tolerances. The final selection must apply every target and state whether any confirmation case affected it.

Analytical benchmarks and code tests verify the implementation of the chosen mathematical model. They do not measure whether a real plate has constant `alpha`, controlled face temperatures or negligible lateral losses. The NASA modelling guidance distinguishes verification against specifications from validation against the real world for an intended use. No empirical validation is claimed here. [NASA modelling and simulation FAQ](https://public.ksc.nasa.gov/mns/faq/).

