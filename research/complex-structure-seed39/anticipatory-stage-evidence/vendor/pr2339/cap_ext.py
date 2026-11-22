#!/usr/bin/env python3
"""Fixed-local-profile packing caps (exact intervals) for the T74 borrow words, using the merged
research/complex-local-word-ceiling/ceiling.py (Douglas Colkitt's interval engine lineage; see that package).

For a fixed per-call local paid profile, ceiling() bounds the complex saving a of ANY hosting, owner packing or
idle-remainder choice under PR1012's coverage law (m = 73, 896 families per nine-stage replica, centre 64): all
idle mass in (fractional) children of the largest allowed rank R.  The T74 supplier's maximum child is 48; R = 51
(the halving-guard maximum) is also reported.  The local profile used is the call-weighted average
(249 gauge44 + 417 extra calls) of the two words.  These are upper bounds, not attained savings.
Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0."""
import importlib.util
import os
import sys
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
spec = importlib.util.spec_from_file_location('ceiling', os.path.join(ROOT, 'research/complex-local-word-ceiling/ceiling.py'))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

PROFILES = {
    'pr2269_high43': ({1: 2351, 2: 501, 3: 414, 4: 129, 5: 42, 8: 8}, {1: 2339, 2: 509, 3: 418, 4: 125, 5: 42, 8: 8}),
    'ext80_this_package': ({1: 2303, 2: 527, 3: 386, 4: 125, 5: 37, 8: 8}, {1: 2287, 2: 535, 3: 386, 4: 125, 5: 37, 8: 8}),
}
CLAIMED_2269_B = Q('0.0016962471390584742207696225394800943861')


def avg(pg, pe):
    return {r: Q(249 * pg.get(r, 0) + 417 * pe.get(r, 0), 666) for r in set(pg) | set(pe)}


def main():
    caps = {}
    for R in (48, 51):
        for name, (pg, pe) in PROFILES.items():
            lo, hi = C.ceiling(avg(pg, pe), 73, 896, 9, 64, R=R)
            caps[(name, R)] = (lo, hi)
            print('R=%d %-20s cap in [%s, %s]' % (R, name, float(lo), float(hi)))
    lo69, hi69 = caps[('pr2269_high43', 48)]
    assert CLAIMED_2269_B < lo69, 'positive control: #2269 claimed b must lie below its own cap'
    lo80, hi80 = caps[('ext80_this_package', 48)]
    assert lo80 > hi69, 'the 80-alias cap must exceed the 43-alias cap'
    frac = CLAIMED_2269_B / hi69
    print('#2269 realised fraction of its R=48 cap >= %.6f' % float(frac))
    print('same fraction of the ext80 cap (estimate, not a bound): %.10f' % float(frac * lo80))
    print('PASS_T74_LOW_ALIAS_PACKING_CAPS cap48_high43=%.12f cap48_ext80=%.12f' % (float(hi69), float(lo80)))
    return 0


if __name__ == '__main__':
    if not __debug__:
        sys.exit('refusing to run with -O')
    sys.exit(main())
