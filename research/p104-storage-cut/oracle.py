#!/usr/bin/env python3
"""Independent static frame graph using complete XOR spans.

This module has no project imports.  It validates the pinned witness's frame
trace, but deliberately does not replay scalar coefficients or native Clifford
operators.  ``analyze`` is pure and permits equivalent binary bases.  It reports
reachability rather than assuming the separation conclusion.
"""

from collections import Counter, defaultdict, deque
from fractions import Fraction
import hashlib
import json


CUT_EVENTS = (2463, 2472, 2479, 2487, 2495, 2503, 2510, 2518)
EVENT_COUNTS = {
    "add": 2624,
    "transport": 1410,
    "zero": 8,
    "copy": 8,
    "erase": 8,
}
ARITIES = {"add": 5, "transport": 5, "zero": 3, "copy": 4, "erase": 3}
ROLES = frozenset(
    [f"X{i}" for i in range(104)]
    + [f"Y{i}" for i in range(104)]
    + [f"G{i}" for i in range(32)]
    + [f"D{i}" for i in range(32)]
    + [f"Q{i}" for i in range(8)]
)


def require(condition, description):
    if not condition:
        raise ValueError(description)


def full_span(generators):
    """Enumerate a binary subspace, without elimination or a canonical basis."""
    require(isinstance(generators, list), "a frame must be a list")
    values = {0}
    for vector in generators:
        require(type(vector) is int and 0 <= vector < 512, "bad frame vector")
        values |= {value ^ vector for value in values}
    return tuple(sorted(values))


def dimension(frame):
    return len(frame).bit_length() - 1


def walk(seeds, arrows):
    outgoing = defaultdict(set)
    for source, target in arrows:
        outgoing[source].add(target)
    seen = set(seeds)
    queue = deque(seeds)
    while queue:
        for target in outgoing[queue.popleft()]:
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def dimension_counts(frames):
    counts = Counter(dimension(frame) for frame in frames)
    return {str(rank): counts[rank] for rank in sorted(counts)}


def span_lists(frames):
    return [list(frame) for frame in sorted(frames)]


def digest(value):
    packed = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("ascii")
    return hashlib.sha256(packed).hexdigest()


