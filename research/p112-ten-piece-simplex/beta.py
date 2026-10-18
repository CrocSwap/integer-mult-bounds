"""Ten-piece applications and a bounded audit of earlier weight-cover rules.

The filters follow DreamingOfClouds's PR3154 TWOSIDE. The incidence argument
extends Nick Petalas's PR3164; earlier cover theorems are PR3161/3162/3167.
Apache-2.0. Exact source heads are recorded in SOURCES.json.
"""

from itertools import combinations, combinations_with_replacement, product

from geometry import require

CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
TARGET_CAP = {**CAP, 7: 32}
DISTANCE = (0, 53, 78, 92, 100, 106)
NEW_SHAPES = ((2, 2, 4, 5, 6, 6, 6, 6, 6, 6),
              (2, 2, 5, 5, 5, 6, 6, 6, 6, 6),
              (2, 3, 4, 4, 6, 6, 6, 6, 6, 6),
              (2, 3, 4, 5, 5, 6, 6, 6, 6, 6),
              (2, 4, 4, 4, 5, 6, 6, 6, 6, 6))
ANCHOR_CONTROL = (3, 3, 3, 4, 6, 6, 6, 6, 6, 6)


def validate_weights(weights):
    require(5 <= len(weights) <= 10
            and all(type(w) is int and w in CAP for w in weights)
            and tuple(sorted(weights)) == tuple(weights), "invalid weight multiset")


def two_flat_cuts(weights):
    """Minimum cardinality allowance outside two bins of dimension six."""
    require(len(weights) <= 5 and all(type(w) is int and w in CAP for w in weights),
            "cover input")
    best = sum(CAP[w] for w in weights)
    for assignment in product(range(3), repeat=len(weights)):
        if any(sum(w for w, a in zip(weights, assignment, strict=True) if a == k) > 6
               for k in (0, 1)):
            continue
        cuts = sum(CAP[w] for w, a in zip(weights, assignment, strict=True) if a == 2)
        best = min(best, cuts)
    return best


def original_survivor(weights):
    """Exactly the pinned BK/BK7 necessary filters for b=5, t<=5."""
    validate_weights(weights)
    if sum(w - 2 for w in weights) >= 30:
        return False
    for level in range(1, 6):
        retained = weights[:len(weights) - (5 - level)]
        global_cap = sum(CAP[w] for w in retained)
        target_cap = sum(TARGET_CAP[w] for w in retained)
        if level == 1 and target_cap < 53 and global_cap < 73:
            return False
        if level == 2 and target_cap < 78 and global_cap < 82:
            return False
        if level >= 3 and global_cap < DISTANCE[level]:
            return False
    basis = weights[:len(weights) - 5]
    if sum(CAP[w] for w in basis) < 53:
        if sum(basis) <= 7 or two_flat_cuts(basis) == 0:
            return False
    return True


def prior_cover_audit(weights):
    """Search every quotient basis, including bases other than the smallest."""
    validate_weights(weights)
    rho = len(weights) - 5
    best, best_anchor = 113, 113
    exclusions = set()
    bases = set()
    for indices in combinations(range(len(weights)), rho):
        basis = tuple(weights[i] for i in indices)
        if basis in bases or sum(CAP[w] for w in basis) >= 53:
            continue
        bases.add(basis)
        complement = tuple(w for i, w in enumerate(weights) if i not in indices)
        cuts = two_flat_cuts(basis)
        best = min(best, cuts)
        sevens = complement.count(7)
        if cuts <= 8 and 3 + sevens < 5:
            exclusions.add("PR3161:p8")
        if cuts <= 10 and 4 + sevens < 5:
            exclusions.add("PR3162:p10")
        if any(w <= 4 for w in complement):
            best_anchor = min(best_anchor, cuts)
            if cuts <= 12 and 3 + sevens < 5:
                exclusions.add("PR3167:H4-p12")
    return {"minimum_cuts": None if best == 113 else best,
            "minimum_anchor_cuts": None if best_anchor == 113 else best_anchor,
            "quotient_weight_bases": len(bases), "prior_exclusions": sorted(exclusions)}


def incidence(small_cap, large_caps):
    require(type(small_cap) is int and 0 <= small_cap <= 112
            and len(large_caps) == 6
            and all(type(n) is int and 0 <= n <= 112 for n in large_caps),
            "invalid support bounds")
    ordered = sorted(large_caps, reverse=True)
    require(small_cap + ordered[0] < 53, "quotient independence is uncertified")
    require(small_cap + sum(ordered[:2]) < 70, "root-edge hypothesis is uncertified")
    large_sum = sum(large_caps)
    original_upper = 9 * small_cap + 5 * large_sum
    coordinate_upper = 112 + 8 * small_cap + 4 * large_sum
    upper = min(original_upper, coordinate_upper)
    return {"small_support_cap": small_cap, "large_support_sum_cap": sum(large_caps),
            "quotient_support_cap": small_cap + ordered[0],
            "edge_support_cap": small_cap + sum(ordered[:2]),
            "edge_incidence_lower": 15 * 53,
            "original_incidence_upper": original_upper,
            "coordinate_incidence_upper": coordinate_upper,
            "original_margin": 15 * 53 - original_upper,
            "margin": 15 * 53 - upper, "excluded": 15 * 53 > upper}


def ten_piece_obstruction(weights):
    validate_weights(weights)
    require(len(weights) == 10 and max(weights) <= 6, "ten bounded pieces required")
    return {"weights": list(weights), "small_weights": list(weights[:4]),
            "large_weights": list(weights[4:]),
            **incidence(sum(CAP[w] for w in weights[:4]),
                        [CAP[w] for w in weights[4:]])}


def beta_receipt():
    examined, survivors = 0, []
    for size in range(5, 11):
        for weights in combinations_with_replacement(range(2, 8), size):
            examined += 1
            if original_survivor(weights):
                survivors.append(weights)
    require(len(survivors) == 38, "pinned (5,5) survivor count")
    applications = []
    for shape in NEW_SHAPES:
        require(shape in survivors, "new shape is absent from the original residue")
        audit = prior_cover_audit(shape)
        require(not audit["prior_exclusions"], "proposed exclusion is already covered")
        row = {**ten_piece_obstruction(shape), "prior_cover_audit": audit}
        require(row["excluded"], "new exclusion margin")
        applications.append(row)
    overlap = prior_cover_audit(ANCHOR_CONTROL)
    require("PR3167:H4-p12" in overlap["prior_exclusions"], "missed anchor overlap")
    return {"multisets_examined": examined, "pinned_survivors": [list(w) for w in survivors],
            "new_exclusions": applications,
            "overlap_control": {"weights": list(ANCHOR_CONTROL), **overlap}}
