"""Seven-endpoint exclusion for the actual P112 3,4,6^8 profile.

Nick Petalas. Apache-2.0. Geometry and mixed-edge routines retain PR3176's
exact source; this five-clique application and its support budget are new.
"""

from collections import Counter
from itertools import combinations_with_replacement, product

from vendor.geometry import dot, require
from vendor.mixed import ANCHOR, CAP, cliques, rational_rank, root_extensions

PROFILE = (3, 4) + (6,) * 8


def support_lower(costs, removed):
    require(len(costs) in (112, 120), "support inventory size")
    require(type(removed) is int and 0 <= removed <= len(costs), "deletion budget")
    require(all(type(c) is int and 0 <= c <= 6 for c in costs), "support costs")
    return sum(sorted(costs)[:len(costs) - removed])


def mixed_six(vertices, adjacency, points):
    anchor = tuple(2 * x for x in ANCHOR)
    evaluations = tuple(
        (0, dot(p, anchor), *(dot(p, v) for v in vertices)) for p in points
    )
    ranks, bounds = Counter(), Counter()
    witness = None
    for chosen in cliques(adjacency, 5):
        rank = rational_rank((anchor, *(vertices[i] for i in chosen)))
        ranks[rank] += 1
        if rank != 6:
            continue
        costs = [
            7 - max(Counter(row[:2] + tuple(row[i + 2] for i in chosen)).values())
            for row in evaluations
        ]
        lower = support_lower(costs, 32)
        bounds[lower] += 1
        if witness is None or lower < witness["lower"]:
            witness = {"lower": lower, "indices": chosen,
                       "spectrum": dict(sorted(Counter(costs).items()))}
    require(ranks == {4: 630, 5: 3360, 6: 3360}, "five-clique rank census")
    require(bounds == {142: 1344, 145: 336, 146: 336, 147: 112,
                       148: 448, 149: 560, 150: 224}, "mixed support census")
    require(witness is not None and witness["lower"] == 142, "minimum witness")
    return {"ranks": dict(sorted(ranks.items())),
            "bounds": dict(sorted(bounds.items())), "witness": witness}


def all_root_six(roots):
    level, steps = [()], []
    for rank in range(6):
        following = []
        for prefix in level:
            representatives, sizes = root_extensions(prefix, roots)
            steps.append({"rank": rank, "orbit_sizes": sizes})
            following.extend((*prefix, v) for v in representatives)
        level = following
    require(len(level) == 1, "root A6 branch count")
    costs = tuple(
        7 - max(Counter((0, *(dot(r, v) for v in level[0]))).values())
        for r in roots
    )
    require(Counter(costs) == {0: 1, 1: 21, 2: 63, 3: 35}, "A6 spectrum")
    losing = support_lower(costs, 40)
    require(losing == 137, "A6 arbitrary-deletion losing control")
    return {"steps": steps, "spectrum": dict(sorted(Counter(costs).items())),
            "losing_after_40_cuts": losing, "representative": level[0]}


def original_survivors():
    """Independent transcription of the pinned filter, only for (b,t)=(6,4)."""
    distance = (0, 53, 78, 92, 100, 106, 109)
    rows = []
    for size in range(6, 11):
        for weights in combinations_with_replacement(range(2, 8), size):
            if sum(w - 2 for w in weights) >= 36:
                continue
            feasible = True
            for level in range(1, 7):
                prefix = weights[:size - 6 + level]
                total = sum(CAP[w] for w in prefix)
                target = sum(32 if w == 7 else CAP[w] for w in prefix)
                if ((level == 1 and target < 53 and total < 73)
                        or (level == 2 and target < 78 and total < 82)
                        or (level >= 3 and total < distance[level])):
                    feasible = False
                    break
            basis = weights[:size - 6]
            killed = False
            if sum(CAP[w] for w in basis) < 53:
                killed = sum(basis) <= 7 or any(
                    all(sum(w for w, g in zip(basis, assignment, strict=True)
                            if g == group) <= 6 for group in (0, 1))
                    for assignment in product(range(2), repeat=len(basis))
                )
            if feasible and not killed:
                rows.append(weights)
    require(len(rows) == 69 and PROFILE in rows, "original (6,4) residue changed")
    return rows


def application():
    rows = original_survivors()
    small = (3, 4, 6)
    support = sum(CAP[w] for w in small)
    require(support == 32 and support + 20 < 53, "quotient basis budget")
    require(support + 40 == 72, "edge alphabet boundary")
    return {"b": 6, "t": 4, "weights": PROFILE, "original_survivors": len(rows),
            "small_weights": small, "small_support_cap": support,
            "quotient_basis_cap": support + 20, "edge_support_cap": 72,
            "endpoints": 7, "endpoint_support_cap": 140,
            "mixed_lower": 142, "all_root_lower": 141, "margin": 1}
