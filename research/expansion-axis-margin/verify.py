"""Margin between two expansion axes and the chirp input cap.

One axis of norm below 3/4 does not fit an input cap of 3/5. The product
of two such bounds is 9/16, and 3/5 - 9/16 = 3/80 exactly.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
ONE = Fraction(3, 4)
CAP = Fraction(3, 5)
GRID = 400


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_EXPANSION_AXIS_MARGIN selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def main() -> None:
    pinned = load()
    square = ONE * ONE
    gap = CAP - square
    if square != Fraction(9, 16) or gap != Fraction(3, 80) or ONE <= CAP:
        raise SystemExit("FAIL_EXPANSION_AXIS_MARGIN margin moved")
    if square + gap != CAP:
        raise SystemExit("FAIL_EXPANSION_AXIS_MARGIN closure moved")
    sums = 0
    for left in range(GRID):
        x = Fraction(left, GRID)
        if x >= ONE:
            continue
        for right in range(GRID):
            y = Fraction(right, GRID)
            if y >= ONE:
                continue
            product = x * y
            if product >= square:
                raise SystemExit("FAIL_EXPANSION_AXIS_MARGIN product moved")
            for step in range(3):
                if product + Fraction(step, 80) >= CAP:
                    raise SystemExit("FAIL_EXPANSION_AXIS_MARGIN sum moved")
                sums += 1
    if pinned["sums"] != sums or pinned["no_new_kappa"] is not True:
        raise SystemExit("FAIL_EXPANSION_AXIS_MARGIN pinned result moved")
    print(f"PASS_EXPANSION_AXIS_MARGIN sums={sums} no_new_kappa")


if __name__ == "__main__":
    main()
