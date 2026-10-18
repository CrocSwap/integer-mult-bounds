"""Small, independent dense exact-matrix oracles; no cycle certificate calls.

Prepared for William Lawyer with substantial OpenAI Codex assistance.
Apache-2.0. This is deliberately separate from the cycle/prefix algorithm.
"""

from dataclasses import dataclass
from fractions import Fraction as F
from math import isqrt


@dataclass(frozen=True)
class Gaussian:
    re: F = F(0)
    im: F = F(0)

    def __post_init__(self):
        object.__setattr__(self, "re", F(self.re))
        object.__setattr__(self, "im", F(self.im))

    @staticmethod
    def coerce(value):
        return value if isinstance(value, Gaussian) else Gaussian(value)

    def __add__(self, other):
        other = self.coerce(other)
        return Gaussian(self.re + other.re, self.im + other.im)

    __radd__ = __add__

    def __neg__(self):
        return Gaussian(-self.re, -self.im)

    def __sub__(self, other):
        return self + -self.coerce(other)

    def __rsub__(self, other):
        return self.coerce(other) + -self

    def __mul__(self, other):
        other = self.coerce(other)
        return Gaussian(self.re * other.re - self.im * other.im,
                        self.re * other.im + self.im * other.re)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self.coerce(other)
        d = other.re ** 2 + other.im ** 2
        if not d:
            raise ZeroDivisionError("zero Gaussian rational")
        return self * Gaussian(other.re / d, -other.im / d)

    def __bool__(self):
        return bool(self.re or self.im)


def identity(n, scalar=F(1)):
    return [[scalar if i == j else scalar * 0 for j in range(n)]
            for i in range(n)]


def multiply(a, b):
    n = len(a)
    result = [[a[0][0] * 0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if a[i][k]:
                for j in range(n):
                    if b[k][j]:
                        result[i][j] += a[i][k] * b[k][j]
    return result


def inverse(a):
    """Gauss-Jordan with exact pivots; independent of permutation structure."""
    n = len(a)
    unit = a[0][0] * 0 + 1
    ident = identity(n, unit)
    rows = [list(row) + ident[i] for i, row in enumerate(a)]
    for j in range(n):
        pivot = next((k for k in range(j, n) if rows[k][j]), None)
        if pivot is None:
            raise ValueError("singular matrix")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        divisor = rows[j][j]
        rows[j] = [x / divisor for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                factor = rows[i][j]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def weighted_matrix(permutation, weights):
    zero = weights[0] * 0
    n = len(weights)
    result = [[zero for _ in range(n)] for _ in range(n)]
    for i, j in enumerate(permutation):
        result[i][j] = weights[i]
    return result


def monomial_norm2(matrix):
    """Squared infinity norm when every row has exactly one nonzero."""
    values = []
    for row in matrix:
        nonzero = [x for x in row if x]
        if len(nonzero) != 1:
            raise ValueError("not a monomial matrix")
        x = nonzero[0]
        values.append(x.re ** 2 + x.im ** 2)
    return max(values)


def real_norm(matrix):
    return max(sum(abs(x) for x in row) for row in matrix)


def gaussian_norm2(matrix):
    """Exact squared row norm when within-row magnitude ratios are rational.

    This includes a real radial resolvent of a Gaussian-rational weighted
    cycle whose weight magnitudes are rational. Irrational ratios raise an
    error; they are never approximated or silently rounded.
    """
    rows = []
    for row in matrix:
        squared = [x.re ** 2 + x.im ** 2 for x in row]
        pivot = next((q for q in squared if q), None)
        if pivot is None:
            rows.append(F(0))
            continue
        total = F(0)
        for q in squared:
            ratio = q / pivot
            top, bottom = isqrt(ratio.numerator), isqrt(ratio.denominator)
            if top * top != ratio.numerator or bottom * bottom != ratio.denominator:
                raise ValueError("row has irrational magnitude ratios")
            total += F(top, bottom)
        rows.append(pivot * total ** 2)
    return max(rows)


def polynomial_matrix(matrix, coefficients):
    n = len(matrix)
    result = identity(n, F(0))
    for c in reversed(coefficients):
        result = multiply(result, matrix)
        for i in range(n):
            result[i][i] += c
    return result


def polynomial_from_roots(roots):
    result = [F(1)]
    for root in roots:
        updated = [F(0)] * (len(result) + 1)
        for i, c in enumerate(result):
            updated[i] -= root * c
            updated[i + 1] += c
        result = updated
    return result
