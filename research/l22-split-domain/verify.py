#!/usr/bin/env python3
"""Eleven length-22 splits survive, and nine survive the 17-point import.

The checker evaluates the budgets. It does not census words.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_L22_SPLIT_DOMAIN representatives=11 after_import=9 no_new_kappa"
EXPECTED = (
    ((11, 11), 22, 0, 47, 29, 121),
    ((11, 10), 21, 1, 37, 23, 110),
    ((11, 9), 20, 2, 28, 18, 99),
    ((10, 10), 20, 2, 27, 18, 100),
    ((11, 8), 19, 3, 20, 12, 88),
    ((10, 9), 19, 3, 18, 13, 90),
    ((11, 7), 18, 4, 13, 7, 77),
    ((10, 8), 18, 4, 10, 8, 80),
    ((9, 9), 18, 4, 9, 9, 81),
    ((11, 6), 17, 5, 7, 1, 66),
    ((10, 7), 17, 5, 3, 3, 70),
)


def fail(message):
    raise SystemExit("FAIL_L22_SPLIT_DOMAIN " + message)


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


def masks(labels):
    return 1 << (labels - 1)


def even_budget(large, small, labels):
    return large * (large - 1) // 2 + small * (small - 1) // 2 - (masks(labels) - 1)


def identity_need(large, small, labels):
    excess = large * small - masks(labels)
    if excess <= 0:
        return 0
    return (excess + 1) // 2


def passes(large, small, labels, length):
    budget = even_budget(large, small, labels)
    need = identity_need(large, small, labels)
    upper = budget + budget * budget // 4 if budget > 0 else budget
    return (
        large <= length // 2 and small <= length // 2
        and large * small >= masks(labels)
        and budget >= 0
        and upper >= need
    )


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require(masks(7) == 64, "the mask count moved")
    rows = []
    for small in range(1, 22):
        for large in range(small, 22):
            budget = even_budget(large, small, 7)
            need = identity_need(large, small, 7)
            upper = budget + budget * budget // 4 if budget > 0 else budget
            require(not (budget <= 0 and upper >= need), "a nonpositive even budget passed")
            if passes(large, small, 7, 22):
                rows.append((
                    (large, small),
                    large + small,
                    22 - (large + small),
                    budget,
                    need,
                    large * small,
                ))
    rows.sort(key=lambda row: (-row[1], -row[0][0]))
    require(tuple(rows) == EXPECTED, "the length-22 table moved")
    require(sum(row[2] == 0 for row in rows) == 1 and rows[0][0] == (11, 11), "self-avoidance moved")
    require(not passes(13, 5, 7, 22) and not passes(12, 6, 7, 22), "a time-bound split survived")
    require(even_budget(9, 8, 7) == 1 and identity_need(9, 8, 7) == 4 and not passes(9, 8, 7, 22), "the pair identity moved")
    floor = None
    for size in range(1, 24):
        survivors = []
        for large in range((size + 1) // 2, size):
            small = size - large
            if small < 1:
                continue
            budget = even_budget(large, small, 7)
            need = identity_need(large, small, 7)
            upper = budget + budget * budget // 4 if budget > 0 else budget
            if large * small >= 64 and budget >= 0 and upper >= need:
                survivors.append((large, small))
        if survivors:
            floor = (size, tuple(sorted(survivors)))
            break
    require(floor == (17, ((10, 7), (11, 6))), "the covering floor moved")
    remaining = [row[0] for row in rows if row[0] not in {(11, 6), (10, 7)}]
    require(len(rows) == 11 and len(remaining) == 9, "the imported count moved")
    return {
        "representatives": 11,
        "after_import": 9,
        "covering_floor": 17,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
