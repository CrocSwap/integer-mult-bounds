"""Full-ring preparation for the retained generic good/fallback normal forms.

Adapted from source527 and PR2160/2159/2171/2188/2207. This module performs
control arithmetic only; it never reads or writes a payload address.
"""
from dataclasses import dataclass
from functools import cached_property, lru_cache
from itertools import product
from math import gcd, prod


def need(test, message):
    if not test:
        raise ValueError(message)


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def mul(a, b, modulus):
    out = [[0] * len(b[0]) for _ in a]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        out[i][j] = (out[i][j] + x * y) % modulus
    return out


def inverse(a, modulus):
    n = len(a)
    rows = [list(row) + e for row, e in zip(a, eye(n))]
    for k in range(n):
        pivot = next((i for i in range(k, n) if gcd(rows[i][k], modulus) == 1), None)
        need(pivot is not None, "unit matrix pivot")
        rows[k], rows[pivot] = rows[pivot], rows[k]
        unit = pow(rows[k][k], -1, modulus)
        rows[k] = [x * unit % modulus for x in rows[k]]
        for i in range(n):
            if i != k and rows[i][k]:
                c = rows[i][k]
                rows[i] = [(x - c * y) % modulus for x, y in zip(rows[i], rows[k])]
    need([row[:n] for row in rows] == eye(n), "matrix inverse endpoint")
    return [row[n:] for row in rows]


@dataclass(frozen=True)
class Header:
    q: int
    width: int
    matrix: tuple
    axes: tuple

    @property
    def modulus(self): return self.q**self.width
    @property
    def dimension(self): return len(self.matrix)
    @cached_property
    def low(self): return tuple(tuple(x % self.q for x in row) for row in self.matrix)
    @cached_property
    def specification(self): return self.q, self.width, self.low, self.axes


@lru_cache(None)
def projection(header):
    a, modulus = header.matrix, header.modulus
    n = header.dimension
    need(1 <= len(header.axes) < n <= 64 and len(set(header.axes)) == len(header.axes)
         and all(0 <= k < n for k in header.axes),
         "projector dimensions")
    need(all(len(row) == n and all(0 <= x < modulus for x in row) for row in a), "header entries")
    gi = inverse(a, modulus)
    return tuple(map(tuple, mul([[row[k] for k in header.axes] for row in a],
                               [gi[k] for k in header.axes], modulus)))


def residual(p, modulus):
    n = len(p)
    out = [[0] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            out[i][j] = (int(i == j) - p[i][j]) % modulus
            out[i][n + j] = p[i][n - 1 - j]
            out[n + i][j] = p[n - 1 - i][j]
            out[n + i][n + j] = (int(i == j) - p[n - 1 - i][n - 1 - j]) % modulus
    return out


@dataclass(frozen=True)
class Good:
    pivots: tuple
    rows: tuple
    columns: tuple
    cross: tuple


@lru_cache(None)
def good(header):
    p, modulus = projection(header), header.modulus
    n, rank = len(p), len(header.axes)
    a = [list(row[::-1]) for row in p]
    left, right, pivots, rows, columns = eye(n), eye(n), [], [], []
    for k in range(rank):
        col = n - 1 - k
        pivot = a[k][col]
        need(gcd(pivot, modulus) == 1, "bad low class")
        pivots.append(pivot)
        pinv = pow(pivot, -1, modulus)
        for i in range(k + 1, n):
            c = -a[i][col] * pinv % modulus
            rows.append((i, k, c))
            a[i] = [(x + c * y) % modulus for x, y in zip(a[i], a[k])]
            left[i] = [(x + c * y) % modulus for x, y in zip(left[i], left[k])]
        for j in range(col):
            c = -a[k][j] * pinv % modulus
            columns.append((col, j, c))
            for i in range(n):
                a[i][j] = (a[i][j] + c * a[i][col]) % modulus
                right[i][j] = (right[i][j] + c * right[i][col]) % modulus
    expected = [[0] * n for _ in range(n)]
    for k, pivot in enumerate(pivots):
        expected[k][n - 1 - k] = pivot
    need(a == expected, "complete full-ring Schur block")
    li, ri = inverse(left, modulus), inverse(right, modulus)
    alpha = [[-x % modulus for x in row] for row in mul(mul(left, p, modulus), li, modulus)[:rank]]
    beta = [[-x % modulus for x in row] for row in mul(ri, [row[:rank] for row in li[::-1]], modulus)]
    cross = [[0] * n for _ in range(n)]
    for k, pivot in enumerate(pivots):
        pinv = pow(pivot, -1, modulus)
        for i in range(n):
            cross[i][k] = (-beta[i][k] - int(i == n - 1 - k) * pinv) % modulus
        for j in range(rank, n):
            cross[n - 1 - k][j] = pinv * alpha[k][j] % modulus
    return Good(tuple(pivots), tuple(rows), tuple(columns), tuple(map(tuple, cross)))


@dataclass(frozen=True)
class Operation:
    kind: str
    target: int
    source: int
    weight_kind: str
    scalar: int = 1
    first: int = 0
    second: int = 0
    permutation: tuple = ()


@dataclass(frozen=True)
class Fallback:
    diagonal: tuple
    permutation: tuple
    operations: tuple


@lru_cache(None)
def fallback(header):
    modulus = header.modulus
    a = residual(projection(header), modulus)
    n = len(a)
    pi, reductions = list(range(n)), []
    for k in range(n):
        pivot = next((i for i in range(k, n) if gcd(a[i][k], modulus) == 1), None)
        need(pivot is not None, "fallback unit pivot")
        if pivot != k:
            reductions.append(("swap", k, pivot, 0, tuple(pi)))
            a[k], a[pivot] = a[pivot], a[k]
            pi[k], pi[pivot] = pi[pivot], pi[k]
        inv = pow(a[k][k], -1, modulus)
        for i in range(n):
            if i != k:
                c = -a[i][k] * inv % modulus
                reductions.append(("add", i, k, c, tuple(pi)))
                a[i] = [(x + c * y) % modulus for x, y in zip(a[i], a[k])]
    need(all(a[i][j] == 0 for i in range(n) for j in range(n) if i != j), "fallback diagonal")
    diagonal = tuple(a[i][i] for i in range(n))
    out = []
    def unit(i, k): return Operation("swap", i, k, "unit")
    for i, value in enumerate(diagonal[:-1]):
        out.extend((unit(i, n - 1), Operation("swap", i, n - 1, "pair", value, i, n - 1, tuple(pi))))
    sign = prod(diagonal) % modulus
    need(sign in (1, modulus - 1), "residual determinant sign")
    if sign != 1:
        out.append(Operation("sign", n - 1, -1, "fixed", -1))
    for kind, i, k, c, snapshot in reversed(reductions):
        if kind == "swap":
            out.append(unit(i, k))
        else:
            op = Operation("lower", max(i, k), min(i, k), "shear", -c % modulus, i, k, snapshot)
            out.extend((op,) if i > k else (unit(i, k), op, unit(i, k)))
    return Fallback(diagonal, tuple(pi), tuple(out))


def lifts(low, q, width, axes=(0,)):
    m = len(low)
    for high in product(range(q**(width - 1)), repeat=m * m):
        matrix = tuple(tuple(low[i][j] + q * high[i * m + j] for j in range(m)) for i in range(m))
        yield Header(q, width, matrix, axes)


def gl2(q):
    return tuple(((a, b), (c, d)) for a, b, c, d in product(range(q), repeat=4)
                 if (a * d - b * c) % q)
