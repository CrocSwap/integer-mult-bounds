# SPDX-License-Identifier: Apache-2.0
"""Separate fixed-denominator execution of literal coefficient instructions."""

from fractions import Fraction as Q

DENOMINATOR = 1 << 32


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encode(row):
    require(len(row) <= 4096, "bounded integer row")
    out = {}
    for atom, value in row.items():
        scaled = value * DENOMINATOR
        require(scaled.denominator == 1, "integer interpreter input grid")
        if scaled.numerator:
            out[atom] = scaled.numerator
    return out


def step(rows, instruction):
    require(len(rows) == 3, "three local rows")
    kind, target = instruction[:2]
    require(type(target) is int and 0 <= target < 3, "literal target")
    before = rows[target]
    if kind in ("add", "copy"):
        source = instruction[2]
        require(
            type(source) is int and 0 <= source < 3 and target != source,
            "literal source",
        )
        if kind == "copy":
            require(not before, "copy requires zero scratch")
            after = rows[source].copy()
        else:
            sign = instruction[3]
            require(sign in (-1, 1), "literal ADD sign")
            after = before.copy()
            for atom, value in rows[source].items():
                after[atom] = after.get(atom, 0) + sign * value
    elif kind == "half":
        require(
            all(value % 2 == 0 for value in before.values()), "exact half remainder"
        )
        after = {atom: value // 2 for atom, value in before.items()}
    else:
        require(kind in ("clear", "neg", "double"), "literal unary kind")
        factor = {"clear": 0, "neg": -1, "double": 2}[kind]
        after = {atom: value * factor for atom, value in before.items()}
    rows[target] = {atom: value for atom, value in after.items() if value}
    require(len(rows[target]) <= 4096, "bounded changed integer row")
    return rows[target]


def check_rows(recipe, before, source, expected, rational_rows):
    require(len(recipe) == len(rational_rows) <= 32, "complete bounded microstates")
    rows = [encode(before), encode(source), {}]
    for instruction, rational in zip(recipe, rational_rows, strict=True):
        actual = step(rows, instruction)
        require(
            actual == encode(rational), "integer/Fraction every-microstate equality"
        )
    require(
        rows == [encode(expected), encode(source), {}],
        "literal macro/source restoration/scratch cleanup",
    )
    return len(recipe)


def bounds(row, rank):
    require(type(rank) is int and 0 <= rank <= 9, "frame rank")
    values = encode(row).values()
    power = (rank + 1) // 2
    grid = max(
        (32 - min(32, (abs(v) & -abs(v)).bit_length() - 1) for v in values), default=0
    )
    return grid + power, Q(sum(abs(v) for v in values), DENOMINATOR) * (1 << power)
