#!/usr/bin/env python3
"""Published G20 frame routes have no inverse, and non-member moves stay unpaired.

The cut algebra is Nick Petalas's free-carrier checker for Ali Romman's
PR5708 word. This file does not import that package. Apache-2.0.
"""
from collections import Counter, defaultdict
import gzip
import hashlib
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "research/g20-conjugation-admission/WORD.json.gz"
PATHS = "research/g20-conjugation-admission/PATHS.json"
FRAMES = ("research/g20-conjugation-admission/prior/prior/prior/source/"
          "vendor/g20/inputs/FRAMES.json")
HELPER_BEGIN = 222
WITNESS_HELPER = 222
WITNESS_EDGE = (1, 517, 1)
OFFROUTE_CUT = 7407
OFFROUTE_FIELD = 208
OFFROUTE_FRAME = 509


def require(ok, message):
    if not ok:
        raise ValueError(message)


def dependencies(rows):
    basis, result = {}, []
    width = max((row.bit_length() for row in rows), default=0)
    for i, source in enumerate(rows):
        row, coefficients = source, 1 << i
        for _ in range(width + 1):
            if not row:
                result.append(coefficients)
                break
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row, coefficients
                break
            old, combination = basis[pivot]
            row ^= old
            coefficients ^= combination
        else:
            raise ValueError("dependency elimination bound")
    return result


def rank_low(rows):
    basis = {}
    width = max((row.bit_length() for row in rows), default=0)
    for source in rows:
        row = source
        for _ in range(width + 1):
            if not row:
                break
            pivot = (row & -row).bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
        else:
            raise ValueError("rank elimination bound")
    return len(basis)


def combine(rows, coefficients):
    value = 0
    require(coefficients.bit_length() <= len(rows), "coefficient width")
    for i, row in enumerate(rows):
        if coefficients >> i & 1:
            value ^= row
    return value


def eligible(rows, outside):
    masked = [row & outside for row in rows]
    kernel = dependencies(masked)
    require(len(kernel) == len(rows) - rank_low(masked), "kernel dimension")
    require(rank_low(kernel) == len(kernel), "kernel independence")
    require(all(combine(masked, item) == 0 for item in kernel), "kernel equations")
    return kernel, [combine(rows, item) for item in kernel]


def pairings(prefix, suffix, outside):
    left, inputs = eligible(prefix, outside)
    right, outputs = eligible(suffix, outside)
    boundary = [sum(((one & two).bit_count() & 1) << j
                    for j, two in enumerate(outputs)) for one in inputs]
    internal = [sum(((one & two).bit_count() & 1) << j
                    for j, two in enumerate(right)) for one in left]
    return len(left), len(right), rank_low(boundary), rank_low(internal)


def frame_shapes(frames):
    from fractions import Fraction

    def rows_of(entry):
        basis = {}
        for source in entry["B"]:
            row = list(map(Fraction, source))
            for pivot in sorted(basis):
                factor = row[pivot]
                row = [x - factor * y for x, y in zip(row, basis[pivot])]
            pivot = next((i for i, x in enumerate(row) if x), None)
            if pivot is None:
                continue
            factor = row[pivot]
            row = [x / factor for x in row]
            for old in tuple(basis):
                factor = basis[old][pivot]
                basis[old] = [x - factor * y for x, y in zip(basis[old], row)]
            basis[pivot] = row
        return tuple(tuple(row) for _, row in sorted(basis.items()))

    spaces = {int(i): rows_of(entry) for i, entry in frames.items()}
    shapes = sorted(set(spaces.values()))
    labels = {i: shapes.index(space) for i, space in spaces.items()}
    labels[None] = None
    return labels, shapes


