"""Exact lower-lower Bruhat factorization A = L1 * Mon * L2 (L1, L2 lower triangular, Mon monomial)
by elimination, plus helpers. Rows top-to-bottom; pivot = rightmost nonzero entry of the current row."""
from fractions import Fraction as Q

def ident(n): return [[Q(int(i == j)) for j in range(n)] for i in range(n)]
def mul(A, B):
    Bt = list(zip(*B))
    return [[sum((a*b for a, b in zip(r, c) if a and b), Q(0)) for c in Bt] for r in A]
def rank(M):
    M = [r[:] for r in M]; rk = 0; cols = len(M[0]) if M else 0
    for c in range(cols):
        piv = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if piv is None: continue
        M[rk], M[piv] = M[piv], M[rk]
        for i in range(rk+1, len(M)):
            if M[i][c] != 0:
                f = M[i][c]/M[rk][c]; M[i] = [a-f*b for a, b in zip(M[i], M[rk])]
        rk += 1
    return rk
def inv(M):
    n = len(M); A = [r[:]+[Q(int(i == j)) for j in range(n)] for i, r in enumerate(M)]
    for c in range(n):
        p = next(i for i in range(c, n) if A[i][c] != 0); A[c], A[p] = A[p], A[c]
        f = A[c][c]; A[c] = [x/f for x in A[c]]
        for i in range(n):
            if i != c and A[i][c] != 0:
                g = A[i][c]; A[i] = [a-g*b for a, b in zip(A[i], A[c])]
    return [r[n:] for r in A]

def bruhat(A, track=True):
    """Return (piv, L1, Mon, L2) with A = L1 Mon L2; piv[i] = column of row i's pivot."""
    n = len(A); M = [r[:] for r in A]
    L1 = ident(n) if track else None; L2 = ident(n) if track else None
    piv = [None]*n
    for i in range(n):
        c = max((j for j in range(n) if M[i][j] != 0), default=None)
        if c is None: raise ValueError('singular')
        piv[i] = c; a = M[i][c]
        for k in range(i+1, n):                     # rows below: row_k -= f row_i  (left lower op)
            if M[k][c] != 0:
                f = M[k][c]/a; M[k] = [x-f*y for x, y in zip(M[k], M[i])]
                if track:                           # L1 <- L1 (I + f e_k e_i^T): col_i += f col_k
                    for r in range(n):
                        if L1[r][k]: L1[r][i] += f*L1[r][k]
        for j in range(c):                          # cols left: col_j -= g col_c  (right lower op)
            if M[i][j] != 0:
                g = M[i][j]/a
                for r in range(n):
                    if M[r][c]: M[r][j] -= g*M[r][c]
                if track:                           # L2 <- (I + g e_c e_j^T) L2: row_c += g row_j
                    L2[c] = [x+g*y for x, y in zip(L2[c], L2[j])]
    assert sorted(piv) == list(range(n))
    return piv, L1, M, L2

def swapmat(p):
    m = len(p)
    return [[Q(int(i == j))-p[i][j] for j in range(m)]+[p[i][j] for j in range(m)] for i in range(m)] + \
           [[p[i][j] for j in range(m)]+[Q(int(i == j))-p[i][j] for j in range(m)] for i in range(m)]

def predicted(p_corner_perm, m, k):
    """Predicted involution: H_l <-> D_sigma(l) (l in L), H_i <-> D_i (i in M), fixed elsewhere."""
    w = list(range(2*m))
    for l, r in p_corner_perm.items(): w[l] = m+r; w[m+r] = l
    for i in range(k, m-k): w[i] = m+i; w[m+i] = i
    return w
