#!/usr/bin/env python3
"""Re-instantiate the assembly's atom exponent at its toll edge on #157's
unchanged certificates: conditional kappa = 1111463/2000000000 = 5.557315e-4.

#157's bit side binds (coarse 5566382/10^10 < complex 5622769/10^10). The
atom exponent theta of #144's retained assembly is a free positive constant
(it enters only through ab = (1-theta)*COARSE + theta*OLD and the strict
toll ab < theta < 1-ab). #157 inherits the merged value 1/1000; the first
grid point at which the toll holds is theta = 556349912/10^12, and kappa is
strictly decreasing in theta on the acceptance window, so the grid-maximal
instantiation is that first point.

This script (stdlib only; do not use -O):
  1. reproduces #157's published kappa = 5555021/10^10 at the inherited
     constants, with #157's own producer, certificates and assembly;
  2. re-instantiates theta = 556349912/10^12 (and retains #157's phase-stop
     1/10^6, which is slack: the bit side binds below the beta ceiling);
  3. asserts kappa = 1111463/2000000000 on the 10^-10 grid with the next
     grid point rejected, all 47 strict constraints positive.
"""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.set_int_max_str_digits(0)

import paired_cube_network as pcn  # pyright: ignore[reportMissingImports]

THETA = Q(556349912, 10**12)
PHASE_STOP = Q(1, 10**6)      # #157's inherited value, unchanged (slack here)
GRID = 10**10


def assembly_inputs():
    row = json.loads((ROOT / 'certificates/paired-cube-complex-input.json').read_text())
    from paired_cube_physical import checked_record  # pyright: ignore[reportMissingImports]
    phys = checked_record()
    phase = pcn.complex_certificate(row, phys)
    bridge = pcn.finite_bridge(phase, None, row)
    return bridge


def kappa_for(atom, beta, bridge, grid=GRID):
    ab = (1 - atom) * pcn.COARSE + atom * pcn.OLD
    assert ab < atom < 1 - ab, 'Subordinate adapter and row tolls'
    asb = min(ab, (1 - beta) * pcn.AC - Q(1, 10**10))

    def accepts(kk):
        try:
            pcn.assembly(asb, pcn.AC, bridge, Q(kk, grid), beta=beta)
            return True
        except (AssertionError, ValueError):
            return False

    lo, hi = 0, int(pcn.AC * grid)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if accepts(mid) else (lo, mid)
    return Q(lo, grid)


def main():
    assert not sys.flags.optimize
    bridge = assembly_inputs()

    # 1) #157 control at inherited constants
    assert pcn.ATOM == Q(1, 1000)
    k0 = kappa_for(pcn.ATOM, pcn.PHASE_STOP, bridge)
    assert k0 == Q(5555021, 10**10), k0
    print('PASS #157 control: kappa = 5555021/10^10 (bit side binds: coarse', 
          float(pcn.COARSE), '< complex', float(pcn.AC), ')')

    # 2) edge check: one grid step below theta is rejected by the toll
    ab_below = (1 - (THETA - Q(1, 10**12))) * pcn.COARSE + (THETA - Q(1, 10**12)) * pcn.OLD
    assert not ab_below < THETA - Q(1, 10**12), 'theta window floor is loose'

    # 3) re-instantiated theta
    k1 = kappa_for(THETA, PHASE_STOP, bridge)
    assert k1 == Q(1111463, 2 * 10**9), k1
    # next grid point rejected
    asb = min((1 - THETA) * pcn.COARSE + THETA * pcn.OLD,
              (1 - PHASE_STOP) * pcn.AC - Q(1, 10**10))
    try:
        pcn.assembly(asb, pcn.AC, bridge, k1 + Q(1, GRID), beta=PHASE_STOP)
        raise AssertionError('next grid point should be rejected')
    except (AssertionError, ValueError) as e:
        if 'next grid point should be rejected' in str(e):
            raise
        print('  (next grid point rejected by the assembly, as required)')
    res = pcn.assembly(asb, pcn.AC, bridge, k1, beta=PHASE_STOP)
    assert len(res['strict_constraints']) == 47 and all(v > 0 for v in res['strict_constraints'].values())
    assert len(res['margins']) == 7
    print('PASS re-instantiated atom exponent: theta = 556349912/10^12,'
          ' kappa = 1111463/2000000000 =', '5.557315e-4 (next 10^-10 point rejected),'
          ' 47 constraints, 7 margins')
    print('gain: +2294 points of the 10^-10 grid over #157 (5555021/10^10)')
    print('PASS conditional re-instantiation; inherited interfaces remain assumptions')


if __name__ == '__main__':
    main()
