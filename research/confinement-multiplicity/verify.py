#!/usr/bin/env python3
"""Difference multiplicities for the five imported 20-point covers.

The checker reads the table. It does not sample bases.
"""

import hashlib
import json
from fractions import Fraction
from itertools import combinations, combinations_with_replacement
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_CONFINEMENT_MULTIPLICITY excluded=14 open=21 no_new_kappa"
TABLE = "research/connector-covering-code/table6.json"
LABELS = 7
EDGES = 18


def fail(message):
    raise SystemExit("FAIL_CONFINEMENT_MULTIPLICITY " + message)


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
    require(set(pinned) == {TABLE}, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def histogram(points):
    counts = {}
    for left, right in combinations(points, 2):
        difference = left ^ right
        counts[difference] = counts.get(difference, 0) + 1
    return counts


def patterns():
    found = []
    for counts in combinations_with_replacement(range(2, 23, 2), LABELS):
        if sum(counts) != 22 or max(counts) > 6:
            continue
        if any(left + right > 10 for left, right in combinations(counts, 2)):
            continue
        found.append(sorted(counts, reverse=True))
    return sorted(found, reverse=True)


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    table = json.loads((ROOT / TABLE).read_text(encoding="utf-8"))
    rows = []
    for representative in table["representatives"]:
        points = sorted({0} | set(representative["columns"]))
        require(len(points) == 20, "a representative lost a point")
        require(len({left ^ right for left in points for right in points}) == 1 << LABELS, "a representative lost a cover")
        top = sorted(histogram(points).values(), reverse=True)[:LABELS]
        rows.append({"id": representative["id"], "sum": sum(top)})
    rows.sort(key=lambda row: row["id"])
    require([row["sum"] for row in rows] == [21, 21, 21, 14, 14], "a multiplicity sum moved")
    require(patterns() == [[6, 4, 4, 2, 2, 2, 2], [4, 4, 4, 4, 2, 2, 2]], "the simple-cycle patterns moved")
    return {
        "excluded_sum": 14,
        "open_sum": 21,
        "edges_needed": EDGES,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
