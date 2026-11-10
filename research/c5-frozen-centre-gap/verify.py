#!/usr/bin/env python3
"""Finite census for the characteristic-5 centre on s + t = 33.

The human argument is in README.md. This program exhausts three finite
domains and checks the witness word. It does not search for a depth-two
word and it does not call a SAT solver.
"""

import itertools
import math

K = 6
C = 5
LENGTH = K * C
CENTRE_S = 3 * C + 1  # 16; partner is 17, and 16 + 17 = 33
SIGMA = K * C + 3  # 33
ALLOWED = (0, 1, C, C + 1, 2 * C)
MASK_BIT = {0: 0, 1: 1, C: 0, C + 1: 1, 2 * C: 0}
WITNESS = (0, 0, 0, 0, 0, 1, 2, 3, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5,
           1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 4, 5)


def fail(msg):
    raise SystemExit('FAIL: ' + msg)


def mask_weight(sum_vec):
    """Return the mask weight, or None when a coordinate lies outside ALLOWED."""
    bits = 0
    for value in sum_vec:
        bit = MASK_BIT.get(value)
        if bit is None:
            return None
        bits += bit
    return bits


def prefixes(word):
    counts = [0] * K
    out = [tuple(counts)]
    for letter in word:
        counts[letter] += 1
        out.append(tuple(counts))
    return out


