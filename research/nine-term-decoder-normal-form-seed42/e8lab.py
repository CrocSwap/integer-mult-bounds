# SPDX-License-Identifier: Apache-2.0
"""Exact E8 / label / rational linear-algebra helpers for the nine-term normal-form package.

Standard library only.  Written independently of the PR968/PR1077/PR1180 checkers: the 120 E8 lines
are generated here, the binary label pairing is (<r_i, r_j> + 1) mod 2 (PR717 B14 / PR968 eq. (1)),
and every rank over Q is computed with exact Fractions.
"""
import itertools
from fractions import Fraction as Q

# ------------------------------------------------------------------ E8 lines (doubled coordinates)


def _roots240():
    out = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0] * 8
                v[i], v[j] = 2 * si, 2 * sj
                out.append(tuple(v))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0:
            out.append(tuple(s))
    return out


ROOTS240 = _roots240()


def _canon(v):
    for a in v:
        if a:
            return tuple(v) if a > 0 else tuple(-x for x in v)
    raise ValueError('zero vector')


LINES = sorted({_canon(v) for v in ROOTS240}, reverse=True)
N = len(LINES)
FULL = (1 << N) - 1


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def gram(i, j):
    """True inner product of the norm-2 representatives of lines i, j."""
    return dot(LINES[i], LINES[j]) // 4


G = [[gram(i, j) for j in range(N)] for i in range(N)]
# label pairing rows as bitsets: bit j of M[i] is (G_ij + 1) mod 2
M = [sum(((G[i][j] + 1) & 1) << j for j in range(N)) for i in range(N)]


def bits(mask):
    i = 0
    while mask:
        if mask & 1:
            yield i
        mask >>= 1
        i += 1


def popcount(x):
    return bin(x).count('1')


def f2_rank(rows):
    piv = {}
    r = 0
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in piv:
                v ^= piv[h]
            else:
                piv[h] = v
                r += 1
                break
    return r


def pairing_rank(X, Y):
    """Theorem C cost of a term: F2 rank of the label pairing between line sets X and Y (bitmasks)."""
    return f2_rank([M[i] & Y for i in bits(X)])


def label_dim(X):
    """dim of the label span V_X (= rank of the pairing rows of X against all lines)."""
    return f2_rank([M[i] for i in bits(X)])


def support(vec, live=FULL):
    """Live lines not orthogonal to the (rational) vector vec."""
    m = 0
    for i in bits(live):
        if sum(Q(a) * b for a, b in zip(LINES[i], vec)) != 0:
            m |= 1 << i
    return m


def code_words():
    """The 511 nonzero codewords (supports of nonzero label functionals) as bitmasks."""
    piv = {}
    basis = []
    for v in M:
        w = v
        while w:
            h = w.bit_length() - 1
            if h in piv:
                w ^= piv[h]
            else:
                piv[h] = w
                basis.append(v)
                break
    words = []
    for c in range(1, 1 << len(basis)):
        w = 0
        for t in range(len(basis)):
            if c >> t & 1:
                w ^= basis[t]
        words.append(w)
    return basis, words


# ------------------------------------------------------------------ exact linear algebra over Q


def q_rank(rows):
    rows = [[Q(x) for x in r] for r in rows]
    if not rows:
        return 0
    ncol = len(rows[0])
    r = 0
    for c in range(ncol):
        p = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        pv = rows[r][c]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                f = rows[i][c] / pv
                rows[i] = [x - f * y for x, y in zip(rows[i], rows[r])]
        r += 1
        if r == len(rows):
            break
    return r


def line_rank(mask):
    """Real rank of the root vectors of the lines in mask (integer elimination)."""
    rows = [list(LINES[i]) for i in bits(mask)]
    r = 0
    for c in range(8):
        p = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                a, b = rows[r][c], rows[i][c]
                rows[i] = [a * x - b * y for x, y in zip(rows[i], rows[r])]
        r += 1
        if r == 8:
            break
    return r


def q_inv(A):
    n = len(A)
    Mx = [[Q(x) for x in row] + [Q(int(i == j)) for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        p = next(r for r in range(c, n) if Mx[r][c] != 0)
        Mx[c], Mx[p] = Mx[p], Mx[c]
        pv = Mx[c][c]
        Mx[c] = [x / pv for x in Mx[c]]
        for r in range(n):
            if r != c and Mx[r][c] != 0:
                f = Mx[r][c]
                Mx[r] = [x - f * y for x, y in zip(Mx[r], Mx[c])]
    return [row[n:] for row in Mx]


def q_nullspace(A, ncol):
    """Basis of {x : A x = 0} for a list of rows A with ncol columns."""
    rows = [[Q(x) for x in r] for r in A]
    pivots = []
    r = 0
    for c in range(ncol):
        p = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        pv = rows[r][c]
        rows[r] = [x / pv for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                f = rows[i][c]
                rows[i] = [x - f * y for x, y in zip(rows[i], rows[r])]
        pivots.append(c)
        r += 1
    free = [c for c in range(ncol) if c not in pivots]
    basis = []
    for f in free:
        x = [Q(0)] * ncol
        x[f] = Q(1)
        for i, c in enumerate(pivots):
            x[c] = -rows[i][f]
        basis.append(x)
    return basis


def matmul(A, B):
    Bt = list(zip(*B))
    return [[sum((a * b for a, b in zip(row, col)), Q(0)) for col in Bt] for row in A]


def transpose(A):
    return [list(r) for r in zip(*A)]


# ------------------------------------------------------------------ root subsystems and weight frames


def simple_chain(n, orth_to=()):
    """Deterministic A_n simple-root chain (roots in doubled coords), orthogonal to the given vectors."""
    nb = {v: [w for w in ROOTS240 if dot(v, w) == -4] for v in ROOTS240}
    for start in ROOTS240:
        if any(dot(start, a) for a in orth_to):
            continue
        stack = [[start]]
        while stack:
            ch = stack.pop()
            if len(ch) == n:
                return ch
            for w in nb[ch[-1]]:
                if w not in ch and all(dot(w, u) == 0 for u in ch[:-1]) and all(dot(w, a) == 0 for a in orth_to):
                    stack.append(ch + [w])
    raise ValueError('no chain')


def an_weights(chain):
    """The n+1 weights of the vector representation of A_n: w_1 - w_2 = a_1, ..., sum w = 0."""
    n = len(chain)
    w1 = [Q(0)] * 8
    for t, a in enumerate(chain):
        for c in range(8):
            w1[c] += Q(n - t, n + 1) * a[c]
    W = [tuple(w1)]
    for a in chain:
        W.append(tuple(x - y for x, y in zip(W[-1], a)))
    return W


def root_basis_orthogonal_to(vecs, size):
    out = []
    for v in ROOTS240:
        if all(dot(v, u) == 0 for u in vecs) and q_rank(out + [list(v)]) > len(out):
            out.append(list(v))
        if len(out) == size:
            return [tuple(x) for x in out]
    raise ValueError('basis not found')
