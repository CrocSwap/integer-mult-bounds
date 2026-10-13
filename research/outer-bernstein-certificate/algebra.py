"""Exact sparse polynomials and independently reconstructed Bernstein evidence.

Gareth Davidson / OpenAI Codex, Apache-2.0. No predecessor arithmetic imported.
The first five coordinates lie in (0,1); the last two are arbitrary positive.
"""
from fractions import Fraction as F
from itertools import product
from math import comb, lcm

VARIABLES = ("beta", "32b", "a/((1-beta)b)", "2eta", "kappa/G", "L", "R")
ZERO = (0,) * len(VARIABLES)


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Poly:
    def __init__(self, terms=0):
        if isinstance(terms, Poly):
            self.terms = dict(terms.terms)
        elif type(terms) in (int, F):
            self.terms = {ZERO: F(terms)} if terms else {}
        else:
            self.terms = {tuple(k): F(v) for k, v in terms.items() if v}
            require(all(len(k) == 7 and all(type(i) is int and i >= 0 for i in k)
                        for k in self.terms), "invalid monomial")

    @classmethod
    def variable(cls, index):
        k = list(ZERO)
        k[index] = 1
        return cls({tuple(k): F(1)})

    def __add__(self, other):
        terms = dict(self.terms)
        for k, value in Poly(other).terms.items():
            terms[k] = terms.get(k, F(0)) + value
        return Poly(terms)

    __radd__ = __add__

    def __neg__(self):
        return Poly({k: -v for k, v in self.terms.items()})

    def __sub__(self, other):
        return self + -Poly(other)

    def __rsub__(self, other):
        return Poly(other) - self

    def __mul__(self, other):
        terms = {}
        for a, x in self.terms.items():
            for b, y in Poly(other).terms.items():
                key = tuple(i + j for i, j in zip(a, b))
                terms[key] = terms.get(key, F(0)) + x * y
        return Poly(terms)

    __rmul__ = __mul__

    def __pow__(self, power):
        require(type(power) is int and power >= 0, "invalid polynomial power")
        result = Poly(1)
        for _ in range(power):
            result = result * self
        return result

    def __eq__(self, other):
        return self.terms == Poly(other).terms

    def evaluate(self, point):
        require(len(point) == 7, "wrong point dimension")
        total = F(0)
        for alpha, coefficient in self.terms.items():
            term = coefficient
            for x, power in zip(point, alpha):
                term *= x ** power
            total += term
        return total

    def degrees(self):
        return tuple(max((k[i] for k in self.terms), default=0) for i in range(7))


class RationalPoly:
    """Numerator / D**power for the single positive denominator D=1+q."""
    def __init__(self, numerator, denominator, power=0):
        self.numerator = Poly(numerator)
        self.denominator = Poly(denominator)
        self.power = power

    def coerce(self, other):
        if isinstance(other, RationalPoly):
            require(other.denominator == self.denominator, "different denominators")
            return other
        return RationalPoly(other, self.denominator)

    def __add__(self, other):
        other = self.coerce(other)
        power = max(self.power, other.power)
        left = self.numerator * self.denominator ** (power - self.power)
        right = other.numerator * self.denominator ** (power - other.power)
        return RationalPoly(left + right, self.denominator, power)

    __radd__ = __add__

    def __neg__(self):
        return RationalPoly(-self.numerator, self.denominator, self.power)

    def __sub__(self, other):
        return self + -self.coerce(other)

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        return RationalPoly(self.numerator * other.numerator, self.denominator,
                            self.power + other.power)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self.coerce(other)
        require(other.power == 0, "unsupported division by rational polynomial")
        if other.numerator == self.denominator:
            return RationalPoly(self.numerator, self.denominator, self.power + 1)
        require(set(other.numerator.terms) == {ZERO}, "unsupported denominator")
        divisor = other.numerator.terms[ZERO]
        require(divisor != 0, "zero denominator")
        return RationalPoly(self.numerator * (1 / divisor), self.denominator, self.power)

    def cleared(self):
        require(self.power <= 1, "source needs more than one denominator factor")
        return self.numerator * self.denominator ** (1 - self.power)

    def evaluate(self, point):
        d = self.denominator.evaluate(point)
        require(d > 0, "nonpositive denominator")
        return self.numerator.evaluate(point) / d ** self.power


def indices(degrees):
    return product(*(range(n + 1) for n in degrees))


def nominate(poly):
    """Power-to-Bernstein transform; the checker below does not call this."""
    degrees = poly.degrees()
    coefficients = []
    for k in indices(degrees):
        value = F(0)
        for alpha, coefficient in poly.terms.items():
            if alpha[5:] != k[5:] or any(a > b for a, b in zip(alpha[:5], k[:5])):
                continue
            term = coefficient
            for i in range(5):
                term *= F(comb(k[i], alpha[i]), comb(degrees[i], alpha[i]))
            value += term
        coefficients.append(value)
    scale = lcm(*(x.denominator for x in coefficients))
    return {"degrees": list(degrees), "scale": scale,
            "weights": [int(x * scale) for x in coefficients]}


def reconstruct(certificate, *, strict=True):
    """Expand Bernstein basis directly into powers, using integer binomials.

    Deliberately does not use Poly multiplication or the nomination transform.
    Last two coordinates retain ordinary positive monomials, without upper caps.
    """
    require(set(certificate) == {"degrees", "scale", "weights"}, "certificate fields")
    degrees, scale, weights = (certificate[k] for k in ("degrees", "scale", "weights"))
    require(type(degrees) is list and len(degrees) == 7 and
            all(type(n) is int and 0 <= n <= 8 for n in degrees), "invalid degrees")
    require(type(scale) is int and scale > 0, "invalid scale")
    count = 1
    for n in degrees:
        count *= n + 1
    require(type(weights) is list and len(weights) == count, "wrong coefficient count")
    require(all(type(n) is int and n >= 0 for n in weights), "negative or noninteger weight")
    require(not strict or any(weights), "no strict-positive term")
    expanded = {}
    for k, weight in zip(indices(degrees), weights):
        if not weight:
            continue
        factor = weight
        for i in range(5):
            factor *= comb(degrees[i], k[i])
        for j in product(*(range(degrees[i] - k[i] + 1) for i in range(5))):
            coefficient = factor * (-1) ** sum(j)
            for i in range(5):
                coefficient *= comb(degrees[i] - k[i], j[i])
            alpha = tuple(k[i] + j[i] for i in range(5)) + k[5:]
            expanded[alpha] = expanded.get(alpha, 0) + coefficient
    return Poly({k: F(v, scale) for k, v in expanded.items() if v})


def check_certificate(poly, certificate, *, strict=True):
    require(reconstruct(certificate, strict=strict) == poly,
            "Bernstein expansion differs from source polynomial")


def symbolic_inputs():
    u, v, w, z, t, literal, row = (Poly.variable(i) for i in range(7))
    a = (1 - u) * v * w * F(1, 32)
    b = v * F(1, 32)
    eta = z * F(1, 2)
    q = a * (1 - z)
    denominator = 1 + q
    lift = lambda p: RationalPoly(p, denominator)
    gain = RationalPoly((1 - eta) * q, denominator, 1)
    return dict(bit_saving=lift(a), complex_saving=lift(b), beta=lift(u),
                eta=lift(eta), kappa=lift(t) * gain,
                bridge={"semantic": {"strict_literal_gap": lift(literal)},
                        "rows": {"degree_gap": lift(row)}}), denominator
