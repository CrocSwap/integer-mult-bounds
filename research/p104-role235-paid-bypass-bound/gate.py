"""Replay one #7481 owned-to-productive restoration gate, with exact arithmetic."""
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import alarm

ROOT = Path(__file__).resolve().parent
PINS = {
    '7481-WORD.json.gz': 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9',
    '7113-CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    '7481-APPLICATION.json': '1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799',
    'pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
}
ROLE, START, CUT = 1533, 38139, 42503


def add(row, j, coefficient):
    result = row.get(j, Q(0)) + coefficient
    if result:
        row[j] = result
    else:
        row.pop(j, None)


def exact_cut_rows(tape, roles, public):
    out = []
    for role in roles:
        row = {role: Q(1)}
        for op, dest, *args in reversed(tape):
            if dest not in row or op == 'MOVE':
                continue
            factor = row[dest]
            if op in ('INIT', 'CLEAR', 'COPY'):
                del row[dest]
            if op == 'SCALE':
                row[dest] *= Q(args[0])
            if op in ('ADD', 'COPY'):
                add(row, args[0], Q(args[1]) * factor)
        assert all(j < public for j in row)
        out.append(row)
    return out


def column(tape, start, cut, role):
    live = {role: Q(1)}
    dirty_guards = []
    for clock in range(start + 1, cut):
        op, dest, *args = tape[clock]
        if op == 'MOVE':
            continue
        if op in ('INIT', 'CLEAR', 'COPY'):
            before = live.pop(dest, Q(0))
            if before and op in ('INIT', 'COPY'):
                dirty_guards.append((clock, op, dest, str(before)))
        if op in ('ADD', 'COPY') and args[0] in live:
            add(live, dest, Q(args[1]) * live[args[0]])
        if op == 'SCALE' and dest in live:
            live[dest] *= Q(args[0])
    return live, dirty_guards


def basis(rows):
    pivots = {}
    for i, source in enumerate(rows):
        row = source.copy()
        coeff = {i: Q(1)}
        for pivot, (vector, origin) in sorted(pivots.items()):
            if pivot in row:
                scale = row[pivot]
                for j, val in vector.items():
                    add(row, j, -scale * val)
                for j, val in origin.items():
                    add(coeff, j, -scale * val)
        if row:
            pivot = min(row)
            scale = row[pivot]
            pivots[pivot] = ({j: val / scale for j, val in row.items()},
                             {j: val / scale for j, val in coeff.items()})
    return pivots


def representation(pivots, target):
    row = target.copy()
    coeff = {}
    for pivot, (vector, origin) in sorted(pivots.items()):
        if pivot in row:
            scale = row[pivot]
            for j, val in vector.items():
                add(row, j, -scale * val)
            for j, val in origin.items():
                add(coeff, j, scale * val)
    return (row, coeff)


def census(word, cut):
    active = dict(enumerate(word['initial']))
    owned = {}
    lifetimes = []
    paid = Counter()
    cut_roles = None
    ranks = list(map(len, word['frames']))
    for clock, (op, dest, *args) in enumerate(word['program']):
        if clock == cut:
            cut_roles = active.copy()
        if op == 'INIT':
            assert dest not in active
            owned[dest] = (clock, args[0], [])
            active[dest] = args[0]
        elif op == 'CLEAR':
            start, chart, moves = owned.pop(dest)
            assert active.pop(dest) == args[0]
            gain = ranks[args[0]] - ranks[chart]
            if gain > 0 and all(d > 0 for _, _, _, d in moves):
                assert gain == sum(d for _, _, _, d in moves)
                lifetimes.append((dest, start, clock, chart, args[0], gain, moves))
        elif op == 'MOVE':
            before, after, owned_flag = args
            assert active[dest] == before and (dest in owned) == owned_flag
            delta = ranks[after] - ranks[before]
            assert delta
            paid[abs(delta)] += 1
            active[dest] = after
            if owned_flag:
                owned[dest][2].append((clock, before, after, delta))
        elif op in ('ADD', 'COPY'):
            assert active[dest] == active[args[0]] == args[-1]
        else:
            assert op == 'SCALE' and active[dest] == args[-1]
    assert not owned and list(active.values()) == word['final']
    assert sum(paid.values()) == 6279
    return lifetimes, cut_roles, paid


