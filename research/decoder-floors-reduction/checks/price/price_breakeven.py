"""K6 break-even prices (README section 5): largest per-line cost c at which the P112 unit (v = 112 lines) at label height h still has
both the skeleton ceiling X and the c1240 roof ratio >= 1 against the h = 9, c = 64 base.  Model code: skel.py, cert.py, c1240_ceiling.py
(shipped unchanged next to this file; standard library only).  Expected: h = 11, 12, 13, 14 -> 55, 51, 46, 42."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Q
import c1240_ceiling as C, skel
def roof(v, c, h, s=9, k=1):
    m = k + s * (h - k); q, r = divmod(c, 8)
    loc = {h - 1: Q(2 * v)}
    for rk, n in ((q + 1, r), (q, 8 - r)):
        if n: loc[rk] = loc.get(rk, 0) + n
    return float(C.ceiling(loc, m, 8 * v, s, c, grid=Q(1, 10 ** 12))[1])
def Xc(v, c, h): return float(skel.X(9, h, 1, Q(c, v))['hi'])
base = Xc(112, 64, 9); rb = roof(112, 64, 9)
for h in (11, 12, 13, 14):
    best = None
    for c in range(60, 30, -1):
        if Xc(112, c, h) / base >= 1 and roof(112, c, h) / rb >= 1: best = c; break
    print('h', h, 'break-even (both >= 1):', best, flush=True)
