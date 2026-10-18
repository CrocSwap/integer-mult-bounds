"""Coordinate-sensitive root-simplex bound for six named P112 profiles."""

from itertools import combinations, combinations_with_replacement, product

from vendor.geometry import require

CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
DISTANCE = (0, 53, 78, 92, 100, 106, 109, 111, 112)


def profiles(b):
    require(type(b) is int and b in (6, 7, 8), "unsupported cell")
    return ((3, 5, 5, 5) + (6,) * b, (4, 4, 5, 5) + (6,) * b)


def coordinate_bound(n, small, large):
    require(type(n) is int and 6 <= n <= 9, "unsupported simplex size")
    require(type(small) is int and 0 <= small <= 112, "invalid small support")
    require(len(large) == n and all(type(x) is int and 0 <= x <= 112 for x in large),
            "invalid endpoint supports")
    largest = sorted(large)[-2:]
    require(small + largest[-1] < 53, "quotient independence is not certified")
    require(small + sum(largest) < 70, "root-edge hypothesis is not certified")
    edges = n * (n - 1) // 2
    cap = max(n * n // 4, 2 * n - 3)
    upper = 112 + (cap - 1) * small + (n - 2) * sum(large)
    old_upper = cap * small + (n - 1) * sum(large)
    return {"vertices": n, "edges": edges, "coordinate_cap": cap,
            "small_support_cap": small, "endpoint_support_sum_cap": sum(large),
            "basis_support_cap": small + largest[-1],
            "edge_support_cap": small + sum(largest),
            "required_incidences": 53 * edges, "upper": upper,
            "margin": 53 * edges - upper, "old_upper": old_upper,
            "old_margin": 53 * edges - old_upper}


def feasible(weights, b):
    """Independent transcription of the pinned pre-BK weight filters."""
    for level in range(1, b + 1):
        prefix = weights[:len(weights) - b + level]
        global_cap = sum(CAP[w] for w in prefix)
        target_cap = sum(32 if w == 7 else CAP[w] for w in prefix)
        if level == 1 and target_cap < 53 and global_cap < 73:
            return False
        if level == 2 and target_cap < 78 and global_cap < 82:
            return False
        if level >= 3 and global_cap < DISTANCE[level]:
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


def survivors(b):
    require(type(b) is int and b in (6, 7, 8), "unsupported survivor cell")
    rows = []
    for size in range(b, b + 5):
        for weights in combinations_with_replacement(range(2, 8), size):
            if (sum(w - 2 for w in weights) < 6 * b and feasible(weights, b)
                    and not basis_killed(weights, b)):
                rows.append(weights)
    return tuple(rows)


def cover_audit(weights):
    """Weight-certified four-piece bases, two six-flats and paid cuts."""
    require(weights in tuple(w for b in (6, 7, 8) for w in profiles(b)),
            "unsupported cover profile")
    options = []
    for basis in sorted(set(combinations(weights, 4))):
        if sum(CAP[w] for w in basis) >= 53:
            continue
        rest = list(weights)
        for w in basis:
            rest.remove(w)
        costs = []
        for assignment in product((0, 1, 2), repeat=4):
            loads = [sum(w for w, g in zip(basis, assignment, strict=True) if g == i)
                     for i in (0, 1)]
            if max(loads) <= 6:
                costs.append(sum(CAP[w] for w, g in zip(basis, assignment, strict=True)
                                 if g == 2))
        require(bool(costs), "no legal packing with paid cuts")
        options.append({"basis": list(basis), "minimum_cuts": min(costs),
                        "rank_four_anchor": min(rest) <= 4})
    require(bool(options), "no weight-certified quotient basis")
    return {"options": options, "minimum_cuts": min(x["minimum_cuts"] for x in options),
            "anchored_minimum_cuts": min((x["minimum_cuts"] for x in options
                                          if x["rank_four_anchor"]), default=None)}


def partition_controls(n):
    """All equality patterns of n values and a distinguished zero value."""
    require(type(n) is int and 6 <= n <= 9, "unsupported partition size")
    patterns = [(0,)]
    for _ in range(n):
        following = []
        for pattern in patterns:
            for value in range(max(pattern) + 2):
                following.append(pattern + (value,))
        require(len(following) <= 115975, "partition capacity exceeded")
        patterns = following
    maxima = [-1] * (n + 1)
    for pattern in patterns:
        values = pattern[1:]
        nonzero = sum(x != 0 for x in values)
        unequal = sum(x != y for x, y in combinations(values, 2))
        require(unequal <= (n - 2) * nonzero + 1, "coordinate inequality failed")
        maxima[nonzero] = max(maxima[nonzero], unequal)
    expected = {6: 877, 7: 4140, 8: 21147, 9: 115975}[n]
    require(len(patterns) == expected, "incomplete equality-pattern census")
    require(maxima[1] == n - 1 and maxima[2] == 2 * n - 3,
            "sharp one/two-nonzero controls changed")
    return {"vertices": n, "patterns": len(patterns), "maxima": maxima}


def exclusions(table):
    rows = []
    for b, count, margin in ((6, 69, 33), (7, 154, 40), (8, 251, 60)):
        original = survivors(b)
        require(len(original) == count, "independent survivor count changed")
        require(next(r[2] for r in table if r[:2] == (b, 4)) == count,
                "original survivor count disagrees")
        for weights in profiles(b):
            require(weights in original, "target is absent from original residue")
            small = sum(CAP[w] for w in weights[:3])
            bound = coordinate_bound(b + 1, small, [CAP[w] for w in weights[3:]])
            require(bound["margin"] == margin and bound["old_margin"] < 0,
                    "new/old incidence comparison changed")
            audit = cover_audit(weights)
            require(audit["minimum_cuts"] == 16, "prior deletion overlap changed")
            require(audit["anchored_minimum_cuts"] in (None, 20),
                    "prior anchor overlap changed")
            rows.append({"b": b, "t": 4, "weights": list(weights),
                         "original_survivors": count, "bound": bound,
                         "weight_cover_audit": audit})
    require(len(rows) == 6, "incomplete exclusion inventory")
    return rows
