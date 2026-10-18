"""Bind three eleven-piece applications to the original TWOSIDE filters."""

from itertools import combinations, combinations_with_replacement, product

from geometry import require

CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
TARGET_CAP = {**CAP, 7: 32}
DISTANCE = (0, 53, 78, 92, 100, 106)
PROFILES = ((3, 3) + (5,) * 9,
            (3, 4, 4) + (5,) * 8,
            (4,) * 4 + (5,) * 7)


def validate(weights):
    require(5 <= len(weights) <= 11, "piece count outside this audit")
    require(all(type(w) is int and 2 <= w <= 7 for w in weights),
            "invalid piece weights")
    require(tuple(sorted(weights)) == tuple(weights), "weights must be sorted")


def prefixes(weights):
    validate(weights)
    return tuple(sum(CAP[w] for w in weights[:len(weights) - 5 + level])
                 for level in range(1, 6))


def survives(weights):
    """Original BK/BK7 necessary rules, fixed b=5 and t<=6."""
    validate(weights)
    if sum(w - 2 for w in weights) >= 30:
        return False
    for level, total in enumerate(prefixes(weights), 1):
        kept = weights[:len(weights) - 5 + level]
        target = sum(TARGET_CAP[w] for w in kept)
        if level == 1 and not (target >= 53 or total >= 73):
            return False
        if level == 2 and not (target >= 78 or total >= 82):
            return False
        if level >= 3 and total < DISTANCE[level]:
            return False
    basis = weights[:len(weights) - 5]
    if sum(CAP[w] for w in basis) >= 53:
        return True
    if sum(basis) <= 7:
        return False
    for assignment in product((0, 1), repeat=len(basis)):
        if all(sum(w for w, side in zip(basis, assignment, strict=True)
                   if side == group) <= 6 for group in (0, 1)):
            return False
    return True


def support_budget(small, endpoint):
    require(all(type(x) is int and 0 < x <= 112 for x in (small, endpoint)),
            "invalid support capacities")
    require(small + endpoint < 53 and small + 3 * endpoint < 70,
            "strict quotient support thresholds fail")
    selected = small + endpoint
    require(selected + 2 * endpoint < 70, "strict root-edge threshold fails")
    upper = 9 * selected + 5 * 6 * endpoint
    require(upper < 15 * 53, "no incidence contradiction")
    return selected, 6 * endpoint, upper


def application(weights):
    validate(weights)
    require(len(weights) == 11 and survives(weights), "not an eleven-piece survivor")
    small = sum(CAP[w] for w in weights[:4])
    remaining = tuple(CAP[w] for w in weights[4:])
    require(small <= 32 and len(remaining) == 7 and max(remaining) <= 12,
            "quotient-selection hypotheses fail")
    basis_caps = tuple(sum(CAP[weights[i]] for i in subset)
                       for subset in combinations(range(11), 6))
    selected, endpoints, upper = support_budget(small, max(remaining))
    return {"weights": weights, "deficit": 30 - sum(w - 2 for w in weights),
            "prefix_caps": prefixes(weights), "four_small_cap": small,
            "three_class_cap": small + 36, "selected_five_cap": selected,
            "endpoint_sum_cap": endpoints, "edge_cap": selected + 24,
            "old_support_basis_subsets": len(basis_caps),
            "minimum_six_piece_support_cap": min(basis_caps),
            "support_certified_bases": sum(cap < 53 for cap in basis_caps),
            "incidence_lower": 795, "incidence_upper": upper,
            "contradiction_margin": 795 - upper}


def beta_receipt():
    survivors = [weights for length in range(5, 12)
                 for weights in combinations_with_replacement(range(2, 8), length)
                 if survives(weights)]
    require(len(survivors) == 77, "original beta survivor inventory changed")
    require(all(weights in survivors for weights in PROFILES), "application binding")
    return {"cell": [5, 6], "original_survivors": survivors,
            "new_exclusions": [application(weights) for weights in PROFILES]}
