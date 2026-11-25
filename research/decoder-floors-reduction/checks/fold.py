"""CANCEL: exact check of the twin-fold theorem TF on the HUNT-BATCH anchor at Phi = I (common chart).
Batch: coordinate decoders in both calls, term i of call 0 merged with term j of call 1, two pure-cross cancellers.
Fold0(lam) = {(p^0, q^0 + lam q^1)}, Fold1(mu) = {(p^1, q^1 + mu q^0)}: each must decode M on B = 1 positions; costs <= batch costs."""
import sys; sys.path.insert(0, '.')
from hb import *
n = 112; Z = np.zeros(n, dtype=np.int64)
def batch(i, j):
    T = []
    for k in range(8):
        if k != i: T.append((np.r_[X[:, k], Z], np.r_[X[:, k], Z]))
    for l in range(8):
        if l != j: T.append((np.r_[Z, X[:, l]], np.r_[Z, X[:, l]]))
    T.append((np.r_[X[:, i], X[:, j]], np.r_[X[:, i], X[:, j]]))
    T.append((np.r_[X[:, i], Z], -np.r_[Z, X[:, j]]))
    T.append((np.r_[Z, X[:, j]], -np.r_[X[:, i], Z]))
    return T
BJ = np.block([[B, B], [B, B]])  # Phi = I: joint table
cst = lambda a, c, BB: rank2(BB[np.ix_(np.nonzero(a)[0], np.nonzero(c)[0])]) if a.any() and c.any() else 0
for (i, j) in [(0, 0), (0, 1), (0, 5)]:
    T = batch(i, j); bc = [cst(a, c, BJ) for a, c in T]
    for lam in (1, -1, 2):
        F0 = [(a[:n], c[:n] + lam * c[n:]) for a, c in T]; F1 = [(a[n:], c[n:] + lam * c[:n]) for a, c in T]
        for F in (F0, F1):
            S = sum(np.outer(a, c) for a, c in F)
            assert np.array_equal(S[B == 1], M[B == 1]), 'fold does not decode M on mask'
        f0 = [cst(a, c, B) for a, c in F0]; f1 = [cst(a, c, B) for a, c in F1]
        assert all(x <= y for x, y in zip(f0, bc)) and all(x <= y for x, y in zip(f1, bc))
        print(f'(i,j)=({i},{j}) lam={lam:2d}: batch {sum(bc)}, fold0 {sum(f0)}, fold1 {sum(f1)}, fold0+fold1 {sum(f0)+sum(f1)}, shared-term charges {f0[14]}+{f1[14]} (batch {bc[14]})')
