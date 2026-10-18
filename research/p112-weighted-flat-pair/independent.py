"""Separate 3+3 clique check and root-generated high-cost flat enumeration.

Shares retained root reconstruction, rational Gram intersections, integer rank,
and the proved full120 five-flat capacity twelve. Does not call the primary
annihilator enumerator, six-clique iterator, rank code, or pair-bound function.
"""

import hashlib
import json
from collections import Counter
from itertools import combinations

from vendor.geometry import frame_lines, require, root_data
from vendor.independent_mixed import (
    A,
    direction_inventory,
    gram_vertices,
    graph,
    inner,
    integer_rank,
)
from verify import PACKAGE, bind_sources, full_labels, read_bytes


def split_six(adjacency):
    triples = tuple(
        indices
        for indices in combinations(range(58), 3)
        if all(adjacency[i] >> j & 1 for i, j in combinations(indices, 2))
    )
    require(len(triples) == 2114, "independent triple inventory")
    result = []
    masks = tuple(sum(1 << i for i in t) for t in triples)
    for left in triples:
        common = adjacency[left[0]] & adjacency[left[1]] & adjacency[left[2]]
        for right, mask in zip(triples, masks, strict=True):
            if left[-1] < right[0] and mask & common == mask:
                result.append((*left, *right))
    require(len(result) == len(set(result)) == 9737, "3+3 clique coverage")
    return tuple(result)


def mixed_check(vertices, adjacency):
    points = tuple(r for r in root_data()[0] if r not in frame_lines())
    anchor, ranks, bounds = tuple(2 * x for x in A), Counter(), Counter()
    for indices in split_six(adjacency):
        rows = (anchor, *(vertices[i] for i in indices))
        rank = integer_rank((*rows, (0,) * 8))
        ranks[rank] += 1
        if rank == 7:
            costs = []
            for point in points:
                values = [0] + [inner(point, row) for row in rows]
                costs.append(8 - max(values.count(x) for x in values))
            bounds[sum(sorted(costs)[:80])] += 1
    return dict(sorted(ranks.items())), dict(sorted(bounds.items()))


def binary_basis(rows):
    require(
        len(rows) <= 5 and all(type(x) is int and 0 <= x < 512 for x in rows),
        "binary basis input",
    )
    pivots = [0] * 9
    for value in rows:
        for column in range(8, -1, -1):
            if value >> column & 1:
                if pivots[column]:
                    value ^= pivots[column]
                else:
                    pivots[column] = value
                    break
    for column in range(9):
        if pivots[column]:
            for other in range(column + 1, 9):
                if pivots[other] >> column & 1:
                    pivots[other] ^= pivots[column]
    return tuple(value for value in reversed(pivots) if value)


def span(basis):
    require(len(basis) <= 5, "binary span dimension")
    values = [0]
    for row in basis:
        values.extend(tuple(x ^ row for x in values))
    require(
        len(values) == len(set(values)) == 1 << len(basis), "dependent binary basis"
    )
    return tuple(values)


def generated_flats(labels, costs):
    high = tuple(label for label, cost in zip(labels, costs, strict=True) if cost == 4)
    require(len(high) == 35, "high-cost root labels")
    high_set, bases, fours = set(high), set(), set()
    for chosen in combinations(high, 5):
        basis = binary_basis(chosen)
        if len(basis) == 5:
            bases.add(basis)
    for chosen in combinations(high, 4):
        basis = binary_basis(chosen)
        if len(basis) != 4 or sum(x in high_set for x in span(basis)) != 8:
            continue
        fours.add(basis)
    require(len(fours) == 105, "rank-four high-cost intersection count")
    for basis in fours:
        for extra in range(1, 512):
            extended = binary_basis((*basis, extra))
            if len(extended) == 5:
                bases.add(extended)
        require(len(bases) <= 400_000, "generated-flat capacity")
    label_bits = {label: 1 << i for i, label in enumerate(labels)}
    selected = set()
    for basis in bases:
        mask = sum(label_bits.get(x, 0) for x in span(basis))
        score = sum(costs[i] for i in range(120) if mask >> i & 1)
        require(mask.bit_count() <= 12, "independent generated-flat capacity")
        if score >= 40:
            selected.add(mask)
    require(len(selected) == 3248, "independent selected-flat count")
    return tuple(sorted(selected)), len(bases), len(fours)


