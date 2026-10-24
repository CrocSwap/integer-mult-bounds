#!/usr/bin/env python3
"""Rank-one idempotents in the three-bit matrix ring.

The checker enumerates these projectors. It does not search words.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_RANK_ONE_IDEMPOTENT_COUNT matrices=28 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_RANK_ONE_IDEMPOTENT_COUNT " + message)


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


def matrix(image, dual):
    return tuple(tuple((image >> row) & 1 & (dual >> column) & 1 for column in range(3)) for row in range(3))


def multiply(left, right):
    return tuple(
        tuple(sum(left[row][index] * right[index][column] for index in range(3)) % 2 for column in range(3))
        for row in range(3)
    )


def trace(grid):
    return sum(grid[index][index] for index in range(3)) % 2


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    idempotents = {}
    rejected = 0
    for image in range(1, 8):
        for dual in range(8):
            grid = matrix(image, dual)
            if dual == 0:
                require(grid == ((0, 0, 0), (0, 0, 0), (0, 0, 0)), "the zero dual was not zero")
                continue
            square = multiply(grid, grid)
            if dot(dual, image) == 1:
                require(square == grid and trace(grid) == 1, "a trace-one product was not idempotent")
                require(grid not in idempotents, "two pairs gave the same matrix")
                idempotents[grid] = (image, dual)
            else:
                require(square != grid and trace(grid) == 0, "a trace-zero product was idempotent")
                rejected += 1
    require(len(idempotents) == 28 and rejected == 21, "the projector count moved")
    require(len({image for image, _ in idempotents.values()}) == 7, "an image vector was missed")
    return {"matrices": 28, "trace_zero_rank_one": 21, "image_vectors": 7, "no_new_kappa": True}


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
