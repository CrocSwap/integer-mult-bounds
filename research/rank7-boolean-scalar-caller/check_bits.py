# SPDX-License-Identifier: Apache-2.0
"""Exhaustive truth columns and an independent one-bit array interpreter."""

import json
from fractions import Fraction as Q

import caller
from replay import lower, templates

ALPHABET = [
    ("add", a, b)
    for a, b in [
        (-7, 4),
        (-5, 8),
        (-3, 2),
        (-3, 4),
        (-3, 8),
        (-2, 1),
        (-1, 1),
        (-1, 2),
        (-1, 4),
        (-1, 8),
        (1, 1),
        (1, 2),
        (1, 4),
        (1, 8),
        (2, 1),
        (3, 2),
        (3, 4),
        (3, 8),
        (5, 8),
        (7, 8),
    ]
]
ALPHABET += [
    ("scale", a, b)
    for a, b in [
        (-2, 1),
        (-1, 1),
        (-1, 2),
        (1, -2),
        (1, -1),
        (1, 1),
        (1, 2),
        (2, -1),
        (2, 1),
    ]
]


def recipe_guard(recipe, target, source, width):
    rows = [Q(target), Q(source), Q(0)]
    for instruction in recipe:
        kind, t = instruction[:2]
        if kind == "copy":
            caller.require(rows[t] == 0, "zero copy target")
            rows[t] = rows[instruction[2]]
        elif kind == "add":
            rows[t] += instruction[3] * rows[instruction[2]]
        else:
            rows[t] *= {"half": Q(1, 2), "double": 2, "neg": -1, "clear": 0}[kind]
        caller.require(rows[t].denominator == 1, "recipe grid")
        caller.require(
            -(1 << (width - 1)) <= rows[t] < 1 << (width - 1), "recipe range"
        )
    caller.require(rows[1:] == [source, 0], "recipe cleanup")
    return int(rows[0])


def packed(cases, gates, width):
    caller.require(0 < len(cases) <= 16384, "bounded truth columns")
    banks = {(k, i): 0 for k in range(4) for i in range(width - (k == 3))}
    expected = dict(banks)
    for column, (source, target, result) in enumerate(cases):
        for bank, value in ((0, target), (1, source)):
            for i in range(width):
                banks[bank, i] |= ((value >> i) & 1) << column
        for bank, value in ((0, result), (1, source)):
            for i in range(width):
                expected[bank, i] |= ((value >> i) & 1) << column
    after = caller.apply(gates, banks, width)
    caller.require(after == expected, "all truth columns / source / scratch / carry")
    return len(cases)


def array(gates, width, target, source):
    banks = [[(v >> i) & 1 for i in range(width)] for v in (target, source, 0)]
    banks.append([0] * (width - 1))
    for gate in gates:
        ports = gate[1:]
        if gate[0] == "cx":
            (a, i), (b, j) = ports
            banks[b][j] = banks[b][j] ^ banks[a][i]
        else:
            (a, i), (b, j), (c, k) = ports
            banks[c][k] = banks[c][k] ^ (banks[a][i] and banks[b][j])
    caller.require(
        banks[1] == [(source >> i) & 1 for i in range(width)], "array source"
    )
    caller.require(not any(banks[2]) and not any(banks[3]), "array cleanup")
    return sum(bit << i for i, bit in enumerate(banks[0]))


def cases_for(width, key, policy):
    kind, a, b = key
    recipe = lower.certify(kind, a, b, policy="target_walk")
    limit = 1 << (width - 1)
    cases = []
    for source in range(-limit, limit) if kind == "add" else [0]:
        for target in range(-limit, limit):
            try:
                result = caller.guards(width, kind, a, b, target, source)
                if policy == "control":
                    caller.require(
                        recipe_guard(recipe, target, source, width) == result,
                        "control endpoint",
                    )
            except ValueError:
                continue
            cases.append((source, target, result))
    return cases


def run():
    count, circuits = 0, 0
    # Opposite orientations reverse coefficient signs; include the exact union.
    alphabet = sorted(set(ALPHABET + [("add", -7, 8), ("add", 7, 4)]))
    for width in range(3, 8):
        emitted = json.loads(json.dumps(templates(width, alphabet)))
        for key in alphabet:
            for policy, gates in emitted[f"{key[0]}:{key[1]}:{key[2]}"].items():
                cases = cases_for(width, key, policy)
                if cases:
                    count += packed(cases, gates, width)
                circuits += 1
    fixtures = 0
    for width in (23, 64, 84, 148, 256):
        emitted = json.loads(json.dumps(templates(width, alphabet)))
        limit = 1 << (width - 1)
        for key in alphabet:
            kind, a, b = key
            recipe = lower.certify(kind, a, b, policy="target_walk")
            for source, target in (
                (0, 0),
                (8, -17),
                (-8, 17),
                (0, -limit + 1),
                (0, limit - 1),
            ):
                for policy, gates in emitted[f"{kind}:{a}:{b}"].items():
                    try:
                        expected = caller.guards(width, kind, a, b, target, source)
                        if policy == "control":
                            recipe_guard(recipe, target, source, width)
                    except ValueError:
                        continue
                    caller.require(
                        array(gates, width, target, source) == expected % (1 << width),
                        "independent array signed fixture",
                    )
                    fixtures += 1
    return {
        "exhaustive_widths": [3, 4, 5, 6, 7],
        "truth_columns": count,
        "small_circuits": circuits,
        "array_fixtures": fixtures,
    }
