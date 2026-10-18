"""Weight-certified quotient covers for the pinned TWOSIDE (5,4) boundary."""

from itertools import combinations, combinations_with_replacement, product

CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
TARGET_CAP = CAP | {7: 32}
DISTANCE = (0, 53, 78, 92, 100, 106, 109, 111, 112)
NEW_SHAPE = (2, 4, 5, 6, 6, 6, 6, 6, 6)
REMAINDER = ((2, 5, 5, 5, 6, 6, 6, 6, 6), (3, 4, 4, 6, 6, 6, 6, 6, 6))


def validate(weights):
    if not 5 <= len(weights) <= 9 or any(
        type(w) is not int or w not in CAP for w in weights
    ):
        raise ValueError("weights must be five to nine integers in 2..7")
    if tuple(sorted(weights)) != tuple(weights):
        raise ValueError("weights must be sorted")


def size_feasible(weights):
    for level in range(1, 6):
        kept = weights[: len(weights) - 5 + level]
        global_cap = sum(CAP[w] for w in kept)
        target_cap = sum(TARGET_CAP[w] for w in kept)
        if level == 1 and target_cap < 53 and global_cap < 73:
            return False
        if level == 2 and target_cap < 78 and global_cap < 82:
            return False
        if level >= 3 and global_cap < DISTANCE[level]:
            return False
    return True


def cover(basis, budget):
    """Two bins of total label dimension six and one support-cardinality bin."""
    for assignment in product(range(3), repeat=len(basis)):
        bins = tuple(
            tuple(w for w, a in zip(basis, assignment, strict=True) if a == j)
            for j in range(3)
        )
        if (
            sum(bins[0]) <= 6
            and sum(bins[1]) <= 6
            and sum(CAP[w] for w in bins[2]) <= budget
        ):
            return bins
    return None


def certificate(weights, budget, span_bound):
    validate(weights)
    if (
        type(budget) is not int
        or not 0 <= budget <= 144
        or type(span_bound) is not int
        or not 0 <= span_bound <= 8
    ):
        raise ValueError("invalid cover budget or span bound")
    rho = len(weights) - 5
    for basis in sorted(set(combinations(weights, rho))):
        support_cap = sum(CAP[w] for w in basis)
        bins = cover(basis, budget)
        if support_cap >= 53 or bins is None:
            continue
        complement = list(weights)
        for w in basis:
            complement.remove(w)
        upper = span_bound + complement.count(7)
        if upper < 5:
            return {
                "weights": weights,
                "quotient_basis": basis,
                "support_cap": support_cap,
                "bins": bins,
                "deleted_lines": sum(CAP[w] for w in bins[2]),
                "nonbasis_sevens": complement.count(7),
                "direction_bound": upper,
            }
    return None


def pinned_survivors():
    result = []
    examined = 0
    for n in range(5, 10):
        for weights in combinations_with_replacement(range(2, 8), n):
            examined += 1
            if sum(w - 2 for w in weights) >= 30 or not size_feasible(weights):
                continue
            small = weights[: n - 5]
            packed = any(
                max(
                    sum(w for w, a in zip(small, assignment, strict=True) if a == j)
                    for j in (0, 1)
                )
                <= 6
                for assignment in product((0, 1), repeat=len(small))
            )
            if sum(CAP[w] for w in small) < 53 and (sum(small) <= 7 or packed):
                continue
            result.append(weights)
    if examined != 4795 or len(result) != 15:
        raise ValueError("pinned TWOSIDE boundary changed")
    return result


def reduction():
    old = pinned_survivors()
    earlier, new, remaining = [], [], []
    for weights in old:
        before = certificate(weights, 8, 3)
        after = certificate(weights, 10, 4)
        if before is not None:
            earlier.append(before)
        elif after is not None:
            new.append(after)
        else:
            remaining.append(weights)
    if (
        tuple(row["weights"] for row in new) != (NEW_SHAPE,)
        or tuple(remaining) != REMAINDER
        or len(earlier) != 12
    ):
        raise ValueError("unexpected beta residue")
    minima = [
        next(p for p in range(145) if certificate(w, p, 0) is not None)
        for w in (NEW_SHAPE, *REMAINDER)
    ]
    if minima != [10, 14, 12]:
        raise ValueError("minimum weight-certified cover changed")
    return {
        "examined": 4795,
        "pinned_survivors": old,
        "earlier_p8_exclusions": earlier,
        "new_p10_exclusions": new,
        "remaining": remaining,
        "minimum_cover_budgets": minima,
    }
