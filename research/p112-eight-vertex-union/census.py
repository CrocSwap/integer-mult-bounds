"""Eight-vertex mixed-edge census and original TWOSIDE profile binding."""

from collections import Counter
from itertools import combinations_with_replacement, product

from vendor import mixed
from vendor.geometry import dot, require

PROFILE = (4, 5, 5) + (6,) * 8


def mixed_receipt(vertices, adjacency, points):
    anchor = tuple(2 * x for x in mixed.ANCHOR)
    evaluations = tuple(
        (0, dot(p, anchor), *(dot(p, v) for v in vertices)) for p in points
    )
    ranks, bounds, witness, minimum = Counter(), Counter(), None, 1000
    for chosen in mixed.cliques(adjacency, 6):
        rank = mixed.rational_rank((anchor, *(vertices[i] for i in chosen)))
        ranks[rank] += 1
        if rank != 7:
            continue
        values = tuple(
            row[:2] + tuple(row[i + 2] for i in chosen) for row in evaluations
        )
        costs = [8 - max(Counter(row).values()) for row in values]
        lower = sum(sorted(costs)[:80])
        bounds[lower] += 1
        if lower < minimum:
            minimum = lower
            witness = {
                "indices": chosen,
                "spectrum": dict(sorted(Counter(costs).items())),
                "vertices_doubled": [anchor] + [vertices[i] for i in chosen],
                "lower_after_33_cuts": sum(sorted(costs)[:79]),
            }
    require(ranks == {4: 105, 5: 2520, 6: 5096, 7: 2016}, "six-clique rank census")
    require(bounds == {162: 784, 163: 112, 170: 784, 175: 336}, "mixed support census")
    require(minimum == 162 and witness is not None, "mixed lower bound")
    return {
        "cliques": sum(ranks.values()),
        "rank_histogram": dict(sorted(ranks.items())),
        "support_histogram": dict(sorted(bounds.items())),
        "minimum_lower": minimum,
        "witness": witness,
    }


def survives(weights, b):
    require(
        b == 7
        and b <= len(weights) <= b + 4
        and tuple(sorted(weights)) == weights
        and all(type(w) is int and 2 <= w <= 7 for w in weights),
        "profile domain",
    )
    if sum(w - 2 for w in weights) >= 6 * b:
        return False
    distances = (0, 53, 78, 92, 100, 106, 109, 111)
    for level in range(1, b + 1):
        prefix = weights[: len(weights) - b + level]
        total = sum(mixed.CAP[w] for w in prefix)
        target = sum(32 if w == 7 else mixed.CAP[w] for w in prefix)
        if (
            (level == 1 and target < 53 and total < 73)
            or (level == 2 and target < 78 and total < 82)
            or (level >= 3 and total < distances[level])
        ):
            return False
    basis = weights[: len(weights) - b]
    if sum(mixed.CAP[w] for w in basis) >= 53:
        return True
    return not (
        sum(basis) <= 7
        or any(
            all(
                sum(w for w, g in zip(basis, assignment, strict=True) if g == group)
                <= 6
                for group in (0, 1)
            )
            for assignment in product(range(2), repeat=len(basis))
        )
    )


def application():
    survivors = tuple(
        w
        for n in range(7, 12)
        for w in combinations_with_replacement(range(2, 8), n)
        if survives(w, 7)
    )
    require(PROFILE in survivors, "profile not in original residue")
    return {
        "b": 7,
        "t": 4,
        "weights": PROFILE,
        "original_survivors": len(survivors),
        "deficit": 42 - sum(w - 2 for w in PROFILE),
        "small_support_cap": 32,
        "quotient_basis_cap": 52,
        "edge_support_cap": 72,
        "endpoint_allowance": 160,
        "mixed_lower": 162,
        "all_root_lower": 162,
        "margin": 2,
    }
