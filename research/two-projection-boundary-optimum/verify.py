#!/usr/bin/env python3
"""Exhaust the boundary-demand sets for one fixed two-projection connector."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BASE_PACKAGE = ROOT / "research/two-projection-connector-seed51a5"
WORD = (0, 1, 0, 1, 2, 3, 4, 2, 4, 3)
SPECIAL = 3
IDENTITY = (1, 0, 0, 1)
GENERATORS = ((1, 1, 0, 1), (1, 0, 1, 1))
BOUNDARIES = 11
SUBSETS = 1 << BOUNDARIES
FULL_NONZERO = (1 << 32) - 2


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL_TWO_PROJECTION_BOUNDARY_OPTIMUM " + message)


def mul(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, int, int, int]:
    return tuple(
        (a[2 * r] * b[c] + a[2 * r + 1] * b[2 + c]) & 1
        for r in range(2)
        for c in range(2)
    )  # type: ignore[return-value]


def inverse(a: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    # For an invertible 2x2 matrix over F2 the determinant is 1.
    return a[3], a[1], a[2], a[0]


def apply(a: tuple[int, int, int, int], v: tuple[int, int]) -> tuple[int, int]:
    return (
        (a[0] * v[0] + a[1] * v[1]) & 1,
        (a[2] * v[0] + a[3] * v[1]) & 1,
    )


def frames() -> tuple[tuple[int, int, int, int], ...]:
    out = []
    for code in range(16):
        a = tuple((code >> shift) & 1 for shift in (3, 2, 1, 0))
        if (a[0] * a[3] + a[1] * a[2]) & 1:
            out.append(a)
    need(len(out) == 6, "GL(2,F2) must have six frames")
    return tuple(out)  # type: ignore[return-value]


def generator_distances(
    group: tuple[tuple[int, int, int, int], ...],
) -> dict[tuple[int, int, int, int], int]:
    """Shortest words in the two paid row shears, by breadth-first search."""
    distances = {IDENTITY: 0}
    queue = deque([IDENTITY])
    while queue:
        here = queue.popleft()
        for generator in GENERATORS:
            there = mul(generator, here)
            if there not in distances:
                distances[there] = distances[here] + 1
                queue.append(there)
    need(set(distances) == set(group), "the two row shears must generate GL(2,F2)")
    return distances


def transition_cost(
    source: tuple[int, int, int, int],
    target: tuple[int, int, int, int],
    distances: dict[tuple[int, int, int, int], int],
) -> int:
    relative = mul(target, inverse(source))
    return distances[relative]


def prefix_paths() -> tuple[list[int], list[int]]:
    all_values = [0]
    regular_values = [0]
    all_state = regular_state = 0
    for source in WORD:
        all_state ^= 1 << source
        if source != SPECIAL:
            regular_state ^= 1 << source
        all_values.append(all_state)
        regular_values.append(regular_state)
    return all_values, regular_values


def projection_coverages(values: list[int]) -> list[int]:
    """For each boundary subset, return its set of nonzero XOR differences."""
    cover = [0] * SUBSETS
    for chosen in range(1, SUBSETS):
        lowest = chosen & -chosen
        new_index = lowest.bit_length() - 1
        earlier = chosen ^ lowest
        value = cover[earlier]
        scan = earlier
        while scan:
            bit = scan & -scan
            old_index = bit.bit_length() - 1
            difference = values[new_index] ^ values[old_index]
            if difference:
                value |= 1 << difference
            scan ^= bit
        cover[chosen] = value
    return cover


def allowed_source_frames(
    group: tuple[tuple[int, int, int, int], ...], source: int
) -> tuple[tuple[int, int, int, int], ...]:
    direction = (1, 1) if source == SPECIAL else (1, 0)
    return tuple(frame for frame in group if apply(frame, direction) == (1, 0))


def min_frame_cost(
    all_nodes: int,
    regular_nodes: int,
    group: tuple[tuple[int, int, int, int], ...],
    distances: dict[tuple[int, int, int, int], int],
) -> int:
    """Minimize frame shears for readout nodes plus the ten fixed B events."""
    all_frames = tuple(frame for frame in group if frame[:2] == (1, 0))
    regular_frames = tuple(frame for frame in group if frame[:2] == (1, 1))
    states = {IDENTITY: 0}

    for boundary in range(BOUNDARIES):
        demands = []
        if (all_nodes >> boundary) & 1:
            demands.append(("all", all_frames))
        if (regular_nodes >> boundary) & 1:
            demands.append(("regular", regular_frames))
        orders = [demands]
        if len(demands) == 2:
            orders.append(demands[::-1])

        after_readouts: dict[tuple[int, int, int, int], int] = {}
        for order in orders:
            current = states
            for _, allowed in order:
                current = {
                    target: min(
                        value + transition_cost(source, target, distances)
                        for source, value in current.items()
                    )
                    for target in allowed
                }
            for frame, value in current.items():
                after_readouts[frame] = min(after_readouts.get(frame, 10**9), value)
        states = after_readouts

        if boundary < len(WORD):
            allowed = allowed_source_frames(group, WORD[boundary])
            states = {
                target: min(
                    value + transition_cost(source, target, distances)
                    for source, value in states.items()
                )
                for target in allowed
            }

    return min(
        value + transition_cost(frame, IDENTITY, distances)
        for frame, value in states.items()
    )


def readout_pairs_valid(
    readouts: list[dict[str, object]],
    all_values: list[int],
    regular_values: list[int],
) -> bool:
    if len(readouts) != 31:
        return False
    for mask, row in enumerate(readouts, start=1):
        projection = row.get("projection")
        values = all_values if projection == "all" else regular_values if projection == "regular" else None
        boundaries = row.get("boundaries")
        if row.get("mask") != mask or values is None or not isinstance(boundaries, list):
            return False
        if len(boundaries) != 2 or not all(type(b) is int and 0 <= b < BOUNDARIES for b in boundaries):
            return False
        if boundaries[0] >= boundaries[1] or values[boundaries[0]] ^ values[boundaries[1]] != mask:
            return False
    return True


def check_predecessor_witness(
    all_values: list[int],
    regular_values: list[int],
    group: tuple[tuple[int, int, int, int], ...],
    distances: dict[tuple[int, int, int, int], int],
) -> tuple[int, int, int, int]:
    expected_path = BASE_PACKAGE / "EXPECTED.json"
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    need(expected["source_word"] == list(WORD), "pinned predecessor source word changed")
    need(expected["special_source"] == SPECIAL, "pinned predecessor source direction changed")
    need(expected["field"] == "F2", "pinned predecessor field changed")
    need(expected["expected"]["fixed_boundary_shortest_frame_xors"] == 10,
         "pinned predecessor fixed-table frame cost changed")
    need(expected["expected"]["weighted_rank_one_children"] == 180,
         "pinned predecessor child count changed")
    need(expected["expected"]["one_row_comparator_children"] == 182,
         "pinned predecessor one-row comparison changed")
    readouts = expected["readouts"]
    need(readout_pairs_valid(readouts, all_values, regular_values),
         "predecessor readout pair table failed its mask identities")
    need(len(readouts) == 31, "predecessor witness must have 31 output rows")
    all_nodes = regular_nodes = 0
    for mask, row in enumerate(readouts, start=1):
        need(row["mask"] == mask, f"predecessor row order changed at mask {mask}")
        projection = row["projection"]
        values = all_values if projection == "all" else regular_values if projection == "regular" else None
        need(values is not None, f"unknown projection at mask {mask}")
        boundaries = row["boundaries"]
        need(len(boundaries) == 2 and boundaries[0] < boundaries[1], f"bad pair for mask {mask}")
        need(values[boundaries[0]] ^ values[boundaries[1]] == mask,
             f"predecessor boundary pair fails at mask {mask}")
        for boundary in boundaries:
            if projection == "all":
                all_nodes |= 1 << boundary
            else:
                regular_nodes |= 1 << boundary

    # Validate and price the retained frame-action witness by shortest words.
    actions = expected["frame_actions"]
    current = IDENTITY
    actual_cost = 0
    readout_nodes = {"all": [], "regular": []}
    seen_source_boundaries = set()
    last_boundary = -1
    last_phase = -1
    for action in actions:
        boundary = action["boundary"]
        kind = action["kind"]
        frame = tuple(action["frame"])
        need(frame in group, "predecessor action is not an invertible frame")
        phase = 0 if kind in ("all", "regular") else 1 if kind == "B" else 2
        need(boundary >= last_boundary, "predecessor actions are not chronological")
        if boundary == last_boundary:
            need(phase >= last_phase, "a source call precedes a same-boundary readout")
        else:
            last_phase = -1
        last_boundary, last_phase = boundary, phase
        if kind == "all":
            need(frame[:2] == (1, 0), "all-source readout has the wrong covector")
            readout_nodes["all"].append(boundary)
        elif kind == "regular":
            need(frame[:2] == (1, 1), "regular readout has the wrong covector")
            readout_nodes["regular"].append(boundary)
        elif kind == "B":
            need(0 <= boundary < len(WORD), "source boundary is outside the word")
            need(boundary not in seen_source_boundaries, "duplicate source boundary")
            seen_source_boundaries.add(boundary)
            direction = (1, 1) if WORD[boundary] == SPECIAL else (1, 0)
            need(apply(frame, direction) == (1, 0), "source uses the wrong helper direction")
        elif kind == "end":
            need(boundary == len(WORD) and frame == IDENTITY, "bad final frame restoration")
        else:
            need(False, f"unknown frame action {kind}")
        actual_cost += transition_cost(current, frame, distances)
        current = frame  # type: ignore[assignment]
    need(current == IDENTITY, "predecessor frame schedule does not restore identity")
    need(seen_source_boundaries == set(range(len(WORD))), "predecessor omits a source call")
    need(len(readout_nodes["all"]) == len(set(readout_nodes["all"])),
         "duplicate all-readout demand node")
    need(len(readout_nodes["regular"]) == len(set(readout_nodes["regular"])),
         "duplicate regular-readout demand node")
    need(set(readout_nodes["all"]) == {i for i in range(BOUNDARIES) if all_nodes >> i & 1},
         "predecessor all-readout demand set changed")
    need(set(readout_nodes["regular"]) == {i for i in range(BOUNDARIES) if regular_nodes >> i & 1},
         "predecessor regular-readout demand set changed")
    need(len(expected["frame_actions"]) > 0, "missing predecessor frame-action witness")

    # A deliberately corrupted pair must fail the exact mask identity.
    corrupted = [dict(row) for row in readouts]
    corrupted[20] = {**corrupted[20], "boundaries": [0, 1]}
    row = corrupted[20]
    vals = all_values if row["projection"] == "all" else regular_values
    need(vals[row["boundaries"][0]] ^ vals[row["boundaries"][1]] != 21,
         "corrupted-pair control did not actually break mask 21")
    need(not readout_pairs_valid(corrupted, all_values, regular_values),
         "corrupted-pair negative control was not rejected")
    return all_nodes, regular_nodes, actual_cost, len(readouts) * 2


def main() -> None:
    group = frames()
    distances = generator_distances(group)
    all_values, regular_values = prefix_paths()
    all_cover = projection_coverages(all_values)
    regular_cover = projection_coverages(regular_values)

    valid_sets = 0
    node_histogram: dict[int, int] = {}
    cost_histogram: dict[int, int] = {}
    best_cost = 10**9
    best_sets = 0
    for all_nodes in range(SUBSETS):
        for regular_nodes in range(SUBSETS):
            covered = all_cover[all_nodes] | regular_cover[regular_nodes]
            if (covered & FULL_NONZERO) != FULL_NONZERO:
                continue
            valid_sets += 1
            node_count = all_nodes.bit_count() + regular_nodes.bit_count()
            node_histogram[node_count] = node_histogram.get(node_count, 0) + 1
            cost = min_frame_cost(all_nodes, regular_nodes, group, distances)
            cost_histogram[cost] = cost_histogram.get(cost, 0) + 1
            if cost < best_cost:
                best_cost = cost
                best_sets = 1
            elif cost == best_cost:
                best_sets += 1

    current_all, current_regular, current_cost, readout_calls = check_predecessor_witness(
        all_values, regular_values, group, distances
    )
    need(valid_sets == 848, f"covering demand-set count changed: {valid_sets}")
    need(node_histogram == {13: 1, 14: 15, 15: 69, 16: 161, 17: 225,
                            18: 202, 19: 119, 20: 45, 21: 10, 22: 1},
         f"covering-set node histogram changed: {node_histogram}")
    need(cost_histogram == {10: 38, 12: 248, 14: 386, 16: 176},
         f"minimum-cost histogram changed: {cost_histogram}")
    need(best_cost == 10 and best_sets == 38, "global minimum frame-XOR count is not 10")
    need(current_cost == 10 and readout_calls == 62, "predecessor witness does not attain the minimum")
    result = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    need(result["enumeration"]["candidate_node_sets"] == SUBSETS * SUBSETS,
         "RESULT.json candidate count differs from exhaustive domain")
    need(result["enumeration"]["node_sets_covering_all_31_masks"] == valid_sets,
         "RESULT.json covering-set count differs from exhaustive replay")
    need(result["enumeration"]["covering_sets_by_node_count"]
         == {str(k): v for k, v in sorted(node_histogram.items())},
         "RESULT.json node histogram differs from exhaustive replay")
    need(result["enumeration"]["covering_sets_by_minimum_frame_xors"]
         == {str(k): v for k, v in sorted(cost_histogram.items())},
         "RESULT.json frame-cost histogram differs from exhaustive replay")
    need(result["enumeration"]["minimum_frame_xors"] == best_cost,
         "RESULT.json minimum differs from exhaustive replay")
    need(result["enumeration"]["minimizing_node_sets"] == best_sets,
         "RESULT.json minimizer count differs from exhaustive replay")
    need(result["predecessor_attainment"]["frame_xors"] == current_cost,
         "RESULT.json predecessor cost differs from independent replay")
    need(result["predecessor_attainment"]["readout_calls"] == readout_calls,
         "RESULT.json readout count differs from predecessor certificate")
    need(result["predecessor_attainment"]["all_readout_boundaries"]
         == [i for i in range(BOUNDARIES) if current_all >> i & 1],
         "RESULT.json all-projection nodes differ from predecessor certificate")
    need(result["predecessor_attainment"]["regular_readout_boundaries"]
         == [i for i in range(BOUNDARIES) if current_regular >> i & 1],
         "RESULT.json regular-projection nodes differ from predecessor certificate")
    need(result["predecessor_attainment"]["rank_one_children"] == 180
         and result["predecessor_attainment"]["single_row_comparison_children"] == 182,
         "RESULT.json predecessor child comparison changed")
    need((all_cover[SUBSETS - 1] & FULL_NONZERO) != FULL_NONZERO,
         "all-source projection alone unexpectedly covers every mask")
    need((regular_cover[SUBSETS - 1] & FULL_NONZERO) != FULL_NONZERO,
         "regular projection alone unexpectedly covers every mask")

    node_histogram = dict(sorted(node_histogram.items()))
    cost_histogram = dict(sorted(cost_histogram.items()))
    print(
        "PASS_TWO_PROJECTION_BOUNDARY_OPTIMUM "
        f"demand_sets={SUBSETS * SUBSETS} covering={valid_sets} "
        f"node_hist={node_histogram} xor_hist={cost_histogram} "
        f"minimum_xors={best_cost} minimizers={best_sets} current_xors={current_cost}"
    )


if __name__ == "__main__":
    main()
