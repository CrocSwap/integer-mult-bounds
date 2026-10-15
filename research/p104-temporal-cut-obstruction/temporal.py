# SPDX-License-Identifier: Apache-2.0
"""Saturated information flow through the frozen P104 chronological skeleton.

The relaxation allows arbitrary linear mixing among *all* live registers in
the same canonical frame at every event boundary.  It thus contains every
scalar redesign with the fixed transports and private-register lifetimes.
No channel producer or native compiler is imported.
"""

from collections import Counter
from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical_frame(vectors):
    """Return the actual binary subspace, rejecting a dependent input basis."""
    require(isinstance(vectors, list), "frame basis must be a list")
    require(len(vectors) <= 9, "frame exceeds the nine-dimensional label space")
    space = {0}
    for vector in vectors:
        require(type(vector) is int and 0 < vector < 512,
                "frame vector must be a nonzero nine-bit integer")
        require(vector not in space, "dependent frame basis")
        space.update(value ^ vector for value in tuple(space))
    return tuple(sorted(space))


def _normalize(witness):
    """Check every literal operation before considering the larger relaxation."""
    require(isinstance(witness, dict), "witness must be an object")
    initial = witness["initial_frames"]
    final = witness["final_frames"]
    program = witness["program"]
    require(isinstance(initial, dict) and isinstance(final, dict),
            "endpoint frames must be objects")
    require(isinstance(program, list), "program must be a list")
    expected = ({f"X{i}" for i in range(104)}
                | {f"Y{i}" for i in range(104)}
                | {f"Q{i}" for i in range(8)}
                | {f"G{i}" for i in range(32)}
                | {f"D{i}" for i in range(32)})
    require(set(initial) == set(final) == expected,
            "P104 requires 104 sources, 104 targets and 72 dirty helpers")
    frames = {name: canonical_frame(frame) for name, frame in initial.items()}
    start = dict(frames)
    finish = {name: canonical_frame(frame) for name, frame in final.items()}
    normalized = []
    profile = Counter()
    operations = Counter()
    lifetime = None
    lifetimes = 0
    maximum_live = len(frames)
    cut_edges = []

    for index, event in enumerate(program):
        require(isinstance(event, list) and event, f"malformed event {index}")
        operation = event[0]
        operations[operation] += 1
        if operation == "transport":
            require(len(event) == 5, f"transport arity at {index}")
            _, name, old, new, rank = event
            old_frame = canonical_frame(old)
            new_frame = canonical_frame(new)
            require(name in frames and frames[name] == old_frame,
                    f"transport entry frame at {index}")
            require(type(rank) is int and rank > 0
                    and rank == abs(len(old) - len(new)),
                    f"positive transport rank at {index}")
            require(set(old_frame) <= set(new_frame)
                    or set(new_frame) <= set(old_frame),
                    f"transport frames are not nested at {index}")
            if name == "C" and len(old) == 8 and len(new) == 1:
                require(lifetime is not None and lifetime["copied"]
                        and not lifetime["dropped"],
                        f"private descent lifetime at {index}")
                lifetime["dropped"] = True
                cut_edges.append(index)
            frames[name] = new_frame
            profile[rank] += 1
            normalized.append((operation, name, old_frame, new_frame, rank))
        elif operation == "zero":
            require(len(event) == 3, f"zero arity at {index}")
            _, name, frame = event
            common = canonical_frame(frame)
            require(name == "C" and name not in frames and lifetime is None,
                    f"owned private allocation at {index}")
            frames[name] = common
            lifetime = {"copied": False, "dropped": False, "clean": True}
            lifetimes += 1
            maximum_live = max(maximum_live, len(frames))
            normalized.append((operation, name, common))
        elif operation == "erase":
            require(len(event) == 3, f"erase arity at {index}")
            _, name, frame = event
            common = canonical_frame(frame)
            require(name == "C" and name in frames and frames[name] == common
                    and lifetime is not None and lifetime["copied"]
                    and lifetime["dropped"],
                    f"owned private discard at {index}")
            del frames[name]
            lifetime = None
            normalized.append((operation, name, common))
        elif operation == "copy":
            require(len(event) == 4, f"copy arity at {index}")
            _, target, source, frame = event
            common = canonical_frame(frame)
            require(target == "C" and target != source and source in frames
                    and target in frames
                    and frames[target] == frames[source] == common
                    and lifetime is not None and lifetime["clean"]
                    and not lifetime["copied"],
                    f"owned common-frame copy at {index}")
            lifetime["copied"] = True
            lifetime["clean"] = False
            normalized.append((operation, target, source, common))
        elif operation == "add":
            require(len(event) == 5, f"add arity at {index}")
            _, target, source, coefficient, frame = event
            common = canonical_frame(frame)
            require(target != source and target in frames and source in frames
                    and frames[target] == frames[source] == common,
                    f"common-frame addition at {index}")
            try:
                value = Fraction(coefficient)
            except (TypeError, ValueError, ZeroDivisionError) as error:
                raise ValueError(f"invalid rational coefficient at {index}") from error
            if target == "C" and value:
                lifetime["clean"] = False
            normalized.append((operation, target, source, value, common))
        else:
            raise ValueError(f"unknown operation at {index}: {operation}")

    require(lifetime is None and frames == finish, "final frame/lifetime mismatch")
    require(lifetimes == 8 and len(cut_edges) == 8,
            "expected eight separate rank-seven private descents")
    return start, finish, normalized, cut_edges, {
        "event_count": len(program),
        "event_boundary_count": len(program) + 1,
        "initial_register_count": len(start),
        "maximum_live_register_count": maximum_live,
        "private_lifetime_count": lifetimes,
        "operation_counts": dict(sorted(operations.items())),
        "paid_profile": {str(rank): count for rank, count in sorted(profile.items())},
        "rank_mass": sum(rank * count for rank, count in profile.items()),
    }


