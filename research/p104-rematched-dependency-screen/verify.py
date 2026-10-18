# SPDX-License-Identifier: Apache-2.0
"""Certify the matching-coherence limit of the fixed P104 support relaxation."""

import hashlib
import json
import runpy
import sys
from fractions import Fraction
from itertools import combinations, pairwise, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
INPUTS = (
    "research/p104-joint-unit-flags/CERTIFICATE.json",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-native-channel/inputs/P104-FIXTURE.json",
)
LIMIT = 2_000_000


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def read_json(path):
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "JSON size bound")
    return json.loads(raw, object_pairs_hook=unique)


def inputs():
    records = read_json(PACKAGE / "SOURCES.json")["files"]
    require(type(records) is list and len(records) == 5, "five source records")
    pins = {r["path"]: r["sha256"] for r in records if r["usage"] == "input"}
    require(set(pins) == set(INPUTS), "exact input inventory")
    values = []
    for name in INPUTS:
        with (ROOT / name).open("rb") as stream:
            raw = stream.read(LIMIT + 1)
        require(len(raw) <= LIMIT, "input size bound")
        require(hashlib.sha256(raw).hexdigest() == pins[name], "input SHA256")
        values.append(json.loads(raw, object_pairs_hook=unique))
    return values


def span(basis):
    require(type(basis) is list and len(basis) <= 9, "basis size")
    points = [0]
    for vector in basis:
        require(type(vector) is int and 0 < vector < 512, "binary vector")
        require(vector not in points, "independent basis")
        points += [point ^ vector for point in points]
    return sum(1 << point for point in points)


def bits(mask, width):
    require(type(mask) is int and 0 <= mask < 1 << width, "mask domain")
    for _ in range(width):
        if not mask:
            break
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def dim(frame):
    count = frame.bit_count()
    require(count > 0 and count & (count - 1) == 0, "subspace size")
    return count.bit_length() - 1


def data_paths(word):
    paths = {
        f"{kind}{i}": [span(word["initial_frames"][f"{kind}{i}"])]
        for kind in "XY"
        for i in range(104)
    }
    require(type(word["program"]) is list and len(word["program"]) == 4058, "word size")
    for event in word["program"]:
        op, name = event[:2]
        if op != "transport":
            require(op in {"add", "copy", "zero", "erase"}, "opcode")
            require(not name.startswith("X"), "immutable X")
            if op in {"add", "copy"}:
                require(not event[2].startswith("Y"), "unread Y")
            continue
        if name not in paths:
            continue
        old, new = span(event[2]), span(event[3])
        require(paths[name][-1] == old and old != new and old & new == old, "path")
        rank = event[4]
        require(type(rank) is int and rank == dim(new) - dim(old), "transport rank")
        paths[name].append(new)
    for name, chain in paths.items():
        require(
            len(chain) <= 10 and chain[-1] == span(word["final_frames"][name]), "exit"
        )
        require(
            (dim(chain[0]), dim(chain[-1])) == ((1, 9) if name[0] == "X" else (0, 8)),
            "data endpoints",
        )
    return paths


def cover_frames(certificate, paths):
    forms = certificate["forms"]
    require(set(forms) == {"departure", "arrival"}, "cover orientations")
    lines = [paths[f"X{s}"][0] for s in range(104)]
    caps = [paths[f"Y{t}"][-1] for t in range(104)]
    require(len(set(lines)) == len(set(caps)) == 104, "distinct data endpoints")
    departures, arrivals = [], []
    for kind in ("departure", "arrival"):
        require(type(forms[kind]) is list and len(forms[kind]) == 104, "cover count")
        for index, pair in enumerate(forms[kind]):
            require(type(pair) is list and len(pair) == 2, "two cover slots")
            for form in pair:
                require(type(form) is int and 0 < form < 512, "cover functional")
                if kind == "departure":
                    basis = [lines[index].bit_length() - 1, form]
                    departures.append(span(basis))
                else:
                    frame = sum(
                        1 << p
                        for p in bits(caps[index], 512)
                        if (p & form).bit_count() % 2 == 0
                    )
                    require(dim(frame) == 7, "arrival dimension")
                    arrivals.append(frame)
    graph = [[j for j, b in enumerate(arrivals) if a & b == a] for a in departures]
    require(sum(map(len, graph)) == 2309, "compatibility edges")
    return lines, departures, arrivals, caps, graph


def check_pairing(pairing, graph):
    size = len(graph)
    require(type(pairing) is list and len(pairing) == size, "pairing size")
    require(all(type(j) is int and 0 <= j < size for j in pairing), "pairing integers")
    require(len(set(pairing)) == size, "pairing bijection")
    require(all(j in graph[i] for i, j in enumerate(pairing)), "compatible pairing")


