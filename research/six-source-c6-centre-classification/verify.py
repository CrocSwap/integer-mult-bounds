#!/usr/bin/env python3
"""Exhaustive centre census for the c=6 diagonal s+t=39.

The written argument is in README.md. This program enumerates every length-19
count vector and every legal centre letter. It does not search words and it
does not call a SAT solver.
"""
import itertools

K = 6
C = 6
CENTRE_LENGTH = 19
ALLOWED = (0, 1, 6, 7, 12)
ALLOWED_SET = set(ALLOWED)
# 13 would be 6+6+1. It is unreachable for two counts in 0..6, and it is
# kept here only as a widened control.
WIDENED = ALLOWED_SET | {13}
MASK_BIT = {0: 0, 1: 1, 6: 0, 7: 1, 12: 0, 13: 1}


def fail(msg):
    raise SystemExit("FAIL: " + msg)


def mask_weight(sum_vec, allowed):
    """Return the number of mask bits, or None if any coordinate is illegal."""
    bits = 0
    for value in sum_vec:
        if value not in allowed:
            return None
        bits += MASK_BIT[value]
    return bits


def weight3(sum_vec):
    return mask_weight(sum_vec, ALLOWED_SET) == 3


def prefix_counts(word, length):
    counts = [0] * K
    for source in word[:length]:
        counts[source] += 1
    return counts


def centre_pair_sum(counts, centre):
    return [2 * counts[j] + (1 if j == centre else 0) for j in range(K)]


