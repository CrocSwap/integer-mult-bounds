"""E6, dense B, root-code decoders (factors in the scaled-Gram realisation's column/row space), any number of terms m.
Exact integer arithmetic, standard library only.
  (i)   deficient directions (27), pair-rank table (432 pairs of rank 5, 297 of rank 6), all 27 x 27 cross pairings nonzero,
        one deficient direction per deficient class, the bilinear-form space is 1-dimensional;
  (ii)  W(E6) is transitive on the 432 rank-5 pairs (orbit of one pair under the 36 reflections), so one pair may be fixed;
  (iii) exhaustive search for 7 rank-5 pairs containing pair 0 whose cross matrix Lambda_pq = <y_p, x_q> has rank one off the diagonal
        (the necessary condition of Lemma OC for m = T+1): node counts per size, and the rank test of the direction sets on every leaf.
Input arithmetic is integers only: rank-one is tested by cross-multiplication, never by floats."""
import sys, os, itertools, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from dirs import *

L, T = UNITS['E6']; Br = b0rows(L)
dmap = deficient_directions(L, T)
X = sorted(set(dmap.values()))
check('c4.dirs', len(dmap) == 27 and len(X) == 27, 'E6: 27 deficient classes, 27 distinct deficient directions, one direction per class (so delta = 1 for each)')
check('c4.nspace', bilinear_space_dim(L, T) == 1, 'E6: the space of bilinear forms N on V with r_t N r_s = 0 for all orthogonal t, s is 1-dimensional (spanned by the metric)')
supp = {x: support(L, x) for x in X}
rk = {(i, j): blk(Br, supp[X[i]], supp[X[j]]) for i in range(27) for j in range(27)}
from collections import Counter
cnt = Counter(rk.values())
check('c4.pairranks', dict(cnt) == {5: 432, 6: 297}, 'E6 deficient x deficient pair ranks (dense B): %s' % dict(sorted(cnt.items())))
nz = all(dot(X[i], X[j]) != 0 for i in range(27) for j in range(27))
check('c4.cross', nz, 'E6: <y,x> != 0 for all 27 x 27 pairs of deficient directions (the column directions are the same 27 lines as the row directions)')
P = sorted(k for k, r in rk.items() if r == 5); n = len(P)
check('c4.rank5', n == 432, 'E6: 432 rank-5 pairs')

# (ii) transitivity of W(E6) on the rank-5 pairs
idx = {x: i for i, x in enumerate(X)}
def act(r, i): return idx[reflect(X[i], r)]
seen = {P[0]}; fr = [P[0]]
while fr:
    nf = []
    for (i, j) in fr:
        for r in L:
            q = (act(r, i), act(r, j))
            if q not in seen: seen.add(q); nf.append(q)
    fr = nf
check('c4.transitive', seen == set(P), 'E6: the 36 reflections generate a single orbit on the 432 rank-5 pairs (so pair 0 may be fixed WLOG); orbit size %d' % len(seen))

# (iii) search.  Lam[p][q] = <y_p, x_q> with y_p = X[P[p][1]], x_q = X[P[q][0]]
Lam = [[dot(X[P[p][1]], X[P[q][0]]) for q in range(n)] for p in range(n)]
t0 = time.time()
def run():
    depth = Counter(); leaves = []
    for p in range(1, n):
        L0p = Lam[0][p]; Lp0 = Lam[p][0]
        for q in range(p + 1, n):
            L0q = Lam[0][q]; Lq0 = Lam[q][0]; Lpq = Lam[p][q]; Lqp = Lam[q][p]
            if L0p * Lpq * Lq0 != L0q * Lqp * Lp0: continue
            depth[3] += 1
            # a = (1, Lpq/L0q, Lqp/L0p), b = (Lp0 L0q/Lpq, L0p, L0q); candidate c > q must have a_c = L_ci/b_i (i in {0,p,q}) and b_c = L_ic/a_i
            cand = []
            for c in range(q + 1, n):
                Lc0 = Lam[c][0]; Lcp = Lam[c][p]; Lcq = Lam[c][q]
                if Lcp * L0q != Lcq * L0p: continue
                if Lc0 * Lpq * L0p != Lcp * Lp0 * L0q: continue
                L0c = Lam[0][c]
                if Lam[p][c] * L0q != L0c * Lpq: continue
                if Lam[q][c] * L0p != L0c * Lqp: continue
                cand.append(c)
            m = len(cand)
            if not m: continue
            # compatibility of candidates c < d: L_dc L_0p == L_dp L_0c and L_cd L_0p == L_cp L_0d
            adj = [0] * m
            for u in range(m):
                c = cand[u]
                for w in range(u + 1, m):
                    d = cand[w]
                    if Lam[d][c] * L0p == Lam[d][p] * Lam[0][c] and Lam[c][d] * L0p == Lam[c][p] * Lam[0][d]:
                        adj[u] |= 1 << w; adj[w] |= 1 << u
            def ext(S, size, cm):
                depth[size] += 1
                if size == 7: leaves.append(tuple(S)); return
                while cm:
                    low = cm & -cm; u = low.bit_length() - 1; cm ^= low
                    ext(S + [cand[u]], size + 1, cm & adj[u])
            # cliques of the compatibility graph, ordered increasingly
            for u in range(m):
                ext([0, p, q, cand[u]], 4, adj[u] & ~((1 << (u + 1)) - 1))
    return depth, leaves
depth, leaves = run()
exp = {3: 27250, 4: 206275, 5: 898460, 6: 2502409, 7: 5504660}
check('c4.nodes', dict(depth) == exp, 'E6 rank-one-off-diagonal sets containing pair 0, by size: %s (%.0f s)' % (dict(sorted(depth.items())), time.time() - t0))
rcache = {}
def rk6(vecs):
    key = tuple(sorted(set(vecs)))
    if key not in rcache: rcache[key] = rank_q([list(v) for v in key]) if len(key) >= 6 else len(key)
    return rcache[key]
ok = 0; dis = 0
for S in leaves:
    xs = [P[s][0] for s in S]; ys = [P[s][1] for s in S]
    if len(set(xs)) < 6 or len(set(ys)) < 6: continue
    dis += 1
    if rk6([X[i] for i in xs]) == 6 and rk6([X[j] for j in ys]) == 6: ok += 1
check('c4.noleaf', ok == 0 and dis == 0, 'E6: of %d candidate 7-sets, %d have >= 6 distinct row AND >= 6 distinct column directions, and %d have both direction sets of rank 6 (none: no 7-term decomposition from seven rank-5 pairs)' % (len(leaves), dis, ok))
finish()