def main():
    assert __debug__
    alarm(30)
    inputs = {name: (ROOT / name).read_bytes() for name in PINS}
    assert {k: sha256(v).hexdigest() for k, v in inputs.items()} == PINS
    w = json.loads(gzip.decompress(inputs['7481-WORD.json.gz']))
    caller = json.loads(inputs['7113-CALLER.json'])
    app = json.loads(inputs['7481-APPLICATION.json'])
    power_bounds = run_path(str(ROOT / 'pricing.py'))['power_bounds']
    tape = w['program']
    public = w['public']
    assert len(tape) == 76475 and public == 1501
    assert caller['stages'] == sum(event[0] == 'J' for event in caller['events']) == 17
    assert tape[START] == ['INIT', ROLE, 597] and tape[CUT] == ['CLEAR', ROLE, 591]
    lifetimes, active, paid = census(w, CUT)
    assert len(lifetimes) == 19 and sum(entry[5] for entry in lifetimes) == 56
    lead, = [entry for entry in lifetimes if entry[0] == ROLE and entry[1] == START]
    assert lead[2:] == (CUT, 597, 591, 7, [(42487, 597, 1031, 4), (42500, 1031, 591, 3)])
    peers = tuple(sorted(q for q, chart in active.items() if chart == 591))
    assert peers == (133, 697, 767, 901, 1334, 1377, ROLE)
    assert not any(f == 591 for f in w['final'])
    lo, hi = map(Q, app['directed_crossing_bracket'])
    assert Q(0) < lo < hi < 1
    gross = (17 * power_bounds(7, hi)[0], 17 * power_bounds(7, lo)[1])
    whole = sum(17 * power_bounds(lead[5], lo)[1] for lead in lifetimes)
    assert 0 < gross[0] <= gross[1] < 119 and whole < 952
    assert app['paid_calls'] == 110519 and app['productive_calls'] == 22461 and app['surplus'] == 1424
    live, guards = column(tape, START, CUT, ROLE)
    assert set(live) <= set(active)
    exterior = {q: value for q, value in live.items() if q not in peers}
    controls = [(['INIT', 3, 0], ['ADD', 2, 3, '2', 0], ['CLEAR', 3, 0]),
                (['INIT', 3, 0], ['COPY', 3, 2, '2', 0], ['CLEAR', 3, 0])]
    assert column(controls[0], 0, 2, 3) == ({2: Q(2), 3: Q(1)}, [])
    assert column(controls[1], 0, 2, 3) == ({}, [(1, 'COPY', 3, '1')])
    necessary = not exterior and not guards
    restoration = None
    if necessary:
        rows = exact_cut_rows(tape[:CUT], peers, public)
        raised = [row.copy() for row in rows]
        for q, row in zip(peers, raised):
            add(row, public, live.get(q, Q(0)))
        target = [row for q, row in zip(peers, rows) if q != ROLE] + [{public: Q(1)}]
        old_rank = len(basis(raised))
        new_rank = len(basis(target))
        union_rank = len(basis(raised + target))
        pivots = basis(raised)
        representations = [representation(pivots, row) for row in target]
        restoration = {'source_rank': old_rank, 'restored_rank': new_rank, 'union_rank': union_rank,
                       'unsupported': sum(bool(remainder) for remainder, _ in representations),
                       'rational_representations': [coeff for _, coeff in representations]}
        necessary = old_rank == new_rank == union_rank
    alarm(0)
    print(json.dumps({
        'case_cap': 1, 'runner_cap_seconds': 30, 'cases_completed': 1,
        'pins': PINS, 'lifetime': lead, 'coframe': peers, 'stock_count': len(lifetimes),
        'stock_rank': 56, 'local_paid': dict(sorted(paid.items())), 'changed_full_paid': {},
        'changed_full_productive': {7: 17}, 'changed_full_rank_surplus': 119,
        'gross_range': list(gross), 'whole_stock_optimistic_upper': whole,
        'cut_dirty_column': dict(sorted(live.items())), 'exterior_dirty_column': dict(sorted(exterior.items())),
        'dirty_guards': guards, 'restoration': restoration, 'necessary_survived': necessary,
        'status': 'NECESSARY_GATE_SURVIVES_DYADIC_AND_PHYSICAL_REPLAY_PENDING' if necessary else 'EXACT_FIXED_CUT_EXCLUSION',
    }, indent=2, sort_keys=True, default=str))


if __name__ == '__main__':
    main()
