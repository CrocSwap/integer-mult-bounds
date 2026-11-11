"""Check exact proportional donors in every live chart on retained #7161 clocks."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
from time import monotonic

OWNED_SHA = '53da0a7b551b34f3baf633083a4362570ebe694a694e2d0b6226d01c08a6ab3b'


def load_pinned(name, path, expected):
    assert sha256(path.read_bytes()).hexdigest() == expected, path
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row_key(row):
    first = min(row)
    leading = row[first]
    return tuple((i, row[i] / leading) for i in sorted(row))


def replay(word, last_cut, visit, check_time):
    public = word['public']
    charts = word['initial'] + [None]*word['owned_fields']
    rows = [{i:Fraction(1)} for i in range(public)] + [{} for _ in range(word['owned_fields'])]
    coefficients = {}
    for r, row in enumerate(rows):
        visit(0, r, charts[r], row)
    for i, (op, role, *args) in enumerate(word['program'][:last_cut]):
        if i % 1024 == 0:
            check_time()
        if op == 'MOVE':
            assert charts[role] == args[0]
            charts[role] = args[1]
        elif op == 'INIT':
            assert charts[role] is None and not rows[role]
            charts[role] = args[0]
        elif op == 'CLEAR':
            assert charts[role] == args[0]
            charts[role], rows[role] = None, {}
        else:
            token = args[0 if op == 'SCALE' else 1]
            if token not in coefficients:
                coefficients[token] = Fraction(token)
            value = coefficients[token]
            if op == 'SCALE':
                assert charts[role] == args[1] and value
                rows[role] = {i:value*x for i,x in rows[role].items()}
            else:
                source = args[0]
                assert charts[role] == charts[source] == args[2]
                assert op == 'ADD' or op == 'COPY' and not rows[role]
                for coordinate,x in rows[source].items():
                    z = rows[role].get(coordinate,0) + value*x
                    if z:
                        rows[role][coordinate] = z
                    else:
                        rows[role].pop(coordinate,None)
        visit(i+1, role, charts[role], rows[role])


def controls():
    assert row_key({0:Fraction(2),3:Fraction(-5)}) == row_key({3:Fraction(15),0:Fraction(-6)})
    assert row_key({0:Fraction(2),3:Fraction(-5)}) != row_key({0:Fraction(-6),3:Fraction(-15)})
    toy = dict(public=3, owned_fields=0, initial=[0,0,0],
               program=[['ADD',0,2,'3',0], ['SCALE',0,'-2',0]])
    timeline = []
    replay(toy, 2, lambda cut,role,chart,row: timeline.append((cut,role,dict(row))), lambda:None)
    assert timeline[-2:] == [(1,0,{0:1,2:3}), (2,0,{0:-2,2:-6})]


def run(peer_root, caller_path, gate_path, owned_path, cut_cap, seconds):
    controls()
    started = monotonic()

    def check_time():
        if monotonic()-started > seconds:
            raise TimeoutError('donor tape prepass reached its deadline')

    helper = load_pinned('owned_clocks', owned_path, OWNED_SHA)
    package = peer_root / helper.PACKAGE
    pins = helper.PINS | {'round8/evidence/complex/owned.py': OWNED_SHA}
    word_raw = gzip.decompress(helper.pinned(package/'WORD.json.gz', f'peer/{helper.PACKAGE}/WORD.json.gz'))
    assert sha256(word_raw).hexdigest() == pins[f'peer/{helper.PACKAGE}/WORD.json.gz#decompressed']
    word = json.loads(word_raw)
    result = json.loads(helper.pinned(package/'RESULT.json', f'peer/{helper.PACKAGE}/RESULT.json'))
    caller = json.loads(helper.pinned(caller_path, 'caller-inputs/CALLER.json'))
    gate = load_pinned('directed_power', gate_path, pins['caller-inputs/interval_gate.py'])
    try:
        spaces, native, moves, _ = helper.scan_word(word, check_time, 80000)
        signed, invoice = helper.full_invoice(word, caller, result, native)
        baseline = gate.moment(signed, helper.TARGET)
        by_role = defaultdict(set)
        for m in moves:
            by_role[m['role']].add(m['event'])
        seen_by_cut = {}

        def sample(cut, role, chart, row):
            if cut-1 in by_role.get(role, ()):
                assert chart is not None and row
                seen_by_cut[cut-1] = row_key(row)

        replay(word, max(m['event'] for m in moves)+1, sample, check_time)
        assert seen_by_cut.keys() == {m['event'] for m in moves}
        moves_by_key = defaultdict(list)
        for move in moves:
            moves_by_key[seen_by_cut[move['event']]].append(move)
        allowed_leads = {(len(key), key[0][0]) for key in moves_by_key}
        last_cut = max(m['window'][1] for m in moves)
        available = {}
        intervals = []
        stored = Counter()

        def flush(role, stop):
            lo,key,chart = available[role]
            for move in moves_by_key[key]:
                first = max(lo, move['window'][0])
                last = min(stop, move['window'][1])
                if role != move['role'] and first <= last:
                    d = helper.distance(spaces[chart], spaces[move['target']])
                    intervals.append(dict(first=first, last=last, event=move['event'], role=role,
                                          chart=chart, target=move['target'], old_rank=move['rank'], rank=d))
                stored['interval_move_intersections'] += 1
            stored['constant_intervals'] += 1

        def index(cut, role, chart, row):
            key = None
            if row and (len(row), min(row)) in allowed_leads:
                key = row_key(row)
            old = available.get(role)
            if old and (old[1],old[2]) == (key,chart):
                return
            if old:
                flush(role, cut-1)
                del available[role]
            if key in moves_by_key:
                assert chart is not None
                available[role] = (cut,key,chart)

        replay(word, last_cut, index, check_time)
        for role in available:
            flush(role,last_cut)
    except TimeoutError:
        return dict(status='INCOMPLETE_TAPE_PREPASS', head=helper.HEAD, pins=pins, first_pending='prepass')
    intervals.sort(key=lambda x:(x['first'],x['event'],x['role'],x['chart'],x['last']))
    cuts = set()
    checked = []
    pending = None
    best = {m['event']:m['rank'] for m in moves}
    for i, candidate in enumerate(intervals):
        new = candidate['first'] not in cuts
        if new and len(cuts) >= cut_cap or monotonic()-started > seconds:
            pending = i
            break
        cuts.add(candidate['first'])
        checked.append(candidate)
        event = candidate['event']
        best[event] = min(best[event], candidate['rank'])
    assert len(cuts) <= cut_cap
    untested = intervals[pending:] if pending is not None else ()
    # Grant each pending site its shortest price-compatible distance. The tape
    # index has already authenticated these interval lengths and chart labels.
    for candidate in untested:
        event = candidate['event']
        best[event] = min(best[event], candidate['rank'])
    paid = {m['event']:m['rank'] for m in moves}
    old = Counter(paid.values())
    reduced = Counter(rank for rank in best.values() if rank)
    difference = old.copy()
    difference.subtract(reduced)
    saving = gate.smul(gate.moment(difference, helper.TARGET), helper.STAGES)
    packed_rank = sum(best.values())
    packed = gate.power(packed_rank, helper.TARGET) if packed_rank else (0,0)
    packed_saving = gate.smul(gate.sub(gate.moment(old, helper.TARGET), packed), helper.STAGES)
    paid_sites = sorted(i for i in best if best[i] < paid[i])
    assert all(c['role'] != next(m['role'] for m in moves if m['event']==c['event']) for c in intervals)
    return dict(status='EXHAUSTED' if pending is None else 'CAP_PENDING', head=helper.HEAD,
                target=str(helper.TARGET), pins=pins, baseline=gate.show(baseline), invoice=invoice,
                caps=dict(representative_cuts=cut_cap, seconds=seconds),
                all_integer_cuts=len({c for m in moves for c in range(m['window'][0],m['window'][1]+1)}),
                representative_cuts_tested=len(cuts), proportional_intervals_total=len(intervals),
                proportional_intervals_tested=len(checked), proportional_intervals_unresolved=len(untested),
                first_pending=untested[0] if untested else None, census=stored,
                projective_target_rows=len(moves_by_key), intervals=checked,
                old_native_ranks=old, optimistic_native_ranks=reduced,
                potentially_saving_events=paid_sites, site_lower_rank={i:best[i] for i in paid_sites},
                directed_saving_upper=gate.show(saving)[1],
                directed_resulting_moment_upper=gate.show(gate.add(baseline, (0,max(0,saving[1]))))[1],
                additive_packing=dict(rank=packed_rank, directed_saving_upper=gate.show(packed_saving)[1],
                                      directed_resulting_moment_upper=gate.show(gate.add(baseline, (0,packed_saving[1])))[1]),
                controls=['rational projective equality and sign negative', 'ADD/COPY coordinate cannot replace event clock'],
                seed=None)


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run with assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('peer_root','caller_path','gate_path','owned_path'):
        parser.add_argument(name,type=Path)
    parser.add_argument('--cut-cap',type=int,default=2048)
    parser.add_argument('--seconds',type=int,default=480)
    args = parser.parse_args()
    assert 0 < args.cut_cap <= 2048 and 0 < args.seconds <= 480
    print(json.dumps(run(**vars(args)),indent=2,sort_keys=True))
