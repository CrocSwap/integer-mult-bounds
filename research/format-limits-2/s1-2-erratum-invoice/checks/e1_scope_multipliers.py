"""E1 (erratum to #595): the x1.15-2.15 "schedule/rho family" multipliers of #595 A.7 are the effect of DROPPING idle-frame
rules from the scope, not a rho family.  Default (fast, two processes): recompute idlefree, idle_onechild and nosplit for
the two units with #595's own skel.X (vendored, inputs/pr595) and compare with the multipliers a5 prints.
E1_FULL=1: run #595's a5_scope_multipliers.py unchanged (all 7 variants, about 56 s)."""
import contextlib
import io
import os
import re
import runpy
import sys
from fractions import Fraction as Fr
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), 'inputs', 'pr595')
sys.path.insert(0, SRC)
S_LIST = (3, 5, 7, 9, 11, 13)
UNITS = {'cx-112/64': (9, 64, 112), 'bit-111/63': (8, 63, 111)}
EXP = {'cx-112/64': {'idlefree': (1.68, 2.15), 'idle_onechild': (1.20, 1.55), 'nosplit': (1.15, 1.18)},
       'bit-111/63': {'idlefree': (1.67, 2.14), 'idle_onechild': (1.19, 1.55), 'nosplit': (1.15, 1.18)}}


def roots(h, x, var):
    from skel import X
    out = {}
    for s in S_LIST:
        r = X(s, h, 1, x, var)
        out[s] = r['hi'] if r else Fr(0)
    return out


def unit(name):
    h, cst, v = UNITS[name]
    x = Fr(cst, v)
    base = roots(h, x, 'thm')
    res = {}
    for var in EXP[name]:
        rr = roots(h, x, var)
        res[var] = (float(max(rr.values()) / max(base.values())), float(rr[9] / base[9]), max(rr, key=rr.get))
    return name, res


def fast():
    with Pool(2) as p:
        out = dict(p.map(unit, list(UNITS)))
    fail = False
    for name in UNITS:
        for var, (best, at9, sb) in out[name].items():
            e = EXP[name][var]
            ok = abs(best - e[0]) <= 0.006 and abs(at9 - e[1]) <= 0.006
            fail |= not ok
            print('%s E1.%s.%s  best s=%d: x%.2f;  s = 9: x%.2f  (#595 A.7: x%.2f / x%.2f)'
                  % ('PASS' if ok else 'FAIL', name, var, sb, best, at9, e[0], e[1]), flush=True)
    return fail


def full():
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf):
        try:
            runpy.run_path(os.path.join(SRC, 'a5_scope_multipliers.py'), run_name='__main__')
        except SystemExit as e:
            code = e.code or 0
    lines = [l for l in buf.getvalue().splitlines() if l.startswith(('PASS', 'FAIL'))]
    bad = [l for l in lines if l.startswith('FAIL')]
    print('%s E1.a5-rerun  %d claim lines from #595 a5_scope_multipliers.py (all 7 variants, both units), %d FAIL'
          % ('PASS' if lines and not bad and not code else 'FAIL', len(lines), len(bad)))
    return bool(bad or code or not lines)


if __name__ == '__main__':
    sys.exit(1 if (full() if os.environ.get('E1_FULL') else fast()) else 0)
