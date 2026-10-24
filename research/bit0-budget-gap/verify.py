#!/usr/bin/env python3
"""Even and odd budgets for unbalanced bit-0 class sizes.

The checker evaluates the binomial formulas. It does not run a seven-label census.
"""

import json
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_BIT0_BUDGET_GAP deviations=11 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
HALF = 1 << 6


def fail(message):
    raise SystemExit("FAIL_BIT0_BUDGET_GAP " + message)


def require(condition, message):
    if not condition:
        fail(message)


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    deviations = 0
    obstructions = 0
    for deviation in range(0, 11):
        left = 10 + deviation
        right = 10 - deviation
        even_pairs = comb(left, 2) + comb(right, 2)
        require(even_pairs == 90 + deviation * deviation, "the pair polynomial moved")
        require(even_pairs - (HALF - 1) == 27 + deviation * deviation, "the even budget moved")
        cross = left * right
        require(cross == 100 - deviation * deviation, "the cross count moved")
        if cross < HALF:
            require(deviation >= 7, "a small deviation lost its odd masks")
            obstructions += 1
        else:
            require(deviation <= 6, "a large deviation still covered the odd masks")
            require(cross - HALF == 36 - deviation * deviation, "the odd excess moved")
        deviations += 1
    require(deviations == 11 and obstructions == 4, "the deviation count moved")
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(receipt["deviations"] == 11, "receipt deviations")
    require(receipt["even_slack"] == "d^2", "receipt slack")
    require(receipt["odd_obstructions"] == 4, "receipt obstructions")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
