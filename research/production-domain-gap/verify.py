"""Simultaneous production bounds on precision, scale, spacing and width.

The stated domain asks for an integer precision p >= 101, a scale
u >= ceil(log2(8p)), a positive integer spacing d, and
w = ceil(sqrt(16p/u))+2, with u*d <= p and d-2 > 4w.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
FIRST = 101
WITNESS = 4464


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_PRODUCTION_DOMAIN_GAP selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def ceil_log2(value: int) -> int:
    return (value - 1).bit_length()


def min_product(precision: int) -> Fraction:
    """Least u*d over real u and the smallest integer d that can meet d-2 > 4w."""
    minimum_scale = ceil_log2(8 * precision)
    best: Fraction | None = None
    width_root = 1
    while True:
        left = Fraction(16 * precision, width_root * width_root)
        if left <= minimum_scale:
            break
        product = left * (4 * width_root + 11)
        if best is None or product < best:
            best = product
        width_root += 1
    root = 1
    while root * root * minimum_scale < 16 * precision:
        root += 1
    product = Fraction(minimum_scale * (4 * root + 11))
    if best is None or product < best:
        best = product
    return best


def main() -> None:
    pinned = load()
    blocked = 0
    for precision in range(FIRST, WITNESS):
        if min_product(precision) <= precision:
            raise SystemExit("FAIL_PRODUCTION_DOMAIN_GAP early precision moved")
        blocked += 1
    scale, spacing, width = 16, 279, 69
    if (
        scale < ceil_log2(8 * WITNESS)
        or scale * spacing != WITNESS
        or spacing - 2 <= 4 * width
    ):
        raise SystemExit("FAIL_PRODUCTION_DOMAIN_GAP witness moved")
    root = width - 2
    argument = 16 * WITNESS // scale
    if (root - 1) * (root - 1) >= argument or root * root < argument:
        raise SystemExit("FAIL_PRODUCTION_DOMAIN_GAP width moved")
    if Fraction(1, 4 * spacing) >= Fraction(1, 2 * spacing - 1):
        raise SystemExit("FAIL_PRODUCTION_DOMAIN_GAP theta interval moved")
    if min_product(WITNESS) != WITNESS:
        raise SystemExit("FAIL_PRODUCTION_DOMAIN_GAP first precision moved")
    if (
        pinned["blocked_precisions"] != blocked
        or pinned["first_precision"] != WITNESS
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_PRODUCTION_DOMAIN_GAP pinned result moved")
    print(f"PASS_PRODUCTION_DOMAIN_GAP precisions={blocked} no_new_kappa")


if __name__ == "__main__":
    main()
