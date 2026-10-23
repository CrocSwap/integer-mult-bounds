"""h=9 two-call batch, square coordinate decoders in both calls, ONE shared term (i in call 0 merged with j in call 1).
Can its cross residual (Xe_i)(Xe_j)^T be cancelled on B01=1 positions by FREE dangling parts of the other 14 terms
(supports whose labels stay inside the term's own hyperplane), possibly plus masked freedom?  Exact rank mod p."""
import random, sys
from hb import *
p = 1000003
iso = [np.array(v, dtype=np.uint8) for v in itertools.product((0, 1), repeat=9) if any(v) and (np.array(v) @ Gb @ np.array(v)) % 2 == 0]
def transv(v): return (np.eye(9, dtype=np.int64) + np.outer(v, v @ Gb)) % 2
def rand_phi(rng, L_=30):
    P = np.eye(9, dtype=np.int64)
    for _ in range(L_): P = (transv(rng.choice(iso)) @ P) % 2
    return P
def rank_modp(rows, ncols):
    # rows: list of dict col->val ; gaussian elimination mod p (dense, small)
    A = np.zeros((len(rows), ncols), dtype=np.int64)
    for r, d in enumerate(rows):
        for c, v in d.items(): A[r, c] = v % p
    return gauss(A)
def gauss(A):
    A = A.copy() % p; r = 0; R, C = A.shape
    for c in range(C):
        piv = None
        for i in range(r, R):
            if A[i, c]: piv = i; break
        if piv is None: continue
        A[[r, piv]] = A[[piv, r]]
        inv = pow(int(A[r, c]), p - 2, p); A[r] = (A[r] * inv) % p
        nz = np.nonzero(A[:, c])[0]
        for i in nz:
            if i != r: A[i] = (A[i] - A[i, c] * A[r]) % p
        r += 1
        if r == R: break
    return r
def inH(v, k): return int(v @ hyp[k]) % 2 == 0
def test(Phi, i, j, free_only=True):
    lab1 = (lab @ Phi.T) % 2
    B01 = (lab @ Gb @ lab1.T) % 2
    Hinv = np.linalg.inv(Phi.astype(float))  # not used
    # free supports
    var = []  # (kind, k, line)
    for k in range(8):
        if k == i: continue
        for s in range(112):
            if (not free_only) or inH(lab1[s], k): var.append(('b', k, s))
    # call-1 term l: output span = Phi(H_l) ; lab_t in Phi(H_l) iff hyp[l] . Phi^{-1} lab_t = 0 ; Phi^{-1} = Gb^{-1} Phi^T Gb (isometry)
    for l in range(8):
        if l == j: continue
        for t in range(112):
            # find whether lab_t in span(lab1[N(f_l)])
            if (not free_only) or rank2(np.vstack([lab1[np.nonzero(X[:, l])[0]], lab[t]])) == 8: var.append(('c', l, t))
    vidx = {v: n for n, v in enumerate(var)}
    eqs = []; rhs = []
    for t in range(112):
        for s in range(112):
            if not B01[t, s]: continue
            d = {}
            for k in range(8):
                if k != i and X[t, k] and ('b', k, s) in vidx: d[vidx['b', k, s]] = int(X[t, k])
            for l in range(8):
                if l != j and X[s, l] and ('c', l, t) in vidx: d[vidx['c', l, t]] = int(X[s, l])
            r = -int(X[t, i]) * int(X[s, j])
            if d or r: eqs.append(d); rhs.append(r)
    n = len(var)
    A = np.zeros((len(eqs), n + 1), dtype=np.int64)
    for r, d in enumerate(eqs):
        for c, v in d.items(): A[r, c] = v % p
        A[r, n] = rhs[r] % p
    rA = gauss(A[:, :n]); rAb = gauss(A)
    return len(var), len(eqs), rA, rAb, rA == rAb
if __name__ == '__main__':
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
    for trial in range(int(sys.argv[2]) if len(sys.argv) > 2 else 3):
        Phi = np.eye(9, dtype=np.int64) if trial == 0 else rand_phi(rng)
        for (i, j) in [(0, 0), (0, 1)]:
            for fo in (True, False):
                print(trial, (i, j), 'free_only' if fo else 'any-dangling', test(Phi, i, j, fo), flush=True)
