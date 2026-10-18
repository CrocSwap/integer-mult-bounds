#!/usr/bin/env python3
"""Exact finite audit of a distance-2 triangle proxy used in the centre screen."""

from itertools import combinations
from math import comb


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def triangles(vertices, edges):
    return [
        triple
        for triple in combinations(vertices, 3)
        if all(tuple(sorted(pair)) in edges for pair in combinations(triple, 2))
    ]


def main():
    m = 13
    vertices = tuple(range(m))
    offsets = (0, 1, 3)

    # B_i and D_j are adjacent exactly when i-j is one of 0, 1, 3 mod 13.
    d_neighborhoods = {
        j: tuple(sorted((j + offset) % m for offset in offsets))
        for j in vertices
    }
    b_neighborhoods = {
        i: tuple(j for j in vertices if i in d_neighborhoods[j])
        for i in vertices
    }
    require(all(len(nbrs) == 3 for nbrs in d_neighborhoods.values()), "D-side degree 3")
    require(all(len(nbrs) == 3 for nbrs in b_neighborhoods.values()), "B-side degree 3")

    pair_multiplicity = {}
    distance2_edges = set()
    for j, nbrs in d_neighborhoods.items():
        for pair in combinations(nbrs, 2):
            pair = tuple(sorted(pair))
            pair_multiplicity[pair] = pair_multiplicity.get(pair, 0) + 1
            distance2_edges.add(pair)
    require(len(pair_multiplicity) == 39, "39 distinct B pairs occur in D neighborhoods")
    require(max(pair_multiplicity.values()) == 1, "no B pair repeats across D neighborhoods")
    require(len(distance2_edges) == 39, "G2 has 39 edges")
    # Two B vertices share at most one D neighbor, exactly the no-C4 condition.
    require(all(
        sum(a in d and b in d for d in d_neighborhoods.values()) <= 1
        for a, b in combinations(vertices, 2)
    ), "C4-free incidence graph")

    distance2_triangles = triangles(vertices, distance2_edges)
    complement_edges = {
        pair for pair in combinations(vertices, 2) if pair not in distance2_edges
    }
    complement_triangles = triangles(vertices, complement_edges)
    complement_degrees = {
        v: sum(v in pair for pair in complement_edges) for v in vertices
    }
    complement_wedges = sum(comb(degree, 2) for degree in complement_degrees.values())

    # Every D neighborhood gives one claw triangle. In a C4-free incidence
    # graph, any distance-2 triangle not contained in one D neighborhood is a
    # 6-cycle; uniqueness of every B-pair's common D verifies this decomposition.
    claw_triangles = {
        tuple(sorted(triple))
        for triple in d_neighborhoods.values()
    }
    require(len(claw_triangles) == len(d_neighborhoods) == 13, "13 distinct incidence claws")
    require(claw_triangles <= set(distance2_triangles), "each D neighborhood is a G2 triangle")
    six_cycles = len(set(distance2_triangles) - claw_triangles)

    U = len(complement_edges)
    q, r = divmod(2 * U, m)
    balanced_wedge_minimum = r * comb(q + 1, 2) + (m - r) * comb(q, 2)
    proxy_triangles = comb(m, 3) - U * (m - 2) + balanced_wedge_minimum
    proxy_six_cycle_lower_bound = proxy_triangles - len(claw_triangles)
    degree3_capacity = (m * 1) // 3

    # Inclusion-exclusion over absent pairs gives the exact identity. The
    # audited proxy omits complement triangles and inserts only a minimum
    # wedge count, so it can lie above the true triangle count.
    exact_triangles_from_complement = (
        comb(m, 3) - U * (m - 2) + complement_wedges - len(complement_triangles)
    )
    require(complement_degrees == {v: 6 for v in vertices}, "complement is 6-regular")
    require(U == 39, "complement edge count")
    require(complement_wedges == balanced_wedge_minimum == 195, "balanced wedge minimum attained")
    require(len(complement_triangles) == 13, "exact complement triangle count")
    require(len(distance2_triangles) == exact_triangles_from_complement == 39,
            "distance-2 triangle count and complement identity agree")
    require(six_cycles == 26, "exact non-claw triangle count")
    require(proxy_triangles == 52, "audited proxy triangle value")
    require(proxy_six_cycle_lower_bound == 39, "audited proxy six-cycle value")
    require(proxy_six_cycle_lower_bound > six_cycles, "proxy exceeds true six-cycle count")
    require(degree3_capacity == 4, "degree-3 cycle-capacity calculation")
    # The construction is not a braid-capacity witness: it has more than four
    # six-cycles, so this audit refutes only the proxy's lower-bound status.
    require(six_cycles > degree3_capacity, "example is not braid-capacity feasible")

    print(
        "PASS_CENTRE_BRAID_TRIANGLE_AUDIT",
        "m=13",
        "degrees=3/3",
        "C4=0",
        "G2_edges=39",
        "G2_triangles=39",
        "claws=13",
        "six_cycles=26",
        "complement_triangles=13",
        "proxy_triangles=52",
        "proxy_cycle_value=39",
        "degree3_capacity=4",
        "no_labelled_feasibility_claim",
    )


if __name__ == "__main__":
    main()
