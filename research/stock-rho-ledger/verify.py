#!/usr/bin/env python3
"""The published row-ledger terms sum to 16469, and the caps differ by 8194.

The checker multiplies the published terms. It does not choose a reading of rho.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_STOCK_RHO_LEDGER ledger=16469 caps_differ=8194 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_STOCK_RHO_LEDGER " + message)


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
    require(set(pinned) == set(), "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def ceil_log2(value):
    guard = 0
    while (1 << guard) < value:
        guard += 1
    return guard


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    coarse = 367 * 27
    ordinary = 9 * 28
    prefix = 2 * 512
    require(coarse == 9909 and ordinary == 252 and prefix == 1024, "the family charges moved")
    bit = 2 * (64 * 64 + 1)
    require(bit == 8194 and bit + coarse + ordinary == 18355, "the BIT row moved")
    ledger = 2 * 2642 + coarse + ordinary + prefix
    require(ledger == 16469 and coarse + ordinary + prefix == 11185, "the ledger moved")
    gap = 10**6 - Fraction(51, 25) * 20161
    require(gap == Fraction(23971789, 25), "the row-product gap moved")
    low = Fraction("4362.14")
    high = Fraction("12556.14")
    require(high - low == 8194, "the displayed caps no longer differ by the BIT factor")
    require(ceil_log2(8 * low) == 16 and ceil_log2(8 * high) == 17, "the guards moved")
    require(high < 6562783, "a displayed cap meets the stage-1 guard")
    return {
        "ledger": 16469,
        "external_terms": 11185,
        "bit_row": 18355,
        "caps_differ_by": 8194,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
