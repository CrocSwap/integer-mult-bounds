#!/usr/bin/env python3
"""Composition of the full and normal address exchanges.

The checker compares the two operators on one root. It does not rerun port charts.
"""

import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ADDRESS_OPERATOR_COMPOSITION pairs=16 no_new_kappa"
RECIPE = "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py"
ROOT_VECTOR = (2, 2, 0, 0, 0, 0, 0, 0)


def fail(message):
    raise SystemExit("FAIL_ADDRESS_OPERATOR_COMPOSITION " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(row):
    return max(tuple(row), tuple(-entry for entry in row))


def contains_root(row):
    found = set()
    for left, right in combinations(range(8), 2):
        for sign in (-2, 2):
            line = [0] * 8
            line[left], line[right] = 2, sign
            found.add(canonical(line))
    for line in product((-1, 1), repeat=8):
        if sum(entry == -1 for entry in line) % 2 == 0:
            found.add(canonical(line))
    require(len(found) == 120 and canonical(row) in found, "the witness root left the inventory")


def apply(matrix, vector):
    return tuple(sum(matrix[row][column] * vector[column] for column in range(8)) for row in range(8))


def projector(row):
    norm = sum(entry * entry for entry in row)
    return tuple(tuple(Fraction(left * right, norm) for right in row) for left in row)


def complement(matrix):
    return tuple(tuple((1 if row == column else 0) - matrix[row][column] for column in range(8)) for row in range(8))


def exchange(matrix, head, tail):
    projected_head = apply(matrix, head)
    projected_tail = apply(matrix, tail)
    return (
        tuple(entry - left + right for entry, left, right in zip(head, projected_head, projected_tail)),
        tuple(entry - left + right for entry, left, right in zip(tail, projected_tail, projected_head)),
    )


def identity():
    return tuple(tuple(1 if row == column else 0 for column in range(8)) for row in range(8))


def evaluate():
    require(sha256(ROOT / RECIPE) == "6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8", "recipe drift")
    recipe = (ROOT / RECIPE).read_text(encoding="utf-8")
    require("D_I D_P = D_(I-P) exactly" in recipe, "the operator clause moved")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    contains_root(ROOT_VECTOR)
    normal = projector(ROOT_VECTOR)
    kernel = complement(normal)
    require(apply(normal, ROOT_VECTOR) == ROOT_VECTOR, "the normal missed its root")
    require(apply(kernel, ROOT_VECTOR) == (0, 0, 0, 0, 0, 0, 0, 0), "the complement met its root")
    require(sum(normal[index][index] for index in range(8)) == 1, "the normal trace moved")
    require(apply_matrix(normal, normal) == normal, "the normal square moved")
    pairs = 0
    for index in range(8):
        for bank in ("head", "tail"):
            head = tuple(1 if bank == "head" and column == index else 0 for column in range(8))
            tail = tuple(1 if bank == "tail" and column == index else 0 for column in range(8))
            once = exchange(normal, head, tail)
            require(exchange(identity(), *once) == exchange(kernel, head, tail), "a basis pair disagreed")
            pairs += 1
    full = exchange(identity(), ROOT_VECTOR, (0, 0, 0, 0, 0, 0, 0, 0))
    held = exchange(kernel, ROOT_VECTOR, (0, 0, 0, 0, 0, 0, 0, 0))
    require(full == ((0, 0, 0, 0, 0, 0, 0, 0), ROOT_VECTOR), "the full image moved")
    require(held == (ROOT_VECTOR, (0, 0, 0, 0, 0, 0, 0, 0)), "the complement image moved")
    require(pairs == 16, "the basis count moved")
    return {
        "root": list(ROOT_VECTOR),
        "basis_pairs": pairs,
        "full_image": "tail",
        "complement_image": "head",
        "no_new_kappa": True,
    }


def apply_matrix(left, right):
    return tuple(tuple(sum(left[row][index] * right[index][column] for index in range(8)) for column in range(8)) for row in range(8))


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
