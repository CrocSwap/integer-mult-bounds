#!/usr/bin/env python3
"""Exact, stdlib-only necessary-condition audit of T24 replica separability.

Does NOT prove or rule out a physical T24 construction. Derived from the
PR #890 fixed-U8 width/capacity/signed-price relaxation.
"""
from itertools import product

WIDTHS = (4, 5, 7, 8, 9)
PRICES = (-1, -20, -8, -2, 4)
CAP_BONUSES = {8: 2, 16: 4, 32: 8, 48: -13}
BINS_PER_REPLICA = {8: 672, 16: 448, 32: 448, 48: 448}
HELPERS_PER_CALL = (80, 32, 54, 122, 216)
CALLS_PER_REPLICA = 9
TOTAL_BINS_PER_REPLICA = sum(BINS_PER_REPLICA.values())
CAPACITY_PER_REPLICA = sum(c * k for c, k in BINS_PER_REPLICA.items())
USED_PER_REPLICA = CALLS_PER_REPLICA * sum(w * k for w, k in zip(WIDTHS, HELPERS_PER_CALL))
MASS_PER_REPLICA = CAPACITY_PER_REPLICA - USED_PER_REPLICA
SCORE_PER_REPLICA = (
    sum(CAP_BONUSES[c] * k for c, k in BINS_PER_REPLICA.items())
    + CALLS_PER_REPLICA * sum(p * k for p, k in zip(PRICES, HELPERS_PER_CALL))
)


def signed_dual_table():
    """Independently enumerate every possible local whole-helper bin inventory."""
    result = {}
    count = 0
    for cap, bonus in CAP_BONUSES.items():
        for counts in product(*(range(cap // w + 1) for w in WIDTHS)):
            idle = cap - sum(w * k for w, k in zip(WIDTHS, counts))
            if idle < 0:
                continue
            count += 1
            score = bonus + sum(p * k for p, k in zip(PRICES, counts))
            result[idle] = max(result.get(idle, -10**9), score)
    return result, count


def total_credit(profile, v):
    return sum(v[r] * count for r, count in profile.items())


def profile_mass(profile):
    return sum(r * count for r, count in profile.items())


def split_candidates(profile, T, v):
    """Enumerate necessary-condition closed splits, not owner schedules."""
    residues = {r: k for r, k in profile.items() if r not in (0, 48)}
    choices = list(residues.items())
    assert MASS_PER_REPLICA * T == profile_mass(profile)
    assert sum(profile.values()) <= TOTAL_BINS_PER_REPLICA * T
    results = []
    for g in range(1, T):
        for subset in product(*(range(n + 1) for _, n in choices)):
            selected = {r: a for (r, _), a in zip(choices, subset) if a}
            m = profile_mass(selected)
            if (MASS_PER_REPLICA * g - m) % 48:
                continue
            n48 = (MASS_PER_REPLICA * g - m) // 48
            n0 = TOTAL_BINS_PER_REPLICA * g - n48 - sum(selected.values())
            if n48 < 0 or n48 > profile.get(48, 0) or n0 < 0:
                continue
            c = total_credit(selected, v)
            complementary = {r: residues[r] - selected.get(r, 0) for r in residues}
            complement_credit = total_credit(complementary, v)
            results.append({
                "g": g, "selected": selected,
                "credit_left": c, "credit_right": complement_credit,
                "passes_left": c >= 150 * g,
                "passes_right": complement_credit >= 150 * (T - g),
                "closed": c >= 150 * g and complement_credit >= 150 * (T - g)
            })
    return results


def main():
    U, options = signed_dual_table()
    assert options == 1163, options
    assert CAPACITY_PER_REPLICA == 48384
    assert USED_PER_REPLICA == 34002
    assert MASS_PER_REPLICA == 14382
    assert SCORE_PER_REPLICA == -3892
    coefficient = 48 * SCORE_PER_REPLICA + 13 * MASS_PER_REPLICA
    assert coefficient == 150
    v = {r: 48 * u + 13 * r for r, u in U.items()}
    assert {r: U[r] for r in (0, 1, 3, 44, 48)} == {
        0: 0, 1: 19, 3: 7, 44: -14, 48: -13
    }
    assert {r: v[r] for r in (0, 1, 3, 44, 48)} == {
        0: 0, 1: 925, 3: 375, 44: -100, 48: 0
    }
    profile24 = {48: 7190, 44: 1, 1: 4}
    assert profile_mass(profile24) == MASS_PER_REPLICA * 24
    assert total_credit(profile24, v) == 150 * 24
    candidates24 = split_candidates(profile24, 24, v)
    assert {(a["g"], a["selected"].get(1, 0), a["selected"].get(44, 0))
            for a in candidates24} == {
                (8, 0, 0), (8, 4, 1), (16, 0, 0), (16, 4, 1)
            }
    assert not any(a["closed"] for a in candidates24)
    print("PASS T24: no proper independently closed replica partition")
    print("T24 mass per replica:", MASS_PER_REPLICA, "; signed dual target:", coefficient)
    print("T24 modulo-compatible candidates:", len(candidates24))
    for a in candidates24:
        print("  g={g:2d} residuals={selected} credit=({credit_left},{credit_right}) "
              "valid=({passes_left},{passes_right})".format(**a))
    profile21 = {48: 6292, 3: 1, 1: 3}
    assert profile_mass(profile21) == MASS_PER_REPLICA * 21
    assert total_credit(profile21, v) == 150 * 21
    assert not any(a["closed"] for a in split_candidates(profile21, 21, v))
    print("PASS T21 control: the same obstruction permits cross-replica edits")
    alternative = {48: 7189, 44: 2, 3: 1, 2: 1, 1: 3}
    assert profile_mass(alternative) == MASS_PER_REPLICA * 24
    assert total_credit(alternative, v) == 150 * 24
    alt_splits = [a for a in split_candidates(alternative, 24, v) if a["closed"]]
    assert any(a["g"] in (8, 16) for a in alt_splits)
    print("PASS positive control: modified T24 rank profile can pass both group relaxations")
    damaged = {48: 7191, 44: 1, 1: 4}
    try:
        split_candidates(damaged, 24, v)
    except AssertionError:
        print("PASS negative control: corrupted rank mass rejected")
    else:
        raise RuntimeError("Corrupt rank mass was not detected")
    print("SCOPE: necessary aggregate constraints; NOT an owner map, prefix repair, or new kappa.")


if __name__ == "__main__":
    main()
