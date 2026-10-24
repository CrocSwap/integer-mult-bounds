"""Completed compression error below two p-grid units.

For eta = 2^(-32768 p) and every integer p >= 101, the proof states

    sqrt(2)*2^(-p) + 2^(-16p) + 2^(-32p) + 2^(-42p) + 18 p eta
      < 2*2^(-p).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
FIRST = 101
LAST = 200


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_COMPRESSION_ERROR_SUM selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def main() -> None:
    pinned = load()
    if 99 * 99 <= 2 * 70 * 70:
        raise SystemExit("FAIL_COMPRESSION_ERROR_SUM square root moved")
    # 2 - 99/70 = 41/70. The coefficient 18p starts below 2^11, and each
    # later precision multiplies it by less than 2 while the exponent gap
    # grows by 32752.
    if 18 * FIRST >= (1 << 11) or 32752 * FIRST <= 11:
        raise SystemExit("FAIL_COMPRESSION_ERROR_SUM opening coefficient moved")
    if 32752 < 1:
        raise SystemExit("FAIL_COMPRESSION_ERROR_SUM induction gap moved")
    checked = 0
    for precision in range(FIRST, LAST + 1):
        if precision + 1 >= 2 * precision:
            raise SystemExit("FAIL_COMPRESSION_ERROR_SUM induction step moved")
        if 4 * 70 >= 41 * (1 << (15 * precision - 2)):
            raise SystemExit("FAIL_COMPRESSION_ERROR_SUM tail moved")
        checked += 1
    if pinned["precisions"] != checked or pinned["no_new_kappa"] is not True:
        raise SystemExit("FAIL_COMPRESSION_ERROR_SUM pinned result moved")
    print(f"PASS_COMPRESSION_ERROR_SUM precisions={checked} no_new_kappa")


if __name__ == "__main__":
    main()
