"""E8 lines, the 8 rank-7 flat types, flat orbits and the Lemma-G-failure option sets (numpy only).
Line order = first occurrence of the 240 E8 roots (doubled coordinates, norm 8) as listed below; every state file of data/states uses these indices.
options(M, flat, s, pmax): the inclusion-minimal sets e = s^perp \\ F' over rank-7 flats F' containing s with |e| <= pmax; minimality <=> the
section s^perp & F' has rank 6.  Row order = (size, sorted index tuple): the leaf CNFs, hence their md5, depend on it."""
import itertools
import numpy as np

def _roots():
    R = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (2, -2):
            for sj in (2, -2):
                v = [0] * 8; v[i] = si; v[j] = sj; R.append(tuple(v))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0: R.append(s)
    return R
_seen = set(); _L = []
for _r in _roots():
    if tuple(-x for x in _r) not in _seen:
        _seen.add(_r); _L.append(_r)
L = np.array(_L, dtype=np.int64)            # 120 x 8
G = (L @ L.T) // 4                          # Gram, entries 0, +-1, +-2
assert L.shape == (120, 8)
_idx = {}
for _t in range(120): _idx[tuple(L[_t])] = _t; _idx[tuple(-L[_t])] = _t
def refl(r):
    """permutation of the 120 lines induced by the reflection in line r"""
    return [_idx[tuple(L[t] - (2 * (L[t] @ L[r]) // (L[r] @ L[r])) * L[r])] for t in range(120)]
PER = [refl(r) for r in range(120)]
_SR = np.array([(1,-1,-1,-1,-1,-1,-1,1),(2,2,0,0,0,0,0,0),(-2,2,0,0,0,0,0,0),(0,-2,2,0,0,0,0,0),(0,0,-2,2,0,0,0,0),(0,0,0,-2,2,0,0,0),(0,0,0,0,-2,2,0,0),(0,0,0,0,0,-2,2,0)])
_Winv = np.linalg.inv(_SR.astype(float))
def _coweight(i):
    s = _Winv[:, i]
    for m in range(1, 200):
        if np.allclose(s * m, np.round(s * m)): return np.round(s * m).astype(np.int64)
FLATREP = {i: (L @ _coweight(i)) == 0 for i in range(8)}      # type i -> boolean mask of the rank-7 flat F*_i
FLATSIZE = {i: int(FLATREP[i].sum()) for i in range(8)}
def _keys(A):
    return np.ascontiguousarray(np.packbits(A, axis=1, bitorder='big')).view(np.dtype((np.void, 15))).ravel()
def orbit(mask):
    """W-orbit of a boolean mask over the 120 lines (breadth-first, reflections as generators)"""
    seen = {_keys(mask[None])[0].tobytes(): 0}; allm = [mask[None].copy()]; fr = mask[None].copy()
    while len(fr):
        nxt = []
        for P in PER:
            img = np.zeros_like(fr); img[:, np.array(P)] = fr; nxt.append(img)
        nxt = np.concatenate(nxt); k = _keys(nxt); u, ix = np.unique(k, return_index=True)
        new = [i for kk, i in zip(u.tolist(), ix.tolist()) if kk not in seen]
        for kk in u.tolist(): seen.setdefault(kk, 0)
        fr = nxt[new]
        if len(fr): allm.append(fr)
    return np.concatenate(allm)
def all_flats():
    """the 440,880 rank-7 flats (union of the 8 W-orbits), boolean masks, 440880 x 120"""
    M = np.concatenate([orbit(FLATREP[t]) for t in range(8)])
    return M
def options(M, s, pmax=56):
    perp = (G[s] == 0)
    Ms = M[M[:, s]]; need = perp[None, :] & ~Ms; sz = need.sum(1)
    U = np.unique(need[sz <= pmax], axis=0); mins = []
    for r in U:
        sec = perp & ~r
        if np.linalg.matrix_rank(L[sec].astype(float)) == 6: mins.append(r)
    mins = np.array(mins, dtype=bool).reshape(-1, 120)
    o = sorted(range(len(mins)), key=lambda i: (int(mins[i].sum()), tuple(np.flatnonzero(mins[i]).tolist())))   # order of the recorded runs
    return mins[o]
