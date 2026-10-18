# SPDX-License-Identifier: Apache-2.0
"""Negate a Gaussian component pair using its own two banks and one carry."""

from fractions import Fraction

import bindings

s = bindings.load_scalar()
MAX_PAIR_GATES = (42 * s.MAX_WIDTH - 24) + 24 * (3 * s.MAX_WIDTH - 2)


def validate(width, gates):
    """A Gaussian pair can exceed the inherited single-real gate limit."""
    s.validate(width, ())
    s.require(len(gates) <= MAX_PAIR_GATES, "bounded Gaussian pair circuit")
    for start in range(0, len(gates), s.MAX_GATES):
        s.validate(width, gates[start : start + s.MAX_GATES])


def apply(width, gates, wires):
    """Run at most two bounded single-real interpreter batches."""
    validate(width, gates)
    result = s.apply(width, (), wires)
    for start in range(0, len(gates), s.MAX_GATES):
        result = s.apply(width, gates[start : start + s.MAX_GATES], result)
    return result


def negate(width):
    """Four shears over Z/(2**width), including modular overflow."""
    s.validate(width, ())
    real = tuple(range(width))
    imag = tuple(range(width, 2 * width))
    add = s.adder(imag, real, 2 * width)
    subtract_twice = list(reversed(s.adder(real[:-1], imag[1:], 2 * width)))
    gates = add + subtract_twice + add + subtract_twice
    s.validate(width, gates)
    s.require(
        s.counts(gates) == {"cx": 16 * width - 16, "ccx": 8 * width - 12},
        "complete paired negation tariff",
    )
    return gates


def shift_pair(width, exponent):
    recipe = [("double" if exponent > 0 else "half", 0)] * abs(exponent)
    gates = s.scale(width, recipe, Fraction(2) ** exponent)
    s.require(all(i < width for g in gates for i in g), "single-component shift")
    return gates + [tuple(i + width for i in g) for g in gates]


def coefficient(a, b):
    """Parse exactly the inherited bounded signed-power SCALE alphabet."""
    s.require(type(a) is int and type(b) is int and b != 0, "integer coefficient")
    value = Fraction(a, b)
    s.require(
        abs(value.numerator) <= 255 and value.denominator <= 4096,
        "bounded dyadic coefficient",
    )
    s.require(
        abs(value.numerator).bit_count() == 1 and value.denominator.bit_count() == 1,
        "signed power of two",
    )
    exponent = abs(value.numerator).bit_length() - value.denominator.bit_length()
    s.require(abs(exponent) <= 12, "bounded scale exponent")
    return value, exponent


def circuit(width, a, b, recipe, *, control=False):
    """Compile the same canonical SCALE recipe for both components."""
    s.validate(width, ())
    value, exponent = coefficient(a, b)
    expected = [("neg", 0)] if value < 0 else []
    expected += [("double" if exponent > 0 else "half", 0)] * abs(exponent)
    s.require(recipe == expected, "canonical guarded SCALE recipe")
    gates = []
    if value < 0:
        if control:
            single = s.negate(width)
            exchange = (
                tuple(range(width, 2 * width)) + tuple(range(width)) + (2 * width,)
            )
            gates = single + [tuple(exchange[i] for i in g) for g in single]
        else:
            gates = negate(width)
    gates += shift_pair(width, exponent)
    validate(width, gates)
    return gates


def endpoint(width, a, b, value):
    """Guard the inherited signed SCALE prefixes, never the modular shears."""
    s.validate(width, ())
    s.require(type(value) is int, "encoded signed integer")
    factor, exponent = coefficient(a, b)
    limit = 1 << (width - 1)
    s.require(-limit <= value < limit, "signed input")
    current = -value if factor < 0 else value
    s.require(-limit <= current < limit, "negation prefix range")
    for _ in range(abs(exponent)):
        s.require(exponent > 0 or current % 2 == 0, "HALF prefix alignment")
        current = current * 2 if exponent > 0 else current // 2
        s.require(-limit <= current < limit, "shift prefix range")
    s.require(current == factor * value, "exact signed endpoint")
    return current


def execute(width, gates, real, imag, *, carry=0):
    """Evaluate a pair without an auxiliary bank; return unsigned bit patterns."""
    validate(width, gates)
    s.require(carry == 0, "clean carry entrance")
    limit = 1 << (width - 1)
    s.require(
        all(type(v) is int and -limit <= v < limit for v in (real, imag)),
        "signed component inputs",
    )
    wires = [(v >> i) & 1 for v in (real, imag) for i in range(width)] + [carry]
    after = apply(width, gates, wires)
    s.require(after[-1] == 0, "clean carry return")
    return tuple(
        sum(after[offset + i] << i for i in range(width)) for offset in (0, width)
    )


def scale(width, a, b, real, imag, recipe, *, carry=0):
    """Guard both signed components before executing a complete SCALE."""
    expected = tuple(endpoint(width, a, b, v) % (1 << width) for v in (real, imag))
    actual = execute(width, circuit(width, a, b, recipe), real, imag, carry=carry)
    s.require(actual == expected, "complete guarded Gaussian SCALE")
    return actual
