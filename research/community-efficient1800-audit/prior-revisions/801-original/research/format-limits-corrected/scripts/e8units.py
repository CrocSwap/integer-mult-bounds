"""Geometry shared by the E8 / paired-cube checks of research/format-limits: exact linear algebra over F_2 and Q,
the 120 root lines of E8, and the 9-bit labels of a complex or bit unit.  Everything is generated here; nothing is
read from a file.

Conventions.  A 'unit' on v ports has an integer Gram matrix G (diagonal 2 for E8) and F_2 labels u_T in F_2^c with
U U^T = (J + G) mod 2, i.e. <u_S, u_T> = 1 + G_ST (mod 2).  Vectors of F_2^n are Python integers (bit j = coordinate j)
or 0/1 numpy rows; both representations are used below and the function names say which.
Two coordinate systems of the same 120 E8 root lines are provided.  standard_e8(): doubled standard coordinates
(roots +-2e_i +-2e_j and the half-integer (+-1)^8 with an even number of minus signs, G = L L^T/4); the totals
'coordinate a' used for the complex decoder are the 78 lines with a nonzero a-th coordinate.  hamming_e8(): lines
numbered as in the Hamming-code construction:
  lines 0..7    : the coordinate lines 2 e_a,
  lines 8..119  : the 112 'code lines', for each of the 14 weight-4 words of the extended Hamming code [8,4,4]
                  (support i0<i1<i2<i3) the 8 sign patterns (+1, +-1, +-1, +-1) on the support.
Roots are these vectors up to sign (norm 4 in these coordinates, so G = L L^T / 2 has diagonal 2 and off-diagonal
0, +-1).
"""
import itertools
import math

import numpy as np


# ---------------------------------------------------------------------------------------------------------------
# F_2 linear algebra on bit-packed rows
def f2_rows(M):
    """rows of a 0/1 matrix as Python integers (bit j of row i = M[i, j])."""
    M = np.asarray(M).astype(np.uint8) & 1
    if M.shape[1] == 0:
        return [0] * M.shape[0]
    P = np.packbits(M, axis=1, bitorder='little')
    return [int.from_bytes(r.tobytes(), 'little') for r in P]


def f2_rank_rows(rows):
    basis = {}
    for x in rows:
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                break
    return len(basis)


def f2_rank(M):
    return f2_rank_rows(f2_rows(M))


def f2_row_basis_idx(M):
    """indices of a maximal independent set of rows, chosen greedily in order."""
    rows = f2_rows(M)
    basis, idx = {}, []
    for i, x in enumerate(rows):
        y = x
        while y:
            h = y.bit_length() - 1
            if h in basis:
                y ^= basis[h]
            else:
                basis[h] = y
                idx.append(i)
                break
    return idx


def orthonormal_basis_f2(N):
    """N: nonsingular symmetric non-alternating c x c matrix over F_2.  Rows of the result B form a basis with
    B N B^T = I."""
    N = (np.array(N, dtype=np.uint8) & 1).astype(np.int64)
    c = len(N)

    def residual(basis):
        Z = np.eye(c, dtype=np.int64)
        for b in basis:
            Z = (Z + np.outer((Z @ N @ b) % 2, b)) % 2
        return Z
    basis = []
    Z = np.eye(c, dtype=np.int64)
    q = np.array([int(Z[i] @ N @ Z[i]) % 2 for i in range(c)])
    while len(basis) < c:
        cand = np.nonzero(q)[0]
        if len(cand):
            b = Z[cand[0]].copy()
            basis.append(b)
            t = (Z @ N @ b) % 2
            Z = (Z + np.outer(t, b)) % 2            # project every residual vector off b (b N b = 1)
            q = (q + t) % 2
            continue
        # the residual space is alternating: absorb a hyperbolic pair with the first basis vector
        assert basis, 'form is alternating'
        nzrows = [i for i in range(c) if Z[i].any()]
        x = Z[nzrows[0]]
        y = next(Z[i] for i in nzrows[1:] if (x @ N @ Z[i]) % 2)
        u = basis.pop(0)
        basis += [(u + x) % 2, (u + y) % 2, (u + x + y) % 2]
        Z = residual(basis)
        q = np.array([int(Z[i] @ N @ Z[i]) % 2 for i in range(c)])
    B = np.array(basis, dtype=np.uint8)
    assert ((B.astype(np.int64) @ N @ B.T.astype(np.int64)) % 2 == np.eye(c, dtype=np.int64)).all()
    return B


def sym_factor_f2(M):
    """M symmetric over F_2 with all-ones diagonal: U (v x c), c = rank M, with U U^T = M (mod 2).  Deterministic:
    c greedily chosen independent rows, then an orthonormal basis of their (non-alternating) Gram block."""
    M = np.asarray(M).astype(np.uint8) & 1
    I = f2_row_basis_idx(M)
    N = M[np.ix_(I, I)]
    B = orthonormal_basis_f2(N)
    U = (M[:, I].astype(np.int64) @ B.T.astype(np.int64)) % 2
    assert ((U @ U.T) % 2 == M).all()
    return U.astype(np.uint8)


# bit-integer helpers (vectors of F_2^n as integers)
def dot2(a, b):
    return bin(a & b).count('1') & 1


def span_basis(vecs):
    """sorted (decreasing) echelon basis of the span of the integers vecs."""
    b = []
    for u in vecs:
        for x in b:
            if u ^ x < u:
                u ^= x
        if u:
            b.append(u)
            b.sort(reverse=True)
    return b


def rows_to_int(row):
    """0/1 sequence -> integer with bit j = row[j]."""
    return sum(int(x) << j for j, x in enumerate(row))


