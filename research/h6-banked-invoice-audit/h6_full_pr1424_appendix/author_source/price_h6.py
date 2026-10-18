"""Banked-invoice break-even helper counts R* for the E8^2 Pauli factor (the H6 row of PR1590 / our escape map).

Run from the repository root:  python3 -B research/h6-banked-breakeven/price_h6.py
Uses PR606's research/niemeier-lattices/workbench/paid-controller/banked.py unchanged (invoice(), lines 65-72).

Model (PR606 'complex' row inputs): n=30960 ports, h=17, hist={17:256, 15:560} (256 width-17 + 560 width-15 centres,
degree-3 K=(t^3-4t)/48 of rank 816), data path [16], helper path hp=[1,7,8,1] (17 rank of stock per helper),
virtual=False, L in {3,5,7} stages.  kappa(L,R) = lower end of invoice(...)['nominal_kappa_interval_scaled_1e18'].

Convention: R* = the largest R in [0, 2,000,000) with kappa(L,R) STRICTLY above the target, found by bisection on
the invariant kappa(lo) > target >= kappa(hi) (lo=0, hi=2,000,000).  Monotonicity in R is checked at the boundary
(kappa(R*) > target >= kappa(R*+1)) and printed.  Two comparison modes are reported:
  float : kappa_scaled/1e18 (Python float) > float(target)          -- the convention behind the published 80,558
  exact : kappa_scaled (int) > target * 1e18 (Fraction, exact)      -- no rounding
Targets are kept as the exact decimal strings below.  '#890 as used' is the 10-digit rounding we used in the escape
map; '#890 title' is PR890's merged title value; '#1424 title' is the open best at the time of writing (2026-10-14).

The 'x1.538 paper ceiling' is the ratio of two zero-helper nominal kappas in PR606's COSTS.txt (same model):
E8^2 full Pauli factor (.006945535353) / E8 root reference (.004515128332); see ceiling() below, which parses them.
It is a paper ceiling: no compensation helpers, no bit-side cap, no construction.

Not included in the invoice (necessary budget, not sufficient): K encoder beyond PR606's base terms, compensation
restoration/chronology (frame-0 precompensation, target cap-15 <-> FULL), spectator/padding beyond helper_pad,
sharing between compensation and other stages, and any helper-loading/capacity lemma.
"""
import sys, re, os
from fractions import Fraction as F
sys.dont_write_bytecode = True
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
NM = ROOT + '/research/niemeier-lattices'
sys.path.insert(0, NM + '/workbench/paid-controller')
import banked as b

N, H, HIST, DATA, HP = 30960, 17, {17: 256, 15: 560}, (16,), (1, 7, 8, 1)
TARGETS = {
    '#890 as used (rounded)': '0.001661957775',
    '#890 title (exact)':     '0.001661957774647029',
    '#1424 title (exact)':    '0.001676855229071321886206381217337893',
}
HI = 2_000_000

def kscaled(L, R):
    d = b.invoice(N, H, HIST, L, list(DATA), list(HP), R, False)
    return int(d['nominal_kappa_interval_scaled_1e18'][0])

def above(L, R, t, mode):
    s = kscaled(L, R)
    return (s / 1e18 > float(t)) if mode == 'float' else (F(s) > F(t) * 10**18)

def breakeven(L, t, mode):
    if not above(L, 0, t, mode): return 0
    lo, hi = 0, HI
    assert not above(L, hi, t, mode)
    while hi - lo > 1:
        m = (lo + hi) // 2
        if above(L, m, t, mode): lo = m
        else: hi = m
    return lo

def ceiling():
    txt = open(NM + '/COSTS.txt').read()
    e8 = re.search(r'E8 root reference\s+\d+\s+\d+\s+\d+\s+(\.\d+)', txt).group(1)
    pa = re.search(r'E8\^2 full Pauli factor\s+\d+\s+\d+\s+\d+\s+(\.\d+)', txt).group(1)
    return e8, pa, F(pa) / F(e8)

if __name__ == '__main__':
    e8, pa, r = ceiling()
    print('ceiling: E8^2 full Pauli %s / E8 root reference %s = %.6f  (COSTS.txt, zero helpers)' % (pa, e8, float(r)))
    print('model: n=%d h=%d hist=%s data=%s hp=%s virtual=False; bracket [0,%d); strict >' % (N, H, HIST, list(DATA), list(HP), HI))
    for name, t in TARGETS.items():
        for mode in ('float', 'exact'):
            row = []
            for L in (3, 5, 7):
                R = breakeven(L, t, mode)
                ok = above(L, R, t, mode) and not above(L, R + 1, t, mode)
                row.append('L%d R*=%d (30960/R*=%.4f, k(R*)=%d, k(R*+1)=%d, boundary %s)' % (
                    L, R, N / R if R else 0, kscaled(L, R), kscaled(L, R + 1), 'ok' if ok else 'NON-MONOTONE'))
            print('%-24s %-5s target=%s' % (name, mode, t)); [print('   ' + x) for x in row]
