"""Section 4.6: the 72 arcs of the 9-term digon clique realised by explicit GL(9, F2) charts (re-run; replaces the former RECORDED remark).
Call c has out-normals x_{c,a} = Psi_c h_a and in-normals y_{c,a} = Psi_c^{-T} g_a (a = 1..8), Psi_c in GL(9, F2); h_a = the 8 exceptional
functionals of P112 (hb.py), g_a = Gb^{-1} h_a, with h_a . g_b = 1 for all a, b.  Clique: x_j = e_j, y_i = 1 - e_i.  Arc i -> j needs a slot
(c, a) with Psi_c h_a = x_j and Psi_c^T y_i = g_a.  Arcs are packed into calls of <= 4 arcs with disjoint in/out index sets; each call is
solved for an invertible Psi_c by exact F2 linear algebra and every slot normal and the product h.g are re-verified."""
import sys, random, numpy as np
sys.path.insert(0, '.')
import hb
from hb import hyp, Gb, rank2
def inv2(A):
    n = len(A); M = np.concatenate([A % 2, np.eye(n, dtype=np.uint8)], 1).astype(np.uint8); r = 0
    for c in range(n):
        p = next(i for i in range(r, n) if M[i, c]); M[[r, p]] = M[[p, r]]
        for i in range(n):
            if i != r and M[i, c]: M[i] ^= M[r]
        r += 1
    return M[:, n:]
h = [np.array(v, dtype=np.uint8) for v in hyp]; Gbinv = inv2(Gb)
g = [(Gbinv @ v) % 2 for v in h]
assert all(int(h[a] @ g[b]) % 2 == 1 for a in range(8) for b in range(8))
rng = random.Random(17)
def solve_f2(A, b):
    n = A.shape[1]; M = np.concatenate([A % 2, (b % 2)[:, None]], 1).astype(np.uint8); piv = []; r = 0
    for c in range(n):
        p = next((i for i in range(r, M.shape[0]) if M[i, c]), None)
        if p is None: continue
        M[[r, p]] = M[[p, r]]
        for i in range(M.shape[0]):
            if i != r and M[i, c]: M[i] ^= M[r]
        piv.append(c); r += 1
    if any(M[i, n] for i in range(r, M.shape[0])): return None
    z = np.zeros(n, np.uint8)
    for i, c in enumerate(piv): z[c] = M[i, n]
    null = []
    for f in [c for c in range(n) if c not in piv]:
        v = np.zeros(n, np.uint8); v[f] = 1
        for i, c in enumerate(piv): v[c] = M[i, f]
        null.append(v)
    return z, null
X = [np.eye(9, dtype=np.uint8)[j] for j in range(9)]
Y = [np.array([0 if j == i else 1 for j in range(9)], dtype=np.uint8) for i in range(9)]
def call_psi(arcs):
    rows, rhs = [], []
    for a, (i, j) in enumerate(arcs):
        for r in range(9):
            e = np.zeros(81, np.uint8); e[r * 9:(r + 1) * 9] = h[a]; rows.append(e); rhs.append(X[j][r])
        for c in range(9):
            e = np.zeros(81, np.uint8); e[c::9] = Y[i]; rows.append(e); rhs.append(g[a][c])
    s = solve_f2(np.array(rows), np.array(rhs, np.uint8))
    if s is None: return None
    z, null = s
    for _ in range(400):
        v = z.copy()
        for nb in null:
            if rng.random() < .5: v ^= nb
        P = v.reshape(9, 9)
        if rank2(P) == 9: return P
    return None
arcs_left = {(i, j) for i in range(9) for j in range(9) if i != j}; calls = []
while arcs_left:
    best = []
    for _ in range(60):
        cand = sorted(arcs_left); rng.shuffle(cand); cur, ins, outs = [], set(), set()
        for (i, j) in cand:
            if i in ins or j in outs or i in outs or j in ins: continue
            if len(cur) == 4: break
            cur.append((i, j)); ins.add(i); outs.add(j)
        if len(cur) > len(best): best = cur
    P = call_psi(best)
    if P is None: best = best[:1]; P = call_psi(best); assert P is not None
    calls.append((best, P)); arcs_left -= set(best)
for arcs, P in calls:
    xs = [(P @ h[a]) % 2 for a in range(8)]
    ys = [solve_f2(P.T.copy(), g[a])[0] for a in range(8)]
    assert rank2(P) == 9 and all(int(xs[a] @ ys[b]) % 2 == 1 for a in range(8) for b in range(8))
    for a, (i, j) in enumerate(arcs): assert np.array_equal(xs[a], X[j]) and np.array_equal(ys[a], Y[i])
print(f'glclique: 72 arcs of the 9-term digon clique realised by {len(calls)} GL(9,F2) charts; all slot normals and h.g = 1 verified; arcs covered {sum(len(a) for a, _ in calls)}')
