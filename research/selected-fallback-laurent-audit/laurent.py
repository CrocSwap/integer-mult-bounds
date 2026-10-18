"""Independent exact Laurent ring and sparse linear operators.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Zero divisors are allowed; only unit monomials can be inverted here.
"""
from math import gcd


def require(ok, message):
    if not ok:
        raise ValueError(message)


class Ring:
    def __init__(self, modulus):
        require(isinstance(modulus, int) and modulus > 1, "invalid modulus")
        self.modulus = modulus

    def scalar(self, value):
        value %= self.modulus
        return {(): value} if value else {}

    def variable(self, index):
        require(isinstance(index, int) and index >= 0, "invalid variable")
        return {((index, 1),): 1}

    def coerce(self, value):
        return self.scalar(value) if isinstance(value, int) else value

    def add(self, left, right):
        out = dict(left)
        for powers, coefficient in right.items():
            value = (out.get(powers, 0) + coefficient) % self.modulus
            if value:
                out[powers] = value
            else:
                out.pop(powers, None)
        return out

    @staticmethod
    def powers(left, right):
        result = dict(left)
        for variable, exponent in right:
            result[variable] = result.get(variable, 0) + exponent
        return tuple(sorted((v, e) for v, e in result.items() if e))

    def mul(self, left, right):
        left, right = self.coerce(left), self.coerce(right)
        out = {}
        for a, x in left.items():
            for b, y in right.items():
                powers = self.powers(a, b)
                value = (out.get(powers, 0) + x*y) % self.modulus
                if value:
                    out[powers] = value
                else:
                    out.pop(powers, None)
        return out

    def inv(self, value):
        value = self.coerce(value)
        require(len(value) == 1, "inverse requires one unit monomial")
        powers, coefficient = next(iter(value.items()))
        require(gcd(coefficient, self.modulus) == 1, "nonunit coefficient")
        return {tuple((v, -e) for v, e in powers): pow(coefficient, -1, self.modulus)}

    def evaluate(self, value, assignment):
        result = 0
        for powers, coefficient in value.items():
            term = coefficient
            for variable, exponent in powers:
                x = assignment[variable]
                require(gcd(x, self.modulus) == 1, "evaluation requires unit weights")
                term = term * pow(x, exponent, self.modulus) % self.modulus
            result = (result + term) % self.modulus
        return result


def scale_row(ring, row, coefficient):
    result = {}
    for column, value in row.items():
        product = ring.mul(value, coefficient)
        if product:
            result[column] = product
    return result


def add_row(ring, target, source, coefficient):
    result = dict(target)
    for column, value in scale_row(ring, source, coefficient).items():
        total = ring.add(result.get(column, {}), value)
        if total:
            result[column] = total
        else:
            result.pop(column, None)
    return result


def identity(ring, dimension):
    return [{i: ring.scalar(1)} for i in range(dimension)]


def mismatch(left, right):
    require(len(left) == len(right), "operator dimensions differ")
    for i, (a, b) in enumerate(zip(left, right)):
        for j in sorted(a.keys() | b.keys()):
            if a.get(j, {}) != b.get(j, {}):
                return i, j, a.get(j, {}), b.get(j, {})
    return None
