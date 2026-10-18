# MASK9 case (b), two or more big terms (row deficiency d >= 2). Their planes must be pairwise (2,2)-compatible: cnt.py found, for each
# 2-dim orbit rep R, the W' with lb(C(R) ∩ C(W')) <= 7 (all other pairs certified). For each such pair: add further bigs (pairwise compatible
# + J-conditions), extend every big to all larger subspaces keeping the J-conditions, then for every τ-pattern of the bigs enumerate small
# sets K, extras and apply the support filter of cnt8 (D, C). All tests are necessary conditions (sound).   usage: cnt9.py UNIT
import sys
sys.argv = sys.argv[:2]
from m9lib import *
cliques = [sum(1 << t for t in c) for c in pickle.load(open(f'cliques_{unit}.pkl', 'rb')) if len(c) in (7, 8)]
csz = {Cq: pc(Cq) for Cq in cliques}
lb22 = pickle.load(open(f'cnt_{unit}.pkl', 'rb'))['lb22']
pairs = [(R, W) for (R, W), x in lb22.items() if x <= 7]
print('compatible (rep, plane) pairs', len(pairs), flush=True)
allc = [c for c in ks if cls[c] != full]
def jset(Xs):
    """J-conditions on a list of line sets (one per distinct masked term): every subfamily J has lb(∩J) <= 9 - |J| (|J| >= 2)."""
    for r in range(2, len(Xs) + 1):
        for J in itertools.combinations(Xs, r):
            X = full
            for x in J: X &= x
            if lb(X) > 9 - r: return False
    return True
def jadd(Xs, x):
    for r in range(1, len(Xs) + 1):
        for J in itertools.combinations(Xs, r):
            X = x
            for y in J: X &= y
            if lb(X) > 9 - (r + 1): return False
    return True
def extend(Z, others):
    """all subspaces Z' ⊇ Z whose C(Z') keeps the J-conditions with the other bigs' sets"""
    out = {Z}; level = {Z}
    while level:
        nxt = set()
        for Y in level:
            Ys = set(Y)
            for x in ks:
                if x in Ys: continue
                Y2 = tuple(sorted(Ys | {x ^ y for y in Ys} | {x}))
                if Y2 in out or Y2 in nxt: continue
                if C(Y2) != full and jadd(others, C(Y2)): nxt.add(Y2)
        out |= nxt; level = nxt
    return out
def matchings(items, opts):
    if not items: yield {}; return
    it = items[0]
    for s in opts[it]:
        for m in matchings(items[1:], opts):
            if s not in m.values(): yield {**m, it: s}
t0 = time.time(); alive = []; nconf = 0
for (R, W) in pairs:
    if R == W: continue
    nbrs = [W3 for (R3, W3) in pairs if R3 == R and W3 not in (R, W)]
    bigsets = []
    def grow(pl, cs):
        bigsets.append(tuple(pl))
        for i, x in enumerate(cs):
            if jadd([C(P) for P in pl], C(x)): grow(pl + [x], cs[i + 1:])
    grow([R, W], [x for x in nbrs if x > W])
    for planes in bigsets:
        exts = [extend(P, [C(Q) for Q in planes if Q != P]) for P in planes]
        for Zs in itertools.product(*exts):
            Xs = [C(Z) for Z in Zs]
            if not jset(Xs): continue
            nconf += 1
            dims = [(len(Z) + 1).bit_length() - 1 for Z in Zs]
            S0s = [[s for s in surv if rk(full ^ C(Z), full ^ cls[s]) == 8 - d] for Z, d in zip(Zs, dims)]
            for taus in itertools.product(*[[0, 1] if S else [0] for S in S0s]):
                sigb = sum(min(7, d - 1 + t) for d, t in zip(dims, taus)); nb = len(Zs)
                cand = [c for c in small if jadd(Xs, cls[c])]
                items0 = [f'B{i}' for i in range(nb) if taus[i]]
                opts = dict(tauS)
                for i in range(nb): opts[f'B{i}'] = S0s[i]
                def match(K): return next(matchings(list(K) + items0, opts), None) is not None
                Ks = []
                def dfs(K, cs):
                    Ks.append(tuple(K))
                    for i, x in enumerate(cs):
                        if jadd(Xs + [cls[c] for c in K], cls[x]) and match(K + [x]):
                            dfs(K + [x], [y for y in cs[i + 1:] if y in adj[x]])
                dfs([], cand)
                for K in Ks:
                    k = len(K); e = 9 - nb - k; slack = sigb + k - 9; survleft = 8 - k - sum(taus)
                    if slack < 0 or e < 0: continue
                    for tx in range(0, min(survleft, max(0, e - slack)) + 1):
                        ncl = max(0, e - slack - tx)
                        extras = []
                        def ext(E, cs):
                            if len(E) == ncl: extras.append(tuple(E)); return
                            for i, x in enumerate(cs):
                                if jadd(Xs + [cls[c] for c in K] + [cls[c] for c in E], cls[x]): ext(E + [x], cs[i:])   # repeats allowed (two extras may share a survivor class; audit item 2)
                        ext([], allc)
                        for m in matchings(list(K) + items0, opts):
                            free = [s_ for s_ in surv if s_ not in m.values()]
                            for TX in itertools.combinations(free, tx):
                                for E in extras:
                                    terms = [(full ^ Xs[i], full ^ (cls[m[f'B{i}']] if taus[i] else 0)) for i in range(nb)]
                                    terms += [(full ^ cls[c], full ^ cls[m[c]]) for c in K]
                                    terms += [(full ^ cls[c], full) for c in E]
                                    terms += [(full, full ^ cls[s_]) for s_ in TX]
                                    terms += [(full, full)] * (9 - len(terms))
                                    cover = 0
                                    for r_, a_ in terms: cover |= r_ & a_
                                    if cover != full: continue
                                    if all(sum(1 for r_, a_ in terms if r_ & Cq and a_ & Cq) >= csz[Cq] for Cq in cliques):
                                        alive.append((Zs, taus, K, m, E, TX))
    print('pair', R, W, 'configs so far', nconf, 'alive', len(alive), round(time.time() - t0), flush=True)
print('DONE multi-big: big configurations', nconf, 'alive after J + support filter', len(alive), flush=True)
pickle.dump(alive, open(f'cnt9_{unit}.pkl', 'wb'))
