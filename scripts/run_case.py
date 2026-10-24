"""Run one JSON-configured case and save an inspectable result archive."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from heat_project.model import PlateConfig, SolverConfig
from heat_project.solvers import solve
from heat_project.metrics import threshold_crossing_time

def main() -> None:
    """Read validated inputs, run the solver and write NPZ plus JSON outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('configs/baseline.json'))
    parser.add_argument('--output', type=Path, default=Path('results/single_case'))
    args = parser.parse_args()
    data = json.loads(args.config.read_text())
    plate, settings = PlateConfig(**data['plate']), SolverConfig(**data['solver'])
    result = solve(plate, settings, np.linspace(0, settings.end_time_s, 7))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output.with_suffix('.npz'), x_m=result.x_m,
                        times_s=result.times_s, max_temperature_c=result.max_temperature_c,
                        snapshot_times_s=result.snapshot_times_s,
                        temperature_snapshots_c=result.temperature_snapshots_c)
    summary = {'steps': result.steps, 'diffusion_number': result.diffusion_number,
               'threshold_time_s': threshold_crossing_time(result.times_s, result.max_temperature_c, plate.target_temp_c),
               'temperature_axis_order': ['snapshot_time', 'position'], 'input': data}
    args.output.with_suffix('.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
