# HELPER independent re-implementation of MASK9 case (b) class-level counting (one big term, d0 = D). Own code from THEORY.md §3 rules.
# data primitives reused: setup9.load (E8 lines, orthogonality frames, nbar, label classes cls[c]=O_c), orbits_P112.pkl perms (verified here).
# usage: ind.py D     (D = 5 or 6)
import sys, os, pickle, itertools, time, numpy as np
DD = int(sys.argv[1])
# (working-card sys.path entries removed: run with the package checks/ directory importable)
from setup9 import load
L, v, G, frames, nbar, h, basis, cls = load('P112')
FULL = (1 << v) - 1; LAB = sorted(cls)
pcnt = lambda x: bin(x).count('1')
FR = np.array([[F >> t & 1 for t in range(v)] for F in frames], dtype=np.float32)
NB = np.array([[nbar[t] >> s & 1 for s in range(v)] for t in range(v)], dtype=np.float32)
def bits(x): return np.array([x >> t & 1 for t in range(v)], dtype=np.float32)
_lb = {}
def lb(X):
    """8 - min_E |S_E| after the support-propagation fixed point (IDEAL3 Lemma 1.1): S_E subset of E \\ X, keep t only if every frame's S reaches t via nbar."""
    r = _lb.get(X)
    if r is None:
        S = FR * (1 - bits(X))[None, :]
        while True:
            reach = (S @ NB) > 0
            W = reach.all(axis=0).astype(np.float32)
            S2 = S * W[None, :]
            if np.array_equal(S2, S): break
            S = S2
        r = 8 - int(S.sum(axis=1).min()); _lb[X] = r
    return r
def rank2(rows):
    bs = []
    for r in rows:
        for b in bs: r = min(r, r ^ b)
        if r: bs.append(r)
    return len(bs)
# B0 pattern: B0[t,s]=1 iff t=s or t orth s  (G = Gram, entry 0 iff orthogonal)
B0 = [sum(1 << s for s in range(v) if s == t or G[t][s] == 0) for t in range(v)]
def blkrank(Rm, Am):
    Al = [s for s in range(v) if Am >> s & 1]
    return rank2([sum(1 << i for i, s in enumerate(Al) if B0[t] >> s & 1) for t in range(v) if Rm >> t & 1])
surv = [c for c in LAB if lb(cls[c]) < 8]
NS = [c for c in LAB if c not in surv and cls[c] != FULL]
tauS = {c: [s for s in surv if blkrank(FULL ^ cls[c], FULL ^ cls[s]) == 7] for c in NS}
small = [c for c in NS if tauS[c]]
allc = [c for c in LAB if cls[c] != FULL]
print('h', h, 'classes', len(LAB), 'surv', len(surv), 'NS', len(NS), 'small', len(small), flush=True)
# ---- group on labels (verify) ----
D = pickle.load(open('orbits_P112.pkl', 'rb'))
inv = {cls[c]: c for c in LAB}
gens = []
for p in D['perms']:
    assert all((G[p[a]][p[b]] == 0) == (G[a][b] == 0) for a in range(v) for b in range(a))   # preserves orthogonality
    g = [0] * (1 << h)
    for c in LAB:
        O = 0
        for t in range(v):
            if cls[c] >> t & 1: O |= 1 << p[t]
        g[c] = inv[O]
    assert all(g[a ^ b] == g[a] ^ g[b] for a in range(1 << h) for b in (1, 2, 4, 8, 16, 32, 64, 128, 256))   # linear on labels
    gens.append(g)
sset = set(surv); assert all(g[s] in sset for g in gens for s in surv)
print('verified', len(gens), 'automorphisms: orth-preserving, linear on labels, survivors preserved', flush=True)
def span_of(vs):
    S = {0}
    for x in vs: S |= {y ^ x for y in S}
    return S
def mk(S): return tuple(sorted(S - {0}))
def Cset(Z):
    x = 0
    for c in Z: x |= cls[c]
    return x
