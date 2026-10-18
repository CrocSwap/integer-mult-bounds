"""STRAYS-MASK finite inputs (standard library only): (1) #1180's nine-term outside-col-M identity on P112 costs exactly 65 under the dense B (and the
removed-frame decoder it merges into costs 64); (2) all 120 co-star dead sets V \\ S_alpha are certified spanning in every rank-8 realisation (Lemma 1.1),
so every nine-term masked co-star decoder is a square biorthogonal decoder of a rank-9 realisation; (3) every survivor class contains an orthogonal 7-clique."""
import sys, os, itertools
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from report import check, finish
from units import *
from supprop import setup, propagate, census

L = sub(P112_IDX); v = len(L); Br = b0rows(L); G = gram(L)
sup = lambda col: [t for t in range(v) if col[t] != 0]
R = [[dot(r, E8[f]) for r in L] for f in F0]                      # coordinates in the removed-frame basis
base = [blk(Br, sup(R[j]), sup(R[j])) for j in range(8)]
check('c4.coordinate', base == [8] * 8, 'removed-frame coordinate decoder: term ranks %s, total %d' % (base, sum(base)))
def identity_scale(D, T):
    c = sum(D[0][k] * T[0][k] for k in range(len(D[0]))); c0 = G[0][0]
    return c // c0 if c0 and c % c0 == 0 and all(sum(D[a][k] * T[b][k] for k in range(len(D[0]))) == (c // c0) * G[a][b] for a in range(v) for b in range(v)) else None
for name, zval in (('z = e_line0 (value 1, #1180)', 1), ('z chosen to kill line 0 in term 1', -R[0][0])):
    z = [zval if t == 0 else 0 for t in range(v)]
    t1 = [R[0][t] + z[t] for t in range(v)]
    terms = [(sup(t1), sup(R[0]))] + [(sup(R[j]), sup(R[j])) for j in range(1, 8)] + [(sup(z), sup(R[0]))]
    rk = [blk(Br, a, b) for a, b in terms]
    D = [[t1[t]] + [R[j][t] for j in range(1, 8)] + [-z[t]] for t in range(v)]
    T = [[R[0][t]] + [R[j][t] for j in range(1, 8)] + [R[0][t]] for t in range(v)]
    sc = identity_scale(D, T)
    if zval == 1:
        check('c4.ex1180', sc is not None and rk == [8] * 8 + [1] and sum(rk) == 65, '#1180 nine-term identity (%s): D T^T = %s x Gram exactly on all 112 x 112 entries; term ranks %s, total %d' % (name, sc, rk, sum(rk)))
    else:
        print('   info: %s -> identity scale %s, term ranks %s, total %d' % (name, sc, rk, sum(rk)))
        check('c4.ex1180.alt', sc is not None and sum(rk) >= 64, 'variant %s: exact identity and total %d >= 64' % (name, sum(rk)))
# the two outside-col-M terms of #1180 share one column vector R_0: they merge into the removed-frame term
# (co-star theorem) all 120 dead sets are certified spanning
v_, frames, nbar = setup(L, 8); full = (1 << v) - 1
res = []
for a in range(120):
    S = sum(1 << t for t in range(v) if dot(L[t], E8[a]) == 0 or P112_IDX[t] == a)
    dead = full & ~S
    res.append((a in set(F0), popcount(S), min(popcount(s) for s in propagate(dead, frames, nbar)) == 0))
cnt = Counter(res)
check('c4.costar', cnt == Counter({(False, 60, True): 112, (True, 56, True): 8}), 'all 120 co-star dead sets V \\ S_alpha are certified spanning in every rank-8 realisation: %s (alpha in F0, |S_alpha|, certified): count' % dict(cnt))
# survivor classes: max orthogonal clique 7
unc = census(L, 8)['unc']
og = orth_graph(L)
w = set()
for _, O in unc:
    adj = [og[t] & O if O >> t & 1 else 0 for t in range(v)]
    w.add(max(popcount(c) for c in maximal_cliques(adj) if c & O == c and c))
check('c4.survclique', w == {7}, 'each of the 8 survivor classes contains an orthogonal 7-clique and no orthogonal 8-clique (so the killing functional is unique up to scale in every rank-8 realisation): %s' % sorted(w))
finish()
