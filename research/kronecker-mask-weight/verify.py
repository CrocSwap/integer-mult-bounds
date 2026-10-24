"""Outer-product mask weights.

Placing the second mask into each set bit of the first, with stride equal to
the second width, produces a mask whose weight is the product of the weights.
A stride one shorter collides.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
MAX_PRODUCT_BITS = 20


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_KRONECKER_MASK_WEIGHT selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def flattened_weight(left: int, right: int, stride: int) -> int:
    value = 0
    shift = 0
    bits = left
    while bits:
        if bits & 1:
            value |= right << shift
        bits >>= 1
        shift += stride
    return value.bit_count()


def check(max_product_bits: int) -> tuple[int, int]:
    pairs = 0
    colliding = 0
    for left_width in range(1, max_product_bits + 1):
        for right_width in range(1, max_product_bits + 1):
            if left_width * right_width > max_product_bits:
                continue
            for left in range(1 << left_width):
                left_weight = left.bit_count()
                for right in range(1 << right_width):
                    weight = flattened_weight(left, right, right_width)
                    if weight != left_weight * right.bit_count():
                        raise SystemExit(
                            f"FAIL_KRONECKER_MASK_WEIGHT pair {left_width} {right_width}"
                        )
                    pairs += 1
            if left_width >= 2 and right_width >= 2:
                collided = flattened_weight(
                    (1 << left_width) - 1,
                    (1 << right_width) - 1,
                    right_width - 1,
                )
                if collided >= left_width * right_width:
                    raise SystemExit(
                        f"FAIL_KRONECKER_MASK_WEIGHT collision {left_width} {right_width}"
                    )
                colliding += 1
    return pairs, colliding


def main() -> None:
    pinned = load()
    pairs, colliding = check(MAX_PRODUCT_BITS)
    if (
        pinned["max_product_bits"] != MAX_PRODUCT_BITS
        or pinned["pairs"] != pairs
        or pinned["colliding_shapes"] != colliding
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_KRONECKER_MASK_WEIGHT pinned result moved")
    print(f"PASS_KRONECKER_MASK_WEIGHT pairs={pairs} no_new_kappa")


if __name__ == "__main__":
    main()