def group_contract(word, labels, shapes):
    groups = defaultdict(set)
    owned = set(word["owned"])
    for helper in range(HELPER_BEGIN, len(word["start"])):
        if helper not in owned:
            key = labels[word["start"][helper]], labels[word["final"][helper]]
            groups[key].add(helper)
    compatible, masks = defaultdict(list), {}
    full = (1 << len(word["start"])) - 1
    for group, members in groups.items():
        entrance, exit_frame = group
        masks[group] = full ^ sum(1 << helper for helper in members)
        for index, shape in enumerate(shapes):
            if not len(shapes[exit_frame]) < len(shape) < len(shapes[entrance]):
                continue
            if frame_contains(shapes[entrance], shape) and frame_contains(shape, shapes[exit_frame]):
                compatible[index].append(group)
    return groups, compatible, masks


def frame_contains(outer, inner):
    from fractions import Fraction
    basis = {}
    for source in list(outer) + list(inner):
        row = list(map(Fraction, source))
        for pivot in sorted(basis):
            factor = row[pivot]
            row = [x - factor * y for x, y in zip(row, basis[pivot])]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is None:
            continue
        factor = row[pivot]
        row = [value / factor for value in row]
        for old in tuple(basis):
            factor = basis[old][pivot]
            basis[old] = [x - factor * y for x, y in zip(basis[old], row)]
        basis[pivot] = row
    return tuple(tuple(row) for _, row in sorted(basis.items())) == outer


def basis_of(rows):
    basis = {}
    for source in rows:
        row, guard = source, 0
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
            guard += 1
            require(guard <= 800, "elimination bound")
    return basis


def in_span(basis, vec):
    for pivot, row in basis.items():
        if (vec >> pivot) & 1:
            vec ^= row
    return vec == 0


def load():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    expected = {row["path"]: row["sha256"] for row in manifest["files"] if row["usage"] == "input"}
    require(set(expected) == {WORD, PATHS, FRAMES}, "three live inputs")
    payloads = {}
    for path in (WORD, PATHS, FRAMES):
        raw = (ROOT / path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected[path], "hash " + path)
        decoded = gzip.decompress(raw) if path.endswith(".gz") else raw
        payloads[path] = json.loads(decoded)
    frames = payloads[FRAMES]["frames"]
    edges = [tuple(edge) for bundle in payloads[PATHS].values() for edge in bundle]
    return payloads[WORD], frames, edges


def suffix_start(events, count):
    columns, erased = [1 << i for i in range(count)], {}
    for index in reversed(range(len(events))):
        event = events[index]
        op, dest = event[:2]
        if op == "ADD":
            columns[event[2]] ^= columns[dest]
        elif op == "ERASE":
            erased[index] = columns[dest]
            columns[dest] = 0
    return columns, erased


def apply_event(event, index, prefix, suffix, erased, state, labels, banks):
    op, dest = event[:2]
    before = labels[state[dest]]
    if op == "ADD":
        source = event[2]
        require(state[dest] == state[source] == event[3], "ADD common frame")
        prefix[dest] ^= prefix[source]
        suffix[source] ^= suffix[dest]
        return {labels[state[dest]]}
    if op == "ERASE":
        prefix[dest] = 0
        suffix[dest] = erased[index]
        state[dest] = event[2]
    elif op in ("Q", "ZERO_Q"):
        require(state[dest] == event[2], "query entrance")
        state[dest] = event[3]
    elif op == "INIT":
        state[dest] = event[2]
    else:
        raise ValueError("unknown event")
    after = labels[state[dest]]
    banks[before].remove(dest)
    banks[after].add(dest)
    return {before, after}


def kernel_controls():
    checked = 0
    for rows in itertools.product(range(8), repeat=3):
        kernel = dependencies(rows)
        exhaustive = {x for x in range(8) if combine(rows, x) == 0}
        generated = {combine(kernel, x) for x in range(1 << len(kernel))}
        require(generated == exhaustive, "exhaustive dependency control")
        checked += 1
    require(pairings([1], [1], 0)[2] == 1, "unit boundary channel")
    require(pairings([1], [2], 0)[2] == 0, "orthogonal images")
    return checked + 2


