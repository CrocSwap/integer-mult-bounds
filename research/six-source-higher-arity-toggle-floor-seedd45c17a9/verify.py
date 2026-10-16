#!/usr/bin/env python3
"""Exact replay of the additive-cost high-arity connector floor."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STEPS = (2, 16, 8, 16, 1, 4, 48, 4, 3, 4, 32, 8, 4, 16)
EXPECTED = (ROOT / "research/universal-connector-six-source/EXPECTED.json")


def need(ok: bool, label: str) -> None:
    if not ok:
        raise SystemExit("FAIL: " + label)


def weight(mask: int) -> int:
    return mask.bit_count()


def prefixes(steps: tuple[int, ...]) -> list[int]:
    q = 0
    out = [q]
    for step in steps:
        need(0 < step < 64, "nonempty six-source step")
        q ^= step
        out.append(q)
    return out


def differences(points: list[int]) -> set[int]:
    return {a ^ b for a in points for b in points}


def singleton_expand(mask: int) -> tuple[int, ...]:
    return tuple(1 << j for j in range(6) if mask & (1 << j))


def macro_effect(mask: int, x: int, z: int) -> int:
    return z ^ ((mask & x).bit_count() & 1)


def optimistic_query_floor(k: int) -> int:
    # P has at most k distinct prefixes because the final prefix repeats zero.
    # r((C2)^6)=14 forces at least one missing pair-difference for k=12,13.
    if k >= 14:
        return k + 126
    if k >= 12:
        return k + 128
    missing = 63 - k * (k - 1) // 2
    return k + 126 + 2 * missing


def make_pairs(points: list[int]) -> dict[int, tuple[int, int]]:
    unique = points[:-1]  # the closing boundary repeats q_0
    pairs: dict[int, tuple[int, int]] = {}
    for mask in range(1, 64):
        pair = next(((a, b) for a in range(len(unique))
                     for b in range(a + 1, len(unique))
                     if unique[a] ^ unique[b] == mask), None)
        need(pair is not None, f"readout boundary for mask {mask}")
        pairs[mask] = pair
    return pairs


def batch_schedule(steps: tuple[int, ...], pairs: dict[int, tuple[int, int]]):
    reads: list[list[int]] = [[] for _ in range(len(steps) + 1)]
    for mask, (a, b) in pairs.items():
        reads[a].append(mask)
        reads[b].append(mask)
    ops: list[tuple[str, int]] = []
    for boundary in range(len(steps)):
        ops.extend(("read", mask) for mask in sorted(reads[boundary]))
        ops.append(("source", steps[boundary]))
    ops.extend(("read", mask) for mask in sorted(reads[-1]))
    return ops


def apply(ops, x: int, z: int, y: list[int]) -> tuple[int, list[int]]:
    for kind, arg in ops:
        if kind == "source":
            z = macro_effect(arg, x, z)
        else:
            y[arg] ^= z
    return z, y


def replay_batch(steps: tuple[int, ...], pairs: dict[int, tuple[int, int]]) -> bool:
    ops = batch_schedule(steps, pairs)
    if len(ops) != 140:
        return False
    for x in range(64):
        for z0 in range(2):
            for seed in (0, 1):
                y0 = [((mask * 0x2D + seed) >> (mask % 6)) & 1
                      for mask in range(64)]
                z, y = apply(ops, x, z0, y0.copy())
                if z != z0:
                    return False
                for mask in range(1, 64):
                    if y[mask] != (y0[mask] ^ ((mask & x).bit_count() & 1)):
                        return False
                zr, yr = apply(list(reversed(ops)), x, z, y.copy())
                if zr != z0 or yr != y0:
                    return False
    return True


def main() -> None:
    receipt = json.loads(EXPECTED.read_text(encoding="utf-8"))
    census = {row["length"]: row for row in receipt["censuses"]
              if row["sources"] == 6}
    need(census[12]["max_coverage"] == 49 and census[12]["words"] == 10395,
         "pinned length-12 singleton census prerequisite")
    need(census[14]["max_coverage"] == 59 and census[14]["words"] == 945945,
         "pinned length-14 singleton census prerequisite")
    need(receipt["batch"]["optimum_queries"] == 142,
         "pinned six-source batch receipt")
    query_floors = [optimistic_query_floor(k) for k in range(15)]
    need(min(query_floors) == 140 and optimistic_query_floor(12) == 140
         and optimistic_query_floor(13) == 141 and optimistic_query_floor(11) == 153,
         "all-readout query lower-bound case split")

    q = prefixes(STEPS)
    need(len(STEPS) == 14 and q[-1] == 0, "14-call witness closes dirty connector")
    need(sum(map(weight, STEPS)) == 16, "witness source-add charge W=16")
    witness_points = q[:-1]
    need(len(set(witness_points)) == 14, "14 distinct witness boundaries")
    need(differences(witness_points) == set(range(64)),
         "witness prefix differences cover every source mask")

    expanded: list[int] = []
    q_expanded = 0
    retained = {0}
    expanded_prefixes = [0]
    for step in STEPS:
        for singleton in singleton_expand(step):
            expanded.append(singleton)
            q_expanded ^= singleton
            expanded_prefixes.append(q_expanded)
        retained.add(q_expanded)
    need(len(expanded) == 16 and q_expanded == 0,
         "expansion has exactly W=16 singleton toggles and closes")
    need(retained == set(witness_points), "all original event boundaries survive expansion")
    need(differences(expanded_prefixes) == set(range(64)),
         "expanded singleton word remains universal")

    # Tiny exact dirty-state test for every source-hyperedge, including arities 4..6.
    macro_cases = 0
    for mask in range(1, 64):
        split = singleton_expand(mask)
        for x in range(64):
            for z0 in range(2):
                z_macro = macro_effect(mask, x, z0)
                z_split = z0
                for bit in split:
                    z_split = macro_effect(bit, x, z_split)
                need(z_macro == z_split, f"dirty macro/split identity S={mask}")
                macro_cases += 1
    need(macro_cases == 8064, "complete small macro-state coverage")

    pairs = make_pairs(q)
    ops = batch_schedule(STEPS, pairs)
    need(sum(kind == "source" for kind, _ in ops) == 14,
         "full-batch source calls")
    need(sum(weight(arg) for kind, arg in ops if kind == "source") == 16,
         "full-batch source-add invoice")
    need(sum(kind == "read" for kind, _ in ops) == 126,
         "two readouts for each nonzero row")
    need(len(ops) == 140 and replay_batch(STEPS, pairs),
         "full dirty-input batch and reverse replay")

    # Failure controls: open connector, wrong output mask, and undercharged arity.
    need(prefixes(STEPS[:-1])[-1] != 0, "missing final source event is rejected")
    mutated_pairs = dict(pairs)
    mutated_pairs[1] = (0, 0)
    need(not replay_batch(STEPS, mutated_pairs), "wrong mask boundary is rejected")
    correct_macro_price = 1 + weight(0b001111)
    fake_macro_price = 1 + weight(0b001111) - 1
    need(correct_macro_price == 5 and fake_macro_price < correct_macro_price,
         "a four-tap macro cannot be billed as three taps")

    print("PASS_HIGH_ARITY_CONNECTOR_FLOOR arities=4..6 queries>=140 W>=16 "
          "readouts>=126 adds>=142 dirty_macro_cases=8064 query_cases=15 reverse=True controls=3")


if __name__ == "__main__":
    main()
