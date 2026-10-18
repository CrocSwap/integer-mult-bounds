#!/usr/bin/env python3
"""Independent replay of dcharb78/PR3182's pooled P104 support cut.

Geometry conventions follow Petalas/PR2981/3013 and the retained P104 sources.
No predecessor executable or reported result is imported.
"""

import argparse
import hashlib
import json
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = (
    "research/p104-joint-unit-flags/CERTIFICATE.json",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-native-channel/inputs/P104-FIXTURE.json",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = dict(pairs)
    need(len(value) == len(pairs), "duplicate JSON key")
    return value


def read_json(path):
    with path.open("rb") as stream:
        raw = stream.read(2_000_001)
    need(len(raw) <= 2_000_000, "input exceeds 2 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def load_inputs():
    manifest = read_json(HERE / "SOURCES.json")
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    need(tuple(r["path"] for r in rows) == INPUTS, "exact source inventory")
    for row in rows:
        path = ROOT / row["path"]
        need(path.stat().st_size <= 2_000_000, "source size")
        need(
            hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
            "source hash: " + row["path"],
        )
    return tuple(read_json(ROOT / rel) for rel in INPUTS)


def points(basis):
    need(type(basis) is list and len(basis) <= 9, "basis size")
    result = [0]
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in result, "basis vector")
        result += [p ^ v for p in result]
    return frozenset(result)


def bitmap(space):
    return sum(1 << p for p in space)


def data_paths(word):
    need(len(word["program"]) == 4058, "word length")
    paths = {
        f"{k}{i}": [points(word["initial_frames"][f"{k}{i}"])]
        for k in "XY"
        for i in range(104)
    }
    for event in word["program"]:
        op, name = event[:2]
        need(op in {"transport", "add", "copy", "erase", "zero"}, "opcode")
        if op != "transport" or name not in paths:
            continue
        old, new = points(event[2]), points(event[3])
        need(paths[name][-1] == old and old < new, "monotone data path")
        need(len(new) == len(old) * 2 ** event[4], "transport rank")
        paths[name].append(new)
    for name, chain in paths.items():
        need(len(chain) <= 10, "path length")
        need(chain[-1] == points(word["final_frames"][name]), "final frame")
        need(
            (len(chain[0]), len(chain[-1]))
            == ((2, 512) if name[0] == "X" else (1, 256)),
            "endpoints",
        )
    return paths


def endpoints(cert, paths):
    need(set(cert["forms"]) == {"departure", "arrival"}, "cover kinds")
    lines = [paths[f"X{i}"][0] for i in range(104)]
    caps = [paths[f"Y{i}"][-1] for i in range(104)]
    departures, arrivals = [], []
    for i in range(104):
        for v in cert["forms"]["departure"][i]:
            line = next(p for p in lines[i] if p)
            departures.append(points([line, v]))
        for functional in cert["forms"]["arrival"][i]:
            arrivals.append(
                frozenset(p for p in caps[i] if (p & functional).bit_count() % 2 == 0)
            )
    need(len(departures) == len(arrivals) == 208, "slot count")
    need(
        all(len(a) == 4 for a in departures) and all(len(b) == 128 for b in arrivals),
        "cover dimensions",
    )
    edges = [
        (a, b) for a in range(208) for b in range(208) if departures[a] <= arrivals[b]
    ]
    need(len(edges) == 2309, "all compatible edges")
    return lines, departures, arrivals, caps, edges


def bounds_at(frames, dimension):
    lines, departures, arrivals, caps, edges = frames
    if dimension == 1:
        return [(lines[a // 2], lines[a // 2]) for a, _ in edges]
    if dimension == 2:
        return [(departures[a], departures[a]) for a, _ in edges]
    if dimension == 7:
        return [(arrivals[b], arrivals[b]) for _, b in edges]
    if dimension == 8:
        return [(caps[b // 2], caps[b // 2]) for _, b in edges]
    need(3 <= dimension <= 6, "layer dimension")
    return [(departures[a], arrivals[b]) for a, b in edges]


def interval_relation(bounds, dimension):
    masks = [(bitmap(a), bitmap(b)) for a, b in bounds]
    adjacency = [1 << i for i in range(len(bounds))]
    for i, (a, b) in enumerate(masks):
        for j in range(i):
            c, e = masks[j]
            if a & e != a or c & b != c:
                continue
            lower = a.bit_count() * c.bit_count() // (a & c).bit_count()
            if lower <= 2**dimension <= (b & e).bit_count():
                adjacency[i] |= 1 << j
                adjacency[j] |= 1 << i
    return adjacency


def quotient_subspaces():
    result = [[] for _ in range(6)]
    for size in range(6):
        for pivots in combinations(range(5), size):
            free = [
                (i, j)
                for i, p in enumerate(pivots)
                for j in range(p + 1, 5)
                if j not in pivots
            ]
            for code in range(1 << len(free)):
                basis = [1 << p for p in pivots]
                for bit, (i, j) in enumerate(free):
                    basis[i] |= ((code >> bit) & 1) << j
                result[size].append(points(basis))
    need([len(x) for x in result] == [1, 31, 155, 155, 31, 1], "quotients")
    need(all(len(set(x)) == len(x) for x in result), "unique quotients")
    return result


def literal_choices(low, high, dimension, quotients):
    if low == high:
        return [bitmap(low)]
    basis, generated = [], set(low)
    for v in sorted(high):
        if v not in generated:
            basis.append(v)
            generated |= {p ^ v for p in tuple(generated)}
    need(len(basis) == 5 and generated == high, "five-dimensional quotient")
    cosets = []
    for code in range(32):
        v = 0
        for i in range(5):
            if (code >> i) & 1:
                v ^= basis[i]
        cosets.append(bitmap({p ^ v for p in low}))
    choices = []
    for quotient in quotients[dimension - 2]:
        frame = 0
        for p in quotient:
            frame |= cosets[p]
        choices.append(frame)
    return choices


def literal_relation(bounds, dimension, quotients):
    choices = [literal_choices(a, b, dimension, quotients) for a, b in bounds]
    hosts = {}
    for i, options in enumerate(choices):
        for frame in options:
            hosts[frame] = hosts.get(frame, 0) | (1 << i)
    adjacency = []
    for options in choices:
        neighbors = 0
        for frame in options:
            neighbors |= hosts[frame]
        adjacency.append(neighbors)
    return adjacency


def contacts(bounds, dimension, paths, kind):
    snapshots = [
        (i, f)
        for i in range(104)
        for f in paths[f"{kind}{i}"]
        if len(f) == 2**dimension
    ]
    return [
        sum(1 << i for i, f in snapshots if low <= f <= high) for low, high in bounds
    ]


def transfer(state, reads, adjacency):
    # Read first. No connected-component closure is allowed in this relaxation.
    seeded = [s | r for s, r in zip(state, reads, strict=True)]
    result = seeded.copy()
    for i, signal in enumerate(seeded):
        if signal:
            mask = adjacency[i]
            for j in range(len(state)):
                if (mask >> j) & 1:
                    result[j] |= signal
    return result


def required_masks(fixture):
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    roots += [(1, *s) for s in product((-1, 1), repeat=7) if s.count(-1) % 2 == 0]
    removed = fixture["section4_explicit_P104"]
    ports = sorted(set(roots) - {tuple(v) for v in removed["F0"] + removed["C"]})
    need(len(roots) == 120 and len(ports) == 104, "P104 roots")
    matrix8 = [
        [
            8 * int(t == s) - sum(a * b for a, b in zip(x, y, strict=True))
            for s, x in enumerate(ports)
        ]
        for t, y in enumerate(ports)
    ]
    need(matrix8[71][102] == -4, "C[71,102] = -1/2")
    masks = [sum(1 << s for s, v in enumerate(row) if v) for row in matrix8]
    need(sum(m.bit_count() for m in masks) == 4992, "required pairs")
    return masks


def layer_digest(adjacency):
    size = (len(adjacency) + 7) // 8
    payload = b"".join(m.to_bytes(size, "little") for m in adjacency)
    return hashlib.sha256(payload).hexdigest()


def compute_layer(frames, paths, d, quotients, state, outputs):
    bounds = bounds_at(frames, d)
    adjacency = (
        literal_relation(bounds, d, quotients)
        if quotients is not None
        else interval_relation(bounds, d)
    )
    reads = contacts(bounds, d, paths, "X")
    writes = contacts(bounds, d, paths, "Y")
    state = transfer(state, reads, adjacency)
    for i, targets in enumerate(writes):
        for t in range(104):
            if (targets >> t) & 1:
                outputs[t] |= state[i]
    record = {
        "dimension": d,
        "relation_sha256": layer_digest(adjacency),
        "source102_reached": sum(bool((s >> 102) & 1) for s in state),
        "source102_readers": sum(bool((r >> 102) & 1) for r in reads),
        "target71_writers": sum(bool((w >> 71) & 1) for w in writes),
        "target71_hits": sum(
            bool((w >> 71) & 1 and (s >> 102) & 1)
            for w, s in zip(writes, state, strict=True)
        ),
    }
    return state, record, adjacency, writes


def replay(literal):
    cert, word, fixture = load_inputs()
    paths = data_paths(word)
    frames = endpoints(cert, paths)
    edges = frames[-1]
    state = [0] * len(edges)
    outputs = [
        sum(1 << s for s in range(104) if set(paths[f"X{s}"]) & set(paths[f"Y{t}"]))
        for t in range(104)
    ]
    quotients = quotient_subspaces() if literal else None
    layers, history, relations, writes_all = [], [], [], []
    for d in range(1, 9):
        state, record, adjacency, writes = compute_layer(
            frames, paths, d, quotients, state, outputs
        )
        history.append(sum(1 << i for i, s in enumerate(state) if (s >> 102) & 1))
        relations.append(adjacency)
        writes_all.append(writes)
        layers.append(record)
    required = required_masks(fixture)
    missing = [
        [t, s]
        for t in range(104)
        for s in range(104)
        if (required[t] >> s) & 1 and not (outputs[t] >> s) & 1
    ]
    backward = sum(1 << i for i, w in enumerate(writes_all[7]) if (w >> 71) & 1)
    for d in (7, 6, 5):
        expanded = backward
        for i in range(len(edges)):
            if (backward >> i) & 1:
                expanded |= relations[d][i]
        backward = expanded
    return {
        "status": "PASS_P104_POOLED_CUT",
        "edges": len(edges),
        "required": 4992,
        "missing": missing,
        "coefficient": "-1/2",
        "layers": layers,
        "output_masks": [hex(m) for m in outputs],
        "forward5_edges": [
            list(e) for i, e in enumerate(edges) if (history[4] >> i) & 1
        ],
        "backward6_edges": [
            list(e) for i, e in enumerate(edges) if (backward >> i) & 1
        ],
        "cut_intersection": (history[4] & backward).bit_count(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--literal", action="store_true")
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = replay(args.literal)
    need(
        result["missing"] == [[71, 102]] and result["cut_intersection"] == 0,
        "pooled support exclusion",
    )
    need(result == read_json(HERE / "RESULT.json"), "complete receipt mismatch")
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_P104_POOLED_CUT edges=2309 required=4992 missing=1 no_new_kappa")


if __name__ == "__main__":
    main()
