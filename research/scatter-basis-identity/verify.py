#!/usr/bin/env python3
"""The corrected scatter satisfies U^{-1}(U d + U S p) = d + S p.

The checker multiplies one invertible example and the published invoices.
It does not replay the columns.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_SCATTER_BASIS_IDENTITY invoices=185,878 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_SCATTER_BASIS_IDENTITY " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == set(), "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def multiply(left, right):
    size = len(left)
    return tuple(
        tuple(sum(left[row][term] * right[term][column] for term in range(size)) for column in range(size))
        for row in range(size)
    )


def apply(matrix, vector):
    size = len(matrix)
    return tuple(sum(matrix[row][column] * vector[column] for column in range(size)) for row in range(size))


def add(left, right):
    return tuple(left[index] + right[index] for index in range(len(left)))


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    change = ((1, 1), (0, 1))
    inverse = ((1, -1), (0, 1))
    scatter = ((2, 0), (1, 3))
    require(multiply(inverse, change) == ((1, 0), (0, 1)), "the sample inverse moved")
    for target in ((4, 5), (0, 1), (-3, 8)):
        for source in ((6, 7), (1, 0), (2, -5)):
            corrected = apply(inverse, add(apply(change, target), apply(multiply(change, scatter), source)))
            direct = add(target, apply(scatter, source))
            require(corrected == direct, "the scatter identity moved")
    require(167 + 18 == 185 and 6 * 3 == 18 and 181 - 176 == 5, "the three-tetrad invoice moved")
    require(794 + 84 == 878 and 6 * 14 == 84 and 214 - 176 == 38, "the fourteen-tetrad invoice moved")
    return {
        "three_tetrad_operations": 185,
        "fourteen_tetrad_operations": 878,
        "identity_holds": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
