"""Group G3: cex_min_1 (19 lines in {-1,0,1}^3): Conjecture F is false for the one-copy certificate, and the multi-copy certificate (MCC, Lemma MC)
reaches 20 >= v.  VERIFICATION of the stored certificate only (the CP-SAT solve is not repeated), plus the {-1,0,1} parity lemmas."""
import sys, os, json, ast, random, itertools, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from kit import *

P, Q = load_cfg('cex_min_1.json'); v = len(P)
pi = [frozenset(k for k in range(3) if p[k]) for p in P]; sg = [frozenset(k for k in range(3) if q[k]) for q in Q]
Dt = [pi[t] & sg[t] for t in range(v)]
types = collections.Counter(tuple(sorted(d)) for d in Dt)
print("CX v=%d entries in {-1,0,1}: %s; |D(t)| odd for %d lines (set G), even (=2, tied) for %d" % (
    v, all(abs(x) <= 1 for l in P + Q for x in l), sum(1 for d in Dt if len(d) % 2), sum(1 for d in Dt if len(d) % 2 == 0)))
print("CX D-types %s" % dict(sorted(types.items())))
inc = lambda t, s: t != s and dot(P[t], Q[s]) == 0
print("CX Lemma 1.1: every incidence t->s has |pi(t) & sigma(s)| in {0,2}: %s (%d incidences)" % (
    all(len(pi[t] & sg[s]) in (0, 2) for t in range(v) for s in range(v) if inc(t, s)), sum(1 for t in range(v) for s in range(v) if inc(t, s))))
# Lemma 1.2: tied lines with the same D and the same eps are never incident
eps = {}
for t in range(v):
    if len(Dt[t]) == 2:
        i, j = sorted(Dt[t]); eps[t] = (i, j, P[t][i] * P[t][j])
print("CX Lemma 1.2: tied lines of the same (D, eps) are never incident: %s (%d classes)" % (
    all(not inc(t, s) for t in eps for s in eps if t != s and eps[t] == eps[s]), len(set(eps.values()))))

# multi-copy certificate
raw = json.load(open(os.path.join(DATA, 'mcc_cex_min_1_solution.json')))
sol = {ast.literal_eval(k): (set(a), set(b), pos) for k, (a, b, pos) in raw.items()}
def verify_mcc(sol):
    for (t, c), (a, b, p) in sol.items():
        if not (a <= pi[t] and b <= sg[t] and len(a & b) % 2 == 1): return False
    for (t, c), (a, _, p) in sol.items():
        for (s, d), (_, b, q) in sol.items():
            if (t, c) == (s, d): continue
            if (t != s and inc(t, s)) or t == s:
                if len(a & b) % 2 and not p < q: return False
    return True
print("CX MCC: stored solution has %d copies on %d lines (up to %d per line); labels inside supports, odd diagonals, every odd entry on an incidence or same-line pair forward: %s" % (
    len(sol), len({t for t, _ in sol}), max(collections.Counter(t for t, _ in sol).values()), verify_mcc(sol)))
print("CX MCC: %d copies >= v = %d: %s" % (len(sol), v, len(sol) >= v))
# the identity behind Lemma MC on random admissible B: N is unit upper triangular in the order, rank N = #copies <= sum_j r_j
rng = random.Random(5); R, A, free = setup(P, Q); order = sorted(sol, key=lambda k: sol[k][2]); ok = 0; mincost = 99; tri = 0
for it in range(60):
    g = rng.getrandbits(len(free)) & rng.getrandbits(len(free)) if it else 0
    B = tomat(g, free, v); br = blockranks(B, R, A)
    N = [[(B[x[0]][y[0]] * (len(sol[x][0] & sol[y][1]) % 2)) % 2 for y in order] for x in order]
    up = all(N[i][i] == 1 and all(N[i][j] == 0 for j in range(i)) for i in range(len(order)))
    tri += up; ok += (sum(br) >= len(sol)); mincost = min(mincost, sum(br))
print("CX Lemma MC on 60 admissible B (incl. B = I): N unit upper triangular for %d of 60; sum_j rank B_j >= %d for %d of 60 (smallest sum seen %d)" % (tri, len(sol), ok, mincost))
# stored B of cost 22 (costsat2 at K = 22)
B22 = json.load(open(os.path.join(DATA, 'cex_min_1.json.B22.json')))
adm = all(B22[t][t] == 1 and all(B22[t][s] == 0 or inc(t, s) for s in range(v) if s != t) for t in range(v))
print("CX stored B of cost <= 22: admissible %s; block ranks %s sum %d; so 20 <= cost(cex_min_1) <= 22" % (adm, blockranks(B22, R, A), sum(blockranks(B22, R, A))))

# 121-line pool: Lemma 1.1 for all pairs
def prim():
    out = []
    for x in itertools.product((-1, 0, 1), repeat=3):
        if any(x) and next(c for c in x if c) > 0: out.append(x)
    return out
pr = prim(); pool = [(p, q) for p in pr for q in pr if dot(p, q)]
ok11 = all(len({k for k in range(3) if p[k]} & {k for k in range(3) if q2[k]}) % 2 == 0 for (p, q) in pool for (p2, q2) in pool if (p, q) != (p2, q2) and dot(p, q2) == 0)
print("CX pool: %d primitive pairs (p,q) in {-1,0,1}^3 with p.q != 0 (13 vectors up to sign); Lemma 1.1 on all incidences of the pool: %s" % (len(pool), ok11))
