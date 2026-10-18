"""Exact six-vertex support bounds at the P112 shortening boundary.

Reuses Nick Petalas/PR3176's complete root/D7 alphabet and graph.
New work is Apache-2.0, copyright 2026 Nick Petalas.
"""

from collections import Counter

from mixed import ANCHOR, cliques, rational_rank, root_extensions
from vendor.geometry import dot, require


def support_costs(points, vertices):
    require(
        len(points) in (112, 120) and len(vertices) == 5, "six affine vertices required"
    )
    return tuple(
        6 - max(Counter((0, *(dot(p, v) for v in vertices))).values()) for p in points
    )


def after_cuts(costs, cuts):
    require(
        len(costs) in (112, 120)
        and type(cuts) is int
        and 0 <= cuts <= len(costs)
        and all(type(c) is int and 0 <= c <= 5 for c in costs),
        "invalid coordinate-cost budget",
    )
    return sum(sorted(costs)[: len(costs) - cuts])


def mixed_bound(vertices, adjacency, points):
    anchor = tuple(2 * x for x in ANCHOR)
    ranks, bounds = Counter(), Counter()
    witness, minimum, next_minimum = None, 1000, 1000
    for chosen in cliques(adjacency, 4):
        rows = (anchor, *(vertices[i] for i in chosen))
        rank = rational_rank(rows)
        ranks[rank] += 1
        if rank != 5:
            continue
        costs = support_costs(points, rows)
        lower = after_cuts(costs, 30)
        bounds[lower] += 1
        next_minimum = min(next_minimum, after_cuts(costs, 31))
        if lower < minimum:
            minimum = lower
            witness = {
                "indices": chosen,
                "vertices_doubled": rows,
                "cost_spectrum": dict(sorted(Counter(costs).items())),
                "cuts": sorted(range(112), key=lambda i: (-costs[i], i))[:30],
            }
    require(ranks == {3: 63, 4: 1260, 5: 3136}, "four-clique rank coverage")
    require(
        minimum == 121 and sum(bounds.values()) == 3136,
        "mixed support boundary changed",
    )
    return {
        "rank_histogram": dict(sorted(ranks.items())),
        "support_histogram": dict(sorted(bounds.items())),
        "minimum_after_30_cuts": minimum,
        "minimum_after_31_cuts": next_minimum,
        "witness": witness,
    }


def orthogonal_frames(roots):
    require(len(roots) == 120, "incomplete root inventory")
    adjacency = tuple(
        sum(1 << j for j in range(i + 1, 120) if dot(roots[i], roots[j]) == 0)
        for i in range(120)
    )
    stack, frames = [((), (1 << 120) - 1)], []
    for _ in range(2_000_000):
        if not stack:
            break
        chosen, candidates = stack.pop()
        if len(chosen) == 8:
            frames.append(chosen)
            continue
        for _ in range(120):
            if not candidates:
                break
            bit = candidates & -candidates
            candidates ^= bit
            i = bit.bit_length() - 1
            stack.append(((*chosen, i), candidates & adjacency[i]))
        require(len(stack) <= 961, "frame stack capacity")
    require(
        not stack and len(frames) == len(set(frames)) == 2025,
        "incomplete orthogonal-frame census",
    )
    return tuple(sorted(frames))


def root_bound(roots, frames):
    level, steps = [()], []
    for rank in range(5):
        following = []
        for prefix in level:
            representatives, sizes = root_extensions(prefix, roots)
            steps.append({"rank": rank, "orbit_sizes": sizes})
            following.extend((*prefix, v) for v in representatives)
        level = following
    require(len(level) == 1, "A5 star coverage changed")
    costs = support_costs(roots, level[0])
    require(Counter(costs) == {0: 4, 1: 36, 2: 60, 3: 20}, "A5 spectrum")
    histogram, witness, minimum, next_minimum = Counter(), None, 1000, 1000
    for frame in frames:
        live = tuple(costs[i] for i in range(120) if i not in frame)
        lower = after_cuts(live, 30)
        histogram[lower] += 1
        next_minimum = min(next_minimum, after_cuts(live, 31))
        if lower < minimum:
            minimum, witness = lower, frame
    require(histogram == {122: 720, 123: 720, 124: 585}, "puncture-frame bound")
    return {
        "star": level[0],
        "orbit_steps": steps,
        "full_spectrum": dict(sorted(Counter(costs).items())),
        "frames": len(frames),
        "support_histogram": dict(sorted(histogram.items())),
        "minimum_after_30_cuts": minimum,
        "minimum_after_31_cuts": next_minimum,
        "arbitrary_38_cut_control": after_cuts(costs, 38),
        "witness_frame": witness,
    }


def shortening_contract(small, endpoints, code_dimension):
    """Validate the sufficient support/dimension contract, not arbitrary pieces."""
    require(
        type(small) is int and 0 <= small <= 30,
        "common small support must be at most thirty",
    )
    require(
        isinstance(endpoints, tuple)
        and len(endpoints) == 6
        and all(type(x) is int and 0 <= x <= 20 for x in endpoints),
        "six endpoint supports of at most twenty required",
    )
    require(
        type(code_dimension) is int and 5 <= code_dimension <= 8,
        "five retained code dimensions required",
    )
    require(small + max(endpoints) < 53, "uncertified quotient independence")
    require(small + sum(sorted(endpoints)[-2:]) <= 70, "uncertified edge alphabet")
    return {
        "small_support_cap": small,
        "endpoint_caps": endpoints,
        "code_dimension_lower": code_dimension,
        "endpoint_allowance": sum(endpoints),
        "root_lower": 122,
        "mixed_lower": 121,
        "minimum_contradiction_margin": 121 - sum(endpoints),
    }