def route_facts(frames, edges):
    dims = {int(i): entry["dim"] for i, entry in frames.items()}
    require(len(edges) == 2369, "route count")
    reverses = {(b, a) for a, b, _ in edges}
    for src, dst, rank in edges:
        require(dims[dst] < dims[src], "dimension drop")
        require(rank == dims[src] - dims[dst], "rank equals dimension drop")
        require((src, dst) not in reverses, "reverse edge")
    require(sum(entry["dim"] == 8 for entry in frames.values()) == 1, "one dim-8 frame")
    require(dims[1] == 8, "frame 1 is dim 8")
    require(not any(dst == 1 for _, dst, _ in edges), "frame 1 has an entrance")
    require(WITNESS_EDGE in edges, "witness edge published")
    return dims


def opening_witness(word, labels, shapes, groups, compatible, masks, edges):
    group = next(key for key, members in groups.items() if len(members) == 413)
    mask, members = masks[group], groups[group]
    require(WITNESS_HELPER in members, "witness helper is public")
    require(word["start"][WITNESS_HELPER] == 1, "helper starts at frame 1")
    prefix = [1 << i for i in range(len(word["start"]))]
    suffix, _ = suffix_start(word["records"], len(word["start"]))
    odd = []
    for helper in sorted(members):
        row, column = prefix[helper], suffix[helper]
        require((row & mask) == 0 and (column & mask) == 0, "helper support")
        if (row & column).bit_count() & 1:
            odd.append(helper)
    require(odd == sorted(members), "every public helper has odd self-pairing")
    require(pairings([prefix[WITNESS_HELPER]], [suffix[WITNESS_HELPER]], mask) == (1, 1, 1, 1),
            "witness singleton channel")
    occupied = Counter(labels[frame] for frame in word["start"] if frame is not None)
    exits = []
    for src, dst, rank in edges:
        if src != 1:
            continue
        shape = labels[dst]
        if occupied[shape] == 0 and group in compatible[shape]:
            exits.append((src, dst, rank))
    require(WITNESS_EDGE in exits, "witness exit is an empty compatible route")
    require(min(rank for _src, _dst, rank in exits) == 1, "cheapest empty exit")
    first = next(i for i, event in enumerate(word["records"])
                 if event[1] == WITNESS_HELPER or (event[0] == "ADD" and event[2] == WITNESS_HELPER))
    require(first == 5638 and word["records"][first][:4] == ["ADD", 222, 98, 1], "frame-1 ADD")
    require(all(event[0] == "ADD" and event[3] == 1 for event in word["records"][5638:5644]),
            "six opening ADDs stay on frame 1")
    ranks = Counter(rank for _src, _dst, rank in exits)
    return {"public_helpers": len(members), "empty_compatible_exits": len(exits),
            "empty_exit_ranks": dict(sorted(ranks.items())),
            "witness_edge": list(WITNESS_EDGE), "first_add": first}