def analyze(witness):
    """Check a frame trace and compute its graph with the eight descents cut.

    Counts and shape are restricted to the 4,058-event P104 witness.  This is
    intentionally not an analyzer for arbitrary extended words.  The theorem
    allowing added transports is a separate written argument.
    """
    require(isinstance(witness, dict), "witness must be an object")
    require(
        set(witness) == {"initial_frames", "final_frames", "program"},
        "unexpected witness fields",
    )
    initial = witness["initial_frames"]
    final = witness["final_frames"]
    program = witness["program"]
    require(isinstance(initial, dict) and set(initial) == ROLES, "initial roles")
    require(isinstance(final, dict) and set(final) == ROLES, "final roles")
    require(isinstance(program, list) and len(program) == 4058, "event count")
    state = {role: full_span(basis) for role, basis in initial.items()}
    endpoints = {role: full_span(basis) for role, basis in final.items()}
    sources = {state[f"X{i}"] for i in range(104)}
    target_list = [endpoints[f"Y{i}"] for i in range(104)]
    targets = set(target_list)
    require(len(sources) == 104, "source frames are not distinct")
    require(len(targets) == 104, "target frames are not distinct")
    require(all(dimension(frame) == 1 for frame in sources), "source dimensions")
    require(all(dimension(frame) == 8 for frame in targets), "target dimensions")
    for role in ROLES:
        if not role.startswith("X"):
            require(state[role] == (0,), "non-source initial frame")
        if not role.startswith("Y"):
            require(len(endpoints[role]) == 512, "non-target endpoint frame")

    vertices = set(state.values()) | set(endpoints.values())
    counts = Counter()
    transports = []
    cut = []
    retained = []
    for index, event in enumerate(program):
        require(isinstance(event, list) and event, f"event {index}: shape")
        opcode = event[0]
        require(isinstance(opcode, str) and opcode in ARITIES, f"event {index}: opcode")
        require(len(event) == ARITIES[opcode], f"event {index}: arity")
        counts[opcode] += 1
        role = event[1]
        require(isinstance(role, str), f"event {index}: role type")
        if opcode == "zero":
            require(role == "C" and role not in state, f"event {index}: allocation")
            state[role] = full_span(event[2])
            vertices.add(state[role])
            continue

        require(role in state, f"event {index}: inactive destination")
        if opcode == "transport":
            source, target = full_span(event[2]), full_span(event[3])
            rank = event[4]
            require(state[role] == source, f"event {index}: transport source frame")
            require(
                set(source) <= set(target) or set(target) <= set(source),
                f"event {index}: nonnested transport",
            )
            require(
                type(rank) is int and 0 < rank == abs(dimension(source) - dimension(target)),
                f"event {index}: native rank",
            )
            record = (index, role, rank, source, target)
            transports.append(record)
            if index in CUT_EVENTS:
                require(
                    role == "C" and rank == 7 and dimension(source) == 8 and dimension(target) == 1,
                    f"event {index}: cut descent",
                )
                cut.append(record)
            else:
                retained.append(record)
            state[role] = target
            vertices.update((source, target))
            continue

        frame = full_span(event[-1])
        require(state[role] == frame, f"event {index}: operation frame")
        vertices.add(frame)
        if opcode == "erase":
            require(role == "C", f"event {index}: private erase")
            del state[role]
            continue

        other = event[2]
        require(isinstance(other, str) and other in state, f"event {index}: inactive source")
        require(other != role and state[other] == frame, f"event {index}: common frame")
        if opcode == "copy":
            require(role == "C", f"event {index}: private copy")
        else:
            require(type(event[3]) in (str, int), f"event {index}: scalar format")
            try:
                Fraction(event[3])
            except (ValueError, ZeroDivisionError) as exc:
                raise ValueError(f"event {index}: invalid rational scalar") from exc

    require(dict(counts) == EVENT_COUNTS, "event opcode census")
    require(state == endpoints, "final frame trace")
    require(tuple(record[0] for record in cut) == CUT_EVENTS, "cut event inventory")
    require(
        tuple(record[0] for record in transports if record[1] == "C") == CUT_EVENTS,
        "private transport inventory",
    )

    arrows = [(record[3], record[4]) for record in retained]
    forward = walk(sources, arrows)
    backward = walk(targets, [(target, source) for source, target in arrows])
    remaining = vertices - forward
    unclassified = vertices - forward - backward
    signatures = [
        [index, role, rank, list(source), list(target)]
        for index, role, rank, source, target in transports
    ]
    side = lambda frame: "R" if frame in forward else "T"
    direction_counts = Counter(side(source) + side(target) for source, target in arrows)
    distinct_direction_counts = Counter(
        side(source) + side(target) for source, target in set(arrows)
    )
    return {
        "vertex_count": len(vertices),
        "source_frame_count": len(sources),
        "target_frame_count": len(targets),
        "transport_occurrences": len(transports),
        "retained_transport_occurrences": len(retained),
        "distinct_retained_arrows": len(set(arrows)),
        "source_reachable_frames": len(forward),
        "target_coreachable_frames": len(backward),
        "reachable_target_indices": [i for i, frame in enumerate(target_list) if frame in forward],
        "reachable_target_count": len(targets & forward),
        "reachable_by_dimension": dimension_counts(forward),
        "coreachable_by_dimension": dimension_counts(backward),
        "reachable_frames": span_lists(forward),
        "coreachable_frames": span_lists(backward),
        "unreachable_frames": span_lists(remaining),
        "unclassified_count": len(unclassified),
        "unclassified_by_dimension": dimension_counts(unclassified),
        "partition_complete": vertices == forward | backward and not forward & backward,
        "cut_events": list(CUT_EVENTS),
        "cut_sources_reachable": all(record[3] in forward for record in cut),
        "cut_targets_coreachable": all(record[4] in backward for record in cut),
        "retained_arrow_directions": dict(sorted(direction_counts.items())),
        "distinct_retained_arrow_directions": dict(sorted(distinct_direction_counts.items())),
        "edge_restoration_target_counts": {
            str(index): len(walk(sources, arrows + [(source, target)]) & targets)
            for index, _, _, source, target in cut
        },
        "all_restored_target_count": len(
            walk(sources, arrows + [(record[3], record[4]) for record in cut]) & targets
        ),
        "transport_event_signatures_sha256": digest(signatures),
        "reachable_frames_sha256": digest(span_lists(forward)),
        "coreachable_frames_sha256": digest(span_lists(backward)),
    }
