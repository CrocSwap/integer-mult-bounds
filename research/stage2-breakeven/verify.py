"""Stage-2 break-even offset.

Each printed extraction margin equals the negation of its price minus
2,091,300.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
BREAK_EVEN = 2_091_300
ROWS = (
    (-2_101_683, 10_383),
    (-2_106_679, 15_379),
    (-2_101_683, 10_383),
    (-2_106_679, 15_379),
    (-2_106_679, 15_379),
)


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_STAGE2_BREAKEVEN selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def price_sum() -> int:
    return sum(price for price, _margin in ROWS)


def price_gap() -> int:
    prices = {price for price, _margin in ROWS}
    if len(prices) != 2:
        raise SystemExit("FAIL_STAGE2_BREAKEVEN price classes moved")
    return max(prices) - min(prices)


def main() -> None:
    pinned = load()
    for price, margin in ROWS:
        if margin != -price - BREAK_EVEN:
            raise SystemExit(f"FAIL_STAGE2_BREAKEVEN row {price}")
    total = price_sum()
    gap = price_gap()
    margins = {margin for _price, margin in ROWS}
    if max(margins) - min(margins) != gap:
        raise SystemExit("FAIL_STAGE2_BREAKEVEN margin gap moved")
    if (
        pinned["steps"] != len(ROWS)
        or pinned["break_even"] != BREAK_EVEN
        or pinned["price_sum"] != total
        or pinned["price_gap"] != gap
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_STAGE2_BREAKEVEN pinned result moved")
    print(f"PASS_STAGE2_BREAKEVEN steps={len(ROWS)} no_new_kappa")


if __name__ == "__main__":
    main()
