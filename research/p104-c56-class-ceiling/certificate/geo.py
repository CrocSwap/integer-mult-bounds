"""PORTSET geo.py (own code): full E8 line geometry with F2^9 labels, consistent with REBASET1 (lines104.json, G104.npy).
Exports: N120 lines, R (120x8 float roots), G120 (int Gram), U (labels, 9-bit ints, standard dot), PORT104 (indices of the
104 ports in REBASET1 order), dot.  Labels of the 16 virtual lines are SOLVED over F2 from S(u_l,u_t) = G_lt+1 (mod 2)."""
import json, numpy as np, itertools, functools
import os; WD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data') + '/'
G104 = np.load(WD + 'G104.npy').astype(int)
Q104 = json.load(open(WD + 'lines104.json'))
dot = lambda a, b: bin(a & b).count('1') & 1


@functools.lru_cache(None)
def build():
    ev, V = np.linalg.eigh(G104.astype(float))
    R = V[:, ev > 13] * np.sqrt(26.0)
    assert np.allclose(R @ R.T, G104)
    key = lambda v: tuple(np.round(v * 1e6).astype(np.int64))
    seen = {}
    for v in R:
        seen[key(v)] = v; seen[key(-v)] = -v
    frontier = list(seen.values())
    while frontier:
        new = []; allr = list(seen.values())
        for a in frontier:
            for b in allr:
                w = b - (a @ b) * a
                k = key(w)
                if k not in seen: seen[k] = w; new.append(w)
        frontier = new
    assert len(seen) == 240
    lines = [R[i] for i in range(104)]
    for v in seen.values():
        if not any(abs(abs(v @ u) - 2) < 1e-6 for u in lines): lines.append(v)
    assert len(lines) == 120
    L = np.array(lines)
    G = np.rint(L @ L.T).astype(int)
    assert np.allclose(L @ L.T, G)
    U = list(Q104)
    for l in range(104, 120):
        # solve u (9 bits) with dot(u, Q104[t]) = (G[l,t]+1)%2 for all t<104
        sols = [u for u in range(512) if all(dot(u, Q104[t]) == (G[l, t] + 1) % 2 for t in range(104))]
        assert len(sols) == 1, (l, len(sols))
        U.append(sols[0])
    for i in range(120):
        for j in range(120):
            assert dot(U[i], U[j]) == (G[i, j] + 1) % 2
    assert len(set(U)) == 120
    return L, G, U


R, G120, U = build()
N = 120
PORT104 = list(range(104))


def partners(A, s):
    return [t for t in A if t != s and G120[s, t] != 0]


def hcount(A, s, nondeg=False):
    """max over v (v not in <u_s>) of #{t in P_s(A): u_t.v = 0}; returns (h, |P|, argmax list)."""
    P = partners(A, s); us = U[s]
    best, arg = -1, []
    for v in range(1, 512):
        if v == us: continue
        if nondeg:
            # frame <u_s,v> nondegenerate: Gram [[1, us.v],[us.v, v.v]] invertible over F2
            a, b = dot(us, v), dot(v, v)
            if (1 * b - a * a) % 2 == 0: continue
        c = sum(1 for t in P if dot(U[t], v) == 0)
        if c > best: best, arg = c, [v]
        elif c == best: arg.append(v)
    return best, len(P), arg