def published_pairing(certificate, graph):
    rows = certificate["helpers"]
    require(type(rows) is list and len(rows) == 208, "208 original flags")
    pairing = [-1] * 208
    for row in rows:
        s, a, t, b = [
            row[k] for k in ("source", "departure_choice", "target", "arrival_choice")
        ]
        require(all(type(v) is int for v in (s, a, t, b)), "integer slots")
        require(0 <= s < 104 and 0 <= t < 104 and a in (0, 1) and b in (0, 1), "slots")
        require(pairing[2 * s + a] == -1, "unique departure")
        pairing[2 * s + a] = 2 * t + b
    check_pairing(pairing, graph)
    return pairing


def matching_support(graph, pairing):
    """Check an explicit alternating-cycle matching for every compatibility edge."""
    check_pairing(pairing, graph)
    size = len(graph)
    require(0 < size <= 208, "matching graph capacity")
    mate = {j: i for i, j in enumerate(pairing)}
    paths = []
    for start in range(size):
        parent = {start: None}
        queue = [start]
        for cursor in range(size):
            if cursor == len(queue):
                break
            for j in graph[queue[cursor]]:
                nxt = mate[j]
                if nxt not in parent:
                    parent[nxt] = queue[cursor]
                    queue.append(nxt)
        require(len(parent) == size, "strongly connected alternating graph")
        paths.append(parent)
    digest, checked = hashlib.sha256(), 0
    for u, targets in enumerate(graph):
        for target in targets:
            v = mate[target]
            backward = [u]
            for _ in range(size):
                previous = paths[v][backward[-1]]
                if previous is None:
                    break
                backward.append(previous)
            require(backward[-1] == v, "alternating path bound")
            chain = list(reversed(backward))
            candidate = pairing.copy()
            for left, right in pairwise(chain):
                candidate[left] = pairing[right]
            candidate[u] = target
            check_pairing(candidate, graph)
            require(candidate[u] == target, "forced edge")
            digest.update(bytes(candidate))
            checked += 1
    return {
        "supported_edges": checked,
        "alternating_vertices": size,
        "forced_matchings_sha256": digest.hexdigest(),
    }


