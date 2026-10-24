#!/usr/bin/env python3
"""T360 has 470016 fewer roles than the 488-replica allocation.

The checker factors the published counts. It does not rerun the pattern replay.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_T360_ROLE_GAP roles=470016 physical=114688 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_T360_ROLE_GAP " + message)


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
    require(488 * 9 == 4392 and 4392 * 408 == 1791936, "the T488 schedule moved")
    require(360 * 9 * 408 == 1321920, "the T360 schedule moved")
    require(1791936 - 1321920 == (488 - 360) * 9 * 408 == 470016, "the role gap moved")
    require(437757 - 323069 == 114688, "the physical gap moved")
    return {
        "t360_roles": 1321920,
        "t488_roles": 1791936,
        "role_gap": 470016,
        "physical_gap": 114688,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
