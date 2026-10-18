# SPDX-License-Identifier: Apache-2.0
"""A native-tariff optimum, not a scalar-gate-count optimum."""

import copy
from fractions import Fraction
from itertools import product

from contract import FRAME, OLD, START, expected_cleanup, operator
from frames import require

OPTIMAL = [
    ["add", 230, 22, -1, 1, FRAME],
    ["add", 22, 230, 1, 1, FRAME],
    ["scale", 22, -1, 1, FRAME],
    ["scale", 230, -1, 1, FRAME],
]
TARGET = ((0, -1), (1, -1))
INVERSE = ((-1, 1), (-1, 0))


def price(gate):
    """Independently recount bw_emit's one-real-component bound."""
    kind = gate[0]
    if kind in ("clear", "copy"):
        return 1
    require(kind in ("add", "scale"), "priced scalar kind")
    a, b = gate[3:5] if kind == "add" else gate[2:4]
    require(type(a) is int and type(b) is int and b != 0, "rational coefficient")
    q = Fraction(a, b)
    require(q != 0, "remove identity zero ADDs before pricing")
    numerator, denominator = abs(q.numerator), q.denominator
    require(denominator & (denominator - 1) == 0, "dyadic denominator")
    numerator_bits = bin(numerator)[2:]
    denominator_exponent = len(bin(denominator)[2:]) - 1
    if kind == "scale":
        require(numerator & (numerator - 1) == 0, "signed-power-of-two SCALE")
        return abs(len(numerator_bits) - 1 - denominator_exponent) + int(q < 0)
    return (
        3 + len(numerator_bits) - 1 + numerator_bits.count("1") + denominator_exponent
    )


def matrix(gates):
    rows = operator(gates, (22, 230))
    return tuple(
        tuple(rows[r].get(c, Fraction(0)) for c in (22, 230)) for r in (22, 230)
    )


def lower_bound(target):
    """Check the hypotheses of the written all-length cost-at-least-ten proof."""
    require(len(target) == 2 and all(len(row) == 2 for row in target), "two rows")
    a, b = target[0]
    c, d = target[1]
    require(b != 0 and c != 0, "both ADD directions required")
    require(a * d - b * c == 1, "unit determinant forces a nontrivial SCALE pair")
    require(a != 1 and d != 1, "two unscaled ADDs cannot realize the target")
    return 10


def bounded_exclusions():
    """All two-ADD cores with tariff <10, after deleting identity SCALEs."""
    unit = [
        ["add", t, s, a, 1, FRAME] for t, s in ((22, 230), (230, 22)) for a in (-1, 1)
    ]
    next_cost = [
        ["add", t, s, a, b, FRAME]
        for t, s in ((22, 230), (230, 22))
        for a, b in ((-2, 1), (2, 1), (-1, 2), (1, 2))
    ]
    scales = [
        ["scale", t, a, b, FRAME]
        for t in (22, 230)
        for a, b in ((-1, 1), (2, 1), (1, 2))
    ]
    count = 0
    for first, second in product(unit + next_cost, repeat=2):
        if price(first) + price(second) < 10:
            require(matrix([first, second]) not in (TARGET, INVERSE), "cheap ADD core")
            count += 1
    for first, second, scale in product(unit, unit, scales):
        for position in range(3):
            gates = [first, second]
            gates.insert(position, scale)
            require(sum(map(price, gates)) == 9, "cost-nine core")
            require(matrix(gates) not in (TARGET, INVERSE), "cheap scaled core")
            count += 1
    require(count == 368, "complete bounded two-ADD core enumeration")
    return count


def produce(parent):
    require(parent["restore"][START : START + 4] == OLD, "literal PR3042 block")
    require(parent["cleanup"] == expected_cleanup(parent), "parent inverse cleanup")
    result = copy.deepcopy(parent)
    result["restore"][START : START + 4] = copy.deepcopy(OPTIMAL)
    result["cleanup"] = expected_cleanup(result)
    return result
