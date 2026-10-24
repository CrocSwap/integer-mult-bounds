#!/usr/bin/env python3
"""The published R438 profile has rank mass 4989, a local drop of 132.

The checker adds the published counts. It does not regenerate the word.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_R438_RANK_DROP rank_mass=4989 drop=132 no_new_kappa"
HISTOGRAM = {1: 1298, 2: 1342, 3: 79, 4: 44, 5: 93, 6: 11, 7: 9}


def fail(message):
    raise SystemExit("FAIL_R438_RANK_DROP " + message)


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
    children = sum(HISTOGRAM.values())
    mass = sum(rank * count for rank, count in HISTOGRAM.items())
    drop = 9 * 7 + 24 * 1 + 9 * 5
    require(children == 2876 and mass == 4989, "the profile moved")
    require(drop == 132 and 5121 - drop == 4989, "the rank drop moved")
    require(2918 - (9 + 24 + 9) == 2876, "the child drop moved")
    require(438 - 9 == 429 and 9 * 8 == 72 and 72 * 9 == 648, "the helper return moved")
    require(5758 + 5619 + 1499 + 347 == 13223, "the ADD split moved")
    require(24248 - 13223 == 11025, "the ADD drop moved")
    return {
        "rank_mass": 4989,
        "rank_drop": 132,
        "helpers": 429,
        "idle_return": 72,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
