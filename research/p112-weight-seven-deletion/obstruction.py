"""Delete one unrestricted piece before applying the P112 A5 coordinate bound.

The inequality is Nick Petalas/PR3169's. Historical necessary filters below
follow DreamingOfClouds/PR3154 TWOSIDE, not a new decoder reduction.
Apache-2.0. Exact source pins and retained text are in SOURCES.json.
"""

from itertools import combinations, combinations_with_replacement, product

from geometry import require

CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
TARGET_CAP = {**CAP, 7: 32}
DISTANCE = (0, 53, 78, 92, 100, 106, 109)
TARGET = (4, 4, 4, 6, 6, 6, 6, 6, 6, 7)
RETAINED = TARGET[:-1]


def intersection_after_deletion(dimension, intersection, removed):
    """A codimension-r restriction loses at most r intersection dimensions."""
    require(all(type(x) is int for x in (dimension, intersection, removed))
            and 0 <= intersection <= dimension <= 16
            and 0 <= removed <= dimension, "invalid dimension ledger")
    return max(0, intersection - removed)


def coordinate_bound(small_cap, endpoint_caps):
    """PR3169's bound, after independently certifying the support hypotheses."""
    require(type(small_cap) is int and 0 <= small_cap <= 112
            and len(endpoint_caps) == 6
            and all(type(x) is int and 0 <= x <= 112 for x in endpoint_caps),
            "invalid support ledger")
    ordered = sorted(endpoint_caps, reverse=True)
    quotient_cap = small_cap + ordered[0]
    edge_cap = small_cap + sum(ordered[:2])
    require(quotient_cap < 53, "quotient independence is uncertified")
    require(edge_cap < 70, "root-edge classification is uncertified")
    total = sum(endpoint_caps)
    old_upper = 9 * small_cap + 5 * total
    upper = 112 + 8 * small_cap + 4 * total
    return {"small_support_cap": small_cap, "endpoint_sum_cap": total,
            "quotient_support_cap": quotient_cap, "edge_support_cap": edge_cap,
            "edge_incidence_lower": 795, "old_incidence_upper": old_upper,
            "coordinate_incidence_upper": upper, "old_margin": 795 - old_upper,
            "margin": 795 - upper, "excluded": 795 > upper}


def original_survivor(weights):
    """Pinned BK/BK7 filters at b=6, t=4; finite historical inclusion only."""
    require(6 <= len(weights) <= 10 and tuple(sorted(weights)) == tuple(weights)
            and all(type(w) is int and w in CAP for w in weights),
            "invalid historical weight multiset")
    if sum(w - 2 for w in weights) >= 36:
        return False
    for level in range(1, 7):
        retained = weights[:len(weights) - (6 - level)]
        global_cap = sum(CAP[w] for w in retained)
        target_cap = sum(TARGET_CAP[w] for w in retained)
        if level == 1 and target_cap < 53 and global_cap < 73:
            return False
        if level == 2 and target_cap < 78 and global_cap < 82:
            return False
        if level >= 3 and global_cap < DISTANCE[level]:
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


def prior_cover_audit():
    """Check all 210 weight-certified quotient bases and their two-flat covers."""
    bases = {}
    for indices in combinations(range(10), 4):
        basis = tuple(TARGET[i] for i in indices)
        if basis in bases or sum(CAP[w] for w in basis) >= 53:
            continue
        complement = tuple(w for i, w in enumerate(TARGET) if i not in indices)
        minimum = sum(CAP[w] for w in basis)
        for assignment in product(range(3), repeat=4):
            if any(sum(w for w, a in zip(basis, assignment, strict=True) if a == k)
                   > 6 for k in (0, 1)):
                continue
            cuts = sum(CAP[w] for w, a in zip(basis, assignment, strict=True) if a == 2)
            minimum = min(minimum, cuts)
        bases[basis] = {"basis": list(basis), "complement": list(complement),
                        "support_cap": sum(CAP[w] for w in basis),
                        "minimum_two_flat_cuts": minimum,
                        "rank_four_anchor": any(w <= 4 for w in complement)}
    rows = [bases[basis] for basis in sorted(bases)]
    require(len(rows) == 1
            and all(row["minimum_two_flat_cuts"] == 16
                    and not row["rank_four_anchor"] for row in rows),
            "prior weight-cover audit")
    return rows


def application():
    survivors = []
    examined = 0
    for size in range(6, 11):
        for weights in combinations_with_replacement(range(2, 8), size):
            examined += 1
            if original_survivor(weights):
                survivors.append(weights)
    require(len(survivors) == 69 and TARGET in survivors, "historical inclusion")
    retained_intersection = intersection_after_deletion(10, 6, 1)
    require(retained_intersection == 5 and len(RETAINED) == 9,
            "nine-piece intersection hypothesis")
    bound = coordinate_bound(3 * CAP[4], [CAP[6]] * 6)
    require(bound["excluded"] and bound["margin"] == 11
            and bound["old_margin"] == -21, "coordinate-bound gain")
    return {"historical_cell": [6, 4], "multisets_examined": examined,
            "historical_survivors": [list(w) for w in survivors],
            "target": list(TARGET), "retained_weights": list(RETAINED),
            "original_intersection_lower": 6, "removed_pieces": 1,
            "retained_intersection_lower": retained_intersection,
            "retained_quotient_dimension": 4, "new_profile_exclusions": 1,
            "concurrent_PR3195_profile_counted_as_new": False,
            "prior_cover_audit": prior_cover_audit(), **bound}
