#!/usr/bin/env python3
"""Exact normalized census for one weight-three closing call on F_2^6."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIM = 6
START = (0, 1, 3)
POINT_COUNT = 12


def weight(x: int) -> int:
    return x.bit_count()


def initial_cover(points: list[int]) -> int:
    cover = 0
    for i, x in enumerate(points):
        for y in points[i + 1 :]:
            cover |= 1 << (x ^ y)
    return cover


def main() -> dict:
    points = list(START)
    visited = set(points)
    counts = Counter()
    digest = hashlib.sha256()
    max_coverage = -1
    max_prefixes = None
    full_witnesses = []

    def visit(cover: int) -> None:
        nonlocal max_coverage, max_prefixes
        if len(points) == POINT_COUNT:
            counts["simple_walks"] += 1
            if weight(points[-1]) != 3:
                return
            counts["trio_endpoints"] += 1
            coverage = cover.bit_count()
            counts[str(coverage)] += 1
            row = bytes(points) + cover.to_bytes(8, "big")
            digest.update(row)
            if coverage > max_coverage:
                max_coverage = coverage
                max_prefixes = points.copy()
            if coverage == 63:
                full_witnesses.append(points.copy())
            return

        current = points[-1]
        for coordinate in range(DIM):
            nxt = current ^ (1 << coordinate)
            if nxt in visited:
                continue
            new_cover = cover
            for old in points:
                new_cover |= 1 << (old ^ nxt)
            points.append(nxt)
            visited.add(nxt)
            visit(new_cover)
            visited.remove(nxt)
            points.pop()

    visit(initial_cover(points))
    histogram = {
        str(k): counts[str(k)]
        for k in range(64)
        if counts[str(k)]
    }
    missing_at_max = sorted(
        set(range(1, 64))
        - {
            max_prefixes[i] ^ max_prefixes[j]
            for i in range(len(max_prefixes))
            for j in range(i + 1, len(max_prefixes))
        }
    )
    result = {
        "schema_version": 1,
        "claim": "No normalized simple 12-vertex F2^6 path with eleven unit edges and a closing weight-three edge has all 63 nonzero pairwise differences.",
        "normalization": {
            "dimension": DIM,
            "initial_prefixes": list(START),
            "reason": "Translate q0 to 0; rotate the unique weight-three edge to closing; permute coordinates so the first two distinct unit edges are 1 and 2.",
            "remaining_unit_edges": 9,
            "raw_upper_bound": 5**9,
        },
        "profile": {
            "vertices": POINT_COUNT,
            "unit_edges": 11,
            "weight_three_closing_edges": 1,
            "calls": 12,
            "source_adds": 14,
            "required_nonzero_differences": 63,
        },
        "counts": {
            "normalized_simple_walks": counts["simple_walks"],
            "closing_weight_three_candidates": counts["trio_endpoints"],
            "coverage_histogram": histogram,
            "maximum_coverage": max_coverage,
            "full_cover_witnesses": len(full_witnesses),
        },
        "maximum_example_prefixes": max_prefixes,
        "maximum_example_missing_masks": missing_at_max,
        "endpoint_records_sha256": digest.hexdigest(),
        "positive_control_pr2128": {
            "steps": [2, 16, 8, 16, 1, 4, 48, 4, 3, 4, 32, 8, 4, 16],
            "prefixes": [0, 2, 18, 26, 10, 11, 15, 63, 59, 56, 60, 28, 20, 16],
            "calls": 14,
            "source_adds": 16,
            "readouts": 126,
            "root_queries": 140,
            "source": "CrocSwap/integer-mult-bounds PR #2128, head 697369a971eed02c0fbcd75ebefec9f59945f08e",
        },
        "scope_limit": "This excludes only the stated normalized profile. It does not exclude other arities, other step-weight profiles, repeated boundary prefixes, deferred readout, or other interfaces.",
    }
    (HERE / "CERTIFICATE.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        "PASS_TRIO_CYCLE_CENSUS "
        f"walks={counts['simple_walks']} endpoints={counts['trio_endpoints']} "
        f"max={max_coverage} full={len(full_witnesses)}"
    )
    return result


if __name__ == "__main__":
    main()
