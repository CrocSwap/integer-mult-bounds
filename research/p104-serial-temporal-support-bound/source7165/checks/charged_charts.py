"""One- or two-chart charged span recovery on the exact #7161 contact tape."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from pathlib import Path
from time import monotonic

DEPENDENCIES = {
    'round9/evidence/complex/side_rows.py': '4ee7c51298e53d54e33b9ab4abc68d489078f0cf5032f52248f773df3f4294e9',
    'round9/evidence/complex/donors/donor_intervals.py': '307af640b97bcc31a13a4b139b418038bbce137686fd6ffed93e8865e44c65ce',
    'round8/evidence/complex/owned.py': '53da0a7b551b34f3baf633083a4362570ebe694a694e2d0b6226d01c08a6ab3b',
}


class ScreenCap(Exception):
    pass


def import_pinned(name, path, expected):
    assert sha256(path.read_bytes()).hexdigest() == expected, path
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def in_span(elimination, target, vectors):
    basis = {}
    for vector in vectors:
        elimination.insert(basis, vector)
    return elimination.insert(basis, target) == 0


def controls(elimination):
    x, y, z = ({0: 1}, {1: 1}, {2: 1})
    assert in_span(elimination, {0: 1, 1: 1}, [x, y])
    assert not in_span(elimination, {0: 1, 1: 1}, [x, z])
    assert in_span(elimination, {0: 1, 1: 1}, [{0: -3, 1: -3}, z])
    assert not list(states_over_time([[], [(0,1,1)], [(2,3,2)]]))
    assert list(states_over_time([[(0,4,0)], [(0,2,1)], [(2,3,2)]])) == [
        (2, ((0,), (1,), (2,)))
    ]


def read_sources(peer, caller_path, interval_path, owned, source_count):
    package = peer / owned.PACKAGE
    name = f'peer/{owned.PACKAGE}/WORD.json.gz'
    compressed = owned.pinned(package/'WORD.json.gz', name)
    raw = gzip.decompress(compressed)
    assert sha256(raw).hexdigest() == owned.PINS[name+'#decompressed']
    result = owned.pinned(package/'RESULT.json', f'peer/{owned.PACKAGE}/RESULT.json')
    caller = owned.pinned(caller_path, 'caller-inputs/CALLER.json')
    interval = import_pinned(f'chart_price_{source_count}', interval_path, owned.PINS['caller-inputs/interval_gate.py'])
    return json.loads(raw), json.loads(result), json.loads(caller), interval


def chart_states(word, moves, chart_classes, geometry, elimination, donor, check_time):
    # Store states only where one of the legal cheap routes could query them.
    windows = {}
    for move in moves:
        lo, hi = move['window']
        for chart in geometry[move['event']]:
            if chart in windows:
                l, h = windows[chart]
                windows[chart] = min(lo,l), max(hi,h)
            else:
                windows[chart] = lo, hi
    last_cut = max(m['window'][1] for m in moves)
    move_events = {m['event']:m['role'] for m in moves}
    active = {}
    intervals = defaultdict(list)
    vectors = []
    sampled = {}
    last_seen = 0

    def flush(role, upper):
        lower, chart, row = active[role]
        left, right = windows[chart]
        lower, upper = max(lower,left), min(upper,right)
        if lower <= upper:
            intervals[chart].append((lower,upper,role,len(vectors)))
            vectors.append(elimination.integral(row))

    def visit(cut, role, chart, row):
        nonlocal last_seen
        assert cut >= last_seen, (cut,last_seen)
        last_seen = cut
        if move_events.get(cut-1) == role:
            assert row
            sampled[cut-1] = elimination.integral(row)
        if role in active:
            flush(role,cut-1)
            del active[role]
        if chart is not None and chart_classes[chart] in windows and row:
            active[role] = (cut,chart_classes[chart],row.copy())

    donor.replay(word,last_cut,visit,check_time)
    assert last_seen == last_cut
    assert sampled.keys() == move_events.keys()
    for role in active:
        flush(role,last_cut)
    return intervals, vectors, sampled


def clipped(records, role, lo, hi):
    return [(max(l,lo),min(h,hi),i) for l,h,r,i in records if r != role and l <= hi and lo <= h]


def states_over_time(pools):
    changes = defaultdict(list)
    for chart,records in enumerate(pools):
        for lo,hi,r in records:
            changes[lo].append((chart, r, True))
            changes[hi+1].append((chart, r, False))
    live = [set() for _ in pools]
    seen = set()
    for cut in sorted(changes):
        for chart,row,added in changes[cut]:
            if added:
                live[chart].add(row)
            else:
                live[chart].remove(row)
        if not all(live[1:]):
            continue
        key = tuple(tuple(sorted(rows)) for rows in live)
        if key not in seen:
            seen.add(key)
            yield cut, key


def run(peer, caller_path, interval_path, owned_path, side_path, donor_path, group_cap, seconds, source_count):
    started = monotonic()

    def check_time():
        if monotonic()-started >= seconds:
            raise ScreenCap('time')

    owned = import_pinned('retained_owned_clocks', owned_path, DEPENDENCIES['round8/evidence/complex/owned.py'])
    elimination = import_pinned('exact_sparse_row_rank', side_path, DEPENDENCIES['round9/evidence/complex/side_rows.py'])
    donor = import_pinned('exact_literal_tape_rows', donor_path, DEPENDENCIES['round9/evidence/complex/donors/donor_intervals.py'])
    controls(elimination)
    word, result, caller, gate = read_sources(peer, caller_path, interval_path, owned, source_count)
    pins = owned.PINS | DEPENDENCIES
    try:
        spaces, native, moves, _ = owned.scan_word(word, check_time, 80000)
        signed, invoice = owned.full_invoice(word, caller, result, native)
        baseline = gate.moment(signed, owned.TARGET)
        rep = {}
        chart_classes = [rep.setdefault(s,i) for i,s in enumerate(spaces)]
        geometry = {}
        for m in moves:
            check_time()
            target = chart_classes[m['target']]
            distances = {i:owned.distance(s,spaces[target]) for s,i in rep.items()}
            geometry[m['event']] = {i:d for i,d in distances.items() if d < m['rank']}
            assert geometry[m['event']][target] == 0
        intervals, vectors, sampled = chart_states(word,moves,chart_classes,geometry,elimination,donor,check_time)
    except ScreenCap as error:
        return dict(status='PREPASS_PENDING', head=owned.HEAD, pins=pins, first_pending=str(error), source_count=source_count)

    routes = []
    local = {}
    for m in sorted(moves,key=lambda m:(-m['rank'],m['event'])):
        lo,hi = m['window']
        ev = m['event']
        target = chart_classes[m['target']]
        possible = geometry[ev]
        groups = {chart:clipped(intervals[chart],m['role'],lo,hi) for chart in possible}
        local[ev] = groups
        positive = sorted(i for i in possible if i != target and groups[i])
        for sources in combinations(positive,source_count):
            cost = sum(possible[chart] for chart in sources)
            if cost < m['rank']:
                routes.append((m,sources,cost))
    routes.sort(key=lambda r:(-r[0]['rank'],r[2],r[0]['event'],r[1]))
    checked = Counter()
    results = []
    first_pending = None
    pending_index = None
    best = {m['event']:m['rank'] for m in moves}

    def test(kind, site, sources, cut, rows):
        nonlocal first_pending
        first_pending = dict(event=site, charts=sources, cut=cut, step=kind)
        check_time()
        if sum(checked.values()) >= group_cap:
            raise ScreenCap('groups')
        checked[kind] += 1
        return in_span(elimination, sampled[site], (vectors[r] for chart in rows for r in chart))

    for index,(move,sources,cost) in enumerate(routes):
        event = move['event']
        target = chart_classes[move['target']]
        pools = [local[event][chart] for chart in (target,*sources)]
        record = dict(event=event, sources=sources, target=target, old_rank=move['rank'], cost=cost,
                      window=move['window'], exact_cuts_tested=0, witness_cut=None)
        try:
            union = [tuple(sorted(r for _,_,r in pool)) for pool in pools]
            optimistic = test('window_union',event,sources,move['window'][0],union)
            record['union_in_span'] = optimistic
            if optimistic:
                for cut,state in states_over_time(pools):
                    supported = test('exact_cut',event,sources,cut,state)
                    record['exact_cuts_tested'] += 1
                    if supported:
                        record['witness_cut'] = cut
                        best[event] = min(best[event],cost)
                        break
        except ScreenCap as error:
            record['pending'] = str(error)
            first_pending['reason'] = str(error)
            pending_index = index
            results.append(record)
            break
        results.append(record)
    if pending_index is None:
        first_pending = None
    pending = routes[pending_index:] if pending_index is not None else []
    optimistic = best.copy()
    for move,_,cost in pending:
        event = move['event']
        optimistic[event] = min(optimistic[event],cost)
    old = Counter(m['rank'] for m in moves)

    def price(rank_by_site):
        histogram = Counter(r for r in rank_by_site.values() if r)
        delta = old.copy()
        delta.subtract(histogram)
        saving = gate.smul(gate.moment(delta,owned.TARGET),owned.STAGES)
        rank_sum = sum(rank_by_site.values())
        packed = gate.power(rank_sum,owned.TARGET) if rank_sum else (0,0)
        packed_saving = gate.smul(gate.sub(gate.moment(old,owned.TARGET),packed),owned.STAGES)
        return dict(ranks=histogram, rank_sum=rank_sum, savings=gate.show(saving),
                    moment=gate.show(gate.add(baseline,saving)),
                    additive_pack_savings=gate.show(packed_saving),
                    additive_pack_moment=gate.show(gate.add(baseline,packed_saving)),
                    lower_rank_sites={m['event']:rank_by_site[m['event']] for m in moves
                                      if rank_by_site[m['event']] < m['rank']})

    return dict(status='CAP_PENDING' if pending else 'EXHAUSTED', head=owned.HEAD, pins=pins,
                source_count=source_count, target=str(owned.TARGET), invoice=invoice, baseline=gate.show(baseline),
                caps=dict(groups=group_cap,seconds=seconds), first_pending=first_pending,
                native_sites=len(moves), admissible_integer_cuts=len({c for m in moves for c in range(m['window'][0],m['window'][1]+1)}),
                interval_rows=len(vectors), chart_spans_with_intervals=len(intervals),
                routes_total=len(routes), routes_tested=len(routes)-len(pending), routes_unresolved=len(pending),
                groups_tested=checked, positive_route_count=sum(r['witness_cut'] is not None for r in results),
                routes=results, confirmed_price=price(best), optimistic_price=price(optimistic), seed=None)


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run with assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('peer','caller_path','interval_path','owned_path','side_path','donor_path'):
        parser.add_argument(name,type=Path)
    parser.add_argument('--group-cap',type=int,default=4096)
    parser.add_argument('--seconds',type=int,default=720)
    parser.add_argument('--source-count',type=int,choices=(1,2),default=1)
    args = parser.parse_args()
    assert 0 < args.group_cap <= 4096 and 0 < args.seconds <= 720
    print(json.dumps(run(**vars(args)),indent=2,sort_keys=True))
