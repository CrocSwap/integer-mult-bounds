# SPDX-License-Identifier: Apache-2.0
"""Small outward-rounded interval arithmetic for this proof's real constants."""
from dataclasses import dataclass
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN
from fractions import Fraction

PRECISION = 90
DOWN = Context(prec=PRECISION, rounding=ROUND_FLOOR)
UP = Context(prec=PRECISION, rounding=ROUND_CEILING)
NEAR = Context(prec=PRECISION, rounding=ROUND_HALF_EVEN)


@dataclass(frozen=True)
class I:
    lo: Decimal
    hi: Decimal

    @classmethod
    def point(cls, value):
        if isinstance(value, cls):
            return value
        if isinstance(value, Fraction):
            a, b = Decimal(value.numerator), Decimal(value.denominator)
            return cls(DOWN.divide(a, b), UP.divide(a, b))
        a = Decimal(value)
        return cls(a, a)

    def __add__(self, other):
        other = I.point(other)
        return I(DOWN.add(self.lo, other.lo), UP.add(self.hi, other.hi))

    __radd__ = __add__

    def __sub__(self, other):
        other = I.point(other)
        return I(DOWN.subtract(self.lo, other.hi), UP.subtract(self.hi, other.lo))

    def __mul__(self, other):
        other = I.point(other)
        pairs = [(a, b) for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return I(min(DOWN.multiply(a, b) for a, b in pairs), max(UP.multiply(a, b) for a, b in pairs))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = I.point(other)
        if other.lo <= 0:
            raise ValueError('interval denominator must be strictly positive')
        return self * I(DOWN.divide(Decimal(1), other.hi), UP.divide(Decimal(1), other.lo))

    def __pow__(self, exponent):
        if not isinstance(exponent, int) or exponent < 0:
            raise ValueError('interval integer exponent must be nonnegative')
        out = I.point(1)
        power = self
        while exponent:
            if exponent & 1:
                out *= power
            exponent //= 2
            if exponent:
                power *= power
        return out

    def ln(self):
        if self.lo <= 0:
            raise ValueError('interval natural logarithm requires positive values')
        if self.lo == self.hi == 1:
            return I.point(0)
        return I(NEAR.next_minus(NEAR.ln(self.lo)), NEAR.next_plus(NEAR.ln(self.hi)))

    def exp(self):
        if self.lo == self.hi == 0:
            return I.point(1)
        return I(NEAR.next_minus(NEAR.exp(self.lo)), NEAR.next_plus(NEAR.exp(self.hi)))

    def bounds(self):
        return [str(self.lo), str(self.hi)]
