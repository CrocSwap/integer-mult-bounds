"""Exact coverage of one historical cell by six fixed published contracts."""

from itertools import combinations, combinations_with_replacement

from binding import require

CAP = (0, 0, 2, 4, 8, 12, 20, 36)
DISTANCE = (0, 53, 78, 92, 100, 106, 109)
RULES = (
    "PR3262-three-rank6-cut29",
    "PR3205-six-support20-cut30",
    "PR3260-ranks556-cut37",
    "PR3186-profile34-six8",
    "PR3192-profile5-six8",
    "PR3253-seven-flat-common5",
)


def validate(weights):
    require(isinstance(weights, tuple) and 6 <= len(weights) <= 10, "cell piece count")
    require(all(type(w) is int and 2 <= w <= 7 for w in weights), "piece weights")
    require(tuple(sorted(weights)) == weights, "unsorted weights")


def historical(weights):
    """Direct-weight BK/BK7 transcription, independent of the frozen filter."""
    validate(weights)
    if sum(w - 2 for w in weights) >= 36:
        return False
    for level in range(1, 7):
        kept = weights[: len(weights) - 6 + level]
        total = sum(CAP[w] for w in kept)
        target = sum(32 if w == 7 else CAP[w] for w in kept)
        if level == 1 and target < 53 and total < 73:
            return False
        if level == 2 and target < 78 and total < 82:
            return False
        if level >= 3 and total < DISTANCE[level]:
            return False
    small = weights[: len(weights) - 6]
    if sum(CAP[w] for w in small) >= 53:
        return True
    if sum(small) <= 7:
        return False
    total_weight = sum(small)
    return not any(
        total_weight - 6 <= sum(subset) <= 6
        for length in range(len(small) + 1)
        for subset in combinations(small, length)
    )


def universe():
    return tuple(
        weights
        for length in range(6, 11)
        for weights in combinations_with_replacement(range(2, 8), length)
    )


def partition_receipt(weights, small, endpoints, code_dimension):
    used = set(small) | set(endpoints)
    deleted = tuple(i for i in range(len(weights)) if i not in used)
    require(len(used) == len(small) + len(endpoints), "overlapping roles")
    require(6 - len(deleted) == code_dimension, "lost code dimensions")
    return {
        "small_indices": small,
        "endpoint_indices": endpoints,
        "deleted_indices": deleted,
        "retained_code_dimension": code_dimension,
        "common_support_cap": sum(CAP[weights[i]] for i in small),
        "endpoint_weight_caps": tuple(weights[i] for i in endpoints),
    }


def shortening(weights, endpoint_count, limits, cut_limit):
    """Check every role assignment; retain one witness and the exact count."""
    delete_count = 7 - endpoint_count
    small_count = len(weights) - 7
    if small_count < 0:
        return {"valid_partitions": 0, "witness": None, "minimum_admissible_cut": None}
    count, witness, minimum = 0, None, None
    for endpoints in combinations(range(len(weights)), endpoint_count):
        ranks = tuple(weights[i] for i in endpoints)
        if any(rank > limit for rank, limit in zip(ranks, limits, strict=True)):
            continue
        available = tuple(i for i in range(len(weights)) if i not in endpoints)
        for small in combinations(available, small_count):
            cut = sum(CAP[weights[i]] for i in small)
            minimum = cut if minimum is None else min(minimum, cut)
            if cut > cut_limit:
                continue
            count += 1
            if witness is None:
                witness = partition_receipt(weights, small, endpoints, 6 - delete_count)
    return {
        "valid_partitions": count,
        "witness": witness,
        "minimum_admissible_cut": minimum,
    }


def literal(weights, target):
    applies = len(weights) == len(target) and all(
        w <= bound for w, bound in zip(weights, target, strict=True)
    )
    return {"applies": applies, "target_weights": target, "required_code_dimension": 6}


def common_five(weights):
    small_count = len(weights) - 7
    if small_count < 0:
        return {"valid_partitions": 0, "witness": None}
    count, witness = 0, None
    for small in combinations(range(len(weights)), small_count):
        cut = sum(CAP[weights[i]] for i in small)
        if cut > 5:
            continue
        endpoints = tuple(i for i in range(len(weights)) if i not in small)
        for anchor in endpoints:
            if cut + CAP[weights[anchor]] >= 53:
                continue
            count += 1
            if witness is None:
                witness = partition_receipt(weights, small, endpoints, 6)
                witness.update(
                    anchor_index=anchor,
                    independent_directions=6,
                    projective_direction_limit=2,
                    quotient_basis_support_cap=cut + CAP[weights[anchor]],
                )
    return {"valid_partitions": count, "witness": witness}


def classify(weights):
    validate(weights)
    attempts = (
        shortening(weights, 3, (6, 6, 6), 29),
        shortening(weights, 6, (6,) * 6, 30),
        shortening(weights, 3, (5, 5, 6), 37),
        literal(weights, (3, 4) + (6,) * 8),
        literal(weights, (5,) + (6,) * 8),
        common_five(weights),
    )
    certificates = {
        name: attempt
        for name, attempt in zip(RULES, attempts, strict=True)
        if attempt.get("applies", attempt.get("valid_partitions", 0))
    }
    return {
        "weights": weights,
        "attempts": dict(zip(RULES, attempts, strict=True)),
        "certificates": certificates,
        "primary": next(iter(certificates), None),
    }
