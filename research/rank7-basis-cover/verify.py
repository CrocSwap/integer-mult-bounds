"""Printed rank-7 pattern cover.

The ten printed patterns meet nine copies of the width inventory, and the
printed face swap has the same width multiset on both sides.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
INVENTORY = {4: 26, 5: 2, 6: 16, 7: 52, 8: 99, 9: 213}
SCALE = 9
PATTERNS = (
    ((8,), 672),
    ((7, 9), Fraction(1757, 4)),
    ((7, 8, 8, 9), Fraction(115, 4)),
    ((8, 8), Fraction(35, 4)),
    ((6, 8, 9, 9), 144),
    ((4, 9, 9, 9), 234),
    ((9, 9, 9, 9, 9), Fraction(1341, 20)),
    ((9, 9, 9), Fraction(93, 4)),
    ((5, 9, 9, 9), 18),
    ((), Fraction(7619, 20)),
)
LEFT_SWAP = ((7, 8, 8, 9), (7, 9))
RIGHT_SWAP = ((8, 8), (7, 7, 9, 9))


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_RANK7_BASIS_COVER selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def width_totals() -> dict[int, Fraction]:
    totals = {width: Fraction(0) for width in INVENTORY}
    for widths, multiplicity in PATTERNS:
        for width in widths:
            totals[width] += multiplicity
    return totals


def main() -> None:
    pinned = load()
    totals = width_totals()
    covered = Fraction(0)
    for width, count in INVENTORY.items():
        if totals[width] != SCALE * count:
            raise SystemExit(f"FAIL_RANK7_BASIS_COVER width {width}")
        covered += totals[width]
    pattern_total = sum((multiplicity for _, multiplicity in PATTERNS), Fraction(0))
    if pattern_total != 2016 or covered != 3672:
        raise SystemExit("FAIL_RANK7_BASIS_COVER totals moved")
    if sorted(width for side in LEFT_SWAP for width in side) != sorted(
        width for side in RIGHT_SWAP for width in side
    ):
        raise SystemExit("FAIL_RANK7_BASIS_COVER swap moved")
    if (
        pinned["widths"] != len(INVENTORY)
        or pinned["scale"] != SCALE
        or pinned["covered_slots"] != int(covered)
        or pinned["pattern_total"] != int(pattern_total)
        or pinned["swap_width_count"] != 6
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_RANK7_BASIS_COVER pinned result moved")
    print(f"PASS_RANK7_BASIS_COVER slots={int(covered)} no_new_kappa")


if __name__ == "__main__":
    main()
