"""Checks of supported inputs, reference functions and reported metrics."""

import numpy as np
import pytest

from heat_project.model import PlateConfig, SolverConfig
from heat_project.solvers import solve
from heat_project.reference import sine_temperature, uniform_temperature, reference_cooling_time
from heat_project.metrics import temperature_errors, threshold_crossing_time


@pytest.mark.parametrize("override", [
    {"length_m": 0.0}, {"length_m": -0.01}, {"length_m": np.inf},
    {"diffusivity_m2_s": 0.0}, {"diffusivity_m2_s": -1e-5},
    {"diffusivity_m2_s": np.nan}, {"initial_temp_c": np.inf},
    {"boundary_temp_c": np.nan}, {"target_temp_c": np.nan},
])
def test_invalid_physical_inputs_rejected(override):
    with pytest.raises((ValueError, TypeError)):
        solve(PlateConfig(**override), SolverConfig(intervals=8, end_time_s=0.01))


@pytest.mark.parametrize("override", [
    {"target_temp_c": 20.0}, {"target_temp_c": 100.0},
    {"target_temp_c": 120.0}, {"boundary_temp_c": 101.0},
])
def test_reference_cooling_time_rejects_unsupported_thresholds(override):
    with pytest.raises(ValueError):
        reference_cooling_time(PlateConfig(**override))


@pytest.mark.parametrize("override", [
    {"intervals": 3}, {"intervals": 8.5}, {"intervals": True},
    {"dt_s": 0.0}, {"dt_s": -0.01}, {"dt_s": np.nan},
    {"end_time_s": 0.0}, {"end_time_s": np.inf},
    {"method": "unknown"}, {"profile": "unknown"},
    {"implementation": "unknown"}, {"amplitude_c": np.nan},
])
def test_invalid_numerical_settings_rejected(override):
    common = dict(intervals=8, dt_s=0.001, end_time_s=0.01)
    common.update(override)
    with pytest.raises((ValueError, TypeError)):
        solve(PlateConfig(), SolverConfig(**common))


def test_ftcs_rejects_unstable_step_but_be_accepts_it():
    settings = dict(intervals=10, dt_s=0.06, end_time_s=0.12)
    # dx=0.001 m makes r=0.6 for the requested full step.
    with pytest.raises(ValueError, match="(?i)(stabil|diffusion|0.5)"):
        solve(PlateConfig(), SolverConfig(**settings, method="ftcs"))
    implicit = solve(PlateConfig(), SolverConfig(**settings, method="backward_euler"))
    assert np.all(np.isfinite(implicit.final_temperature_c))
    assert implicit.diffusion_number == pytest.approx(0.6)


def test_ftcs_stability_limit_is_inclusive():
    result = solve(
        PlateConfig(),
        SolverConfig(intervals=10, dt_s=0.05, end_time_s=0.1),
    )
    assert result.diffusion_number == pytest.approx(0.5)
    assert np.min(result.final_temperature_c) >= 20.0


def test_unstable_diagnostic_is_explicitly_opt_in():
    result = solve(
        PlateConfig(),
        SolverConfig(intervals=10, dt_s=0.06, end_time_s=0.12,
                     allow_unstable=True, perturbation_c=1e-5),
    )
    assert result.diffusion_number > 0.5
    assert np.all(np.isfinite(result.final_temperature_c))


@pytest.mark.parametrize("times", [[-0.1], [0.11], [np.nan]])
def test_invalid_snapshot_times_rejected(times):
    with pytest.raises((ValueError, TypeError)):
        solve(PlateConfig(), SolverConfig(intervals=8, end_time_s=0.1), snapshot_times=times)


def test_reference_sine_has_correct_decay_boundaries_and_initial_shape():
    plate = PlateConfig()
    x = np.array([0.0, 0.0025, 0.005, 0.0075, 0.01])
    initial = sine_temperature(x, 0.0, plate, amplitude_c=60.0)
    np.testing.assert_allclose(initial, 20 + 60 * np.sin(np.pi * x / 0.01), atol=1e-13)
    later = sine_temperature(x, 0.3, plate, amplitude_c=60.0)
    ratio = np.exp(-1e-5 * (np.pi / 0.01) ** 2 * 0.3)
    np.testing.assert_allclose(later[1:-1] - 20, (initial[1:-1] - 20) * ratio, atol=1e-13)
    np.testing.assert_allclose(later[[0, -1]], 20.0, atol=1e-13)


def test_uniform_reference_initial_values_boundaries_and_series_convergence():
    plate = PlateConfig()
    x = np.linspace(0.0, plate.length_m, 21)
    initial = uniform_temperature(x, 0.0, plate, terms=200)
    np.testing.assert_allclose(initial[1:-1], 100.0, atol=1e-12)
    np.testing.assert_allclose(initial[[0, -1]], 20.0, atol=1e-12)
    coarse = uniform_temperature(x, 0.01, plate, terms=100)
    fine = uniform_temperature(x, 0.01, plate, terms=200)
    np.testing.assert_allclose(coarse, fine, atol=1e-11, rtol=0)


def test_reference_cooling_time_hits_target_and_obeys_diffusion_timescale():
    plate = PlateConfig()
    crossing = reference_cooling_time(plate)
    assert crossing > 0
    centre = uniform_temperature(np.array([0.005]), crossing, plate, terms=200)[0]
    assert centre == pytest.approx(40.0, abs=1e-7)
    # For fixed temperature ratio, a doubled thickness quadruples time,
    # and doubled diffusivity halves it. These are independent physics checks.
    assert reference_cooling_time(PlateConfig(length_m=0.02)) == pytest.approx(4 * crossing, rel=1e-9)
    assert reference_cooling_time(PlateConfig(diffusivity_m2_s=2e-5)) == pytest.approx(0.5 * crossing, rel=1e-9)


def test_error_metrics_use_all_entries_in_temperature_units():
    errors = temperature_errors(np.array([20., 23., 24.]), np.array([20., 20., 20.]))
    assert errors["rmse_c"] == pytest.approx(np.sqrt(25 / 3))
    assert errors["max_abs_error_c"] == pytest.approx(4.0)


@pytest.mark.parametrize("values,target,expected", [
    ([100, 60, 20], 60, 1.0),
    ([100, 60, 20], 40, 1.5),
    ([40, 30, 20], 40, 0.0),
    ([30, 25, 20], 40, 0.0),
    ([100, 90, 80], 40, None),
    ([100, 40, 40], 40, 1.0),
])
def test_threshold_crossing_edge_cases(values, target, expected):
    actual = threshold_crossing_time(np.array([0., 1., 2.]), np.array(values, dtype=float), target)
    if expected is None:
        assert actual is None
    else:
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize("times,values", [
    ([0, 1], [100]),
    ([0, 0], [100, 20]),
    ([1, 0], [100, 20]),
    ([0, np.nan], [100, 20]),
    ([0, 1], [100, np.inf]),
])
def test_threshold_crossing_rejects_invalid_histories(times, values):
    with pytest.raises((ValueError, TypeError)):
        threshold_crossing_time(np.array(times, dtype=float), np.array(values, dtype=float), 40.0)

