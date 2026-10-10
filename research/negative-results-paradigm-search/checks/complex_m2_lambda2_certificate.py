r"""Exact FO certificate: the complex primitive has no coded saving at m = 2, for ANY frames in GL_4(C),
with ALL monomial matrices free (any invertible diagonal, any permutation of the 4 basis states), arbitrary
complex gate coefficients, and the register (different-frame) model. Standard library only.

FO lemma (README section 2.2, different-frame gates): for a representation rho of the frame group and a subspace Y0 invariant
under the free group B, f(g) = dim(Y0 + rho(g) Y0) - dim Y0 is B-bi-invariant and subadditive, and every network
satisfies sum over paid children of f(child) >= W f(target). If f(child) <= cost(child), then s >= W f(target).

Here rho(g) = conjugation by Lambda^2(g) on End(Lambda^2 C^4) (a rational representation of GL_4).
Lambda^2 C^4 = P_1 + P_2 + P_3 with P_a = span{e_x ^ e_{x xor a}} (one plane per perfect matching of F_2^2).
Y0 = span{Pi_1, Pi_2, Pi_3}, Pi_a the coordinate projector onto P_a. A diagonal matrix acts diagonally on
Lambda^2, so it fixes each Pi_a; a permutation of the four basis states permutes the three perfect matchings, so
it permutes the Pi_a. Hence Y0 is invariant under the whole monomial group.
Verified exactly below: f = 0 on generic diagonals and all 24 permutations; f = 1 for the Hadamard on each of the
three matchings (qubit 1, qubit 2, parity); f(H (x) H) = 2. So s >= 2W = Wm.
Scalars cancel under conjugation, so the integer matrix H = [[1,1],[1,-1]] is used."""
import itertools
from fractions import Fraction as Fr

N = 4
pairs = [(x, y) for x in range(N) for y in range(N) if x < y]
pidx = {p: i for i, p in enumerate(pairs)}


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def inverse(M):
    n = len(M)
    A = [[Fr(v) for v in row] + [Fr(int(i == j)) for j in range(n)] for i, row in enumerate(M)]
    for c in range(n):
        p = next(i for i in range(c, n) if A[i][c] != 0)
        A[c], A[p] = A[p], A[c]
        piv = A[c][c]
        A[c] = [v / piv for v in A[c]]
        for i in range(n):
            if i != c and A[i][c] != 0:
                f = A[i][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[c])]
    return [row[n:] for row in A]


def rank(vectors):
    """rank over Q of a list of equal-length vectors"""
    rows = [[Fr(v) for v in vec] for vec in vectors]
    r = 0
    ncol = len(rows[0])
    for c in range(ncol):
        p = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                f = rows[i][c] / rows[r][c]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        r += 1
    return r


def wedge2(g):
    """matrix of Lambda^2 g in the basis e_x ^ e_y (x < y)"""
    M = [[Fr(0)] * 6 for _ in range(6)]
    for j, (x, y) in enumerate(pairs):
        for i, (u, v) in enumerate(pairs):
            M[i][j] = Fr(g[u][x]) * g[v][y] - Fr(g[u][y]) * g[v][x]
    return M


Pi = {}
for a in (1, 2, 3):
    D = [[Fr(0)] * 6 for _ in range(6)]
    for (x, y) in pairs:
        if x ^ y == a:
            D[pidx[(x, y)]][pidx[(x, y)]] = Fr(1)
    Pi[a] = D


def vec(M):
    return [v for row in M for v in row]


Y0 = [vec(Pi[a]) for a in (1, 2, 3)]
assert rank(Y0) == 3


def f(g):
    L = wedge2(g)
    Li = inverse(L)
    gY = [vec(matmul(matmul(L, Pi[a]), Li)) for a in (1, 2, 3)]
    return rank(Y0 + gY) - 3


def perm_matrix(sig):
    P = [[0] * 4 for _ in range(4)]
    for x in range(4):
        P[sig[x]][x] = 1
    return P


def kron(A, B):
    return [[A[i // 2][j // 2] * B[i % 2][j % 2] for j in range(4)] for i in range(4)]


H2 = [[1, 1], [1, -1]]
I2 = [[1, 0], [0, 1]]
# index x = x1 + 2 x2; kron(A, B) puts A on bit 1 and B on bit 0
H_q1 = kron(I2, H2)                       # matching a = 1
H_q2 = kron(H2, I2)                       # matching a = 2
CNOT = perm_matrix([0, 3, 2, 1])          # a permutation of F_2^2 mapping matching 1 to matching 3
H_par = matmul(matmul(CNOT, H_q1), CNOT)  # Hadamard on the parity matching a = 3
T = kron(H2, H2)

diags = [[[Fr(2), 0, 0, 0], [0, Fr(-3, 5), 0, 0], [0, 0, Fr(7, 3), 0], [0, 0, 0, Fr(11, 13)]],
         [[Fr(5, 7), 0, 0, 0], [0, Fr(13), 0, 0], [0, 0, Fr(-1, 4), 0], [0, 0, 0, Fr(9, 2)]]]
ok_diag = all(f(d) == 0 for d in diags)
ok_perm = all(f(perm_matrix(s)) == 0 for s in itertools.permutations(range(4)))
print('f = 0 on generic diagonals:', ok_diag)
print('f = 0 on all 24 permutations:', ok_perm)
fq1, fq2, fpar, fT = f(H_q1), f(H_q2), f(H_par), f(T)
print('f(H on qubit 1) =', fq1, ' f(H on qubit 2) =', fq2, ' f(H on parity matching) =', fpar)
print('f(H (x) H) =', fT)
assert ok_diag and ok_perm and (fq1, fq2, fpar, fT) == (1, 1, 1, 2)
print('certificate holds: every network at m = 2 has s >= 2W = Wm (no saving)')
