#!/usr/bin/env python3
"""Recorded stock coefficients in the selected bootstrap audit.

The checker reads the receipt. It does not recompute the fourteen stages.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_STOCK_COEFFICIENT_NULLS stages=14 adopted=false no_new_kappa"
RECEIPT = "research/selected-bootstrap-stock-audit/RESULT.json"


def fail(message):
    raise SystemExit("FAIL_STOCK_COEFFICIENT_NULLS " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == {RECEIPT}, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    receipt = json.loads((ROOT / RECEIPT).read_text(encoding="utf-8"))
    kappa = Fraction(836330098538459, 500000000000000000)
    require(Fraction(selected["kappa"]) == kappa, "the selected kappa moved")
    require(Fraction(receipt["selected_kappa"]) == kappa, "the receipt kappa moved")
    stages = []
    headrooms = []
    for name in ("bootstrap", "conservative_bootstrap"):
        rows = receipt["branches"][name]["stages"]
        require(len(rows) == 7, "a branch lost a stage")
        stages.extend(rows)
        headrooms.append(rows[0]["stock_headroom_log2"])
    require(len(stages) == 14, "the stage count moved")
    require(all(row["actual_stock_coefficient"] is None for row in stages), "a recorded coefficient is present")
    require(receipt["source_boundary"]["actual_stage_stock_coefficients"] is None, "the boundary coefficient is present")
    candidate = receipt["source_boundary"]["historical_candidate"]["new_stock_coefficient"]
    require(candidate == 57604, "the historical candidate moved")
    require(all(row["actual_stock_coefficient"] != candidate for row in stages), "the historical candidate was adopted")
    require(headrooms == [6562783, 6562783], "the recorded stage-1 headrooms moved")
    return {
        "stages": 14,
        "null_coefficients": 14,
        "stage1_headroom": 6562783,
        "historical_candidate": 57604,
        "adopted": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
