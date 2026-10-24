#!/usr/bin/env python3
"""Hyperplanes through the 7-dimensional subspaces of F_2^9.

The checker enumerates those subspaces. It does not rerun a fresh-extraction search.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_RANK7_HYPERPLANE_COUNT subspaces=43435 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
AMBIENT = 9
SPACE = 1 << AMBIENT


def fail(message):
    raise SystemExit("FAIL_RANK7_HYPERPLANE_COUNT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def dot(left, right):
    return (left & right).bit_count() & 1


def subspaces():
    for first in range(1, SPACE):
        for second in range(first + 1, SPACE):
            third = first ^ second
            if first < second < third:
                yield first, second, third


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    require((SPACE - 1) * (SPACE - 2) // 6 == 43435, "the Gaussian count moved")
    found = 0
    incidence = [0] * SPACE
    for first, second, third in subspaces():
        span = {0}
        basis = []
        size = 0
        for point in range(SPACE):
            if dot(point, first) or dot(point, second):
                continue
            size += 1
            if point not in span:
                span = span | {item ^ point for item in span}
                basis.append(point)
        require(size == 128 and len(basis) == 7, "a subspace left dimension 7")
        annihilator = 0
        for normal in range(SPACE):
            if all(dot(normal, vector) == 0 for vector in basis):
                annihilator += 1
        require(annihilator == 4, "an annihilator left four vectors")
        incidence[first] += 1
        incidence[second] += 1
        incidence[third] += 1
        found += 1
    require(found == 43435, "the subspace count moved")
    require(all(incidence[normal] == 255 for normal in range(1, SPACE)), "a hyperplane left 255 subspaces")
    require(incidence[0] == 0, "the zero normal was counted")
    require(found * 3 == (SPACE - 1) * 255, "the incidence identity moved")
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(receipt["ambient_dimension"] == AMBIENT, "receipt dimension")
    require(receipt["subspaces"] == found, "receipt subspaces")
    require(receipt["hyperplanes_per_subspace"] == 3, "receipt hyperplanes")
    require(receipt["subspaces_per_hyperplane"] == 255, "receipt incidence")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
