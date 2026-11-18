# AUDIT-JR3 aud_cert.py: independent exact re-check of the JR3 Lagrangian certificate. Own code (not jr_lag/jr_lagx).
# Model: chain k = pair (z,z'), w[t]=G[t,z], u[s]=G[s,z'], g=G[z,z']. Flag S_0=<z'> < ... < S_7 = z^perp (subspaces as element sets).
# tau(t) = first i with q_t in S_i (inf if never); sigma(s) = last i with q_s perp S_i (-1 if none). Live_k(t,s) iff tau > gather <= sigma.
# J = #even off-diagonal cells with sum_{k live} w u / g != 0.  Weak duality for any lam >= 0 (keys only (c,k), k in K(c)):
#   J >= sum_k min_{flag} sum_c lam_ck [tau_k(t) > sigma_k(s)]  +  sum_c min_{L subset K(c)} (f_c(L) - sum_{k in L} lam_ck).
# Chain min: DP over ALL subspaces of z^perp containing z' (element-set representation), integer-scaled exact weights;
# includes the boundary terms (sigma=-1 symbols, tau=inf readers) generically. Usage: aud_cert.py CFG LAM.pkl
import sys, os, pickle, math
from fractions import Fraction as Fr
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import geo
G = geo.G120; U = geo.U; n = 104; Q = [U[t] for t in range(n)]
par = lambda a: bin(a).count('1') & 1
cfgs = [c for c in pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'f1cfgs.pkl'), 'rb'))
        if all(par(U[z] & U[zp]) == 0 for z, zp in c)]
assert len(cfgs) == 8
ci = int(sys.argv[1]); lam = pickle.load(open(sys.argv[2], 'rb'))
cfg = cfgs[ci]
CH = []
for z, zp in cfg:
    w = [int(G[t, z]) for t in range(n)]; u = [int(G[s, zp]) for s in range(n)]; g = int(G[z, zp]); assert g != 0
    CH.append((U[z], U[zp], w, u, g))
EVEN = [(t, s) for t in range(n) for s in range(n) if t != s and not par(Q[t] & Q[s])]
K = {c: [k for k in range(8) if CH[k][2][c[0]] and CH[k][3][c[1]]] for c in EVEN}
# --- lam sanity: nonneg, keys only on (even cell, contributing chain)
bad = [key for key in lam if key[0] not in K or key[1] not in K[key[0]]]
neg = [key for key, v in lam.items() if v < 0]
print('cfg', ci, 'lam keys', len(lam), 'bad keys', len(bad), 'neg', len(neg), 'expected keys', sum(len(v) for v in K.values()), flush=True)
assert not neg
L = lambda c, k: Fr(lam.get((c, k), 0)) if (c in K and k in K[c]) else Fr(0)
# --- local part
loc = Fr(0)
for c in EVEN:
    ks = K[c]; t, s = c
    vals = [Fr(CH[k][2][t] * CH[k][3][s], CH[k][4]) for k in ks]
    best = None
    for m in range(1 << len(ks)):
        f = 1 if sum((vals[i] for i in range(len(ks)) if m >> i & 1), Fr(0)) != 0 else 0
        v = f - sum((L(c, ks[i]) for i in range(len(ks)) if m >> i & 1), Fr(0))
        if best is None or v < best: best = v
    loc += best
# --- chain part
def span_add(S, v):           # S: frozenset of elements (a subspace); returns S + <v>
    return frozenset(S | {x ^ v for x in S})
tot = Fr(0)
for k in range(8):
    z, zp, w, u, g = CH[k]
    W = {}
    for c in EVEN:
        x = L(c, k)
        if x > 0: W[c] = x
    if not W: print('chain', k, 'min 0', flush=True); continue
    D = 1
    for x in W.values(): D = D * x.denominator // math.gcd(D, x.denominator)
    Wi = {c: int(x * D) for c, x in W.items()}
    col = {}
    for (t, s), x in Wi.items(): col.setdefault(s, []).append((t, x))
    zperp = [v for v in range(512) if not par(v & z)]
    assert not par(zp & z)
    def legal(S): return frozenset(s for s in col if all(not par(Q[s] & x) for x in S))
    def arr(S): return frozenset(t for t in range(n) if Q[t] in S)
    S0 = frozenset({0, zp})
    base = sum(x for s in col if s not in legal(S0) for (t, x) in col[s])   # sigma = -1: always live
    layer = {S0: base}; cache = {S0: (legal(S0), arr(S0))}
    for d in range(7):
        nxt = {}
        for S, cst in layer.items():
            lg, ar = cache[S]; done = set()
            for v in zperp:
                if v in S or v in done: continue
                S2 = span_add(S, v); done |= S2
                if S2 not in cache: cache[S2] = (legal(S2), arr(S2))
                lg2 = cache[S2][0]
                e = sum(x for s in lg - lg2 for (t, x) in col[s] if t not in ar)
                if S2 not in nxt or cst + e < nxt[S2]: nxt[S2] = cst + e
        layer = nxt
    assert len(layer) == 1
    (Sf, cst), = layer.items(); assert len(Sf) == 256
    lg, ar = cache[Sf]
    cst += sum(x for s in lg for (t, x) in col[s] if t not in ar)            # sigma = 7, tau = inf
    m = Fr(cst, D); tot += m
    print('chain', k, 'nodes-last', len(cache), 'min', float(m), flush=True)
LB = tot + loc
print('cfg', ci, 'chain', float(tot), 'local', float(loc), 'EXACT LB', LB.numerator, '/', LB.denominator, '=', float(LB), '>=4165.98:', LB >= Fr(416598, 100))
