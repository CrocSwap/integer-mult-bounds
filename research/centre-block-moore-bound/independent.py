#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Independent finite graph controls for the written owner-block bound.

The two graphs are constructed from their definitions. Six-cycles are found by
literal alternating walks, independently of the primary triangle census.
No predecessor or primary executable is imported.
"""

from itertools import combinations
import json
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def affine_nine():
    points = list((x, y) for x in range(3) for y in range(3))
    lines = [set(i for i, (x, y) in enumerate(points) if (y - slope * x) % 3 == intercept)
             for slope in range(3) for intercept in range(3)]
    return len(points), lines


def duad_fifteen():
    duads = list(combinations(range(6), 2))
    indices = {pair: index for index, pair in enumerate(duads)}

    def matchings(remaining):
        if not remaining:
            yield ()
            return
        first = remaining[0]
        for second in remaining[1:]:
            rest = tuple(value for value in remaining if value not in (first, second))
            for tail in matchings(rest):
                yield ((first, second),) + tail

    lines = [set(indices[pair] for pair in matching)
             for matching in matchings(tuple(range(6)))]
    require(len(lines) == 15 and len({tuple(sorted(line)) for line in lines}) == 15,
            "fifteen distinct synthemes")
    return len(duads), lines


def canonical_cycle(walk):
    representations = []
    for direction in (tuple(walk), tuple(reversed(walk))):
        representations.extend(direction[offset:] + direction[:offset]
                               for offset in range(len(direction)))
    return min(representations)


def six_cycles(point_neighbors, lines):
    """Enumerate actual simple closed walks; do not infer cycles from triangles."""
    point_count = len(point_neighbors)
    found = set()
    for a in range(point_count):
        for first in point_neighbors[a]:
            for b in lines[first] - {a}:
                for second in point_neighbors[b] - {first}:
                    for c in lines[second] - {a, b}:
                        for third in point_neighbors[c] - {first, second}:
                            if a in lines[third]:
                                found.add(canonical_cycle((a, point_count + first,
                                                          b, point_count + second,
                                                          c, point_count + third)))
    return sorted(found)


def triangles(adjacency):
    return sum(b in adjacency[a] and c in adjacency[a] and c in adjacency[b]
               for a, b, c in combinations(range(len(adjacency)), 3))


def graph_certificate(point_count, lines):
    require(point_count > 0 and lines, "nonempty bipartite graph")
    point_neighbors = [set() for _ in range(point_count)]
    for line, points in enumerate(lines):
        require(points and all(type(point) is int and 0 <= point < point_count
                               for point in points), "line endpoints")
        for point in points:
            point_neighbors[point].add(line)
    b_degrees = list(map(len, point_neighbors))
    d_degrees = list(map(len, lines))
    c4 = sum(comb(len(point_neighbors[a] & point_neighbors[b]), 2)
             for a, b in combinations(range(point_count), 2))
    require(c4 == 0, "control graph is C4-free")
    require(min(b_degrees + d_degrees) >= 3, "minimum degree three")
    cycles = six_cycles(point_neighbors, lines)
    per_b = [sum(point in cycle for cycle in cycles) for point in range(point_count)]
    per_d = [sum(point_count + line in cycle for cycle in cycles)
             for line in range(len(lines))]
    require(sum(per_b) == sum(per_d) == 3 * len(cycles), "cycle incidence divisibility")
    distance_two = [set(b for b in range(point_count) if b != a
                        and point_neighbors[a] & point_neighbors[b])
                    for a in range(point_count)]
    complement = [set(range(point_count)) - neighbors - {a}
                  for a, neighbors in enumerate(distance_two)]
    u = sum(map(len, complement)) // 2
    wedges = sum(comb(len(neighbors), 2) for neighbors in complement)
    complement_triangles = triangles(complement)
    distance_triangles = triangles(distance_two)
    claws = sum(comb(degree, 3) for degree in d_degrees)
    require(distance_triangles - claws == len(cycles), "independent cycle/triangle identity")
    require(distance_triangles == comb(point_count, 3) - u * (point_count - 2)
            + wedges - complement_triangles, "triangle inclusion-exclusion")
    quotient, remainder = divmod(2 * u, point_count)
    balanced_wedges = ((point_count - remainder) * comb(quotient, 2)
                       + remainder * comb(quotient + 1, 2))
    source_bound = comb(point_count, 3) - u * (point_count - 2) + balanced_wedges
    corrected_bound = max(0, comb(point_count, 3) - u * (point_count - 2)
                          + (2 * balanced_wedges + 2) // 3)
    require(corrected_bound <= distance_triangles, "sound repaired global bound")
    moore = []
    for root, first in enumerate(lines):
        second = set().union(*(point_neighbors[b] for b in first)) - {root}
        require(all(len(lines[d] & first) == 1 for d in second), "unique second-level parent")
        third = set().union(*(lines[d] for d in second)) - first
        multiplicities = [len(point_neighbors[b] & second) for b in sorted(third)]
        edge_count = sum(multiplicities)
        require(all(len({next(iter(lines[d] & first)) for d in point_neighbors[b] & second})
                    == len(point_neighbors[b] & second) for b in third),
                "different branches meet at a third-level point")
        require(sum(comb(value, 2) for value in multiplicities) == per_d[root],
                "root six-cycles equal pairs of third-level incidences")
        k = len(first)
        require(len(second) >= 2 * k and edge_count >= 2 * len(second), "BFS expansion")
        require(len(third) >= edge_count - per_d[root], "collision accounting")
        require(point_count >= 5 * k - per_d[root], "local owner lower bound")
        moore.append([root, k, len(second), edge_count, len(third), per_d[root],
                      5 * k - per_d[root]])
    return {
        "B": point_count, "D": len(lines), "E": sum(b_degrees),
        "min_degree": min(b_degrees + d_degrees), "B_degrees": b_degrees,
        "D_degrees": d_degrees, "c4": c4, "c6": len(cycles),
        "per_B_c6": per_b, "per_D_c6": per_d,
        "distance2_triangles": distance_triangles, "claws": claws,
        "complement_edges": u, "complement_wedges": wedges,
        "complement_triangles": complement_triangles,
        "source_triangle_claim": source_bound, "sound_triangle_bound": corrected_bound,
        "moore_root_bounds": moore,
    }


def floor_certificate():
    degree_bounds = [[k, 5 * k - (1 if k == 3 else k * k // 4)]
                     for k in range(3, 15)]
    require(degree_bounds[0] == [3, 14], "cubic root lower bound")
    require(all(bound > 14 for k, bound in degree_bounds if k >= 4),
            "all noncubic root degrees excluded at fourteen owners")
    # Once D is cubic, a B-neighbor of degree at least four gives seven
    # second-level vertices, fourteen further edges, and at most one collision.
    require(3 + 2 * (3 + 2 + 2) - 1 == 16, "noncubic B neighbor exclusion")
    require(14 % 3 != 0, "fourteen cubic roots cannot each lie on exactly one six-cycle")
    return {
        "minimum_nonzero_owner_support": 15, "blocks_proved": [1, 14],
        "repair_per_owner": 104, "degree_bounds": degree_bounds,
        "degree14_divisibility": [14, 3, 14 % 3],
    }


def build():
    affine = graph_certificate(*affine_nine())
    duads = graph_certificate(*duad_fifteen())
    require((affine["B"], affine["D"], affine["E"], affine["c6"]) == (9, 9, 27, 18),
            "nine-point incidence graph")
    require(affine["source_triangle_claim"] == 30 and affine["distance2_triangles"] == 27,
            "source lower-bound counterexample")
    require(affine["source_triangle_claim"] - affine["claws"] == 21,
            "source overcounts forced six-cycles")
    require(affine["per_D_c6"] == [6] * 9, "counterexample does not meet the route cycle cap")
    require((duads["B"], duads["D"], duads["E"], duads["c4"], duads["c6"])
            == (15, 15, 45, 0, 0), "abstract sharpness control")
    return {"graph_certificates": {"affine_nine": affine, "duad_fifteen": duads},
            "floor15": floor_certificate()}


def main():
    observed = build()
    expected = json.loads((HERE / "RESULT.json").read_bytes())
    for key, value in observed.items():
        require(expected.get(key) == value, "independent receipt mismatch: " + key)
    print(json.dumps({"independent": "pass", "affine_six_cycles": 18,
                      "abstract_sharp_owner_count": 15}, sort_keys=True))


if __name__ == "__main__":
    main()
