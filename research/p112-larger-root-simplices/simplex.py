"""Larger root-simplex incidence bounds and the three named weight shapes."""

from itertools import combinations, combinations_with_replacement, product

from vendor.geometry import canonical, dot, require

CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
TARGETS = {b: (2, 5, 5, 5) + (6,) * b for b in (6, 7, 8)}


def incidence_bound(b, small_cap, large_caps):
    """Return a conditional certificate, never accept an uncertified boundary."""
    require(type(b) is int and 5 <= b <= 8, "unsupported simplex dimension")
    require(type(small_cap) is int and 0 <= small_cap <= 112,
            "invalid small-support capacity")
    require(len(large_caps) == b + 1
            and all(type(x) is int and 0 <= x <= 112 for x in large_caps),
            "invalid large-support capacities")
    caps = sorted(large_caps)
    basis_cap, edge_cap = small_cap + caps[-1], small_cap + sum(caps[-2:])
    require(basis_cap < 53, "quotient basis is not certified")
    require(edge_cap < 70, "edge directions are not certified to be roots")
    vertices = b + 1
    edges = vertices * b // 2
    coordinate_cap = max(vertices * vertices // 4, 2 * vertices - 3)
    lower = edges * 53 - coordinate_cap * small_cap
    upper = b * sum(caps)
    return {"vertices": vertices, "edges": edges, "coordinate_cap": coordinate_cap,
            "small_support_cap": small_cap, "large_support_sum_cap": sum(caps),
            "quotient_basis_support_cap": basis_cap, "edge_support_cap": edge_cap,
            "outside_lower": lower, "outside_upper": upper,
            "margin": lower - upper, "excluded": lower > upper}


def target_bound(b):
    require(type(b) is int and b in TARGETS, "unsupported target")
    return {"b": b, "t": 4, "weights": list(TARGETS[b]),
            "small_weights": [2, 5, 5], "large_weights": [5] + [6] * b,
            **incidence_bound(b, 26, [12] + [20] * b)}


def feasible(weights, b):
    """The pinned TWOSIDE weight-only filters, before BK/BK7."""
    require(5 <= b <= 8 and b <= len(weights) <= b + 6
            and tuple(sorted(weights)) == weights and all(w in CAP for w in weights),
            "invalid ordered weight row")
    distances = (0, 53, 78, 92, 100, 106, 109, 111, 112)
    for level in range(1, b + 1):
        prefix = weights[:len(weights) - b + level]
        global_cap = sum(CAP[w] for w in prefix)
        target_cap = sum(32 if w == 7 else CAP[w] for w in prefix)
        if level == 1 and target_cap < 53 and global_cap < 73:
            return False
        if level == 2 and target_cap < 78 and global_cap < 82:
            return False
        if level >= 3 and global_cap < distances[level]:
            return False
    return True


def basis_killed(weights, b):
    basis = weights[:len(weights) - b]
    if sum(CAP[w] for w in basis) >= 53:
        return False
    if sum(basis) <= 7:
        return True
    for assignment in product((0, 1), repeat=len(basis)):
        loads = [sum(w for w, group in zip(basis, assignment, strict=True) if group == g)
                 for g in (0, 1)]
        if max(loads) <= 6:
            return True
    return False


def survivor_rows(b, t=4):
    require(type(b) is int and 5 <= b <= 8 and type(t) is int and 1 <= t <= 6,
            "invalid TWOSIDE cell")
    rows = []
    for size in range(b, b + t + 1):
        for weights in combinations_with_replacement(range(2, 8), size):
            if (sum(w - 2 for w in weights) < 6 * b and feasible(weights, b)
                    and not basis_killed(weights, b)):
                rows.append(weights)
    return tuple(rows)


def cover_audit(weights):
    """Exhaust all four-piece weight-certified bases and two six-flat packs."""
    require(weights in TARGETS.values(), "unsupported cover-audit shape")
    costs, anchored_costs = [], []
    bases = set(combinations(weights, 4))
    certified = 0
    for basis in sorted(bases):
        if sum(CAP[w] for w in basis) >= 53:
            continue
        certified += 1
        rest = list(weights)
        for w in basis:
            rest.remove(w)
        for assignment in product((0, 1, 2), repeat=4):
            loads = [sum(w for w, g in zip(basis, assignment, strict=True) if g == i)
                     for i in (0, 1)]
            if max(loads) > 6:
                continue
            cost = sum(CAP[w] for w, g in zip(basis, assignment, strict=True) if g == 2)
            costs.append(cost)
            if min(rest) <= 4:
                anchored_costs.append(cost)
    require(costs and certified == 2, "weight-certified cover inventory changed")
    return {"distinct_basis_weight_multisets": len(bases), "certified_bases": certified,
            "minimum_separate_deletion_budget": min(costs),
            "rank_four_anchor_minimum_budget": min(anchored_costs, default=None)}


def simplex_fixture(roots, points, b):
    """One literal positive fixture per size; not universal direction coverage."""
    require(b in (6, 7, 8), "unsupported fixture size")
    vertices = [(0,) * 8]
    for i in range(1, min(b, 7) + 1):
        vertex = [0] * 8
        vertex[0], vertex[i] = (-2 if b == 7 else 2), 2
        vertices.append(tuple(vertex))
    if b == 8:
        vertices.append((1,) * 8)
    require(len(vertices) == b + 1, "fixture vertex count")
    edges = [canonical(tuple(x - y for x, y in zip(a, c, strict=True)))
             for a, c in combinations(vertices, 2)]
    require(len(set(edges)) == b * (b + 1) // 2 and all(e in roots for e in edges),
            "fixture is not a root simplex")
    require(all(dot(a, c) == (8 if i == j else 4)
                for i, a in enumerate(vertices[1:]) for j, c in enumerate(vertices[1:])),
            "fixture Gram matrix is not I+J")
    histogram = {}
    for root in points:
        values = [dot(root, vertex) for vertex in vertices]
        count = sum(x != y for x, y in combinations(values, 2))
        histogram[str(count)] = histogram.get(str(count), 0) + 1
    maximum = max(map(int, histogram))
    require(maximum <= (b + 1) ** 2 // 4, "fixture exceeds universal incidence cap")
    return {"vertices": [list(v) for v in vertices], "incidence_histogram": histogram,
            "maximum": maximum}
