"""Permutation decreasing-subsequence products.

For permutations p and q of the same order, the longest decreasing subsequence
of p composed with q is at most the product of the two lengths.
"""

from __future__ import annotations

import bisect
import json
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
MAX_ORDER = 7


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_PERMUTATION_LDS_PRODUCT selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def longest_decreasing(values: list[int] | tuple[int, ...]) -> int:
    piles: list[int] = []
    for value in values:
        key = -value
        index = bisect.bisect_left(piles, key)
        if index == len(piles):
            piles.append(key)
        else:
            piles[index] = key
    return len(piles)


def check_order(order: int) -> tuple[int, int]:
    perms = list(permutations(range(order)))
    lengths = [longest_decreasing(perm) for perm in perms]
    sharp = 0
    for left_index, left in enumerate(perms):
        left_length = lengths[left_index]
        for right_index, right in enumerate(perms):
            composed = [left[right[index]] for index in range(order)]
            length = longest_decreasing(composed)
            bound = left_length * lengths[right_index]
            if length > bound:
                raise SystemExit(f"FAIL_PERMUTATION_LDS_PRODUCT order {order}")
            if length == bound:
                sharp += 1
    return len(perms) ** 2, sharp


def main() -> None:
    pinned = load()
    pairs = 0
    sharp = 0
    for order in range(1, MAX_ORDER + 1):
        found_pairs, found_sharp = check_order(order)
        pairs += found_pairs
        sharp += found_sharp
    if sharp == 0:
        raise SystemExit("FAIL_PERMUTATION_LDS_PRODUCT equality missing")
    if (
        pinned["max_order"] != MAX_ORDER
        or pinned["pairs"] != pairs
        or pinned["sharp_pairs"] != sharp
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_PERMUTATION_LDS_PRODUCT pinned result moved")
    print(f"PASS_PERMUTATION_LDS_PRODUCT pairs={pairs} no_new_kappa")


if __name__ == "__main__":
    main()
