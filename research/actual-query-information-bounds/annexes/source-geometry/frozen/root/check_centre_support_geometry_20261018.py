#!/usr/bin/env python3
"""Check the binary source geometry of the eight structured queries."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent / "lanes"
SOURCES = {
    "directions": (
        "history-encoding/independent-skeleton-20261018/fresh-three-child/"
        "FRESH-THREE-CHILD-PROGRAMS.json.gz",
        "b08cb4146f1aec241e027cd62c942f6eca4ddab3e97f000a9c0017575d36deb5",
    ),
    "centres": (
        "controller-followthrough-20261017/structured-centres/"
        "STRUCTURED-CENTRES-PROGRAM.json.gz",
        "2b9de1454c2025ae4e230bd64de36b4f6c937628c63fc5afede6640dd3c0e1e1",
    ),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def basis(values):
    pivots = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return list(pivots.values())


def annihilator(values):
    return [v for v in range(1, 512)
            if all((v & w).bit_count() % 2 == 0 for w in values)]


def main():
    data = {}
    for label, (relative, pin) in SOURCES.items():
        raw = gzip.decompress((LANES / relative).read_bytes())
        need(sha256(raw).hexdigest() == pin, label + " source pin")
        data[label] = json.loads(raw)

    records = data["directions"]["transfers"]
    need([r["port"] for r in records] == list(range(112)), "Port order")
    q = [r["q"] for r in records]
    need(len(set(q)) == 112 and all(v.bit_count() % 2 == 1 for v in q),
         "Distinct anisotropic port lines")
    rows = data["centres"]["centre_rows"]
    need(len(rows) == 8, "Eight centre rows")
    supports = [sorted(int(p) for p, c in row.items() if Fraction(c))
                for row in rows]
    need(all(len(s) == 12 for s in supports), "Twelve ports per row")
    spaces = [basis(q[p] for p in support) for support in supports]
    need([len(s) for s in spaces] == [7] * 8, "Eight rank-seven supports")
    duals = [annihilator(s) for s in spaces]
    expected = [[7, 42, 45], [25, 45, 52], [45, 82, 127], [45, 76, 97],
                [45, 76, 97], [7, 42, 45], [25, 45, 52], [45, 82, 127]]
    need(duals == expected, "Actual annihilator planes")
    classes = [[i for i, dual in enumerate(duals) if tuple(dual) == value]
               for value in dict.fromkeys(map(tuple, duals))]
    need(classes == [[0, 5], [1, 6], [2, 7], [3, 4]], "Four classes")
    incidence = {}
    for i, support in enumerate(supports):
        for port in support:
            incidence.setdefault(port, []).append(i)
    need(len(incidence) == 48 and all(len(v) == 2 for v in incidence.values()),
         "Two incident centres per port")
    edges = sorted({tuple(v) for v in incidence.values()})
    expected_edges = [pair for pair in combinations(range(8), 2)
                      if duals[pair[0]] != duals[pair[1]]]
    need(edges == expected_edges and len(edges) == 24,
         "The incidence graph is complete four-partite")
    need(all(sum(tuple(v) == edge for v in incidence.values()) == 2
             for edge in edges), "Two physical ports per graph edge")
    intersections = [[14 - len(basis(left + right)) for right in spaces]
                     for left in spaces]
    need(all(intersections[i][j] == (7 if duals[i] == duals[j] else 6)
             for i in range(8) for j in range(8)), "Pair intersections")
    common_dual = set.intersection(*(set(d) for d in duals))
    need(common_dual == {45}, "Common rank-eight ambient hyperplane")
    need(len(basis(sum(spaces, []))) == 8, "All supports span that hyperplane")
    need(len(basis(sum(duals, []))) == 4, "Common intersection has rank five")
    independent = []
    for mask in range(256):
        chosen = [i for i in range(8) if (mask >> i) & 1]
        if all(not ((mask >> i) & 1 and (mask >> j) & 1) for i, j in edges):
            independent.append(chosen)
    maximum = max(map(len, independent))
    need(maximum == 2, "At most two compatible rank-seven query vertices")
    maximizers = [s for s in independent if len(s) == maximum]
    need(sorted(maximizers) == sorted(classes), "The four maximal compatible pairs")
    receipt = {
        "status": "PASS_CENTRE_SUPPORT_GEOMETRY",
        "source_decompressed_sha256": {k: v[1] for k, v in SOURCES.items()},
        "query_supports": supports,
        "binary_support_ranks": list(map(len, spaces)),
        "annihilators": duals,
        "equal_subspace_classes": classes,
        "intersection_ranks": intersections,
        "common_hyperplane_normal": 45,
        "common_intersection_rank": 5,
        "incidence_edges": edges,
        "maximum_independent_set_size": maximum,
        "maximum_independent_sets": maximizers,
        "conditional_eight_query_rank_lower_bound": 62,
        "scope": (
            "Exact source geometry. The rank-62 statement assumes one scalar "
            "capture per stated query and one monotone subspace path per "
            "unwarped source value, with no extra carrier. No new native word "
            "or general query lower bound is claimed."
        ),
    }
    target = HERE / "CENTRE-SUPPORT-GEOMETRY-20261018.json"
    target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