def main():
    if CENTRE_S != 16 or SIGMA != 33 or ALLOWED != (0, 1, 5, 6, 10):
        fail('pinned characteristic-5 constants changed')
    if len(WITNESS) != LENGTH:
        fail('witness length is not 30')

    # Local types are the integer r in 0..5 whose doubled sum lands in ALLOWED.
    non_centre = [r for r in range(C + 1) if 2 * r in MASK_BIT]
    centre_types = [r for r in range(C) if 2 * r + 1 in MASK_BIT]
    if non_centre != [0, 3, 5] or centre_types != [0, 2]:
        fail(f'local types changed: non-centre {non_centre}, centre {centre_types}')

    type_r0 = 6 * math.comb(5, 2) * math.comb(3, 2)
    type_r2 = 6 * math.comb(5, 3) * math.comb(2, 1)
    if type_r0 != 180 or type_r2 != 120:
        fail(f'multinomial prediction changed: {type_r0}, {type_r2}')

    found_r0 = 0
    found_r2 = 0
    frozen = 0
    weights = {}
    for counts in itertools.product(range(C + 1), repeat=K):
        if sum(counts) != CENTRE_S:
            continue
        for centre in range(K):
            if counts[centre] >= C:
                continue
            summed = tuple(2 * counts[j] + (1 if j == centre else 0) for j in range(K))
            weight = mask_weight(summed)
            if weight is None:
                continue
            weights[weight] = weights.get(weight, 0) + 1
            n10 = 0
            for j, value in enumerate(summed):
                if value != 10:
                    continue
                n10 += 1
                frozen += 1
                if counts[j] != C or j == centre:
                    fail(f'10 is not a pair of fives off the centre letter: {counts} {centre}')
            if counts[centre] == 0 and summed[centre] == 1 and n10 == 2 and weight == 3:
                others = sorted(counts[j] for j in range(K) if j != centre)
                if others != [0, 3, 3, 5, 5]:
                    fail(f'type r=0 shape changed: {counts}')
                found_r0 += 1
            elif counts[centre] == 2 and summed[centre] == 5 and n10 == 1 and weight == 3:
                others = sorted(counts[j] for j in range(K) if j != centre)
                if others != [0, 3, 3, 3, 5]:
                    fail(f'type r=2 shape changed: {counts}')
                found_r2 += 1
            else:
                fail(
                    f'centre outside the two types: q={counts} centre={centre} '
                    f'sum={summed} weight={weight} tens={n10}'
                )

    if weights != {3: type_r0 + type_r2}:
        fail(f'legal centre weights are not exactly weight 3: {weights}')
    if found_r0 != type_r0 or found_r2 != type_r2 or frozen != 2 * type_r0 + type_r2:
        fail(
            f'census/multinomial mismatch: found {found_r0}, {found_r2}, frozen {frozen}'
        )

    increments = [v for v in ALLOWED if v + 1 in MASK_BIT]
    decrements = [v for v in ALLOWED if v - 1 in MASK_BIT]
    if increments != [0, 5] or decrements != [1, 6]:
        fail(f'move table changed: +{increments} -{decrements}')
    if 10 in increments or 10 in decrements:
        fail('10 is movable inside the allowed set')

    controls = 0

    # A sum of 16 can still fail the allowed set. Five 3s and a 1 is one example.
    near = (3, 3, 3, 3, 3, 1)
    if sum(near) != CENTRE_S:
        fail('near-miss no longer sums to 16')
    near_sum = tuple(2 * near[j] + (1 if j == 5 else 0) for j in range(K))
    if mask_weight(near_sum) is not None:
        fail('near-miss centre was accepted')
    controls += 1

    # Every length-4 count in {0,...,5}^6 is too small to contain a 5.
    for prefix in itertools.product(range(C + 1), repeat=K):
        if sum(prefix) == 4 and max(prefix) >= C:
            fail('length-4 prefix contains a 5')
    controls += 1

    # Every allowed 6-tuple has coordinate sum congruent to its mask weight.
    # Sum 33 therefore admits only weight 3, never weight 2 or 6.
    for values in itertools.product(ALLOWED, repeat=K):
        weight = mask_weight(values)
        if sum(values) % C != weight % C:
            fail(f'weight identity failed on {values}')
    if 33 % C != 3:
        fail('33 is not residue 3')
    for weight in (0, 1, 2, 4, 5, 6):
        if weight % C == 3:
            fail('another weight in 0..6 is congruent to 3')
    controls += 1

    # Complete pair census: every 0 <= s <= t <= 29.
    slot_counts = {}
    pair_total = 0
    for s in range(LENGTH):
        for t in range(s, LENGTH):
            pair_total += 1
            slot_counts[s + t] = slot_counts.get(s + t, 0) + 1
    if pair_total != 465 or slot_counts[33] != 13 or slot_counts[3] != 2:
        fail(f'pair census changed: total {pair_total}, 33={slot_counts.get(33)}, 3={slot_counts.get(3)}')
    residue3 = sorted(sigma for sigma in slot_counts if sigma % C == 3)
    expected_residue = [3, 8, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58]
    expected_counts = {
        3: 2, 8: 5, 13: 7, 18: 10, 23: 12, 28: 15,
        33: 13, 38: 11, 43: 8, 48: 6, 53: 3, 58: 1,
    }
    if residue3 != expected_residue:
        fail(f'residue-3 sums changed: {residue3}')
    for sigma, count in expected_counts.items():
        if slot_counts[sigma] != count:
            fail(f'slot count at {sigma} is {slot_counts[sigma]}, expected {count}')
    if sum(expected_counts.values()) != 93:
        fail('residue-3 total is not 93')
    middle = [s for s in range(4, 17) if s + (33 - s) == 33 and 33 - s <= 29]
    if middle != list(range(4, 17)):
        fail(f'middle indices changed: {middle}')
    controls += 1

    # (1, 2) never lands in the allowed set: the first letter is at least 2.
    legal_12 = 0
    for first, second in itertools.product(range(K), repeat=2):
        q1 = [0] * K
        q1[first] = 1
        q2 = q1[:]
        q2[second] += 1
        summed = [q1[j] + q2[j] for j in range(K)]
        if mask_weight(summed) is not None:
            legal_12 += 1
        if summed[first] < 2:
            fail('first letter of (1, 2) dropped below 2')
    if legal_12 != 0:
        fail(f'(1, 2) realized a mask {legal_12} times')
    controls += 1
    early = [1, 1, 1, 0, 0, 0]
    if mask_weight(early) != 3:
        fail('(0, 3) with three distinct letters was rejected')
    controls += 1

    # Witness: a floor word with one off-diagonal weight-3 mask and an illegal centre.
    # It realizes 8 nonzero masks and is not a depth-two word.
    counts = [0] * K
    for letter in WITNESS:
        if not 0 <= letter < K:
            fail('witness letter out of range')
        counts[letter] += 1
    if counts != [C] * K:
        fail(f'witness is not a floor word: {counts}')
    pref = prefixes(WITNESS)
    pair_58 = tuple(pref[5][j] + pref[8][j] for j in range(K))
    if pref[5] != (5, 0, 0, 0, 0, 0) or pref[8] != (5, 1, 1, 1, 0, 0):
        fail(f'witness prefixes changed: q5={pref[5]} q8={pref[8]}')
    if pair_58 != (10, 1, 1, 1, 0, 0) or mask_weight(pair_58) != 3 or 5 + 8 != 13:
        fail(f'witness off-diagonal pair changed: {pair_58}')
    centre_sum = tuple(pref[16][j] + pref[17][j] for j in range(K))
    if pref[16] != (5, 3, 3, 3, 1, 1) or pref[17] != (5, 3, 3, 3, 2, 1):
        fail(f'witness centre prefixes changed: {pref[16]} {pref[17]}')
    if centre_sum != (10, 6, 6, 6, 3, 2) or mask_weight(centre_sum) is not None:
        fail(f'witness centre became legal: {centre_sum}')
    realized = set()
    for s in range(LENGTH):
        for t in range(s, LENGTH):
            summed = tuple(pref[s][j] + pref[t][j] for j in range(K))
            weight = mask_weight(summed)
            if weight is None:
                continue
            mask = tuple(MASK_BIT[value] for value in summed)
            if any(mask):
                realized.add(mask)
    by_weight = {}
    for mask in realized:
        by_weight[sum(mask)] = by_weight.get(sum(mask), 0) + 1
    if len(realized) != 8 or by_weight.get(2) != 3 or by_weight.get(3) != 2 or by_weight.get(6, 0) != 0:
        fail(f'witness mask census changed: {len(realized)} {by_weight}')
    if len(realized) == (1 << K) - 1:
        fail('witness is depth two')
    controls += 1

    print(
        'PASS_C5_FROZEN_CENTRE_GAP '
        f'centres={found_r0 + found_r2} type_r0={found_r0} type_r2={found_r2} '
        f'frozen_coordinates={frozen} moves=+{increments}/-{decrements} '
        f'residue3_pairs=93 middle_slots=13 early_realizable_slots=1 '
        f'witness_masks=8 chain_H=empty controls={controls}'
    )


if __name__ == '__main__':
    main()
