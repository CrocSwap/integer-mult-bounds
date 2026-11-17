"""Bounded exact rational matrix operations for the finite checker."""

from fractions import Fraction as F

Matrix = tuple[tuple[F, ...], ...]
LIMIT = 32


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def matrix(rows) -> Matrix:
    out = tuple(tuple(F(x) for x in row) for row in rows)
    require(0 < len(out) <= LIMIT, "matrix row capacity")
    require(len(out[0]) <= LIMIT, "matrix column capacity")
    require(all(len(row) == len(out[0]) for row in out), "ragged matrix")
    return out


def zero(n: int, m: int) -> Matrix:
    return matrix([[0] * m for _ in range(n)])


def eye(n: int) -> Matrix:
    return matrix([[int(i == j) for j in range(n)] for i in range(n)])


def tr(a: Matrix) -> Matrix:
    require(bool(a[0]), "cannot transpose a zero-column matrix")
    return matrix(zip(*a, strict=True))


def add(a: Matrix, b: Matrix, factor=1) -> Matrix:
    require(len(a) == len(b) and len(a[0]) == len(b[0]), "sum shape")
    return matrix([[x + factor * y for x, y in zip(r, s, strict=True)]
                   for r, s in zip(a, b, strict=True)])


def mul(a: Matrix, b: Matrix) -> Matrix:
    require(len(a[0]) == len(b), "product shape")
    return matrix([[sum(x * y for x, y in zip(row, col, strict=True))
                    for col in zip(*b, strict=True)] for row in a])


def rref(a: Matrix):
    rows = [list(row) for row in a]
    pivots = []
    for j in range(len(a[0])):
        candidates = [i for i in range(len(pivots), len(a)) if rows[i][j]]
        if not candidates:
            continue
        k = len(pivots)
        rows[k], rows[candidates[0]] = rows[candidates[0]], rows[k]
        v = rows[k][j]
        rows[k] = [x / v for x in rows[k]]
        for i in range(len(a)):
            if i != k:
                v = rows[i][j]
                rows[i] = [x - v * y for x, y in zip(rows[i], rows[k], strict=True)]
        pivots.append(j)
    return matrix(rows), tuple(pivots)


def rank(a: Matrix) -> int:
    return len(rref(a)[1])


def inv(a: Matrix) -> Matrix:
    n = len(a)
    require(n == len(a[0]) and 2 * n <= LIMIT, "inverse capacity or shape")
    rr, pivots = rref(matrix([row + unit for row, unit in zip(a, eye(n), strict=True)]))
    require(pivots[:n] == tuple(range(n)), "singular matrix")
    return matrix([row[n:] for row in rr])


def basis(a: Matrix) -> Matrix:
    pivots = rref(a)[1]
    return matrix([[row[j] for j in pivots] for row in a])


def orthoproject(a: Matrix) -> Matrix:
    b = basis(a)
    if not b[0]:
        return zero(len(a), len(a))
    return mul(mul(b, inv(mul(tr(b), b))), tr(b))


def block(a: Matrix, rows: range, cols: range) -> Matrix:
    return matrix([[a[i][j] for j in cols] for i in rows])


def diag(values) -> Matrix:
    values = tuple(values)
    return matrix([[v if i == j else 0 for j in range(len(values))]
                   for i, v in enumerate(values)])


def householder(vector) -> Matrix:
    v = tuple(F(x) for x in vector)
    norm = sum(x * x for x in v)
    require(bool(norm), "zero reflection vector")
    return matrix([[int(i == j) - 2 * x * y / norm
                    for j, y in enumerate(v)] for i, x in enumerate(v)])


def schur(p: Matrix, d: int) -> Matrix:
    n = len(p)
    require(1 <= d < n, "pivot size")
    first, tail = range(d), range(d, n)
    a = block(p, first, first)
    correction = mul(mul(block(p, tail, first), inv(a)), block(p, first, tail))
    return add(block(p, tail, tail), correction, -1)


def psd(a: Matrix) -> bool:
    if a != tr(a):
        return False
    rows = [list(row) for row in a]
    for k in range(len(a)):
        if any(rows[i][i] < 0 for i in range(k, len(a))):
            return False
        positive = [i for i in range(k, len(a)) if rows[i][i] > 0]
        if not positive:
            return all(rows[i][j] == 0 for i in range(k, len(a))
                       for j in range(k, len(a)))
        p = positive[0]
        rows[k], rows[p] = rows[p], rows[k]
        for row in rows:
            row[k], row[p] = row[p], row[k]
        pivot = rows[k][k]
        for i in range(k + 1, len(a)):
            for j in range(k + 1, len(a)):
                rows[i][j] -= rows[i][k] * rows[k][j] / pivot
    return True
