"""A5 support accounting, extending Nick Petalas/PR3188 and PR3195.

The stabilizer-orbit enumeration follows the retained PR3176 root_extensions
algorithm. It keeps every orbit, including when the subgroup is not maximal.
Apache-2.0; E8/P112 source credit is in SOURCES.json and vendor/NOTICE.md.
"""

from collections import Counter
from math import comb

from vendor.geometry import dot, require


def extensions(prefix, roots):
    signed = tuple(v for r in roots for v in (r, tuple(-x for x in r)))
    candidates = {r for r in signed if all(dot(r, p) == 4 for p in prefix)}
    normals = tuple(r for r in roots if all(dot(r, p) == 0 for p in prefix))
    unseen, representatives, sizes = set(candidates), [], []
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
                require(pairing % 4 == 0, "nonintegral stabilizer reflection")
                image = tuple(
                    x - pairing // 4 * y
                    for x, y in zip(queue[index], normal, strict=True)
                )
                require(image in candidates, "reflection leaves star candidates")
                if image not in seen:
                    seen.add(image)
                    queue.append(image)
            require(len(queue) <= 240, "star orbit capacity")
        require(seen <= unseen, "overlapping star orbits")
        unseen.difference_update(seen)
        representatives.append(first)
        sizes.append(len(seen))
    require(not unseen, "incomplete star orbit coverage")
    return representatives, sizes


def star_costs(roots):
    level, steps = [()], []
    for rank in range(5):
        following = []
        for prefix in level:
            representatives, sizes = extensions(prefix, roots)
            steps.append({"rank": rank, "orbit_sizes": sizes})
            following.extend((*prefix, v) for v in representatives)
        level = following
    require(len(level) == 1, "A5 star orbit inventory")
    require(
        [s["orbit_sizes"] for s in steps] == [[240], [56], [27], [16], [10]],
        "A5 extension counts",
    )
    star = level[0]
    require(
        all(
            dot(a, b) == (8 if i == j else 4)
            for i, a in enumerate(star)
            for j, b in enumerate(star)
        ),
        "A5 star Gram matrix",
    )
    costs = tuple(
        6 - max(Counter((0, *(dot(r, v) for v in star))).values()) for r in roots
    )
    require(Counter(costs) == root_class_spectrum(), "A5 cost spectrum")
    return star, costs, steps


def root_class_spectrum():
    integer = Counter({0: 2, 1: 24, 2: 30})
    half = Counter()
    for j in range(6):
        half[min(j, 6 - j)] += 2 * comb(5, j)
    require(
        sum(integer.values()) == 56 and sum(half.values()) == 64, "root class counts"
    )
    return integer + half


def invoice(costs, small_support):
    require(
        len(costs) == 120 and all(type(c) is int and 0 <= c <= 3 for c in costs),
        "invalid A5 costs",
    )
    require(
        type(small_support) is int and 0 <= small_support <= 112,
        "invalid support budget",
    )
    cuts = min(120, 8 + small_support)
    lower = sum(sorted(costs)[: 120 - cuts])
    return {
        "small_support_cap": small_support,
        "quotient_support_cap": small_support + 20,
        "edge_support_cap": small_support + 40,
        "cuts_including_puncture": cuts,
        "full_cost": sum(costs),
        "endpoint_lower": lower,
        "endpoint_allowance": 120,
        "margin": lower - 120,
        "old_coordinate_lower": 795,
        "old_coordinate_upper": 112 + 8 * small_support + 4 * 120,
    }


def certify_slice(costs, small_support):
    result = invoice(costs, small_support)
    require(result["quotient_support_cap"] < 53, "quotient independence fails")
    require(result["edge_support_cap"] < 70, "root-only edge alphabet fails")
    require(result["margin"] > 0, "support budget is not a contradiction")
    return result
