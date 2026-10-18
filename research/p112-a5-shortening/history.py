"""Bind one actual TWOSIDE profile and audit named earlier sufficient covers.

The filter is a separate transcription of DreamingOfClouds/PR3154 bk2b.py.
It does not certify a complete current residue or nonexistence of other proofs.
"""

from itertools import combinations, combinations_with_replacement, product

PROFILE = (2, 5, 5) + (6,) * 6 + (7,)
CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}


def historical_profiles():
    distance = (0, 53, 78, 92, 100, 106, 109)
    rows, examined = [], 0
    for size in range(6, 11):
        for weights in combinations_with_replacement(range(2, 8), size):
            examined += 1
            if sum(w - 2 for w in weights) >= 36:
                continue
            feasible = True
            for level in range(1, 7):
                prefix = weights[: size - 6 + level]
                total = sum(CAP[w] for w in prefix)
                target = sum(32 if w == 7 else CAP[w] for w in prefix)
                if (
                    (level == 1 and target < 53 and total < 73)
                    or (level == 2 and target < 78 and total < 82)
                    or (level >= 3 and total < distance[level])
                ):
                    feasible = False
                    break
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
                    for assignment in product(range(2), repeat=len(basis))
                )
            if feasible and not killed:
                rows.append(weights)
    if len(rows) != 69 or PROFILE not in rows:
        raise ValueError("historical (6,4) profile binding changed")
    return {
        "examined": examined,
        "cell": [6, 4],
        "profiles": rows,
        "target": PROFILE,
        "excess": sum(w - 2 for w in PROFILE),
        "strict_excess_threshold": 36,
    }


def weight_only_covers():
    rows = []
    for basis in sorted(set(combinations(PROFILE, 4))):
        if sum(CAP[w] for w in basis) >= 53:
            continue
        rest = list(PROFILE)
        for w in basis:
            rest.remove(w)
        budgets = {}
        for dimension in (6, 7):
            cuts = []
            for assignment in product(range(3), repeat=4):
                if all(
                    sum(w for w, g in zip(basis, assignment, strict=True) if g == group)
                    <= dimension
                    for group in (0, 1)
                ):
                    cuts.append(
                        sum(
                            CAP[w]
                            for w, g in zip(basis, assignment, strict=True)
                            if g == 2
                        )
                    )
            budgets[str(dimension)] = min(cuts)
        rows.append(
            {
                "basis": basis,
                "nonbasis": rest,
                "small_support_cap": sum(CAP[w] for w in basis),
                "minimum_paid_cut_budgets": budgets,
            }
        )
    if not rows:
        raise ValueError("no weight-certified quotient basis")
    return rows
