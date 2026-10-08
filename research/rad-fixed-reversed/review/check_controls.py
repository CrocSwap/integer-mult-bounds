"""Focused negative controls for event-slot validation; all paths explicit."""
from pathlib import Path
import argparse
import json
from schedule_audit import run, selected


def check(dag, matching):
    original = json.loads(Path(matching).read_text())
    edges = [{'donor':u,'event':e} for u,e in selected(original)]
    base = run(dag,edges)
    # A nonmaximum partial matching is valid but must allocate one extra role.
    less = run(dag,edges[1:])
    assert less['roles'] == base['roles']+1
    assert less['copied_center_outputs'] == base['copied_center_outputs']
    bad = {
        'duplicate_donor': edges+[dict(edges[0])],
        'duplicate_receiver': [edges[0],dict(donor=edges[1]['donor'],event=edges[0]['event'])]+edges[2:],
        'same_event_backedge': [dict(donor=edges[0]['donor'],event=2*edges[0]['donor'])]+edges[1:],
    }
    rejected = []
    for name,case in bad.items():
        try:
            run(dag,case)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError('accepted '+name)
    return dict(h=base['h'],rejected=rejected,nonmaximum_still_valid=True,
                one_fewer_match_adds_one_role=True,centers_preserved=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--dag',required=True)
    p.add_argument('--matching',required=True)
    p.add_argument('--output',required=True)
    a = p.parse_args()
    result = check(a.dag,a.matching)
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS matching gate controls',result['h'])
