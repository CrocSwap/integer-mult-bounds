#!/usr/bin/env python3
"""Exact two-projection connector witness and bounded search."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WORD = (0, 1, 0, 1, 2, 3, 4, 2, 4, 3)
SPECIAL = 3
ALL_MASKS = set(range(1 << 5))
NONZERO_MASKS = set(range(1, 1 << 5))
B_PRICES = (1, 4, 10, 16, 28)
IDENTITY = (1, 0, 0, 1)
GENERATORS = {
    "u0": (1, 1, 0, 1),  # z0 <- z0 + z1
    "u1": (1, 0, 1, 1),  # z1 <- z1 + z0
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL_TWO_PROJECTION_CONNECTOR " + message)


def canonical_words() -> list[tuple[int, ...]]:
    """Generate restricted-growth pair words, independently of permutations."""
    out: list[tuple[int, ...]] = []
    path = [0]
    counts = [1, 0, 0, 0, 0]

    def visit(max_label: int) -> None:
        if len(path) == 10:
            if max_label == 4 and counts == [2, 2, 2, 2, 2]:
                out.append(tuple(path))
            return
        for label in range(max_label + 2):
            if label > 4 or counts[label] == 2:
                continue
            if label > max_label + 1:
                continue
            counts[label] += 1
            path.append(label)
            visit(max(max_label, label))
            path.pop()
            counts[label] -= 1

    visit(0)
    return out


def prefixes(word: tuple[int, ...], special_mask: int) -> tuple[list[int], list[int]]:
    all_prefix = [0]
    regular_prefix = [0]
    all_state = regular_state = 0
    for source in word:
        all_state ^= 1 << source
        if not (special_mask >> source) & 1:
            regular_state ^= 1 << source
        all_prefix.append(all_state)
        regular_prefix.append(regular_state)
    return all_prefix, regular_prefix


def difference_set(values: list[int]) -> set[int]:
    return {values[s] ^ values[t] for s in range(len(values)) for t in range(s + 1, len(values))}


def first_pair(values: list[int], mask: int) -> tuple[int, int] | None:
    for s in range(len(values)):
        for t in range(s + 1, len(values)):
            if values[s] ^ values[t] == mask:
                return s, t
    return None


def matrix_mul(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return tuple(
        (a[2 * r] * b[c] + a[2 * r + 1] * b[2 + c]) & 1
        for r in range(2)
        for c in range(2)
    )  # type: ignore[return-value]


def matrix_inv(a: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return a[3], a[1], a[2], a[0]


def matrix_vec(a: tuple[int, int, int, int], v: tuple[int, int]) -> tuple[int, int]:
    return ((a[0] * v[0] + a[1] * v[1]) & 1, (a[2] * v[0] + a[3] * v[1]) & 1)


def frame_paths() -> dict[tuple[int, int, int, int], tuple[str, ...]]:
    paths: dict[tuple[int, int, int, int], tuple[str, ...]] = {IDENTITY: ()}
    todo = deque([IDENTITY])
    while todo:
        frame = todo.popleft()
        for name, generator in GENERATORS.items():
            reached = matrix_mul(generator, frame)
            if reached not in paths:
                paths[reached] = paths[frame] + (name,)
                todo.append(reached)
    need(len(paths) == 6, "the two row shears did not generate all of GL(2,F2)")
    return paths


def allowed_frames(kind: str, source: int | None = None) -> tuple[tuple[int, int, int, int], ...]:
    frames = sorted(frame_paths())
    if kind == "all":
        return tuple(frame for frame in frames if frame[:2] == (1, 0))
    if kind == "regular":
        return tuple(frame for frame in frames if frame[:2] == (1, 1))
    if kind == "B":
        direction = (1, 1) if source == SPECIAL else (1, 0)
        return tuple(frame for frame in frames if matrix_vec(frame, direction) == (1, 0))
    need(False, f"unknown frame action: {kind}")
    return ()


def move_frames(
    states: dict[tuple[int, int, int, int], tuple[int, tuple[tuple[int, str, tuple[int, int, int, int]], ...]]],
    allowed: tuple[tuple[int, int, int, int], ...],
    boundary: int,
    kind: str,
    paths: dict[tuple[int, int, int, int], tuple[str, ...]],
) -> dict[tuple[int, int, int, int], tuple[int, tuple[tuple[int, str, tuple[int, int, int, int]], ...]]]:
    result = {}
    for target in allowed:
        choices = []
        for source, (cost, actions) in states.items():
            transition = matrix_mul(target, matrix_inv(source))
            choices.append((cost + len(paths[transition]), actions + ((boundary, kind, target),)))
        result[target] = min(choices)
    return result


def optimal_frame_actions(readouts: list[dict[str, object]]) -> tuple[int, list[dict[str, object]], dict[tuple[int, int, int, int], tuple[str, ...]]]:
    """Exact shortest frame schedule for this readout-boundary table."""
    paths = frame_paths()
    requests = [{"all": 0, "regular": 0} for _ in range(11)]
    for row in readouts:
        for boundary in row["boundaries"]:  # type: ignore[index]
            requests[int(boundary)][str(row["projection"])] += 1

    states = {IDENTITY: (0, ())}
    for boundary in range(11):
        kinds = [kind for kind in ("all", "regular") if requests[boundary][kind]]
        orders = [kinds, kinds[::-1]] if len(kinds) == 2 else [kinds]
        after_readouts = {}
        for order in orders:
            current = states
            for kind in order:
                current = move_frames(current, allowed_frames(kind), boundary, kind, paths)
            for frame, value in current.items():
                after_readouts[frame] = min(after_readouts.get(frame, (10**9, ())), value)
        states = after_readouts
        if boundary < 10:
            states = move_frames(states, allowed_frames("B", WORD[boundary]), boundary, "B", paths)

    endings = []
    for frame, (cost, actions) in states.items():
        transition = matrix_mul(IDENTITY, matrix_inv(frame))
        endings.append((cost + len(paths[transition]), actions + ((10, "end", IDENTITY),)))
    cost, path = min(endings)
    actions = [
        {"boundary": boundary, "kind": kind, "frame": list(frame)}
        for boundary, kind, frame in path
    ]
    return cost, actions, paths


def compile_transitions(
    actions: list[dict[str, object]],
    paths: dict[tuple[int, int, int, int], tuple[str, ...]],
) -> list[tuple[str, ...]]:
    current = IDENTITY
    transitions = []
    for action in actions:
        target = tuple(int(x) for x in action["frame"])
        transitions.append(paths[matrix_mul(target, matrix_inv(current))])
        current = target
    need(current == IDENTITY, "frame schedule does not restore the initial basis")
    return transitions


def apply_generator(helper: list[int], name: str) -> None:
    if name == "u0":
        helper[0] ^= helper[1]
    elif name == "u1":
        helper[1] ^= helper[0]
    else:
        need(False, f"unknown row-shear generator: {name}")


def simulate_global(
    readouts: list[dict[str, object]],
    actions: list[dict[str, object]],
    paths: dict[tuple[int, int, int, int], tuple[str, ...]],
    omit_transition: tuple[int, int] | None = None,
) -> tuple[list[int], list[int], int, tuple[int, int, int, int], list[int], list[tuple[int, str]]]:
    """Literal physical-row replay in a changing, globally maintained frame."""
    helper = [1 << 0, 1 << 1]  # two arbitrary dirty helper basis symbols
    outputs = [0] * 32
    reads = [[[] for _ in range(2)] for _ in range(11)]  # all, regular
    projection_index = {"all": 0, "regular": 1}
    for row in readouts:
        for boundary in row["boundaries"]:  # type: ignore[index]
            reads[int(boundary)][projection_index[str(row["projection"])]].append(int(row["mask"]))

    transitions = compile_transitions(actions, paths)
    current = IDENTITY
    total_xors = 0
    read_counts = [0] * 32
    frame_violations = []
    for action_index, action in enumerate(actions):
        for operation_index, generator_name in enumerate(transitions[action_index]):
            if omit_transition == (action_index, operation_index):
                continue
            apply_generator(helper, generator_name)
            current = matrix_mul(GENERATORS[generator_name], current)
            total_xors += 1

        boundary = int(action["boundary"])
        kind = str(action["kind"])
        planned = tuple(int(x) for x in action["frame"])
        if kind in ("all", "regular"):
            required = (1, 0) if kind == "all" else (1, 1)
            if current[:2] != required:
                frame_violations.append((action_index, kind))
            for mask in reads[boundary][projection_index[kind]]:
                outputs[mask] ^= helper[0]
                read_counts[mask] += 1
        elif kind == "B":
            source = WORD[boundary]
            direction = (1, 1) if source == SPECIAL else (1, 0)
            if matrix_vec(current, direction) != (1, 0):
                frame_violations.append((action_index, "B"))
            helper[0] ^= 1 << (2 + source)
        elif kind != "end":
            need(False, f"unknown compiled action: {kind}")

        if omit_transition is None:
            need(current == planned, f"transition path missed frame at action {action_index}")

    return helper, outputs, total_xors, current, read_counts, frame_violations


def main() -> None:
    words = canonical_words()
    need(len(words) == 945 and len(set(words)) == 945, "canonical pair census is not 945 unique words")
    need(all(tuple(sorted(word).count(j) for j in range(5)) == (2, 2, 2, 2, 2) for word in words),
         "pair-word generator returned a word with wrong multiplicities")

    full_cover_count = 0
    best_nonzero = 0
    for word in words:
        for directions in range(32):
            all_prefix, regular_prefix = prefixes(word, directions)
            covered = difference_set(all_prefix) | difference_set(regular_prefix)
            count = len(covered & NONZERO_MASKS)
            best_nonzero = max(best_nonzero, count)
            if NONZERO_MASKS <= covered:
                full_cover_count += 1
    need(full_cover_count == 175, f"two-projection full-cover count changed: {full_cover_count}")
    need(best_nonzero == 31, f"bounded-domain maximum changed: {best_nonzero}")

    all_prefix, regular_prefix = prefixes(WORD, 1 << SPECIAL)
    all_differences = difference_set(all_prefix)
    regular_differences = difference_set(regular_prefix)
    union = all_differences | regular_differences
    need(len(all_differences) == 26, "all-source difference set size is not 26")
    need(len(regular_differences) == 16, "regular-source difference set size is not 16")
    need(union == ALL_MASKS, "the two certified projections do not cover F2^5")
    missing = sorted(NONZERO_MASKS - all_differences)
    need(missing == [17, 18, 19, 21, 22, 23], "all-source missing-mask set changed")
    need(set(missing) <= regular_differences, "regular-source projection does not fill every missing mask")

    expected = json.loads((PACKAGE / "EXPECTED.json").read_text(encoding="utf-8"))
    readouts = expected["readouts"]
    need(len(readouts) == 31, "certificate must have one row for each nonzero mask")
    need([int(row["mask"]) for row in readouts] == list(range(1, 32)),
         "readout rows must be ordered masks 1..31")
    readout_count = 0
    for row in readouts:
        mask = int(row["mask"])
        projection = row["projection"]
        covector = row["covector"]
        values = all_prefix if projection == "all" else regular_prefix if projection == "regular" else None
        need(values is not None, f"unknown projection for mask {mask}")
        need((covector == [1, 0]) == (projection == "all"), f"wrong covector for mask {mask}")
        pair = tuple(int(x) for x in row["boundaries"])
        need(len(pair) == 2 and pair[0] < pair[1], f"invalid readout boundaries for mask {mask}")
        need(values[pair[0]] ^ values[pair[1]] == mask, f"boundary pair fails for mask {mask}")
        need(mask in (all_differences if projection == "all" else regular_differences),
             f"selected projection lacks mask {mask}")
        readout_count += 2
    need(readout_count == 62, "each output must be read exactly twice")

    frame_cost, actions, paths = optimal_frame_actions(readouts)
    need(frame_cost == 10, f"fixed-boundary shortest frame schedule changed: {frame_cost}")
    need(actions == expected["frame_actions"], "stored globally maintained frame schedule changed")
    helper, outputs, frame_xors, final_frame, read_counts, violations = simulate_global(readouts, actions, paths)
    need(helper == [1 << 0, 1 << 1], "dirty helper rows were not restored")
    need(final_frame == IDENTITY and not violations, "the final frame or an operation frame is invalid")
    need(read_counts[1:] == [2] * 31, "every output must receive exactly two readouts")
    for mask in range(1, 32):
        expected_atoms = sum(1 << (2 + j) for j in range(5) if (mask >> j) & 1)
        need(outputs[mask] == expected_atoms, f"literal global-frame map fails at output mask {mask}")
    need(frame_xors == 10, f"global frame XOR invoice changed: {frame_xors}")

    # Negative control 1: without the second projection, exactly six nonzero masks are absent.
    need(sorted(NONZERO_MASKS - all_differences) == missing, "single-projection negative control changed")
    # Negative control 2: making every source use direction (1,0) removes the second projection.
    wrong_all, wrong_regular = prefixes(WORD, 0)
    wrong_cover = difference_set(wrong_all) | difference_set(wrong_regular)
    need(not (NONZERO_MASKS <= wrong_cover), "wrong direction assignment unexpectedly covers all masks")
    # Negative control 3: a bad boundary pair for mask 21 produces the wrong projected mask.
    row21 = next(row for row in readouts if int(row["mask"]) == 21)
    need(regular_prefix[0] ^ regular_prefix[1] != 21 and row21["projection"] == "regular",
         "corrupt-boundary negative control was not set up")
    # Negative control 4: dropping one CNOT from the first nontrivial transition breaks its frame.
    transitions = compile_transitions(actions, paths)
    changed = next((i, 0) for i, ops in enumerate(transitions) if ops)
    _, bad_outputs, _, bad_frame, _, bad_violations = simulate_global(readouts, actions, paths, changed)
    need(bad_frame != IDENTITY or bad_violations or bad_outputs != outputs,
         "omitted frame-change CNOT was not detected")

    # Price the same fixed B and A child prices carried in the pinned base certificate.
    cert = json.loads((ROOT / "research/universal-connector-boundary/CERTIFICATE.json").read_text())
    baseline = cert["lowered"]["five_extra_output"]
    baseline_schedule = cert["schedules"]["five_extra_output"]
    need(baseline["leaf_calls"] == 182 and baseline_schedule["queries"] == 74,
         "pinned one-row comparator changed")
    need(len(baseline_schedule["source_word"]) == 10, "pinned comparator source count changed")
    pinned_b_prices = tuple(int(baseline["query_leaf_prices"][f"B{j}"]) for j in range(5))
    pinned_a_prices = tuple(int(baseline["query_leaf_prices"][f"A{j}"]) for j in range(31))
    need(pinned_b_prices == B_PRICES, "pinned B child prices changed")
    need(pinned_a_prices == (1,) * 31, "pinned A child prices changed")
    baseline_b_calls = [op for op, _ in baseline_schedule["word"] if op == "B"]
    baseline_a_calls = [op for op, _ in baseline_schedule["word"] if op == "A"]
    need((len(baseline_b_calls), len(baseline_a_calls)) == (10, 64),
         "pinned one-row comparator call split changed")
    candidate_b_children = 2 * sum(pinned_b_prices)
    candidate_a_children = readout_count
    candidate_children = candidate_b_children + candidate_a_children
    need(candidate_b_children == 118 and candidate_children == 180,
         "candidate child invoice changed")
    need(baseline["leaf_calls"] - candidate_children == 2,
         "candidate does not save exactly two rank-one children")

    print(
        "PASS_TWO_PROJECTION_CONNECTOR "
        f"words={len(words)} assignments={len(words)*32} full_covers={full_cover_count} "
        f"source_calls=10 readouts=62 calls=72 frame_xors={frame_xors} "
        f"children={candidate_children} baseline_children=182 saved=2"
    )


if __name__ == "__main__":
    main()
