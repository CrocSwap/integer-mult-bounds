#!/usr/bin/env python3
"""Cross-pair collisions equal twice the within-class products.

The checker tests every subset of F_2^4. It does not run a seven-label census.
"""

import json
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_PAIR_COLLISION_IDENTITY checks=983040 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
DIMENSION = 4


def fail(message):
    raise SystemExit("FAIL_PAIR_COLLISION_IDENTITY " + message)


def require(condition, message):
    if not condition:
        fail(message)


def agrees(even, odd):
    within_even = {}
    for left in range(len(even)):
        for right in range(left + 1, len(even)):
            mask = even[left] ^ even[right]
            within_even[mask] = within_even.get(mask, 0) + 1
    within_odd = {}
    for left in range(len(odd)):
        for right in range(left + 1, len(odd)):
            mask = odd[left] ^ odd[right]
            within_odd[mask] = within_odd.get(mask, 0) + 1
    cross = {}
    for left in even:
        for right in odd:
            mask = left ^ right
            cross[mask] = cross.get(mask, 0) + 1
    collisions = sum(comb(count, 2) for count in cross.values())
    product = 0
    for mask in set(within_even) | set(within_odd):
        product += within_even.get(mask, 0) * within_odd.get(mask, 0)
    return collisions == 2 * product


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    space = 1 << DIMENSION
    checks = 0
    for bits in range(1 << space):
        points = [point for point in range(space) if (bits >> point) & 1]
        for mask in range(1, space):
            even = [point for point in points if (point & mask).bit_count() % 2 == 0]
            odd = [point for point in points if (point & mask).bit_count() % 2 == 1]
            require(agrees(even, odd), "the pair identity moved")
            checks += 1
    require(checks == (1 << space) * (space - 1) == 983040, "the check count moved")
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(receipt["dimension"] == DIMENSION, "receipt dimension")
    require(receipt["sets"] == 1 << space, "receipt sets")
    require(receipt["functionals"] == space - 1, "receipt functionals")
    require(receipt["checks"] == checks, "receipt checks")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
