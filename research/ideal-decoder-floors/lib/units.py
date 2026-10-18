"""Root units as exact integer data (coordinates scaled by 2, so every root has norm 8 and the Gram entry of two roots is dot/4),
the dense pairing B (B_ts = 1 iff t = s or r_t _|_ r_s), exact coordinate/frame decoders and their F2 cost.  Standard library only."""
import itertools
from fractions import Fraction as Fr
from exact import rank_f2, dot


def e8_lines():
    """The 120 lines of E8 (one root per +- pair), coordinates doubled: +-2e_i +-2e_j (i<j, first sign +), and (1, +-1, ..., +-1) with an
    even number of minus signs (64 lines); norm 8."""
    L = []
    for i, j in itertools.combinations(range(8), 2):
        for s in (1, -1):
            v = [0] * 8
            v[i] = 2
            v[j] = 2 * s
            L.append(tuple(v))
    for signs in itertools.product((1, -1), repeat=7):
        v = [1] + list(signs)
        if v.count(-1) % 2 == 0:
            L.append(tuple(v))
    assert len(L) == 120
    return L


def dn_lines(n):
    L = []
    for i, j in itertools.combinations(range(n), 2):
        for s in (1, -1):
            v = [0] * n
            v[i] = 2
            v[j] = 2 * s
            L.append(tuple(v))
    return L


def gram(L):
    """Integer Gram matrix of unit roots (dot of the doubled coordinates, divided by 4): diagonal 2, off-diagonal 0, +-1 (+-2 never occurs)."""
    n = len(L)
    G = [[0] * n for _ in range(n)]
    for a in range(n):
        for b in range(n):
            d = dot(L[a], L[b])
            assert d % 4 == 0
            G[a][b] = d // 4
    return G


def orth_sub(L, vs):
    return [r for r in L if all(dot(r, x) == 0 for x in vs)]


E8 = e8_lines()
_r0 = (2, 2, 0, 0, 0, 0, 0, 0)
_r1 = (0, -2, 2, 0, 0, 0, 0, 0)
assert dot(_r0, _r1) == -4
E7 = orth_sub(E8, [_r0])
E6 = orth_sub(E8, [_r0, _r1])
UNITS = {'D4': (dn_lines(4), 4), 'D5': (dn_lines(5), 5), 'D6': (dn_lines(6), 6),
         'E6': (E6, 6), 'E7': (E7, 7), 'E8': (E8, 8)}


def bmasks(G):
    """Dense B as bit rows: B_ts = 1 iff t == s or G_ts == 0."""
    n = len(G)
    return [sum(1 << s for s in range(n) if s == t or G[t][s] == 0) for t in range(n)]


def block_rank(Brows, R, A):
    mask = sum(1 << s for s in A)
    return rank_f2([Brows[t] & mask for t in R])


def first_frame(G, size, avoid=()):
    """Lexicographically first set of `size` pairwise orthogonal lines avoiding `avoid` (None if none)."""
    n = len(G)
    avoid = set(avoid)

    def ext(cur, start):
        if len(cur) == size:
            return cur
        for i in range(start, n):
            if i in avoid:
                continue
            if all(G[i][j] == 0 for j in cur):
                r = ext(cur + [i], i + 1)
                if r:
                    return r
        return None
    return ext([], 0)


def inv_matrix(M):
    T = len(M)
    A = [[Fr(x) for x in row] + [Fr(int(i == j)) for j in range(T)] for i, row in enumerate(M)]
    for c in range(T):
        p = next(r for r in range(c, T) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        pv = A[c][c]
        A[c] = [x / pv for x in A[c]]
        for r in range(T):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [row[T:] for row in A]


def decoder(live_roots, basis):
    """Exact Gram decoder of the unit `live_roots` (true coordinates = doubled / 2) in the basis `basis` (true coordinates, T vectors
    spanning the roots): q(t)_j = <r_t, a_j>, p(t) = Gram(basis)^-1 q(t); then P Q^T = Gram exactly.  Returns P, Q (lists of rows of Fractions)."""
    T = len(basis)
    Gb = [[dot(a, b) for b in basis] for a in basis]
    Gi = inv_matrix(Gb)
    P, Q = [], []
    for r2 in live_roots:
        r = [Fr(x, 2) for x in r2]
        q = [dot(r, a) for a in basis]
        p = [sum(Gi[j][k] * q[k] for k in range(T)) for j in range(T)]
        assert all(sum(p[j] * basis[j][i] for j in range(T)) == r[i] for i in range(len(r))), 'root not in span of the basis'
        P.append(p)
        Q.append(q)
    return P, Q


def gram_exact(live_roots, P, Q):
    """P Q^T equals the Gram matrix of the (unit-norm-2) roots, entry by entry."""
    n, T = len(P), len(P[0])
    for t in range(n):
        for s in range(n):
            if sum(P[t][j] * Q[s][j] for j in range(T)) != Fr(dot(live_roots[t], live_roots[s]), 4):
                return False
    return True


def decoder_cost(live_roots, basis):
    """(exact?, cost, per-term ranks) of the decoder of `live_roots` in `basis` with the dense pairing B of the unit."""
    P, Q = decoder(live_roots, basis)
    ok = gram_exact(live_roots, P, Q)
    G = gram(live_roots)
    Br = bmasks(G)
    n, T = len(P), len(P[0])
    ranks = []
    for j in range(T):
        R = [t for t in range(n) if P[t][j] != 0]
        A = [t for t in range(n) if Q[t][j] != 0]
        ranks.append(block_rank(Br, R, A))
    return ok, sum(ranks), ranks, P, Q


def true(r2):
    return [Fr(x, 2) for x in r2]


def unit_vectors(n):
    return [[Fr(int(i == j)) for j in range(n)] for i in range(n)]
