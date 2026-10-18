"""Unequal-endpoint applications of Nick Petalas/PR3169's A5 inequality.

Historical BK/BK7 filters follow DreamingOfClouds/PR3154. Apache-2.0.
"""

# Copyright 2026 Nick Petalas

from itertools import combinations, combinations_with_replacement, product

CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
TARGET_CAP = {**CAP, 7: 32}
DISTANCE = (0, 53, 78, 92, 100, 106, 109)
TARGETS = ((3, 5, 5, 5, 6, 6, 6, 6, 6, 7),
           (4, 4, 5, 5, 6, 6, 6, 6, 6, 7))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_weights(weights):
    require(isinstance(weights, tuple) and 6 <= len(weights) <= 10
            and all(type(w) is int and w in CAP for w in weights)
            and weights == tuple(sorted(weights)), "invalid weight multiset")


def surviving_dimension(dimension, intersection, removed):
    require(all(type(x) is int for x in (dimension, intersection, removed))
            and 0 <= intersection <= dimension <= 16
            and 0 <= removed <= dimension, "invalid dimension ledger")
    return max(0, intersection - removed)


def coordinate_invoice(small, endpoints):
    """Needs independent pieces, five code dimensions and three small pieces."""
    require(type(small) is int and 0 <= small <= 112
            and isinstance(endpoints, tuple) and len(endpoints) == 6
            and all(type(x) is int and 0 <= x <= 112 for x in endpoints),
            "invalid support ledger")
    ordered = sorted(endpoints, reverse=True)
    require(small + ordered[0] < 53, "uncertified quotient independence")
    require(small + sum(ordered[:2]) < 70, "uncertified root edges")
    total = sum(endpoints)
    upper = 112 + 8 * small + 4 * total
    return {"small_support_cap": small, "endpoint_caps": list(endpoints),
            "endpoint_sum_cap": total, "quotient_support_cap": small + ordered[0],
            "edge_support_cap": small + sum(ordered[:2]),
            "edge_incidence_lower": 795, "coordinate_incidence_upper": upper,
            "old_incidence_upper": 9 * small + 5 * total,
            "margin": 795 - upper, "excluded": upper < 795}


def historical_survivor(weights):
    """Original (b,t)=(6,4) necessary filters, not a current disposition ledger."""
    validate_weights(weights)
    if sum(w - 2 for w in weights) >= 36:
        return False
    for level in range(1, 7):
        kept = weights[:len(weights) - (6 - level)]
        global_cap = sum(CAP[w] for w in kept)
        target_cap = sum(TARGET_CAP[w] for w in kept)
        target_min, global_min = ((53, 73) if level == 1 else
                                  (78, 82) if level == 2 else
                                  (DISTANCE[level], DISTANCE[level]))
        if global_cap < global_min and (level >= 3 or target_cap < target_min):
            return False
    basis = weights[:len(weights) - 6]
    if sum(CAP[w] for w in basis) >= 53:
        return True
    if sum(basis) <= 7:
        return False
    for assignment in product((0, 1), repeat=len(basis)):
        if all(sum(w for w, a in zip(basis, assignment, strict=True) if a == group)
               <= 6 for group in (0, 1)):
            return False
    return True


def prior_cover_rows(weights):
    """Every support-certified four-piece basis and weight-only two-flat cover."""
    validate_weights(weights)
    require(len(weights) == 10, "prior cover needs ten pieces")
    rows = {}
    for indices in combinations(range(10), 4):
        basis = tuple(weights[i] for i in indices)
        if basis in rows or sum(CAP[w] for w in basis) >= 53:
            continue
        complement = tuple(w for i, w in enumerate(weights) if i not in indices)
        paid = sum(CAP[w] for w in basis)
        for assignment in product(range(3), repeat=4):
            if all(sum(w for w, a in zip(basis, assignment, strict=True) if a == k)
                   <= 6 for k in (0, 1)):
                paid = min(paid, sum(CAP[w] for w, a in
                                    zip(basis, assignment, strict=True) if a == 2))
        rows[basis] = {"basis": list(basis), "complement": list(complement),
                       "support_cap": sum(CAP[w] for w in basis),
                       "minimum_two_flat_cuts": paid,
                       "rank_four_anchor": any(w <= 4 for w in complement)}
    return [rows[basis] for basis in sorted(rows)]


def application(weights):
    validate_weights(weights)
    require(weights in TARGETS, "outside the two-profile application")
    retained = weights[:-1]
    small = sum(CAP[w] for w in retained[:3])
    endpoints = tuple(CAP[w] for w in retained[3:])
    invoice = coordinate_invoice(small, endpoints)
    dimension = surviving_dimension(10, 6, 1)
    require(dimension == 5 and invoice["excluded"] and invoice["margin"] == 11,
            "failed dimension or support invoice")
    covers = prior_cover_rows(weights)
    require(covers and min(row["minimum_two_flat_cuts"] for row in covers) == 16
            and all(row["minimum_two_flat_cuts"] > 14 for row in covers),
            "earlier cut route applies")
    return {"weights": list(weights), "retained_weights": list(retained),
            "intersection_before": 6, "intersection_after_lower": dimension,
            "quotient_dimension": 4, "prior_cover_rows": covers, **invoice}


def historical_inventory():
    survivors = []
    examined = 0
    for size in range(6, 11):
        for weights in combinations_with_replacement(range(2, 8), size):
            examined += 1
            if historical_survivor(weights):
                survivors.append(weights)
    require(len(survivors) == 69 and all(w in survivors for w in TARGETS),
            "historical inventory differs")
    return {"cell": [6, 4], "multisets_examined": examined,
            "survivor_count": len(survivors),
            "applications": [application(w) for w in TARGETS]}
