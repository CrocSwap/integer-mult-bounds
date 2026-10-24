"""Spare bits in the published online storage budget.

G = 8p + 8 ceil(log2(p+2)) + 32. The largest stated magnitude is the
prefix bound 2^(8p+18) p^2. Its bit length leaves at least 56 bits inside
G for every precision p >= 101, which covers the claimed twelve spare bits.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
LOW = 101
HIGH = 300


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_STORAGE_SPARE_BITS selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def ceil_log2(value: int) -> int:
    return (value - 1).bit_length()


def budget(precision: int) -> int:
    return 8 * precision + 8 * ceil_log2(precision + 2) + 32


def magnitudes(precision: int) -> list[int]:
    square = precision * precision
    cube = square * precision
    fourth = square * square
    return [
        9 * precision,
        28 * precision,
        (1 << 11) * square,
        (1 << 10) * square,
        (1 << 12) * square,
        (1 << 16) * cube,
        2,
        1 << (8 * precision + 1),
        1,
        (1 << (8 * precision + 18)) * square,
        (1 << 18) * fourth,
        (1 << 13) * square,
        (1 << 17) * cube,
    ]


def main() -> None:
    pinned = load()
    # p <= 2^c - 2 < 2^c, so p^2 < 2^(2c) and the prefix spare is at least
    # 6c + 14. For p >= 101, c >= 7, hence the spare is at least 56.
    if ceil_log2(101 + 2) != 7 or 6 * 7 + 14 != 56:
        raise SystemExit("FAIL_STORAGE_SPARE_BITS closed form moved")
    checks = 0
    minimum = None
    for precision in range(LOW, HIGH + 1):
        guard = ceil_log2(precision + 2)
        square_bits = (precision * precision).bit_length()
        if square_bits > 2 * guard:
            raise SystemExit("FAIL_STORAGE_SPARE_BITS square bits moved")
        spare = budget(precision) - (8 * precision + 18 + square_bits)
        if spare < 6 * guard + 14 or spare < 56:
            raise SystemExit("FAIL_STORAGE_SPARE_BITS spare moved")
        prefix = (1 << (8 * precision + 18)) * precision * precision
        if prefix.bit_length() != 8 * precision + 18 + square_bits:
            raise SystemExit("FAIL_STORAGE_SPARE_BITS prefix bits moved")
        width = budget(precision)
        for value in magnitudes(precision):
            if value.bit_length() > width - 56:
                raise SystemExit("FAIL_STORAGE_SPARE_BITS magnitude moved")
            checks += 1
        if minimum is None or spare < minimum:
            minimum = spare
    if (
        pinned["checks"] != checks
        or pinned["minimum_spare"] != minimum
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_STORAGE_SPARE_BITS pinned result moved")
    print(f"PASS_STORAGE_SPARE_BITS precisions={HIGH - LOW + 1} no_new_kappa")


if __name__ == "__main__":
    main()
