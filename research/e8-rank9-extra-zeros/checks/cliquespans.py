# CHECK (exact, mod 2^61-1 ranks = lower bounds, upper bounds trivial): for every maximal clique K of the E8 non-orthogonality graph
# (one representative per W(E8)-orbit; orbits computed here by BFS under the 120 reflections and shown to exhaust all maximal cliques):
#  (S1-K)  r(O_u \ K) spans r_u^perp (rank 7) for every line u;
#  (S2-K)  r(O_u ∩ O_u' \ K) spans <r_u,r_u'>^perp (rank 6) for every pair u != u'.
import sys, itertools
sys.path.insert(0, sys.argv[1])
from fractions import Fraction as Fr
from e8lib import E, N, G, O
from modrank import rkp
R = [[Fr(x) for x in r] for r in E]
idx = {}
for i, r in enumerate(E): idx[tuple(r)] = i; idx[tuple(-x for x in r)] = i
def refl(rv):
    out = []
    for j in range(N):
        ip = sum(a * b for a, b in zip(E[j], rv))
        out.append(idx[tuple(v - ip * w for v, w in zip(E[j], rv))])
    return out
P = [refl(E[i]) for i in range(N)]
NB = [set(s for s in range(N) if s != u and G[u][s] != 0) for u in range(N)]
# all maximal cliques (Bron-Kerbosch with pivot)
out = []
def bk(Rs, Ps, Xs):
    if not Ps and not Xs: out.append(frozenset(Rs)); return
    piv = max(Ps | Xs, key=lambda v: len(NB[v] & Ps))
    for v in list(Ps - NB[piv]):
        bk(Rs | {v}, Ps & NB[v], Xs & NB[v]); Ps = Ps - {v}; Xs = Xs | {v}
bk(set(), set(range(N)), set())
allmax = set(out)
from collections import Counter
print('maximal cliques:', len(allmax), 'by size:', sorted(Counter(len(k) for k in allmax).items()))
reps = []; seen = set()
for K in sorted(allmax, key=lambda k: sorted(k)):
    if K in seen: continue
    orb = {K}; fr = [K]
    while fr:
        nf = []
        for C in fr:
            for p in P:
                D = frozenset(p[c] for c in C)
                if D not in orb: orb.add(D); nf.append(D)
        fr = nf
    assert orb <= allmax
    seen |= orb; reps.append(K)
    print('orbit rep size %d rank %d, orbit size %d' % (len(K), rkp([R[k] for k in K]), len(orb)))
assert seen == allmax
bad = 0
for K in reps:
    for u in range(N):
        if rkp([R[s] for s in O[u] if s not in K]) != 7: bad += 1; print('S1 fail', sorted(K), u)
    for u, v in itertools.combinations(range(N), 2):
        if rkp([R[s] for s in O[u] & O[v] if s not in K]) != 6: bad += 1; print('S2 fail', sorted(K), u, v)
print('S1-K/S2-K failures:', bad); print('PASS cliquespans' if bad == 0 else 'FAIL cliquespans')
