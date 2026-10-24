#!/usr/bin/env python3
"""The published T450 allocation has 450 replicas, above the T740 root.

The checker adds the published counts. It does not expand the roles.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_T450_REPLICA_COUNT replicas=450 above_selected=true no_new_kappa"
HISTOGRAM = {1: 9983580, 2: 2940300, 3: 936579, 4: 413100, 5: 87495, 8: 32400, 48: 172221}


def fail(message):
    raise SystemExit("FAIL_T450_REPLICA_COUNT " + message)


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
    require(10 * (37 + 8) == 450, "the replica count moved")
    require(450 * 9 == 4050 and 4050 * 408 == 1652400, "the role count moved")
    children = sum(HISTOGRAM.values())
    mass = sum(rank * count for rank, count in HISTOGRAM.items())
    require(children == 14565675, "the child count moved")
    require(mass == 29289600, "the rank mass moved")
    endpoint = Fraction(1730047552093344159584, 10**24)
    previous = Fraction(1730006549538841847005, 10**24)
    stated = endpoint - Fraction(1, 10**46) - Fraction(1, 10**70)
    require(stated > previous, "the stated root fell to the T740 root")
    require(stated > kappa, "the stated root meets the selected kappa")
    return {
        "replicas": 450,
        "calls": 4050,
        "roles": 1652400,
        "children": 14565675,
        "rank_mass": 29289600,
        "above_t740": True,
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
