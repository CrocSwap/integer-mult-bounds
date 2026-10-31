#!/usr/bin/env python3
"""Independently reconstruct the native graph and exact rank distances."""
import argparse
from collections import Counter
from hashlib import sha256
import gzip
import json
from pathlib import Path
from types import ModuleType

_path = Path(__file__).with_name("review_geometry.py")
_geometry = ModuleType("independent_geometry")
_geometry.__file__ = str(_path)
exec(compile(_path.read_bytes(), str(_path), "exec"), _geometry.__dict__)
FRAME_SHA, catalogue, require = _geometry.FRAME_SHA, _geometry.catalogue, _geometry.require


def bucket_distances(adjacency, source):
    distances = {source: 0}
    buckets = {0: {source}}
    while buckets:
        cost = min(buckets)
        nodes = buckets.pop(cost)
        for node in nodes:
            if distances[node] != cost:
                continue
            for target, rank in adjacency[node]:
                new_cost = cost + rank
                if target not in distances or new_cost < distances[target]:
                    distances[target] = new_cost
                    buckets.setdefault(new_cost, set()).add(target)
    return distances


def certify_row(adjacency, source, distances):
    require(distances.keys() == adjacency.keys(), "complete distance row")
    require(distances[source] == 0, "zero source potential")
    require(all(type(d) is int and d >= 0 for d in distances.values()), "nonnegative integer distances")
    require(all(distances[v] > 0 for v in distances if v != source), "distinct frames positive distance")
    for u in adjacency:
        require(all(distances[v] <= distances[u] + rank for v, rank in adjacency[u]), "edge potential inequality")
    # The graph is symmetric. A tight incoming edge descends by a positive
    # integer, providing a finite attaining path to the only zero vertex.
    for v in adjacency:
        if v != source:
            require(any(distances[u] + rank == distances[v] for u, rank in adjacency[v]), "attaining predecessor")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=Path, required=True)
    parser.add_argument("--save", type=Path)
    args = parser.parse_args()
    raw = args.frames.read_bytes()
    if args.frames.suffix == ".gz":
        raw = gzip.decompress(raw)
    require(sha256(raw).hexdigest() == FRAME_SHA, "pinned frames")
    spaces, edges = catalogue(json.loads(raw)["frames"])
    codes = sorted(spaces)
    adjacency = {code: [] for code in codes}
    for (source, target), rank in edges.items():
        adjacency[source].append((target, rank))
    matrix = []
    histogram = Counter()
    for source in codes:
        row = bucket_distances(adjacency, source)
        certify_row(adjacency, source, row)
        matrix.append([row[target] for target in codes])
        histogram.update(row.values())
    encoded = json.dumps({"codes": codes, "matrix": matrix}, separators=(",", ":")).encode()
    keyed_rows = [[source, [[target, distance] for target, distance in zip(codes, row)]]
                  for source, row in zip(codes, matrix)]
    keyed_digest = sha256(json.dumps(keyed_rows, separators=(",", ":")).encode()).hexdigest()
    if args.save:
        args.save.write_bytes(gzip.compress(encoded, mtime=0))
    source = codes[0]
    row = dict(zip(codes, matrix[0]))
    target = next(v for v in codes if row[v] > 1)
    mutants = []
    for label, changed in (
        ("inflated distance", dict(row)),
        ("deflated distance", dict(row)),
        ("nonzero diagonal", dict(row)),
        ("boolean distance", dict(row)),
    ):
        if label == "inflated distance":
            changed[target] += 1
        elif label == "deflated distance":
            changed[target] -= 1
        elif label == "nonzero diagonal":
            changed[source] = 1
        else:
            changed[target] = True
        try:
            certify_row(adjacency, source, changed)
        except ValueError:
            mutants.append(label)
        else:
            raise ValueError("Accepted distance mutant: " + label)
    print(json.dumps({
        "schema": "independent-native-rank-distances-v1",
        "algorithm": "integer bucket relaxation, with edge-potential and tight-predecessor checks",
        "frames_sha256": FRAME_SHA,
        "distance_matrix_sha256": sha256(encoded).hexdigest(),
        "author_keyed_encoding_sha256": keyed_digest,
        "vertices": len(codes),
        "directed_edges": len(edges),
        "ordered_pairs_including_identity": len(codes) ** 2,
        "distance_histogram": dict(sorted(histogram.items())),
        "negative_controls": mutants,
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
