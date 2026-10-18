"""The inherited pricing model (STRAYS/PRICE-P112-H10, as used by the author's cards): a P112 unit of total decoder cost c at label width h pays iff
X(112,c,h) >= base and roof(112,c,h) >= rb, where base/rb are the values of the dense unit (cost 64, h = 9).  X = the format-limit skeleton ceiling
(research/format-limits-corrected/scripts/skel.py + cert.py), roof = the L1 roof of research/complex-local-word-ceiling/ceiling.py (Colkitt).
Both are IMPORTED from the repository tree (sibling directories of this package; not copied) and pinned by sha256 in SOURCES.json.  The author's cards used byte-identical copies.
This model is RECORDED (inherited), not derived or audited here; checks/c5 only recomputes its numbers.  Standard library only."""
import os, sys
RES = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RES, 'format-limits-corrected', 'scripts'))
sys.path.insert(0, os.path.join(RES, 'complex-local-word-ceiling'))
from fractions import Fraction as Q
import ceiling as C
import skel

def roof(v, c, h, s=9, k=1):
    m = k + s * (h - k); q, r = divmod(c, 8)
    loc = {h - 1: Q(2 * v)}
    for rk, n in ((q + 1, r), (q, 8 - r)):
        if n: loc[rk] = loc.get(rk, 0) + n
    return float(C.ceiling(loc, m, 8 * v, s, c, grid=Q(1, 10 ** 12))[1])

def Xc(v, c, h):
    r = skel.X(9, h, 1, Q(c, v))
    return 0.0 if r is None else float(r['hi'])      # skel.X returns None when D <= 0 (no positive root): such a cost never pays

base = Xc(112, 64, 9); rb = roof(112, 64, 9)

def pays(c, h): return Xc(112, c, h) / base >= 1 and roof(112, c, h) / rb >= 1

def breakeven(h, hi=64):
    """largest cost c <= hi that pays at width h (None if none)"""
    for c in range(hi, 0, -1):
        if pays(c, h): return c
    return None
