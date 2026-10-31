#!/usr/bin/env python3
"""Independent exact catalogue review: RREF-derived kernels, no author imports."""
import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
import gzip
import json
from math import gcd, lcm
from pathlib import Path

FRAME_SHA = "0d99fc6b8f45c03dfba5252a03dd9e7fe23be3a7593dfe15368e34da6629a654"
PATHS_SHA = "f4dd58b78121040b1f054c0f7a626b25f6ef8d39f3de044d3456ea7dea8a6a5e"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rref(rows):
    out = [list(map(F, row)) for row in rows]
    require(all(len(row) == 8 for row in out), "eight coordinates")
    rank = 0
    for col in range(8):
        pivot = next((i for i in range(rank, len(out)) if out[i][col]), None)
        if pivot is None:
            continue
        out[rank], out[pivot] = out[pivot], out[rank]
        scale = out[rank][col]
        out[rank] = [v / scale for v in out[rank]]
        for i in range(len(out)):
            if i != rank and out[i][col]:
                scale = out[i][col]
                out[i] = [x - scale * y for x, y in zip(out[i], out[rank])]
        rank += 1
    return tuple(tuple(row) for row in out[:rank])


def primitive(row):
    scale = lcm(*(v.denominator for v in row))
    values = [int(v * scale) for v in row]
    divisor = gcd(*values)
    return tuple(v // (divisor or 1) for v in values)


def kernel(basis):
    pivots = [next(i for i, v in enumerate(row) if v) for row in basis]
    result = []
    for free in set(range(8)) - set(pivots):
        vector = [F(0)] * 8
        vector[free] = F(1)
        for pivot, row in zip(pivots, basis):
            vector[pivot] = -row[free]
        result.append(primitive(vector))
    return tuple(result)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def catalogue(frames):
    spaces = {}
    complements = {}
    for key, frame in frames.items():
        code = int(key)
        basis = rref(frame["B"])
        complement = rref(frame["A"])
        require(len(basis) == frame["dim"], "declared dimension")
        require(len(complement) == 8 - frame["dim"], "complement dimension")
        require(all(dot(a, b) == 0 for a in complement for b in basis), "orthogonal complements")
        spaces[code] = basis
        complements[code] = kernel(basis)
    require(len(set(spaces.values())) == len(spaces), "distinct physical frames")
    integer_spaces = {code: tuple(map(primitive, space)) for code, space in spaces.items()}
    directed = {}
    for a, b in combinations(sorted(spaces), 2):
        lo, hi = sorted((a, b), key=lambda k: len(spaces[k]))
        rank = len(spaces[hi]) - len(spaces[lo])
        if 0 < rank < 8 and all(dot(x, y) == 0 for x in integer_spaces[lo] for y in complements[hi]):
            directed[a, b] = directed[b, a] = rank
    return spaces, directed


def accepted(edges, source, target, rank):
    return (source, target) in edges and edges[source, target] == rank


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--older", type=Path, required=True)
    parser.add_argument("--paths", type=Path, required=True)
    args = parser.parse_args()
    current = args.current.read_bytes()
    older = gzip.decompress(args.older.read_bytes())
    require(current == older, "exact current/older catalogue byte equality")
    require(sha256(current).hexdigest() == FRAME_SHA, "pinned catalogue bytes")
    frames = json.loads(current)["frames"]
    spaces, edges = catalogue(frames)
    require(len(frames) == 645 and len(edges) == 52624, "catalogue coverage")
    paths_raw = args.paths.read_bytes()
    require(sha256(paths_raw).hexdigest() == PATHS_SHA, "pinned retained routes")
    retained = json.loads(paths_raw)
    require(len(retained) == 2369, "retained path count")
    for key, route in retained.items():
        source, target = map(int, key.split(":"))
        require(len(route) == 1, "retained one-edge path")
        require(route[0][:2] == [source, target], "retained route endpoints")
        require(accepted(edges, *route[0]), "retained route native admission")
    zero = next(k for k, v in spaces.items() if len(v) == 0)
    full = next(k for k, v in spaces.items() if len(v) == 8)
    example = next((a, b, r) for (a, b), r in edges.items() if a < b)
    a, b, rank = example
    require(accepted(edges, a, b, rank) and accepted(edges, b, a, rank), "both query directions")
    controls = {
        "rank-eight child rejected": not accepted(edges, zero, full, 8),
        "rank-zero query rejected": not accepted(edges, a, a, 0),
        "wrong residual rank rejected": not accepted(edges, a, b, rank + 1),
    }
    mutant = dict(frames)
    mutant[str(a)] = dict(mutant[str(a)], dim=frames[str(a)]["dim"] + 1)
    try:
        catalogue(mutant)
    except ValueError:
        controls["declared dimension mutant rejected"] = True
    else:
        controls["declared dimension mutant rejected"] = False
    mutant = dict(frames)
    chosen = next(k for k, f in frames.items() if 0 < f["dim"] < 8)
    mutant[chosen] = dict(mutant[chosen], A=frames[chosen]["B"])
    try:
        catalogue(mutant)
    except ValueError:
        controls["complement mutant rejected"] = True
    else:
        controls["complement mutant rejected"] = False
    require(all(controls.values()), "negative controls")
    print(json.dumps({
        "schema": "independent-g20-native-geometry-review-v1",
        "frame_sha256": FRAME_SHA,
        "catalogues_byte_identical": True,
        "frames": len(frames),
        "dimensions": dict(sorted(Counter(map(len, spaces.values())).items())),
        "directed_native_edges": len(edges),
        "edge_ranks": dict(sorted(Counter(edges.values()).items())),
        "retained_edges_admitted": len(retained),
        "zero_frame": zero,
        "full_frame": full,
        "controls": controls,
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
