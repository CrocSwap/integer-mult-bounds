"""Erasure of one unweighted tensor kernel on the P-grid.

For an integer a >= 26 the family p=2^(10a), m=2^(4a), X=2^(3a), d=u=m,
D=d-1, P=32768p, w=4X+2 and k=X/2048 meets the scalar band conditions.
The unweighted coefficient exponent exceeds P, so toward-zero rounding
on the P-grid is zero. The weighted exponent is strictly below p/8.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
FIRST = 26
LAST = 64


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_KERNEL_GRID_ERASURE selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def family(scale: int) -> tuple[int, int, int, int, int, int, int]:
    precision = 1 << (10 * scale)
    width = 1 << (4 * scale)
    box = 1 << (3 * scale)
    spacing = width
    degree = spacing - 1
    places = 32768 * precision
    band = 4 * box + 2
    step = box // 2048
    return precision, width, box, degree, places, band, step


def main() -> None:
    pinned = load()
    cap = Fraction(8 + Fraction(1, 2048) + Fraction(7, 128), 128) + Fraction(1, 128 * 128)
    if cap >= Fraction(1, 8):
        raise SystemExit("FAIL_KERNEL_GRID_ERASURE cap moved")
    base_precision, base_width, base_box, _, _, _, _ = family(FIRST)
    base_lower = Fraction(3 * (1 << FIRST), 4096) - Fraction(1, 2 * base_box * base_box)
    if base_lower <= 32768 or base_width * base_width * base_width * base_width * base_width != base_precision * base_precision:
        raise SystemExit("FAIL_KERNEL_GRID_ERASURE base comparison moved")
    rows = 0
    previous = base_lower
    for scale in range(FIRST, LAST + 1):
        precision, width, box, degree, places, band, step = family(scale)
        if box % 2048 or width * width > precision:
            raise SystemExit("FAIL_KERNEL_GRID_ERASURE scale moved")
        if width < (8 * precision - 1).bit_length():
            raise SystemExit("FAIL_KERNEL_GRID_ERASURE logarithm moved")
        if (band - 2) * (band - 2) * width != 16 * precision:
            raise SystemExit("FAIL_KERNEL_GRID_ERASURE band identity moved")
        if width - 2 <= 2 * band + step + 3:
            raise SystemExit("FAIL_KERNEL_GRID_ERASURE cell inequality moved")
        zero_exponent = degree * (3 * width * step - 1)
        weighted_exponent = 16 * degree * step * (2 * band + step + 3) + degree + 1
        lower = Fraction(3 * (1 << scale), 4096) - Fraction(1, 2 * box * box)
        if scale > FIRST and lower <= 2 * previous:
            raise SystemExit("FAIL_KERNEL_GRID_ERASURE doubling moved")
        previous = lower
        if zero_exponent <= places or Fraction(zero_exponent, precision) < lower:
            raise SystemExit("FAIL_KERNEL_GRID_ERASURE zero exponent moved")
        if Fraction(weighted_exponent, precision) >= cap or 8 * weighted_exponent >= precision:
            raise SystemExit("FAIL_KERNEL_GRID_ERASURE weighted exponent moved")
        rows += 1
    if pinned["rows"] != rows or pinned["no_new_kappa"] is not True:
        raise SystemExit("FAIL_KERNEL_GRID_ERASURE pinned result moved")
    print(f"PASS_KERNEL_GRID_ERASURE rows={rows} no_new_kappa")


if __name__ == "__main__":
    main()
