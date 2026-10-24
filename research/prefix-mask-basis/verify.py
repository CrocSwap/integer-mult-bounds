"""Prefix-mask basis.

The prefix masks M_t = 2^(t+1) - 1 are a basis of the n-bit masks. The unique
subset whose XOR equals a mask is the set of positions where consecutive bits
differ, taking the bit past the top as zero.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
MAX_DIMENSION = 20


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_PREFIX_MASK_BASIS selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def boundary_xor(mask: int, dimension: int) -> tuple[int, int]:
    value = 0
    count = 0
    for index in range(dimension):
        bit = (mask >> index) & 1
        nxt = (mask >> (index + 1)) & 1 if index + 1 < dimension else 0
        if bit != nxt:
            value ^= (1 << (index + 1)) - 1
            count += 1
    return value, count


def run_boundaries(mask: int, dimension: int) -> int:
    runs = 0
    previous = 0
    for index in range(dimension):
        bit = (mask >> index) & 1
        if bit and not previous:
            runs += 1
        previous = bit
    return 2 * runs - (1 if mask & 1 else 0)


def subset_span(dimension: int) -> int:
    reached = {0}
    for index in range(dimension):
        prefix = (1 << (index + 1)) - 1
        reached |= {value ^ prefix for value in reached}
    return len(reached)


def check_dimension(dimension: int) -> int:
    if subset_span(dimension) != 1 << dimension:
        raise SystemExit(f"FAIL_PREFIX_MASK_BASIS uniqueness {dimension}")
    for mask in range(1 << dimension):
        value, count = boundary_xor(mask, dimension)
        if value != mask or count != run_boundaries(mask, dimension):
            raise SystemExit(f"FAIL_PREFIX_MASK_BASIS dimension {dimension} mask {mask}")
        if mask.bit_count() == 1:
            expected = 1 if mask == 1 else 2
            if count != expected:
                raise SystemExit(
                    f"FAIL_PREFIX_MASK_BASIS single bit {dimension} {mask}"
                )
    return 1 << dimension


def main() -> None:
    pinned = load()
    masks = sum(check_dimension(dimension) for dimension in range(1, MAX_DIMENSION + 1))
    if (
        pinned["max_dimension"] != MAX_DIMENSION
        or pinned["masks"] != masks
        or pinned["low_bit_boundaries"] != 1
        or pinned["other_bit_boundaries"] != 2
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_PREFIX_MASK_BASIS pinned result moved")
    print(f"PASS_PREFIX_MASK_BASIS masks={masks} no_new_kappa")


if __name__ == "__main__":
    main()