# ---------------------------------------------------------------------------------------------------------------
# exact rank over Q
def _reduce_int(r, pc, rr):
    """r - (r[pc]/rr[pc]) rr, scaled to stay integral and divided by the content."""
    f, g = r[pc], rr[pc]
    r = [g * x - f * y for x, y in zip(r, rr)]
    c = math.gcd(*r)
    return [x // c for x in r] if c > 1 else r


def rank_q(rows):
    """exact rank over Q of a list of integer rows (fraction-free elimination)."""
    red = []                                  # (pivot column, row)
    for r in rows:
        r = [int(x) for x in r]
        for pc, rr in red:
            if r[pc] != 0:
                r = _reduce_int(r, pc, rr)
        pc = next((j for j, x in enumerate(r) if x != 0), None)
        if pc is not None:
            red.append((pc, r))
    return len(red)


def row_basis_idx_q(rows):
    """indices of a maximal independent set of rows over Q (greedy, in order)."""
    chosen, red = [], []
    for i, r in enumerate(rows):
        r = [int(x) for x in r]
        for pc, rr in red:
            if r[pc] != 0:
                r = _reduce_int(r, pc, rr)
        pc = next((j for j, x in enumerate(r) if x != 0), None)
        if pc is not None:
            red.append((pc, r))
            chosen.append(i)
    return chosen


def gram_rank_q(L, Q, S):
    """rank over Q of the Gram block L_S Q L_S^T (L integer v x h, Q integer h x h, S index list), computed on a
    row basis B of L_S: rank(L_S Q L_S^T) = rank(B Q B^T) because L_S = C B with C of full column rank."""
    LS = [[int(x) for x in L[s]] for s in S]
    idx = row_basis_idx_q(LS)
    if not idx:
        return 0
    B = [LS[i] for i in idx]
    Qm = [[int(x) for x in row] for row in Q]
    BQ = [[sum(b[k] * Qm[k][j] for k in range(len(b))) for j in range(len(Qm[0]))] for b in B]
    BQBt = [[sum(x * y for x, y in zip(bq, b2)) for b2 in B] for bq in BQ]
    return rank_q(BQBt)


# ---------------------------------------------------------------------------------------------------------------
# E8
def hamming_e8():
    """(L, G): L = 120 x 8 integer root lines (norm 4), G = L L^T / 2 (diagonal 2, off-diagonal 0, +-1)."""
    gen = np.array([[1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0], [0, 0, 0, 0, 1, 1, 1, 1],
                    [0, 1, 0, 1, 0, 1, 0, 1]])
    code = {tuple((np.array(c) @ gen) % 2) for c in itertools.product([0, 1], repeat=4)}
    w4 = sorted(c for c in code if sum(c) == 4)
    assert len(w4) == 14
    L = [tuple(2 * (np.arange(8) == a).astype(int)) for a in range(8)]
    for c in w4:
        idx = [i for i in range(8) if c[i]]
        for sg in itertools.product([1, -1], repeat=3):
            x = np.zeros(8, dtype=int)
            x[idx[0]] = 1
            for k in range(3):
                x[idx[k + 1]] = sg[k]
            L.append(tuple(x))
    L = np.array(L, dtype=np.int64)
    G = L @ L.T
    assert (G % 2 == 0).all()
    G = G // 2
    assert len(L) == 120 and set(np.diag(G)) == {2} and set(G[~np.eye(120, dtype=bool)].tolist()) == {-1, 0, 1}
    return L, G


def standard_e8():
    """(L, G): the 120 root lines of E8 in doubled standard coordinates (norm 8), G = L L^T / 4.  Lines 0..55 are
    +-2e_i +-2e_j (i<j, pair order, signs (+,+) and (+,-)); lines 56..119 are the (+-1)^8 with an even number of minus
    signs, one of each pair {x, -x}, in lexicographic order of the sign tuples."""
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (2, -2):
            for sj in (2, -2):
                r = [0] * 8
                r[i], r[j] = si, sj
                roots.append(tuple(r))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0:
            roots.append(s)
    seen, lines = set(), []
    for r in roots:
        if tuple(-x for x in r) in seen or r in seen:
            continue
        seen.add(r)
        lines.append(r)
    L = np.array(lines, dtype=np.int64)
    G4 = L @ L.T
    assert len(L) == 120 and (G4 % 4 == 0).all()
    G = G4 // 4
    assert set(np.diag(G)) == {2} and set(G[~np.eye(120, dtype=bool)].tolist()) == {-1, 0, 1}
    return L, G


def e8_labels(G):
    """9-bit F_2 labels (120 x 9 uint8, U U^T = (J + G) mod 2) of the E8 lines by the deterministic factorisation."""
    M = ((1 + G) % 2).astype(np.uint8)
    U = sym_factor_f2(M)
    assert U.shape[1] == 9 and ((U.astype(int) @ U.T.astype(int)) % 2 == M).all()
    return U


# ---------------------------------------------------------------------------------------------------------------
def first_clique(adj, size):
    """lexicographically first clique of the given size in the graph with 0/1 adjacency matrix adj (list of lists /
    array); None if there is none."""
    n = len(adj)
    nb = [sum(1 << j for j in range(n) if adj[i][j]) for i in range(n)]

    def rec(cl, cand):
        if len(cl) == size:
            return cl
        if len(cl) + bin(cand).count('1') < size:
            return None
        while cand:
            i = (cand & -cand).bit_length() - 1
            cand &= ~(1 << i)
            r = rec(cl + [i], cand & nb[i])
            if r:
                return r
        return None
    return rec([], (1 << n) - 1)
