# SPDX-License-Identifier: Apache-2.0
"""Enumerate all allowed frames and independently trace source dependencies."""

import hashlib
import json
import sys
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
INPUTS = (
    "research/p104-joint-unit-flags/CERTIFICATE.json",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-native-channel/inputs/P104-FIXTURE.json",
)
PROVENANCE = {
    "certificates/selected-result.json",
    "docs/research/agent-task-catalog.json",
}
LIMIT = 2_000_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def read_bytes(path):
    require(path.stat().st_size <= LIMIT, "input size bound")
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "read size bound")
    return raw


def read_json(path):
    return json.loads(read_bytes(path), object_pairs_hook=unique)


def authenticated_inputs():
    records = read_json(PACKAGE / "SOURCES.json")["files"]
    require(type(records) is list and len(records) == 5, "five source records")
    pins = {}
    for record in records:
        name, usage = record["path"], record["usage"]
        require(name not in pins, "unique source records")
        require(
            (name in INPUTS and usage == "input")
            or (name in PROVENANCE and usage == "provenance"),
            "fixed source inventory",
        )
        pins[name] = record["sha256"]
    require(set(pins) == set(INPUTS) | PROVENANCE, "complete source inventory")
    result = []
    for name in INPUTS:
        raw = read_bytes(ROOT / name)
        require(hashlib.sha256(raw).hexdigest() == pins[name], "input SHA256")
        result.append(json.loads(raw, object_pairs_hook=unique))
    return result


def space(basis):
    """Represent the literal members of a binary subspace by a 512-bit integer."""
    require(type(basis) is list and len(basis) <= 9, "basis size")
    points = [0]
    for vector in basis:
        require(type(vector) is int and 0 < vector < 512, "binary vector")
        require(vector not in points, "independent basis")
        points += [point ^ vector for point in points]
    require(len(points) == 1 << len(basis), "span size")
    return sum(1 << point for point in points)


def dimension(frame):
    count = frame.bit_count()
    require(count > 0 and count & (count - 1) == 0, "frame cardinality")
    return count.bit_length() - 1


def original_paths(word):
    names = [f"{kind}{index}" for kind in "XY" for index in range(104)]
    paths = {name: [space(word["initial_frames"][name])] for name in names}
    require(type(word["program"]) is list and len(word["program"]) == 4058, "word size")
    for event in word["program"]:
        op, name = event[:2]
        if op in {"add", "copy", "zero", "erase"}:
            require(not name.startswith("X"), "immutable original X")
            if op in {"add", "copy"}:
                require(not event[2].startswith("Y"), "unread original Y")
            continue
        require(op == "transport", "original opcode")
        if name not in paths:
            continue
        old, new = space(event[2]), space(event[3])
        require(
            paths[name][-1] == old and old & new == old and old != new, "nested path"
        )
        rank = event[4]
        require(type(rank) is int and rank == dimension(new) - dimension(old), "rank")
        paths[name].append(new)
    for name in names:
        path = paths[name]
        require(
            len(path) <= 10 and path[-1] == space(word["final_frames"][name]),
            "data exit",
        )
        endpoints = (1, 9) if name.startswith("X") else (0, 8)
        require(
            (dimension(path[0]), dimension(path[-1])) == endpoints, "data endpoints"
        )
    require(len({paths[f"X{s}"][0] for s in range(104)}) == 104, "distinct X lines")
    require(len({paths[f"Y{t}"][-1] for t in range(104)}) == 104, "distinct Y caps")
    return paths


