#!/usr/bin/env python3
"""Set-valued recomputation of the F_2^6 difference-basis witnesses and the
twelve-point census. Does not import verify.py. Apache-2.0.
"""

from __future__ import annotations

import math
from itertools import combinations

BASIS = (1, 2, 4, 8, 16, 32)
REST = tuple(i for i in range(1, 64) if i not in BASIS)
WITNESS12 = (1, 2, 4, 8, 16, 32, 3, 28, 45, 54, 59)
WITNESS13 = (1, 2, 4, 8, 16, 32, 3, 5, 30, 46, 54, 57)
WITNESS14 = (1, 2, 4, 8, 16, 32, 3, 5, 6, 24, 40, 48, 63)


def require(ok: bool, why: str) -> None:
    if not ok:
        raise SystemExit("FAIL: " + why)


def nonzero_sums(pts: tuple[int, ...]) -> set[int]:
    found: set[int] = set()
    for i, a in enumerate(pts):
        found.add(a)
        for b in pts[i + 1 :]:
            found.add(a ^ b)
    found.discard(0)
    return found


def main() -> None:
    require(len(nonzero_sums(WITNESS12)) == 57, "witness 12")
    require(63 not in nonzero_sums(WITNESS13) and len(nonzero_sums(WITNESS13)) == 62, "witness 13")
    require(nonzero_sums(WITNESS14) == set(range(1, 64)), "witness 14")

    hits = 0
    best = 0
    n = 0
    target = set(range(1, 64))
    for extra in combinations(REST, 5):
        found = nonzero_sums(BASIS + extra)
        best = max(best, len(found))
        if found == target:
            hits += 1
        n += 1
    require(n == math.comb(57, 5) == 4187106, "visit count")
    require(hits == 0 and best == 57, "independent twelve-point census")

    # Order 4 is impossible in F_2^3 by the pair count, and order 5 occurs.
    basis3 = (1, 2, 4)
    require(len(nonzero_sums(basis3)) == 6, "F_2^3 order 4 misses a mask")
    require(any(nonzero_sums(basis3 + (extra,)) == set(range(1, 8)) for extra in (3, 5, 6, 7)), "F_2^3 order 5")
    print("PASS_F2_SIX_DIFFERENCE_BASIS_INDEPENDENT hits12=0 best12=57 order14=1")


if __name__ == "__main__":
    main()
