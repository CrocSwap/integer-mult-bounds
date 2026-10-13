#!/usr/bin/env python3
"""Verify the gauge/recycling composition; stdlib, run without -O.

Default transports the geometry check from PR150 via exact fresh-move equality.
Run PR150's verifier first, or use --frames to rebuild those exact Q checks here.
"""
import json
import random
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'bit-reuse-147'
sys.path.insert(0, str(BASE))
import word147
import price147


def main():
    assert not sys.flags.optimize, 'run without -O'
    _, W, _, S, record, folder = word147.load_schedule()
    oldplan = json.loads((BASE / 'plan.json').read_text())
    plan = json.loads((HERE / 'plan.json').read_text())
    assert plan['elim'] == oldplan['elim'] and plan['pairs'] == oldplan['pairs']
    old = word147.Word(S, **oldplan)
    word = word147.Word(S, **plan)
    added = word.level - old.level
    assert old.level <= word.level
    assert Counter(S.f[b] for b in added) == {16: 165, 17: 22}
    assert all(word.p[b] == p for b, p in old.p.items())
    assert all(word.death[d] < word.p[b] for b, d in plan['pairs'])
    led = word.ledger()
    row = word.row(led, record)
    assert row == json.loads((HERE / 'row.json').read_text())
    fresh = word.new_moves(led)
    assert fresh == old.new_moves(old.ledger()) and len(fresh) == 4878
    delta = Counter({int(r): n for r, n in row['child_histogram'].items()})
    delta.subtract({int(r): n for r, n in old.row(old.ledger(), record)['child_histogram'].items()})
    assert {r: n for r, n in delta.items() if n} == {
        1: 339, 2: 597, 3: 405, 4: 45, 16: 693, 17: -183,
        18: -489, 19: -495, 20: -87, 48: 165, 51: 22}
    print('PASS plan, timetable, ledger, histogram; exact equality of all 4878 fresh moves', flush=True)
    if '--frames' in sys.argv:
        from frames147 import Exact
        exact = Exact(S, W, folder)
        for reg, a, b in fresh:
            assert exact.inside(a, b), (reg, a, b)
            assert exact.nondegenerate(a) and exact.nondegenerate(b)
        print('PASS rebuilt exact Q nesting/nondegeneracy of all fresh moves', flush=True)
    outputs = {(c, tuple(T)): n for c, T, n in W['outputs']}
    for ring in (2, 0):
        assert word.complete(ring, outputs)
        print('PASS complete formal scalar identity over', 'F2' if ring else 'Z', flush=True)
    rng = random.Random(20261009)
    for tamper in ('stale', 'early', 'vlast'):
        assert not word.replay(0, rng, outputs, tamper), tamper
    print('PASS stale/early/wrong-inverse negative controls', flush=True)
    for atom, expected in ((Q(1, 2000), Q(472143085, 10**12)),
                           (Q(473, 10**6), Q(472154791, 10**12))):
        result = price147.price(row, atom)
        assert result['coarse'] == Q(472806533, 10**12)
        assert result['kappa'] == expected
        print('PASS exact assembly, atom', atom, 'kappa', expected, flush=True)
    print('PASS conditional composition; inherited interfaces remain assumptions')


if __name__ == '__main__':
    main()
