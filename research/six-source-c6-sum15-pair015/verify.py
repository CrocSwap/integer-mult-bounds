#!/usr/bin/env python3
"""Weight-3 sums at (0, 15), and one shape against the six families.

The written argument is in README.md. This program enumerates every length-15
count vector and every legal three-letter bridge from the named shape to the
slot (18, 21). It does not search words and it does not call a SAT solver.
"""

import itertools
from math import comb

K = 6
CAP = 6
LENGTH = 15
GAP = 3
ALLOWED = (0, 1, 6, 7, 12)
ALLOWED_SET = set(ALLOWED)
MASK_BIT = {0: 0, 1: 1, 6: 0, 7: 1, 12: 0}
SHAPE = (6, 6, 1, 1, 1, 0)
SORTED_SHAPE = tuple(sorted(SHAPE))

# Recorded q_18 multisets of the six separation-3 families in PR #7029.
# T2 and T3 share a multiset, as do T4 and T5.
FAMILY_Q18 = {
    "T1": (3, 3, 3, 3, 3, 3),
    "T2": (0, 3, 3, 3, 3, 6),
    "T3": (0, 3, 3, 3, 3, 6),
    "T4": (0, 0, 3, 3, 6, 6),
    "T5": (0, 0, 3, 3, 6, 6),
    "T6": (0, 0, 0, 6, 6, 6),
}

# Separation-3 witness from the c=6 centre note. Its (18, 21) sum is weight 3
# and its q_15 is not the shape under test.
SEPARATION3_WORD = "333333444444555555012000001111122222"
# Off-diagonal witness. Weight 3 at (0, 9), not at (18, 21).
PAIR09_WORD = "333333012000001111122222444444555555"
# Same counts as the separation-3 prefix through length 15. Not weight 3,
# and it does extend.
LIVE_PREFIX = (0, 0, 0, 6, 6, 3)


def fail(message):
    raise SystemExit("FAIL: " + message)


def mask_weight(values):
    bits = 0
    for value in values:
        if value not in ALLOWED_SET:
            return None
        bits += MASK_BIT[value]
    return bits


def weight3(values):
    return mask_weight(values) == 3


