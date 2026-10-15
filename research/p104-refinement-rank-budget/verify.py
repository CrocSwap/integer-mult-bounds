#!/usr/bin/env python3
"""Check the P104 survivor separator and its added-rank budget.

Nick Petalas. Apache-2.0. The separator is Tairitsu-Aya's PR2136 result;
the added-rank transcript implication is proved in README.md.
No predecessor verifier/compiler imports, floating point, or network access.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WITNESS = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
RESULT = "research/p104-native-channel/inputs/LOWRANK-RESULT.json"
FULL = frozenset(range(512))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def span(vectors: list[int]) -> frozenset[int]:
    require(len(vectors) <= 9, "at most nine basis vectors")
    values = {0}
    for vector in vectors:
        require(type(vector) is int and 0 < vector < 512, "nine-bit label")
        require(vector not in values, "independent frame basis")
        values.update(value ^ vector for value in tuple(values))
    return frozenset(values)


def dimension(space: frozenset[int]) -> int:
    return len(space).bit_length() - 1


def read_inputs() -> dict:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    records = [item for item in manifest["files"] if item["usage"] == "input"]
    require(len(records) == 3, "three declared live inputs")
    inputs = {}
    for item in records:
        path = ROOT / item["path"]
        require(path.stat().st_size <= 1_048_576, "input size limit")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item["sha256"],
                "source hash mismatch: " + item["path"])
        if item["path"].endswith(".json"):
            inputs[item["path"]] = json.loads(raw)
    return inputs


def trace(word: dict) -> tuple:
    entry = {name: span(rows) for name, rows in word["initial_frames"].items()}
    final = {name: span(rows) for name, rows in word["final_frames"].items()}
    require(len(entry) == 280 and entry.keys() == final.keys(), "280 persistent roles")
    require(all(name in entry for name in [f"X{i}" for i in range(104)]
                + [f"Y{i}" for i in range(104)]), "source and target role names")
    live, moves, private, kinds = dict(entry), [], [], Counter()
    require(len(word["program"]) == 4058, "4058 original events")
    for index, event in enumerate(word["program"]):
        op, name = event[:2]
        kinds[op] += 1
        if op == "transport":
            before, after = span(event[2]), span(event[3])
            require(live[name] == before, "transport continuity")
            require(before < after or after < before, "strict nested transport")
            rank = abs(dimension(after) - dimension(before))
            require(type(event[4]) is int and event[4] == rank, "transport rank")
            moves.append((index, name, before, after, rank))
            live[name] = after
        elif op == "zero":
            require(name == "C" and name not in live, "fresh private C")
            live[name] = span(event[-1])
            private.append([op])
        elif op in ("add", "copy"):
            require(live[name] == live[event[2]] == span(event[-1]), "common chart")
            if op == "copy":
                require(name == "C" and private[-1] == ["zero"], "private copy")
                private[-1].append(op)
        elif op == "erase":
            require(name == "C" and live[name] == span(event[-1]), "private discard")
            require(private[-1] == ["zero", "copy"], "private lifetime")
            private[-1].append(op)
            del live[name]
        else:
            raise ValueError("unknown operation")
    require(live == final, "final frame endpoints")
    require(len(private) == 8 and all(p == ["zero", "copy", "erase"] for p in private),
            "eight private lifetimes")
    return entry, final, moves, kinds


def separator(moves: list[tuple]) -> tuple:
    drops = [move for move in moves if move[3] < move[2]]
    require(len(drops) == 8, "eight original descents")
    lines = []
    for _, name, before, after, rank in drops:
        require(name == "C" and len(before) == 256 and len(after) == 2 and rank == 7,
                "private hyperplane-to-line descent")
        lines.append(next(value for value in after if value))
    hull = span(lines)
    survivors = frozenset(lines)
    for _, _, before, after, _ in drops:
        require(len(before & survivors) == 1 and not before <= hull and after <= hull,
                "descent enters survivor span with exactly one survivor")
    return drops, survivors, hull


def target_side(space: frozenset[int], survivors: frozenset[int],
                hull: frozenset[int]) -> bool:
    return space != FULL and (space <= hull or len(space & survivors) >= 2)


def interval_case(lower: frozenset[int], upper: frozenset[int],
                  survivors: frozenset[int], hull: frozenset[int]) -> str:
    require(lower < upper, "upward nested interval")
    if len(upper & survivors) <= 1:
        return "upper_has_at_most_one_survivor"
    if upper <= hull:
        return "upper_inside_hull"
    if len(lower & survivors) >= 2:
        return "lower_has_two_survivors"
    if len(lower) == 256 and upper == FULL:
        return "last_step_to_full"
    raise ValueError("interval can bypass the inherited separator")


def budget(outside_sources: int, original_crossings: int) -> dict:
    needed = max(0, outside_sources - original_crossings)
    width, roles, calls, copy = 73, 8 * 104, 9, 56
    capacity = width * roles
    baseline = (width - 1) * roles + calls * copy
    completed = baseline + calls * needed
    return {
        "width": width, "roles": roles, "calls": calls,
        "baseline_rank_mass": baseline, "capacity": capacity,
        "headroom_per_call": str(Fraction(capacity - baseline, calls)),
        "added_rank_lower_bound_per_call": needed,
        "completed_rank_mass_lower_bound": completed,
        "zero_saving_moment_lower_bound": str(Fraction(completed, capacity)),
        "credit_needed_for_strict_positive_saving_gt": str(
            Fraction(completed - capacity, calls)),
    }


def analyze(word: dict, source_result: dict) -> dict:
    entry, final, moves, kinds = trace(word)
    drops, survivors, hull = separator(moves)
    classes = Counter(interval_case(before, after, survivors, hull)
                      for _, _, before, after, _ in moves if before < after)
    sources = [entry[f"X{i}"] for i in range(104)]
    targets = [final[f"Y{i}"] for i in range(104)]
    require(all(len(space) == 2 for space in sources), "104 singleton sources")
    require(all(len(space) == 256 and target_side(space, survivors, hull)
                for space in targets), "104 target-side hyperplanes")
    outside = sum(not target_side(space, survivors, hull) for space in sources)
    profile = Counter(rank for _, _, _, _, rank in moves)
    mass = sum(rank * count for rank, count in profile.items())
    progress = sum(dimension(final[name]) - dimension(space)
                   for name, space in entry.items())
    require({str(k): v for k, v in profile.items()} == source_result["paid_profile"],
            "recounted profile agrees with predecessor receipt")
    require(mass == source_result["rank_mass"] and mass - progress == 56,
            "original rank mass is boundary progress plus COPY56")
    return {
        "status": "PASS_P104_REFINEMENT_RANK_BUDGET",
        "original_operations": dict(sorted(kinds.items())),
        "transport_occurrences": len(moves), "upward_interval_cases": dict(sorted(classes.items())),
        "survivor_lines": sorted(survivors), "survivor_span_dimension": dimension(hull),
        "target_side_sources": 104 - outside, "other_side_sources": outside,
        "target_side_targets": len(targets), "original_entering_crossings": len(drops),
        "original_local_rank_mass": mass, "original_boundary_progress": progress,
        "conditional_no_progress_credit_budget": budget(outside, len(drops)),
    }


def charged_path(path: list[frozenset[int]], ranks: list[int],
                 survivors: frozenset[int], hull: frozenset[int]) -> int:
    require(1 <= len(ranks) <= 9 and len(path) == len(ranks) + 1, "bounded chain")
    direction = dimension(path[-1]) - dimension(path[0])
    require(direction != 0, "strict monotone path endpoints")
    arrivals = 0
    for before, after, rank in zip(path, path[1:], ranks):
        require((before < after if direction > 0 else after < before), "monotone chain")
        require(type(rank) is int and rank == abs(dimension(after) - dimension(before)),
                "every strict step is charged its rank")
        arrivals += not target_side(before, survivors, hull) and target_side(after, survivors, hull)
    require(arrivals <= sum(ranks), "entering transcript capacity is bounded by paid rank")
    return arrivals


def controls(word: dict, receipt: dict) -> list[str]:
    _, _, moves, _ = trace(word)
    drops, survivors, hull = separator(moves)
    labels = sorted(survivors)
    outsider = min(FULL - hull)
    one, two, three = span([outsider]), span([outsider, labels[0]]), span([outsider, *labels[:2]])
    require(charged_path([one, two, three], [1, 1], survivors, hull) == 1, "actual added bridge")
    # Full-to-zero can enter T twice. Counting each new obligation only once is unsafe.
    require(charged_path([FULL, three, one, span([])], [6, 2, 1], survivors, hull) == 2,
            "two-entry descending counterexample")
    rejected = []
    for name, expected_error, operation in (
        ("uncharged_bridge", "every strict step is charged its rank",
         lambda: charged_path([two, three], [0], survivors, hull)),
        ("nonnested_bridge", "monotone chain",
         lambda: charged_path([one, span(labels[:2])], [1], survivors, hull)),
        ("new_interval_is_not_original", "interval can bypass the inherited separator",
         lambda: interval_case(one, three, survivors, hull)),
        ("ninth_original_descent", "eight original descents", lambda: separator(moves + drops[:1])),
    ):
        try:
            operation()
        except ValueError as error:
            require(str(error) == expected_error, "control fails for its intended reason: " + name)
            rejected.append(name)
        else:
            raise ValueError("control accepted: " + name)
    changed = json.loads(json.dumps(word))
    changed["program"][moves[0][0]][4] += 1
    try:
        trace(changed)
    except ValueError as error:
        require(str(error) == "transport rank", "rank control fails for its intended reason")
        rejected.append("false_original_rank")
    else:
        raise ValueError("false rank accepted")
    bill = receipt["conditional_no_progress_credit_budget"]
    require(bill["added_rank_lower_bound_per_call"] == 48, "56 independent inputs minus eight crossings")
    require(Fraction(bill["zero_saving_moment_lower_bound"]) == Fraction(585, 584), "literal full bill")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write a receipt exclusively to a new file")
    args = parser.parse_args()
    inputs = read_inputs()
    receipt = analyze(inputs[WITNESS], inputs[RESULT])
    receipt["rejected_controls"] = controls(inputs[WITNESS], receipt)
    require(receipt == json.loads((PACKAGE / "EXPECTED.json").read_text()), "complete expected receipt")
    if args.out:
        with args.out.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