def scan(word, labels, shapes, groups, compatible, masks, edges):
    count = len(word["start"])
    events = word["records"]
    prefix = [1 << i for i in range(count)]
    suffix, erased = suffix_start(events, count)
    state = word["start"][:]
    banks = defaultdict(set)
    for index, frame in enumerate(state):
        banks[labels[frame]].add(index)
    adjacency = defaultdict(list)
    for src, dst, rank in edges:
        adjacency[src].append((dst, rank, labels[dst]))
    members = {group: set(helpers) for group, helpers in groups.items()}
    cache = {}

    def rebuild(shape):
        if shape is None:
            return
        slots = banks.get(shape)
        if not slots or shape not in compatible:
            cache.pop(shape, None)
            return
        built = []
        for group in compatible[shape]:
            mask = masks[group]
            built.append((group, mask,
                          basis_of([prefix[i] & mask for i in slots]),
                          basis_of([suffix[i] & mask for i in slots]),
                          tuple(slots)))
        cache[shape] = built

    for shape in list(banks):
        rebuild(shape)
    singleton_hits = 0
    published_hits = 0
    tested = 0
    offroute = None

    def parity(cut):
        nonlocal singleton_hits
        for field in range(count):
            for group, mask in masks.items():
                if field in members[group]:
                    continue
                row, column = prefix[field] & mask, suffix[field] & mask
                if row == 0 and column == 0 and ((prefix[field] & suffix[field]).bit_count() & 1):
                    singleton_hits += 1

    def published(field, cut):
        nonlocal tested, published_hits
        frame = state[field]
        if frame is None:
            return
        row, column = prefix[field], suffix[field]
        for _dst, _rank, shape in adjacency[frame]:
            built = cache.get(shape)
            if not built or field in banks[shape]:
                continue
            for group, mask, left, right, slots in built:
                if field in members[group]:
                    continue
                if not (in_span(left, row & mask) or in_span(right, column & mask)):
                    continue
                tested += 1
                outcome = pairings([prefix[i] for i in slots] + [row],
                                   [suffix[i] for i in slots] + [column], mask)
                published_hits += int(outcome[2] > 0)

    def consider(cut):
        parity(cut)
        for field in range(count):
            published(field, cut)

    consider(-1)
    for index, event in enumerate(events):
        dirty = apply_event(event, index, prefix, suffix, erased, state, labels, banks)
        for shape in dirty:
            rebuild(shape)
        if index == OFFROUTE_CUT:
            offroute = offroute_view(state, banks, prefix, suffix, labels, masks, groups)
        retest = {event[1]}
        if event[0] == "ADD":
            retest.add(event[2])
        for field in range(count):
            frame = state[field]
            if frame is None:
                continue
            if any(shape in dirty for _dst, _rank, shape in adjacency[frame]):
                retest.add(field)
        parity(index)
        for field in retest:
            published(field, index)
    require(state == word["final"], "final frames")
    require(suffix == [1 << i for i in range(count)], "suffix closure")
    require(singleton_hits == 0, "non-member singleton channel")
    require(published_hits == 0, "published non-member channel")
    require(offroute is not None, "off-route control ran")
    return {"singleton_hits": singleton_hits, "published_hits": published_hits,
            "span_admitted_pairings": tested, "offroute": offroute}


def offroute_view(state, banks, prefix, suffix, labels, masks, groups):
    require(state[OFFROUTE_FIELD] == 622, "off-route field frame")
    shape = labels[OFFROUTE_FRAME]
    slots = tuple(sorted(banks[shape]))
    require(OFFROUTE_FIELD not in slots and len(slots) == 11, "off-route bank")
    group = next(key for key, members in groups.items() if len(members) == 413)
    mask = masks[group]
    base = pairings([prefix[i] for i in slots], [suffix[i] for i in slots], mask)
    augmented = pairings([prefix[i] for i in slots] + [prefix[OFFROUTE_FIELD]],
                         [suffix[i] for i in slots] + [suffix[OFFROUTE_FIELD]], mask)
    require(base[2] == 0 and augmented[2] == 1 and augmented[3] == 1, "off-route detector")
    return {"field": OFFROUTE_FIELD, "src": 622, "dst": OFFROUTE_FRAME,
            "base": list(base), "augmented": list(augmented)}


def main():
    word, frames, edges = load()
    controls = kernel_controls()
    dims = route_facts(frames, edges)
    labels, shapes = frame_shapes(frames)
    groups, compatible, masks = group_contract(word, labels, shapes)
    opening = opening_witness(word, labels, shapes, groups, compatible, masks, edges)
    census = scan(word, labels, shapes, groups, compatible, masks, edges)
    require((622, 509) not in {(a, b) for a, b, _ in edges}, "off-route edge absent")
    report = {"claim_type": "finite route obstruction with one off-route pairing witness",
              "edges": len(edges), "frame_1_dimension": dims[1],
              "opening": opening, "census": census, "controls": controls,
              "round_trip_emits": False, "new_kappa": False}
    print(json.dumps(report, sort_keys=True, indent=2))
    print("PASS_G20_FRAME_ROUND_TRIP_GAP")


if __name__ == "__main__":
    main()
