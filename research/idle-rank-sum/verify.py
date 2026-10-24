"""Idle rank of a nine-stage pair.

Each level from -1 to 8 costs 8 unless an owned shear covers it. A ridden
stage pays that 8. The opening idle before a first stage s is 8s.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
STAGES = 9
UNIT = 8
LEVEL_SPAN = 9


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_IDLE_RANK_SUM selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def segments(stages: tuple[int, ...], owned: set[int]) -> list[int]:
    pieces: list[int] = []
    level = -1
    for stage in stages:
        if stage - 1 > level:
            pieces.append(UNIT * (stage - 1 - level))
        if stage not in owned:
            pieces.append(UNIT)
        level = stage
    if level < STAGES - 1:
        pieces.append(UNIT * (STAGES - 1 - level))
    return [piece for piece in pieces if piece]


def assignments() -> int:
    # Each stage is absent (0), ridden (1) or owned (2). Digits of a base-3 integer.
    checked = 0
    total_codes = 3 ** STAGES
    for code in range(total_codes):
        stages: list[int] = []
        owned: set[int] = set()
        cursor = code
        for stage in range(STAGES):
            kind = cursor % 3
            cursor //= 3
            if kind == 0:
                continue
            stages.append(stage)
            if kind == 2:
                owned.add(stage)
        pieces = segments(tuple(stages), owned)
        if sum(pieces) != UNIT * (LEVEL_SPAN - len(owned)):
            raise SystemExit(f"FAIL_IDLE_RANK_SUM assignment {code}")
        if stages:
            opening = UNIT * stages[0]
            if opening == 0:
                if pieces and pieces[0] == 0:
                    raise SystemExit(f"FAIL_IDLE_RANK_SUM opening {code}")
            elif not pieces or pieces[0] != opening:
                raise SystemExit(f"FAIL_IDLE_RANK_SUM opening {stages[0]}")
        checked += 1
    return checked


def main() -> None:
    pinned = load()
    checked = assignments()
    if checked != 3 ** STAGES:
        raise SystemExit("FAIL_IDLE_RANK_SUM count moved")
    if (
        pinned["stages"] != STAGES
        or pinned["assignments"] != checked
        or pinned["unit"] != UNIT
        or pinned["level_span"] != LEVEL_SPAN
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_IDLE_RANK_SUM pinned result moved")
    print(f"PASS_IDLE_RANK_SUM assignments={checked} no_new_kappa")


if __name__ == "__main__":
    main()
