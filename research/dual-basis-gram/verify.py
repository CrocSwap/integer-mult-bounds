#!/usr/bin/env python3
"""Gram identity of the stated rank-(9,9) dual basis.

The checker multiplies the eight primal vectors by the eight dual vectors.
It does not enumerate roots or character pairs.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_DUAL_BASIS_GRAM pairs=64 total=72 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
COSTS = (1, 7, 9, 9, 9, 9, 9, 9, 9, 1)


def fail(message):
    raise SystemExit("FAIL_DUAL_BASIS_GRAM " + message)


def require(condition, message):
    if not condition:
        fail(message)


def basis(index):
    vector = [0] * 8
    vector[index] = 1
    return vector


def add(left, right):
    return [item + other for item, other in zip(left, right)]


def scale(factor, vector):
    return [factor * item for item in vector]


def dot(left, right):
    return sum(item * other for item, other in zip(left, right))


def frames():
    unit = [basis(index) for index in range(8)]
    primal_head = add(unit[0], unit[1])
    dual_head = add(unit[0], unit[2])
    primal = [
        primal_head,
        unit[1],
        add(unit[0], scale(-1, unit[2])),
        *unit[3:],
    ]
    dual = [
        dual_head,
        add(add(scale(-1, unit[0]), unit[1]), scale(-1, unit[2])),
        scale(-1, unit[2]),
        *unit[3:],
    ]
    return primal_head, dual_head, primal, dual


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    head, dual_head, primal, dual = frames()
    require(dot(head, dual_head) == 1, "v and w are not dual")
    pairs = 0
    for row, left in enumerate(primal):
        for column, right in enumerate(dual):
            pairs += 1
            require(dot(left, right) == (1 if row == column else 0), f"entry {row},{column}")
    require(pairs == 64, "pair count")
    require(sum(COSTS) == 72, "stated total")
    require(len(COSTS) == 10, "term count")
    require(receipt["gram_pairs"] == 64, "receipt pairs")
    require(receipt["dot_vw"] == 1, "receipt dot")
    require(receipt["stated_costs"] == list(COSTS), "receipt costs")
    require(receipt["stated_total"] == 72, "receipt total")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
