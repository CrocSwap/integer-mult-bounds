"""Outward dyadic enclosures. All acceptance arithmetic is integer/rational.

Mason Hale, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from math import factorial, isqrt


def need(condition, message):
    if not condition:
        raise ValueError(message)


def ceildiv(a, b):
    need(b > 0, "positive divisor")
    return -((-a) // b)


@dataclass(frozen=True)
class Interval:
    lo: int
    hi: int
    bits: int

    def __post_init__(self):
        need(self.lo <= self.hi and self.bits > 0, "interval order/precision")

    @property
    def scale(self):
        return 1 << self.bits

    @classmethod
    def rational(cls, x, bits):
        x = F(x)
        a = x.numerator * (1 << bits)
        return cls(a // x.denominator, ceildiv(a, x.denominator), bits)

    def coerce(self, other):
        value = other if isinstance(other, Interval) else self.rational(other, self.bits)
        need(value.bits == self.bits, "one working grid")
        return value

    def __add__(self, other):
        other = self.coerce(other)
        return Interval(self.lo + other.lo, self.hi + other.hi, self.bits)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.hi, -self.lo, self.bits)

    def __sub__(self, other):
        return self + -self.coerce(other)

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        values = (self.lo * other.lo, self.lo * other.hi,
                  self.hi * other.lo, self.hi * other.hi)
        return Interval(min(values) // self.scale, ceildiv(max(values), self.scale), self.bits)

    __rmul__ = __mul__

    def divide_integer(self, divisor):
        need(divisor > 0, "positive integer denominator")
        return Interval(self.lo // divisor, ceildiv(self.hi, divisor), self.bits)

    def reciprocal(self):
        need(self.lo > 0, "positive reciprocal enclosure")
        return Interval(self.scale**2 // self.hi, ceildiv(self.scale**2, self.lo), self.bits)

    def __truediv__(self, other):
        if isinstance(other, int):
            return self.divide_integer(other)
        return self * self.coerce(other).reciprocal()

    def widen(self, units):
        need(units >= 0, "nonnegative enclosure radius")
        return Interval(self.lo - units, self.hi + units, self.bits)

    def contains(self, value):
        value = F(value) * self.scale
        return self.lo <= value <= self.hi

    def overlaps(self, other):
        return self.lo <= other.hi and other.lo <= self.hi

    def absolute_upper(self):
        return max(abs(self.lo), abs(self.hi))


@lru_cache(None)
def pi_interval(bits):
    """Machin identity with the alternating-series remainder, before rounding."""
    def arctan_inverse(q):
        total = F(0)
        n = 0
        while True:
            term = F(1, (2*n+1) * q**(2*n+1))
            total += term if n % 2 == 0 else -term
            n += 1
            tail = F(1, (2*n+1) * q**(2*n+1))
            if tail < F(1, 1 << (bits + 16)):
                return (total, total + tail) if n % 2 == 0 else (total - tail, total)
    a, b = arctan_inverse(5), arctan_inverse(239)
    lower, upper = 16*a[0] - 4*b[1], 16*a[1] - 4*b[0]
    return Interval(Interval.rational(lower, bits).lo, Interval.rational(upper, bits).hi, bits)


def exp_negative(x):
    """Enclose exp(-x), x >= 0, by small positive Taylor sums and squaring."""
    need(x.lo >= 0, "nonnegative exponential argument")
    scale = x.scale
    if x.lo >= x.bits * scale:
        # e > 2 and x >= bits: the answer lies strictly below one grid unit.
        return Interval(0, 1, x.bits)
    halves = 0
    while x.hi > (scale << halves) // 8:
        halves += 1
    y = x / (1 << halves)
    one = Interval.rational(1, x.bits)
    total = term = one
    n = 0
    # y <= 1/8, so the omitted positive Taylor tail is at most
    # 2*(1/8)^(n+1)/(n+1)!; choose it smaller than one grid unit.
    while True:
        n += 1
        term = (term * y) / n
        total += term
        tail = F(2, 8**(n+1) * factorial(n+1))
        if tail < F(1, scale):
            total = Interval(total.lo, total.hi + ceildiv(tail.numerator * scale, tail.denominator), x.bits)
            break
    result = total.reciprocal()
    for _ in range(halves):
        result = result * result
    return Interval(max(0, result.lo), min(scale, result.hi), x.bits)


ComplexInterval = tuple[Interval, Interval]


def point(real, imag, bits):
    return Interval.rational(real, bits), Interval.rational(imag, bits)


def cadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def cneg(a):
    return -a[0], -a[1]


def cconj(a):
    return a[0], -a[1]


def cmul(a, b):
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def cscale(a, real):
    return a[0]*real, a[1]*real


@lru_cache(None)
def root_of_unity(j, k, bits):
    """exp(2 pi i j/k), via rational Taylor remainders; no binary floats."""
    need(k > 0, "positive phase denominator")
    j %= k
    quadrant = (8*j + k) // (2*k)
    residual = F(j, k) - F(quadrant, 4)
    x = pi_interval(bits) * (2 * residual)
    x2 = x*x
    one = Interval.rational(1, bits)
    cosine, sine = one, x
    cterm, sterm = one, x
    n = 0
    while True:
        n += 1
        cterm = -(cterm*x2) / ((2*n-1)*(2*n))
        sterm = -(sterm*x2) / ((2*n)*(2*n+1))
        cosine += cterm
        sine += sterm
        # |x| <= pi/4 < 4/5; alternating Taylor remainders.
        ctail = F(4, 5)**(2*n+2) / factorial(2*n+2)
        stail = F(4, 5)**(2*n+3) / factorial(2*n+3)
        if max(ctail, stail) < F(1, (1 << bits)*16):
            cosine = cosine.widen(1)
            sine = sine.widen(1)
            break
    for _ in range(quadrant % 4):
        cosine, sine = -sine, cosine
    return cosine, sine


def inward_quantize(z, precision):
    """A p-grid point whose component magnitudes do not exceed any z in box.

    Returns integer numerators and a rigorous l1 (hence modulus) error bound.
    """
    bits = z[0].bits
    need(bits >= precision and z[1].bits == bits, "quantization grids")
    step = 1 << (bits - precision)
    out, error = [], 0
    for component in z:
        if component.lo > 0:
            numerator = component.lo // step
        elif component.hi < 0:
            numerator = -((-component.hi) // step)
        else:
            numerator = 0
        encoded = numerator * step
        error += max(abs(encoded-component.lo), abs(encoded-component.hi))
        out.append(numerator)
    return tuple(out), F(error, 1 << bits)


def grid_point(z, precision, bits):
    return point(F(z[0], 1 << precision), F(z[1], 1 << precision), bits)


def in_disk(z, precision):
    return z[0]**2 + z[1]**2 <= 1 << (2*precision)
