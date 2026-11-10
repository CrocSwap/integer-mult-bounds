"""Exact finite witnesses. Produced by Nick Petalas. Apache-2.0."""

from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def walsh(t):
    require(type(t) is int and 0 <= t <= 6, "finite witness exponent outside 0..6")
    n = 1 << t
    return [[(-1) ** ((x & y).bit_count()) for y in range(n)] for x in range(n)]


def rank(matrix, prime=None):
    require(0 < len(matrix) <= 64, "invalid row count")
    width = len(matrix[0])
    require(0 < width <= 64 and all(len(r) == width for r in matrix), "invalid shape")
    require(prime in (None, 101), "only the documented modular control is admitted")
    a = [[Fraction(v) if prime is None else int(v) % prime for v in r] for r in matrix]
    pivot_row = 0
    for col in range(width):
        candidates = [r for r in range(pivot_row, len(a)) if a[r][col]]
        if not candidates:
            continue
        p = candidates[0]
        a[pivot_row], a[p] = a[p], a[pivot_row]
        inv = 1 / a[pivot_row][col] if prime is None else pow(a[pivot_row][col], -1, prime)
        a[pivot_row] = [v * inv if prime is None else v * inv % prime for v in a[pivot_row]]
        for r in range(pivot_row + 1, len(a)):
            scale = a[r][col]
            a[r] = [v - scale * w if prime is None else (v - scale * w) % prime
                    for v, w in zip(a[r], a[pivot_row])]
        pivot_row += 1
        if pivot_row == len(a):
            break
    return pivot_row


def matmul(a, b):
    require(0 < len(a) <= 64 and 0 < len(b) <= 64, "invalid product rows")
    require(all(len(r) == len(b) for r in a), "incompatible product")
    require(0 < len(b[0]) <= 64 and all(len(r) == len(b[0]) for r in b), "ragged product")
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def witness(t):
    require(type(t) is int and 2 <= t <= 6, "sharp family exponent outside 2..6")
    n, m = 1 << t, 1 << (t - 2)
    h = walsh(t)
    permutation = [([0, 2, 1, 3][j // m]) * m + j % m for j in range(n)]
    f = [[row[j] for j in permutation] for row in h]
    u = (1, -1, 1, 1)
    q = [[Fraction(int(i == j)) - Fraction(u[i // m] * u[j // m], 2) * (i % m == j % m)
          for j in range(n)] for i in range(n)]
    target = matmul(q, f)
    return f, q, target, permutation


def independent_target(t):
    require(type(t) is int and 2 <= t <= 6, "target exponent outside 2..6")
    n, m = 1 << t, 1 << (t - 2)
    h = walsh(t - 2)
    partner = (1, 0, 3, 2)
    return [[(2 if i // m < 2 else -2) * h[i % m][j % m]
             if j // m == partner[i // m] else 0 for j in range(n)] for i in range(n)]
