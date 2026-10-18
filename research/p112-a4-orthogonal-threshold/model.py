"""Exact A4 orbit coverage, Parseval bound and support29 construction.

The extension-orbit argument follows Nick Petalas/PR3211. The frame bound
adapts PR3207. New threshold and witness checks are Apache-2.0.
"""

from collections import Counter
from itertools import combinations, combinations_with_replacement

from algebra import parse_witness, rank, require, support
from geometry import dot


def extensions(prefix, roots):
    signed = {v for r in roots for v in (r, tuple(-x for x in r))}
    require(len(signed) == 240, "signed-root inventory")
    candidates = {r for r in signed if all(dot(r, a) == 4 for a in prefix)}
    normals = tuple(r for r in roots if all(dot(r, a) == 0 for a in prefix))
    require(len(prefix) <= 3 and len(candidates) <= 240, "extension bound")
    unseen, classes = set(candidates), []
    for _ in range(240):
        if not unseen:
            break
        first = min(unseen)
        queue, seen = [first], {first}
        for index in range(240):
            if index >= len(queue):
                break
            for normal in normals:
                pairing = dot(queue[index], normal)
                require(pairing % 4 == 0, "reflection integrality")
                image = tuple(
                    x - (pairing // 4) * y
                    for x, y in zip(queue[index], normal, strict=True)
                )
                require(image in candidates, "reflection leaves extension inventory")
                if image not in seen:
                    seen.add(image)
                    queue.append(image)
            require(len(queue) <= 240, "orbit capacity")
        require(seen <= unseen, "overlapping extension orbits")
        unseen.difference_update(seen)
        classes.append((first, len(seen)))
    require(
        not unseen and sum(n for _, n in classes) == len(candidates),
        "incomplete extension partition",
    )
    return classes


def evaluation(roots, star):
    require(len(roots) == 120 and len(star) == 4, "evaluation shape")
    require(
        all(
            dot(a, b) == 4 + 4 * int(i == j)
            for i, a in enumerate(star)
            for j, b in enumerate(star)
        ),
        "A4 Gram",
    )
    raw = tuple((0, *(dot(r, a) for a in star)) for r in roots)
    require(all(x % 4 == 0 for row in raw for x in row), "evaluation integrality")
    values = tuple(tuple(x // 4 for x in row) for row in raw)
    costs = tuple(5 - max(Counter(row).values()) for row in values)
    require(Counter(costs) == {0: 10, 1: 50, 2: 60}, "A4 cost spectrum")
    return values, costs


def orbit_receipt(roots):
    prefix, steps = (), []
    for expected in (240, 56, 27, 16):
        classes = extensions(prefix, roots)
        require(len(classes) == 1 and classes[0][1] == expected, "A4 orbit coverage")
        steps.append(expected)
        prefix += (classes[0][0],)
    _, costs = evaluation(roots, prefix)
    return {
        "extension_orbit_sizes": steps,
        "representative": prefix,
        "spectrum": dict(sorted(Counter(costs).items())),
        "total_cost": sum(costs),
    }


def frame_bound(counts):
    require(
        len(counts) == 3 and all(type(x) is int and 0 <= x <= 8 for x in counts),
        "frame count domain",
    )
    c0, c1, c2 = counts
    require(c0 + c1 + c2 == 8, "frame cardinality")
    require(4 * c1 + 6 * c2 <= 40, "Parseval variance constraint")
    require(3 * c0 + c1 >= 4 and 2 * c0 + c1 >= 3, "integer frame consequence")
    return c1 + 2 * c2


def scalar_receipt():
    minima, patterns = {1: 1000, 2: 1000}, 0
    for values in combinations_with_replacement(range(-2, 3), 5):
        patterns += 1
        cost = 5 - max(Counter(values).values())
        variance5 = 5 * sum(x * x for x in values) - sum(values) ** 2
        require(
            variance5 == sum((a - b) ** 2 for a, b in combinations(values, 2)),
            "pairwise variance identity",
        )
        if cost in minima:
            minima[cost] = min(minima[cost], variance5)
    require((patterns, minima) == (126, {1: 4, 2: 6}), "scalar variance minima")
    star = tuple(tuple(int(i in (0, j)) for i in range(8)) for j in range(1, 5))
    trace = sum(dot(r, r) for r in star)
    total = tuple(sum(r[i] for r in star) for i in range(8))
    require((trace, dot(total, total)) == (8, 20), "Parseval Gram trace")
    signatures = [(a, b, 8 - a - b) for a in range(9) for b in range(9 - a)]
    accepted = [r for r in signatures if 4 * r[1] + 6 * r[2] <= 40]
    require(
        len(signatures) == 45 and max(frame_bound(r) for r in accepted) == 13,
        "symbolic frame maximum",
    )
    return {
        "integer_patterns": patterns,
        "variance5_minima": minima,
        "signatures": len(signatures),
        "admissible_signatures": len(accepted),
        "maximum_frame_cost": 13,
        "lower_after_cuts": {s: 157 - 2 * s for s in (26, 27, 28, 29)},
        "old_arbitrary_puncture_lower_at_28": 98,
    }


def witness_receipt(roots, points, labels, raw):
    star, cuts, endpoints = parse_witness(raw)
    values, costs = evaluation(roots, star)
    frame = tuple(i for i, r in enumerate(roots) if r not in points)
    require(
        len(frame) == 8
        and all(dot(roots[i], roots[j]) == 0 for i, j in combinations(frame, 2)),
        "fixed frame",
    )
    variances = tuple(5 * sum(x * x for x in v) - sum(v) ** 2 for v in values)
    require(sum(variances[i] for i in frame) == 40, "frame Parseval identity")
    frame_counts = tuple(sum(costs[i] == c for i in frame) for c in range(3))
    require(frame_bound(frame_counts) == 13, "attaining frame cost")
    return piece_receipt(points, labels, star, cuts, endpoints, frame_counts)


def piece_receipt(points, labels, star, cuts, endpoints, frame_counts):
    codewords = tuple(tuple(dot(r, a) // 4 for r in points) for a in star)
    values = tuple((0, *(row[t] for row in codewords)) for t in range(112))
    shifts = tuple(min(Counter(v), key=lambda x: (-v.count(x), x)) for v in values)
    generated = tuple(
        tuple(0 if t in cuts else v[i] - shifts[t] for t, v in enumerate(values))
        for i in range(5)
    )
    require(endpoints == generated, "literal endpoint coefficients")
    small = tuple(
        tuple(x if t in cuts else 0 for t, x in enumerate(c)) for c in codewords
    )
    require(frozenset().union(*(support(r) for r in small)) == cuts, "small union")
    require(all(not support(q) & cuts for q in endpoints), "disjoint piece groups")
    require(
        all(
            codewords[i][t] == endpoints[i + 1][t] - endpoints[0][t] + small[i][t]
            for i in range(4)
            for t in range(112)
        ),
        "four exact inclusion relations",
    )
    code = tuple(tuple(r[i] for r in points) for i in range(8))
    pieces = small + endpoints
    matrices = {
        "small": small,
        "endpoints": endpoints,
        "pieces": pieces,
        "code": code,
        "combined": pieces + code,
        "directions": star,
    }
    pivots = {name: rank(rows) for name, rows in matrices.items()}
    ranks = {name: len(columns) for name, columns in pivots.items()}
    require(
        ranks
        == {
            "small": 4,
            "endpoints": 5,
            "pieces": 9,
            "code": 8,
            "combined": 13,
            "directions": 4,
        },
        "rational rank certificate",
    )
    sizes = [len(support(q)) for q in endpoints]
    require(sizes == [20, 19, 20, 20, 20], "endpoint support sizes")
    costs = tuple(5 - max(Counter(v).values()) for v in values)
    require(all(costs[t] == 2 for t in cuts) and sum(sizes) == 99, "attaining cuts")
    label_ranks = [binary_rank([labels[t] for t in support(r)]) for r in pieces]
    return {
        "small_union": len(cuts),
        "small_supports": [len(support(r)) for r in small],
        "endpoint_supports": sizes,
        "total_endpoint_support": sum(sizes),
        "frame_cost_counts": frame_counts,
        "ranks": ranks,
        "pivot_columns": pivots,
        "binary_support_ranks": label_ranks,
        "intersection_dimension": ranks["pieces"] + ranks["code"] - ranks["combined"],
    }


def binary_rank(labels):
    require(
        len(labels) <= 112 and all(type(x) is int and 0 < x < 512 for x in labels),
        "binary rank domain",
    )
    basis = [0] * 9
    for label in labels:
        for bit in range(8, -1, -1):
            if label >> bit & 1:
                if basis[bit]:
                    label ^= basis[bit]
                else:
                    basis[bit] = label
                    break
    return sum(x != 0 for x in basis)
