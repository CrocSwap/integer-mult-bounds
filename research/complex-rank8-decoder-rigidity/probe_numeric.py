#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Numerical probe (evidence, NOT part of the proof): random-start Levenberg-Marquardt on the rank-8
E-graph system x_i.y_j = 0 (orthogonal live pairs), x_i.y_i = 4, and a diagonal-gauge test of every
converged solution against 2G.  Requires numpy.  Usage:
    python3 -I probe_numeric.py <seed> <trials> [P120|P112|P104[,...]]
Recorded runs are listed in README.md ("Numerical probes")."""
import itertools, sys, time
import numpy as np

def _e8_roots():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0] * 8; v[i], v[j] = 2 * si, 2 * sj; roots.append(tuple(v))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0:
            roots.append(tuple(s))
    return roots
_LINES = []; _seen = set()
for _r in _e8_roots():
    _k = _r if _r > tuple(-a for a in _r) else tuple(-a for a in _r)
    if _k not in _seen:
        _seen.add(_k); _LINES.append(_r)
NL = len(_LINES)
RV = np.array(_LINES, dtype=float) / 2.0
G = np.rint(RV @ RV.T).astype(int)
FRAME0 = []
for _a in range(4):
    for _s in (1, -1):
        _v = [0] * 8; _v[2 * _a], _v[2 * _a + 1] = 2, 2 * _s; FRAME0.append(_LINES.index(tuple(_v)))
_P112 = [i for i in range(NL) if i not in FRAME0]
# PR717 D3(b)'s second punctured frame: its clique indices 9,15,24,46,52,66,94,104 are P112 positions
# (PR968 verify.py maps them through p112[q]); as 120-line indices they are [11, 17, 28, 52, 60, 74, 102, 112].
P104_CLIQUE = [_P112[q] for q in (9, 15, 24, 46, 52, 66, 94, 104)]
assert all(G[a][b] == 0 for a in P104_CLIQUE for b in P104_CLIQUE if a != b) and not set(P104_CLIQUE) & set(FRAME0)

def system(live):
    L = list(live); n = len(L)
    orth = [(a, b) for a, i in enumerate(L) for b, j in enumerate(L) if i != j and G[i, j] == 0]
    return L, n, orth

def residual(z, n, orth, oi, oj):
    X = z[:8*n].reshape(n, 8); Y = z[8*n:].reshape(n, 8)
    return np.concatenate([np.einsum('ij,ij->i', X[oi], Y[oj]), np.einsum('ij,ij->i', X, Y) - 4.0])

def jac(z, n, orth, oi, oj):
    X = z[:8*n].reshape(n, 8); Y = z[8*n:].reshape(n, 8)
    m = len(orth); J = np.zeros((m + n, 16*n))
    rows = np.arange(m)
    for c in range(8):
        J[rows, 8*oi + c] = Y[oj, c]
        J[rows, 8*n + 8*oj + c] = X[oi, c]
    for i in range(n):
        J[m+i, 8*i:8*i+8] = Y[i]; J[m+i, 8*n+8*i:8*n+8*i+8] = X[i]
    return J

def lm(z, n, orth, oi, oj, iters=300, tol=1e-20):
    lam = 1e-3
    r = residual(z, n, orth, oi, oj); f = r @ r
    for it in range(iters):
        J = jac(z, n, orth, oi, oj)
        A = J.T @ J; g = J.T @ r; dg = np.diag(A)
        while True:
            dz = -np.linalg.solve(A + lam * (np.diag(dg) + 1e-12*np.eye(A.shape[0])), g)
            z2 = z + dz; r2 = residual(z2, n, orth, oi, oj); f2 = r2 @ r2
            if f2 < f:
                z, r, f = z2, r2, f2; lam = max(lam / 3, 1e-15); break
            lam *= 4
            if lam > 1e14: return z, f
        if f < tol: break
    return z, f

def gauge_test(z, L, n):
    X = z[:8*n].reshape(n, 8); Y = z[8*n:].reshape(n, 8)
    K = X @ Y.T; Gl = G[np.ix_(L, L)]
    odd = [(i, j) for i in range(n) for j in range(n) if abs(Gl[i, j]) == 1]
    if min(abs(K[i, j]) for i, j in odd) < 1e-7:
        return 'ZERO-ODD-ENTRY', None
    # d_i/d_j = K_ij/(2G_ij) must be a consistent potential: log|.| is a coboundary and signs consistent
    w = {(i, j): K[i, j] / (2 * Gl[i, j]) for i, j in odd}
    pot = np.full(n, np.nan); pot[0] = 1.0; frontier = [0]
    adj = {i: [] for i in range(n)}
    for i, j in odd: adj[i].append(j)
    while frontier:
        nf = []
        for i in frontier:
            for j in adj[i]:
                if np.isnan(pot[j]): pot[j] = pot[i] / w[(i, j)]; nf.append(j)
        frontier = nf
    err = max(abs(w[(i, j)] - pot[i] / pot[j]) / (1 + abs(pot[i] / pot[j])) for i, j in odd)
    return ('GAUGE-EQUIV' if err < 1e-6 else 'NOT-GAUGE-EQUIV'), err

if __name__ == '__main__':
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    rng = np.random.default_rng(seed)
    cases = {'P120': [], 'P112': FRAME0, 'P104': FRAME0 + P104_CLIQUE}
    if len(sys.argv) > 3:
        cases = {k: v for k, v in cases.items() if k in sys.argv[3].split(',')}
    for name, punct in cases.items():
        live = [i for i in range(NL) if i not in punct]
        L, n, orth = system(live); oi = np.array([p[0] for p in orth]); oj = np.array([p[1] for p in orth])
        z0 = np.concatenate([(np.sqrt(2) * RV[L]).ravel()] * 2)   # coordinate solution: x_i = y_i = sqrt2 r_i -> x.y = 2<r,r> = 4
        assert np.max(abs(residual(z0, n, orth, oi, oj))) < 1e-9
        s = np.linalg.svd(jac(z0, n, orth, oi, oj), compute_uv=False)
        nul = 16*n - int((s > 1e-8 * s[0]).sum())
        print(f'{name}: live={n} orth_pairs={len(orth)} unknowns={16*n} eqs={len(orth)+n} tangent_nullity_at_coord={nul} (gauge dim 64+{n}-1={63+n})', flush=True)
        t0 = time.time(); summary = {}
        for t in range(trials):
            z = rng.standard_normal(16 * n)
            z, f = lm(z, n, orth, oi, oj)
            if f < 1e-16:
                tag, err = gauge_test(z, L, n)
            else:
                tag, err = f'NOCONV(f={f:.2e})', None
            summary[tag] = summary.get(tag, 0) + 1
        print(f'   {trials} random starts -> {summary}  [{time.time()-t0:.0f}s]', flush=True)
