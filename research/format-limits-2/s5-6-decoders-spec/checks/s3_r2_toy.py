"""S3: relaxing R2 (one identical exact representative per gate) to representatives differing by a right logical permutation is not a
drop-in: h=3 exact Clifford toy.  Same rep -> X = I; rep differing by an address permutation -> X is a permutation with 4/8 addresses
moved; a sideways label -> X not monomial, 8/8 moved; the group-ring span of S3 on 3 qubits is 5 of 64 dimensions."""
import numpy as np
h = 3; N = 2 ** h
I2 = np.eye(2); C = (1 + 1j) / 2 * np.array([[1, -1j], [-1j, 1]])
def kron(*a):
    r = np.eye(1)
    for x in a: r = np.kron(r, x)
    return r
def Tcoord(S): return kron(*[C if i in S else I2 for i in range(h)])
def perm(sig):
    P = np.zeros((N, N))
    for x in range(N):
        bits = [(x >> (h - 1 - i)) & 1 for i in range(h)]
        nb = [bits[sig[i]] for i in range(h)]
        P[sum(b << (h - 1 - i) for i, b in enumerate(nb)), x] = 1
    return P
fails = 0
def ok(tag, cond, info=""):
    global fails
    print(("PASS " if cond else "FAIL ") + tag + (" | " + info if info else ""), flush=True)
    fails += (not cond)
Ts = Tcoord({0}); P = perm([1, 0, 2])
def eff(Tt):
    X = np.linalg.inv(Tt) @ Ts
    return X, int((np.abs(X - np.eye(N)).sum(0) > 1e-9).sum())
X, mv = eff(Ts); ok("S3.same-rep-gives-identity", np.abs(X - np.eye(N)).max() < 1e-12 and mv == 0)
X, mv = eff(Ts @ P)
ok("S3.rep-differs-by-address-permutation-moves-4-of-8", mv == 4 and np.allclose(X @ X.T.conj(), np.eye(N)) and np.allclose(np.abs(X), np.round(np.abs(X))), "moved %d/8, X a permutation" % mv)
X, mv = eff(Tcoord({1}))
ok("S3.sideways-label-moves-8-of-8-non-monomial", mv == 8 and not np.allclose(np.abs(X), np.round(np.abs(X))), "moved %d/8" % mv)
gens = [perm([1, 0, 2]), perm([0, 2, 1])]
G = {tuple(np.eye(N).flatten())}; fr = [np.eye(N)]
while fr:
    n = []
    for a in fr:
        for g in gens:
            b = g @ a; t = tuple(b.flatten())
            if t not in G: G.add(t); n.append(b)
    fr = n
ok("S3.S3-group-ring-span-5-of-64", len(G) == 6 and np.linalg.matrix_rank(np.array(list(G))) == 5, "closure order %d, span rank %d of %d" % (len(G), np.linalg.matrix_rank(np.array(list(G))), N * N))
raise SystemExit(1 if fails else 0)
