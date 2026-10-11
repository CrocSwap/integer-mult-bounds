# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""E8 root lines in Hamming (Construction A) coordinates, same order as the #370 producer (E8COORD=ham).
Fast numpy closure of root-spanned subspaces (frames as bitmasks of the 120 lines)."""
import itertools

import numpy as np


def _roots_hamming():
    g = [(1, 1, 1, 1, 0, 0, 0, 0), (1, 1, 0, 0, 1, 1, 0, 0), (1, 0, 1, 0, 1, 0, 1, 0), (0, 1, 1, 0, 1, 0, 0, 1)]
    H = []
    for a in itertools.product((0, 1), repeat=4):
        H.append(tuple(sum(a[k] * g[k][i] for k in range(4)) % 2 for i in range(8)))
    R = []
    for i in range(8):
        for sg in (2, -2):
            v = [0] * 8
            v[i] = sg
            R.append(tuple(v))
    for w in H:
        if sum(w) == 4:
            idx = [i for i in range(8) if w[i]]
            for sg in itertools.product((1, -1), repeat=4):
                v = [0] * 8
                for i, s_ in zip(idx, sg):
                    v[i] = s_
                R.append(tuple(v))
    return R


ALL = _roots_hamming()
LINES = []
_seen = set()
for r in ALL:
    if r in _seen:
        continue
    neg = tuple(-a for a in r)
    _seen.add(r)
    _seen.add(neg)
    LINES.append(r if [a for a in r if a][0] > 0 else neg)
V = len(LINES)
assert V == 120
LA = np.array(LINES, dtype=float)
GI = (np.array(LINES) @ np.array(LINES).T) // 2  # integer Gram <x,y>/2
G = GI
ORTH = [[b for b in range(V) if GI[a, b] == 0] for a in range(V)]
NEIGH = [[b for b in range(V) if abs(GI[a, b]) == 1] for a in range(V)]
assert all(len(o) == 63 and len(n) == 56 for o, n in zip(ORTH, NEIGH))
FULL = (1 << V) - 1
LINE = [1 << s for s in range(V)]
HYP = [sum(1 << s for s in ORTH[t]) for t in range(V)]


def bits(mask):
    out = []
    while mask:
        b = mask & -mask
        out.append(b.bit_length() - 1)
        mask ^= b
    return out


def popcount(mask):
    return bin(mask).count("1")


_cache = {}


def closure(mask):
    """(closed mask, dim) of the span of the lines in mask."""
    r = _cache.get(mask)
    if r is not None:
        return r
    idx = bits(mask)
    if not idx:
        return (0, 0)
    A = LA[idx]
    # orthonormal basis of the row space
    u, s, vt = np.linalg.svd(A, full_matrices=False)
    k = int((s > 1e-9).sum())
    Q = vt[:k]
    res = LA - (LA @ Q.T) @ Q
    inside = np.abs(res).max(axis=1) < 1e-9
    cm = 0
    for i in np.nonzero(inside)[0]:
        cm |= 1 << int(i)
    r = (cm, k)
    _cache[mask] = r
    _cache[cm] = r
    return r


def dim(mask):
    return closure(mask)[1]


def join(a, b):
    return closure(a | b)[0]


def inside(a, b):
    return a & ~b == 0


def perp(mask):
    """closed mask of root lines orthogonal to every line in mask (root-spanned part of the orthogonal complement)."""
    idx = bits(mask)
    ok = np.all(GI[:, idx] == 0, axis=1) if idx else np.ones(V, bool)
    m = 0
    for i in np.nonzero(ok)[0]:
        m |= 1 << int(i)
    return m


def all_subspaces():
    """dict dim -> set of closed masks of all root-spanned subspaces of Q^8."""
    by = {0: {0}, 1: {1 << s for s in range(V)}}
    for d in range(2, 9):
        nxt = set()
        for m in by[d - 1]:
            rest = FULL & ~m
            while rest:
                b = rest & -rest
                s = b.bit_length() - 1
                cm, k = closure(m | b)
                assert k == d
                nxt.add(cm)
                rest &= ~cm
        by[d] = nxt
    return by
