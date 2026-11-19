"""Exact Gaussian rationals and incremental row reduction over Q(i)."""

from math import gcd
import re


def decimal_integer(value):
    """Read an explicitly written decimal integer in bounded chunks."""
    if not re.fullmatch(r"[+-]?[0-9]+", value):
        raise ValueError("expected a decimal integer")
    negative = value.startswith("-")
    digits = value.lstrip("+-")
    result = 0
    for start in range(0, len(digits), 9):
        chunk = digits[start:start+9]
        result = result * 10**len(chunk) + int(chunk)
    return -result if negative else result


def rational_parts(value):
    if type(value) is int:
        return value, 1
    if type(value) is not str:
        raise ValueError("each component must be an integer or a fraction string")
    top, slash, bottom = value.partition("/")
    denominator = decimal_integer(bottom) if slash else 1
    if denominator <= 0:
        raise ValueError("a rational denominator must be positive")
    return decimal_integer(top), denominator


def decimal_string(value):
    if value < 0:
        return "-" + decimal_string(-value)
    if value.bit_length() < 1024:
        return str(value)
    chunks = []
    while value:
        value, rest = divmod(value, 10**9)
        chunks.append(rest)
    return str(chunks.pop()) + "".join(f"{v:09d}" for v in reversed(chunks))


def rational_string(a, d):
    common = gcd(a, d)
    top, bottom = a // common, d // common
    return decimal_string(top) if bottom == 1 else decimal_string(top) + "/" + decimal_string(bottom)


class G(tuple):
    __slots__ = ()

    def __new__(cls, a, b=0, d=1):
        if not d:
            raise ZeroDivisionError("zero Gaussian denominator")
        if d < 0:
            a, b, d = -a, -b, -d
        if d != 1:
            common = gcd(gcd(a, b), d)
            a, b, d = a // common, b // common, d // common
        return tuple.__new__(cls, (a, b, d))

    @classmethod
    def parse(cls, re, im):
        a, d = rational_parts(re)
        b, h = rational_parts(im)
        return cls(a*h, b*d, d*h)

    def pair(self):
        a, b, d = self
        return [rational_string(a, d), rational_string(b, d)]

    def __bool__(self):
        return self[0] != 0 or self[1] != 0

    def __add__(self, other):
        if not self:
            return other
        if not other:
            return self
        a, b, d = self
        e, f, h = other
        if d == h:
            return G(a + e, b + f, d)
        return G(a*h + e*d, b*h + f*d, d*h)

    def __neg__(self):
        a, b, d = self
        return G(-a, -b, d)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if not self or not other:
            return ZERO
        if self == ONE:
            return other
        if other == ONE:
            return self
        a, b, d = self
        e, f, h = other
        return G(a*e - b*f, a*f + b*e, d*h)

    def __truediv__(self, other):
        a, b, d = self
        e, f, h = other
        return G((a*e + b*f)*h, (b*e - a*f)*h, d*(e*e + f*f))

    def conjugate(self):
        return G(self[0], -self[1], self[2])

    def __pow__(self, exponent):
        if exponent < 0:
            return (ONE / self) ** (-exponent)
        value, base = ONE, self
        while exponent:
            if exponent & 1:
                value = value * base
            exponent //= 2
            if exponent:
                base = base * base
        return value


ZERO, ONE, I = G(0), G(1), G(0, 1)
PHASES = (ONE, I, -ONE, -I)
LETTERS = (ZERO,) + PHASES


def dot(left, right):
    return sum((a*b for a, b in zip(left, right, strict=True) if a and b), ZERO)


class Basis:
    """Keep the reduced row echelon form of the supplied rows."""

    def __init__(self, rows=()):
        self.rows = dict(rows)

    def add(self, values):
        v = list(values)
        for col, row in self.rows.items():
            if v[col]:
                scale = v[col]
                v = [a - scale*b if b else a for a, b in zip(v, row, strict=True)]
        pivot = next((j for j, a in enumerate(v) if a), None)
        if pivot is None:
            return False
        scale = v[pivot]
        row = tuple(a / scale if a else ZERO for a in v)
        for j, old in self.rows.items():
            if old[pivot]:
                self.rows[j] = tuple(a - old[pivot]*b if b else a
                                     for a, b in zip(old, row, strict=True))
        self.rows[pivot] = row
        return True

    def extend(self, rows):
        result = Basis(self.rows)
        for row in rows:
            result.add(row)
        return result


def solve(matrix, values):
    size = len(values)
    basis = Basis()
    for row, value in zip(matrix, values, strict=True):
        basis.add((*row, value))
    if set(basis.rows) != set(range(size)):
        raise ValueError("singular coefficient system")
    return [basis.rows[j][-1] for j in range(size)]
