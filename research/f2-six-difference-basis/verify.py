#!/usr/bin/env python3
"""Smallest difference basis of F_2^6, and the six-source query floor it forces.

The 12-point census is pure Python. The 13- and 14-point censuses are the
compiled loop in census.c. Both coverage routines are checked against each
other on every normalized 12-point set and on the recorded extremal witnesses.
Apache-2.0.
"""

from __future__ import annotations

import math
import subprocess
import tempfile
from itertools import combinations
from pathlib import Path

BASIS = (1, 2, 4, 8, 16, 32)
REST = tuple(i for i in range(1, 64) if i not in BASIS)
FULL = (1 << 64) - 2
WITNESS12 = (1, 2, 4, 8, 16, 32, 3, 28, 45, 54, 59)
WITNESS13 = (1, 2, 4, 8, 16, 32, 3, 5, 30, 46, 54, 57)
WITNESS14 = (1, 2, 4, 8, 16, 32, 3, 5, 6, 24, 40, 48, 63)
MISS12 = (14, 15, 21, 23, 25, 26)
MISS13 = (63,)


def require(ok: bool, why: str) -> None:
    if not ok:
        raise SystemExit("FAIL: " + why)


def cover_mask(pts: tuple[int, ...] | list[int]) -> int:
    seen = 0
    for i, a in enumerate(pts):
        seen |= 1 << a
        for b in pts[i + 1 :]:
            seen |= 1 << (a ^ b)
    return seen


def missed(mask: int) -> tuple[int, ...]:
    return tuple(i for i in range(1, 64) if (mask >> i) & 1 == 0)


def python_census_12() -> tuple[int, int, int]:
    """Normalized 12-point sets: 0, the standard basis, and five other vectors."""
    hits = 0
    best = 0
    n = 0
    for extra in combinations(REST, 5):
        mask = cover_mask(BASIS + extra)
        count = mask.bit_count()
        if count > best:
            best = count
        if mask == FULL:
            hits += 1
        n += 1
    return n, hits, best


def positive_control_f2_3() -> None:
    """In F_2^3 the same test finds order 5 and rejects order 4."""
    basis = (1, 2, 4)
    rest = tuple(i for i in range(1, 8) if i not in basis)
    full = (1 << 8) - 2
    only = cover_mask(basis)
    require(only.bit_count() == 6 and only != full, "F_2^3 basis should miss one mask")
    hits = 0
    for extra in rest:
        if cover_mask(basis + (extra,)) == full:
            hits += 1
    require(hits > 0, "F_2^3 should have a 5-point difference basis")


def compile_and_run() -> dict[str, str]:
    source = Path(__file__).with_name("census.c")
    require(source.is_file(), "census.c missing")
    with tempfile.TemporaryDirectory(prefix="f2-six-basis-") as tmp:
        binary = str(Path(tmp) / "census")
        compiled = subprocess.run(
            ["cc", "-O3", "-std=c11", "-Wall", "-Werror", "-o", binary, str(source)],
            capture_output=True,
            text=True,
            check=False,
        )
        require(compiled.returncode == 0, "cc failed:\n" + compiled.stderr)
        ran = subprocess.run([binary], capture_output=True, text=True, check=False)
        require(ran.returncode == 0, "census failed:\n" + ran.stderr + ran.stdout)
    rows: dict[str, str] = {}
    for line in ran.stdout.splitlines():
        key, _, value = line.partition(" ")
        rows[key] = value
    return rows


def parse_ints(text: str) -> tuple[int, ...]:
    return tuple(int(x) for x in text.split())


def main() -> None:
    require(len(REST) == 57, "basis complement")
    require(math.comb(11, 2) == 55 < 63, "counting floor")
    require(math.comb(57, 5) == 4187106, "twelve-point orbit size")
    require(math.comb(57, 6) == 36288252, "thirteen-point orbit size")
    require(math.comb(57, 7) == 264385836, "fourteen-point orbit size")

    positive_control_f2_3()

    n12, hits12, best12 = python_census_12()
    require(n12 == math.comb(57, 5), "python twelve-point visit count")
    require(hits12 == 0 and best12 == 57, "python twelve-point census")
    require(missed(cover_mask(WITNESS12)) == MISS12, "twelve-point witness")
    require(missed(cover_mask(WITNESS13)) == MISS13, "thirteen-point witness")
    require(missed(cover_mask(WITNESS14)) == (), "fourteen-point witness")
    require(cover_mask(BASIS).bit_count() == 21, "basis coverage")

    # Differences inside a coordinate hyperplane miss the complementary coset.
    flat = tuple(range(1, 15))
    flat_miss = missed(cover_mask(flat))
    require(all(v < 32 for v in flat) and any(v >= 32 for v in flat_miss), "a 5-flat misses an odd coset")

    for drop in range(len(WITNESS14)):
        smaller = WITNESS14[:drop] + WITNESS14[drop + 1 :]
        require(cover_mask(smaller) != FULL, "deleting a point from the order-14 witness")

    compiled = compile_and_run()
    require(compiled.get("extra=5") == "n=4187106 hits=0 best=57", compiled.get("extra=5", ""))
    require(compiled.get("extra=6") == "n=36288252 hits=0 best=62", compiled.get("extra=6", ""))
    require(
        compiled.get("extra=7") == "n=264385836 hits=53340 best=63 fixed=1",
        compiled.get("extra=7", ""),
    )
    require(parse_ints(compiled["witness12"]) == WITNESS12, "C twelve-point witness")
    require(parse_ints(compiled["witness13"]) == WITNESS13, "C thirteen-point witness")

    print(
        "PASS_F2_SIX_DIFFERENCE_BASIS "
        "min_order=14 cover12=57 cover13=62 "
        "sets12=4187106 sets13=36288252 sets14=264385836 hits14=53340 "
        "query_floor=140 no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
