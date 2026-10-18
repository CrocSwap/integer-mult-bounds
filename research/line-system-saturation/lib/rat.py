"""Exact rational matrices (Fractions) for the generic-frame constructions."""
from fractions import Fraction as Fr


def matmul(A, B):
    return [[sum(a * b for a, b in zip(r, c)) for c in zip(*B)] for r in A]


def inv(M):
    n = len(M)
    A = [[Fr(x) for x in r] + [Fr(int(i == j)) for j in range(n)] for i, r in enumerate(M)]
    for c in range(n):
        p = next(i for i in range(c, n) if A[i][c] != 0)
        A[c], A[p] = A[p], A[c]
        iv = 1 / A[c][c]
        A[c] = [x * iv for x in A[c]]
        for i in range(n):
            if i != c and A[i][c] != 0:
                f = A[i][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[c])]
    return [r[n:] for r in A]


def cayley(T, rng, den=7):
    """A rational orthogonal matrix (I - S)(I + S)^(-1), S skew with small random rational entries."""
    S = [[Fr(0)] * T for _ in range(T)]
    for i in range(T):
        for j in range(i + 1, T):
            x = Fr(rng.randint(-den, den), rng.randint(1, den))
            S[i][j], S[j][i] = x, -x
    I = [[Fr(int(i == j)) for j in range(T)] for i in range(T)]
    A = [[I[i][j] - S[i][j] for j in range(T)] for i in range(T)]
    B = [[I[i][j] + S[i][j] for j in range(T)] for i in range(T)]
    O = matmul(A, inv(B))
    Ot = [list(r) for r in zip(*O)]
    P = matmul(Ot, O)
    assert P == I, "not orthogonal"
    return O
