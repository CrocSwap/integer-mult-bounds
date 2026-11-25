"""HUNT-BATCH common: P112 labels (Gram coords), hyperplane functionals h_i (H_i = ker h_i = span lab N(f_i)), F2 rank."""
import sys, itertools, numpy as np
sys.path.insert(0, '.')
from e8 import L, G, F0i, P112, N
def rank2(M):
    M = (np.array(M, dtype=np.uint8) % 2).copy(); r = 0
    if M.size == 0: return 0
    rows, cols = M.shape
    for c in range(cols):
        p = next((i for i in range(r, rows) if M[i, c]), None)
        if p is None: continue
        M[[r, p]] = M[[p, r]]
        for i in range(rows):
            if i != r and M[i, c]: M[i] ^= M[r]
        r += 1
        if r == rows: break
    return r
live = P112; Bd = (1 + G) % 2; B = Bd[np.ix_(live, live)]
basis = []
for t in range(len(live)):
    if rank2(B[basis + [t]]) == len(basis) + 1: basis.append(t)
    if len(basis) == 9: break
Gb = B[np.ix_(basis, basis)]
def solve(Mrows, v):
    for c in itertools.product((0, 1), repeat=9):
        if np.array_equal((np.array(c) @ Mrows) % 2, v % 2): return np.array(c, dtype=np.uint8)
lab = np.array([solve(B[basis], B[t]) for t in range(len(live))])
assert np.array_equal((lab @ Gb @ lab.T) % 2, B)
X = np.array([[G[t, f] for f in F0i] for t in live])  # 112x8 root matrix in removed-frame coords; supp X e_i = N(f_i)
M = X @ X.T  # = 2*Gram restricted (realisation)
hyp = []
for i, f in enumerate(F0i):
    S = np.nonzero(X[:, i])[0]
    sols = [np.array(h, dtype=np.uint8) for h in itertools.product((0, 1), repeat=9) if any(h) and not ((lab[S] @ np.array(h)) % 2).any()]
    assert len(sols) == 1; hyp.append(sols[0])
def basis_of(vecs):
    out = []
    for v in vecs:
        if rank2(out + [v]) > len(out): out.append(v)
    return out
I9 = np.eye(9, dtype=np.uint8)
HB = [np.array(basis_of([v for v in I9] + [])) for _ in range(0)]
def hbasis(i):  # basis of H_i = ker hyp[i]
    ker = [np.array(v, dtype=np.uint8) for v in itertools.product((0, 1), repeat=9) if any(v) and not (np.array(v) @ hyp[i]) % 2]
    return np.array(basis_of(ker))
HBAS = [hbasis(i) for i in range(8)]
def span(t):  # t = None (empty) | int i (H_i) | 'V'
    if t is None: return np.zeros((0, 9), dtype=np.uint8)
    if t == 'V': return I9.copy()
    return HBAS[t]
def vtype(x, tol=1e-9):
    x = np.asarray(x); nz = np.nonzero(np.abs(x) > tol)[0]
    if len(nz) == 0: return None
    if len(nz) == 1: return int(nz[0])
    return 'V'
