# MASK9 common setup (from cnt4.py). Original header follows.
# MASK9 case (b), one big term. Term 0 has row-deficiency space Z_0 (dim d0 >= 2); small terms (d = 1, non-survivor class c, tau = 1) number
# k >= max(2, 9 - d0) (Σσ >= 9, σ_0 <= d0 - 1 + τ_0 <= d0, small σ = 1). For a subspace Z ⊆ Z_0 (dim 2 or 3, orbit reps under Aut(P112)) we
# compute the max size of a set K of small classes with: distinct survivors (matching), and for every J ⊆ K (|J| >= 1):
#   lb(C(Z) ∩ ∩_{c∈J} O_c) <= 9 - (|J| + 1)   (J ∪ {0}: masked terms),   and for |J| >= 2: lb(∩_{c∈J} O_c) <= 9 - |J|.
# Monotone (C(Z) ⊆ C(Z_0)), so a bound for Z bounds every Z_0 ⊇ Z.  usage: cnt4.py UNIT DIM [first last]
import sys, pickle, time, random, itertools, numpy as np
from setup9 import *
from common2 import B0rows, rank_f2
unit = sys.argv[1]
L, v, G, frames, nbar, h, basis, cls = load(unit)
full = (1 << v) - 1; ks = sorted(cls); B0 = B0rows(L)
FR = np.array([[F >> t & 1 for t in range(v)] for F in frames], dtype=np.float32)
NB = np.array([[nbar[t] >> s & 1 for s in range(v)] for t in range(v)], dtype=np.float32)
def tobits(x): return np.array([x >> t & 1 for t in range(v)], dtype=bool)
def minS(Xs):
    S = FR[None, :, :] * (~Xs)[:, None, :]
    while True:
        Wg = ((S @ NB) > 0).all(axis=1)
        S2 = S * Wg[:, None, :]
        if np.array_equal(S2, S): break
        S = S2
    return S.sum(axis=2).min(axis=1).astype(int)
random.seed(4)
smp = [cls[random.choice(ks)] & cls[random.choice(ks)] | cls[random.choice(ks)] & cls[random.choice(ks)] for _ in range(60)]
assert list(minS(np.array([tobits(x) for x in smp]))) == [min(pc(s) for s in propagate(x, frames, nbar, v)) for x in smp]
lbc = {}
def lb(X):
    if X not in lbc: lbc[X] = 8 - int(minS(tobits(X)[None, :])[0])
    return lbc[X]
def rk(R, A):
    Rl = [t for t in range(v) if R >> t & 1]; Al = [s for s in range(v) if A >> s & 1]
    return rank_f2([sum(1 << i for i, s in enumerate(Al) if B0[t] >> s & 1) for t in Rl])
surv = [c for c in ks if lb(cls[c]) < 8]
NS = [c for c in ks if c not in surv and cls[c] != full]
tauS = {c: [s for s in surv if rk(full ^ cls[c], full ^ cls[s]) == 7] for c in NS}
small = [c for c in NS if tauS[c]]
PD = pickle.load(open(f'pairs_{unit}.pkl', 'rb')); assert PD['cls'] == cls
sm = set(small); adj = {c: set() for c in small}
for a, b in PD['unc']:
    if a != b and a in sm and b in sm: adj[a].add(b); adj[b].add(a)
def matchable(K):
    m = {}
    def aug(c, seen):
        for s in tauS[c]:
            if s in seen: continue
            seen.add(s)
            if s not in m or aug(m[s], seen): m[s] = c; return True
        return False
    return all(aug(c, set()) for c in K)
def C(Z):
    x = 0
    for c in Z: x |= cls[c]
    return x
D = pickle.load(open(f'orbits_{unit}.pkl' if unit == 'P112' else f'orbits_{unit}.pkl', 'rb'))
inv = {cls[c]: c for c in cls}
def img(O, p):
    r = 0
    for t in range(v):
        if O >> t & 1: r |= 1 << p[t]
    return r
cpa = [np.array([0] + [inv[img(cls[c], p)] for c in range(1, 1 << h)]) for p in D['perms']]
def span(gs):
    S = {0}
    for g in gs: S |= {x ^ g for x in S}
    return tuple(sorted(S - {0}))
