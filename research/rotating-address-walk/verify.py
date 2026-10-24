"""Six-stage rotating address walk.

Each stage reads one active axis as the normal, moves both banks onto the
complement, and then swaps which bank is the source. Fresh axes replace the
axes that leave the active core. After six stages the spectator has not
returned to the input axis.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
STAGES = 6


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_ROTATING_ADDRESS_WALK selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def walk() -> dict:
    frames = [1, 0]
    expressions = [{(0, 0)}, {(1, 0)}]
    active = list(range(8))
    exterior = 0
    high, low = 0, 1
    next_axis = 8
    profile: dict[int, int] = {}
    normals: list[int] = []

    def move(role: int, new: int) -> None:
        old = frames[role]
        if old & ~new:
            raise SystemExit("FAIL_ROTATING_ADDRESS_WALK nesting moved")
        difference = new ^ old
        if difference:
            profile[difference.bit_count()] = profile.get(difference.bit_count(), 0) + 1
            expressions[role] = {(bank, mask ^ difference) for bank, mask in expressions[role]}
            frames[role] = new

    for stage in range(STAGES):
        source, normal_index = stage % 2, 1 - stage % 2
        full = exterior
        for axis in active:
            full |= 1 << axis
        normal = active[normal_index]
        complement = full ^ (1 << normal)
        if frames[high] != exterior | (1 << active[source]) or frames[low] != exterior:
            raise SystemExit("FAIL_ROTATING_ADDRESS_WALK entrance moved")
        move(high, complement)
        move(low, complement)
        expressions[low] ^= expressions[high]
        move(low, full)
        high, low = low, high
        normals.append(normal)
        if stage != STAGES - 1:
            exterior = complement
            active = [normal if index == normal_index else -1 for index in range(8)]
            for index in range(8):
                if active[index] == -1:
                    active[index] = next_axis
                    next_axis += 1
    dimension = next_axis
    universe = (1 << dimension) - 1
    final = normals[-1]
    if expressions[0] != {(0, universe ^ 1)}:
        raise SystemExit("FAIL_ROTATING_ADDRESS_WALK first endpoint moved")
    if expressions[1] != {(1, universe ^ (1 << final))}:
        raise SystemExit("FAIL_ROTATING_ADDRESS_WALK second endpoint moved")
    correction = 1 | (1 << final)
    fixed = {(bank, mask ^ correction) for bank, mask in expressions[1]}
    if fixed != {(1, universe ^ 1)}:
        raise SystemExit("FAIL_ROTATING_ADDRESS_WALK correction moved")
    banks = [{bank for bank, _mask in group} for group in expressions]
    if banks != [{0}, {1}]:
        raise SystemExit("FAIL_ROTATING_ADDRESS_WALK scalar banks moved")
    mass = sum(rank * count for rank, count in profile.items())
    return {
        "dimension": dimension,
        "high": high,
        "low": low,
        "profile": profile,
        "mass": mass,
        "normals": normals,
        "final": final,
    }


def main() -> None:
    pinned = load()
    found = walk()
    if (
        found["dimension"] != 43
        or found["high"] != 0
        or found["low"] != 1
        or found["profile"] != {1: 6, 6: 6, 7: 6}
        or found["mass"] != 84
        or 2 * found["dimension"] != 86
        or found["final"] != 36
        or found["normals"] != [1, 8, 15, 22, 29, 36]
    ):
        raise SystemExit("FAIL_ROTATING_ADDRESS_WALK walk moved")
    if (
        pinned["stages"] != STAGES
        or pinned["dimension"] != found["dimension"]
        or pinned["rank_mass"] != found["mass"]
        or pinned["capacity"] != 2 * found["dimension"]
        or pinned["final_spectator"] != found["final"]
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_ROTATING_ADDRESS_WALK pinned result moved")
    print(f"PASS_ROTATING_ADDRESS_WALK mass={found['mass']} no_new_kappa")


if __name__ == "__main__":
    main()
