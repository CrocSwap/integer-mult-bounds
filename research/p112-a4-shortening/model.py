"""Five-vertex E8 support costs and two-deletion P112 applications."""

from collections import Counter
from itertools import combinations, combinations_with_replacement, product

from a4_geometry import dot, require

CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
PROFILES = ((3,) + (6,) * 6 + (7,) * 2, (4, 5) + (6,) * 5 + (7,) * 2)
SPECTRUM = {0: 10, 1: 50, 2: 60}


def extensions(prefix, roots):
    """Partition candidates by reflections fixing the prefix pointwise."""
    require(len(roots) == len(set(roots)) == 120, "incomplete root inventory")
    signed = {v for r in roots for v in (r, tuple(-x for x in r))}
    require(
        len(signed) == 240 and all(dot(r, r) == 8 for r in signed),
        "invalid normalized roots",
    )
    require(len(prefix) <= 3 and all(r in signed for r in prefix), "invalid prefix")
    require(all(dot(a, b) == 4 for a, b in combinations(prefix, 2)), "not a star")
    candidates = {r for r in signed if all(dot(r, a) == 4 for a in prefix)}
    normals = [r for r in roots if all(dot(r, a) == 0 for a in prefix)]
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
                require(pairing % 4 == 0, "nonintegral reflection")
                image = tuple(
                    x - (pairing // 4) * y
                    for x, y in zip(queue[index], normal, strict=True)
                )
                require(image in candidates, "reflection leaves candidate set")
                if image not in seen:
                    seen.add(image)
                    queue.append(image)
            require(len(queue) <= 240, "orbit capacity exceeded")
        require(seen <= unseen, "overlapping orbits")
        unseen.difference_update(seen)
        classes.append((first, len(seen)))
    require(
        not unseen and sum(n for _, n in classes) == len(candidates),
        "incomplete orbit partition",
    )
    return classes, len(normals)


def costs(prefix, roots):
    signed = {v for r in roots for v in (r, tuple(-x for x in r))}
    require(len(prefix) == 4 and all(r in signed for r in prefix), "invalid A4 star")
    require(all(dot(a, b) == 4 for a, b in combinations(prefix, 2)), "not an A4 star")
    return [5 - max(Counter([0] + [dot(r, a) for a in prefix]).values()) for r in roots]


def a4_receipt(roots):
    prefix, steps = (), []
    for rank, expected in enumerate((240, 56, 27, 16)):
        classes, normals = extensions(prefix, roots)
        require(
            len(classes) == 1 and classes[0][1] == expected,
            "A4 extension orbit changed",
        )
        steps.append(
            {
                "prefix_rank": rank,
                "normal_lines": normals,
                "orbit_sizes": [n for _, n in classes],
            }
        )
        prefix += (classes[0][0],)
    values = costs(prefix, roots)
    require(dict(Counter(values)) == SPECTRUM, "A4 spectrum changed")
    return {
        "steps": steps,
        "representative": prefix,
        "spectrum": dict(sorted(Counter(values).items())),
        "total_cost": sum(values),
        "lower_after_cuts": {str(s): support_lower(s) for s in (20, 24, 26, 27)},
    }


def support_lower(small):
    require(type(small) is int and 0 <= small <= 52, "invalid common support")
    values = sorted(cost for cost, count in SPECTRUM.items() for _ in range(count))
    return sum(values[: 112 - small])  # Eight punctures, then one common small set.


def original_survivors():
    """Own transcription of TWOSIDE's b=6, t=3 filters, before later exclusions."""
    rows = []
    distance = (0, 53, 78, 92, 100, 106, 109)
    for size in range(6, 10):
        for weights in combinations_with_replacement(range(2, 8), size):
            if sum(w - 2 for w in weights) >= 36:
                continue
            feasible = True
            for level in range(1, 7):
                prefix = weights[: size - 6 + level]
                global_cap = sum(CAP[w] for w in prefix)
                target = sum(32 if w == 7 else CAP[w] for w in prefix)
                if (
                    (level == 1 and target < 53 and global_cap < 73)
                    or (level == 2 and target < 78 and global_cap < 82)
                    or (level >= 3 and global_cap < distance[level])
                ):
                    feasible = False
                    break
            if not feasible:
                continue
            basis = weights[: size - 6]
            killed = False
            if sum(CAP[w] for w in basis) < 53:
                killed = sum(basis) <= 7 or any(
                    all(
                        sum(
                            w
                            for w, g in zip(basis, assignment, strict=True)
                            if g == group
                        )
                        <= 6
                        for group in (0, 1)
                    )
                    for assignment in product((0, 1), repeat=len(basis))
                )
            if not killed:
                rows.append(weights)
    require(len(rows) == 17, "historical survivor inventory changed")
    return rows


def application(weights, required_dimension=6, deleted=2):
    require(weights in PROFILES, "unsupported profile")
    require(type(deleted) is int and 0 <= deleted <= 2, "invalid deletion count")
    require(
        type(required_dimension) is int and 2 <= required_dimension <= 8,
        "invalid code dimension",
    )
    retained = weights[: len(weights) - deleted]
    dimension = required_dimension - deleted
    require(dimension >= 4, "four code dimensions do not survive deletion")
    small = sum(CAP[w] for w in retained[:-5])
    endpoints = [CAP[w] for w in retained[-5:]]
    require(small <= 26 and max(endpoints) <= 20, "A4 shortening hypotheses fail")
    require(
        small + max(endpoints) < 53 and small + sum(endpoints[-2:]) < 70,
        "quotient or root-edge hypothesis fails",
    )
    lower = support_lower(small)
    require(lower > sum(endpoints), "no strict support contradiction")
    return {
        "weights": weights,
        "deleted_pieces": deleted,
        "retained_weights": retained,
        "retained_code_dimension_lower": dimension,
        "common_support_cap": small,
        "basis_support_cap": small + max(endpoints),
        "edge_support_cap": small + sum(endpoints[-2:]),
        "endpoint_cap": sum(endpoints),
        "endpoint_lower": lower,
        "margin": lower - sum(endpoints),
    }


def cover_audit(weights):
    """Check all weight-certified three-piece quotient bases of an original row."""
    require(weights in PROFILES, "unsupported cover profile")
    rows = []
    for basis in sorted(set(combinations(weights, 3))):
        if sum(CAP[w] for w in basis) >= 53:
            continue
        costs = []
        for assignment in product((0, 1, 2), repeat=3):
            loads = [
                sum(w for w, g in zip(basis, assignment, strict=True) if g == group)
                for group in (0, 1)
            ]
            if max(loads) <= 6:
                costs.append(
                    sum(
                        CAP[w] for w, g in zip(basis, assignment, strict=True) if g == 2
                    )
                )
        rows.append({"basis": basis, "minimum_paid_cuts": min(costs)})
    expected = 4 if weights == PROFILES[0] else 8
    require(
        rows and min(r["minimum_paid_cuts"] for r in rows) == expected,
        "old two-cut cover comparison changed",
    )
    return rows
