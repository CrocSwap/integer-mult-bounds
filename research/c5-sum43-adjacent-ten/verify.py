#!/usr/bin/env python3
"""Adjacent centre on s + t = 43 at characteristic 5.

The argument is in README.md. Sigma is fixed at 43 before the census.
This program exhausts q_21 and the realizable one-step neighborhood.
It does not read sigma in {3, 23, 53}, it does not search for a depth-two
word, and it does not call a SAT solver.
"""

import itertools
import math

K = 6
C = 5
LENGTH = K * C
SIGMA = 43
CENTRE_S = (SIGMA - 1) // 2  # 21; partner 22
ALLOWED = (0, 1, C, C + 1, 2 * C)
MASK_BIT = {0: 0, 1: 1, C: 0, C + 1: 1, 2 * C: 0}
# Shape r_w = 0, three coordinates 10. Stationary step: word[20] = word[22] = 1.
SHAPE0_WORD = (1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5,
               1, 0, 1, 0, 0, 0, 0, 1, 2, 2)
# Shape r_w = 2, two coordinates 10. Moving step: subtract source 1, add source 0.
SHAPE2_WORD = (0, 0, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5,
               1, 0, 0, 0, 1, 1, 2, 2, 3, 3)


def fail(msg):
    raise SystemExit('FAIL: ' + msg)


def mask_weight(sum_vec):
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


def require_floor(word, label):
    if len(word) != LENGTH:
        fail(label + ' length is not 30')
    counts = [0] * K
    for letter in word:
        if not 0 <= letter < K:
            fail(label + ' letter out of range')
        counts[letter] += 1
        if counts[letter] > C:
            fail(label + ' exceeds five calls of one source')
    if counts != [C] * K:
        fail(label + ' is not a floor word: ' + str(counts))


def centre_sum(counts, centre):
    return tuple(2 * counts[j] + (1 if j == centre else 0) for j in range(K))


def realize_step(counts, centre, sub, add):
    """One floor word with word[20] = sub, word[21] = centre, word[22] = add."""
    if counts[sub] < 1:
        return None
    q22 = list(counts)
    q22[centre] += 1
    if q22[add] > C - 1:
        return None
    prefix = []
    for source, count in enumerate(counts):
        prefix.extend([source] * (count - (1 if source == sub else 0)))
    if len(prefix) != CENTRE_S - 1:
        fail('prefix before the subtracted letter has the wrong length')
    q23 = list(q22)
    q23[add] += 1
    if any(value > C for value in q23):
        return None
    tail = []
    for source, count in enumerate(q23):
        tail.extend([source] * (C - count))
    word = tuple(prefix + [sub, centre, add] + tail)
    if len(word) != LENGTH:
        fail('realized step does not fill the word')
    return word


