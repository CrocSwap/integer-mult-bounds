#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Nick Petalas.
"""Full-child symbolic replay, adapted from thakrarsagar's PR3297 phase algebra.

The three bitsets hold the low/high Z4 linear coefficients and even quadratic
coefficients of a phase on F_2^73. Formal residual multipliers use 20 bits.
"""
from collections import defaultdict
from functools import cache

BITS = 73
ZERO = (0, 0, 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(left, right):
    a, b, c = left
    d, e, f = right
    return a ^ d, b ^ e ^ (a & d), c ^ f


def scale(value, coefficient):
    result = ZERO
    for _ in range(coefficient % 4):
        result = add(result, value)
    return result


@cache
def axis(vector):
    require(type(vector) is int and 0 <= vector < 1 << BITS, "binary phase axis")
    support = [i for i in range(BITS) if vector >> i & 1]
    cross = sum(1 << (i * BITS + j)
                for offset, i in enumerate(support) for j in support[offset + 1:])
    return vector, 0, cross


def sum_axes(axes):
    require(len(axes) <= BITS, "axis list bound")
    result = ZERO
    for vector in axes:
        result = add(result, axis(vector))
    return result


def phase(matrix, row, exponent, variable=0):
    for column in range(8):
        changed = defaultdict(int)
        for (mask, low, high, cross), coefficient in matrix[row][column].items():
            require(not mask & variable, "formal site repeated along path")
            changed[(mask | variable,) + add((low, high, cross), exponent)] += coefficient
        matrix[row][column] = {key: value for key, value in changed.items() if value}


def shear(matrix, destination, source, coefficient):
    require(destination != source and coefficient in (-1, 1), "data shear")
    for column in range(8):
        changed = dict(matrix[destination][column])
        for key, value in matrix[source][column].items():
            changed[key] = changed.get(key, 0) + coefficient * value
        matrix[destination][column] = {key: value for key, value in changed.items() if value}


def local_event(matrix, event, local, q):
    stage = event["stage"]
    left, right = 2 * local["pair"], 2 * local["pair"] + 1
    for side, row in enumerate((left, right)):
        before = (scale(q, 1 - side) if stage == 0 else
                  add(((1 << (9 + 8 * (stage - 1))) - 1, 0, 0), scale(q, -side)))
        phase(matrix, row, scale(before, -1))
    if local["reverse"]:
        shear(matrix, left, right, -1)
    else:
        shear(matrix, right, left, 1)
    for side, row in enumerate((left, right)):
        phase(matrix, row, add(((1 << (9 + 8 * stage)) - 1, 0, 0), scale(q, -side)))


def data_event(matrix, event, recipe, locals_, seen):
    kind, q = event["kind"], axis(recipe["q"])
    if kind == "local_cover_sweep":
        local_event(matrix, event, locals_[event["stage"]], q)
    elif kind == "idle_cover_sweep":
        for side, child in enumerate(event["child_indices"]):
            require(child not in seen, "duplicate residual site")
            seen.add(child)
            entry = recipe["idle_children"][child]
            value = sum_axes([int(a) for a in entry["orthogonal_axes"]])
            value = add(value, scale(axis(entry["translation_after"]), 2))
            phase(matrix, 2 * event["pair"] + side, value, 1 << child)
    elif kind == "bridge":
        dst, src, coefficient = event["dst"], event["src"], event["coefficient"]
        shear(matrix, 2 * dst, 2 * src, coefficient)
        shear(matrix, 2 * src + 1, 2 * dst + 1, -coefficient)
    elif kind == "terminal_Y_translations":
        for pair in event["pairs"]:
            phase(matrix, 2 * pair + 1, scale(q, 2))
    elif kind == "terminal":
        for pair in range(event["pairs"]):
            matrix[2 * pair], matrix[2 * pair + 1] = matrix[2 * pair + 1], matrix[2 * pair]
            for column in range(8):
                matrix[2 * pair + 1][column] = {
                    key: -value for key, value in matrix[2 * pair + 1][column].items()}
    else:
        raise ValueError("unexpected data event: " + kind)


def replay(template, recipe):
    matrix = [[{(0, 0, 0, 0): 1} if i == j else {} for j in range(8)] for i in range(8)]
    locals_ = {item["stage"]: item for item in template["recipe"] if item["kind"] == "local"}
    require(set(locals_) == set(range(9)), "nine local stages")
    seen, peak = set(), 8
    events = template["execution_schedule"]
    require(len(events) <= 64, "event bound")
    for event in events:
        if event["kind"] in ("bank_padding_cover_sweep", "translate_every_live_family"):
            continue
        data_event(matrix, event, recipe, locals_, seen)
        peak = max(peak, sum(len(entry) for row in matrix for entry in row))
        require(peak <= 256, "symbolic term bound")
    require(seen == set(range(20)), "complete residual interface")
    for row in range(8):
        phase(matrix, row, scale(((1 << BITS) - 1, 0, 0), -1))
    types = {ZERO: 0, scale(axis(recipe["q"]), -1): -1}
    terms = []
    for row in range(8):
        for column in range(8):
            for (mask, low, high, cross), coefficient in matrix[row][column].items():
                value = low, high, cross
                require(value in types, "unexpected ambient phase")
                terms.append([row, column, mask, types[value], coefficient])
    return sorted(terms), peak
