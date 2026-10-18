# SPDX-License-Identifier: Apache-2.0
"""Exhaustive complete-boundary checks and a second literal gate interpreter."""

from fractions import Fraction as Q
import random

import scalars as s


def packed(width, cases):
    s.require(0 < len(cases) <= 65536, "bounded truth batch")
    data = [bytearray((len(cases) + 7) // 8) for _ in range(2 * width + 1)]
    for lane, (source, target, _) in enumerate(cases):
        for bank, value in enumerate((target, source)):
            for bit in range(width):
                data[bank * width + bit][lane // 8] |= ((value >> bit) & 1) << (
                    lane % 8
                )
    return [int.from_bytes(row, "little") for row in data]


def check_batch(width, gates, cases):
    before = packed(width, cases)
    after = s.apply(width, gates, before)
    expected = packed(width, [(source, value, value) for source, _, value in cases])
    s.require(after == expected, "complete literal truth columns and clean return")
    s.require(s.apply(width, list(reversed(gates)), after) == before, "literal inverse")


def array_apply(width, gates, source, target):
    """Independent Boolean-list evaluator; no call to the packed interpreter."""
    wires = [bool((v >> i) & 1) for v in (target, source) for i in range(width)] + [
        False
    ]
    for gate in gates:
        if len(gate) == 2:
            wires[gate[1]] = wires[gate[1]] != wires[gate[0]]
        elif wires[gate[0]] and wires[gate[1]]:
            wires[gate[2]] = not wires[gate[2]]
    return wires


def run(alphabet, build, guards):
    s.require(1 <= len(alphabet) <= 32, "bounded scalar alphabet")
    columns = circuits = fixtures = 0
    rng = random.Random(481516)
    for width in range(4, 8):
        limit = 1 << (width - 1)
        for kind, a, b in alphabet:
            q = Q(a, b)
            cases = []
            for source in range(-limit, limit):
                for target in range(-limit, limit):
                    if kind == "add":
                        if source % q.denominator:
                            continue
                        value = target + q * source
                    else:
                        try:
                            value = guards(width, kind, a, b, target, source)
                        except ValueError:
                            continue
                    cases.append((source, target, int(value)))
            check_batch(width, build(width, kind, a, b), cases)
            columns += len(cases)
            circuits += 1
    for width in (23, 64, 84, 148, 256):
        limit = 1 << (width - 1)
        for kind, a, b in alphabet:
            gates = build(width, kind, a, b)
            for _ in range(10):
                source = rng.randrange(-limit, limit)
                target = rng.randrange(-limit // 4, limit // 4)
                q = Q(a, b)
                if kind == "add":
                    source = (source // (16 * q.denominator)) * q.denominator
                else:
                    target = (target // 16) * 8
                value = guards(width, kind, a, b, target, source)
                actual = array_apply(width, gates, source, target)
                expected = [
                    bool((v >> i) & 1) for v in (value, source) for i in range(width)
                ] + [False]
                s.require(actual == expected, "independent array endpoint and return")
                s.require(
                    s.execute(width, gates, source, target) == value % (1 << width),
                    "interpreters agree",
                )
                fixtures += 1
    return {
        "truth_columns": columns,
        "exhaustive_circuits": circuits,
        "array_fixtures": fixtures,
    }