def main():
    if (K, C, SIGMA, CENTRE_S, LENGTH) != (6, 5, 43, 21, 30):
        fail('pinned characteristic-5 sum-43 constants changed')
    if ALLOWED != (0, 1, 5, 6, 10) or 2 * CENTRE_S + 1 != SIGMA:
        fail('the adjacent sum is not 43')
    if SIGMA % 5 != 3:
        fail('sum 43 is not a weight-3 residue')

    non_centre = [r for r in range(C + 1) if 2 * r in MASK_BIT]
    centre_types = [r for r in range(C) if 2 * r + 1 in MASK_BIT]
    if non_centre != [0, 3, 5] or centre_types != [0, 2]:
        fail('local types changed: non-centre %s, centre %s' % (non_centre, centre_types))

    # Finite case split. n0 + n3 + n5 = 5, and the prefix total is 21.
    solutions = []
    for centre_count, remainder in ((0, 21), (2, 19)):
        for n5 in range(6):
            for n3 in range(6 - n5):
                n0 = 5 - n3 - n5
                if 3 * n3 + 5 * n5 == remainder:
                    solutions.append((centre_count, n0, n3, n5))
    if solutions != [(0, 0, 2, 3), (2, 0, 3, 2)]:
        fail('case split changed: ' + str(solutions))
    if any(n5 < 2 for _centre, _n0, _n3, n5 in solutions):
        fail('a legal solution has fewer than two coordinates equal to 10')
    predicted = {
        0: K * math.comb(5, 3),  # three fives among the five non-centre sources
        2: K * math.comb(5, 2),  # two fives among the five non-centre sources
    }
    if predicted != {0: 60, 2: 60}:
        fail('multinomial prediction changed: %s' % predicted)

    found = {0: [], 2: []}
    weights = {}
    frozen = 0
    min_tens = None
    max_tens = None
    domain = 0
    for counts in itertools.product(range(C + 1), repeat=K):
        domain += 1
        if sum(counts) != CENTRE_S:
            continue
        for centre in range(K):
            if counts[centre] >= C:
                continue
            summed = centre_sum(counts, centre)
            weight = mask_weight(summed)
            if weight is None:
                continue
            weights[weight] = weights.get(weight, 0) + 1
            tens = [j for j in range(K) if summed[j] == 10]
            if centre in tens or counts[centre] == 5:
                fail('a coordinate 10 sits on the centre letter')
            if sorted(counts[j] for j in tens) != [5] * len(tens):
                fail('a 10 is not a doubled five')
            frozen += len(tens)
            min_tens = len(tens) if min_tens is None else min(min_tens, len(tens))
            max_tens = len(tens) if max_tens is None else max(max_tens, len(tens))
            others = tuple(sorted(counts[j] for j in range(K) if j != centre))
            if counts[centre] == 0 and others == (3, 3, 5, 5, 5) and len(tens) == 3:
                shape = 0
            elif counts[centre] == 2 and others == (3, 3, 3, 5, 5) and len(tens) == 2:
                shape = 2
            else:
                fail('legal centre outside the two shapes: q=%s centre=%s sum=%s' % (counts, centre, summed))
            if weight != 3 or summed[centre] != (1 if shape == 0 else 5):
                fail('centre letter or weight left the shape: %s' % (summed,))
            found[shape].append((counts, centre, summed, tuple(tens)))

    if domain != (C + 1) ** K:
        fail('the prefix domain was not every tuple in {0,...,5}^6')
    if weights != {3: 120} or frozen != 300 or min_tens != 2 or max_tens != 3:
        fail('census mismatch: weights %s frozen %s range %s..%s' % (weights, frozen, min_tens, max_tens))
    if len(found[0]) != predicted[0] or len(found[2]) != predicted[2]:
        fail('shape counts changed: %s %s' % (len(found[0]), len(found[2])))

    immovable = [v for v in ALLOWED if v + 1 not in MASK_BIT and v - 1 not in MASK_BIT]
    increments = [v for v in ALLOWED if v + 1 in MASK_BIT]
    decrements = [v for v in ALLOWED if v - 1 in MASK_BIT]
    if immovable != [10] or increments != [0, 5] or decrements != [1, 6]:
        fail('move table changed: immovable %s +%s -%s' % (immovable, increments, decrements))
    if MASK_BIT[10] != 0:
        fail('10 is not a mask bit 0')
    splits = [(a, b) for a in range(C + 1) for b in range(C + 1) if a + b == 10]
    if splits != [(5, 5)]:
        fail('10 has another split inside {0,...,5}: %s' % (splits,))

    # Every legal one-step image keeps the coordinates that equal 10.
    # Counts come from the case split: shape 0 has two stationary steps,
    # shape 2 has four stationary steps and three moving steps.
    legal_steps = 0
    stationary_steps = 0
    moving_steps = 0
    for shape, rows in found.items():
        for counts, centre, summed, tens in rows:
            local_stationary = 0
            local_moving = 0
            for sub in range(K):
                for add in range(K):
                    word = realize_step(counts, centre, sub, add)
                    if word is None:
                        continue
                    image = list(summed)
                    image[sub] -= 1
                    image[add] += 1
                    require_floor(word, 'realized step')
                    pref = prefixes(word)
                    if pref[CENTRE_S] != counts or pref[CENTRE_S + 1][centre] != counts[centre] + 1:
                        fail('realized step left the centre prefix')
                    if word[CENTRE_S - 1] != sub or word[CENTRE_S] != centre or word[CENTRE_S + 1] != add:
                        fail('realized step did not place the chosen letters')
                    got = tuple(pref[CENTRE_S - 1][j] + pref[SIGMA - (CENTRE_S - 1)][j] for j in range(K))
                    if got != tuple(image):
                        fail('realized image disagrees with the letter step')
                    if mask_weight(image) is None:
                        continue
                    if tuple(j for j in range(K) if image[j] == 10) != tens:
                        fail('legal image moved a coordinate 10: %s -> %s' % (summed, image))
                    if mask_weight(image) != 3:
                        fail('legal image left weight 3')
                    if sub == add:
                        if tuple(image) != summed:
                            fail('a stationary step changed the sum')
                        local_stationary += 1
                    else:
                        if shape != 2 or sub == centre or add != centre:
                            fail('moving step outside the shape-2 pattern')
                        if summed[sub] != 6 or image[sub] != 5 or image[centre] != 6:
                            fail('moving step did not trade 6 for 5 against the centre')
                        local_moving += 1
            expect_stationary = 2 if shape == 0 else 4
            expect_moving = 0 if shape == 0 else 3
            if local_stationary != expect_stationary or local_moving != expect_moving:
                fail('one-step counts changed on shape %s: stationary %s moving %s' % (
                    shape, local_stationary, local_moving))
            legal_steps += local_stationary + local_moving
            stationary_steps += local_stationary
            moving_steps += local_moving
    if (legal_steps, stationary_steps, moving_steps) != (540, 360, 180):
        fail('neighborhood totals changed: %s %s %s' % (legal_steps, stationary_steps, moving_steps))

    controls = 0

    # A sum-21 prefix can still leave A. Four fives, a one and a zero is one example.
    near = (5, 5, 5, 5, 1, 0)
    near_sum = centre_sum(near, 5)
    if sum(near) != CENTRE_S or mask_weight(near_sum) is not None or 2 not in near_sum:
        fail('near-miss centre was accepted: %s' % (near_sum,))
    controls += 1

    # Pair geometry on this sum only. The earliest prefix has length 14.
    slots = []
    adjacent = []
    for left in range(LENGTH):
        right = SIGMA - left
        if left <= right <= LENGTH - 1:
            slots.append((left, right))
            if right - left == 1:
                adjacent.append((left, right))
    if slots != [(14, 29), (15, 28), (16, 27), (17, 26), (18, 25), (19, 24), (20, 23), (21, 22)]:
        fail('sum-43 slots changed: %s' % (slots,))
    if adjacent != [(21, 22)]:
        fail('adjacent pair changed: %s' % (adjacent,))
    controls += 1

    # Length 14 can hold a five, so the walk down to s = 14 does not die by quota.
    # This vector is a capacity example. It is not a legal diagonal slot.
    capacity = (5, 5, 4, 0, 0, 0)
    if sum(capacity) != slots[0][0] or any(value > C for value in capacity) or 5 not in capacity:
        fail('length-14 capacity example changed')
    controls += 1

    # Shape 0: three 10s, and a stationary legal neighbor that keeps all three.
    require_floor(SHAPE0_WORD, 'shape-0 witness')
    pref = prefixes(SHAPE0_WORD)
    top = tuple(pref[21][j] + pref[22][j] for j in range(K))
    nxt = tuple(pref[20][j] + pref[23][j] for j in range(K))
    if pref[21] != (0, 3, 3, 5, 5, 5) or top != (1, 6, 6, 10, 10, 10):
        fail('shape-0 centre changed: %s' % (top,))
    if SHAPE0_WORD[20] != SHAPE0_WORD[22] or nxt != top or mask_weight(nxt) != 3:
        fail('shape-0 stationary step changed: %s' % (nxt,))
    if sum(value == 10 for value in top) != 3:
        fail('shape-0 witness lost a 10')
    controls += 1

    # Shape 2: two 10s. The next legal step moves a 6 to a 5 and the centre 5 to a 6.
    require_floor(SHAPE2_WORD, 'shape-2 witness')
    pref = prefixes(SHAPE2_WORD)
    top = tuple(pref[21][j] + pref[22][j] for j in range(K))
    nxt = tuple(pref[20][j] + pref[23][j] for j in range(K))
    if pref[21] != (2, 3, 3, 3, 5, 5) or top != (5, 6, 6, 6, 10, 10):
        fail('shape-2 centre changed: %s' % (top,))
    if nxt != (6, 5, 6, 6, 10, 10) or mask_weight(top) != 3 or mask_weight(nxt) != 3:
        fail('shape-2 moving step changed: %s -> %s' % (top, nxt))
    if SHAPE2_WORD[20] != 1 or SHAPE2_WORD[21] != 0 or SHAPE2_WORD[22] != 0:
        fail('shape-2 letters are not subtract 1, centre 0, add 0')
    if not (top[1] == 6 and nxt[1] == 5 and top[0] == 5 and nxt[0] == 6):
        fail('shape-2 step did not trade the centre against a 6')
    if [j for j in range(K) if top[j] == 10] != [j for j in range(K) if nxt[j] == 10]:
        fail('shape-2 step moved a 10')
    controls += 1

    # Subtracting a five is count-feasible and the added letter has room,
    # but 10 - 1 = 9 leaves A. Feasibility is not what saves the 10.
    bumped = list(top)
    bumped[4] -= 1
    bumped[1] += 1
    if pref[21][4] < 1 or pref[22][1] >= C or mask_weight(bumped) is not None or bumped[4] != 9:
        fail('subtracting a 10 did not exit A')
    controls += 1

    if controls != 6:
        fail('control count changed: %s' % controls)

    print(
        'PASS_C5_SUM43_ADJACENT_TEN '
        'sigma=43 centre=(21,22) centres=120 shape0=60 shape2=60 '
        'frozen10=300 min10=2 max10=3 weight3=120 '
        'steps=540 stationary=360 moving=180 slots=8 '
        'earliest_prefix=14 capacity_has_5=yes controls=6'
    )


if __name__ == '__main__':
    main()
