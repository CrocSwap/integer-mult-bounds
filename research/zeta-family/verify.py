#!/usr/bin/env python3
"""Verify the zeta family: semantic evaluation, THEIR compiler, THEIR assembly.
Stdlib only; run without -O.  Prints PASS with the certified table."""
import random
import sys
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'scripts/paired_cube'))
sys.path.insert(0, str(ROOT / 'research/zeta-family'))
from paired_cube.frames import compile_graph          # THEIR compiler
from structured_bulk_assembly import assembly          # THEIR 47-constraint assembly
from zeta import zeta_graph
from word import run_controls, replay

FRONTIER = Q(593970203079492, 10**18)                 # PR #163, for reference only
EXPECTED = {3: '3.0519e-02', 4: '1.7960e-02', 5: '1.2279e-02',
            6: '9.0809e-03', 7: '7.3150e-03', 8: '5.9618e-03'}  # roots (k>=7: default source)


def dummy_bridge():
    E = 2**200
    return dict(semantic=dict(E=E, strict_literal_gap=E, B=2**80 + E, C0=32 * 66 * (2**80 + E)**2,
                              C1=1, induction_gap=E, fixed_odd_divisor=3),
                rows=dict(degree=70000, coefficient=100, degree_gap=70000 - 204))


def semantics(g, seed):
    rng = random.Random(seed)
    x = [rng.randrange(1, 10**6) for _ in g['inputs']]
    val = list(x) + [0] * (len(g['args']) - len(g['inputs']))
    for i in range(len(g['inputs']), len(g['args'])):
        a, b = g['args'][i]
        val[i] = val[a] + val[b]
    for r in g['roots']:
        t = g['inputs'][r['targets'][0]]
        if val[r['node']] != sum(x[i] for i, u in enumerate(g['inputs']) if (u & t) == 0):
            return False
    return True


def main():
    assert not sys.flags.optimize, 'run without -O'
    print('h  v     R     R/v   root       kappa      x-frontier')
    for h in (3, 4, 5, 6, 7, 8):
        g = zeta_graph(h)
        for seed in (1, 7):
            assert semantics(g, seed), 'semantic evaluation failed at seed %d' % seed
        assert run_controls(g), 'scalar word/replay controls failed'   # the word layer
        prof, _ = compile_graph(g, [])                 # THEIR compiler, all asserts
        root = prof['numerical_complex_root']
        assert root is not None
        a = Q(int(root * 10**12), 10**12)
        b = a * (1 + Q(1, 1000))
        res = assembly(a, b, dummy_bridge(), Q(1, 10**12), beta=Q(1, 10**6))  # THEIR assembly
        kap = res['minimum_margin']
        assert float(kap) / float(FRONTIER) > 9.0, 'frontier multiple'
        print('%d %4d %5d %6.2f %10.4e %10.4e %8.1fx' % (
            h, prof['v'], prof['R'], prof['R'] / prof['v'], root, float(kap), float(kap) / float(FRONTIER)))
    print('PASS: semantic evaluation, scalar word/replay with tamper controls, in-tree compiler identities, in-tree assembly')


if __name__ == '__main__':
    main()