def _saturate(frames, information):
    """Allow unrestricted common-chart mixing, including feedback within a cut."""
    groups = {}
    for name, frame in frames.items():
        groups.setdefault(frame, []).append(name)
    for names in groups.values():
        union = 0
        for name in names:
            union |= information[name]
        for name in names:
            information[name] = union
    return len(groups)


def _forward(initial, events, deleted):
    frames = dict(initial)
    information = {name: (1 << int(name[1:]) if name.startswith("X") else 0)
                   for name in frames}
    counts = {}
    ever_targets = set()
    groups_visited = 0

    def close():
        nonlocal groups_visited
        groups_visited += _saturate(frames, information)
        ever_targets.update(name for name in frames
                            if name.startswith("Y") and information[name])

    close()
    for index, event in enumerate(events):
        operation, name = event[:2]
        if operation == "transport":
            if index in deleted:
                counts[index] = information[name].bit_count()
                information[name] = 0
            frames[name] = event[3]
        elif operation == "zero":
            frames[name] = event[2]
            information[name] = 0
        elif operation == "erase":
            del frames[name]
            del information[name]
        # Literal add/copy edges are already contained in saturated common-frame
        # access. Retaining all input dependencies makes this an upper bound.
        close()
    return information, counts, sorted(ever_targets), groups_visited


def _backward(final, events, deleted):
    frames = dict(final)
    information = {name: (1 << int(name[1:]) if name.startswith("Y") else 0)
                   for name in frames}
    counts = {}
    ever_sources = set()
    groups_visited = 0

    def close():
        nonlocal groups_visited
        groups_visited += _saturate(frames, information)
        ever_sources.update(name for name in frames
                            if name.startswith("X") and information[name])

    close()
    for index in range(len(events) - 1, -1, -1):
        event = events[index]
        operation, name = event[:2]
        if operation == "transport":
            if index in deleted:
                counts[index] = information[name].bit_count()
                information[name] = 0
            frames[name] = event[2]
        elif operation == "zero":
            del frames[name]
            del information[name]
        elif operation == "erase":
            frames[name] = event[2]
            information[name] = 0
        close()
    return information, counts, sorted(ever_sources), groups_visited


def analyze(witness):
    """Return a deterministic exact receipt for the eight-edge temporal cut."""
    initial, final, events, cut_edges, totals = _normalize(witness)
    deleted = set(cut_edges)
    forward, incoming, ever_targets, forward_groups = _forward(initial, events, deleted)
    backward, outgoing, ever_sources, backward_groups = _backward(final, events, deleted)
    reached_targets = sorted(name for name in final
                             if name.startswith("Y") and forward[name])
    reached_sources = sorted(name for name in initial
                             if name.startswith("X") and backward[name])
    require(not reached_targets, "deleted edges do not cut every source-to-target path")
    require(not reached_sources, "backward replay found a source-to-target bypass")
    require(forward_groups == backward_groups, "forward/backward frame census differs")
    return {
        "status": "PASS_P104_FROZEN_TEMPORAL_EIGHT_EDGE_CUT",
        **totals,
        "source_count": 104,
        "target_count": 104,
        "dirty_helper_count": 72,
        "common_frame_groups_saturated": forward_groups,
        "deleted_edge_count": len(cut_edges),
        "deleted_edges": [
            {
                "event_index": index,
                "register": events[index][1],
                "old_dimension": 8,
                "new_dimension": 1,
                "native_rank": events[index][4],
                "reachable_source_inputs_before_deletion": incoming[index],
                "reachable_target_outputs_after_deletion": outgoing[index],
            }
            for index in cut_edges
        ],
        "forward_reachable_final_targets": reached_targets,
        "backward_reachable_initial_sources": reached_sources,
        "forward_ever_reachable_targets": ever_targets,
        "backward_ever_reachable_sources": ever_sources,
        "source_to_target_coefficient_rank_upper_bound": len(cut_edges),
        "relaxation": (
            "Arbitrary common-frame linear mixing among all live registers at every "
            "event boundary; the native transport sequence and private lifetimes are fixed."
        ),
    }
