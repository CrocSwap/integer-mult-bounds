"""Group G4: spot checks of the partial theorems and the two reductions (fprime/PROOF.md sections 7, 2, 13).  Exact arithmetic, fixed seeds.
 M1:   if every point has a zero coordinate, sum_j MAS(G[D_j]) >= sum_t c(t) >= v/2  (MAS = largest induced acyclic subgraph, exact subset DP in mas.c).
 U:    in the unit world (all nonzero entries odd) the explicit label/order scheme of Theorem U is a valid L8 certificate of size >= |G| + |I|/2 >= v/2.
 SCC:  every block is block upper triangular in a topological order of the strong components of H.
 Peel: |pi(t)| = 1 or |sigma(t)| = 1  =>  cost(config) >= cost(config - t) + 1  (exact, exhaustive over all B).
 Monotone: cost(S) <= cost(config) for every sub-configuration (exact)."""
import sys, os, json, random, itertools, subprocess
from math import comb
from fractions import Fraction as F
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from kit import *

def outs(P, Q):
    v = len(P); return [[s for s in range(v) if s != t and dot(P[t], Q[s]) == 0] for t in range(v)]
def mas(nodes, out):
    if not nodes: return 0
    idx = {t: i for i, t in enumerate(nodes)}
    o = [sum(1 << idx[s] for s in out[t] if s in idx) for t in nodes]
    return int(subprocess.run([os.path.join(BIN, 'mas')], input="%d\n" % len(nodes) + "\n".join(map(str, o)), capture_output=True, text=True, check=True).stdout)
def Dj(P, Q, j): return [t for t in range(len(P)) if P[t][j] and Q[t][j]]

# ---------------------------------------------------------------- Theorem M1
rng = random.Random(11); vals = (1, -1, 2, -2, 3, 0)
pts = [x for x in itertools.product(vals, repeat=3) if any(x) and 0 in x]; lns = [x for x in itertools.product(vals, repeat=3) if any(x)]
viol = 0; worst = F(9); ndone = 0; tight = 0
for it in range(80):
    v = rng.randrange(6, 15); P = []; Q = []
    while len(P) < v:
        if P and rng.random() < 0.85:
            s = rng.randrange(len(P)); t = rng.randrange(len(P))
            p = rng.choice([x for x in pts if dot(x, Q[s]) == 0] or pts); q = rng.choice([x for x in lns if dot(P[t], x) == 0] or lns)
        else: p = rng.choice(pts); q = rng.choice(lns)
        if dot(p, q): P.append(list(p)); Q.append(list(q))
    o = outs(P, Q); ms = sum(mas(Dj(P, Q, j), o) for j in range(3)); lb = F(0)
    for p, q in zip(P, Q):
        a = sum(1 for x in p if x) - 1; b = sum(1 for x in q if x) - 1; d = sum(1 for k in range(3) if p[k] and q[k])
        lb += F(d, comb(a + b, a))
    ndone += 1; viol += (ms < lb) or (lb < F(v, 2)); worst = min(worst, F(ms, v)); tight += (ms == lb)
print("M1 %d random configurations with every point having a zero coordinate (v 6-14): violations of MAS-sum >= sum_t c(t) >= v/2: %d; smallest MAS-sum/v %.3f; equality MAS-sum = sum c(t) in %d" % (ndone, viol, float(worst), tight))
# sharpness: private digon, p=(1,1,0) q=(1,0,1); p=(1,0,-1) q=(1,-1,0): MAS-sum 1 of v=2, and cost is 2
Pd = [[1, 1, 0], [1, 0, -1]]; Qd = [[1, 0, 1], [1, -1, 0]]
best, ms_, Rd, Ad, fd = enum(Pd, Qd)
lbd = sum(F(sum(1 for k in range(3) if p[k] and q[k]), comb(sum(1 for x in p if x) - 1 + sum(1 for x in q if x) - 1, sum(1 for x in p if x) - 1)) for p, q in zip(Pd, Qd))
print("M1 sharpness digon: v=2, sum_t c(t) = %s, MAS-sum %d, exact cost %d (so MAS-sum = v/2 is attained while cost = v)" % (lbd, sum(mas(Dj(Pd, Qd, j), outs(Pd, Qd)) for j in range(3)), best))

