# SPDX-License-Identifier: Apache-2.0
"""Complete pair/carry truth checks, independently evaluated signed fixtures."""

import random
from fractions import Fraction

import pairscale as p
from vendor import scalars as s


def pack(width, cases):
    s.require(0 < len(cases) <= 65536, "bounded truth batch")
    rows = [bytearray((len(cases) + 7) // 8) for _ in range(2 * width + 1)]
    for lane, pair in enumerate(cases):
        for bank, value in enumerate(pair):
            for bit in range(width):
                rows[bank * width + bit][lane // 8] |= ((value >> bit) & 1) << (
                    lane % 8
                )
    return [int.from_bytes(row, "little") for row in rows]


def batch(width, gates, inputs, outputs):
    before, expected = pack(width, inputs), pack(width, outputs)
    actual = p.apply(width, gates, before)
    s.require(actual == expected, "complete pair endpoint and carry return")
    s.require(
        p.apply(width, list(reversed(gates)), actual) == before, "literal inverse"
    )


def array_apply(width, gates, real, imag):
    """Separate Boolean-list evaluator, no call to the packed interpreter."""
    wires = [bool((v >> i) & 1) for v in (real, imag) for i in range(width)] + [False]
    for gate in gates:
        if len(gate) == 2:
            wires[gate[1]] = wires[gate[1]] != wires[gate[0]]
        elif wires[gate[0]] and wires[gate[1]]:
            wires[gate[2]] = not wires[gate[2]]
    return wires


def exhaustive(alphabet, lower):
    s.require(1 <= len(alphabet) <= 16, "bounded SCALE alphabet")
    columns = circuits = 0
    for width in range(4, 9):
        bound = 1 << (width - 1)
        inputs = [(x, y) for x in range(-bound, bound) for y in range(-bound, bound)]
        outputs = [(-x, -y) for x, y in inputs]
        batch(width, p.negate(width), inputs, outputs)
        columns += len(inputs)
        circuits += 1
        for a, b in alphabet:
            valid = []
            for value in range(-bound, bound):
                try:
                    valid.append((value, p.endpoint(width, a, b, value)))
                except ValueError:
                    continue
            entries = [(x, y) for x, _ in valid for y, _ in valid]
            expected = [(u, v) for _, u in valid for _, v in valid]
            recipe = lower.certify("scale", a, b, policy="target_walk")
            for control in (False, True):
                batch(
                    width,
                    p.circuit(width, a, b, recipe, control=control),
                    entries,
                    expected,
                )
                columns += len(entries)
                circuits += 1
    return {"truth_columns": columns, "exhaustive_circuits": circuits}


def fixtures(alphabet, lower, guards):
    s.require(1 <= len(alphabet) <= 16, "bounded SCALE alphabet")
    rng, count = random.Random(3152), 0
    for width in (23, 64, 84, 148, 256):
        limit = 1 << (width - 1)
        for a, b in alphabet:
            coefficient = Fraction(a, b)
            recipe = lower.certify("scale", a, b, policy="target_walk")
            gates = p.circuit(width, a, b, recipe)
            for _ in range(12):
                inputs = tuple(
                    (rng.randrange(-limit // 4, limit // 4) // 16) * 8 for _ in range(2)
                )
                values = tuple(guards(width, "scale", a, b, v, 0) for v in inputs)
                s.require(
                    values == tuple(p.endpoint(width, a, b, v) for v in inputs),
                    "independent inherited prefix guards",
                )
                actual = array_apply(width, gates, *inputs)
                expected = [
                    bool((v >> i) & 1) for v in values for i in range(width)
                ] + [False]
                s.require(actual == expected, "independent bit-list endpoint")
                s.require(
                    p.scale(width, a, b, *inputs, recipe)
                    == tuple(int(coefficient * v) % (1 << width) for v in inputs),
                    "integer and gate interpreters agree",
                )
                count += 1
    return count