def main():
    sum19 = 0
    examined = 0
    residue_legal = 0
    weight3_centres = 0
    for counts in itertools.product(range(C + 1), repeat=K):
        if sum(counts) != CENTRE_LENGTH:
            continue
        sum19 += 1
        for centre in range(K):
            # The centre letter is still ahead of q_19, so that source has
            # at most five calls already.
            if counts[centre] >= C:
                continue
            examined += 1
            summed = centre_pair_sum(counts, centre)
            if mask_weight(summed, ALLOWED_SET) is None:
                continue
            residue_legal += 1
            if weight3(summed):
                weight3_centres += 1
                fail(f"weight-3 centre exists: q={counts} centre={centre} sum={summed}")
    if (sum19, examined, residue_legal, weight3_centres) != (9156, 46956, 0, 0):
        fail(
            "centre census changed: "
            f"sum19={sum19} examined={examined} "
            f"residue_legal={residue_legal} weight3={weight3_centres}"
        )

    # Type table: the only counts whose double, or double plus one, lands in
    # the allowed set. Seven values, all checked.
    even_counts = [r for r in range(C + 1) if 2 * r in ALLOWED_SET]
    odd_counts = [r for r in range(C + 1) if 2 * r + 1 in ALLOWED_SET]
    if even_counts != [0, 3, 6] or odd_counts != [0, 3]:
        fail(f"type table changed: even={even_counts} odd={odd_counts}")
    mod3_shapes = sum(
        1
        for counts in itertools.product((0, 3, 6), repeat=K)
        if sum(counts) == CENTRE_LENGTH
    )
    if mod3_shapes != 0:
        fail(f"a multiple-of-3 count vector sums to 19: {mod3_shapes}")

    # Widened control: admitting the unreachable value 13, and admitting a
    # centre source that has already been used six times, is still empty.
    widened_trials = 0
    widened_legal = 0
    for counts in itertools.product(range(C + 1), repeat=K):
        if sum(counts) != CENTRE_LENGTH:
            continue
        for centre in range(K):
            widened_trials += 1
            summed = centre_pair_sum(counts, centre)
            if mask_weight(summed, WIDENED) is not None:
                widened_legal += 1
    if (widened_trials, widened_legal) != (54936, 0):
        fail(f"widened census changed: trials={widened_trials} legal={widened_legal}")

    increments = [v for v in ALLOWED if v + 1 in ALLOWED_SET]
    decrements = [v for v in ALLOWED if v - 1 in ALLOWED_SET]
    if increments != [0, 6] or decrements != [1, 7]:
        fail(f"move table changed: +{increments} -{decrements}")
    if 12 in increments or 12 in decrements or 14 in ALLOWED_SET:
        fail("12 is movable or 14 is an allowed c=6 coordinate")

    controls = 0
    if not weight3((1, 1, 1, 0, 6, 12)):
        fail("predicate rejected a weight-3 sum")
    controls += 1
    if not weight3((1, 1, 1, 12, 12, 12)):
        fail("predicate rejected the separation-3 sum")
    controls += 1
    if weight3((2, 1, 0, 12, 12, 12)):
        fail("predicate accepted a centre sum with a 2")
    controls += 1
    # The c=7 handoff prefix realizes weight 4 at c=6.
    handoff = prefix_counts([3, 3, 3, 3, 0, 1, 2], 3)
    handoff_late = prefix_counts([3, 3, 3, 3, 0, 1, 2], 7)
    handoff_sum = [handoff[j] + handoff_late[j] for j in range(K)]
    if handoff_sum != [1, 1, 1, 7, 0, 0] or mask_weight(handoff_sum, ALLOWED_SET) != 4:
        fail(f"handoff prefix transferred incorrectly: {handoff_sum}")
    controls += 1

    diagonal = (
        [3] * 6 + [4] * 6 + [5] * 6 + [0, 1, 2] + [0] * 5 + [1] * 5 + [2] * 5
    )
    if len(diagonal) != K * C or sorted(diagonal) != sorted(source for source in range(K) for _ in range(C)):
        fail("separation-3 witness is not a floor word")
    q18 = prefix_counts(diagonal, 18)
    q21 = prefix_counts(diagonal, 21)
    q19 = prefix_counts(diagonal, 19)
    sep_sum = [q18[j] + q21[j] for j in range(K)]
    centre_sum = [q19[j] + prefix_counts(diagonal, 20)[j] for j in range(K)]
    if sep_sum != [1, 1, 1, 12, 12, 12] or not weight3(sep_sum):
        fail(f"separation-3 pair is not weight 3: {sep_sum}")
    if centre_sum != [2, 1, 0, 12, 12, 12] or weight3(centre_sum):
        fail(f"same word has a weight-3 centre: {centre_sum}")
    if diagonal[19] != 1 or q19[1] != 0:
        fail("centre letter of the witness moved")
    controls += 1

    off = [3] * 6 + [0, 1, 2] + [0] * 5 + [1] * 5 + [2] * 5 + [4] * 6 + [5] * 6
    if len(off) != K * C or sorted(off) != sorted(diagonal):
        fail("s+t=9 witness is not a floor word")
    q9 = prefix_counts(off, 9)
    if q9 != [1, 1, 1, 6, 0, 0] or not weight3(q9):
        fail(f"s+t=9 pair is not weight 3: {q9}")
    controls += 1

    # Multiples of 3 can sum to 18, so the obstruction is the length 19.
    if sum((6, 6, 6, 0, 0, 0)) != 18:
        fail("length-18 shape disappeared")
    controls += 1

    # s+t=3 has two candidate pairs. (1,2) is 2e_a+e_b or 3e_a.
    for early in ((2, 1, 0, 0, 0, 0), (3, 0, 0, 0, 0, 0)):
        if weight3(early):
            fail(f"(1,2) was accepted: {early}")
    controls += 1

    if controls != 8:
        fail(f"control count changed: {controls}")

    print(
        "PASS_SIX_SOURCE_C6_CENTRE_CLASSIFICATION "
        f"sum19={sum19} examined={examined} "
        f"residue_legal={residue_legal} weight3={weight3_centres} "
        f"mod3_shapes={mod3_shapes} widened_legal={widened_legal} "
        f"moves=+{increments}/-{decrements} frozen_value=12 "
        f"controls={controls}"
    )


if __name__ == "__main__":
    main()
