# SPDX-License-Identifier: Apache-2.0
"""Small exact integer-polynomial algebra with explicit rounding atoms.

No numerical sampling and no source arithmetic implementation is used here.
An atom such as trunc(P,s) remains opaque: it cannot be distributed through
addition or multiplication. Polynomial normalization only uses ring laws.
"""
from dataclasses import dataclass
import json


def need(value, message):
    if not value:
        raise ValueError(message)


@dataclass(frozen=True)
class Poly:
    terms: tuple

    @staticmethod
    def number(value):
        need(type(value) is int, 'integer polynomial constant')
        return Poly(()) if value == 0 else Poly((((), value),))

    @staticmethod
    def from_dict(values):
        return Poly(tuple(sorted((monomial, coefficient) for monomial, coefficient in values.items() if coefficient)))

    @staticmethod
    def atom(kind, *values):
        data = [kind, *(x.data() if isinstance(x, Poly) else x for x in values)]
        key = json.dumps(data, separators=(',', ':'), sort_keys=True)
        return Poly((((key,), 1),))

    def data(self):
        return [[list(m), c] for m, c in self.terms]

    def __add__(self, other):
        other = as_poly(other)
        result = dict(self.terms)
        for monomial, coefficient in other.terms:
            result[monomial] = result.get(monomial, 0)+coefficient
        return Poly.from_dict(result)

    __radd__ = __add__

    def __neg__(self):
        return Poly(tuple((m, -c) for m, c in self.terms))

    def __sub__(self, other):
        return self+-as_poly(other)

    def __rsub__(self, other):
        return as_poly(other)+-self

    def __mul__(self, other):
        other = as_poly(other)
        result = {}
        for a, x in self.terms:
            for b, y in other.terms:
                monomial = tuple(sorted(a+b))
                result[monomial] = result.get(monomial, 0)+x*y
        return Poly.from_dict(result)

    __rmul__ = __mul__

    def integer(self):
        if not self.terms:
            return 0
        need(len(self.terms) == 1 and self.terms[0][0] == (), 'literal integer required')
        return self.terms[0][1]

    def positive_variable_order(self):
        """Only for positive-variable magnitude cases, not arbitrary inputs."""
        if not self.terms:
            return 0
        if all(coefficient > 0 for _, coefficient in self.terms):
            return 1
        if all(coefficient < 0 for _, coefficient in self.terms):
            return -1
        raise ValueError('uncertified magnitude order')


def as_poly(value):
    return value if isinstance(value, Poly) else Poly.number(value)


def variable(name):
    return Poly.atom('integer', name)


def power_two(exponent):
    return Poly.atom('power_two', as_poly(exponent))


def truncation(value, exponent):
    return Poly.atom('truncate_toward_zero', as_poly(value), as_poly(exponent))


def ceiling_log(value):
    return Poly.atom('ceiling_log_two', as_poly(value))
