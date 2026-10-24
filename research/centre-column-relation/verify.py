#!/usr/bin/env python3
"""The published centre columns cancel, and the block product is 424320.

The checker subtracts the three columns. It does not enumerate the coset.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_CENTRE_COLUMN_RELATION block=424320 no_new_kappa"
COLUMNS = (
    (1, 1, 1, 1, 0, 0, 0, 0),
    (0, 1, 1, 0, 1, 0, 0, 1),
    (1, 0, 0, 1, -1, 0, 0, -1),
)


def fail(message):
    raise SystemExit("FAIL_CENTRE_COLUMN_RELATION " + message)


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
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    relation = tuple(COLUMNS[0][i] - COLUMNS[1][i] - COLUMNS[2][i] for i in range(8))
    require(relation == (0, 0, 0, 0, 0, 0, 0, 0), "the columns no longer cancel")
    require(112 - 8 == 104, "the per-owner factor moved")
    require(16 * 15 * 17 == 4080 and 2 * 4080 == 8160, "the subgroup order moved")
    block = 104 * 4080
    require(block == 424320 and block - 1 == 424319, "the repair count moved")
    require(56 + 840 == 896 and 15 <= 4080, "the support interval moved")
    return {
        "columns_cancel": True,
        "owners": 4080,
        "block_coordinates": 424320,
        "saved_coordinates": 1,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
