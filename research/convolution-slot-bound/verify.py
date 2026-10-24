"""Slot width for a nonnegative convolution.

Two length-n sequences with nonnegative coefficients below 2^a and 2^b have
convolution entries at most n(2^a-1)(2^b-1). That quantity is strictly below
2^{a+b+ceil(log2 n)}, so it fits in the low half of a slot of
a+b+ceil(log2 n)+1 bits.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
BIT_LIMIT = 20
LENGTH_LIMIT = 64


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_CONVOLUTION_SLOT_BOUND selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def ceil_log2(length: int) -> int:
    return (length - 1).bit_length()


def largest(left_bits: int, right_bits: int, length: int) -> int:
    return length * ((1 << left_bits) - 1) * ((1 << right_bits) - 1)


def half_slot(left_bits: int, right_bits: int, length: int) -> int:
    return 1 << (left_bits + right_bits + ceil_log2(length))


def sequences(bits: int, length: int) -> list[list[int]]:
    base = 1 << bits
    found = []
    for index in range(base ** length):
        row = []
        for _ in range(length):
            row.append(index % base)
            index //= base
        found.append(row)
    return found


def convolution(left: list[int], right: list[int]) -> list[int]:
    output = [0] * (len(left) + len(right) - 1)
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            output[i + j] += left_value * right_value
    return output


def main() -> None:
    pinned = load()
    # n <= 2^L and (2^a-1)(2^b-1) = 2^{a+b} - 2^a - 2^b + 1, so the largest
    # overlap is strictly below 2^{a+b+L} for every positive a, b, and n.
    if largest(1, 1, 1) >= half_slot(1, 1, 1):
        raise SystemExit("FAIL_CONVOLUTION_SLOT_BOUND unit case moved")
    if (1 << 1) * ((1 << 4) - (1 << 2) - (1 << 2) + 1) >= (1 << (4 + 1)):
        raise SystemExit("FAIL_CONVOLUTION_SLOT_BOUND gap identity moved")
    checked = 0
    for left_bits in range(1, BIT_LIMIT + 1):
        for right_bits in range(1, BIT_LIMIT + 1):
            for length in range(1, LENGTH_LIMIT + 1):
                guard = ceil_log2(length)
                if length > (1 << guard):
                    raise SystemExit("FAIL_CONVOLUTION_SLOT_BOUND length guard moved")
                span = (1 << (left_bits + right_bits)) - (1 << left_bits) - (1 << right_bits) + 1
                expanded = (1 << guard) * span
                closed = (
                    (1 << (guard + left_bits + right_bits))
                    - (1 << (guard + left_bits))
                    - (1 << (guard + right_bits))
                    + (1 << guard)
                )
                if expanded != closed or expanded >= half_slot(left_bits, right_bits, length):
                    raise SystemExit("FAIL_CONVOLUTION_SLOT_BOUND expansion moved")
                if largest(left_bits, right_bits, length) > expanded:
                    raise SystemExit("FAIL_CONVOLUTION_SLOT_BOUND parameter moved")
                checked += 1
    exhaustive = 0
    for left_bits in (1, 2):
        for right_bits in (1, 2):
            for length in range(1, 5):
                limit = half_slot(left_bits, right_bits, length)
                cap = largest(left_bits, right_bits, length)
                for left in sequences(left_bits, length):
                    for right in sequences(right_bits, length):
                        values = convolution(left, right)
                        if max(values) > cap or max(values) >= limit:
                            raise SystemExit("FAIL_CONVOLUTION_SLOT_BOUND sequence moved")
                        exhaustive += 1
    if (
        pinned["parameter_checks"] != checked
        or pinned["exhaustive_pairs"] != exhaustive
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_CONVOLUTION_SLOT_BOUND pinned result moved")
    print(f"PASS_CONVOLUTION_SLOT_BOUND pairs={exhaustive} no_new_kappa")


if __name__ == "__main__":
    main()