def bounded_count(total, cap=CAP, slots=K):
    """Inclusion-exclusion count of {0,...,cap}^slots summing to total."""
    found = 0
    for excised in range(total // (cap + 1) + 1):
        rest = total - excised * (cap + 1)
        sign = 1 if excised % 2 == 0 else -1
        found += sign * comb(slots, excised) * comb(rest + slots - 1, slots - 1)
    return found


def compositions(total, caps):
    """Every tuple with 0 <= entry <= caps[i] and coordinate sum total."""

    def rec(index, remain):
        last = index == len(caps) - 1
        if last:
            if 0 <= remain <= caps[index]:
                yield (remain,)
            return
        for value in range(min(caps[index], remain) + 1):
            for tail in rec(index + 1, remain - value):
                yield (value,) + tail

    yield from rec(0, total)


def bridges(prefix):
    caps = tuple(min(GAP, CAP - prefix[j]) for j in range(K))
    if any(cap < 0 for cap in caps):
        return
    yield from compositions(GAP, caps)


def add(left, right):
    return tuple(left[j] + right[j] for j in range(K))


def separation_sum(q18, delta):
    return tuple(2 * q18[j] + delta[j] for j in range(K))


def extension_census(prefix):
    trials = 0
    hits = 0
    with_twelve = 0
    for epsilon in bridges(prefix):
        q18 = add(prefix, epsilon)
        for delta in bridges(q18):
            trials += 1
            summed = separation_sum(q18, delta)
            if weight3(summed):
                hits += 1
                if 12 in summed:
                    with_twelve += 1
    return trials, hits, with_twelve


def prefix_counts(word, length):
    counts = [0] * K
    for source in word[:length]:
        counts[int(source)] += 1
    return tuple(counts)


def dominates(shape, target):
    """True when some alignment has shape <= target <= shape + (3,3,3,3,3,3)."""
    for perm in set(itertools.permutations(target)):
        if all(shape[j] <= perm[j] <= shape[j] + GAP for j in range(K)):
            return True
    return False


def family_solutions():
    """Nonnegative solutions of the recorded three-letter budget equations."""
    found = []
    for n01, n31, n00, n30, n60 in itertools.product(range(K + 1), repeat=5):
        if n01 + n31 != 3:
            continue
        if n00 + n30 + n60 != 3:
            continue
        if 3 * n30 + 3 * n31 + 6 * n60 != LENGTH + GAP:
            continue
        coords = (
            (0,) * n01
            + (3,) * n31
            + (0,) * n00
            + (3,) * n30
            + (6,) * n60
        )
        if len(coords) != K:
            fail("family coordinate count drifted")
        found.append(
            {
                "counts": (n01, n31, n00, n30, n60),
                "q18": tuple(sorted(coords)),
            }
        )
    return found


def main():
    controls = 0

    if not weight3(SHAPE):
        fail("named shape is not a weight-3 mask")
    controls += 1
    if weight3((2, 1, 1, 6, 6, 0)):
        fail("a coordinate equal to 2 was accepted")
    controls += 1
    for abstract in ((12, 1, 1, 1, 0, 0), (7, 7, 1, 0, 0, 0), (7, 6, 1, 1, 0, 0)):
        if not weight3(abstract):
            fail(f"abstract residue shape rejected: {abstract}")
        if max(abstract) <= CAP:
            fail(f"abstract residue shape is a legal prefix coordinate: {abstract}")
    controls += 1

    closed = bounded_count(LENGTH)
    vectors = 0
    weight3_vectors = []
    for counts in itertools.product(range(CAP + 1), repeat=K):
        if sum(counts) != LENGTH:
            continue
        vectors += 1
        if weight3(counts):
            weight3_vectors.append(counts)
    if vectors != closed or vectors != 7872:
        fail(f"length-15 census changed: enumerated={vectors} closed={closed}")
    controls += 1
    if len(weight3_vectors) != 60:
        fail(f"weight-3 prefix count changed: {len(weight3_vectors)}")
    controls += 1
    if any(tuple(sorted(item)) != SORTED_SHAPE for item in weight3_vectors):
        fail("a weight-3 length-15 vector is outside the named shape")
    controls += 1
    orbit = set(itertools.permutations(SHAPE))
    if orbit != set(weight3_vectors) or len(orbit) != 60:
        fail(f"orbit mismatch: {len(orbit)}")
    controls += 1

    solutions = family_solutions()
    got = sorted(item["counts"] for item in solutions)
    expected_counts = [
        (0, 3, 0, 3, 0),
        (0, 3, 1, 1, 1),
        (1, 2, 0, 2, 1),
        (1, 2, 1, 0, 2),
        (2, 1, 0, 1, 2),
        (3, 0, 0, 0, 3),
    ]
    if got != expected_counts:
        fail(f"family equations changed: {got}")
    controls += 1
    by_counts = {item["counts"]: item["q18"] for item in solutions}
    if by_counts != {
        (0, 3, 0, 3, 0): FAMILY_Q18["T1"],
        (0, 3, 1, 1, 1): FAMILY_Q18["T2"],
        (1, 2, 0, 2, 1): FAMILY_Q18["T3"],
        (1, 2, 1, 0, 2): FAMILY_Q18["T4"],
        (2, 1, 0, 1, 2): FAMILY_Q18["T5"],
        (3, 0, 0, 0, 3): FAMILY_Q18["T6"],
    }:
        fail(f"q_18 multisets changed: {by_counts}")
    controls += 1

    family_hits = 0
    for name, target in FAMILY_Q18.items():
        if sum(target) != 18 or len(target) != K:
            fail(f"{name} is not a length-18 count vector")
        if dominates(SHAPE, target):
            family_hits += 1
    if family_hits != 0:
        fail(f"named shape meets a family multiset: {family_hits}")
    controls += 1

    # Two coordinates are already 6, so the three-letter bridge is supported
    # on the other four coordinates, each at most 3. No part can reach 4
    # inside a sum of 3, and the number of bridges is C(3+4-1, 3) = 20.
    shape_epsilons = sum(1 for _ in bridges(SHAPE))
    if shape_epsilons != 20:
        fail(f"first-gap bridge count changed: {shape_epsilons}")
    controls += 1
    trials, hits, with_twelve = extension_census(SHAPE)
    # Every permutation has the same bridge count, so the orbit total is
    # 60 times this representative.
    if (trials, hits, with_twelve) != (397, 0, 0):
        fail(
            "representative extension census changed: "
            f"trials={trials} hits={hits} with_twelve={with_twelve}"
        )
    controls += 1
    orbit_trials = 0
    orbit_hits = 0
    for counts in orbit:
        item_trials, item_hits, _ = extension_census(counts)
        orbit_trials += item_trials
        orbit_hits += item_hits
    if (orbit_trials, orbit_hits) != (60 * trials, 0):
        fail(f"orbit extension census changed: trials={orbit_trials} hits={orbit_hits}")
    controls += 1

    if weight3(LIVE_PREFIX) or sum(LIVE_PREFIX) != LENGTH or max(LIVE_PREFIX) > CAP:
        fail("live control prefix is not a non-weight-3 length-15 vector")
    controls += 1
    live_trials, live_hits, live_twelves = extension_census(LIVE_PREFIX)
    if (live_trials, live_hits, live_twelves) != (372, 13, 13):
        fail(
            "live control changed: "
            f"trials={live_trials} hits={live_hits} twelves={live_twelves}"
        )
    controls += 1

    if len(SEPARATION3_WORD) != 36 or len(PAIR09_WORD) != 36:
        fail("witness word length changed")
    controls += 1
    for word in (SEPARATION3_WORD, PAIR09_WORD):
        totals = prefix_counts(word, 36)
        if totals != (CAP,) * K:
            fail(f"witness is not a six-source floor word: {totals}")
    controls += 1
    q15 = prefix_counts(SEPARATION3_WORD, 15)
    q18 = prefix_counts(SEPARATION3_WORD, 18)
    q21 = prefix_counts(SEPARATION3_WORD, 21)
    delta = tuple(q21[j] - q18[j] for j in range(K))
    summed = separation_sum(q18, delta)
    if q15 != LIVE_PREFIX or weight3(q15) or not weight3(summed):
        fail(f"separation-3 witness changed: q15={q15} sum={summed}")
    if summed != (1, 1, 1, 12, 12, 12):
        fail(f"separation-3 sum changed: {summed}")
    controls += 1

    q9 = prefix_counts(PAIR09_WORD, 9)
    q18_off = prefix_counts(PAIR09_WORD, 18)
    q21_off = prefix_counts(PAIR09_WORD, 21)
    off_sum = tuple(q18_off[j] + q21_off[j] for j in range(K))
    if q9 != (1, 1, 1, 6, 0, 0) or weight3(off_sum):
        fail(f"(0, 9) witness changed: q9={q9} separation={off_sum}")
    controls += 1

    print(
        "PASS_SIX_SOURCE_C6_SUM15_PAIR015 "
        f"vectors={vectors} weight3={len(weight3_vectors)} "
        f"shape={SORTED_SHAPE} families=6 family_hits={family_hits} "
        f"shape_trials={orbit_trials} shape_extensions={orbit_hits} "
        f"live_prefix_extensions={live_hits} live_prefix_twelves={live_twelves} "
        f"controls={controls}"
    )


if __name__ == "__main__":
    main()
