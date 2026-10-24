#!/usr/bin/env python3
"""Check finite facts used by the written clean-register reductions."""
from collections import Counter, defaultdict
from itertools import combinations_with_replacement, product
import json
from pathlib import Path


def outer(x, y, width):
    return sum(y << (width * i) for i in range(width) if x >> i & 1)


def require(value, message):
    if not value:
        raise ValueError(message)


def main():
    off4 = sum(1 << (4 * i + j) for i in range(3)
               for j in range(3) if i != j)
    all_projectors = [(x, y) for x in range(1, 16) for y in range(1, 16)
                      if (x & y).bit_count() % 2]
    zero = [(x, y) for x, y in all_projectors if not outer(x, y, 4) & off4]
    declared = {(1 << i, 1 << i) for i in range(3)}
    declared |= {(1 << i, 8 | (1 << i)) for i in range(3)}
    declared |= {(8 | (1 << i), 1 << i) for i in range(3)}
    declared |= {(8, 8 | v) for v in range(8)}
    declared |= {(8 | v, 8) for v in range(8)}
    require(len(all_projectors) == 120 and len(zero) == 24,
            "Projector counts")
    require(set(zero) == declared, "Projector alphabet")

    feasible = []
    for d in product(range(9), repeat=3):
        total = sum(d)
        if total > 8:
            continue
        for m in range((8 - total) // 2 + 1):
            for extra in combinations_with_replacement(range(1, 8), m):
                distance = [sum(d[i] for i in range(3) if w >> i & 1)
                            + sum((w & v).bit_count() % 2 for v in extra)
                            for w in range(1, 8)]
                if min(distance) >= 3:
                    feasible.append({"active_counts": d, "extra": extra})
    require(feasible == [{"active_counts": (2, 2, 2), "extra": (7,)}],
            "Distance multiplicity reduction")

    off3 = sum(1 << (3 * i + j) for i in range(3)
               for j in range(3) if i != j)
    patterns = defaultdict(list)
    for x, y in product(range(1, 8), repeat=2):
        pattern = outer(x, y, 3) & off3
        if pattern:
            patterns[pattern].append((x, y))
    types = Counter()
    for entries in patterns.values():
        if len(entries) == 1:
            types["unique"] += 1
        elif any(all(not (x | y) & (1 << i) for x, y in entries)
                 for i in range(3)):
            types["coordinate_plane"] += 1
        elif (len(entries) == 2
              and (any(all(x == 1 << i for x, y in entries) for i in range(3))
                   or any(all(y == 1 << i for x, y in entries) for i in range(3)))):
            types["coordinate_image_or_row"] += 1
        else:
            raise ValueError("Unclassified rank-one completion pattern")
    require(types == {"unique": 16, "coordinate_plane": 6,
                      "coordinate_image_or_row": 6}, "Completion counts")
    result = {"status": "PASS_INDEPENDENT_FINITE_REDUCTIONS",
              "all_rank_one_idempotents": len(all_projectors),
              "zero_active_off_pattern_projectors": len(zero),
              "distance_feasible_families": feasible,
              "active_rank_one_completion_patterns": dict(types)}
    Path(__file__).with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
