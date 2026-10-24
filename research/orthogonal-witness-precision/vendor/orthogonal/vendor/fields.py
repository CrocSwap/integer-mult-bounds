"""Exact Q / prime-field arithmetic shared by the two implementations.

Prepared for Krzysztof Wójt with OpenAI Codex assistance. Apache-2.0.
"""

from fractions import Fraction
from functools import lru_cache
from math import isqrt


@lru_cache(maxsize=64)
def prime(p):
    if p < 2 or p > 2**31 - 1:
        return False
    if p % 2 == 0:
        return p == 2
    return all(p % d for d in range(3, isqrt(p) + 1, 2))


class Field:
    def __init__(self, characteristic=0):
        if type(characteristic) is not int or (
            characteristic != 0 and not prime(characteristic)
        ):
            raise ValueError("field must be 0 (Q) or a prime at most 2^31-1")
        self.characteristic = characteristic
        self.zero = 0 if characteristic else Fraction(0)
        self.one = 1 if characteristic else Fraction(1)

    def parse(self, value):
        if type(value) not in (int, str, Fraction):
            raise ValueError("scalar must be an integer or an exact fraction string")
        try:
            value = Fraction(value)
        except (ValueError, ZeroDivisionError) as error:
            raise ValueError("invalid exact scalar") from error
        p = self.characteristic
        if not p:
            return value
        if value.denominator % p == 0:
            raise ValueError("scalar denominator is zero in the field")
        return value.numerator * pow(value.denominator, -1, p) % p

    def add(self, x, y):
        return (x + y) % self.characteristic if self.characteristic else x + y

    def sub(self, x, y):
        return (x - y) % self.characteristic if self.characteristic else x - y

    def mul(self, x, y):
        return (x * y) % self.characteristic if self.characteristic else x * y

    def neg(self, x):
        return -x % self.characteristic if self.characteristic else -x

    def div(self, x, y):
        if not y:
            raise ValueError("division by zero")
        if self.characteristic:
            return x * pow(y, -1, self.characteristic) % self.characteristic
        return x / y

    def dump(self, x):
        return str(x)

    def is_zero(self, x):
        return x == 0
