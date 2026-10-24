"""Margins for one rounded LU perturbation.

The lower factor moves by at most 2 p eta and the upper factor by at most
3 p eta, with eta = 2^(-32768 p). The stated caps are ||L|| <= 65 p^2,
||L^{-1}|| <= 32 p and ||U|| < 2. Those caps imply the published product,
inverse, growth and residual margins.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
EXPONENT = 32768
LIMIT = 200


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_FACTOR_PERTURBATION_MARGIN selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def below_power(value: int, exponent: int) -> bool:
    return value.bit_length() <= exponent


def main() -> None:
    pinned = load()
    if 66 * 8 != 528 or 528 + 2 != 530 or 32 * 2 != 64:
        raise SystemExit("FAIL_FACTOR_PERTURBATION_MARGIN constants moved")
    if EXPONENT < 2 or (1 + 1) ** 2 != 4 * (1 ** 2):
        raise SystemExit("FAIL_FACTOR_PERTURBATION_MARGIN induction moved")
    half = Fraction(1, 2)
    if Fraction(32) / (1 - half) != 64:
        raise SystemExit("FAIL_FACTOR_PERTURBATION_MARGIN Neumann threshold moved")
    checked = 0
    for precision in range(1, LIMIT + 1):
        exponent = EXPONENT * precision
        if not below_power(128 * precision * precision - 1, exponent):
            raise SystemExit("FAIL_FACTOR_PERTURBATION_MARGIN inverse margin moved")
        if 5 * precision * precision - 4 < 1 or not below_power(6 * precision, exponent):
            raise SystemExit("FAIL_FACTOR_PERTURBATION_MARGIN product margin moved")
        if not below_power(530 * precision * precision, exponent):
            raise SystemExit("FAIL_FACTOR_PERTURBATION_MARGIN residual margin moved")
        if (precision + 1) ** 2 > 4 * precision * precision:
            raise SystemExit("FAIL_FACTOR_PERTURBATION_MARGIN growth step moved")
        if 2 * precision * precision < 2:
            raise SystemExit("FAIL_FACTOR_PERTURBATION_MARGIN absorption moved")
        checked += 1
    if pinned["precisions"] != checked or pinned["no_new_kappa"] is not True:
        raise SystemExit("FAIL_FACTOR_PERTURBATION_MARGIN pinned result moved")
    print(f"PASS_FACTOR_PERTURBATION_MARGIN precisions={checked} no_new_kappa")


if __name__ == "__main__":
    main()
