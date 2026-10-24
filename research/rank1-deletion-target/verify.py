#!/usr/bin/env python3
"""The rank-1 deletion still misses the planning target a = 1/99.

The selected local word pays 2,412 rank-1 children. This checker removes
them, keeps the other ranks, and evaluates the published relaxation. It
does not search a new packing.
"""

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_RANK1_DELETION_TARGET moment_above_one=true no_new_kappa"
LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
from ceiling import ceiling, relax  # noqa: E402


def fail(message):
    raise SystemExit("FAIL_RANK1_DELETION_TARGET " + message)


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
    expected = {
        "research/complex-local-word-ceiling/README.md",
        "research/complex-local-word-ceiling/ceiling.py",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    note = (ROOT / "research/complex-local-word-ceiling/README.md").read_text(encoding="utf-8")
    require(
        "**Even deleting all 2,412 rank-1\n"
        "children per call, with everything else fixed, cannot reach it.**" in note,
        "the deletion sentence moved",
    )
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    kappa = Fraction(selected["kappa"])
    require(kappa == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    local_mass = sum(rank * count for rank, count in LOCAL.items())
    require(local_mass == 5586, "the local mass moved")
    deleted = {rank: count for rank, count in LOCAL.items() if rank != 1}
    deleted_mass = sum(rank * count for rank, count in deleted.items())
    require(deleted_mass == 3174 and 7232 - deleted_mass == 4058, "the idle mass moved")
    require(2 * 51 * 51 < 73 * 73 <= 2 * 52 * 52, "the idle-rank cap moved")
    target = Fraction(1, 99)
    full = relax(LOCAL, 73, 896, 9, 64, target)
    reduced = relax(deleted, 73, 896, 9, 64, target)
    require(reduced[0] > 1, "the deleted word meets the target")
    require(full[0] > reduced[1], "deleting rank 1 did not lower the moment")
    cap = ceiling(LOCAL, 73, 896, 9, 64, grid=Fraction(1, 10**12))
    require(cap[1] == Fraction(169005411, 100000000000), "the packing cap moved")
    saving = kappa / (1 - kappa)
    require(saving < cap[1], "the selected saving meets the cap")
    return {
        "rank1_children": 2412,
        "idle_after_deletion": 4058,
        "idle_rank": 51,
        "ceiling_hi": "169005411/100000000000",
        "deleted_moment_above_one": True,
        "selected_below_ceiling": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
