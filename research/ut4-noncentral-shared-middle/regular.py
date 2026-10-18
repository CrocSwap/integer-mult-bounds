#!/usr/bin/env python3
"""Literal UT4 matrices and faithful dirty-column replay; Apache-2.0.

Written with substantial OpenAI Codex assistance. No primary-verifier imports.
"""
from itertools import product


def multiply(a, b):
    """Multiply binary matrices represented by integer row bitsets."""
    result = []
    for row in a:
        value = 0
        for k, right in enumerate(b):
            if row & (1 << k):
                value ^= right
        result.append(value)
    return tuple(result)


def transpose(a):
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(a))
                 for j in range(len(a)))


def inverse(a):
    n = len(a)
    rows = [row | (1 << (n + i)) for i, row in enumerate(a)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i] & (1 << j)), None)
        if pivot is None:
            raise ValueError("singular matrix")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(n):
            if i != j and rows[i] & (1 << j):
                rows[i] ^= rows[j]
    return tuple(row >> n for row in rows)


IDENTITY = (1, 2, 4, 8)
POSITIONS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
# Build the group from literal entries, not the primary six-bit product formula.
GROUP = []
for number in range(64):
    rows = list(IDENTITY)
    for bit, (i, j) in enumerate(POSITIONS):
        if number & (1 << bit):
            rows[i] ^= 1 << j
    GROUP.append(tuple(rows))
GROUP = tuple(GROUP)
INDEX = {g: i for i, g in enumerate(GROUP)}
LEFT = tuple(tuple(INDEX[multiply(g, h)] for h in GROUP) for g in GROUP)
GENERATORS = {"x": (3, 2, 4, 8), "y": (1, 6, 4, 8), "z": (1, 2, 12, 8)}


def left_translate(g, support):
    result = 0
    while support:
        low = support & -support
        result ^= 1 << LEFT[g][low.bit_length() - 1]
        support ^= low
    return result


def replay(word, registers):
    """Return every faithful regular column, for all 64*r dirty basis inputs.

    A word is in left-to-right matrix order; apply rightmost factor first.
    Each tuple is (label, binary left vector, binary right vector).
    """
    columns = []
    for source, address in product(range(registers), range(64)):
        state = [0] * registers
        state[source] = 1 << address
        for label, left, right in reversed(word):
            g = INDEX[GENERATORS[label]]
            value = 0
            for j in range(registers):
                if right & (1 << j):
                    value ^= state[j]
            delta = left_translate(g, value) ^ value
            for i in range(registers):
                if left & (1 << i):
                    state[i] ^= delta
        columns.append(sum(block << (64 * i) for i, block in enumerate(state)))
    return tuple(columns)


def represented(formal, dual=False):
    """Map a formal matrix to natural/contragredient address blocks."""
    r = len(formal)
    result = [0] * (4 * r)
    for i in range(r):
        for j in range(r):
            mask = formal[i][j]
            while mask:
                low = mask & -mask
                address = GROUP[low.bit_length() - 1]
                if dual:
                    address = transpose(inverse(address))
                for a, row in enumerate(address):
                    for b in range(4):
                        if row & (1 << b):
                            result[a * r + i] ^= 1 << (b * r + j)
                mask ^= low
    return tuple(result)
