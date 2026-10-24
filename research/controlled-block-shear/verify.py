"""Controlled block reversal.

Reversing each aligned block of length 2^width whose start has a chosen bit
set equals XORing the low width bits on the indices where that bit is set,
exactly when the bit is constant on every block.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
MAX_DIMENSION = 16


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_CONTROLLED_BLOCK_SHEAR selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def reversed_blocks(dimension: int, width: int, control: int) -> list[int]:
    size = 1 << width
    values = list(range(1 << dimension))
    output: list[int] = []
    for start in range(0, len(values), size):
        block = values[start : start + size]
        output.extend(reversed(block) if (start >> control) & 1 else block)
    return output


def controlled_xor(dimension: int, width: int, control: int) -> list[int]:
    mask = (1 << width) - 1
    return [
        index ^ (mask if (index >> control) & 1 else 0)
        for index in range(1 << dimension)
    ]


def check_dimension(dimension: int) -> tuple[int, int]:
    positive = 0
    negative = 0
    for width in range(1, dimension):
        for control in range(dimension):
            same = reversed_blocks(dimension, width, control) == controlled_xor(
                dimension, width, control
            )
            if control >= width:
                if not same:
                    raise SystemExit(
                        f"FAIL_CONTROLLED_BLOCK_SHEAR agree {dimension} {width} {control}"
                    )
                positive += 1
            else:
                if same:
                    raise SystemExit(
                        f"FAIL_CONTROLLED_BLOCK_SHEAR split {dimension} {width} {control}"
                    )
                negative += 1
    return positive, negative


def main() -> None:
    pinned = load()
    positive = 0
    negative = 0
    for dimension in range(2, MAX_DIMENSION + 1):
        found_positive, found_negative = check_dimension(dimension)
        positive += found_positive
        negative += found_negative
    if (
        pinned["max_dimension"] != MAX_DIMENSION
        or pinned["positive_pairs"] != positive
        or pinned["negative_pairs"] != negative
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_CONTROLLED_BLOCK_SHEAR pinned result moved")
    print(f"PASS_CONTROLLED_BLOCK_SHEAR pairs={positive} no_new_kappa")


if __name__ == "__main__":
    main()
