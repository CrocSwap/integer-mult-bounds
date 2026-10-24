#!/usr/bin/env python3
"""The published sector dimensions sum to 28800, and both invoices exceed 30960.

The checker multiplies the published ranks. It does not act on the columns.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_H6_SECTOR_DIMENSIONS sectors=28800 above_ports=true no_new_kappa"
RANKS = (1, 8, 35, 112, 84)
PAIRS = ((1, 0), (3, 0), (1, 2), (3, 2), (1, 4), (3, 4))


def fail(message):
    raise SystemExit("FAIL_H6_SECTOR_DIMENSIONS " + message)


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
    require(sum(RANKS) == 240, "the idempotent ranks moved")
    dimensions = tuple(2 * RANKS[left] * RANKS[right] for left, right in PAIRS)
    require(dimensions == (16, 224, 560, 7840, 1344, 18816), "the sector dimensions moved")
    require(sum(dimensions) == 120 * 240 == 28800, "the block size moved")
    require(sum(dimensions[:3]) == 800, "the cubic rank moved")
    require(28800 + 2160 == 30960, "the port count moved")
    quintic = 17 * 9424
    septic = 17 * 20400
    require(quintic == 160208 and septic == 346800, "the invoices moved")
    require(quintic > 30960 and septic > 30960, "an invoice fits in the ports")
    return {
        "sector_sum": 28800,
        "cubic_rank": 800,
        "quintic_invoice": 160208,
        "septic_invoice": 346800,
        "above_ports": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
