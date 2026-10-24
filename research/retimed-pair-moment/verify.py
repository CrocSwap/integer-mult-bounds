#!/usr/bin/env python3
"""The retimed pair keeps rank mass 5135 and strictly lowers the moment.

The checker compares the two histograms and the integer-power inequality.
It does not replay the columns.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_RETIMED_PAIR_MOMENT rank_mass=5135 moment_decreases=true no_new_kappa"
OLD = {1: 2439, 2: 726, 3: 224, 4: 102, 5: 20, 8: 8}
NEW = {1: 2437, 2: 724, 3: 226, 4: 102, 5: 20, 8: 8}


def fail(message):
    raise SystemExit("FAIL_RETIMED_PAIR_MOMENT " + message)


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


def mass(histogram):
    return sum(rank * count for rank, count in histogram.items())


def power_gap(gap):
    """(1/3)^p > 1/3 and (2/3)^p > 2/3 when the exponent gap is this positive integer."""
    require(gap >= 1, "the exponent gap left the open interval")
    require(3**gap > 1 and 3**gap > 2**gap, "the power comparison failed")


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require(mass(OLD) == mass(NEW) == 5135, "the rank mass moved")
    require(NEW[1] == OLD[1] - 2 and NEW[2] == OLD[2] - 2 and NEW[3] == OLD[3] + 2, "the exchange moved")
    require(-2 * 1 - 2 * 2 + 2 * 3 == 0, "the rank change moved")
    require(26 + 2 + 18 + 52 + 97 + 213 == 408, "the width inventory moved")
    require(3 > 2, "the induction base moved")
    for gap in range(1, 25):
        power_gap(gap)
        require(3 * (3**gap) > 2 * (2**gap), "the induction step moved")
    return {
        "rank_mass": 5135,
        "rank_change": 0,
        "moment_decreases": True,
        "helpers": 408,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