def quotient_bases():
    """All reduced row echelon subspaces of the five-dimensional quotient."""
    result = [[] for _ in range(6)]
    for size in range(6):
        for pivots in combinations(range(5), size):
            free = [
                (i, j)
                for i, pivot in enumerate(pivots)
                for j in range(pivot + 1, 5)
                if j not in pivots
            ]
            require(len(free) <= 6, "RREF free-entry bound")
            for bits in range(1 << len(free)):
                rows = [1 << pivot for pivot in pivots]
                for index, (i, j) in enumerate(free):
                    if bits >> index & 1:
                        rows[i] |= 1 << j
                result[size].append(rows)
        require(
            len({space(rows) for rows in result[size]}) == len(result[size]),
            "unique quotient spaces",
        )
    require(
        [len(rows) for rows in result] == [1, 31, 155, 155, 31, 1], "quotient counts"
    )
    return result


def frame_choices(basis, quotients):
    space(basis)
    require(len(basis) == 9, "complete flag")
    result = {1: {space(basis[:1])}, 8: {space(basis[:8])}}
    for d in range(2, 8):
        choices = set()
        for rows in quotients[d - 2]:
            lifted = []
            for row in rows:
                vector = 0
                for j in range(5):
                    if row >> j & 1:
                        vector ^= basis[2 + j]
                lifted.append(vector)
            choices.add(space(basis[:2] + lifted))
        require(len(choices) == len(quotients[d - 2]), "lifted quotient bijection")
        result[d] = choices
    return result


def helper_choices(certificate, paths, quotients):
    rows = certificate["helpers"]
    require(type(rows) is list and len(rows) == 208, "208 helpers")
    choices, departures, arrivals = [], set(), set()
    for row in rows:
        s, a, t, b = [
            row[key]
            for key in ("source", "departure_choice", "target", "arrival_choice")
        ]
        require(all(type(v) is int for v in (s, a, t, b)), "integer slots")
        require(
            0 <= s < 104 and 0 <= t < 104 and a in (0, 1) and b in (0, 1), "slot domain"
        )
        require((s, a) not in departures and (t, b) not in arrivals, "distinct slots")
        departures.add((s, a))
        arrivals.add((t, b))
        frames = frame_choices(row["basis"], quotients)
        require(frames[1] == {paths[f"X{s}"][0]}, "prescribed source line")
        require(frames[8] == {paths[f"Y{t}"][-1]}, "prescribed target cap")
        choices.append(frames)
    return choices


def literal_graph(choices):
    """Contacts are exact common membership masks, without an interval formula."""
    hosts, layers = {}, []
    for d in range(1, 9):
        index = {}
        for helper in range(208):
            for frame in choices[helper][d]:
                index.setdefault(frame, []).append(helper)
        adjacency = [set() for _ in range(208)]
        for helpers in index.values():
            require(len(helpers) <= 208, "frame hosts bound")
            for left, right in combinations(helpers, 2):
                adjacency[left].add(right)
                adjacency[right].add(left)
        hosts[d] = index
        layers.append(adjacency)
    graph = [set() for _ in range(8 * 208)]
    for d, layer in enumerate(layers):
        for helper, adjacent in enumerate(layer):
            node = d * 208 + helper
            graph[node] = {d * 208 + other for other in adjacent}
            if d < 7:
                graph[node].add(node + 208)
    return hosts, layers, graph


def reachable(graph, starts):
    size = len(graph)
    require(0 < size <= 1664 and len(starts) <= size, "traversal bound")
    seen = set(starts)
    require(all(type(node) is int and 0 <= node < size for node in seen), "start nodes")
    queue = sorted(seen)
    for cursor in range(size):
        if cursor == len(queue):
            break
        for node in graph[queue[cursor]]:
            require(0 <= node < size, "graph endpoint")
            if node not in seen:
                seen.add(node)
                queue.append(node)
    require(len(seen) == len(queue) <= size, "traversal capacity")
    return seen


def components(layer):
    seen, count = set(), 0
    for helper in range(208):
        if helper not in seen:
            seen |= reachable(layer, {helper})
            count += 1
    require(len(seen) == 208, "complete layer components")
    return count