def intervals(frames, edges, dimension):
    lines, departures, arrivals, caps, _ = frames
    if dimension == 1:
        return [(lines[a // 2],) * 2 for a, _ in edges]
    if dimension == 2:
        return [(departures[a],) * 2 for a, _ in edges]
    if dimension == 7:
        return [(arrivals[b],) * 2 for _, b in edges]
    if dimension == 8:
        return [(caps[b // 2],) * 2 for _, b in edges]
    require(3 <= dimension <= 6, "intermediate dimension")
    return [(departures[a], arrivals[b]) for a, b in edges]


def fits(bounds, dimension, frame):
    low, high = bounds
    return dim(frame) == dimension and low & frame == low and frame & high == frame


def contact(left, right, dimension):
    a, b = left
    c, e = right
    if a & e != a or c & b != c:
        return False
    minimum = a.bit_count() * c.bit_count() // (a & c).bit_count()
    return minimum <= 1 << dimension <= (b & e).bit_count()


def interval_layers(frames, edges, paths):
    require(0 < len(edges) <= 2309, "virtual helper capacity")
    layers = []
    for d in range(1, 9):
        bounds = intervals(frames, edges, d)
        adjacency = [1 << i for i in range(len(edges))]
        reads, writes = [], []
        for i, left in enumerate(bounds):
            reads.append(
                sum(
                    1 << s
                    for s in range(104)
                    if any(fits(left, d, f) for f in paths[f"X{s}"])
                )
            )
            writes.append(
                sum(
                    1 << t
                    for t in range(104)
                    if any(fits(left, d, f) for f in paths[f"Y{t}"])
                )
            )
            for j in range(i):
                if contact(left, bounds[j], d):
                    adjacency[i] |= 1 << j
                    adjacency[j] |= 1 << i
        layers.append((adjacency, reads, writes))
    return layers


def components(adjacency):
    count = len(adjacency)
    require(0 < count <= 2309, "component capacity")
    unvisited, groups = (1 << count) - 1, []
    for start in range(count):
        if not unvisited >> start & 1:
            continue
        queue = [start]
        unvisited ^= 1 << start
        for cursor in range(count):
            if cursor == len(queue):
                break
            new = adjacency[queue[cursor]] & unvisited
            queue.extend(bits(new, count))
            unvisited ^= new
        require(len(queue) <= count, "bounded component")
        groups.append(queue)
    require(unvisited == 0, "complete components")
    return groups


def trace(layers, paths):
    count = len(layers[0][0])
    support = [0] * count
    outputs = [
        sum(1 << s for s in range(104) if set(paths[f"X{s}"]) & set(paths[f"Y{t}"]))
        for t in range(104)
    ]
    summary = []
    for d, (adjacency, reads, writes) in enumerate(layers, 1):
        for i in range(count):
            support[i] |= reads[i]
        groups = components(adjacency)
        for group in groups:
            joined = 0
            for i in group:
                joined |= support[i]
            for i in group:
                support[i] = joined
        for i in range(count):
            for t in bits(writes[i], 104):
                outputs[t] |= support[i]
        summary.append(
            {
                "dimension": d,
                "contacts": (sum(a.bit_count() for a in adjacency) - count) // 2,
                "components": len(groups),
                "max_sources": max(s.bit_count() for s in support),
            }
        )
    return outputs, summary


def correction(fixture):
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    roots += [(1, *s) for s in product((-1, 1), repeat=7) if s.count(-1) % 2 == 0]
    removed = fixture["section4_explicit_P104"]
    ports = sorted(set(roots) - {tuple(v) for v in removed["F0"] + removed["C"]})
    require(len(roots) == 120 and len(ports) == 104, "ordered P104 roots")
    return [
        [
            Fraction(
                8 * int(t == s)
                - sum(a * b for a, b in zip(ports[t], ports[s], strict=True)),
                8,
            )
            for s in range(104)
        ]
        for t in range(104)
    ]


def report(edges, layers, paths, matrix):
    outputs, summary = trace(layers, paths)
    required = [(t, s) for t in range(104) for s in range(104) if matrix[t][s]]
    missing = [(t, s) for t, s in required if not outputs[t] >> s & 1]
    missing_masks = [0] * 104
    for t, s in missing:
        missing_masks[t] |= 1 << s
    first = None
    if missing:
        t, s = missing[0]
        first = {"target": t, "source": s, "coefficient": str(matrix[t][s])}
    require(len(required) == 4992, "required correction pairs")
    return {
        "virtual_helpers": len(edges),
        "required_pairs": len(required),
        "unreachable_required_pairs": len(missing),
        "missing_source_masks_hex": [hex(m) for m in missing_masks],
        "first_missing_coefficient": first,
        "reachable_required_pairs": len(required) - len(missing),
        "target_source_masks_hex": [hex(m) for m in outputs],
        "layers": summary,
    }


def compute(certificate, word, fixture, pairing, literal=False):
    paths = data_paths(word)
    frames = cover_frames(certificate, paths)
    graph = frames[-1]
    original = published_pairing(certificate, graph)
    check_pairing(pairing, graph)
    matrix = correction(fixture)
    require(
        all(
            bool(matrix[t][s])
            == bool(frames[3][t] >> (frames[0][s].bit_length() - 1) & 1)
            for t in range(104)
            for s in range(104)
        ),
        "Gram support binds to ordered data endpoints",
    )
    edge_sets = {
        "published": list(enumerate(original)),
        "rematched": list(enumerate(pairing)),
        "union": [(a, b) for a in range(208) for b in graph[a]],
    }
    result = {
        "schema_version": 1,
        "matching_support": matching_support(graph, original),
    }
    if literal:
        # One fixed package-local oracle; no predecessor implementation is loaded.
        oracle = runpy.run_path(str(PACKAGE / "literal.py"))["literal_layers"]
    for name, edges in edge_sets.items():
        if literal:
            layers = oracle(frames, edges, paths)
        else:
            layers = interval_layers(frames, edges, paths)
        result[name] = report(edges, layers, paths, matrix)
    return result


def main():
    allowed = ([], ["--emit"], ["--literal"], ["--literal", "--emit"])
    require(sys.argv[1:] in allowed, "usage: verify.py [--literal] [--emit]")
    witness = read_json(PACKAGE / "WITNESS.json")
    require(set(witness) == {"schema_version", "pairing"}, "witness schema")
    require(
        type(witness["schema_version"]) is int and witness["schema_version"] == 1,
        "witness version",
    )
    result = compute(*inputs(), witness["pairing"], literal="--literal" in sys.argv)
    if "--emit" in sys.argv:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    expected = read_json(PACKAGE / "RESULT.json")
    require(
        json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "exact typed receipt",
    )
    print(
        "PASS_P104_MATCHING_COHERENCE",
        "literal" if "--literal" in sys.argv else "interval",
        f"supported_edges={result['matching_support']['supported_edges']}",
        f"union_missing={result['union']['unreachable_required_pairs']}",
        f"rematched_missing={result['rematched']['unreachable_required_pairs']}",
        "no_new_kappa",
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"FAIL_P104_MATCHING_COHERENCE: {error}") from error
