"""Recount the pinned TWOSIDE (5,3) necessary filters, without importing them."""

from itertools import combinations_with_replacement

CAP = (0, 1, 2, 4, 8, 12, 20, 36)
SMALL_TARGET_CAP = (0, 1, 2, 4, 8, 12, 20, 32)
DISTANCE = (0, 53, 78, 92, 100, 106, 109, 111, 112)
EXPECTED = (
    (2, 6, 6, 6, 6, 6, 6, 6),
    (2, 6, 6, 6, 6, 6, 6, 7),
    (3, 6, 6, 6, 6, 6, 6, 6),
    (4, 5, 6, 6, 6, 6, 6, 6),
)
BASES = ((2, 6, 6), (2, 6, 6), (3, 6, 6), (4, 6, 6))


def size_feasible(weights, b):
    """The smallest rho+level pieces must meet each necessary support bound."""
    for level in range(1, b + 1):
        retained = weights[: len(weights) - b + level]
        global_cap = sum(CAP[w] for w in retained)
        target_cap = sum(SMALL_TARGET_CAP[w] for w in retained)
        if level == 1 and target_cap < 53 and global_cap < 73:
            return False
        if level == 2 and target_cap < 78 and global_cap < 82:
            return False
        if level >= 3 and global_cap < DISTANCE[level]:
            return False
    return True


def two_bins(weights):
    total = sum(weights)
    return any(
        total - sum(w for i, w in enumerate(weights) if code >> i & 1) <= 6
        and sum(w for i, w in enumerate(weights) if code >> i & 1) <= 6
        for code in range(1 << len(weights))
    )


def remaining_shapes():
    result, examined = [], 0
    for n in range(5, 9):
        for weights in combinations_with_replacement(range(2, 8), n):
            examined += 1
            if sum(w - 2 for w in weights) >= 30 or not size_feasible(weights, 5):
                continue
            smallest = weights[: n - 5]
            if sum(CAP[w] for w in smallest) < 53:
                if sum(smallest) <= 7 or two_bins(smallest):
                    continue
            result.append(weights)
    if tuple(result) != EXPECTED:
        raise ValueError("the pinned four-shape boundary changed")
    certificates = []
    for weights, basis in zip(result, BASES, strict=True):
        complement = list(weights)
        for w in basis:
            complement.remove(w)
        support_cap = sum(CAP[w] for w in basis)
        extra_lines = CAP[basis[0]]
        seven = complement.count(7)
        if (
            support_cap >= 53
            or extra_lines > 8
            or len(complement) != 5
            or 3 + seven >= 5
        ):
            raise ValueError("invalid mixed-rank exclusion")
        certificates.append(
            {
                "weights": weights,
                "quotient_basis": basis,
                "support_cap": support_cap,
                "extra_lines": extra_lines,
                "nonbasis_sevens": seven,
                "direction_bound": 3 + seven,
            }
        )
    return {"examined": examined, "old_survivors": certificates, "new_survivors": 0}
