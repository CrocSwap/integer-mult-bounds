"""Exact T-block decoders of root units and F2 costs.  decoder(L, basis): P = coordinates of each root line in the chosen basis of the unit,
Q = P . Gram(basis) (exact Fractions), so that M = P Q^T = Gram(L) (coordinates scaled by 2, entries are 4 <r_t, r_s>).  The F2 cost of an admissible B
is sum_j rank_F2 B[R_j, A_j] with R_j = supp p_j, A_j = supp q_j (Theorem C without the floor)."""
from fractions import Fraction as F
from roots import dot
def solve_coords(basis, r):
    """exact coordinates x with sum_i x_i basis_i = r (basis independent rows): Gaussian elimination over Q."""
    n = len(basis); m = len(r)
    M = [[F(basis[i][k]) for i in range(n)] + [F(r[k])] for k in range(m)]
    piv = []; row = 0
    for c in range(n):
        p = next((i for i in range(row, m) if M[i][c] != 0), None)
        if p is None: raise ValueError('dependent basis')
        M[row], M[p] = M[p], M[row]; M[row] = [x / M[row][c] for x in M[row]]
        for i in range(m):
            if i != row and M[i][c] != 0:
                f = M[i][c]; M[i] = [a - f * b for a, b in zip(M[i], M[row])]
        row += 1
    for i in range(n, m): assert M[i][n] == 0, 'vector not in span'
    return [M[i][n] for i in range(n)]
def first_basis(L):
    idx = []; cur = []
    for i, r in enumerate(L):
        try:
            solve_coords(cur + [r], r) if False else None
        except Exception: pass
        if rank(cur + [r]) > len(cur): idx.append(i); cur.append(r)
    return idx
def rank(rows):
    M = [[F(x) for x in r] for r in rows]; rk = 0
    if not M: return 0
    for c in range(len(M[0])):
        p = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]
        for i in range(rk + 1, len(M)):
            if M[i][c] != 0:
                f = M[i][c] / M[rk][c]; M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        rk += 1
    return rk
def decoder(L, bidx):
    basis = [L[i] for i in bidx]; n = len(basis)
    C = [[dot(basis[i], basis[k]) for k in range(n)] for i in range(n)]
    P = [solve_coords(basis, r) for r in L]
    Q = [[sum(P[t][i] * C[i][k] for i in range(n)) for k in range(n)] for t in range(len(L))]
    return P, Q
def exact(L, P, Q):
    v = len(L)
    return all(sum(P[t][j] * Q[s][j] for j in range(len(P[0]))) == dot(L[t], L[s]) for t in range(v) for s in range(v))
def rank2(rows):
    piv = []
    for x in rows:
        for p in piv: x = min(x, x ^ p)
        if x: piv.append(x); piv.sort(reverse=True)
    return len(piv)
def block_ranks(P, Q, B):
    v = len(P); T = len(P[0]); out = []
    for j in range(T):
        R = [t for t in range(v) if P[t][j] != 0]; A = [s for s in range(v) if Q[s][j] != 0]
        out.append(rank2([sum(B[t][s] << i for i, s in enumerate(A)) for t in R]))
    return out
def b0(L):
    """full orthogonal pattern: B_ts = 1 iff t = s or r_t orthogonal to r_s."""
    v = len(L); return [[1 if (t == s or dot(L[t], L[s]) == 0) else 0 for s in range(v)] for t in range(v)]
def admissible(L, B):
    v = len(L); return all(B[t][t] == 1 and all(B[t][s] == 0 or dot(L[t], L[s]) == 0 for s in range(v) if s != t) for t in range(v))
def decoder_std(L):
    """standard coordinates (basis e_1..e_n, Gram 4I in the x2 scaling): P = Q = the root coordinates; M = P Q^T = <r_t, r_s>."""
    return [[F(x) for x in r] for r in L], [[F(x) for x in r] for r in L]
