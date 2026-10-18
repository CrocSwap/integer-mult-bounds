"""Free terms and the 120-line frame unit.  A decoder of the unit 'all 120 lines pairwise orthogonal' (so M = I is allowed and every
off-diagonal entry of B may be 1) with the E8 dense pairing B = J + Abar_E8 has exact cost 72 (8 coordinate terms of rank 9, 6720 free
single-entry terms of rank 0).  Exact Fractions; standard library only."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from fractions import Fraction as Fr
from roots import *

L = E8; v = len(L); Gd = gram(L)                  # doubled coordinates: real inner product = Gd/4, real coordinates = L/2
Br = b0rows(L)
real = lambda t, j: Fr(L[t][j], 2)
Greal = lambda t, s: Fr(Gd[t][s], 4)
terms = []                                        # (p, q) as dicts
for j in range(8):
    p = {t: real(t, j) / 2 for t in range(v) if L[t][j] != 0}
    q = {t: real(t, j) for t in range(v) if L[t][j] != 0}
    terms.append((p, q))
nfree = 0
for t in range(v):
    for s in range(v):
        if t != s and Gd[t][s] != 0:
            terms.append(({t: -Greal(t, s) / 2}, {s: Fr(1)})); nfree += 1
M = {}
for p, q in terms:
    for t, a in p.items():
        for s, b in q.items(): M[t, s] = M.get((t, s), 0) + a * b
isI = all(M.get((t, s), 0) == int(t == s) for t in range(v) for s in range(v))
check('c2.M_is_I', isI, 'E8 coordinate terms (p_j = R_j/2, q_j = R_j) plus %d free single-entry terms sum to M = I_120 exactly (%d terms)' % (nfree, len(terms)))
ranks = [blk(Br, sorted(p), sorted(q)) for p, q in terms]
paid = [r for r in ranks if r]
check('c2.cost72', sum(ranks) == 72 and paid == [9] * 8 and nfree == 6720 and all(r == 0 for r in ranks[8:]),
      'B = J + Abar_E8: the 8 coordinate terms have F2-rank 9 each, the %d free terms have rank 0; total cost %d < 120 = v (M = I, unit diagonal)' % (nfree, sum(ranks)))
# B fits the frame unit: B_tt = 1 and B_ts = 1 only where allowed -- in the frame unit every pair is orthogonal, so every B with unit diagonal fits
check('c2.fits', all(Br[t] >> t & 1 for t in range(v)), 'B has unit diagonal; the frame unit allows any off-diagonal B (all 120 lines pairwise orthogonal)')
finish()
