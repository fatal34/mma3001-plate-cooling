"""Reproduce the declared numerical experiments and save raw evidence.

Run from the repository root: ``python scripts/run_experiments.py``.
Acceptance tolerances and candidate grids are read before any result is
observed. Timings exclude references, plots and disk I/O and are machine
dependent. All retained experimental parameters are synthetic.
"""
from __future__ import annotations

import argparse
import cProfile
import csv
from dataclasses import asdict, replace
from datetime import datetime, timezone
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import pstats
import subprocess
import sys
from time import perf_counter

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from heat_project.model import PlateConfig, SolverConfig
from heat_project.solvers import solve
from heat_project.reference import (sine_temperature, uniform_temperature,
                                    reference_cooling_time)
from heat_project.metrics import temperature_errors, threshold_crossing_time


def write_csv(path: Path, rows: list[dict]) -> None:
    """Write numeric evidence with explicit headers, including empty values."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def timed_solver(plate: PlateConfig, settings: SolverConfig,
                 repeats: int) -> dict[str, float | int]:
    """Warm up, then time comparable solves in batches exceeding timer noise."""
    start = perf_counter()
    solve(plate, settings, snapshot_times=[])
    pilot = max(perf_counter() - start, 1e-6)
    batch = max(1, min(20, math.ceil(0.04 / pilot)))
    samples = []
    for _ in range(repeats):
        start = perf_counter()
        for _ in range(batch):
            solve(plate, settings, snapshot_times=[])
        samples.append((perf_counter() - start) / batch)
    return {'median_runtime_s': float(np.median(samples)),
            'min_runtime_s': min(samples), 'max_runtime_s': max(samples),
            'timing_repeats': repeats, 'timing_batch_size': batch}


def evaluate(plate: PlateConfig, settings: SolverConfig,
             times: list[float], reference_time: float) -> tuple[dict, object]:
    """Evaluate fixed positive-time fields, crossing time and sampled bounds."""
    result = solve(plate, settings, snapshot_times=times)
    reference = np.stack([uniform_temperature(result.x_m, t, plate) for t in times])
    error = temperature_errors(result.temperature_snapshots_c, reference)
    crossing = threshold_crossing_time(result.times_s, result.max_temperature_c,
                                        plate.target_temp_c)
    if crossing is None:
        raise RuntimeError('candidate horizon did not reach the declared target')
    bounded = bool(np.min(result.temperature_snapshots_c) >= plate.boundary_temp_c-1e-9
                   and np.max(result.max_temperature_c) <= plate.initial_temp_c+1e-9
                   and np.all(np.diff(result.max_temperature_c) <= 1e-9))
    arrays = [result.x_m, result.times_s, result.max_temperature_c,
              result.temperature_snapshots_c, result.snapshot_times_s,
              result.final_temperature_c]
    return {**error, 'threshold_time_s': crossing,
            'threshold_error_pct': 100*abs(crossing-reference_time)/reference_time,
            'steps': result.steps, 'actual_r': result.diffusion_number,
            'within_bounds': bounded,
            'retained_array_bytes': sum(array.nbytes for array in arrays)}, result


def main() -> None:
    """Execute E1-E6, select from development evidence, then confirm once."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT/'results')
    parser.add_argument('--timing-repeats', type=int, default=None)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    tables = out/'tables'
    tables.mkdir(parents=True, exist_ok=True)
    baseline = json.loads((ROOT/'configs/baseline.json').read_text())
    study = json.loads((ROOT/'configs/study.json').read_text())
    plate = PlateConfig(**baseline['plate'])
    baseline_settings = SolverConfig(**baseline['solver'])
    reference_time = reference_cooling_time(plate)
    times = study['benchmark_times_s']
    criteria = study['selection']
    repeats = args.timing_repeats or study['timing_repeats']
    if repeats < 1:
        raise ValueError('timing repeats must be positive')

    print('E1/E2: analytical checks and baseline', flush=True)
    smooth_rows, reference_rows = [], []
    for method in ['ftcs', 'backward_euler']:
        for time in [0.1, 0.5, 1.0]:
            setting = replace(baseline_settings, method=method, profile='sine', end_time_s=time)
            result = solve(plate, setting, [])
            error = temperature_errors(result.final_temperature_c,
                                       sine_temperature(result.x_m, time, plate))
            smooth_rows.append({'method': method, 'time_s': time,
                                'intervals': setting.intervals, 'dt_s': setting.dt_s, **error})
    for time in times:
        x = np.linspace(0, plate.length_m, 161)
        a, b = uniform_temperature(x, time, plate, terms=20), uniform_temperature(x, time, plate, terms=40)
        reference_rows.append({'time_s': time, 'starting_terms_a': 20,
                               'starting_terms_b': 40,
                               'max_difference_c': float(np.max(abs(a-b))),
                               'adaptive_tail_bound_c': 1e-11})
    write_csv(tables/'smooth_verification.csv', smooth_rows)
    write_csv(tables/'reference_convergence.csv', reference_rows)
    base_metrics, _ = evaluate(plate, baseline_settings, times, reference_time)
    base_timing = timed_solver(plate, baseline_settings, repeats)

    print('E3: separate spatial and temporal refinement', flush=True)
    spatial, temporal = [], []
    for method in ['ftcs', 'backward_euler']:
        previous_error = None
        for n in [10, 20, 40, 80]:
            dt, end = 1e-5, 0.2
            setting = SolverConfig(intervals=n, dt_s=dt, end_time_s=end,
                                   method=method, profile='sine')
            result = solve(plate, setting, [])
            exact = sine_temperature(result.x_m, end, plate)
            errors = temperature_errors(result.final_temperature_c, exact)
            halved = solve(plate, replace(setting, dt_s=dt/2), [])
            time_effect = float(np.max(abs(halved.final_temperature_c-result.final_temperature_c)))
            order = '' if previous_error is None else math.log2(previous_error/errors['max_abs_error_c'])
            spatial.append({'method': method, 'intervals': n, 'dt_s': dt, **errors,
                            'observed_order': order, 'time_halving_change_c': time_effect,
                            'reference': 'continuous analytical sine'})
            previous_error = errors['max_abs_error_c']
        previous_error = None
        n, end = 80, 0.5
        dx = plate.length_m/n
        eigenvalue = -4*plate.diffusivity_m2_s/dx**2*np.sin(np.pi/(2*n))**2
        for dt in [0.0004, 0.0002, 0.0001, 0.00005]:
            setting = SolverConfig(intervals=n, dt_s=dt, end_time_s=end,
                                   method=method, profile='sine')
            result = solve(plate, setting, [])
            # Exact solution of the spatially discretised ODE isolates time error.
            exact = plate.boundary_temp_c + 80*np.sin(np.pi*result.x_m/plate.length_m)*np.exp(eigenvalue*end)
            exact[[0, -1]] = plate.boundary_temp_c
            errors = temperature_errors(result.final_temperature_c, exact)
            order = '' if previous_error is None else math.log2(previous_error/errors['max_abs_error_c'])
            temporal.append({'method': method, 'intervals': n, 'dt_s': dt, **errors,
                             'observed_order': order, 'reference': 'exact semi-discrete sine mode'})
            previous_error = errors['max_abs_error_c']
    write_csv(tables/'spatial_convergence.csv', spatial)
    write_csv(tables/'temporal_convergence.csv', temporal)

    print('E5: candidate accuracy and comparable solver timings', flush=True)
    candidates, seen = [], set()
    alignment = min(times)
    for method, diffusion_numbers in [('ftcs', study['ftcs_diffusion_numbers']),
                                       ('backward_euler', study['backward_euler_diffusion_numbers'])]:
        for n in study['candidate_intervals']:
            for requested_r in diffusion_numbers:
                raw_dt = requested_r*(plate.length_m/n)**2/plate.diffusivity_m2_s
                # All benchmark events lie on the same integration schedule as
                # timed runs. Cap dt at 0.1s and round down to divide that interval.
                divisions = max(1, math.ceil(alignment/raw_dt-1e-12))
                dt = alignment/divisions
                key = (method, n, dt)
                if key in seen:
                    continue
                seen.add(key)
                setting = SolverConfig(intervals=n, dt_s=dt, end_time_s=3, method=method)
                measures, result = evaluate(plate, setting, times, reference_time)
                finer = solve(plate, replace(setting, intervals=2*n, dt_s=dt/4), [])
                fine_cross = threshold_crossing_time(finer.times_s, finer.max_temperature_c, plate.target_temp_c)
                refine_pct = 100*abs(fine_cross-measures['threshold_time_s'])/fine_cross
                timing = timed_solver(plate, setting, repeats)
                eligible = bool(measures['max_abs_error_c'] <= criteria['max_temperature_error_c']
                                 and measures['threshold_error_pct'] <= 100*criteria['max_threshold_relative_error']
                                 and refine_pct < 100*criteria['max_refinement_relative_change']
                                 and measures['within_bounds'])
                row = {'method': method, 'intervals': n, 'requested_r': requested_r,
                       'dt_s': dt, **measures, **timing,
                       'refinement_change_pct': refine_pct, 'eligible': eligible}
                candidates.append(row)
                print(f"  {method:14} N={n:3} dt={dt:.6g} error={measures['max_abs_error_c']:.4g} C eligible={eligible}", flush=True)
    write_csv(tables/'candidate_comparison.csv', candidates)
    eligible = [row for row in candidates if row['eligible']]
    if not eligible:
        raise RuntimeError('no candidate meets predeclared criteria; report failure rather than retune silently')
    selected = min(eligible, key=lambda row: row['median_runtime_s'])
    method_best = {method: min((row for row in eligible if row['method']==method),
                               key=lambda row: row['median_runtime_s'])
                   for method in ['ftcs', 'backward_euler']}
    selected_settings = SolverConfig(intervals=selected['intervals'], dt_s=selected['dt_s'],
                                    end_time_s=3, method=selected['method'])
    # Persist the frozen choice before any independent confirmation result exists.
    (out/'selection_frozen.json').write_text(json.dumps({'selected': selected,
                                                       'criteria': criteria}, indent=2)+'\n')

    profiles, histories = [], []
    for method, row in method_best.items():
        setting = SolverConfig(intervals=row['intervals'], dt_s=row['dt_s'], end_time_s=3, method=method)
        metrics, result = evaluate(plate, setting, times, reference_time)
        for t, field in zip(result.snapshot_times_s, result.temperature_snapshots_c):
            exact = uniform_temperature(result.x_m, float(t), plate)
            for x, numerical, analytical in zip(result.x_m, field, exact):
                profiles.append({'method': method, 'time_s': float(t), 'x_m': float(x),
                                  'temperature_c': float(numerical), 'reference_c': float(analytical)})
        # Save all solver samples. Analytical centre values are inexpensive here.
        analytical_history = [float(uniform_temperature(plate.length_m/2, float(t), plate)) for t in result.times_s]
        for t, value, reference in zip(result.times_s, result.max_temperature_c, analytical_history):
            histories.append({'method': method, 'time_s': float(t), 'max_temperature_c': float(value),
                               'reference_c': reference, 'target_c': plate.target_temp_c})
    write_csv(tables/'profiles.csv', profiles)
    write_csv(tables/'cooling_history.csv', histories)

    print('E4: controlled unstable high-frequency mode', flush=True)
    stability = []
    for r in [0.4, 0.6]:
        n, steps = 40, 120
        dt = r*(plate.length_m/n)**2/plate.diffusivity_m2_s
        setting = SolverConfig(intervals=n, dt_s=dt, end_time_s=steps*dt,
                               method='ftcs', profile='sine', allow_unstable=True,
                               perturbation_c=1e-8)
        requested = np.arange(steps+1)*dt
        requested[-1] = setting.end_time_s
        result = solve(plate, setting, requested)
        for t, field in zip(result.snapshot_times_s, result.temperature_snapshots_c):
            error = temperature_errors(field, sine_temperature(result.x_m, float(t), plate))
            stability.append({'requested_r': r, 'time_s': float(t), **error,
                              'actual_max_r': result.diffusion_number})
    write_csv(tables/'stability.csv', stability)

    print('E6: dimensionally consistent engineering sensitivity', flush=True)
    sensitivity = []
    for parameter in ['length_m', 'diffusivity_m2_s']:
        for multiplier in study['sensitivity_multipliers']:
            changed = replace(plate, **{parameter: getattr(plate, parameter)*multiplier})
            scale = (changed.length_m**2/changed.diffusivity_m2_s)/(plate.length_m**2/plate.diffusivity_m2_s)
            result = solve(changed, replace(selected_settings, dt_s=selected_settings.dt_s*scale,
                                            end_time_s=3*scale), [])
            exact_time = reference_cooling_time(changed)
            numerical_time = threshold_crossing_time(result.times_s, result.max_temperature_c, changed.target_temp_c)
            sensitivity.append({'parameter': parameter, 'multiplier': multiplier,
                                 'length_m': changed.length_m, 'diffusivity_m2_s': changed.diffusivity_m2_s,
                                 'reference_time_s': exact_time, 'numerical_time_s': numerical_time,
                                 'relative_error_pct': 100*abs(numerical_time-exact_time)/exact_time})
    write_csv(tables/'sensitivity.csv', sensitivity)

    print('Implementation optimisation and profiling', flush=True)
    optimisation = []
    opt_setting = SolverConfig(intervals=160, dt_s=0.4*(plate.length_m/160)**2/plate.diffusivity_m2_s,
                               end_time_s=0.1, method='ftcs')
    opt_reference = solve(plate, opt_setting, []).final_temperature_c
    for implementation in ['loop', 'vectorized']:
        setting = replace(opt_setting, implementation=implementation)
        result = solve(plate, setting, [])
        timing = timed_solver(plate, setting, max(repeats, 5))
        optimisation.append({'implementation': implementation, **timing,
                              'steps': result.steps, 'intervals': setting.intervals,
                              'output_max_difference_c': float(np.max(abs(result.final_temperature_c-opt_reference)))})
    write_csv(tables/'optimisation.csv', optimisation)
    # Reproduction into a separate directory must preserve the submitted
    # profile alongside the original numerical and timing evidence.
    profile_directory = ROOT/'reports' if out == (ROOT/'results').resolve() else out
    profile_directory.mkdir(parents=True, exist_ok=True)
    profiler = cProfile.Profile()
    profiler.runcall(solve, plate, replace(opt_setting, implementation='loop'), [])
    with (profile_directory/'profile.txt').open('w') as stream:
        pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats('cumulative').print_stats(20)

    print('Final confirmation: frozen N and Fourier-number setting', flush=True)
    confirmation_plate = PlateConfig(**study['confirmation'])
    scale = (confirmation_plate.length_m**2/confirmation_plate.diffusivity_m2_s)/(plate.length_m**2/plate.diffusivity_m2_s)
    confirm_setting = replace(selected_settings, dt_s=selected_settings.dt_s*scale, end_time_s=3*scale)
    confirm_time = reference_cooling_time(confirmation_plate)
    confirm_metrics, _ = evaluate(confirmation_plate, confirm_setting, [t*scale for t in times], confirm_time)
    confirmation = {'plate': asdict(confirmation_plate), 'settings': asdict(confirm_setting),
                    'reference_time_s': confirm_time, **confirm_metrics,
                    'passed_temperature_and_crossing_targets': bool(confirm_metrics['max_abs_error_c']<=criteria['max_temperature_error_c']
                        and confirm_metrics['threshold_error_pct']<=100*criteria['max_threshold_relative_error']
                        and confirm_metrics['within_bounds']),
                    'retuned_after_confirmation': False}
    packages = {name: importlib.metadata.version(name) for name in
                ['numpy', 'scipy', 'matplotlib', 'pytest', 'pytest-html', 'pdoc']}
    try:
        commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    summary = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'parameter_status': 'synthetic illustrative study; no empirical dataset',
        'plate': asdict(plate), 'criteria': criteria, 'reference_cooling_time_s': reference_time,
        'candidate_count': len(candidates), 'eligible_count': len(eligible),
        'benchmark_times_s': times, 'candidate_time_alignment_s': alignment,
        'baseline': {**asdict(baseline_settings), **base_metrics, **base_timing},
        'selected': selected, 'best_per_method': method_best,
        'baseline_to_selected_runtime_ratio': base_timing['median_runtime_s']/selected['median_runtime_s'],
        'optimisation_speedup': optimisation[0]['median_runtime_s']/optimisation[1]['median_runtime_s'],
        'confirmation': confirmation,
        'spatial_order_last': {m: [row for row in spatial if row['method']==m][-1]['observed_order'] for m in method_best},
        'temporal_order_last': {m: [row for row in temporal if row['method']==m][-1]['observed_order'] for m in method_best},
        'environment': {'python': sys.version, 'platform': platform.platform(),
                        'machine': platform.machine(), 'processor': platform.processor(),
                        'packages': packages, 'core_commit_at_run': commit},
        'timing_protocol': 'Warm solve, then >=40ms target batches (max20 solves), median of independent batches; no field snapshots, disk/plot/reference excluded; scalar maximum history retained.',
        'memory_protocol': 'retained ndarray nbytes, not peak process memory; Python lists and temporaries excluded',
        'validation_limit': 'Analytical benchmarks verify mathematical implementation; no physical experimental validation.'}
    (out/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({'selected': selected, 'confirmation': confirmation,
                       'reference_time_s': reference_time}, indent=2), flush=True)


if __name__ == '__main__':
    main()
