#!/usr/bin/env python3
"""Re-instantiate #152's assembly phase-stop constant and re-price kappa.

#152's paired_cube_network.py declares PHASE_STOP = 1/10^6 (the merged #144
value) while its complex side binds (AC = 5113520/10^10). The phase-stop beta
is a free positive constant of the retained assembly (it enters only the
(1-beta)*AC - 10^-10 ceiling term and the 47 strict inequalities, exactly as
in #104/#135/#137/#138 in this repository's lineage), so re-instantiating it
changes no lemma. This script:

  1. reproduces #152's published value exactly at the inherited constants
     (kappa = 5108289/10^10, next point rejected);
  2. re-runs the same assembly with beta = 10^-12 and reports the new exact
     grid kappa with the next grid point rejected.

All arithmetic is #152's own paired_cube_network.py; only the module-global
PHASE_STOP is re-bound between runs. Stdlib only; do not use -O.
"""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.set_int_max_str_digits(0)

import paired_cube_network as pcn

complex_input = json.loads((ROOT / 'certificates/paired-cube-complex-input.json').read_text())


def best_kappa():
    phase = pcn.complex_certificate(complex_input)
    bridge = pcn.finite_bridge(phase, None, complex_input)
    ab = (1 - pcn.ATOM) * pcn.COARSE + pcn.ATOM * pcn.OLD
    assert ab < pcn.ATOM < 1 - ab, 'Subordinate adapter and row tolls'
    asb = min(ab, (1 - pcn.PHASE_STOP) * pcn.AC - Q(1, 10**10))
    grid = 10**10

    def accepts(kk):
        try:
            pcn.assembly(asb, pcn.AC, bridge, Q(kk, grid), beta=pcn.PHASE_STOP)
            return True
        except (AssertionError, ValueError):
            return False

    lo, hi = 0, int(pcn.AC * grid)
    assert accepts(lo) and not accepts(hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if accepts(mid) else (lo, mid)
    assert accepts(lo) and not accepts(lo + 1)
    res = pcn.assembly(asb, pcn.AC, bridge, Q(lo, grid), beta=pcn.PHASE_STOP)
    assert len(res['strict_constraints']) == 47 and all(v > 0 for v in res['strict_constraints'].values())
    assert len(res['margins']) == 7
    return Q(lo, grid), res


def main():
    assert not sys.flags.optimize
    # 1) #152 control at inherited constants
    assert pcn.PHASE_STOP == Q(1, 10**6), pcn.PHASE_STOP
    k0, res0 = best_kappa()
    assert k0 == Q(5108289, 10**10), k0
    print('PASS #152 control: kappa = 5108289/10^10 (next point rejected), 47 constraints, 7 margins')

    # 2) re-instantiate beta
    pcn.PHASE_STOP = Q(1, 10**12)
    k1, res1 = best_kappa()
    assert k1 == Q(2554147, 5 * 10**9), k1
    assert (k1 - Q(5108289, 10**10)) * 10**10 == 5
    print('PASS tightened phase-stop: beta = 10^-12, kappa = 2554147/5000000000 =',
          '5.108294e-4 (next point rejected), 47 constraints, 7 margins')
    print('gain: +5 grid points of the 10^-10 grid over the inherited instantiation')
    print('PASS conditional re-instantiation; all inherited interfaces remain assumptions')


if __name__ == '__main__':
    main()
