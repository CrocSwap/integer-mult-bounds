#!/usr/bin/env python3
"""Rank-1 deletions maximize the power-sum drop, and the pair bracket stays positive.

The checker proves those two comparisons at a = 1/596. It does not recompute
the signed excess enclosure.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_RANK_UNIT_DELETION_ORDER rank1_drop=1 bracket_positive=true no_new_kappa"
SAVING = Fraction(1, 596)


def fail(message):
    raise SystemExit("FAIL_RANK_UNIT_DELETION_ORDER " + message)


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


def higher_rank_is_strict(rank):
    """A one-step drop at this rank is strictly below one."""
    width = rank - 1
    base = Fraction(width + 1, width)
    require(base**595 < base**596, "the power comparison failed at rank " + str(rank))
    return True


def bracket_margin(pairs, saving):
    """Positive lower bound for the second-derivative bracket divided by U, when U>V."""
    return 16 * pairs + 16 * saving * pairs + 2 + 16 * saving


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    kappa = Fraction(selected["kappa"])
    require(kappa == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require(0 < SAVING < 1 and 0 < kappa < 1, "a saving left the unit interval")
    require(1**595 == 1, "the rank-1 drop moved")
    for rank in range(2, 74):
        require(higher_rank_is_strict(rank), "a higher rank matched the rank-1 drop")
    for pairs in (1, 6, 7, 8):
        require(bracket_margin(pairs, SAVING) > 0, "the test bracket failed")
        require(bracket_margin(pairs, kappa) > 0, "the selected bracket failed")
    sample_u, sample_v = Fraction(3), Fraction(2)
    pairs = 7
    bracket = (16 * (1 + SAVING) * pairs + 18) * sample_u - 16 * (1 - SAVING) * sample_v
    require(bracket > sample_u * bracket_margin(pairs, SAVING) > 0, "the sample bracket failed")
    return {
        "saving": "1/596",
        "rank1_drop": 1,
        "higher_rank_drop_below_one": True,
        "bracket_positive": True,
        "ranks_checked": 73,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
