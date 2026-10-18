"""Literal exact Fourier/convolution oracle, independent of admission formulas.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor code is imported. Values lie in Z[z]/Phi_m; denominator N**3.
"""

from fractions import Fraction
from itertools import product
from math import lcm, prod


def exact_quotient(a, b):
    a = list(a)
    out = [0] * (len(a) - len(b) + 1)
    for k in range(len(out) - 1, -1, -1):
        out[k] = a[k + len(b) - 1]
        for j, coefficient in enumerate(b):
            a[k + j] -= out[k] * coefficient
    if any(a):
        raise ValueError("nonexact polynomial quotient")
    return tuple(out)


def cyclotomic(m):
    polynomials = {}
    for n in range(1, m + 1):
        if m % n:
            continue
        p = (-1,) + (0,) * (n - 1) + (1,)
        for d in range(1, n):
            if n % d == 0:
                p = exact_quotient(p, polynomials[d])
        polynomials[n] = p
    return polynomials[m]


class Ring:
    def __init__(self, m):
        self.m = m
        self.polynomial = cyclotomic(m)
        self.degree = len(self.polynomial) - 1
        self.zero = (0,) * self.degree
        self.one = (1,) + (0,) * (self.degree - 1)
        powers = []
        value = self.one
        for _ in range(m):
            powers.append(value)
            a = [0] + list(value)
            leading = a.pop()
            value = tuple(a[i] - leading * self.polynomial[i]
                          for i in range(self.degree))
        if value != self.one or len(set(powers)) != m:
            raise ValueError("root of unity is not primitive")
        self.powers = tuple(powers)

    def integer(self, n):
        return (n,) + (0,) * (self.degree - 1)

    def add(self, a, b):
        return tuple(x + y for x, y in zip(a, b))

    def scale(self, a, n):
        return tuple(n * x for x in a)

    def root_mul(self, a, e):
        out = [0] * self.degree
        for j, coefficient in enumerate(a):
            if coefficient:
                for i, entry in enumerate(self.powers[(e + j) % self.m]):
                    out[i] += coefficient * entry
        return tuple(out)

    def mul(self, a, b):
        out = [0] * self.degree
        for j, aj in enumerate(a):
            if not aj:
                continue
            for k, bk in enumerate(b):
                if bk:
                    for i, entry in enumerate(self.powers[(j + k) % self.m]):
                        out[i] += aj * bk * entry
        return tuple(out)


class FourierOracle:
    def __init__(self, moduli):
        self.moduli = tuple(moduli)
        self.points = tuple(product(*(range(q) for q in moduli)))
        self.n = prod(moduli)
        self.m = lcm(4, *moduli)
        self.ring = Ring(self.m)
        self.indices = {x: i for i, x in enumerate(self.points)}
        self.kernel = []
        for x in self.points:
            row = []
            for y in self.points:
                turn = sum((Fraction(a * b, q)
                            for a, b, q in zip(x, y, moduli)), Fraction())
                exponent = self.m * turn
                if exponent.denominator != 1:
                    raise ValueError("character is outside phase field")
                row.append(int(exponent) % self.m)
            self.kernel.append(tuple(row))
        self.sums = tuple(tuple(self.indices[tuple((a + b) % q
                          for a, b, q in zip(x, y, moduli))]
                          for y in self.points) for x in self.points)

    def basis(self, i):
        return tuple(self.ring.one if j == i else self.ring.zero
                     for j in range(self.n))

    def character(self, i):
        return tuple(self.ring.powers[self.kernel[j][i]]
                     for j in range(self.n))

    def dense(self, seed, salt):
        return tuple(self.ring.integer(((seed + salt) * (j + 1) ** 2
                                        + 3 * j + salt) % 11 - 5)
                     for j in range(self.n))

    def transform(self, values, sign):
        if sign not in (-1, 1):
            raise ValueError("Fourier sign must be -1 or 1")
        result = []
        for row in self.kernel:
            total = self.ring.zero
            for value, exponent in zip(values, row):
                total = self.ring.add(total, self.ring.root_mul(value, sign * exponent))
            result.append(total)
        return tuple(result)

    def layout(self, values, permutation, phases):
        return tuple(self.ring.root_mul(values[j], phase)
                     for j, phase in zip(permutation, phases))

    def convolution(self, u, v):
        result = [self.ring.zero] * self.n
        for i, a in enumerate(u):
            if not any(a):
                continue
            for j, b in enumerate(v):
                if any(b):
                    k = self.sums[i][j]
                    result[k] = self.ring.add(result[k], self.ring.mul(a, b))
        return tuple(result)

    def evaluate(self, u, v, pi, sigma, rho, alpha, beta, omega,
                 inverse_sign=1, expected_scale=None):
        """Compare literal unnormalized numerator to N times direct convolution."""
        left = self.layout(self.transform(u, -1), pi, alpha)
        right = self.layout(self.transform(v, -1), sigma, beta)
        pointwise = tuple(self.ring.mul(a, b) for a, b in zip(left, right))
        actual = self.layout(self.transform(pointwise, inverse_sign), rho, omega)
        factor = self.n if expected_scale is None else expected_scale
        expected = tuple(self.ring.scale(x, factor) for x in self.convolution(u, v))
        return actual, expected

    def first_basis_failure(self, **layout):
        for i in range(self.n):
            for j in range(self.n):
                actual, expected = self.evaluate(self.basis(i), self.basis(j), **layout)
                for k, (a, b) in enumerate(zip(actual, expected)):
                    if a != b:
                        return {"input_basis": [i, j], "output_index": k,
                                "actual_numerator": list(a), "expected_numerator": list(b),
                                "common_denominator": self.n ** 3,
                                "cyclotomic_order": self.m}
        return None
