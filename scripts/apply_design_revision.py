"""Preserve a failed confirmation and transparently evaluate a revised design.

Run after run_experiments.py. The initial confirmation becomes development
evidence once inspected. A fresh mathematical confirmation checks the revised
choice once. No tolerance is relaxed and no physical validation is implied.
"""
from __future__ import annotations
import argparse
import csv
from dataclasses import asdict, replace
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from heat_project.model import PlateConfig, SolverConfig
from heat_project.solvers import solve
from heat_project.reference import uniform_temperature, reference_cooling_time
from heat_project.metrics import threshold_crossing_time
from run_experiments import evaluate, write_csv


def main() -> None:
    """Freeze a margin-qualified choice, then regenerate all final-design evidence."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results')
    args=parser.parse_args()
    out=args.output_dir.resolve()
    summary=json.loads((out/'summary.json').read_text())
    if 'design_revision' in summary:
        raise RuntimeError('run run_experiments.py first to regenerate the initial evidence')
    revision=json.loads((ROOT/'configs/design_revision.json').read_text())
    (out/'initial_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    initial_selection,initial_confirmation=summary['selected'],summary['confirmation']
    with (out/'tables/candidate_comparison.csv').open(newline='') as stream:
        raw=list(csv.DictReader(stream))
    candidates=[]
    for row in raw:
        converted={}
        for key,value in row.items():
            if key=='method': converted[key]=value
            elif value in ['True','False']: converted[key]=value=='True'
            else: converted[key]=float(value)
        for key in ['intervals','steps','retained_array_bytes','timing_repeats','timing_batch_size']:
            converted[key]=int(converted[key])
        converted['robust_eligible']=bool(converted['eligible'] and converted['max_abs_error_c']<=revision['additional_development_margin_c'])
        candidates.append(converted)
    robust=[row for row in candidates if row['robust_eligible']]
    selected=min(robust,key=lambda row:row['median_runtime_s'])
    best={method:min((row for row in robust if row['method']==method),key=lambda row:row['median_runtime_s'])
          for method in ['ftcs','backward_euler']}
    # This record is written before evaluating either the reused or fresh case.
    (out/'final_selection_frozen.json').write_text(json.dumps({'selected':selected,'revision':revision,
                                                             'initial_confirmation_reclassified':'development'},indent=2)+'\n')
    for row in candidates:
        row['selected_for_final']=row['method']==selected['method'] and row['intervals']==selected['intervals'] and row['dt_s']==selected['dt_s']
    write_csv(out/'tables/candidate_comparison.csv',candidates)
    plate=PlateConfig(**summary['plate'])
    setting=SolverConfig(intervals=selected['intervals'],dt_s=selected['dt_s'],end_time_s=3,method=selected['method'])
    characteristic=plate.length_m**2/plate.diffusivity_m2_s
    times=summary['benchmark_times_s']
    profiles,histories=[],[]
    for method,row in best.items():
        current=SolverConfig(intervals=row['intervals'],dt_s=row['dt_s'],end_time_s=3,method=method)
        _,result=evaluate(plate,current,times,summary['reference_cooling_time_s'])
        for t,field in zip(result.snapshot_times_s,result.temperature_snapshots_c):
            analytical=uniform_temperature(result.x_m,float(t),plate)
            for x,num,ref in zip(result.x_m,field,analytical):
                profiles.append({'method':method,'time_s':float(t),'x_m':float(x),
                                  'temperature_c':float(num),'reference_c':float(ref)})
        for t,value in zip(result.times_s,result.max_temperature_c):
            histories.append({'method':method,'time_s':float(t),'max_temperature_c':float(value),
                               'reference_c':float(uniform_temperature(plate.length_m/2,float(t),plate)),
                               'target_c':plate.target_temp_c})
    write_csv(out/'tables/profiles.csv',profiles)
    write_csv(out/'tables/cooling_history.csv',histories)
    sensitivity=[]
    for parameter in ['length_m','diffusivity_m2_s']:
        for multiplier in [0.5,1.0,2.0]:
            changed=replace(plate,**{parameter:getattr(plate,parameter)*multiplier})
            scale=(changed.length_m**2/changed.diffusivity_m2_s)/characteristic
            result=solve(changed,replace(setting,dt_s=setting.dt_s*scale,end_time_s=3*scale),[])
            ref=reference_cooling_time(changed)
            crossing=threshold_crossing_time(result.times_s,result.max_temperature_c,changed.target_temp_c)
            sensitivity.append({'parameter':parameter,'multiplier':multiplier,'length_m':changed.length_m,
                                 'diffusivity_m2_s':changed.diffusivity_m2_s,'reference_time_s':ref,
                                 'numerical_time_s':crossing,'relative_error_pct':100*abs(crossing-ref)/ref})
    write_csv(out/'tables/sensitivity.csv',sensitivity)
    def check_case(config):
        case=PlateConfig(**config)
        scale=(case.length_m**2/case.diffusivity_m2_s)/characteristic
        current=replace(setting,dt_s=setting.dt_s*scale,end_time_s=3*scale)
        ref=reference_cooling_time(case)
        metrics,_=evaluate(case,current,[t*scale for t in times],ref)
        return {'plate':asdict(case),'settings':asdict(current),'reference_time_s':ref,**metrics,
                 'passed_temperature_and_crossing_targets':bool(metrics['max_abs_error_c']<=1
                     and metrics['threshold_error_pct']<=2 and metrics['within_bounds'])}
    reused=check_case(initial_confirmation['plate'])
    final=check_case(revision['final_confirmation'])
    final['retuned_after_confirmation']=False
    final['independence_limit']='Fresh mathematical check after an openly documented design revision, not empirical validation. Linear scaling makes temperature-span effects predictable.'
    summary.update({'initial_selection':initial_selection,'initial_confirmation':initial_confirmation,
                    'selected':selected,'best_per_method':best,'design_revision':revision,
                    'reused_case_development_check':reused,'confirmation':final,
                    'robust_eligible_count':len(robust),
                    'baseline_to_selected_runtime_ratio':summary['baseline']['median_runtime_s']/selected['median_runtime_s']})
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'final_selected':selected,'reused_development':reused,'final_confirmation':final},indent=2))

if __name__=='__main__':
    main()
