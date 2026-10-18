#!/usr/bin/env python3
"""Separate full-index bit-mask cover scan; no primary application routines."""

import itertools
from pathlib import Path

from verify import read_json, require, sources

ROOT = Path(__file__).resolve().parent


def scan(weights, first, second, cut, bound, residual):
    n = len(weights)
    sizes = (0, 0, 2, 4, 8, 12, 20, 36)
    count = 0
    for basis in range(1 << n):
        if basis.bit_count() != n - 6:
            continue
        indices = tuple(i for i in range(n) if basis & (1 << i))
        if sum(sizes[weights[i]] for i in indices) >= 53:
            continue
        extra = sum(w > residual for i, w in enumerate(weights) if not basis & (1 << i))
        if bound + extra >= 6:
            continue
        # These at-most-four selected pieces have at most16local subsets.
        for deleted in range(1 << len(indices)):
            point_indices = tuple(
                indices[k] for k in range(len(indices)) if deleted & (1 << k)
            )
            if sum(sizes[weights[i]] for i in point_indices) > cut:
                continue
            rest = tuple(i for i in indices if i not in point_indices)
            for left in range(1 << len(rest)):
                w_left = sum(weights[i] for k, i in enumerate(rest) if left & (1 << k))
                w_right = sum(
                    weights[i] for k, i in enumerate(rest) if not left & (1 << k)
                )
                count += w_left <= first and w_right <= second
    return count


def main():
    old = sources(ROOT)
    result = read_json(ROOT / "RESULT.json")
    rules = (
        ("alpha74", 7, 4, 0, 4, 7),
        ("beta7p2", 6, 6, 2, 4, 7),
        ("beta6p4", 6, 6, 4, 1, 6),
        ("beta6p8", 6, 6, 8, 3, 6),
    )
    require(len(old["rows"]) == len(result["rows"]) == 69, "row inventory")
    combined, new, remaining = 0, [], []
    for previous, row in zip(old["rows"], result["rows"], strict=True):
        w = tuple(previous["weights"])
        require(row["weights"] == list(w), "row identity")
        successes = []
        for name, a, b, cut, bound, residual in rules:
            number = scan(w, a, b, cut, bound, residual)
            require(
                number == row["attempts"][name]["count"], "independent assignment count"
            )
            successes.append(number > 0)
        covered = previous["primary"] is not None or any(successes)
        require(covered == row["covered"], "independent coverage")
        combined += covered
        if covered and previous["primary"] is None:
            new.append(list(w))
        if not covered:
            remaining.append(list(w))
    require(combined == result["combined"] == 65, "combined coverage")
    require(new == result["newly_accounted"] and len(new) == 3, "newly accounted")
    require(remaining == result["inventory_uncertified"], "remaining inventory")
    require(
        sum(
            1
            for n in range(6, 11)
            for _ in itertools.combinations_with_replacement(range(2, 8), n)
        )
        == 7546,
        "complete domain count",
    )
    print("PASS_INDEPENDENT_COVER_MASKS 276 exact assignment counts;65of69")


if __name__ == "__main__":
    main()
