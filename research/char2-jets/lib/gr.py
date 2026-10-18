"""Generic char-2 rank GR(B) = rank of B o (X Y^T) over F2(X,Y), X_tj (j in pi(t)), Y_sj (j in sigma(s)) indeterminates.
cost(B) >= rank_K(B o P~Q~^T) for every support-compatible P~,Q~ over any K of char 2 (Hadamard argument), hence >= GR(B).
A random evaluation over GF(2^16) of full rank v PROVES GR(B) = v (it is an explicit certificate); a deficient evaluation
is only probabilistic evidence (Schwartz-Zippel, error <= v/2^16 per trial)."""
import random
POLY = 0x1100B; Q = 1 << 16
EXP = [0] * (2 * Q); LOG = [0] * Q
x = 1
for i in range(Q - 1):
    EXP[i] = x; LOG[x] = i
    x <<= 1
    if x & Q: x ^= POLY
for i in range(Q - 1, 2 * Q): EXP[i] = EXP[i - (Q - 1)]
def mul(a, b):
    return 0 if a == 0 or b == 0 else EXP[LOG[a] + LOG[b]]
def inv(a): return EXP[(Q - 1) - LOG[a]]
def rank(M):
    M = [r[:] for r in M]; n = len(M); m = len(M[0]) if M else 0; r = 0
    for c in range(m):
        p = next((i for i in range(r, n) if M[i][c]), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; iv = inv(M[r][c])
        M[r] = [mul(iv, e) for e in M[r]]
        for i in range(n):
            if i != r and M[i][c]:
                f = M[i][c]; M[i] = [e ^ mul(f, g) for e, g in zip(M[i], M[r])]
        r += 1
    return r
def gr(B, pi, sig, trials=3, rng=random):
    v = len(B); best = 0
    for _ in range(trials):
        X = [[rng.randrange(1, Q) if j in pi[t] else 0 for j in range(3)] for t in range(v)]
        Y = [[rng.randrange(1, Q) if j in sig[s] else 0 for j in range(3)] for s in range(v)]
        N = [[(mul(X[t][0], Y[s][0]) ^ mul(X[t][1], Y[s][1]) ^ mul(X[t][2], Y[s][2])) if B[t][s] else 0 for s in range(v)] for t in range(v)]
        best = max(best, rank(N))
        if best == v: break
    return best
