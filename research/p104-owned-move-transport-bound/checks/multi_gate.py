"""Window-union necessary rank gate for at least three separately charged charts."""

import argparse
from collections import Counter
import json
from pathlib import Path
from time import monotonic

import hashlib
import importlib.util

MAIN_SHA = '6745163b953006ae1ee2627a8a375cb0711748a6c2b89eead7abb71f887ed280'


def main_module(path):
    assert hashlib.sha256(path.read_bytes()).hexdigest() == MAIN_SHA, path
    spec = importlib.util.spec_from_file_location('charged_chart_gate',path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(peer, caller_path, interval_path, owned_path, side_path, donor_path, chart_gate_path, seconds):
    started = monotonic()

    def check_time():
        if monotonic()-started >= seconds:
            raise TimeoutError('four-minute gate cap')

    main = main_module(chart_gate_path)
    pins = main.DEPENDENCIES
    owned = main.import_pinned('multi_owned_clocks',owned_path,pins['round8/evidence/complex/owned.py'])
    elimination = main.import_pinned('multi_row_rank',side_path,pins['round9/evidence/complex/side_rows.py'])
    donor = main.import_pinned('multi_tape_rows',donor_path,pins['round9/evidence/complex/donors/donor_intervals.py'])
    main.controls(elimination)
    word,result,caller,gate = main.read_sources(peer,caller_path,interval_path,owned,3)
    pins = owned.PINS | pins | {'round10/evidence/complex/charged_charts.py': MAIN_SHA}
    try:
        spaces,native,moves,_ = owned.scan_word(word,check_time,80000)
        signed,invoice = owned.full_invoice(word,caller,result,native)
        baseline = gate.moment(signed,owned.TARGET)
        sites = sorted((m for m in moves if m['rank'] >= 4),key=lambda m:(-m['rank'],m['event']))
        assert len(sites) == 16
        rep = {}
        classes = [rep.setdefault(s,i) for i,s in enumerate(spaces)]
        geometry = {}
        for m in sites:
            check_time()
            target = classes[m['target']]
            d = {i:owned.distance(s,spaces[target]) for s,i in rep.items()}
            geometry[m['event']] = {i:r for i,r in d.items() if r <= m['rank']-3}
        intervals,vectors,selected = main.chart_states(word,sites,classes,geometry,elimination,donor,check_time)
    except TimeoutError:
        return dict(status='PREPASS_PENDING',head=owned.HEAD,pins=pins,first_pending='prepass',cap_seconds=seconds)

    results = []
    pending = None
    best = {m['event']:m['rank'] for m in moves}
    group_count = 0
    for i,m in enumerate(sites):
        event = m['event']
        target = classes[m['target']]
        lo,hi = m['window']
        costs = geometry[event]
        pools = {chart:main.clipped(intervals[chart],m['role'],lo,hi) for chart in costs}
        available = [chart for chart in sorted(costs,key=lambda chart:(costs[chart],chart)) if chart != target and pools[chart]]
        site = dict(event=event, old_rank=m['rank'], target=target, clock=m['window'], tests=[], optimistic_lower_rank=None)
        try:
            for budget in range(3,m['rank']):
                check_time()
                eligible = []
                for chart in available:
                    other = [x for x in available[:3] if x != chart][:2]
                    if len(other) == 2 and costs[chart]+sum(costs[x] for x in other) <= budget:
                        eligible.append(chart)
                test = dict(budget=budget,charts=eligible,union_in_span=False)
                if eligible:
                    assert len(eligible) >= 3
                    vectors_here = (vectors[r] for chart in (target,*eligible) for _,_,r in pools[chart])
                    test['union_in_span'] = main.in_span(elimination,selected[event],vectors_here)
                    group_count += 1
                site['tests'].append(test)
                if test['union_in_span']:
                    best[event] = budget
                    site['optimistic_lower_rank'] = budget
                    break
        except TimeoutError:
            pending = dict(index=i,event=event,budget=budget)
            site['pending'] = True
            results.append(site)
            break
        results.append(site)
    if pending:
        # Each pending site retains the optimistic cost of three positive ranks.
        for m in sites[pending['index']:]:
            best[m['event']] = 3
    old = Counter(m['rank'] for m in moves)
    delta = old.copy()
    delta.subtract(Counter(best.values()))
    saving = gate.smul(gate.moment(delta,owned.TARGET),owned.STAGES)
    rank_sum = sum(best.values())
    packed = gate.smul(gate.sub(gate.moment(old,owned.TARGET),gate.power(rank_sum,owned.TARGET)),owned.STAGES)
    survivors = [r['event'] for r in results if r['optimistic_lower_rank'] is not None]
    return dict(status='CAP_PENDING' if pending else 'EXHAUSTED',head=owned.HEAD,pins=pins,
                invoice=invoice,target=str(owned.TARGET),baseline=gate.show(baseline),cap_seconds=seconds,
                first_pending=pending,old_sites=len(moves),high_rank_sites=len(sites),
                high_rank_sites_unresolved=len(sites)-len(results)+(1 if pending else 0),
                union_groups_tested=group_count,union_survivor_sites=survivors,results=results,
                optimistic_price=dict(saving=gate.show(saving),moment=gate.show(gate.add(baseline,saving)),
                                      additive_pack_rank=rank_sum,
                                      additive_pack_moment=gate.show(gate.add(baseline,packed))),seed=None)


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run with assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    for label in ('peer','caller_path','interval_path','owned_path','side_path','donor_path','chart_gate_path'):
        parser.add_argument(label,type=Path)
    parser.add_argument('--seconds',type=int,default=240)
    args = parser.parse_args()
    assert 0 < args.seconds <= 240
    print(json.dumps(run(**vars(args)),indent=2,sort_keys=True))
