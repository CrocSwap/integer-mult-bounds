# SPDX-License-Identifier: Apache-2.0
"""One exact, source-addressed dyadic contraction. No word search or frame edit."""

import copy
from fractions import Fraction

from frames import registers, require

START = 175
FRAME = [256, 128, 64, 38, 20, 10, 1]
OLD = [["add", x, y, c, 1, FRAME] for x, y, c in
       ((22, 230, -1), (230, 22, 1), (22, 230, -1), (230, 22, 1))]
NEW = [["add", x, y, c, 1, FRAME] for x, y, c in
       ((230, 22, 1), (22, 230, -1), (230, 22, 2))]


def operator(gates, universe):
    """Exact rows on independent dirty columns, including untouched registers."""
    require(len(gates) <= 1000 and len(universe) <= 704, "bounded scalar operator")
    rows = {r: {r: Fraction(1)} for r in universe}
    for gate in gates:
        kind, target = gate[:2]
        require(kind in ("add", "scale"), "scalar substitution only")
        require(all(r in rows for r in registers(gate)), "operator registers")
        if kind == "scale":
            require(len(gate) == 5 and gate[3] != 0, "scale shape and denominator")
            factor = Fraction(gate[2], gate[3])
            require(factor != 0, "invertible scale")
            rows[target] = {r: factor * v for r, v in rows[target].items()}
        else:
            require(len(gate) == 6 and gate[4] != 0, "ADD shape and denominator")
            require(target != gate[2], "distinct ADD operands")
            factor = Fraction(gate[3], gate[4])
            row = rows[target].copy()
            for r, value in rows[gate[2]].items():
                row[r] = row.get(r, Fraction(0)) + factor * value
            rows[target] = {r: value for r, value in row.items() if value}
    return rows


def projected_block(gates):
    """2x2 matrix over Q[P]/(P^2-P), with entries (I coefficient, P coefficient)."""
    require(len(gates) <= 4, "bounded projected block")
    rows = [[(Fraction(1), Fraction(0)), (Fraction(0), Fraction(0))],
            [(Fraction(0), Fraction(0)), (Fraction(1), Fraction(0))]]
    for gate in gates:
        require(gate[0] == "add" and gate[-1] == FRAME, "one common frame")
        require(set(gate[1:3]) == {22, 230}, "two projected registers")
        target = 0 if gate[1] == 22 else 1
        source = 1 - target
        factor = Fraction(gate[3], gate[4])
        projected = [(Fraction(0), factor * (a + b)) for a, b in rows[source]]
        rows[target] = [(a + c, b + d) for (a, b), (c, d) in
                        zip(rows[target], projected, strict=True)]
    return rows


def expected_cleanup(word):
    """Inherited inverse reverse with injective private-buffer renaming."""
    full = [256, 128, 64, 32, 16, 8, 4, 2, 1]
    restored = set(map(int, word["helper_final"]))
    require(len(restored) == 91, "91 restored helpers")
    forward = list(word["A"][word["prelude_events"]:])
    warps = {}
    for index, record in enumerate(word["warps"], 1):
        warps.setdefault(record[0], []).append(["warp", record[1], index])
    for index in range(len(word["B"]) + 1):
        forward.extend(warps.get(index, []))
        if index < len(word["B"]):
            forward.append(word["B"][index])
    forward.extend(word["restore"])
    require(len(forward) <= 60000, "bounded cleanup body")
    cleanup = []
    for gate in reversed(forward):
        kind, target = gate[:2]
        if kind != "warp" and 112 <= target < 224:
            continue
        target = target + 704 if target in restored else target
        if kind == "warp":
            inverse = [kind, target, -gate[2], full]
        elif kind == "scale":
            inverse = [kind, target, gate[3], gate[2], full]
        else:
            source = gate[2] + 704 if gate[2] in restored else gate[2]
            inverse = [kind, target, source, -gate[3], gate[4], full]
        cleanup.append(inverse)
    return cleanup


def produce(parent):
    require(parent["restore"][START:START + 4] == OLD, "literal restore preimage")
    require(parent["cleanup"] == expected_cleanup(parent), "parent cleanup")
    result = copy.deepcopy(parent)
    result["restore"][START:START + 4] = copy.deepcopy(NEW)
    result["cleanup"] = expected_cleanup(result)
    return result
