"""Reproduce tests, numerical evidence, plots, HTML documentation and report."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

def main() -> None:
    """Run the documented workflow without hidden state or silent stale claims."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-experiments',action='store_true',help='retain saved numerical/timing evidence')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    env=dict(os.environ,PYTHONPATH=str(root/'src'),MPLCONFIGDIR=str(root/'.mplconfig'),MPLBACKEND='Agg')
    def run(*command):
        subprocess.run([sys.executable,*command],cwd=root,env=env,check=True)
    (root/'reports').mkdir(exist_ok=True)
    run('-m','pytest','--html=reports/test_report.html','--self-contained-html','--junitxml=reports/test_results.xml','-q')
    old=json.loads((root/'results/summary.json').read_text()) if (root/'results/summary.json').exists() else None
    if not args.skip_experiments:
        # Reproduce into a separate location. Preserve the submitted run,
        # timing evidence and matching report rather than overwrite its data.
        fresh=root/'tmp/reproduced_results'
        run('scripts/run_experiments.py','--output-dir',str(fresh))
        run('scripts/apply_design_revision.py','--output-dir',str(fresh))
    run('scripts/make_figures.py')
    run('scripts/generate_docs.py')
    new=json.loads((root/'tmp/reproduced_results/summary.json').read_text()) if not args.skip_experiments else old
    if old and not args.skip_experiments:
        difference=abs(old['reference_cooling_time_s']-new['reference_cooling_time_s'])
        if difference>1e-9:
            raise RuntimeError('Reproduced analytical crossing differs from the recorded run.')
        import csv
        with (root/'tmp/reproduced_results/tables/candidate_comparison.csv').open(newline='') as stream:
            candidates=list(csv.DictReader(stream))
        matching=[r for r in candidates if r['method']==old['selected']['method']
                  and int(r['intervals'])==old['selected']['intervals']
                  and abs(float(r['dt_s'])-old['selected']['dt_s'])<1e-15]
        if len(matching)!=1 or any(abs(float(matching[0][k])-old['selected'][k])>1e-9
                                   for k in ['max_abs_error_c','threshold_time_s']):
            raise RuntimeError('The recorded selected configuration did not reproduce numerically.')
        print('Numerical reproduction agrees. Fresh timings are under tmp/reproduced_results; submitted evidence is preserved.')
    run('scripts/build_report.py')
    print('Workflow complete. Saved report and slides describe the recorded run; review any changed timings before resubmission.')

if __name__=='__main__':
    main()
