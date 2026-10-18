# SPDX-License-Identifier: Apache-2.0
"""Independent fixed-denominator replay of the serialized scalar instructions."""

import hashlib
import json
from math import gcd

from vendor.format_source.format import canonical, require

UNIT = 1 << 32


def scaled(row, numerator, denominator):
    require(type(denominator) is int and denominator != 0, "nonzero integer divisor")
    result = {}
    for atom, value in row.items():
        quotient, remainder = divmod(value * numerator, denominator)
        require(remainder == 0, "exact fixed-denominator division")
        if quotient:
            result[atom] = quotient
    require(len(result) <= 4096, "bounded integer row")
    return result


def plus(left, right, sign):
    result = left.copy()
    for atom, value in right.items():
        combined = result.get(atom, 0) + sign * value
        if combined:
            result[atom] = combined
        else:
            result.pop(atom, None)
    require(len(result) <= 4096, "bounded integer sum")
    return result


def instruction(rows, item):
    require(len(item) in (2, 3, 4), "literal instruction shape")
    kind, target = item[:2]
    require(type(target) is int and 0 <= target < 3, "literal target")
    if kind in ("copy", "add"):
        require(len(item) == (3 if kind == "copy" else 4), "binary instruction")
        source = item[2]
        require(type(source) is int and 0 <= source < 3 and source != target, "source")
        if kind == "copy":
            rows[target] = dict(rows[source])
        else:
            require(type(item[3]) is int and item[3] in (-1, 1), "signed unit ADD")
            rows[target] = plus(rows[target], rows[source], item[3])
    else:
        require(len(item) == 2, "unary instruction")
        factors = {"clear": (0, 1), "neg": (-1, 1), "double": (2, 1), "half": (1, 2)}
        require(kind in factors, "known literal instruction")
        rows[target] = scaled(rows[target], *factors[kind])
    return target


def record(index, offset, target, row):
    terms = []
    for (variable, word), value in sorted(row.items()):
        divisor = gcd(abs(value), UNIT)
        terms.append([variable, list(word), value // divisor, UNIT // divisor])
    return [index, offset, target, terms]


def macro(stream, index, event, before, source, after, digest):
    raw = stream.readline(16_385)
    require(0 < len(raw) <= 16_384, "bounded serialized macro")
    literal = json.loads(raw)
    require(
        literal["event"] == index and literal["gate"] == event[1], "literal binding"
    )
    require(literal["frame"] == event[2], "literal common frame")
    recipe = literal["instructions"]
    require(len(recipe) <= 32, "bounded literal recipe")
    rows = [before, source, {}]
    for offset, item in enumerate(recipe):
        target = instruction(rows, item)
        digest.update(canonical(record(index, offset, target, rows[target])))
    require(rows == [after, source, {}], "integer endpoint/source/scratch identity")


def trace(events, literals):
    require(len(events) <= 30_000, "bounded integer stream")
    state = {("L", r): {(r, ()): UNIT} for r in range(632)}
    digest = hashlib.sha256()
    active = ended = False
    for index, event in enumerate(events):
        tag = event[0]
        if tag == "phase":
            if event[1] == "A":
                active = True
            elif active:
                require(event[1] == "centers", "integer A boundary")
                ended = True
                break
            continue
        if tag in ("adapter", "residual_adapter", "climb"):
            continue
        require(tag in ("warp", "scalar"), "known integer event")
        if tag == "warp":
            target, operation = tuple(event[1]), event[2]
            moved = {}
            for (variable, word), value in state[target].items():
                changed = (
                    word[1:] if word and word[0] == -operation else (operation, *word)
                )
                require(len(changed) <= 256, "bounded integer warp word")
                moved[variable, changed] = value
            state[target] = moved
            continue
        gate = event[1]
        target = tuple(gate[1])
        before = state[target]
        if gate[0] == "add":
            source = state[tuple(gate[2])]
            after = plus(before, scaled(source, gate[3], gate[4]), 1)
        else:
            require(gate[0] == "scale", "integer ordinary scalar")
            source = {}
            after = scaled(before, gate[2], gate[3])
        macro(literals, index, event, before, source, after, digest)
        state[target] = after
    require(ended and literals.read(1) == b"", "complete literal consumption")
    return digest.hexdigest()
