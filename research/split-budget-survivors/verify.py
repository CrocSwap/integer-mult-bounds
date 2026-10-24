#!/usr/bin/env python3
"""Weight splits that survive the even budget and the pair identity.

The checker classifies those splits. It does not run a seven-label census.
"""

import json
from math import ceil, comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_SPLIT_BUDGET_SURVIVORS splits=5 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
HALF = 1 << 6
LENGTH20 = ((10, 10), (10, 9), (10, 8), (9, 9), (10, 7))


def fail(message):
    raise SystemExit("FAIL_SPLIT_BUDGET_SURVIVORS " + message)


def require(condition, message):
    if not condition:
        fail(message)


def maximum_product(budget):
    return (budget // 2) * ((budget + 1) // 2)


def classify(limit):
    survivors = []
    examined = 0
    for larger in range(0, limit + 1):
        for smaller in range(0, larger + 1):
            examined += 1
            budget = comb(larger, 2) + comb(smaller, 2) - (HALF - 1)
            cross = larger * smaller
            if budget < 0 or cross < HALF:
                continue
            need = ceil((cross - HALF) / 2)
            if budget + maximum_product(budget) < need:
                continue
            survivors.append((larger, smaller))
    return examined, survivors


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    budget = comb(9, 2) + comb(8, 2) - (HALF - 1)
    require(budget == 1, "the (9,8) budget moved")
    require(ceil((9 * 8 - HALF) / 2) == 4, "the (9,8) need moved")
    require(all(left * right == 0 for left in range(2) for right in range(2) if left + right <= 1), "a (9,8) row had a product")
    examined20, survivors20 = classify(10)
    examined18, survivors18 = classify(9)
    require(examined20 == 66 and sorted(survivors20) == sorted(LENGTH20), "the length-20 list moved")
    require(examined18 == 55 and survivors18 == [(9, 9)], "the length-18 list moved")
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(receipt["length20_splits"] == 66, "receipt length 20")
    require(receipt["length20_survivors"] == 5, "receipt survivors")
    require(receipt["length18_splits"] == 55, "receipt length 18")
    require(receipt["length18_survivors"] == 1, "receipt length-18 survivors")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
