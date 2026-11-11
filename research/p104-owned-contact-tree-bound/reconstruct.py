"""Reconstruct the owned-contact projection and signed invoice from literal inputs."""
from collections import Counter, defaultdict
from functools import cache


def gf2_rank(rows):
    pivots = {}
    for v in rows:
        while v:
            pivot = v.bit_length()
            if pivot not in pivots:
                pivots[pivot] = v
                break
            v ^= pivots[pivot]
    return len(pivots)


def reconstruct(word, caller, invoice):
    public = word["public"]
    program = word["program"]
    frames = word["frames"]
    dims = [len(frame) for frame in frames]
    assert all(gf2_rank(frame) == dim for frame, dim in zip(frames, dims, strict=True))
    owned = word["owned_fields"]

    @cache
    def rank(a, b, is_owned):
        if a == b:
            return 0
        gap = dims[b] - dims[a]
        relative = 2 * gf2_rank(frames[a] + frames[b]) - dims[a] - dims[b]
        assert relative == abs(gap) > 0
        assert is_owned or gap > 0
        return relative

    local = {}
    for clock, (op, role, *args) in enumerate(program):
        if role >= public and (
            op in ("INIT", "CLEAR", "SCALE")
            or op in ("ADD", "COPY") and args[0] >= public
        ):
            local[clock] = dims[args[-1]]

    current = word["initial"] + [None] * owned
    previous = [(-1, f) for f in word["initial"]] + [None] * owned
    pending = [None] * (public + owned)
    adjacency = {clock: set() for clock in local}
    internal = Counter()
    boundary = defaultdict(list)
    native_paid = Counter()
    edge_count = 0
    lifetimes = 0

    def touch(role, clock, frame):
        nonlocal edge_count
        assert current[role] == frame
        old_clock, old_frame = previous[role]
        move = pending[role]
        assert (old_frame == frame and move is None) or move == (old_frame, frame)
        assert old_clock < clock
        edge_count += 1
        previous[role] = clock, frame
        pending[role] = None
        if old_clock not in local and clock not in local:
            return
        assert role >= public
        if old_clock in local and clock in local:
            adjacency[old_clock].add(clock)
            adjacency[clock].add(old_clock)
            internal[old_clock, clock] += 1
        elif old_clock in local:
            boundary[old_clock].append(dims[frame])
        else:
            boundary[clock].append(dims[old_frame])

    for clock, (op, role, *args) in enumerate(program):
        if op == "MOVE":
            start, end, is_owned = args
            assert current[role] == start and is_owned == (role >= public)
            assert previous[role] is not None and pending[role] is None
            native_paid[rank(start, end, is_owned)] += 1
            current[role] = end
            pending[role] = start, end
        elif op == "INIT":
            (frame,) = args
            assert role >= public and current[role] is previous[role] is pending[role] is None
            current[role] = frame
            previous[role] = clock, frame
        else:
            assert op in ("ADD", "COPY", "SCALE", "CLEAR")
            frame = args[-1]
            touch(role, clock, frame)
            if op in ("ADD", "COPY") and args[0] != role:
                touch(args[0], clock, frame)
            if op == "CLEAR":
                assert role >= public
                current[role] = previous[role] = None
                lifetimes += 1

    assert current == word["final"] + [None] * owned and lifetimes == 70
    assert all(v is None for v in previous[public:])
    for role, frame in enumerate(word["final"]):
        touch(role, len(program), frame)
    assert all(v is None for v in pending)
    assert edge_count == 137891 and sum(native_paid.values()) == 6280

    # Assign each mutable contact to exactly one connected component.
    component = {}
    for root in sorted(local):
        if root in component:
            continue
        component[root] = root
        queue = [root]
        for clock in queue:
            for neighbor in sorted(adjacency[clock]):
                if neighbor not in component:
                    component[neighbor] = root
                    queue.append(neighbor)
    regions = {
        root: {"contacts": [], "links": [], "boundary": []}
        for root in sorted(set(component.values()))
    }
    for clock, dim in sorted(local.items()):
        row = regions[component[clock]]
        row["contacts"].append([clock, dim])
        row["boundary"].extend([clock, b] for b in sorted(boundary[clock]))
    for (u, v), count in sorted(internal.items()):
        assert component[u] == component[v]
        regions[component[u]]["links"].append([u, v, count])

    main = set(word["live"]) | {r + 112 for r in word["live"]} | set(
        word["hosted"]["X2"] + word["hosted"]["Y2"]
    )
    assert len(main) == 400
    native_targets = Counter(
        rank(a, b, False)
        for role, (a, b) in enumerate(zip(word["initial"], word["final"], strict=True))
        if role not in main
    )
    assert 0 not in native_targets and sum(native_targets.values()) == 1101
    copies = [event[1] for event in caller["events"] if event[0] == "J"]
    assert copies == list(range(1, 18))
    paid, targets = (
        Counter({r: len(copies) * q for r, q in hist.items()})
        for hist in (native_paid, native_targets)
    )
    for spec in caller["types"].values():
        for sign, offset, *bits in spec["diagonal"]:
            assert sign == -1 and offset == 0 and len(bits) == len(copies)
            targets[1 + 8 * sum(bits)] += len(spec["ports"])
    for event in caller["events"]:
        if event[0] == "J":
            continue
        ty, op, _, *args = event
        n = len(caller["types"][ty]["ports"])
        if op == "QUERY":
            paid[1] += n
        elif op in ("IDLE_ONE", "IDLE_ODD"):
            paid[8 * len(args[0]) + (op == "IDLE_ODD")] += n
    assert {str(r): q for r, q in paid.items()} == invoice["P"]
    assert {str(r): q for r, q in targets.items()} == invoice["T"]
    assert sum(r * (targets[r] - paid[r]) for r in targets.keys() | paid.keys()) == invoice["S"]
    return {
        "native_contact_edges": edge_count,
        "native_paid_moves": sum(native_paid.values()),
        "copies": len(copies),
        "max_old_chart_dimension": max(dims),
        "regions": list(regions.values()),
    }