# ---------------------------------------------------------------- Theorem U
def supp(x): return sum(1 << k for k in range(3) if x[k] != 0)
par = lambda x: bin(x).count('1') & 1
def u_scheme(P, Q, special):
    v = len(P); c0, c1, c2 = [(special + r) % 3 for r in range(3)]
    a = [supp(P[t]) for t in range(v)]; b = [supp(Q[t]) for t in range(v)]
    G = []; cl = {}
    for t in range(v):
        Dd = a[t] & b[t]
        if bin(Dd).count('1') % 2: G.append(t); continue
        i, j = [k for k in range(3) if Dd >> k & 1]
        al = F(P[t][i], P[t][j]); be = F(-Q[t][j], Q[t][i]); assert al != be
        cl.setdefault((i, j), {True: [], False: []})[al < be].append((t, al, be))
    A1 = []; A2 = []; B1 = []; B2 = []; tiedtot = 0
    for (i, j), H in cl.items():
        tiedtot += len(H[True]) + len(H[False])
        h = max((True, False), key=lambda x: len(H[x])); L = H[h]
        L = sorted(L, key=lambda z: -z[1]) if h else sorted(L, key=lambda z: z[2]); T = [z[0] for z in L]; s = {i, j}
        if s == {c0, c2}:
            for t in T: a[t] &= ~(1 << c0)
            A2 += T
        elif s == {c0, c1}:
            for t in T: b[t] &= ~(1 << c0)
            B1 += T
        else:
            for t in T:
                if P[t][c0]: a[t] &= ~(1 << c2); A1.append(t)
                else: b[t] &= ~(1 << c2); B2.append(t)
    S = A1 + A2 + G + B1 + B2
    pos = {t: i for i, t in enumerate(S)}
    for t in S:
        assert a[t] & ~supp(P[t]) == 0 and b[t] & ~supp(Q[t]) == 0 and par(a[t] & b[t]) == 1
    for t in S:
        for s in S:
            if t != s and dot(P[t], Q[s]) == 0 and par(a[t] & b[s]): assert pos[t] < pos[s], 'conflict points backward'
    return len(S), len(G), tiedtot
P, Q = load_cfg('cex_min_1.json')
r = [u_scheme(P, Q, sp) for sp in range(3)]
print("U cex_min_1: certificate sizes for the three special coordinates %s (|S|, |G|, #tied); best %d of v = 19; all valid (checked inside)" % (r, max(x[0] for x in r)))
def prim():
    return [x for x in itertools.product((-1, 0, 1), repeat=3) if any(x) and next(c for c in x if c) > 0]
pr = prim(); pool = [(p, q) for p in pr for q in pr if dot(p, q)]
rp = [u_scheme([l[0] for l in pool], [l[1] for l in pool], sp) for sp in range(3)]
print("U 121-line pool: sizes %s; best %d of v = 121" % ([x[0] for x in rp], max(x[0] for x in rp)))
rng = random.Random(7); worst = 9; n = 0
for it in range(250):
    v = rng.randrange(4, 30); Pu = []; Qu = []
    while len(Pu) < v:
        p = [rng.choice((1, -1, 3, -3, 5, 0, 0)) for _ in range(3)]; q = [rng.choice((1, -1, 3, -3, 5, 0, 0)) for _ in range(3)]
        if any(p) and any(q) and dot(p, q): Pu.append(p); Qu.append(q)
    for _ in range(v):
        t, s = rng.randrange(len(Pu)), rng.randrange(len(Pu))
        cand = [(p, Qu[rng.randrange(len(Qu))]) for p in itertools.product((1, -1, 3, 0), repeat=3) if any(p) and dot(p, Qu[s]) == 0]
        cand = [(p, q) for p, q in cand if dot(p, q)]
        if cand: p, q = rng.choice(cand); Pu.append(list(p)); Qu.append(list(q))
    best = max(u_scheme(Pu, Qu, sp)[0] for sp in range(3)); worst = min(worst, best / len(Pu)); n += 1
print("U %d random unit-world configurations (4-60 lines, forced incidences): every scheme valid; smallest best-certificate/v = %.3f (>= 1/2: %s)" % (n, worst, worst >= 0.5))

# ---------------------------------------------------------------- Lemma SCC
def sccs(G):
    idx = {}; low = {}; st = []; on = set(); out = []; c = [0]
    sys.setrecursionlimit(10000)
    def dfs(u):
        idx[u] = low[u] = c[0]; c[0] += 1; st.append(u); on.add(u)
        for w in G[u]:
            if w not in idx: dfs(w); low[u] = min(low[u], low[w])
            elif w in on: low[u] = min(low[u], idx[w])
        if low[u] == idx[u]:
            comp = []
            while True:
                w = st.pop(); on.discard(w); comp.append(w)
                if w == u: break
            out.append(comp)
    for u in G:
        if u not in idx: dfs(u)
    return out[::-1]
