"""Bit budget for a cleared minor.

A k-by-k matrix whose entries are ratios of B-bit integers clears, row by
row, to integers below 2^{k B}. The published coarse entry budget is
(k+1)B bits. The Hadamard number k!(2^M-1)^k then fits in
D = k(k+1)B + k ceil(log2 k) + 2 bits.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
LIMIT = 20


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_MINOR_BIT_BUDGET selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def ceil_log2(value: int) -> int:
    return (value - 1).bit_length()


def budget(order: int, bits: int) -> int:
    return order * (order + 1) * bits + order * ceil_log2(order) + 2


def factorial(order: int) -> int:
    value = 1
    for factor in range(2, order + 1):
        value *= factor
    return value


def main() -> None:
    pinned = load()
    pairs = 0
    for order in range(1, LIMIT + 1):
        fact = factorial(order)
        if order > 1 and fact.bit_length() > order * ceil_log2(order):
            raise SystemExit("FAIL_MINOR_BIT_BUDGET factorial moved")
        for bits in range(1, LIMIT + 1):
            entry_bits = order * bits
            if entry_bits > (order + 1) * bits:
                raise SystemExit("FAIL_MINOR_BIT_BUDGET entry budget moved")
            width = (order + 1) * bits
            hadamard = fact * ((1 << width) - 1) ** order
            if hadamard.bit_length() > budget(order, bits):
                raise SystemExit("FAIL_MINOR_BIT_BUDGET Hadamard moved")
            pairs += 1
    small = 0
    small_budget = budget(2, 1)
    for a in range(-3, 4):
        for b in range(-3, 4):
            for c in range(-3, 4):
                for d in range(-3, 4):
                    determinant = a * d - b * c
                    if abs(determinant).bit_length() > small_budget:
                        raise SystemExit("FAIL_MINOR_BIT_BUDGET small determinant moved")
                    small += 1
    if (
        pinned["pairs"] != pairs
        or pinned["small_determinants"] != small
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_MINOR_BIT_BUDGET pinned result moved")
    print(f"PASS_MINOR_BIT_BUDGET pairs={pairs} no_new_kappa")


if __name__ == "__main__":
    main()
