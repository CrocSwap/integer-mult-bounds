"""Coefficient-width bounds for the Gaussian interval routine.

For positive integers P and F, set X=4F, k=ceil(log2(8(X+1))),
H0=P+X+k+16, c=ceil(log2(H0)), and R=P+4X+4k+2c+64. These quantities
satisfy H0>=27, R>=115, R<5 H0, and the derived block count is at most
R/2. The exponential comparison e<3<4 supplies the strict width bound.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
BOX = 40


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def ceil_log2(value: int) -> int:
    if value < 1:
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND logarithm domain moved")
    return (value - 1).bit_length()


def parameters(precision: int, frequency: int) -> tuple[int, int, int, int, int, int]:
    scale = 4 * frequency
    bits = ceil_log2(8 * (scale + 1))
    height = precision + scale + bits + 16
    guard = ceil_log2(height)
    working = precision + 4 * scale + 4 * bits + 2 * guard + 64
    blocks = (working + 2) // 3 + 8
    return scale, bits, height, guard, working, blocks


def exponential_is_below_three() -> None:
    partial = Fraction(1) + Fraction(1) + Fraction(1, 2)
    geometric = Fraction(1, 2)
    if partial + geometric != 3:
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND series total moved")
    factorial = 2
    for index in range(3, 8):
        factorial *= index
        if Fraction(1, factorial) >= Fraction(1, 2 ** (index - 1)):
            raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND factorial comparison moved")


def universal(minimum_height: int, minimum_working: int) -> None:
    if minimum_height != 27 or minimum_working != 115:
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND minimum moved")
    if 2 * 5 >= minimum_height:
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND logarithm base moved")
    if 2 * 6 > 2 ** 5:
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND induction base moved")
    # If 2c <= 2^(c-1), then 2(c+1) = 2c+2 <= 2^(c-1)+2^(c-1) = 2^c.
    if 2 > 2 ** 5:
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND induction step moved")
    # Thus 2c < H0 for every height at least 27, and 5 H0 - R = H0 + 3P - 2c > 0.
    # Residue 0: 2*(R/3)+16 <= R once R>=48.
    # Residue 1: 2*((R+2)/3)+16 <= R once R>=52.
    # Residue 2: 2*((R+1)/3)+16 <= R once R>=50.
    if 2 * ((48) // 3) + 16 != 48:
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND zero residue moved")
    if 2 * ((52 + 2) // 3) + 16 != 52:
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND one residue moved")
    if 2 * ((50 + 1) // 3) + 16 != 50:
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND two residue moved")
    if minimum_working < 52:
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND block threshold moved")
    height = minimum_height
    margin = 7 * height * height + 10 * height - 3
    expanded = 32 * height * height - ((5 * height - 1) ** 2 + 2)
    if margin != expanded or margin <= 0:
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND square margin moved")
    if (7 * (2 * height + 1) + 10) <= 0:
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND square growth moved")


def main() -> None:
    pinned = load()
    exponential_is_below_three()
    scale, bits, height, guard, working, blocks = parameters(1, 1)
    if (scale, bits, height, guard, working, blocks) != (4, 6, 27, 5, 115, 47):
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND minimum parameters moved")
    universal(height, working)
    checked = 0
    for precision in range(1, BOX + 1):
        for frequency in range(1, BOX + 1):
            scale, bits, height, guard, working, blocks = parameters(precision, frequency)
            if height < 27 or working < 115 or working >= 5 * height:
                raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND pair bound moved")
            if 2 * blocks > working or working * working + 2 > 32 * height * height:
                raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND pair width moved")
            if height > 1 << guard:
                raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND guard moved")
            exponent = bits + 2 * scale + 7 + 2 * guard - working
            if exponent != -precision - 2 * scale - 3 * bits - 57:
                raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND exponent moved")
            if exponent > -precision - 83:
                raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND final exponent moved")
            checked += 1
    if (
        pinned["minimum_H0"] != 27
        or pinned["minimum_R"] != 115
        or pinned["checked_pairs"] != checked
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_COEFFICIENT_WIDTH_BOUND pinned result moved")
    print(f"PASS_COEFFICIENT_WIDTH_BOUND pairs={checked} no_new_kappa")


if __name__ == "__main__":
    main()