def scc_check(P, Q):
    v = len(P)
    G = {t: [s for s in range(v) if s != t and dot(P[t], Q[s]) == 0 and any(P[t][k] and Q[s][k] for k in range(3))] for t in range(v)}
    C = sccs(G); comp = {t: i for i, cc in enumerate(C) for t in cc}
    for j in range(3):
        for t in range(v):
            if not P[t][j]: continue
            for s in range(v):
                if Q[s][j] and (t == s or dot(P[t], Q[s]) == 0):
                    if comp[t] > comp[s]: return None
    return sorted(len(c) for c in C)
rng = random.Random(1); vl = (-2, -1, 0, 1, 2); pool5 = [x for x in itertools.product(vl, repeat=3) if any(x)]; okc = 0; multi = 0
for it in range(300):
    v = rng.randrange(4, 16); Ps = []; Qs = []
    while len(Ps) < v:
        p = rng.choice(pool5); q = rng.choice(pool5)
        if dot(p, q): Ps.append(list(p)); Qs.append(list(q))
    r = scc_check(Ps, Qs); okc += r is not None; multi += (r is not None and len(r) > 1)
print("SCC block upper-triangularity in topological order of the strong components of H: %d of 300 random configurations (%d of them with more than one component)" % (okc, multi))
Pt, Qt = load_cfg('tied_min.json')
print("SCC component sizes: tied_min %s, cex_min_1 %s" % (scc_check(Pt, Qt), scc_check(P, Q)))

# ---------------------------------------------------------------- Lemma Peel and monotonicity (exact, exhaustive over all B)
def cost_of(P, Q):
    return enum(P, Q)[0]
rng = random.Random(4); vl = (-2, -1, 0, 1, 2); pool5 = [x for x in itertools.product(vl, repeat=3) if any(x)]
unit_p = [x for x in pool5 if sum(1 for c in x if c) == 1]; unit_q = unit_p
npeel = 0; viol = 0; nmono = 0; viol2 = 0; tried = 0
while npeel < 36 and tried < 3000:
    tried += 1; v = rng.randrange(4, 8); Ps = []; Qs = []
    while len(Ps) < v:
        if rng.random() < 0.9 and Ps:
            s = rng.randrange(len(Ps)); t = rng.randrange(len(Ps))
            p = rng.choice([x for x in pool5 if dot(x, Qs[s]) == 0] or pool5); q = rng.choice([x for x in pool5 if dot(Ps[t], x) == 0] or pool5)
        else: p = rng.choice(pool5); q = rng.choice(pool5)
        if dot(p, q): Ps.append(list(p)); Qs.append(list(q))
    # make line 0 a unit-support point (case |pi|=1) or unit-support line (|sigma|=1), keeping p.q != 0
    if npeel % 2 == 0:
        p = rng.choice(unit_p); q = rng.choice([x for x in pool5 if dot(p, x)])
    else:
        q = rng.choice(unit_q); p = rng.choice([x for x in pool5 if dot(x, q)])
    Ps[0] = list(p); Qs[0] = list(q)
    R, A, free = setup(Ps, Qs)
    if len(free) > 18: continue
    full = enum(Ps, Qs)[0]; rest = enum(Ps[1:], Qs[1:])[0]
    npeel += 1; viol += (full < rest + 1)
    nmono += 1; viol2 += (rest > full)
print("PEEL %d configurations with a unit-support point or line: exact cost(config) >= cost(config - t) + 1 violated in %d" % (npeel, viol))
print("MONO exact cost(sub-configuration) <= cost(config) violated in %d of %d" % (viol2, nmono))

# ---------------------------------------------------------------- Conjecture PP is false (S2): a lone line costs |D(t)|, so cost(S) >= cost(S-X) + |X| fails already at v = 2
Pt, Qt = load_cfg('tied_min.json')
single = [enum([Pt[t]], [Qt[t]])[0] for t in range(12)]
pair = enum([Pt[0], Pt[3]], [Qt[0], Qt[3]])[0]
def prop(a, b): return all(x == 0 for x in (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]))
dist = (not prop(Pt[0], Pt[3])) and (not prop(Qt[0], Qt[3]))
print("PP lone tied lines of tied_min cost %s; lines 0 and 3 (different point, different line: %s) together cost %d, so no group X of S = {0,3} satisfies cost(S) >= cost(S - X) + |X| (X = a single line: %d >= %d + 1 is false)" % (sorted(set(single)), dist, pair, pair, single[0]))
