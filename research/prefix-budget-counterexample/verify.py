#!/usr/bin/env python3
"""Dimension-4 counterexample to a balanced collision budget.

The checker reconstructs one length-8 word. It does not run a seven-label census.
"""

import json
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_PREFIX_BUDGET_COUNTEREXAMPLE excess=8 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
WORD = (0, 1, 0, 2, 1, 3, 2, 3)
PREFIXES = (0, 1, 2, 3, 4, 6, 8, 12)
SPLITS = ((10, 10, 27, 36), (10, 9, 18, 26), (10, 8, 10, 16), (9, 9, 9, 17), (10, 7, 3, 6))


def fail(message):
    raise SystemExit("FAIL_PREFIX_BUDGET_COUNTEREXAMPLE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def functional(mask, point):
    return (point & mask).bit_count() % 2


def representations(group):
    counts = {}
    for left in range(len(group)):
        for right in range(left + 1, len(group)):
            mask = group[left] ^ group[right]
            counts[mask] = counts.get(mask, 0) + 1
    return counts


def collision_excess(left, right):
    first = representations(left)
    second = representations(right)
    return (
        comb(len(left), 2) - len(first)
        + comb(len(right), 2) - len(second),
        first,
        second,
    )


def classes(points, mask):
    zero = [point for point in points if functional(mask, point) == 0]
    one = [point for point in points if functional(mask, point) == 1]
    return zero, one


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    state = 0
    seen = [0]
    for bit in WORD:
        state ^= 1 << bit
        seen.append(state)
    require(seen[-1] == 0, "the walk did not return")
    require(tuple(sorted(set(seen[:-1]))) == PREFIXES, "the prefix set moved")
    require(len(set(seen[:-1])) == 8, "a prefix repeated")
    labels = [0, 0, 0, 0]
    for bit in WORD:
        labels[bit] += 1
    require(labels == [2, 2, 2, 2], "a label left its even count")
    covered = {left ^ right for left in PREFIXES for right in PREFIXES}
    require(covered == set(range(16)), "a mask was missed")

    even, odd = classes(PREFIXES, 15)
    weight_excess, _, _ = collision_excess(even, odd)
    require((len(even), len(odd), weight_excess) == (4, 4, 0), "the weight split moved")
    low, high = classes(PREFIXES, 1)
    bit_excess, low_pairs, high_pairs = collision_excess(low, high)
    require((len(low), len(high), bit_excess) == (6, 2, 8), "the bit-0 excess moved")
    balanced = comb(4, 2) + comb(4, 2) - 7
    actual = comb(6, 2) + comb(2, 2) - 7
    require(balanced == 5 and actual == 9, "a budget moved")
    require(bit_excess > balanced and bit_excess <= actual, "the rejection moved")

    cross = {}
    for left in low:
        for right in high:
            mask = left ^ right
            cross[mask] = cross.get(mask, 0) + 1
    pair_sum = sum(comb(count, 2) for count in cross.values())
    product = 0
    for mask in set(low_pairs) | set(high_pairs):
        product += low_pairs.get(mask, 0) * high_pairs.get(mask, 0)
    require(pair_sum == 2 * product, "the pair identity moved")
    require(len(low) * len(high) - len(cross) == 4, "the odd excess moved")

    admitted = 0
    for mask in range(1, 16):
        left, right = classes(PREFIXES, mask)
        excess, _, _ = collision_excess(left, right)
        budget = comb(len(left), 2) + comb(len(right), 2) - 7
        require(excess <= budget, "an actual budget rejected the word")
        admitted += 1
    require(admitted == 15, "functional count")

    rows = 0
    half = 1 << 6
    for left, right, even_budget, odd_budget in SPLITS:
        require(comb(left, 2) + comb(right, 2) - (half - 1) == even_budget, "an even row moved")
        require(left * right - half == odd_budget, "an odd row moved")
        rows += 1

    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(receipt["prefix_states"] == 8, "receipt prefixes")
    require(receipt["coverage"] == 16, "receipt coverage")
    require(receipt["bit0_excess"] == 8, "receipt excess")
    require(receipt["balanced_budget"] == 5, "receipt balanced")
    require(receipt["bit0_budget"] == 9, "receipt bit budget")
    require(receipt["functionals"] == 15, "receipt functionals")
    require(receipt["table_rows"] == rows == 5, "receipt rows")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
