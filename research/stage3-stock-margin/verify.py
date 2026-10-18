#!/usr/bin/env python3
"""Native stage 3 sends its width-w calls into stage 2's stopped range.

The stock coefficient itself stays unresolved. No supplier replay.
"""
import json
import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
RESULT = ROOT / "research/selected-bootstrap-stock-audit/RESULT.json"

STAGE2_MARGIN = 2851485324488315
STAGE3_MARGIN = 1015784602045963452130
ROUTING_ROOM = 1701909188404384116
LEMMA = (
    "For the selected native receipt, s*L3 - L2 > 1015784602045963452130. "
    "Every width w >= e^s with e >= 2^L3 therefore satisfies w > 2^(L2 + 1015784602045963452130), "
    "so that call sits in stage 2's stopped range. "
    "This does not choose between an external factor of 1 and a hoisted routing factor."
)


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def floor_fraction(value):
    return value.numerator // value.denominator


def main():
    stages = json.loads(RESULT.read_text(encoding="utf-8"))["branches"]["bootstrap"]["stages"]
    require(all(stage["actual_stock_coefficient"] is None for stage in stages), "a native coefficient is already stored")
    s = 1 - Fraction(stages[0]["gaps"]["stock"])
    one_s = Fraction(stages[0]["gaps"]["stock"])
    require(all(Fraction(stage["gaps"]["stock"]) == one_s for stage in stages), "native stock gap is not uniform")
    cutoffs = [int(stage["cutoff_log2"]) for stage in stages]
    require(floor_fraction(s * cutoffs[1] - cutoffs[0]) == STAGE2_MARGIN, "stage-2 margin does not match the published integer")
    margin = s * cutoffs[2] - cutoffs[1]
    require(floor_fraction(margin) == STAGE3_MARGIN and margin > STAGE3_MARGIN, "stage-3 margin mismatch")
    require(s * cutoffs[1] - cutoffs[1] < 0, "replacing L3 by L2 stayed nonnegative")
    require(floor_fraction(one_s * cutoffs[1]) == ROUTING_ROOM, "routing room mismatch")
    require(math.ceil(math.log2(8 * 8194)) == 17, "8194 bit length changed")
    require(17 <= stages[2]["stock_headroom_log2"], "stage-3 headroom does not cover ell 17")
    require(LEMMA in (PACKAGE / "README.md").read_text(encoding="utf-8"), "README dropped the lemma")
    print(
        "PASS_STAGE3_STOCK_MARGIN stage=3 "
        f"margin={STAGE3_MARGIN} routing_room={ROUTING_ROOM} "
        "coefficient=unresolved stage2_margin_reproduced=true"
    )


if __name__ == "__main__":
    main()
