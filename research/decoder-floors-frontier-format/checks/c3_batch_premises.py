"""Finite premises of Theorem B / Bk (STRAYS-BATCH THEORY §1-§3): labels of P112 in F2^9, the 8 exceptional hyperplanes, the normals w_i with b(w_i,w_j) = 1,
rho(N(f_i), N(f_j)) = 8, the frame lemma E cap N(f_i) cap N(f_j) = empty, and an O(9) chart on which all 64 cross pairs of coordinate supports pair at rank 7
(the per-term floor 7 of Theorem B is attained, so the counting bound 120 is not the truth).  Standard library only; the chart is searched
with a fixed seed (random.Random(52)) and the found chart is shipped in data/chart_rank7.json, which is re-verified here."""
import sys, os, json, random, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from report import check, finish
from units import *

L = sub(P112_IDX); v = len(L); Br = b0rows(L); G = gram(L)
# dense B has rank 9; basis = first 9 independent rows
basis = []
for t in range(v):
    if rank_f2([Br[x] for x in basis + [t]]) == len(basis) + 1: basis.append(t)
    if len(basis) == 9: break
check('c3.rank', rank_f2(Br) == 9 and len(basis) == 9, 'P112 dense pairing has rank 9; basis lines %s' % basis)
combo = {}
for co in range(512):
    w = 0
    for i in range(9):
        if co >> i & 1: w ^= Br[basis[i]]
    combo.setdefault(w, co)
lab = [combo[Br[t]] for t in range(v)]                      # label of line t: coefficient vector (9-bit int) over the basis rows
Gb = [[Br[basis[i]] >> basis[j] & 1 for j in range(9)] for i in range(9)]
def bf(x, y):
    s = 0
    for i in range(9):
        if x >> i & 1:
            for j in range(9):
                if y >> j & 1: s ^= Gb[i][j]
    return s
check('c3.labels', all(bf(lab[t], lab[s]) == (Br[t] >> s & 1) for t in range(v) for s in range(v)), 'labels realise the dense pairing: b(lab_t, lab_s) = B_ts for all 112 x 112 pairs')
def hfun(h, x): return bin(h & x).count('1') & 1
live_of = [E8[i] for i in P112_IDX]
Of = []; N = []
for f in F0:
    Of.append(set(t for t in range(v) if dot(live_of[t], E8[f]) == 0)); N.append([t for t in range(v) if dot(live_of[t], E8[f]) != 0])
hyps = []
for Oset in Of:
    sols = [h for h in range(1, 512) if set(t for t in range(v) if hfun(h, lab[t])) == Oset]
    hyps.append(sols)
check('c3.hyps', all(len(s) == 1 for s in hyps), 'for each removed root f_i the class O_i = {live lines orthogonal to f_i} is the support of exactly one functional h_i on the label space')
W = []
for s in hyps:
    h = s[0]; ws = [w for w in range(512) if all(bf(w, 1 << j) == (h >> j & 1) for j in range(9))]
    W.append(ws[0] if len(ws) == 1 else None)
check('c3.normals', all(w is not None for w in W), 'the pairing is nondegenerate: each h_i = b(w_i, .) for a unique normal w_i')
check('c3.premiseP2a', all(bf(W[i], W[j]) == 1 for i in range(8) for j in range(8)), 'b(w_i, w_j) = 1 for all 64 ordered pairs, i = j included (every normal is non-isotropic, any two are non-orthogonal)')
rho = set(rank_f2([sum(1 << k for k, s in enumerate(N[j]) if Br[t] >> s & 1) for t in N[i]]) for i in range(8) for j in range(8))
check('c3.premiseP2b', rho == {8}, 'rho(E_i, E_j) = rank_F2 B[N(f_i), N(f_j)] = %s for all 64 ordered pairs' % sorted(rho))
# survivors (Gram-deficient classes) via Q-rank: label classes whose support has rank_Q < 8 ... equivalently the 8 hyperplanes O_i
surv = [h for h in range(1, 512) if rank_q([list(L[t]) for t in range(v) if hfun(h, lab[t])]) < 8]
check('c3.deficient', sorted(surv) == sorted(s[0] for s in hyps) and len(surv) == 8, 'the Gram-deficient label classes (support of rank_Q < 8) are exactly the 8 classes O_i')
check('c3.nosub2', not any((a ^ b) in set(surv) for a, b in itertools.combinations(surv, 2)), 'no two of them add up to a third: no 2-dimensional subspace among the 8 deficient classes')
# frame lemma for Theorem Bk: for every i < j some live 8-frame E has E cap N(f_i) cap N(f_j) = empty
adj = orth_graph(L); frames = [c for c in maximal_cliques(adj) if popcount(c) == 8]
Nm = [sum(1 << t for t in n) for n in N]
ok = all(any(E & Nm[i] & Nm[j] == 0 for E in frames) for i, j in itertools.combinations(range(8), 2))
check('c3.framelemma', ok and len(frames) == 1260, 'for every i < j (28 pairs) some one of the 1260 live 8-frames E has E cap N(f_i) cap N(f_j) = empty')
# O(9) charts: transvections x -> x + b(x, u) u (u isotropic) generate; Phi given by images of the 9 basis vectors
iso = [u for u in range(1, 512) if bf(u, u) == 0]
def tv(u, x): return x ^ (u if bf(x, u) else 0)
def compose(Phi, u): return [tv(u, x) for x in Phi]
def apply(Phi, x):
    y = 0
    for i in range(9):
        if x >> i & 1: y ^= Phi[i]
    return y
def orth_count(Phi): return sum(bf(W[i], apply(Phi, W[k])) == 0 for i in range(8) for k in range(8))
def is_isometry(Phi): return all(bf(apply(Phi, 1 << i), apply(Phi, 1 << j)) == bf(1 << i, 1 << j) for i in range(9) for j in range(9))
chart_file = os.path.join(HERE, '..', 'data', 'chart_rank7.json')
if not os.path.exists(chart_file):
    rng = random.Random(52); best = (0, None)
    for s in range(30000):
        Phi = [1 << i for i in range(9)]
        for _ in range(rng.randint(1, 40)): Phi = compose(Phi, rng.choice(iso))
        c = orth_count(Phi)
        if c > best[0]: best = (c, Phi)
        if c == 64: break
    json.dump(dict(orth_cross_pairs=best[0], Phi=best[1], note='images of the 9 label basis vectors (9-bit ints); found by random.Random(52) products of isotropic transvections'), open(chart_file, 'w'))
ch = json.load(open(chart_file)); Phi = ch['Phi']
check('c3.chart.isometry', is_isometry(Phi), 'the shipped chart Phi preserves the pairing b (Phi in O(9, F2))')
lab2 = [apply(Phi, x) for x in lab]
def span_cost(S, T_):
    return rank_f2([sum(bf(a, b) << k for k, b in enumerate(T_)) for a in S])
costs = set(span_cost([lab[t] for t in N[i]], [lab2[t] for t in N[k]]) for i in range(8) for k in range(8))
check('c3.chart.rank7', orth_count(Phi) == ch['orth_cross_pairs'] and costs == {7}, 'chart Phi: b(w_i, Phi w_k) = 0 for %d/64 (i,k) and all 64 cross pairs rho(call-1 support N(f_i), call-2 support N(f_k)) have F2-rank %s' % (orth_count(Phi), sorted(costs)))
same = set(span_cost([lab[t] for t in N[i]], [lab[t] for t in N[k]]) for i in range(8) for k in range(8))
check('c3.chart.same', same == {8}, 'within one call the same pairings have rank %s (so rank-7 terms are pure cross-call)' % sorted(same))
finish()
