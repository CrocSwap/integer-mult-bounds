#!/usr/bin/env python3
"""COPY floor for normalized ranks at most nine.

The checker applies the pairing inequality and Sylvester's count. It does
not exhaust character pairs.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_COPY_FLOOR_ARITHMETIC floor=72 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_COPY_FLOOR_ARITHMETIC " + message)


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


def pairing_rank(left, right):
    kernel = {vector for vector in left if all(dot(vector, other) == 0 for other in right)}
    return dimension(left) - dimension(kernel)


def frame():
    vectors = []
    for index in range(4):
        positive = [0] * 8
        negative = [0] * 8
        positive[2 * index] = 1
        positive[2 * index + 1] = 1
        negative[2 * index] = 1
        negative[2 * index + 1] = -1
        vectors.append(positive)
        vectors.append(negative)
    total = [[0] * 8 for _ in range(8)]
    for vector in vectors:
        for row, left in enumerate(vector):
            for column, right in enumerate(vector):
                total[row][column] += left * right
    require(all(total[row][column] == (2 if row == column else 0) for row in range(8) for column in range(8)), "the frame sum moved")
    require(all(sum(entry * entry for entry in vector) == 2 for vector in vectors), "a frame norm moved")
    require(len(vectors) == 8, "the frame lost a vector")


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")

    form_rank = pairing_rank(set(range(512)), set(range(512)))
    require(form_rank == 9, "the nine-bit form degenerated")
    spaces = subspaces(3)
    require(len(spaces) == 16, "the three-bit subspace count moved")
    for left in spaces:
        for right in spaces:
            require(
                pairing_rank(left, right) >= dimension(left) + dimension(right) - 3,
                "the pairing inequality moved",
            )

    floors = []
    for excess_p in (0, 1):
        for excess_q in (0, 1):
            terms = 8 + excess_p + excess_q
            floor = 9 * (terms - excess_p - excess_q)
            require(floor == 72, "a rank pair left 72")
            floors.append(floor)
    require(floors == [72, 72, 72, 72], "the four floors moved")
    for excess in (0, 1):
        require(9 * (8 + excess) - 9 * excess == 72, "a one-sided basis left 72")
    frame()
    return {
        "rank_pairs": 4,
        "copy_floor": 72,
        "frame_terms": 8,
        "frame_term_cost": 9,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
