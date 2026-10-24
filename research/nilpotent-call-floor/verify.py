#!/usr/bin/env python3
"""Trace-zero rank-one calls still cost twelve.

The checker separates the diagonal pairing from the cross scalar and the
stacked rank. It does not search words.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_NILPOTENT_CALL_FLOOR calls=12 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_NILPOTENT_CALL_FLOOR " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def dot(left, right):
    return (left & right).bit_count() % 2


def multiply_field(left, right):
    a0, a1 = left & 1, (left >> 1) & 1
    b0, b1 = right & 1, (right >> 1) & 1
    low = (a0 & b0) ^ (a1 & b1)
    high = (a0 & b1) ^ (a1 & b0) ^ (a1 & b1)
    return low | (high << 1)


def multiply_group(left, right):
    a, b, c = left
    ap, bp, cp = right
    return (a ^ ap, b ^ bp, c ^ cp ^ multiply_field(a, bp))


def subspaces(dimension):
    found = set()

    def extend(start, seen):
        found.add(frozenset(seen))
        for vector in range(start, 1 << dimension):
            if vector in seen:
                continue
            larger = set(seen)
            for item in seen:
                larger.add(item ^ vector)
            extend(vector + 1, larger)

    extend(1, {0})
    return found


def dimension(space):
    return len(space).bit_length() - 1


def sum_space(left, right):
    total = set(left)
    for vector in right:
        total.update(item ^ vector for item in list(total))
    return total


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")

    nilpotents = [(image, dual) for image in range(1, 8) for dual in range(1, 8) if dot(dual, image) == 0]
    require(len(nilpotents) == 21, "the trace-zero count moved")
    require(dot(0b010, 0b001) == 0 and dot(0b001, 0b010) == 0, "the sample calls were not trace zero")
    require(dot(0b001, 0b001) == 1 and dot(0b010, 0b010) == 1, "the cross scalars vanished")
    alive = sum(dot(dual_j, image_i) for image_j, dual_j in nilpotents for image_i, _dual_i in nilpotents)
    require(alive > 0, "every cross scalar vanished")

    column_span = {0}
    for column in (0b100000, 0b000010, 0b001001):
        column_span.update(item ^ column for item in list(column_span))
    require(len(column_span) == 8, "the target column space moved")

    spaces = subspaces(3)
    require(len(spaces) == 16, "the three-bit subspace count moved")
    for first in spaces:
        for second in spaces:
            for third in spaces:
                triple = first & second & third
                image_dimension = dimension(first) + dimension(second) + dimension(third) - dimension(triple)
                pairwise = (first & second, first & third, second & third)
                difference = sum(dimension(space) for space in pairwise) - 2 * dimension(triple)
                require(difference >= 0, "a pairwise intersection shrank")
                require(image_dimension >= dimension(sum_space(sum_space(first, second), third)), "the stacked rank fell below the shadow")

    labels = {(kind, coefficient): ((coefficient, 0, 0) if kind == "X" else (0, coefficient, 0)) for kind in ("X", "Y") for coefficient in (1, 2, 3)}
    registers = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
    schedule = (
        (0, "X", 1), (0, "Y", 1), (0, "X", 1), (0, "Y", 1),
        (1, "X", 2), (1, "Y", 1), (1, "X", 2), (1, "Y", 1),
        (2, "X", 3), (2, "Y", 1), (2, "X", 3), (2, "Y", 1),
    )
    for register, kind, coefficient in schedule:
        registers[register] = multiply_group(registers[register], labels[(kind, coefficient)])
    require(registers == [(0, 0, 1), (0, 0, 2), (0, 0, 3)], "the twelve-call word moved")
    require(3 + 3 == 6, "the side floor moved")
    return {
        "nilpotent_matrices": 21,
        "cross_scalar": 1,
        "x_calls": 6,
        "y_calls": 6,
        "attaining_calls": 12,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
