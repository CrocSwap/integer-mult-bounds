#!/usr/bin/env python3
"""Twelve-call and fourteen-call realizations of the central triple.

The checker multiplies these words. It does not search shorter words.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_TWELVE_CALL_CENTRAL_TRIPLE calls=12,14 no_new_kappa"
IDENTITY = (0, 0, 0)
X1, XW = (1, 0, 0), (2, 0, 0)
Y1, YW = (0, 1, 0), (0, 2, 0)
Z1, ZW, ZW2 = (0, 0, 1), (0, 0, 2), (0, 0, 3)


def fail(message):
    raise SystemExit("FAIL_TWELVE_CALL_CENTRAL_TRIPLE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def add(left, right):
    return left ^ right


def multiply_scalar(left, right):
    low = (left & 1) & (right & 1)
    low ^= ((left >> 1) & 1) & ((right >> 1) & 1)
    high = (left & 1) & ((right >> 1) & 1)
    high ^= ((left >> 1) & 1) & (right & 1)
    high ^= ((left >> 1) & 1) & ((right >> 1) & 1)
    return low | (high << 1)


def multiply(left, right):
    return (
        add(left[0], right[0]),
        add(left[1], right[1]),
        add(add(left[2], right[2]), multiply_scalar(left[0], right[1])),
    )


def elements():
    return tuple((a, b, c) for a in range(4) for b in range(4) for c in range(4))


def product(labels):
    value = IDENTITY
    for label in labels:
        value = multiply(label, value)
    return value


def apply_word(calls, width, registers):
    state = list(registers)
    for label, coordinate in calls:
        state = [
            frozenset(multiply(label, element) for element in state[index]) if index == coordinate else state[index]
            for index in range(width)
        ]
    return tuple(state)


def realizes(schedule, width, targets):
    calls = [(label, coordinate) for coordinate, labels in schedule for label in labels]
    for element in elements():
        for register, target in enumerate(targets):
            start = [frozenset() for _ in range(width)]
            start[register] = frozenset((element,))
            expected = [frozenset() for _ in range(width)]
            expected[register] = frozenset((multiply(target, element),))
            if apply_word(calls, width, start) != tuple(expected):
                return False
    return True


def nilpotent(kind, coefficient):
    matrix = [[0] * 6 for _ in range(6)]
    block = ((1, 0), (0, 1)) if coefficient == 1 else ((0, 1), (1, 1))
    row0, column0 = (0, 2) if kind == "X" else (2, 4)
    for row in range(2):
        for column in range(2):
            matrix[row0 + row][column0 + column] = block[row][column]
    return matrix


def matmul(left, right):
    return tuple(
        tuple(sum(left[row][index] * right[index][column] for index in range(6)) % 2 for column in range(6))
        for row in range(6)
    )


def zero(matrix):
    return all(entry == 0 for row in matrix for entry in row)


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    group = elements()
    require(len(group) == 64, "the group order moved")
    for left in group:
        require(multiply(left, IDENTITY) == left and multiply(IDENTITY, left) == left, "the identity moved")
        inverse = (left[0], left[1], add(left[2], multiply_scalar(left[0], left[1])))
        require(multiply(left, inverse) == IDENTITY, "an inverse moved")
        for middle in group:
            for right in group:
                require(multiply(multiply(left, middle), right) == multiply(left, multiply(middle, right)), "associativity moved")
    for label in (X1, XW, Y1, YW):
        require(multiply(label, label) == IDENTITY, "a label was not an involution")
    require(product((X1, Y1, X1, Y1)) == Z1, "the first commutator moved")
    require(product((X1, YW, X1, YW)) == ZW, "the second commutator moved")
    require(product((XW, YW, XW, YW)) == ZW2, "the third commutator moved")
    require(product((X1, XW, Y1, X1, XW, Y1)) == ZW2, "the six-call composite moved")
    require(multiply(Z1, ZW) == ZW2, "the central product moved")
    labels = (("X", 1), ("X", 2), ("Y", 1), ("Y", 2))
    blocks = {key: nilpotent(*key) for key in labels}
    for later in labels:
        for earlier in labels:
            product_matrix = matmul(blocks[later], blocks[earlier])
            if later[0] == "X" and earlier[0] == "Y":
                require(not zero(product_matrix), "an X-then-Y corner vanished")
            else:
                require(zero(product_matrix), "a nilpotent product moved")
    short = (
        (0, (X1, Y1, X1, Y1)),
        (1, (X1, YW, X1, YW)),
        (2, (XW, YW, XW, YW)),
    )
    long = (
        (0, (X1, Y1, X1, Y1)),
        (1, (XW, Y1, XW, Y1)),
        (2, (X1, XW, Y1, X1, XW, Y1)),
    )
    require(realizes(short, 3, (Z1, ZW, ZW2)), "the twelve-call word moved")
    require(realizes(short, 4, (Z1, ZW, ZW2, IDENTITY)), "the spectator moved")
    require(realizes(long, 3, (Z1, ZW, ZW2)), "the fourteen-call word moved")
    short_calls = [label for _, labels in short for label in labels]
    require(sum(label in (X1, XW) for label in short_calls) == 6, "the X count moved")
    require(sum(label in (Y1, YW) for label in short_calls) == 6, "the Y count moved")
    require(len(short_calls) == 12 and sum(len(labels) for _, labels in long) == 14, "a length moved")
    return {
        "group_order": 64,
        "twelve_call_word": 12,
        "fourteen_call_word": 14,
        "x_calls": 6,
        "y_calls": 6,
        "spectator_registers": 1,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
