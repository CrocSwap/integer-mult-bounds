# MASK9 case (b), one big term. Term 0 has row-deficiency space Z_0 (dim d0 >= 2); small terms (d = 1, non-survivor class c, tau = 1) number
# k >= max(2, 9 - d0) (Σσ >= 9, σ_0 <= d0 - 1 + τ_0 <= d0, small σ = 1). For a subspace Z ⊆ Z_0 (dim 2 or 3, orbit reps under Aut(P112)) we
# compute the max size of a set K of small classes with: distinct survivors (matching), and for every J ⊆ K (|J| >= 1):
#   lb(C(Z) ∩ ∩_{c∈J} O_c) <= 9 - (|J| + 1)   (J ∪ {0}: masked terms),   and for |J| >= 2: lb(∩_{c∈J} O_c) <= 9 - |J|.
# Monotone (C(Z) ⊆ C(Z_0)), so a bound for Z bounds every Z_0 ⊇ Z.  usage: cnt4.py UNIT DIM [first last]
import sys, pickle, time, random, itertools, numpy as np
from setup9 import *
from common2 import B0rows, rank_f2
unit = sys.argv[1]; DIM = int(sys.argv[2])
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
D = pickle.load(open(f'orbits_{unit}.pkl', 'rb'))
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
# subspaces of dimension DIM (DIM = 2 or 3), orbit reps under the full generator set
if DIM == 2:
    subs = sorted({span((a, b)) for a in ks for b in ks if a < b})
else:
    s2 = sorted({span((a, b)) for a in ks for b in ks if a < b})
    subs = sorted({span((W[0], W[1], d)) for W in s2 for d in ks if d not in W})
print('subspaces dim', DIM, len(subs), flush=True)
gb = cpa if DIM == 2 else random.Random(7).sample(cpa, 12)   # subgroup for dim 3 (sound: a subgroup only adds reps)
seen = set(); reps = []
for Z in subs:
    if Z in seen: continue
    reps.append(Z); seen.add(Z); st = [Z]
    while st:
        x = st.pop()
        for g in gb:
            y = tuple(sorted(int(g[c]) for c in x))
            if y not in seen: seen.add(y); st.append(y)
print('orbit reps', len(reps), flush=True)
need = max(2, 9 - DIM)   # the weakest requirement among d0 >= DIM is max(2, 9 - d0); we report the max k so each d0 can be read off
t0 = time.time(); out = {}
for ri, Z in enumerate(reps):
    X0 = C(Z)
    if X0 == full: out[Z] = (-1, None); continue
    cand = [c for c in small if lb(X0 & cls[c]) <= 7]
    best = [0, ()]
    def ok_add(K, x):
        for r in range(0, len(K) + 1):
            for J in itertools.combinations(K, r):
                X = cls[x]
                for c in J: X &= cls[c]
                if r >= 1 and lb(X) > 9 - (r + 1): return False
                if lb(X0 & X) > 9 - (r + 2): return False
        return True
    def dfs(K, cs):
        if len(K) > best[0]: best[0] = len(K); best[1] = tuple(K)
        for i, x in enumerate(cs):
            if len(K) + 1 + len(cs) - i - 1 <= best[0] and best[0] >= 8: break
            if ok_add(K, x) and matchable(K + [x]):
                dfs(K + [x], [y for y in cs[i + 1:] if y in adj[x]])
    dfs([], cand)
    out[Z] = (best[0], best[1])
    print('rep', ri, Z if DIM == 2 else Z[:3], '|C|', pc(X0), 'cands', len(cand), 'max k', best[0], round(time.time() - t0), flush=True)
hist = {}
for Z, (k, _) in out.items(): hist[k] = hist.get(k, 0) + 1
print('DONE dim', DIM, 'histogram of max k over orbit reps', sorted(hist.items()), flush=True)
pickle.dump({'out': out, 'reps': reps}, open(f'cnt4_{unit}_{DIM}.pkl', 'wb'))
