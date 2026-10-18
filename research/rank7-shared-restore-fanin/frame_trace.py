# SPDX-License-Identifier: Apache-2.0
"""Separate set-of-vectors frame census for the four registers touched by R2."""

from collections import Counter
from functools import lru_cache

from rewrite import need

REGISTERS = (18, 22, 40, 54)


@lru_cache(maxsize=128)
def span(vectors):
    need(
        len(vectors) <= 9 and all(type(x) is int and 0 < x < 512 for x in vectors),
        "nine-dimensional binary frame",
    )
    result = frozenset({0})
    for vector in vectors:
        result = result | frozenset(x ^ vector for x in result)
    return result


def dimension(space):
    size = len(space)
    need(size > 0 and size & (size - 1) == 0, "subspace cardinality")
    return size.bit_length() - 1


def step(gate, current, paid):
    if gate[0] == "warp":
        register = gate[1]
        if register in current:
            need(current[register] == span(tuple(gate[3])), "warp entry")
            current[register] = span(tuple(gate[4]))
        return
    registers = gate[1:3] if gate[0] == "add" else gate[1:2]
    for register in registers:
        if register in current:
            space = span(tuple(gate[-1]))
            need(current[register] <= space, "monotone four-register frame")
            delta = dimension(space) - dimension(current[register])
            if delta:
                paid[delta] += 1
            current[register] = space


def census(word):
    need(not set(REGISTERS) & set(word["centers"]), "no omitted centre-path charge")
    need(
        len(word["A"]) <= 4100
        and len(word["B"]) <= 1900
        and len(word["restore"]) <= 204
        and len(word["warps"]) <= 72,
        "fixed-word bounds",
    )
    current = {r: span((word["ports"][r],)) for r in REGISTERS}
    paid = Counter()
    for gate in word["A"]:
        step(gate, current, paid)
    warps = {}
    for record in word["warps"]:
        warps.setdefault(record[0], []).append(record)
    for index in range(len(word["B"]) + 1):
        for record in warps.get(index, []):
            step(["warp", record[1], None, record[3], record[4]], current, paid)
        if index < len(word["B"]):
            step(word["B"][index], current, paid)
    before = {str(r): dimension(current[r]) for r in REGISTERS}
    for gate in word["restore"]:
        step(gate, current, paid)
    full = span(tuple(1 << i for i in range(9)))
    for register in REGISTERS:
        delta = 9 - dimension(current[register])
        if delta:
            paid[delta] += 1
        current[register] = full
    return {str(rank): count for rank, count in sorted(paid.items())}, before