def endpoint_nodes(paths, hosts, kind):
    result = []
    for index in range(104):
        nodes = set()
        for frame in paths[f"{kind}{index}"]:
            d = dimension(frame)
            if 1 <= d <= 8:
                nodes.update(
                    (d - 1) * 208 + helper for helper in hosts[d].get(frame, [])
                )
        result.append(nodes)
    return result


def trace_sources(paths, hosts, layers, graph):
    reads = endpoint_nodes(paths, hosts, "X")
    writes = endpoint_nodes(paths, hosts, "Y")
    masks, support = [0] * 104, [0] * 1664
    for s in range(104):
        reached = reachable(graph, reads[s])
        for node in reached:
            support[node] |= 1 << s
        for t in range(104):
            direct = set(paths[f"X{s}"]) & set(paths[f"Y{t}"])
            if reached & writes[t] or direct:
                masks[t] |= 1 << s
    summary = []
    for offset, layer in enumerate(layers):
        summary.append(
            {
                "dimension": offset + 1,
                "contacts": sum(len(adjacent) for adjacent in layer) // 2,
                "components": components(layer),
                "max_sources": max(
                    support[offset * 208 + h].bit_count() for h in range(208)
                ),
            }
        )
    return masks, summary


def required_correction(fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[i], root[j] = 2, 2 * sign
            roots.add(tuple(root))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    excluded = fixture["section4_explicit_P104"]
    ports = sorted(roots - {tuple(root) for root in excluded["F0"] + excluded["C"]})
    require(len(roots) == 120 and len(ports) == 104, "ordered roots")
    result = []
    for t in range(104):
        for s in range(104):
            gram = sum(ports[t][i] * ports[s][i] for i in range(8))
            coefficient = Fraction(8 * int(t == s) - gram, 8)
            if coefficient:
                result.append((t, s, coefficient))
    require(len(result) == 4992, "correction support count")
    return result


def enumeration_control(quotients):
    first = frame_choices([1, 2, 4, 8, 16, 32, 64, 128, 256], quotients)
    second = frame_choices([4, 8, 1, 2, 16, 32, 64, 128, 256], quotients)
    require(not first[3] & second[3], "disjoint planes cannot meet at dimension three")
    require(
        space([1, 2, 4, 8]) in first[4] & second[4], "literal dimension-four contact"
    )


def compute(certificate, word, fixture):
    paths = original_paths(word)
    quotients = quotient_bases()
    enumeration_control(quotients)
    choices = helper_choices(certificate, paths, quotients)
    hosts, layers, graph = literal_graph(choices)
    masks, summary = trace_sources(paths, hosts, layers, graph)
    required = required_correction(fixture)
    missing = [(t, s, value) for t, s, value in required if not masks[t] >> s & 1]
    require(bool(missing), "nonempty missing dependency witness")
    t, s, coefficient = missing[0]
    return {
        "schema_version": 1,
        "helpers": 208,
        "required_pairs": len(required),
        "reachable_required_pairs": len(required) - len(missing),
        "unreachable_required_pairs": len(missing),
        "layers": summary,
        "target_source_masks_hex": [hex(mask) for mask in masks],
        "witness": {
            "source": s,
            "target": t,
            "required_coefficient": str(coefficient),
            "optimistic_coefficient": "0",
        },
        "scope": "All intermediate completions of fixed matched endpoint planes; optimistic untimed contacts, no restoration charge; no new kappa.",
    }


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: independent.py [--emit]")
    result = compute(*authenticated_inputs())
    if sys.argv[1:]:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    expected = read_json(PACKAGE / "RESULT.json")
    require(
        json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "all receipt fields",
    )
    print(
        "PASS_P104_ENDPOINT_COMPLETION_FLOW_INDEPENDENT",
        f"required={result['required_pairs']}",
        f"unreachable={result['unreachable_required_pairs']}",
        "enumerated_quotient_subspaces",
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(
            f"FAIL_P104_ENDPOINT_COMPLETION_FLOW_INDEPENDENT: {error}"
        ) from error
