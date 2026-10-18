"""Small exact Gaussian-rational reference arithmetic, without float coercion."""
from dataclasses import dataclass
from fractions import Fraction as F
from math import isqrt


@dataclass(frozen=True)
class G:
    re: F = F(0)
    im: F = F(0)

    def __post_init__(self):
        object.__setattr__(self, 're', F(self.re))
        object.__setattr__(self, 'im', F(self.im))

    def __add__(self, other):
        z = coerce(other)
        return G(self.re+z.re, self.im+z.im)

    __radd__ = __add__

    def __neg__(self):
        return G(-self.re, -self.im)

    def __sub__(self, other):
        return self + -coerce(other)

    def __rsub__(self, other):
        return coerce(other) + -self

    def __mul__(self, other):
        z = coerce(other)
        return G(self.re*z.re-self.im*z.im, self.re*z.im+self.im*z.re)

    __rmul__ = __mul__

    def __truediv__(self, other):
        z = coerce(other)
        if not z:
            raise ZeroDivisionError('Gaussian zero divisor')
        return self * G(z.re/z.norm2(), -z.im/z.norm2())

    def __rtruediv__(self, other):
        return coerce(other) / self

    def __bool__(self):
        return bool(self.re or self.im)

    def norm2(self):
        return self.re*self.re + self.im*self.im

    def upper(self):
        return abs(self.re) + abs(self.im)

    def modulus_upper(self):
        squared = self.norm2()
        value = squared.numerator*squared.denominator*(1 << 128)
        root = isqrt(value)
        if root*root != value:
            root += 1
        return F(root, squared.denominator*(1 << 64))

    def conjugate(self):
        return G(self.re, -self.im)

    def __str__(self):
        return f'({self.re},{self.im})'


def coerce(z):
    return z if isinstance(z, G) else G(z)


def rounded(z, bits):
    z = coerce(z)
    scale = 1 << bits
    def component(v):
        v = v*scale + F(1, 2)
        return F(v.numerator // v.denominator, scale)
    return G(component(z.re), component(z.im))


def identity(n):
    return [[G(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum((x*y for x, y in zip(row, col)), G())
             for col in zip(*b)] for row in a]


def norm_upper(a):
    return max(sum(v.upper() for v in row) for row in a)


def power(c, n, bits=None):
    if n == 0:
        return identity(len(c))
    if n == 1:
        return [row.copy() for row in c]
    half = power(c, n//2, bits)
    out = multiply(half, half)
    if bits is not None:
        out = [[rounded(v, bits) for v in row] for row in out]
    if n % 2:
        out = multiply(out, c)
        if bits is not None:
            out = [[rounded(v, bits) for v in row] for row in out]
    return out


def solve(a, b):
    n = len(a)
    a = [row.copy()+[rhs] for row, rhs in zip(a, b)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if a[i][j])
        a[j], a[pivot] = a[pivot], a[j]
        v = a[j][j]
        a[j] = [x/v for x in a[j]]
        for i in range(n):
            if i != j:
                v = a[i][j]
                a[i] = [x-v*y for x, y in zip(a[i], a[j])]
    return [row[-1] for row in a]


def solve_dyadic(a, b, stats=None):
    """Classical fraction-free elimination on a real integer embedding.

Every division during elimination is exact. Input fractions must be dyadic;
the final back substitution returns exact rational coordinates. Matrix rows
are pivoted when needed. Integer minors have O(k*(input_bits+log k)) bits.
"""
    k = len(a)
    n = 2*k
    real = [[a[i][j].re for j in range(k)] + [-a[i][j].im for j in range(k)] + [b[i].re]
            for i in range(k)]
    real += [[a[i][j].im for j in range(k)] + [a[i][j].re for j in range(k)] + [b[i].im]
             for i in range(k)]
    width = 0
    for row in real:
        for value in row:
            d = value.denominator
            if d & (d-1):
                raise ValueError('dyadic closure input required')
            width = max(width, d.bit_length()-1)
    integer = [[value.numerator << (width-value.denominator.bit_length()+1)
                for value in row] for row in real]
    initial_bits = max(abs(value).bit_length() for row in integer for value in row)
    max_bits, pivots, divisions = initial_bits, 0, 0
    previous = 1
    for j in range(n-1):
        pivot_row = next((i for i in range(j, n) if integer[i][j]), None)
        if pivot_row is None:
            raise ValueError('singular dyadic closure')
        if pivot_row != j:
            integer[j], integer[pivot_row] = integer[pivot_row], integer[j]
            pivots += 1
        pivot = integer[j][j]
        for i in range(j+1, n):
            left = integer[i][j]
            for col in range(j+1, n+1):
                value, remainder = divmod(pivot*integer[i][col]-left*integer[j][col], previous)
                if remainder:
                    raise ValueError('fraction-free division was not exact')
                integer[i][col] = value
                max_bits = max(max_bits, abs(value).bit_length())
                divisions += 1
            integer[i][j] = 0
        previous = pivot
    if not integer[-1][-2]:
        raise ValueError('singular dyadic closure')
    out = [F(0)]*n
    for i in range(n-1, -1, -1):
        out[i] = (F(integer[i][-1])-sum(integer[i][j]*out[j] for j in range(i+1, n))) / integer[i][i]
    if stats is not None:
        stats.update(dimension=n, input_bits=initial_bits, maximum_minor_bits=max_bits,
                     row_pivots=pivots, exact_divisions=divisions)
    return [G(out[i], out[k+i]) for i in range(k)]
