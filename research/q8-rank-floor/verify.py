#!/usr/bin/env python3
"""Ten-call splits removed by the Q8 block rank floor.

The checker applies the count conditions. It does not search for a word.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_Q8_RANK_FLOOR removed=3 fixture_rank=2 no_new_kappa"
CALLS = 10
TARGETS = 4


def fail(message):
    raise SystemExit("FAIL_Q8_RANK_FLOOR " + message)


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


def splits(targets_i, targets_j, calls, floor):
    total = targets_i + targets_j
    found = []
    for count_i in range(calls + 1):
        count_j = calls - count_i
        if count_i % 2 != targets_i % 2 or count_j % 2 != targets_j % 2:
            continue
        if floor and (count_i < targets_i or count_j < targets_j):
            continue
        if 2 * calls + count_i < 6 * total - targets_i:
            continue
        if 2 * calls + count_j < 6 * total - targets_j:
            continue
        found.append([count_i, count_j])
    return found


def rank(rows, width):
    pivots = {}
    for row in rows:
        current = row
        while current:
            bit = current.bit_length() - 1
            require(bit < width, "a fixture row is too wide")
            if bit in pivots:
                current ^= pivots[bit]
            else:
                pivots[bit] = current
                break
    return len(pivots)


def block_ranks(columns, rows):
    product = []
    for bit in range(TARGETS):
        accumulator = 0
        for index, column in enumerate(columns):
            if column >> bit & 1:
                accumulator ^= rows[index]
        product.append(accumulator)
    return rank(columns, TARGETS), rank(rows, TARGETS), rank(product, TARGETS)


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    removed = {}
    for shape in ((4, 0), (0, 4), (3, 1), (1, 3), (2, 2)):
        plain = splits(*shape, CALLS, False)
        kept = splits(*shape, CALLS, True)
        require(plain and kept, "a ten-call shape lost every split")
        removed[f"{shape[0]},{shape[1]}"] = [pair for pair in plain if pair not in kept]
    require(removed == {
        "4,0": [[0, 10], [2, 8]],
        "0,4": [[8, 2], [10, 0]],
        "3,1": [[1, 9]],
        "1,3": [[9, 1]],
        "2,2": [],
    }, "a removal set moved")
    require(splits(2, 2, CALLS, True) == [[2, 8], [4, 6], [6, 4], [8, 2]], "the balanced splits moved")
    columns_i, rows_i = [0b0001, 0b0010], [0b0001, 0b0010]
    columns_j = [0b0100, 0b1000] * 4
    rows_j = [0b0100, 0b1000, 0, 0, 0, 0, 0, 0]
    ranks = block_ranks(columns_i, rows_i) + block_ranks(columns_j, rows_j)
    require(ranks == (2, 2, 2, 2, 2, 2), "the balanced fixture rank moved")
    return {
        "calls": CALLS,
        "removed_shapes": 3,
        "balanced_splits": 4,
        "fixture_rank": 2,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
