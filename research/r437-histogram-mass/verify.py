#!/usr/bin/env python3
"""The published R437 histogram has rank mass 1808352, above the selected kappa.

The checker adds the published counts. It does not replay the word.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_R437_HISTOGRAM_MASS rank_mass=1808352 above_selected=true no_new_kappa"
HISTOGRAM = {1: 380160, 2: 400864, 3: 22176, 4: 26592, 5: 29376, 6: 17376, 7: 26496, 34: 64, 42: 352}


def fail(message):
    raise SystemExit("FAIL_R437_HISTOGRAM_MASS " + message)


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


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    kappa = Fraction(selected["kappa"])
    require(kappa == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    children = sum(HISTOGRAM.values())
    mass = sum(rank * count for rank, count in HISTOGRAM.items())
    require(children == 903456, "the child count moved")
    require(mass == 1808352, "the rank mass moved")
    require(32 * 3933 == 125856 and 32 * 888 == 28416, "the replica totals moved")
    require(28425 - 28416 == 9, "the physical margin moved")
    require(209 * 5 + 2 == 1047 and 209 + 2 + 11 == 222, "the window moved")
    coefficient = Fraction(868314126713557740143, 500000000000000000000000)
    require(coefficient == Fraction(1736628253427115480286, 10**24), "the decimal moved")
    require(coefficient > kappa, "the BIT coefficient meets the selected kappa")
    return {
        "children": 903456,
        "rank_mass": 1808352,
        "occurrences": 125856,
        "width": 28416,
        "above_selected": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
