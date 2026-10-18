"""Y1: centre/cut facts for the 112-port content map M of the #656 word (rows Y1, O1 numerics).
Inputs: inputs/pr656-FULL-WORD.json.gz (root_lines R; M = exact replay of precondition-free A+B+cut)."""
import itertools
from fractions import Fraction as Q
import numpy as np
from common import *

d = jgz('pr656-FULL-WORD.json.gz')
R = np.array(d['root_lines'], float)
check('y1.R-shape', R.shape == (112, 8), str(R.shape))
# exact replay of A, B, cut
rows = {r: {r: Q(1)} for r in range(112)}
for ph in ('A', 'B', 'cut'):
    for o in d[ph]:
        if o[0] == 'add':
            t, s, q = o[1], o[2], Q(o[3], o[4])
            rt = rows.setdefault(t, {}); rs = rows.get(s, {})
            for j, x in list(rs.items()):
                z = rt.get(j, 0) + q * x
                if z: rt[j] = z
                else: rt.pop(j, None)
        else:
            t = o[1]; q = Q(o[2], o[3])
            rows[t] = {j: q * x for j, x in rows.get(t, {}).items()}
M = np.zeros((112, 112))
for t in range(112):
    for j, x in rows.get(112 + t, {}).items():
        M[t, j] = float(x)
check('y1.M-from-replay', np.linalg.matrix_rank(M) == 112 and all(abs(float(v) * 64 - round(float(v) * 64)) < 1e-9 for v in M.ravel()),
      'rank M 112, entries multiples of 1/64')
rk = lambda A: int(np.linalg.matrix_rank(A, tol=1e-8))
G = R.T @ R
check('y1.rank-G-8', rk(G) == 8)
res = {k: rk(M[:k, k:]) for k in (14, 28, 56, 84)}
check('y1.matched-cut-ranks-6-7-7-8', [res[k] for k in (14, 28, 56, 84)] == [6, 7, 7, 8], str(res))
rng = np.random.default_rng(1)
mx = 0
for _ in range(2000):
    p = rng.permutation(112)
    mx = max(mx, rk(M[np.ix_(p[:56], p[56:])]))
check('y1.random-bipartition-offdiag-rank-max-8', mx == 8, 'max over 2000 seeded random 56|56 splits (sample, not a bound)')
# blocks of 8 consecutive lines (equal octad support)
sup = [tuple(np.nonzero(R[i])[0]) for i in range(112)]
check('y1.blocks-are-8-consecutive-lines', all(sup[i] == sup[8 * (i // 8)] for i in range(112)) and len(set(sup)) == 14)
blocks = [list(range(8 * b, 8 * b + 8)) for b in range(14)]
cnt = {}
for S in itertools.combinations(range(1, 14), 6):
    A = [i for b in [0] + list(S) for i in blocks[b]]
    sa = set(A); B = [i for i in range(112) if i not in sa]
    r = max(rk(M[np.ix_(A, B)]), rk(M[np.ix_(B, A)]))
    cnt[r] = cnt.get(r, 0) + 1
check('y1.block-7|7-splits-rank8-in-1708-of-1716', cnt == {8: 1708, 7: 8}, str(cnt))
# the 8 exceptions are the coordinate splits (rows with R[:,j]==0 vs !=0), rank 7
ex = 0
for j in range(8):
    A = [i for i in range(112) if R[i, j] == 0]; B = [i for i in range(112) if R[i, j] != 0]
    ex += (len(A) == 56 and rk(M[np.ix_(A, B)]) == 7 and rk(M[np.ix_(B, A)]) == 7)
check('y1.exceptions-are-8-coordinate-splits-rank7', ex == 8, 'CAVEAT: rank 7 does occur at these 8 splits')
# F2 weights of the centre code
Ri = R.astype(int)
from collections import Counter
c = Counter(int(((Ri @ np.array([(x >> k) & 1 for k in range(8)])) % 2).sum()) for x in range(1, 256))
check('y1.centre-F2-weights-0:15,56:128,64:112', dict(c) == {0: 15, 56: 128, 64: 112}, str(dict(c)))
# real-valued support of centre combinations: sampled minimum (an upper bound on the true minimum)
rg = np.random.default_rng(1); best = 112
for _ in range(20000):
    S = rg.choice(112, 7, replace=False)
    u, s, vt = np.linalg.svd(R[S])
    if s[-1] < 1e-9: continue
    best = min(best, int((np.abs(R @ vt[-1]) > 1e-9).sum()))
check('y1.min-centre-support-sampled-53', best == 53, 'min over 20000 seeded 7-subsets; upper bound on the true min')
# root-system closure: rows plus the 8 lines 2e_i give 120 lines = E8 root system (240 roots); reflections close it
roots = [tuple(int(x) for x in r) for r in Ri] + [tuple(2 * int(i == j) for j in range(8)) for i in range(8)]
roots = set(roots) | {tuple(-x for x in r) for r in roots}
ok = len(roots) == 240 and all(sum(x * x for x in r) == 4 for r in roots)
if ok:
    rl = [np.array(r) for r in roots]
    for a in rl[:60]:
        for b in rl:
            if tuple(int(x) for x in (b - (2 * (a @ b) // 4) * a)) not in roots:
                ok = False
check('y1.rows+8 coordinate lines = E8 root system (240 roots, reflection-closed on 60 reflectors)', ok)
# strand/total rank: a weight-4 total from 4 different blocks adds +1 rank over the centres
rg = np.random.default_rng(0); allp = True
for _ in range(300):
    T = np.zeros(112)
    for b in rg.choice(14, 4, replace=False):
        T[8 * b + rg.integers(8)] = rg.choice([-1, 1])
    allp &= (rk(np.hstack([R, T[:, None]])) == 9)
check('y1.cross-block-weight4-total-adds-rank-1', allp, '300 seeded totals; support 4 << 53')
# Y2 (numeric part, B106): the 8 coordinate 56|56 splits of the Gram matrix RR^T
GG = R @ R.T; okk = True
for j in range(8):
    A = [i for i in range(112) if R[i, j] == 0]; B = [i for i in range(112) if R[i, j] != 0]
    okk &= (rk(GG[np.ix_(A, B)]), rk(GG[np.ix_(A, A)]), rk(GG[np.ix_(B, B)])) == (7, 7, 8)
check('y2.coordinate-splits-rank(G_AB,G_AA,G_BB)=(7,7,8)', okk, 'all 8 splits; whole-split schedule saves no decoder term (price argument RECORDED)')
done()
