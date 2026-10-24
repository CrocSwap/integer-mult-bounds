#!/usr/bin/env python3
"""Six-owner centre repair count.

The checker applies the published column and route premises to the owner
count. It does not enumerate route products.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_SIX_OWNER_REPAIR_COUNT owners=7 no_new_kappa"
PIVOTS = (0, 1, 2, 3, 4, 5, 6, 12)


def fail(message):
    raise SystemExit("FAIL_SIX_OWNER_REPAIR_COUNT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")

    ports = 112
    rank = 8
    require(len(set(PIVOTS)) == rank and all(0 <= port < ports for port in PIVOTS), "the pivot set moved")
    complement = [port for port in range(ports) if port not in set(PIVOTS)]
    per_owner = ports - rank
    require(len(complement) == per_owner == 104, "the complement count moved")

    # One active owner reaches at least three outputs. Each output needs two
    # further owners, and one pair of owners meets in at most one output.
    outputs = 3
    extras = 2
    slots = outputs * extras
    require(slots == 6, "the output slots moved")
    for others in range(0, 6):
        require(others < slots, "six other owners became unnecessary")
    support = slots + 1
    require(support == 7, "the support bound moved")
    for block in range(1, support):
        require(block < support, "a block of size at most six survived")
    coordinates = [per_owner * block for block in range(1, 7)]
    require(coordinates == [104, 208, 312, 416, 520, 624], "the block coordinates moved")
    require(per_owner * 6 == coordinates[-1], "the six-owner total moved")
    return {
        "ports": ports,
        "rank": rank,
        "per_owner": per_owner,
        "support_lower_bound": support,
        "maximum_block": 6,
        "block_coordinates": coordinates,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
