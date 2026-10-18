# MASK9 case (b), exactly one big term (d0 = D >= 2), final class-level residue check.
# Accounting (STRAYS-MASK §4.1-4.2): σ_0 = min(7, D - 1 + τ_0), τ_0 = 1 needs a survivor s_0 with rank B0[~C(Z_0), ~O_s0] = 8 - D;
# small terms σ = 1 (d = 1 non-survivor class, τ = 1, distinct survivors); every other term ("extra") has σ ∈ {-1, 0}, and σ = 0 needs either a
# row-dead class (d = 1, any class) or τ = 1 on an unused survivor. Σσ >= 9 with 9 terms. For each Z_0 and τ_0 we enumerate all valid small sets K
# (cnt4 J-conditions with C(Z_0), survivor matching incl. s_0), then need rc = max(0, e - slack - survleft) extra classes c (distinct from K),
# jointly satisfying the J-conditions with C(Z_0), K and each other (all are masked or J ∩ S != ∅ since term 0 is masked).
# usage: cnt7.py UNIT D source   (source: 'cnt4' -> cnt4_UNIT_D.pkl reps; 'cnt6' -> cnt6_UNIT_D.pkl subspaces)
import sys
DD = int(sys.argv[2]); src = sys.argv[3]; sys.argv = sys.argv[:2]
from m9lib import *
if src == 'cnt4': Zs = list(pickle.load(open(f'cnt4_{unit}_{DD}.pkl', 'rb'))['out'].keys())
else: Zs = pickle.load(open(f'cnt6_{unit}_{DD}.pkl', 'rb'))
allc = [c for c in ks if cls[c] != full]
def jok(sets, x, X0):
    """x added to list `sets` (class codes); J-conditions for all J ⊆ sets with x, with and without term 0 (X0)."""
    for r in range(0, len(sets) + 1):
        for J in itertools.combinations(sets, r):
            X = cls[x]
            for c in J: X &= cls[c]
            if r >= 1 and lb(X) > 9 - (r + 1): return False
            if lb(X0 & X) > 9 - (r + 2): return False
    return True
t0 = time.time(); residue = []; nZ = 0
for Z in Zs:
    X0 = C(Z)
    if X0 == full: continue
    nZ += 1
    S0 = [s for s in surv if rk(full ^ X0, full ^ cls[s]) == 8 - DD]
    mm = minS(np.array([tobits(X0 & cls[c]) for c in small])); cand = [c for c, x in zip(small, mm) if 8 - int(x) <= 7]
    for tau0 in ([1, 0] if S0 else [0]):
        if tau0 and DD >= 8: continue
        sig0 = min(7, DD - 1 + tau0); kmin = max(0, 9 - sig0 - 0)
        def match(K):
            tS = dict(tauS)
            if tau0: tS['T0'] = S0
            m = {}
            def aug(c, seen):
                for s in tS[c]:
                    if s in seen: continue
                    seen.add(s)
                    if s not in m or aug(m[s], seen): m[s] = c; return True
                return False
            return all(aug(c, set()) for c in list(K) + (['T0'] if tau0 else []))
        Ks = []
        def dfs(K, cs):
            Ks.append(tuple(K))
            for i, x in enumerate(cs):
                if jok(K, x, X0) and match(K + [x]):
                    dfs(K + [x], [y for y in cs[i + 1:] if y in adj[x]])
        dfs([], cand)
        for K in Ks:
            k = len(K); e = 8 - k; slack = sig0 + k - 9; survleft = 8 - k - tau0
            if slack < 0: continue
            rc = max(0, e - slack - survleft)
            if rc > e: continue
            # find rc extra classes jointly valid
            found = []
            def ext(E, cs):
                if len(E) == rc: found.append(tuple(E)); return True
                for i, x in enumerate(cs):
                    if jok(list(K) + E, x, X0) and ext(E + [x], cs[i:]): return True   # repeats allowed (audit item 2)
                return False
            if ext([], allc):
                residue.append((Z, tau0, K, found[0]))
    if nZ % 10 == 0: print('subspaces', nZ, 'residue so far', len(residue), round(time.time() - t0), flush=True)
print('DONE D', DD, 'subspaces', nZ, 'residue configurations', len(residue), flush=True)
for r in residue[:10]: print('  ', r[0][:4], 'tau0', r[1], 'K', r[2], 'extra', r[3])
pickle.dump(residue, open(f'cnt7_{unit}_{DD}.pkl', 'wb'))
