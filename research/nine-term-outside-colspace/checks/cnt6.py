# MASK9 case (b), one big term with d0 = D >= 4. Need k >= max(2, 9 - D) small terms jointly valid with C(Z_0) (cnt4 conditions).
# k-validity is monotone decreasing in Z, so every subspace of Z_0 also admits k >= 9 - D. WLOG (Aut) a 3-dim subspace of Z_0 is a cnt4 dim-3
# orbit rep; extend one vector at a time (dedup per level), keeping only subspaces admitting k >= need.  usage: cnt6.py UNIT D
import sys
DD = int(sys.argv[2]); sys.argv = sys.argv[:2]
from m9lib import *
need = max(2, 9 - DD)
R3 = pickle.load(open(f'cnt4_{unit}_3.pkl', 'rb'))
start = [Z for Z, (k, _) in R3['out'].items() if k >= need]
print("D", DD, 'need k >=', need, 'start reps', len(start), flush=True)
def reach(Z, need, pc_):
    X0 = C(Z)
    if X0 == full: return False, []
    cand = [c for c in pc_ if lb(X0 & cls[c]) <= 7]   # cand(Z) ⊆ cand(parent) by monotonicity
    def ok_add(K, x):
        for r in range(0, len(K) + 1):
            for J in itertools.combinations(K, r):
                X = cls[x]
                for c in J: X &= cls[c]
                if r >= 1 and lb(X) > 9 - (r + 1): return False
                if lb(X0 & X) > 9 - (r + 2): return False
        return True
    def dfs(K, cs):
        if len(K) >= need: return True
        for i, x in enumerate(cs):
            if len(K) + len(cs) - i < need: return False
            if ok_add(K, x) and matchable(K + [x]):
                if dfs(K + [x], [y for y in cs[i + 1:] if y in adj[x]]): return True
        return False
    return dfs([], cand), cand
def candbatch(Z):
    X0 = C(Z)
    if X0 == full: return []
    m = minS(np.array([tobits(X0 & cls[c]) for c in small]))
    return [c for c, x in zip(small, m) if 8 - int(x) <= 7]
t0 = time.time(); level = {Z: candbatch(Z) for Z in start}
print('start cands', sorted(len(x) for x in level.values()), round(time.time() - t0), flush=True)
for d in range(4, DD + 1):
    nxt = {}
    for Z, pcand in level.items():
        Zs = set(Z)
        for x in ks:
            if x in Zs: continue
            Z2 = tuple(sorted(Zs | {x ^ y for y in Zs} | {x}))
            if Z2 in nxt: continue
            nxt[Z2] = pcand
    kept = {}
    for Z2, pcand in nxt.items():
        ok, cnd = reach(Z2, need, pcand)
        if ok: kept[Z2] = cnd
    print('dim', d, 'extensions', len(nxt), 'admitting k >=', need, ':', len(kept), round(time.time() - t0), flush=True)
    level = kept
    if not level: break
print('DONE D', DD, 'residue subspaces', len(level), flush=True)
pickle.dump(sorted(level.keys()), open(f'cnt6_{unit}_{DD}.pkl', 'wb'))
