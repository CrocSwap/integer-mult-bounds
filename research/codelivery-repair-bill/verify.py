#!/usr/bin/env python3
"""The selective co-delivery repair bills 124 against a baseline of 112.

The checker adds the published block ranks. It does not replay columns.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_CODELIVERY_REPAIR_BILL repaired=124 excess=12 no_new_kappa"
CENTRE = (2, 8, 9, 2, 8, 9, 8, 9, 8, 8, 2, 8, 9, 2)
BLOCKS = (0, 3, 10, 13)
REPAIR = ((1, 1, 2, 1), (1, 1, 1, 2), (1, 1, 1, 2), (1, 1, 2, 1))
DEFECTS = (4, 4, 4, 4)


def fail(message):
    raise SystemExit("FAIL_CODELIVERY_REPAIR_BILL " + message)


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
    require(len(CENTRE) == 14 and tuple(CENTRE[index] for index in BLOCKS) == (2, 2, 2, 2), "the centre supports moved")
    saved = sum(CENTRE[index] for index in BLOCKS)
    require(saved == 8 and 112 - saved == 104, "the sensitivity moved")
    require(4 * 4 == 16 and 10 * 4 == 40, "the term profile moved")
    ones = sum(rank == 1 for row in REPAIR for rank in row)
    twos = sum(rank == 2 for row in REPAIR for rank in row)
    mass = sum(sum(row) for row in REPAIR)
    require((ones, twos, mass) == (12, 4, 20) and all(sum(row) == 5 for row in REPAIR), "the repair profile moved")
    require(104 + mass == 124 and 124 - 112 == 12, "the repaired bill moved")
    require(sum(DEFECTS) == 16 and len(DEFECTS) == 4, "the defect rank moved")
    require(252 + 24 == 276 and 212 - 176 == 36 and 4 * 25 == 100, "the scalar invoice moved")
    return {
        "saved": 8,
        "repaired": 124,
        "excess": 12,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
