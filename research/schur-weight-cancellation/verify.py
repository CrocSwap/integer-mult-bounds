"""Diagonal weights in a Schur correction.

If A = D G D^{-1} with D diagonal, the interior Schur correction between two
boundary indices is (a_b / a_c) times the same correction formed from G.
The interior diagonal entries cancel.
"""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
ENTRIES = (-1, 0, 1)
SCALES = (1, 2, 3)


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_SCHUR_WEIGHT_CANCELLATION selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]] | None:
    first, second = matrix
    determinant = first[0] * second[1] - first[1] * second[0]
    if determinant == 0:
        return None
    return [
        [second[1] / determinant, -first[1] / determinant],
        [-second[0] / determinant, first[0] / determinant],
    ]


def main() -> None:
    pinned = load()
    checked = 0
    for raw in product(ENTRIES, repeat=4):
        bare = [
            [Fraction(raw[0]), Fraction(raw[1])],
            [Fraction(raw[2]), Fraction(raw[3])],
        ]
        bare_inverse = inverse(bare)
        if bare_inverse is None:
            continue
        for left in product(ENTRIES, repeat=2):
            left_row = (Fraction(left[0]), Fraction(left[1]))
            mixed = (
                left_row[0] * bare_inverse[0][0] + left_row[1] * bare_inverse[1][0],
                left_row[0] * bare_inverse[0][1] + left_row[1] * bare_inverse[1][1],
            )
            for right in product(ENTRIES, repeat=2):
                bare_correction = mixed[0] * right[0] + mixed[1] * right[1]
                for boundary_left, boundary_right, interior_left, interior_right in product(SCALES, repeat=4):
                    weighted = [
                        [
                            Fraction(interior_left, interior_left) * bare[0][0],
                            Fraction(interior_left, interior_right) * bare[0][1],
                        ],
                        [
                            Fraction(interior_right, interior_left) * bare[1][0],
                            Fraction(interior_right, interior_right) * bare[1][1],
                        ],
                    ]
                    weighted_inverse = inverse(weighted)
                    if weighted_inverse is None:
                        raise SystemExit("FAIL_SCHUR_WEIGHT_CANCELLATION interior became singular")
                    row = (
                        Fraction(boundary_left, interior_left) * left_row[0],
                        Fraction(boundary_left, interior_right) * left_row[1],
                    )
                    column = (
                        Fraction(interior_left, boundary_right) * right[0],
                        Fraction(interior_right, boundary_right) * right[1],
                    )
                    middle = (
                        row[0] * weighted_inverse[0][0] + row[1] * weighted_inverse[1][0],
                        row[0] * weighted_inverse[0][1] + row[1] * weighted_inverse[1][1],
                    )
                    correction = middle[0] * column[0] + middle[1] * column[1]
                    expected = Fraction(boundary_left, boundary_right) * bare_correction
                    if correction != expected:
                        raise SystemExit("FAIL_SCHUR_WEIGHT_CANCELLATION weight moved")
                    checked += 1
    if (
        pinned["interior_checks"] != checked
        or pinned["scales"] != len(SCALES)
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_SCHUR_WEIGHT_CANCELLATION pinned result moved")
    print(f"PASS_SCHUR_WEIGHT_CANCELLATION checks={checked} no_new_kappa")


if __name__ == "__main__":
    main()
