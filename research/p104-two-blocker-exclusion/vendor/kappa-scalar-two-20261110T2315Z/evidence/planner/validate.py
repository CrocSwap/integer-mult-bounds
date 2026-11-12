"""Independent exact scalar matrices and controls for the two-blocker planner."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

from two_blockers import ROOT, WORD_SHA, axes, choices, coefficient_admissible, plans


def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_word(path):
    payload = gzip.decompress(path.read_bytes())
    assert sha256(payload).hexdigest() == WORD_SHA
    return json.loads(payload)


def inventory(word):
    port = load('pinned_port', ROOT/'kappa-typea-birth2-20261110T2258Z/evidence/scalar/port.py')
    graph = port.module('current_graph', port.GRAPH)
    retained = port.module('retained_adjacent_blocker', port.BASE)
    raw, _, _, _, _, _, scalar, _, _, _, child = retained.inventory(word, graph)
    return raw, scalar, child


def exact_rows(events):
    rows = {}
    for event in events:
        op, r = event[:2]
        if op == 'MOVE':
            continue
        prior = rows.get(r, {r: Q(1)})
        if op == 'SCALE':
            row = {a: x * Q(event[2]) for a, x in prior.items()}
        elif op in ('ADD', 'COPY'):
            s, factor = event[2], Q(event[3])
            row = prior.copy()
            for a, x in rows.get(s, {s: Q(1)}).items():
                value = row.get(a, 0) + factor * x
                if value:
                    row[a] = value
                else:
                    row.pop(a, None)
        else:
            assert op in ('INIT', 'CLEAR')
            row = {}
        rows[r] = row
    return {r: row for r, row in rows.items() if row != {r: Q(1)}}


def rewrite(program, add, cut, ops):
    assert cut not in (add, add+1)
    if cut <= add:
        before = program[cut:add+1]
        after = [*ops, *program[cut:add]]
    else:
        before = program[add:cut]
        after = [*program[add+1:cut], *ops]
    return before, after


def run(word_path):
    w = read_word(word_path)
    raw, scalar, child = inventory(w)
    prog = w['program']
    matrix_counts, stats = Counter(), Counter()
    controls, longest = {}, {}
    for i, blockers, _, _, ops in plans(w, scalar, child):
        b1, b2 = blockers
        a, p, q = prog[i], prog[b1], prog[b2]
        later = b1 > i
        if later:
            assert i < b1 < b2
            before, after = (a, p, q), (p, q, *ops)
        else:
            assert b2 < b1 < i
            before, after = (q, p, a), (*ops, q, p)
        target = exact_rows(before)
        assert target == exact_rows(after), (i, blockers, ops)
        assert exact_rows((a, p)) != exact_rows((p, a)), (i, b1)
        assert {e[1] for e in ops}.isdisjoint({e[2] for e in ops})
        assert exact_rows(ops) == exact_rows(reversed(ops))
        direction = 'later' if later else 'earlier'
        matrix_counts[direction] += 1
        if exact_rows((a, q)) == exact_rows((q, a)):
            matrix_counts[f'{direction} second commutes with original'] += 1
            controls.setdefault(f'{direction} recomputed second support', [i, *blockers])
        bad = ((p, q, *ops[:-1]) if later else (*ops[:-1], q, p))
        if target != exact_rows(bad):
            controls.setdefault(f'{direction} missing emitted term', [i, *blockers])
        unchanged = ((p, q, a) if later else (a, q, p))
        if target != exact_rows(unchanged):
            controls.setdefault(f'{direction} unretuned original', [i, *blockers])
    for candidate in choices(w, raw, scalar, child, stats):
        i, blockers, cut, ops, pairs = candidate
        for event, pair in zip(ops, pairs):
            assert tuple(raw[j][0] for j in pair) == tuple(axes(event))
            assert all(raw[j][1] < cut for j in pair)
        key = ('later' if blockers[0] > i else 'earlier', len(ops))
        if key not in longest or abs(cut-i) > abs(longest[key][2]-longest[key][0]):
            longest[key] = candidate
    windows = []
    for (direction, count), (i, blockers, cut, ops, _) in sorted(longest.items()):
        before, after = rewrite(prog, i, cut, ops)
        assert exact_rows(before) == exact_rows(after), (i, blockers, cut)
        windows.append(dict(direction=direction, terms=count, add=i, blockers=blockers,
                            cut=cut, original_events=len(before), ops=ops))
    assert len(controls) == 6 and len(windows) == 8
    assert coefficient_admissible(Q(1,1125*2**25))
    assert not coefficient_admissible(Q(1,7))
    assert not coefficient_admissible(Q(1,2**26))
    assert not coefficient_admissible(Q(2**16))
    return dict(status='PASS_EXACT_TWO_BLOCKER_PLANNER', source_word_sha256=WORD_SHA,
                counts=stats, exact_local_matrices=matrix_counts, controls=controls,
                maximum_interval_controls=windows, coefficient_controls=['denominator 7',
                    'denominator 2^26', 'magnitude 2^16'])


if __name__ == '__main__':
    print(json.dumps(run(Path(sys.argv[1])), indent=2, sort_keys=True))