def admits(Z, need):
    """exists K subset of small, |K|=need: distinct-survivor matching and all J-conditions with X0=C(Z)."""
    X0 = Cset(Z)
    if X0 == FULL: return False
    cand = [c for c in small if lb(X0 & cls[c]) <= 7]
    if len(cand) < need: return False
    m = {}
    def dfs(K, inter, cs):
        if len(K) >= need: return True
        for i, x in enumerate(cs):
            if len(K) + len(cs) - i < need: return False
            # new intersections for subsets containing x
            new = [inter[j] & cls[x] for j in range(len(inter))]
            n = len(K) + 1
            ok = True
            for j, X in enumerate(new):
                size = bin(j).count('1') + 1
                if size >= 2 and lb(X) > 9 - size: ok = False; break
                if lb(X0 & X) > 9 - (size + 1): ok = False; break
            if not ok: continue
            if not matchable(K + [x]): continue
            if dfs(K + [x], inter + new, cs[i + 1:]): return True
        return False
    return dfs([], [FULL], cand)
def matchable(K, extra=None):
    opts = {c: tauS[c] for c in K}
    if extra: opts['T0'] = extra
    mt = {}
    def aug(c, seen):
        for s in opts[c]:
            if s in seen: continue
            seen.add(s)
            if s not in mt or aug(mt[s], seen): mt[s] = c; return True
        return False
    return all(aug(c, set()) for c in opts)
# ---- stage A: planes ----
need = max(2, 9 - DD)
t0 = time.time()
planes = sorted({mk(span_of((a, b))) for a in LAB for b in LAB if a < b})
print('planes', len(planes), flush=True)
def orbits(subs, gs=None):
    gs = gs or gens; seen = {}; reps = []
    for Z in subs:
        if Z in seen: continue
        reps.append(Z); seen[Z] = Z; st = [Z]
        while st:
            x = st.pop()
            for g in gs:
                y = tuple(sorted(g[c] for c in x))
                if y not in seen: seen[y] = Z; st.append(y)
    return reps, seen
preps, pseen = orbits(planes)
print('plane orbits', len(preps), flush=True)
padm = {}
for R in preps: padm[R] = admits(R, need)
ok_planes = {Z for Z in planes if padm[pseen[Z]]}
print('admissible planes', len(ok_planes), 'of', len(planes), 'orbit reps adm', sum(padm.values()), round(time.time() - t0), flush=True)
# ---- stage B: 3-dim subspaces all of whose planes are admissible ----
three = set()
for P in ok_planes:
    for x in LAB:
        if x in P: continue
        S = span_of(list(P) + [x]); Z = mk(S)
        if Z in three: continue
        subs = [mk(span_of((a, b))) for a in Z for b in Z if a < b]
        if all(q in ok_planes for q in subs): three.add(Z)
three = sorted(three)
print('3-dim candidates', len(three), flush=True)
import random
sub16 = random.Random(5).sample(gens, 16)   # subgroup: sound (only adds reps)
treps, tseen = orbits(three, sub16)
print('3-dim orbits', len(treps), round(time.time() - t0), flush=True)
level = [Z for Z in treps if admits(Z, need)]
print('3-dim reps admitting k>=%d:' % need, len(level), round(time.time() - t0), flush=True)
for d in range(4, DD + 1):
    nxt = set()
    for Z in level:
        Zs = set(Z)
        for x in LAB:
            if x in Zs: continue
            nxt.add(tuple(sorted(Zs | {x} | {x ^ y for y in Zs})))
    level = [Z for Z in sorted(nxt) if admits(Z, need)]
    print('dim', d, 'candidates', len(nxt), 'admitting', len(level), round(time.time() - t0), flush=True)
    if not level: break
pickle.dump(level, open(f'ind_level_{DD}.pkl', 'wb'))
print('STAGE1 DONE D', DD, 'subspaces admitting k>=%d:' % need, len(level), flush=True)
