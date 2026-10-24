"""Exact Gaussian rational arithmetic shared by the two checkers."""
from fractions import Fraction
import re


class QI:
    __slots__ = ('real', 'imag')

    def __init__(self, real=0, imag=0):
        if isinstance(real, QI):
            self.real, self.imag = real.real, real.imag
        else:
            self.real, self.imag = Fraction(real), Fraction(imag)

    def __add__(self, other):
        other = QI(other)
        return QI(self.real + other.real, self.imag + other.imag)

    __radd__ = __add__

    def __neg__(self):
        return QI(-self.real, -self.imag)

    def __sub__(self, other):
        return self + -QI(other)

    def __mul__(self, other):
        other = QI(other)
        return QI(self.real * other.real - self.imag * other.imag,
                  self.real * other.imag + self.imag * other.real)

    __rmul__ = __mul__

    def __eq__(self, other):
        if not isinstance(other, (QI, int, Fraction)):
            return False
        other = QI(other)
        return self.real == other.real and self.imag == other.imag

    def __bool__(self):
        return bool(self.real or self.imag)

    def json(self):
        return [str(self.real), str(self.imag)]


def scalar(value):
    """Accept integers, rational strings, or two such components. Reject floats."""
    def component(x):
        if type(x) is int:
            return Fraction(x)
        if isinstance(x, str) and re.fullmatch(r'[+-]?[0-9]+(?:/[+-]?[0-9]+)?', x):
            return Fraction(x)
        raise ValueError('explicit integer or rational component required')
    if type(value) is int or isinstance(value, str):
        return QI(component(value))
    if isinstance(value, list) and len(value) == 2:
        return QI(component(value[0]), component(value[1]))
    raise ValueError('exact Gaussian coefficient required')


def unit(power):
    return (QI(1), QI(0, 1), QI(-1), QI(0, -1))[power % 4]


def need(condition, message):
    if not condition:
        raise ValueError(message)
