# SPDX-License-Identifier: Apache-2.0
"""Check and apply 24 explicit commuting contractions, without a word search."""

from copy import deepcopy
from fractions import Fraction

from contract import expected_cleanup
from frames import registers, require, span, trace
from tariff import price


def check_gate(gate):
    require(isinstance(gate, list) and gate, "gate shape")
    kind = gate[0]
    require(kind in ("add", "scale", "warp"), "gate kind")
    require(len(gate) == (6 if kind == "add" else 5), "gate length")
    require(
        all(type(r) is int and 0 <= r < 704 for r in registers(gate)),
        "original register range",
    )
    if kind == "warp":
        span(tuple(gate[3]))
        span(tuple(gate[4]))
    else:
        require(kind != "add" or gate[1] != gate[2], "distinct ADD registers")
        price(gate)
        span(tuple(gate[-1]))


def commutes(first, other):
    """Conservative exact rule, including common-frame and warp conditions."""
    require(first[0] == "add", "moved gate is an ADD")
    target, source = first[1:3]
    shared = set(registers(first)) & set(registers(other))
    if other[0] == "warp":
        return not shared
    if shared and span(tuple(first[-1])) != span(tuple(other[-1])):
        return False
    if other[0] == "scale":
        return not shared
    return target != other[2] and source != other[1]


def apply_edit(gates, edit, prelude):
    require(isinstance(edit, list) and len(edit) == 6, "edit record")
    first, last, old_first, old_last, replacement, saving = edit
    require(
        type(first) is int
        and type(last) is int
        and prelude <= first < last < len(gates),
        "edit addresses",
    )
    a, b = gates[first], gates[last]
    require(a == old_first and b == old_last, "literal edit preimage")
    require(a[0] == b[0] == "add" and a[:3] == b[:3], "same transvection")
    require(span(tuple(a[-1])) == span(tuple(b[-1])), "same invertible frame")
    require(
        all(commutes(a, gate) for gate in gates[first + 1 : last]),
        "every intervening event commutes",
    )
    coefficient = Fraction(a[3], a[4]) + Fraction(b[3], b[4])
    expected = (
        [*b[:3], coefficient.numerator, coefficient.denominator, b[-1]]
        if coefficient
        else None
    )
    require(replacement == expected, "exact rational combined coefficient")
    delta = price(a) + price(b) - (price(expected) if expected else 0)
    require(type(saving) is int and delta == saving > 0, "strict native saving")
    result = deepcopy(gates)
    if expected:
        result[last] = expected
    else:
        del result[last]
    del result[first]
    return result, delta


def histories_without_addresses(word):
    result = trace(word)
    histories = [[[low, high] for _, low, high in row] for row in result["histories"]]
    return result["profile"], result["widths"], histories


def produce(parent, edits):
    require(
        len(parent["A"]) == 4079 and parent["prelude_events"] == 84,
        "pinned A body and prelude",
    )
    require(len(edits) == 24, "24 explicit witnesses")
    require(parent["cleanup"] == expected_cleanup(parent), "parent cleanup")
    for gate in parent["A"]:
        check_gate(gate)
    candidate = deepcopy(parent)
    savings = []
    for edit in edits:
        candidate["A"], saving = apply_edit(candidate["A"], edit, 84)
        savings.append(saving)
    require(
        all(edit[2][1] >= 224 for edit in edits),
        "every contraction survives cleanup's correction-target omission",
    )
    require(
        len(candidate["A"]) == 4052 and sum(savings) == 85,
        "27 A gates and 85 one-component units removed",
    )
    candidate["cleanup"] = expected_cleanup(candidate)
    require(len(candidate["cleanup"]) == 5189, "27 inverse gates removed")
    require(
        histories_without_addresses(parent) == histories_without_addresses(candidate),
        "every frame itinerary, helper width and recursive child unchanged",
    )
    require(
        {key for key in parent if parent[key] != candidate[key]} == {"A", "cleanup"},
        "only A and its derived inverse change",
    )
    return candidate
