"""Printed V45 margin ladder.

The margins for one through four V45 helpers form an arithmetic progression,
and the five joint prices sum to the stated stage-1 total.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
CLIMB = (-53_141, -27_770, -2_399, 22_972)
JOINT_MARGIN = 22_972
JOINT_PRICES = (-8_388_172, -10_499_041, -10_499_041, -8_382_370, -8_382_370)
STAGE1_TOTAL = -46_150_994


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_V45_MARGIN_LADDER selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def common_difference() -> int:
    gaps = {CLIMB[index + 1] - CLIMB[index] for index in range(len(CLIMB) - 1)}
    if len(gaps) != 1:
        raise SystemExit("FAIL_V45_MARGIN_LADDER the climb is not an arithmetic progression")
    return gaps.pop()


def joint_price_sum() -> int:
    return sum(JOINT_PRICES)


def main() -> None:
    pinned = load()
    difference = common_difference()
    total = joint_price_sum()
    if CLIMB[-1] != JOINT_MARGIN or total != STAGE1_TOTAL:
        raise SystemExit("FAIL_V45_MARGIN_LADDER printed total moved")
    if CLIMB[0] + 3 * difference != CLIMB[-1]:
        raise SystemExit("FAIL_V45_MARGIN_LADDER four-step total moved")
    if (
        pinned["steps"] != len(CLIMB)
        or pinned["common_difference"] != difference
        or pinned["joint_groups"] != len(JOINT_PRICES)
        or pinned["joint_price_sum"] != total
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_V45_MARGIN_LADDER pinned result moved")
    print(f"PASS_V45_MARGIN_LADDER difference={difference} no_new_kappa")


if __name__ == "__main__":
    main()
