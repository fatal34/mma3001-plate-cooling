"""Independent numerical checks for the one-dimensional cooling solvers.

The smooth sine solution avoids the discontinuity at the faces of the uniform
initial condition.  The tiny backward-Euler check is hand-solved rather than
using the production linear-system solver as its own oracle.
"""

import numpy as np
import pytest

from heat_project.model import PlateConfig, SolverConfig
from heat_project.solvers import solve
from heat_project.reference import sine_temperature, uniform_temperature


@pytest.mark.parametrize("method", ["ftcs", "backward_euler"])
def test_smooth_sine_matches_independent_closed_form(method):
    plate = PlateConfig()
    settings = SolverConfig(
        intervals=40, dt_s=0.001, end_time_s=0.1, method=method, profile="sine"
    )
    result = solve(plate, settings)
    reference = 20.0 + 80.0 * np.sin(np.pi * result.x_m / 0.01) * np.exp(
        -1e-5 * (np.pi / 0.01) ** 2 * 0.1
    )
    assert np.max(np.abs(result.final_temperature_c - reference)) < 0.009


def test_backward_euler_one_step_has_hand_solved_values_and_small_residual():
    plate = PlateConfig()
    # N=4, dx=0.0025 m, dt=0.15625 s gives r=1/4. The three
    # absolute-temperature equations have RHS (105, 100, 105).
    result = solve(
        plate,
        SolverConfig(intervals=4, dt_s=0.15625, end_time_s=0.15625,
                     method="backward_euler", profile="uniform"),
    )
    expected = np.array([20.0, 1460 / 17, 1620 / 17, 1460 / 17, 20.0])
    np.testing.assert_allclose(result.final_temperature_c, expected, atol=2e-13, rtol=0)
    interior = result.final_temperature_c[1:-1]
    matrix = np.array([[1.5, -0.25, 0.0], [-0.25, 1.5, -0.25], [0.0, -0.25, 1.5]])
    np.testing.assert_allclose(matrix @ interior, [105, 100, 105], atol=2e-13, rtol=0)


@pytest.mark.parametrize("method", ["ftcs", "backward_euler"])
def test_equilibrium_sine_profile_stays_at_boundary_temperature(method):
    result = solve(
        PlateConfig(),
        SolverConfig(intervals=10, dt_s=0.003, end_time_s=0.025,
                     method=method, profile="sine", amplitude_c=0.0),
        snapshot_times=[0.0, 0.013, 0.025],
    )
    np.testing.assert_allclose(result.temperature_snapshots_c, 20.0, atol=1e-12, rtol=0)
    np.testing.assert_allclose(result.final_temperature_c, 20.0, atol=1e-12, rtol=0)


@pytest.mark.parametrize("method", ["ftcs", "backward_euler"])
def test_uniform_cooling_is_bounded_symmetric_and_monotone_at_hottest_point(method):
    result = solve(
        PlateConfig(),
        SolverConfig(intervals=20, dt_s=0.005, end_time_s=0.2,
                     method=method, profile="uniform"),
        snapshot_times=[0.0, 0.05, 0.1, 0.2],
    )
    fields = result.temperature_snapshots_c
    assert np.min(fields) >= 20.0 - 1e-11
    assert np.max(fields) <= 100.0 + 1e-11
    np.testing.assert_allclose(fields, fields[:, ::-1], atol=1e-11, rtol=0)
    assert np.max(np.diff(result.max_temperature_c)) <= 1e-11
    np.testing.assert_allclose(fields[:, [0, -1]], 20.0, atol=1e-12, rtol=0)


@pytest.mark.parametrize("method", ["ftcs", "backward_euler"])
def test_shortened_final_step_and_requested_snapshot_times_are_exact(method):
    requested = np.array([0.0, 0.0043, 0.0121, 0.0207])
    result = solve(
        PlateConfig(),
        SolverConfig(intervals=8, dt_s=0.003, end_time_s=0.0207,
                     method=method, profile="sine"),
        snapshot_times=requested,
    )
    assert result.times_s[0] == 0.0
    assert result.times_s[-1] == 0.0207
    assert np.all(np.diff(result.times_s) > 0)
    assert np.max(np.diff(result.times_s)) <= 0.003 + 1e-15
    np.testing.assert_allclose(result.snapshot_times_s, requested, atol=1e-15, rtol=0)
    assert result.temperature_snapshots_c.shape == (4, 9)
    np.testing.assert_allclose(result.temperature_snapshots_c[-1], result.final_temperature_c)
    np.testing.assert_allclose(result.temperature_snapshots_c[:, [0, -1]], 20.0)


def test_single_ftcs_step_uses_previous_values_simultaneously():
    plate = PlateConfig()
    result = solve(
        plate,
        SolverConfig(intervals=4, dt_s=0.15625, end_time_s=0.15625,
                     method="ftcs", profile="uniform"),
    )
    np.testing.assert_allclose(result.final_temperature_c, [20, 80, 100, 80, 20], atol=1e-13)


