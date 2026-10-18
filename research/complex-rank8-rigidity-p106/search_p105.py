#!/usr/bin/env python3
"""Exploratory, not part of the verified result: census of the 7-subsets of P112 (P105) under H and a PR1560
pivot search per orbit, with numpy float ranks. Writes nothing. About 20 minutes with 10 processes:

    python3 -I -B research/complex-rank8-rigidity-p106/search_p105.py

Same method as make_units.py, one level deeper, with group elements looked up by a 64-bit hash of their
permutation (checked collision-free on H) instead of a dict. Reported run: 242802 orbits, sizes summing to
C(112,7) = 36227890512; every orbit has a passing pivot; the first live frame passes for 230560 of them.
"""
import collections, itertools, sys, time
from math import comb
from multiprocessing import Pool
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V
import make_units as MU

T0 = time.time()
def log(*a):
    print(f'[{time.time()-T0:7.1f}s]', *a, flush=True)

_EP = None
def init():
    global _EP
    gens = V.stabiliser(V.FRAME0)[::V.GEN_STEP]
    E, _, _ = MU.closure(gens)
    pos = np.full(V.NL, -1); pos[V.P112] = np.arange(112)
    _EP = pos[E[:, V.P112]].astype(np.int16)

def stabsize(R):
    R = np.array(R)
    cand = np.nonzero(np.isin(_EP[:, R[0]], R))[0]
    return int((np.sort(_EP[cand][:, R], axis=1) == np.sort(R)).all(axis=1).sum())

def pivot(Xpos):
    X = [V.P112[x] for x in Xpos]
    live = np.zeros(V.NL, dtype=bool); live[V.P112] = True; live[X] = False
    tried = 0
    for n in np.nonzero(~(MU.FM[:, ~live].any(axis=1)))[0]:
        tried += 1
        if MU.passes(live, V.FRAMES[n]):
            return n, tried
    return None, tried

def main():
    init()
    EP = _EP; NH = len(EP)
    INV = np.argsort(EP, axis=1).astype(np.int16)
    rng = np.random.default_rng(1)
    RV = rng.integers(1, 2**63, size=112, dtype=np.uint64)
    def hsh(H):
        return (H.astype(np.uint64) * RV).sum(axis=1)
    hE = hsh(EP); order = np.argsort(hE); hs_sorted = hE[order]
    assert len(np.unique(hE)) == NH
    def lookup(H):
        h = hsh(H); k = np.searchsorted(hs_sorted, h)
        assert (hs_sorted[k] == h).all()
        return order[k]
    INVIDX = lookup(INV)
    tab = np.array([[comb(x, j + 1) for j in range(7)] for x in range(112)], dtype=np.int64)
    def rank(a):
        a = np.sort(a, axis=1)
        return sum(tab[a[:, j], j] for j in range(a.shape[1]))
    subs4 = np.array(list(itertools.combinations(range(112), 4)), dtype=np.int64)
    byrank = np.empty(len(subs4), dtype=np.int64); byrank[rank(subs4)] = np.arange(len(subs4))
    lab = np.full(len(subs4), -1, dtype=np.int64); tr = np.full(len(subs4), -1, dtype=np.int64)
    reps4 = []
    while (lab < 0).any():
        q = subs4[byrank[np.nonzero(lab < 0)[0][0]]]
        rr = rank(EP[:, q].astype(np.int64))
        _, first = np.unique(rr, return_index=True)
        lab[rr[first]], tr[rr[first]] = len(reps4), first
        reps4.append(tuple(int(x) for x in np.sort(q)))
    def tables(reps):
        OM = np.zeros((len(reps), 112), np.int16); TO = np.zeros((len(reps), 112), np.int64)
        for j, R in enumerate(reps):
            R = np.array(R)
            cand = np.nonzero(np.isin(EP[:, R[0]], R))[0]
            ok = cand[(np.sort(EP[cand][:, R], axis=1) == np.sort(R)).all(axis=1)]
            sub = EP[ok]; OM[j] = sub.min(axis=0); TO[j] = ok[sub.argmin(axis=0)]
        return OM, TO
    def canon(C, lab_of, OM, TO):
        best = np.full(len(C), np.iinfo(np.int64).max); bg = np.zeros(len(C), np.int64); bs = np.zeros(len(C), np.int64)
        for r in range(C.shape[1]):
            j, g = lab_of(np.delete(C, r, axis=1))
            y = INV[g, C[:, r]]
            key = j.astype(np.int64) * 112 + OM[j, y]
            better = key < best
            best[better], bg[better], bs[better] = key[better], g[better], TO[j, y][better]
        return best, lookup(EP[bs[:, None], INV[bg]])
    def lab4(S):
        k = rank(S); return lab[k], tr[k]
    OM4, TO4 = tables(reps4)
    def level(cands, lab_of, OM, TO):
        keys = np.empty(len(cands), np.int64); hs = np.empty(len(cands), np.int64)
        B = 50000
        for a in range(0, len(cands), B):
            keys[a:a+B], hs[a:a+B] = canon(cands[a:a+B], lab_of, OM, TO)
        uk, first = np.unique(keys, return_index=True)
        reps = [tuple(int(x) for x in np.sort(EP[hs[i]][cands[i]])) for i in first]
        return uk, reps
    def mk_lab(uk, lab_prev, OM, TO):
        def f(S):
            keys, h = canon(S, lab_prev, OM, TO)
            return np.searchsorted(uk, keys), INVIDX[h]
        return f
    cand5 = np.array(sorted({tuple(sorted(q + (x,))) for q in reps4 for x in range(112) if x not in q}))
    uk5, reps5 = level(cand5, lab4, OM4, TO4); log('5-orbits', len(reps5))
    OM5, TO5 = tables(reps5); lab5 = mk_lab(uk5, lab4, OM4, TO4)
    cand6 = np.array(sorted({tuple(sorted(R + (x,))) for R in reps5 for x in range(112) if x not in R}))
    uk6, reps6 = level(cand6, lab5, OM5, TO5); log('6-orbits', len(reps6))
    OM6, TO6 = tables(reps6); lab6 = mk_lab(uk6, lab5, OM5, TO5); log('6-tables')
    cand7 = np.array(sorted({tuple(sorted(R + (x,))) for R in reps6 for x in range(112) if x not in R}), dtype=np.int64)
    log('7-candidates', len(cand7))
    uk7, reps7 = level(cand7, lab6, OM6, TO6); log('7-orbits', len(reps7))
    with Pool(10, initializer=init) as pool:
        st = pool.map(stabsize, reps7, chunksize=256)
        tot = sum(NH // s for s in st)
        log('7-orbit sizes sum', tot, 'C(112,7) =', comb(112, 7), tot == comb(112, 7))
        piv = pool.map(pivot, reps7, chunksize=64)
    bad = [r for r, (p, _) in zip(reps7, piv) if p is None]
    log('P105 none-found', len(bad), bad[:10])
    log('frames tried', sorted(collections.Counter(t for p, t in piv if p is not None).items())[:12])

if __name__ == '__main__':
    main()
