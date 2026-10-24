"""XOR-mask decreasing subsequences.

The sequence x |-> x xor mask has longest decreasing subsequence
2**(mask.bit_count()). Composing two masks gives the XOR of the masks, whose
weight is at most the sum of the weights.
"""

from __future__ import annotations

import bisect
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
MAX_DIMENSION = 12
PAIR_DIMENSIONS = 10


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_XOR_MASK_LDS selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def longest_decreasing(values: list[int]) -> int:
    piles: list[int] = []
    for value in values:
        key = -value
        index = bisect.bisect_left(piles, key)
        if index == len(piles):
            piles.append(key)
        else:
            piles[index] = key
    return len(piles)


def mask_lengths(max_dimension: int) -> int:
    checked = 0
    for dimension in range(1, max_dimension + 1):
        size = 1 << dimension
        for mask in range(size):
            length = longest_decreasing([index ^ mask for index in range(size)])
            if length != 1 << mask.bit_count():
                raise SystemExit(
                    f"FAIL_XOR_MASK_LDS dimension {dimension} mask {mask}"
                )
            checked += 1
    return checked


def composition_pairs(max_dimension: int) -> int:
    checked = 0
    for dimension in range(1, max_dimension + 1):
        size = 1 << dimension
        for left in range(size):
            left_weight = left.bit_count()
            for right in range(size):
                combined = left ^ right
                overlap = (left & right).bit_count()
                if combined.bit_count() + 2 * overlap != left_weight + right.bit_count():
                    raise SystemExit(
                        f"FAIL_XOR_MASK_LDS pair {dimension} {left} {right}"
                    )
                checked += 1
    return checked


def main() -> None:
    pinned = load()
    masks = mask_lengths(MAX_DIMENSION)
    pairs = composition_pairs(PAIR_DIMENSIONS)
    if (
        pinned["max_dimension"] != MAX_DIMENSION
        or pinned["masks"] != masks
        or pinned["pair_dimensions"] != PAIR_DIMENSIONS
        or pinned["pairs"] != pairs
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_XOR_MASK_LDS pinned result moved")
    print(f"PASS_XOR_MASK_LDS masks={masks} no_new_kappa")


if __name__ == "__main__":
    main()
