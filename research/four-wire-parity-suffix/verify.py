#!/usr/bin/env python3
"""Exact four-wire parity suffix corroboration.

Produced by Nick Petalas. Apache-2.0.
"""

from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from math import isqrt
from pathlib import Path

ZERO = (F(0), F(0))
ONE = (F(1), F(0))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def sub(x, y):
    return (x[0] - y[0], x[1] - y[1])


def mul(x, y):
    return (x[0] * y[0] - x[1] * y[1],
            x[0] * y[1] + x[1] * y[0])


def radical(integer):
    """Return c,d with sqrt(integer)=c*sqrt(d), d squarefree."""
    if not 0 <= integer <= 2 ** 40:
        raise ValueError("radicand capacity")
    coefficient, residual, remainder = 1, 1, integer
    if not remainder:
        return 0, 1
    for divisor in range(2, isqrt(integer) + 1):
        if divisor * divisor > remainder:
            break
        exponent = 0
        for _ in range(41):
            if remainder % divisor:
                break
            remainder //= divisor
            exponent += 1
        coefficient *= divisor ** (exponent // 2)
        if exponent % 2:
            residual *= divisor
    if remainder > 1:
        residual *= remainder
    require(coefficient * coefficient * residual == integer,
            "exact radical decomposition")
    return coefficient, residual


def magnitude(z):
    square = z[0] * z[0] + z[1] * z[1]
    coefficient, residual = radical(square.numerator * square.denominator)
    return () if not coefficient else ((residual, F(coefficient, square.denominator)),)


def total(*expressions):
    terms = {}
    for expression in expressions:
        for radicand, coefficient in expression:
            terms[radicand] = terms.get(radicand, F(0)) + coefficient
    return tuple(sorted((r, c) for r, c in terms.items() if c))


def compare(x, y):
    difference = total(x, tuple((r, -c) for r, c in y))
    if not difference:
        return 0
    for bits in (16, 32, 64, 128, 256):
        lower = upper = F(0)
        scale = 2 ** bits
        for radicand, coefficient in difference:
            square = radicand * scale * scale
            floor = isqrt(square)
            ceiling = floor + (floor * floor != square)
            lo, hi = F(floor, scale), F(ceiling, scale)
            lower += coefficient * (lo if coefficient > 0 else hi)
            upper += coefficient * (hi if coefficient > 0 else lo)
        if lower > 0:
            return 1
        if upper < 0:
            return -1
    raise ArithmeticError("exact comparison did not separate within capacity")


def largest(expressions):
    require(1 <= len(expressions) <= 16, "finite maximum capacity")
    answer = expressions[0]
    for expression in expressions[1:]:
        if compare(expression, answer) > 0:
            answer = expression
    return answer


def identity():
    return tuple(tuple(ONE if i == j else ZERO for j in range(4))
                 for i in range(4))


def multiply(a, b):
    rows = []
    for i in range(4):
        row = []
        for j in range(4):
            value = ZERO
            for k in range(4):
                value = add(value, mul(a[i][k], b[k][j]))
            row.append(value)
        rows.append(tuple(row))
    return tuple(rows)


def norm(matrix):
    return largest(tuple(total(*(magnitude(z) for z in row)) for row in matrix))


def elementary(updates):
    rows = [list(row) for row in identity()]
    for target, source, coefficient in updates:
        rows[target][source] = add(rows[target][source], coefficient)
    return tuple(map(tuple, rows))


def compiler(a, b, c, even_first):
    """Derive the literal parity macros by truncated polynomial division."""
    for z in (a, b, c):
        if len(z) != 2 or any(not isinstance(x, F) or abs(x) > 2 for x in z):
            raise ValueError("bounded Gaussian-rational coefficient required")
    even, odd = (ONE, a), (b, c)
    quotient = [ZERO, ZERO]
    for i in range(2):
        quotient[i] = odd[i]
        for j in range(1, i + 1):
            quotient[i] = sub(quotient[i], mul(even[j], quotient[i - j]))
    schur = sub(even[1], mul(odd[0], quotient[0]))
    right = elementary(((2, 1, quotient[0]),))
    left = elementary(((1, 0, quotient[0]), (3, 0, quotient[1]),
                       (3, 2, quotient[0])))
    children = (elementary(((2, 0, even[1]),)),
                elementary(((3, 1, schur),)))
    return (right, *children[::1 if even_first else -1], left)


def cut_products(word):
    prefixes = [identity()]
    for gate in word:
        prefixes.append(multiply(gate, prefixes[-1]))
    suffixes = [identity()] * 5
    for i in range(3, -1, -1):
        suffixes[i] = multiply(suffixes[i + 1], word[i])
    return tuple(zip(prefixes, suffixes))


def predicted(a, b, c):
    endpoint = total(magnitude(a), magnitude(b), magnitude(c))
    residual = sub(c, mul(a, b))
    schur = sub(a, mul(b, b))
    transported = total(magnitude(b), magnitude(schur),
                        largest((magnitude(c), magnitude(residual))))
    return total(magnitude(ONE), largest((endpoint, transported)))


def target(a, b, c):
    coefficients = (ONE, b, a, c)
    return tuple(tuple(coefficients[i - j] if i >= j else ZERO
                       for j in range(4)) for i in range(4))


def fixture(a, b, c):
    expected = target(a, b, c)
    maxima = []
    for order in (True, False):
        cuts = cut_products(compiler(a, b, c, order))
        for prefix, suffix in cuts:
            require(multiply(suffix, prefix) == expected, "all-input endpoint at cut")
        maxima.append(largest(tuple(norm(q) for _, q in cuts)))
    observed = largest(tuple(maxima))
    require(compare(observed, predicted(a, b, c)) == 0,
            "exact full-complex per-symbol formula")
    tail = total(magnitude(a), magnitude(b), magnitude(c))
    require(all(r == 1 for r, _ in tail), "rational fixture tail")
    t = sum((v for _, v in tail), F(0))
    envelope = ((1, 1 + t + t * t),)
    equality = compare(observed, envelope) == 0
    require(compare(observed, envelope) <= 0, "tail-budget envelope")
    require(equality == (a == ZERO and c == ZERO), "complete extremizer criterion")
    return 10, equality, compare(maxima[0], maxima[1]) > 0


def controls():
    half, quarter = (F(1, 2), F(0)), (F(1, 4), F(0))
    word = compiler(ZERO, half, ZERO, True)
    expected = target(ZERO, half, ZERO)
    require(cut_products((word[0], word[1], identity(), word[3]))[-1][0]
            != expected, "missing Schur child detected")
    require(cut_products((*word[:3], identity()))[-1][0]
            != expected, "missing root left macro detected")
    require(cut_products((*word[1:], word[0]))[-1][0]
            != expected, "wrong chronology detected")
    require(compare(predicted(ZERO, half, ZERO), norm(expected)) > 0,
            "endpoint-only bound rejected")
    require(compare(predicted(half, ZERO, ZERO), ((1, F(7, 4)),)) < 0,
            "binomial value is not every symbol's exact value")
    require(fixture(sub(ZERO, quarter), half, ZERO)[2],
            "odd-first-only schedule misses the maximum")
    require(compare(magnitude((F(1), F(1))), ((1, F(7, 5)),)) > 0,
            "nonrational square root comparison")
    require(compare(magnitude((F(3, 5), F(4, 5))), magnitude(ONE)) == 0,
            "Pythagorean modulus equality")
    rejected = 0
    for bad in ((3, F(0)), (F(3), F(0))):
        try:
            compiler(bad, ZERO, ZERO, True)
        except ValueError:
            rejected += 1
    require(rejected == 2, "coefficient type and capacity failures")
    return 10


def main():
    phases = ((F(1), F(0)), (F(-1), F(0)), (F(0), F(1)),
              (F(0), F(-1)), (F(3, 5), F(4, 5)))
    values = (ZERO,) + tuple(mul((scale, F(0)), phase)
                             for scale in (F(1, 4), F(1, 2)) for phase in phases)
    cuts = equalities = order_gaps = fixtures = 0
    for a, b, c in product(values, repeat=3):
        count, equality, gap = fixture(a, b, c)
        fixtures += 1
        cuts += count
        equalities += equality
        order_gaps += gap
    controls_count = controls()
    require(fixtures == 11 ** 3 and cuts == 10 * fixtures, "complete finite grid")
    require(equalities == len(values), "every and only binomial extremizer")
    files = sorted(Path(__file__).resolve().parent.iterdir())
    hashes = {p.name: sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
    print(json.dumps({"status": "PASS_FOUR_WIRE_PARITY_SUFFIX", "fixtures": fixtures,
                      "cuts": cuts, "extremizers": equalities,
                      "order_sensitive_fixtures": order_gaps,
                      "controls": controls_count, "errors": 0,
                      "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
