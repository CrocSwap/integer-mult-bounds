"""Bounded exact Q(i) matrices for the three-spectrum certificate."""
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Q:
    r: Fraction = Fraction(0)
    i: Fraction = Fraction(0)

    def __add__(self, other):
        return Q(self.r + other.r, self.i + other.i)

    def __neg__(self):
        return Q(-self.r, -self.i)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        return Q(self.r * other.r - self.i * other.i,
                 self.r * other.i + self.i * other.r)

    def __truediv__(self, other):
        norm = other.r * other.r + other.i * other.i
        if norm == 0:
            raise ZeroDivisionError('zero Gaussian rational')
        return Q((self.r * other.r + self.i * other.i) / norm,
                 (self.i * other.r - self.r * other.i) / norm)

    def __bool__(self):
        return bool(self.r or self.i)

    def encode(self):
        return [str(self.r), str(self.i)]


ZERO, ONE, I = Q(), Q(Fraction(1)), Q(Fraction(0), Fraction(1))


def identity(n):
    if not 1 <= n <= 8:
        raise ValueError('matrix order must be between 1 and 8')
    return [[ONE if r == c else ZERO for c in range(n)] for r in range(n)]


def multiply(a, b):
    rows, inner, cols = len(a), len(b), len(b[0])
    assert 1 <= rows <= 8 and 1 <= inner <= 8 and 1 <= cols <= 8
    assert all(len(row) == inner for row in a)
    return [[sum((a[r][k] * b[k][c] for k in range(inner)), ZERO)
             for c in range(cols)] for r in range(rows)]


def rref(matrix):
    a = [row[:] for row in matrix]
    rows, cols = len(a), len(a[0])
    assert 1 <= rows <= 8 and 1 <= cols <= 8
    assert all(len(row) == cols for row in a)
    pivots = []
    for col in range(cols):
        choices = [r for r in range(len(pivots), rows) if a[r][col]]
        if not choices:
            continue
        pivot = len(pivots)
        a[pivot], a[choices[0]] = a[choices[0]], a[pivot]
        scale = a[pivot][col]
        a[pivot] = [entry / scale for entry in a[pivot]]
        for r in range(rows):
            if r != pivot:
                scale = a[r][col]
                a[r] = [a[r][c] - scale * a[pivot][c] for c in range(cols)]
        pivots.append(col)
        if len(pivots) == rows:
            break
    return a, pivots


def kernel(matrix):
    reduced, pivots = rref(matrix)
    cols = len(matrix[0])
    basis = []
    for free in range(cols):
        if free in pivots:
            continue
        vector = [ZERO for _ in range(cols)]
        vector[free] = ONE
        for r, pivot in enumerate(pivots):
            vector[pivot] = -reduced[r][free]
        basis.append(vector)
    return basis


def factor(z, sign, direction, covector):
    n = len(direction)
    if not 1 <= n <= 8 or n != len(covector) or sign not in (-1, 1):
        raise ValueError('invalid factor dimension or sign')
    if sum((direction[j] * covector[j] for j in range(n)), ZERO) != ONE:
        raise ValueError('paid factor must be a rank-one idempotent')
    parameter = (z if sign == 1 else ONE / z) - ONE
    unit = identity(n)
    return [[unit[r][c] + parameter * direction[r] * covector[c]
             for c in range(n)] for r in range(n)]


def encode_matrix(matrix):
    return [[entry.encode() for entry in row] for row in matrix]
