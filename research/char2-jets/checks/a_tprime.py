"""Theorem T': cost(tied_min) >= 12 for every admissible B, by a first-order jet over F2((eps)) around the Fano collapse (Corollary J / Lemma VCR2).
Exact steps (integer / F2 arithmetic): (1) tied_min is no-wild with 12 harmonic lines; (2) the hand-formula jet X, Y (h = 1) satisfies (J1) on all incidences and (J2) on all lines,
and the eps-expansion of every product P~(t).Q~(s) = c0 + c1 eps + c2 eps^2 gives valuation >= 2 on incidences, 0/1 on diagonals (Lemma VCR2 hypothesis for every directed cycle);
(3) for the 518 stored matrices B: admissible, and rank N = rank (B o P~Q~^T) = 12 at a fixed eps in GF(2^16) (a specialisation: rank can only drop) -- a direct certificate cost(B) >= 12.
For the 217 optima the exact cost (sum of F2 block ranks) is also computed and must equal 12."""
import json, random
from common import *
from kit import *; from gr import mul, rank, Q as FQ; from phi import classify
P, Q = load_cfg('tied_min.json'); v = 12; R, A, free = setup(P, Q)
w, H = classify(P, Q)
report('T1 tied_min is no-wild, v=12, 72 incidences, all 12 lines harmonic', (w, len(H), len(free)) == (0, 12, 72), 'wild=%d |H|=%d f=%d' % (w, len(H), len(free)))
cls = [next(j for j in range(3) if q[j] == 0) for q in Q]
a0 = P[0]
def side(k, x):
    i, j = [y for y in range(3) if y != k]; q = [0, 0, 0]; q[i] = x[j]; q[j] = -x[i]; return q
def same(q1, q2): return all(q1[i] * q2[j] == q1[j] * q2[i] for i in range(3) for j in range(3))
G = lambda k, q: 0 if same(q, side(k, a0)) else 1
f = [[G(k, side(k, P[t])) for k in range(3)] for t in range(v)]
report('T2 f_0+f_1+f_2 = 0 at every point (sum-zero constraint)', all((f[t][0] ^ f[t][1] ^ f[t][2]) == 0 for t in range(v)))
X = [[f[t][1], f[t][0], 0] for t in range(v)]
g = [G(cls[s], Q[s]) for s in range(v)]
Y = []
for s in range(v):
    y = [0, 0, 0]; y[next(j for j in range(3) if j != cls[s])] = g[s]; Y.append(y)
phP = [[1 if x else 0 for x in p] for p in P]; phQ = [[1 if x else 0 for x in q] for q in Q]
d2 = lambda a, b: (a[0] & b[0]) ^ (a[1] & b[1]) ^ (a[2] & b[2])
report('T3 jet is support-compatible', all(all(X[t][j] == 0 for j in range(3) if P[t][j] == 0) and all(Y[t][j] == 0 for j in range(3) if Q[t][j] == 0) for t in range(v)))
c0 = lambda t, s: d2(phP[t], phQ[s]); c1 = lambda t, s: d2(phP[t], Y[s]) ^ d2(X[t], phQ[s])
report('T4 order 0: phi(p).phi(q) = 0 on all 72 incidences and on all 12 diagonals', all(c0(t, s) == 0 for (t, s) in free) and all(c0(t, t) == 0 for t in range(v)))
report('T5 (J1): order-1 coefficient 0 on all 72 incidences  => w_ts >= 2', all(c1(t, s) == 0 for (t, s) in free))
report('T6 (J2): order-1 coefficient 1 on all 12 diagonals  => w_tt = 1', all(c1(t, t) == 1 for t in range(v)))
vl = lambda t, s: 0 if c0(t, s) else (1 if c1(t, s) else 2)    # valuation (capped at 2) of P~(t).Q~(s) = c0 + c1 eps + c2 eps^2
emin = min(vl(t, s) for (t, s) in free); dmax = max(vl(t, t) for t in range(v))
report('T7 VCR2 hypothesis: min incidence valuation (%d) > max diagonal valuation (%d), so every directed cycle C has sum_edges w >= 2|C| > |C| >= sum_vertices w and all w_tt < inf' % (emin, dmax), emin >= 2 and dmax == 1 and all(vl(t, t) == 1 for t in range(v)))
d = json.load(open(PKG + '/data/tied_min_B.json'))
assert d['f'] == len(free)
random.seed(1); e = random.randrange(2, FQ)
Pt = [[phP[t][j] ^ mul(e, X[t][j]) for j in range(3)] for t in range(v)]; Qt = [[phQ[s][j] ^ mul(e, Y[s][j]) for j in range(3)] for s in range(v)]
dd = lambda a, b: mul(a[0], b[0]) ^ mul(a[1], b[1]) ^ mul(a[2], b[2])
M = [[dd(Pt[t], Qt[s]) for s in range(v)] for t in range(v)]
def check(gs, tag, exact_cost=None):
    ok = 0; adm = 0; ex = 0
    for gg in gs:
        B = tomat(gg, free, v)
        adm += all(B[t][t] == 1 for t in range(v)); 
        ok += rank([[M[t][s] if B[t][s] else 0 for s in range(v)] for t in range(v)]) == 12
        if exact_cost is not None: ex += sum(blockranks(B, R, A)) == exact_cost
    return ok, adm, ex
n = len(d['optima'])
ok, adm, ex = check(d['optima'], 'opt', 12)
report('T8 217 optima: admissible, exact cost = 12 (sum of F2 block ranks), rank N = 12', n == 217 and ok == n and adm == n and ex == n, '%d matrices, rank-12 %d, cost-12 %d' % (n, ok, ex))
ok, adm, ex = check([d['full']], 'full', None)
cf = sum(blockranks(tomat(d['full'], free, v), R, A))
report('T9 full B (all 72 incidences): rank N = 12 (exact cost of full B = %d >= 12)' % cf, ok == 1 and cf >= 12)
ok, adm, ex = check(d['random'], 'rnd', None)
cm = min(sum(blockranks(tomat(g_, free, v), R, A)) for g_ in d['random'])
report('T10 300 random admissible B: rank N = 12 for all (min exact cost among them = %d)' % cm, ok == 300 and cm >= 12, 'rank-12 %d/300' % ok)
done()
