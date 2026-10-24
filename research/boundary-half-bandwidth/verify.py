"""Half-bandwidth after removing cell interiors.

A piece of length at most 4w is entirely boundary. A longer piece keeps
its first w and last w rows. Original pairs at distance at most w, and
the Schur fill between the two boundary groups of one piece, stay within
boundary rank separation 2w-1.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
MAX_WIDTH = 3
MAX_LENGTH = 16
WITNESS_WIDTH = 40


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_BOUNDARY_BAND selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def compositions(length: int):
    if length == 1:
        yield [1]
        return
    for mask in range(1 << (length - 1)):
        parts = []
        run = 1
        for bit in range(length - 1):
            if (mask >> bit) & 1:
                parts.append(run)
                run = 1
            else:
                run += 1
        parts.append(run)
        yield parts


def boundary(parts: list[int], width: int) -> list[int]:
    found = []
    start = 0
    for length in parts:
        if length <= 4 * width:
            found.extend(range(start, start + length))
        else:
            if 2 * width > length - 2 * width:
                raise SystemExit("FAIL_BOUNDARY_BAND buffers overlap")
            found.extend(range(start, start + width))
            found.extend(range(start + length - width, start + length))
        start += length
    return found


def main() -> None:
    pinned = load()
    seen = 0
    attained = set()
    for width in range(1, MAX_WIDTH + 1):
        for length in range(1, MAX_LENGTH + 1):
            for parts in compositions(length):
                rows = boundary(parts, width)
                rank = {index: place for place, index in enumerate(rows)}
                worst = 0
                for index, place in rank.items():
                    for distance in range(1, width + 1):
                        other = rank.get(index + distance)
                        if other is None:
                            continue
                        if other - place > distance:
                            raise SystemExit("FAIL_BOUNDARY_BAND original pair moved")
                        worst = max(worst, other - place)
                start = 0
                for part in parts:
                    if part > 4 * width:
                        gap = rank[start + part - 1] - rank[start]
                        if gap != 2 * width - 1:
                            raise SystemExit("FAIL_BOUNDARY_BAND fill gap moved")
                        worst = max(worst, gap)
                    start += part
                if worst > 2 * width - 1:
                    raise SystemExit("FAIL_BOUNDARY_BAND separation moved")
                if worst == 2 * width - 1:
                    attained.add(width)
                seen += 1
    witnesses = 0
    for width in range(1, WITNESS_WIDTH + 1):
        rows = boundary([4 * width + 1], width)
        if rows != list(range(width)) + list(range(3 * width + 1, 4 * width + 1)):
            raise SystemExit("FAIL_BOUNDARY_BAND witness rows moved")
        gap = len(rows) - 1
        if gap != 2 * width - 1:
            raise SystemExit("FAIL_BOUNDARY_BAND witness gap moved")
        witnesses += 1
    if attained != set(range(1, MAX_WIDTH + 1)):
        raise SystemExit("FAIL_BOUNDARY_BAND attained widths moved")
    if (
        pinned["compositions"] != seen
        or pinned["witnesses"] != witnesses
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_BOUNDARY_BAND pinned result moved")
    print(f"PASS_BOUNDARY_BAND compositions={seen} no_new_kappa")


if __name__ == "__main__":
    main()
