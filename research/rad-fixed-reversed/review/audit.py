"""Portable independent review of freshly regenerated ORIGINAL DAG schedules.

No producer modules are imported. Run after producer.py has generated h23/h25.
The exact original event-slot matching is independently checked against each
raw DAG; the producer's positive selected-links.json is a different witness.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

HERE=Path(__file__).resolve().parent


def load(name):
    spec=importlib.util.spec_from_file_location('rad_review_'+name,HERE/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def run(work):
    pins=json.loads((HERE/'input-pins.json').read_text())
    labels=load('original_label_audit');schedule=load('schedule_audit')
    results=[]
    for h in (23,25):
        dag=Path(work)/f'h{h}'/'dag.bin'
        expected=pins[str(h)]
        assert hashlib.sha256(dag.read_bytes()).hexdigest()==expected['dag_sha256']
        matching=HERE/f'original-matching{h}.json'
        assert hashlib.sha256(matching.read_bytes()).hexdigest()==expected['matching_file_sha256']
        fresh=json.loads((Path(work)/f'h{h}'/'events.json').read_text())
        assert sorted(schedule.selected(fresh))==sorted(schedule.selected(json.loads(matching.read_text())))
        label=labels.run(dag)
        allocated=schedule.run(dag,fresh,complete_dirty=True)
        for field in ('roles','matches','selected_edges_sha256'):
            assert allocated[field]==expected[field]
        assert label['center_terminal_count']==allocated['copied_center_outputs']==h
        assert label['JLV_identity'] and allocated['complete_dirty_basis']
        profile=json.loads((Path(work)/f'h{h}'/'profile.json').read_text())
        assert profile['R']==allocated['roles'] and profile['blocks'][h]==h
        assert sum(t*n for t,n in enumerate(profile['blocks']))==h*allocated['roles']+2*h*(h-1)
        results.append(dict(h=h,labels=label,schedule=allocated,
                            original_profile_rank_sum=profile['rank_sum'],
                            copied_profile_rank_sum=profile['rank_sum']-h*(h-1)))
    return dict(status='PASS exact original scalar, frames, carrier slots and complete dirty basis',
                rows=results,
                source_sha256={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                               for name in ('audit.py','original_label_audit.py','schedule_audit.py','input-pins.json')},
                scope='Finite original-envelope producer and matching; profile CRT and all-size transfer checked separately.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=run(a.work);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'])
