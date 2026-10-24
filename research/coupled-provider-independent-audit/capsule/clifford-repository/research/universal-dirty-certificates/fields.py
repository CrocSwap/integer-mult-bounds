"""Small exact scalar layer shared by producer and checker (part of their trust base).

Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from math import isqrt
from functools import lru_cache
import re


class Gaussian:
    """Q(i); input strings use a+bi with rational a,b, or just i/-i."""
    def __init__(self, value=0):
        if isinstance(value, Gaussian):
            self.real, self.imag = value.real, value.imag
        elif type(value) is str and value.endswith("i"):
            body = value[:-1]
            rational = r"\d+(?:/\d+)?"
            match = re.fullmatch(r"([+-]?"+rational+r")([+-](?:"+rational+r")?)", body)
            if match:
                self.real = Fraction(match[1])
                self.imag = Fraction(match[2]+"1" if match[2] in ("+", "-") else match[2])
            else:
                if body in ("", "+", "-"):
                    body += "1"
                self.real, self.imag = Fraction(0), Fraction(body)
        else:
            self.real, self.imag = Fraction(value), Fraction(0)

    @classmethod
    def pair(cls, real, imag):
        out = cls()
        out.real, out.imag = real, imag
        return out

    def __add__(self, other):
        z = Gaussian(other)
        return self.pair(self.real+z.real, self.imag+z.imag)

    __radd__ = __add__

    def __mul__(self, other):
        z = Gaussian(other)
        return self.pair(self.real*z.real-self.imag*z.imag, self.real*z.imag+self.imag*z.real)

    __rmul__ = __mul__

    def __neg__(self):
        return self.pair(-self.real, -self.imag)

    def __sub__(self, other):
        return self+-Gaussian(other)

    def __rsub__(self, other):
        return Gaussian(other)+-self

    def __truediv__(self, other):
        z = Gaussian(other)
        norm = z.real*z.real+z.imag*z.imag
        return self*self.pair(z.real/norm, -z.imag/norm)

    def __rtruediv__(self, other):
        return Gaussian(other)/self

    def __eq__(self, other):
        z = Gaussian(other)
        return self.real == z.real and self.imag == z.imag

    def __bool__(self):
        return bool(self.real or self.imag)

    def __str__(self):
        if not self.imag:
            return str(self.real)
        return str(self.real)+("+" if self.imag >= 0 else "")+str(self.imag)+"i"

    __repr__ = __str__


def scalars(problem):
    p = problem.get("field", "Q")
    if p == "Q":
        return Fraction
    if p == "Qi":
        return Gaussian
    if type(p) is not int:
        raise ValueError("field must be Q, Qi or a prime at most 2^31-1")
    return prime_scalars(p)


@lru_cache(maxsize=32)
def prime_scalars(p):
    if not 2 <= p <= 2**31-1 or any(p % d == 0 for d in range(2, isqrt(p)+1)):
        raise ValueError("field must be Q, Qi or a prime at most 2^31-1")

    class Prime:
        def __init__(self, x=0):
            if isinstance(x, Prime):
                self.value = x.value
            else:
                q = Fraction(x)
                self.value = q.numerator*pow(q.denominator, -1, p) % p

        def __add__(self, other):
            return Prime(self.value+Prime(other).value)

        __radd__ = __add__

        def __mul__(self, other):
            return Prime(self.value*Prime(other).value)

        __rmul__ = __mul__

        def __neg__(self):
            return Prime(-self.value)

        def __sub__(self, other):
            return self+-Prime(other)

        def __rsub__(self, other):
            return Prime(other)+-self

        def __truediv__(self, other):
            return Prime(self.value*pow(Prime(other).value, -1, p))

        def __rtruediv__(self, other):
            return Prime(other)/self

        def __eq__(self, other):
            return self.value == Prime(other).value

        def __bool__(self):
            return bool(self.value)

        def __str__(self):
            return str(self.value)

        __repr__ = __str__

    return Prime