@pytest.mark.parametrize("method", ["ftcs", "backward_euler"])
def test_each_shortened_step_uses_its_actual_duration(method):
    intervals = 4
    result = solve(
        PlateConfig(),
        SolverConfig(intervals=intervals, dt_s=0.1, end_time_s=0.15,
                     method=method, profile="sine"),
        snapshot_times=[0.0, 0.037, 0.15],
    )
    # The sampled sine is an exact eigenvector of the discrete second
    # difference. This checks time-step algebra independently of truncation error.
    discrete_rate = 4 * 1e-5 / (0.01 / intervals) ** 2 * np.sin(np.pi / (2 * intervals)) ** 2
    durations = np.diff(result.times_s)
    if method == "ftcs":
        decay = np.prod(1.0 - discrete_rate * durations)
    else:
        decay = np.prod(1.0 / (1.0 + discrete_rate * durations))
    expected = 20.0 + 80.0 * np.sin(np.pi * result.x_m / 0.01) * decay
    np.testing.assert_allclose(result.final_temperature_c, expected, atol=2e-12, rtol=0)


def test_ftcs_loop_and_vectorized_paths_have_same_solution():
    plate = PlateConfig()
    common = dict(intervals=24, dt_s=0.003, end_time_s=0.037, profile="uniform")
    loop = solve(plate, SolverConfig(**common, implementation="loop"),
                 snapshot_times=[0.0, 0.017, 0.037])
    vectorized = solve(plate, SolverConfig(**common, implementation="vectorized"),
                       snapshot_times=[0.0, 0.017, 0.037])
    np.testing.assert_allclose(loop.final_temperature_c, vectorized.final_temperature_c,
                               atol=1e-12, rtol=0)
    np.testing.assert_allclose(loop.max_temperature_c, vectorized.max_temperature_c,
                               atol=1e-12, rtol=0)
    np.testing.assert_allclose(loop.temperature_snapshots_c, vectorized.temperature_snapshots_c,
                               atol=1e-12, rtol=0)


@pytest.mark.parametrize("method", ["ftcs", "backward_euler"])
def test_spatial_refinement_reduces_smooth_error(method):
    errors = []
    for intervals in [10, 20, 40]:
        # A very small fixed dt leaves the spatial error dominant for both schemes.
        settings = SolverConfig(intervals=intervals, dt_s=1e-5, end_time_s=0.05,
                                method=method, profile="sine")
        result = solve(PlateConfig(), settings, snapshot_times=[])
        exact = sine_temperature(result.x_m, 0.05, PlateConfig(), amplitude_c=80.0)
        errors.append(np.max(np.abs(result.final_temperature_c - exact)))
    assert errors[1] < errors[0] / 3
    assert errors[2] < errors[1] / 3


def test_backward_euler_time_refinement_reduces_smooth_error():
    errors = []
    for step in [0.02, 0.01, 0.005]:
        result = solve(
            PlateConfig(),
            SolverConfig(intervals=200, dt_s=step, end_time_s=0.2,
                         method="backward_euler", profile="sine"),
            snapshot_times=[],
        )
        exact = sine_temperature(result.x_m, 0.2, PlateConfig())
        errors.append(np.max(np.abs(result.final_temperature_c - exact)))
    assert errors[1] < errors[0] * 0.55
    assert errors[2] < errors[1] * 0.55


def test_ftcs_time_refinement_is_first_order_against_discrete_eigenmode():
    intervals = 40
    dx = 0.01 / intervals
    discrete_rate = 4 * 1e-5 / dx**2 * np.sin(np.pi / (2 * intervals)) ** 2
    errors = []
    for step in [0.0025, 0.00125, 0.000625]:
        result = solve(
            PlateConfig(),
            SolverConfig(intervals=intervals, dt_s=step, end_time_s=0.2,
                         method="ftcs", profile="sine"),
            snapshot_times=[],
        )
        # The discrete eigenmode removes spatial error and its possible
        # cancellation with FTCS temporal error from this time-order check.
        exact_in_time = 20 + 80 * np.sin(np.pi * result.x_m / 0.01) * np.exp(-discrete_rate * 0.2)
        errors.append(np.max(np.abs(result.final_temperature_c - exact_in_time)))
    assert 0.45 < errors[1] / errors[0] < 0.55
    assert 0.45 < errors[2] / errors[1] < 0.55


def test_uniform_solution_agrees_with_converged_fourier_reference():
    result = solve(
        PlateConfig(),
        SolverConfig(intervals=80, dt_s=0.0005, end_time_s=0.5, method="ftcs"),
    )
    reference = uniform_temperature(result.x_m, 0.5, PlateConfig(), terms=200)
    assert np.max(np.abs(result.final_temperature_c - reference)) < 0.02