def reflection_checks(roots, labels, prefix):
    # Every root reflection is an invertible linear map on (1, simple coordinates mod 2).
    index = {r: i for i, r in enumerate(roots)}
    checks = 0
    for v in prefix:
        mapped = []
        for r in roots:
            p = inner(r, v)
            image = tuple(r[i] - p // 4 * v[i] for i in range(8))
            image = max(image, tuple(-x for x in image))
            mapped.append(labels[index[image]])
        # Recover the 9-column F2 map from the 120 paired labels by elimination.
        pivots = [None] * 9
        for x, y in zip(labels, mapped, strict=True):
            for column in range(8, -1, -1):
                if x >> column & 1:
                    if pivots[column] is None:
                        pivots[column] = (x, y)
                        break
                    a, b = pivots[column]
                    x, y = x ^ a, y ^ b
            if x == 0:
                require(y == 0, "reflection violates binary label relation")
            checks += 1
        require(all(row is not None for row in pivots), "full binary label rank")
    return checks


def frame_check(roots, selected, costs):
    # Independent nested bitset expansion, retaining all 2025 frames rather than orbits.
    orthogonal = tuple(
        frozenset(j for j, s in enumerate(roots) if inner(r, s) == 0) for r in roots
    )
    level = {(i,) for i in range(120)}
    for _ in range(7):
        following = set()
        for chosen in level:
            common = set(range(chosen[-1] + 1, 120))
            for i in chosen:
                common.intersection_update(orthogonal[i])
            following.update((*chosen, j) for j in common)
        require(len(following) <= 150_000, "independent frame level capacity")
        level = following
    require(len(level) == 2025, "independent frame inventory")
    high = sum(1 << i for i, cost in enumerate(costs) if cost == 4)
    nonzero = sum(1 << i for i, cost in enumerate(costs) if cost)
    hist, decisions = Counter(), Counter()
    for frame in level:
        mask = sum(1 << i for i in frame)
        fw = sum(costs[i] for i in frame)
        hist[fw] += 1
        if fw == 16:
            continue
        threshold = 148 - fw - 80
        candidates = {m & ~mask for m in selected}
        candidates = sorted(
            m
            for m in candidates
            if 2 * ((m & nonzero).bit_count() + (m & high).bit_count()) >= threshold
        )
        maximum = 0
        for i, a in enumerate(candidates):
            for b in candidates[i:]:
                union = a | b
                score = 2 * ((union & nonzero).bit_count() + (union & high).bit_count())
                maximum = max(maximum, score)
        require(fw + maximum + 32 < 148, "independent weighted-pair rejection failed")
        decisions[(fw, len(candidates), maximum)] += 1
    return dict(sorted(hist.items())), [
        (*key, n) for key, n in sorted(decisions.items())
    ]


def main():
    bind_sources()
    expected = json.loads(read_bytes(PACKAGE / "RESULT.json"))
    directions = direction_inventory()
    vertices = gram_vertices(directions)
    adjacency = graph(vertices, directions)
    raw = json.dumps(
        {"vertices_doubled": vertices, "adjacency": adjacency},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    require(
        hashlib.sha256(raw).hexdigest() == expected["graph_sha256"], "independent graph"
    )
    ranks, bounds = mixed_check(vertices, adjacency)
    require(
        {str(k): v for k, v in ranks.items()} == expected["mixed"]["ranks"],
        "independent ranks",
    )
    require(
        {str(k): v for k, v in bounds.items()} == expected["mixed"]["bounds"],
        "independent bounds",
    )
    roots, _, _, coordinates = root_data()
    prefix = expected["root"]["representatives"][1]
    costs = tuple(
        8 - max(values.count(x) for x in values)
        for r in roots
        for values in [[0] + [inner(r, v) for v in prefix]]
    )
    labels = full_labels(coordinates)
    selected, bases, four_count = generated_flats(labels, costs)
    digest = hashlib.sha256(
        json.dumps(selected, separators=(",", ":")).encode()
    ).hexdigest()
    require(
        digest == expected["exceptional"]["selected_masks_sha256"],
        "independent flat masks",
    )
    label_checks = reflection_checks(roots, labels, prefix)
    frame_hist, decisions = frame_check(roots, selected, costs)
    print(
        json.dumps(
            {
                "generated_bases": bases,
                "rank_four_subsets": four_count,
                "label_checks": label_checks,
                "frame_histogram": frame_hist,
                "weighted_pair_decisions": decisions,
            },
            sort_keys=True,
        )
    )
    print(
        "PASS_INDEPENDENT_WEIGHTED_PAIR cliques=9737 rank7=2016 "
        "selected_flats=3248 frames=2025 support_lower=162"
    )


if __name__ == "__main__":
    main()
