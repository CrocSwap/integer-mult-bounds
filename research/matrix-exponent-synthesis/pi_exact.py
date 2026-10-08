"""Exact Gaussian dyadics with a canonical (1+i)-denominator.

Alejandro Zarzuelo Urdiales, with OpenAI Codex assistance, Apache-2.0.
The cancellation rule and uniqueness are proved in GaussianScalarCircuits.lean.
Other operations below have independent Fraction controls; no whole-network
formalization or fixed-tape cost theorem is claimed.
"""
from dataclasses import dataclass
from fractions import Fraction


def times_pi(a, b):
    return a-b, a+b


def times_pi_power(a, b, n):
    # pi^(2q)=2^q i^q; use shifts and unit rotations, not n additions.
    q, odd = divmod(n, 2)
    for _ in range(q % 4):
        a, b = -b, a
    a, b = a << q, b << q
    return times_pi(a, b) if odd else (a, b)


@dataclass(frozen=True)
class Gaussian:
    re: int = 0
    im: int = 0
    exponent: int = 0

    def __post_init__(self):
        if any(type(x) is not int for x in (self.re, self.im, self.exponent)):
            raise TypeError("integer numerator and denominator tag required")
        if self.exponent < 0:
            raise ValueError("negative denominator exponent")
        a, b, e = self.re, self.im, self.exponent
        if a == b == 0:
            e = 0
        while e and (a+b) % 2 == 0:
            a, b = (a+b)//2, (b-a)//2
            e -= 1
        object.__setattr__(self, "re", a)
        object.__setattr__(self, "im", b)
        object.__setattr__(self, "exponent", e)

    def aligned(self, exponent):
        if exponent < self.exponent:
            raise ValueError("cannot align to a smaller denominator without a certificate")
        return times_pi_power(self.re, self.im, exponent-self.exponent)

    def __add__(self, other):
        if type(other) is int:
            other = Gaussian(other)
        e = max(self.exponent, other.exponent)
        a, b = self.aligned(e)
        c, d = other.aligned(e)
        return Gaussian(a+c, b+d, e)

    __radd__ = __add__

    def __neg__(self):
        return Gaussian(-self.re, -self.im, self.exponent)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        if type(other) is int:
            return Gaussian(self.re*other, self.im*other, self.exponent)
        return Gaussian(self.re*other.re-self.im*other.im,
                        self.re*other.im+self.im*other.re,
                        self.exponent+other.exponent)

    __rmul__ = __mul__

    def phase(self, n=1):
        a, b = self.re, self.im
        for _ in range(n % 4):
            a, b = -b, a
        return Gaussian(a, b, self.exponent)

    def over_pi(self):
        return Gaussian(self.re, self.im, self.exponent+1)

    def over_two(self, n=1):
        # 1/2 = i/pi^2.
        if type(n) is not int or n < 0:
            raise ValueError("nonnegative dyadic shift required")
        z = self.phase(n)
        return Gaussian(z.re, z.im, z.exponent+2*n)

    def exact_integer(self):
        if self.exponent:
            raise ValueError("value is not a Gaussian integer")
        return self.re, self.im

    def fractions(self):
        c, d = times_pi_power(1, 0, self.exponent)
        norm = c*c+d*d
        return (Fraction(self.re*c+self.im*d, norm),
                Fraction(self.im*c-self.re*d, norm))


def butterfly(u, v, inverse=False):
    if inverse:
        return (u+v.phase()).over_pi(), (u.phase()+v).over_pi()
    return (u.phase()+v).over_pi(), (u+v.phase()).over_pi()


def translation_phase(values, mask, inverse=False):
    """C_u=(i I+X_u)/pi, when u is an eligible norm-one binary line."""
    out = list(values)
    if not 0 < mask < len(out) or len(out) & (len(out)-1):
        raise ValueError("nonzero translation mask on a binary cube required")
    if mask.bit_count() % 2 != 1:
        raise ValueError("this physical line formula requires odd binary norm")
    for x in range(len(out)):
        y = x ^ mask
        if x < y:
            out[x], out[y] = butterfly(out[x], out[y], inverse)
    return out


def tensor(values, dimension, inverse=False):
    if len(values) != 1 << dimension:
        raise ValueError("wrong tensor dimension")
    out = list(values)
    for axis in range(dimension):
        out = translation_phase(out, 1 << axis, inverse)
    return out


def z_phase(values, mask):
    return [-z if (x & mask).bit_count() % 2 else z for x, z in enumerate(values)]
