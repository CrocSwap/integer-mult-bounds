"""D4: structured classical decoders in the copy-cost model on P112 and all 112 single-puncture P111s:
coordinate 64; D2-butterfly pairs / halves / D4-Hadamard / permuted pairs / WHT 72; coset 4-split 192 (n=32, beta 6 each)."""
import numpy as np
import e8model as m
fails = 0
def ok(tag, cond, info=""):
    global fails
    print(("PASS " if cond else "FAIL ") + tag + (" | " + info if info else ""), flush=True)
    fails += (not cond)
X = m.X.copy(); d8 = np.array([np.count_nonzero(r) == 2 for r in m.RP])
ok("D4.D8-48-spin-64-lines", d8.sum() == 48 and (~d8).sum() == 64)
ok("D4.coordinate-exact-cst-64", m.exact(X, X, 1) and m.cost(X, X) == 64)
A = X * d8[:, None]; B = X * (~d8)[:, None]
D = np.concatenate([A, B, A, B], 1); T = np.concatenate([A, B, B, A], 1)
ok("D4.coset-4split-exact-n32-cst-192", m.exact(D, T, 1) and D.shape[1] == 32 and m.cost(D, T) == 192
   and all(m.pair_rank(np.nonzero(D[:, k])[0], np.nonzero(T[:, k])[0]) == 6 for k in range(32)))
def H(n):
    h = np.array([[1]])
    for _ in range(n): h = np.block([[h, h], [h, -h]])
    return h
def blk(pairs):
    Q = np.zeros((8, 8), int); r = 0
    for a, b in pairs:
        Q[r, a] = 1; Q[r, b] = 1; Q[r + 1, a] = 1; Q[r + 1, b] = -1; r += 2
    return Q
cands = {"pairs(2a,2a+1)": blk([(0, 1), (2, 3), (4, 5), (6, 7)]), "halves(j,j+4)": blk([(0, 4), (1, 5), (2, 6), (3, 7)]),
         "D4-Hadamard-x2": np.kron(np.eye(2, dtype=int), H(2)), "perm-pairs(0,2)(1,3)": blk([(0, 2), (1, 3), (4, 6), (5, 7)]), "WHT8": H(3)}
for nm, Q in cands.items():
    F = X @ Q.T; sc = int((Q @ Q.T)[0, 0])
    ok("D4.%s-exact-cst-72" % nm, (F @ F.T == m.M4 * sc).all() and m.cost(F, F) == 72)
allr = np.arange(112)
fam = {"coord": (X, X), "pairs": (X @ cands["pairs(2a,2a+1)"].T,) * 2, "halves": (X @ cands["halves(j,j+4)"].T,) * 2, "coset4": (D, T)}
want = {"coord": 64, "pairs": 72, "halves": 72, "coset4": 192}
for nm, (D_, T_) in fam.items():
    vals = set()
    for q in range(112):
        keep = np.delete(allr, q)
        vals.add(sum(m.pair_rank(keep[np.nonzero(D_[keep][:, k])[0]], keep[np.nonzero(T_[keep][:, k])[0]]) for k in range(D_.shape[1])))
    ok("D4.P111-all-112-punctures.%s" % nm, vals == {want[nm]}, "cst values %s" % sorted(vals))
raise SystemExit(1 if fails else 0)
