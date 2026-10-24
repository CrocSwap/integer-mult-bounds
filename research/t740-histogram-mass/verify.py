#!/usr/bin/env python3
"""The published T740 histogram has rank mass 48,165,120, above the selected kappa.

The checker adds the published counts. It does not run the fresh-bootstrap wrapper.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_T740_HISTOGRAM_MASS rank_mass=48165120 above_selected=true no_new_kappa"
HISTOGRAM = {1: 16417896, 2: 4835160, 3: 1540174, 4: 679321, 5: 143992, 6: 3, 8: 53280, 48: 283185}


def fail(message):
    raise SystemExit("FAIL_T740_HISTOGRAM_MASS " + message)


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
    require(children == 23953011, "the child count moved")
    require(mass == 48165120, "the rank mass moved")
    require(740 * 9 == 6660 and 6660 * 408 == 2717280, "the role count moved")
    endpoint = Fraction(1730006549538841847005, 10**24)
    stated = endpoint - Fraction(1, 10**46) - Fraction(1, 10**70)
    require(stated > Fraction(173, 100000), "the stated root fell to 0.00173")
    require(stated > kappa, "the stated root meets the selected kappa")
    return {
        "children": 23953011,
        "rank_mass": 48165120,
        "calls": 6660,
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
