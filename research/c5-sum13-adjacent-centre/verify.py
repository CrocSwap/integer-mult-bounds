#!/usr/bin/env python3
"""Classification of the characteristic-5 adjacent centre on s + t = 13.

The argument is in README.md. This program exhausts the finite centre domain
and the finite one-step neighborhood, and it checks three explicit words.
It does not search for a depth-two word and it does not call a SAT solver.
"""

import itertools
import math

K = 6
C = 5
LENGTH = K * C
SIGMA = 13
CENTRE_S = 6  # partner 7; 6 + 7 = 13
ALLOWED = (0, 1, C, C + 1, 2 * C)
MASK_BIT = {0: 0, 1: 1, C: 0, C + 1: 1, 2 * C: 0}
# Floor word whose seven sum-13 pairs are all legal. The centre letter is 0.
DIAGONAL = (1, 1, 1, 2, 2, 2, 0, 2, 2, 3, 1, 1, 4, 0, 0, 0, 0,
            3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5)
# Same centre, with the next letter moving a 6 down to 5.
STEP = (1, 1, 1, 2, 2, 2, 0, 3, 0, 0, 0, 0, 1, 1, 2, 2,
        3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5)
PUBLISHED = (0, 0, 0, 0, 0, 1, 2, 3, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5,
             1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 4, 5)
DIAGONAL_SUMS = {
    0: (1, 5, 5, 1, 1, 0),
    1: (1, 6, 5, 1, 0, 0),
    2: (1, 6, 5, 1, 0, 0),
    3: (1, 6, 5, 1, 0, 0),
    4: (1, 6, 6, 0, 0, 0),
    5: (1, 6, 6, 0, 0, 0),
    6: (1, 6, 6, 0, 0, 0),
}


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


def mask_of(sum_vec):
    if mask_weight(sum_vec) is None:
        return None
    return tuple(MASK_BIT[value] for value in sum_vec)


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


def main():
    if (K, C, SIGMA, CENTRE_S) != (6, 5, 13, 6) or ALLOWED != (0, 1, 5, 6, 10):
        fail('pinned characteristic-5 constants changed')
    if 2 * CENTRE_S + 1 != SIGMA:
        fail('the adjacent sum is not 13')

    non_centre = [r for r in range(C + 1) if 2 * r in MASK_BIT]
    centre_types = [r for r in range(C) if 2 * r + 1 in MASK_BIT]
    if non_centre != [0, 3, 5] or centre_types != [0, 2]:
        fail('local types changed: non-centre %s, centre %s' % (non_centre, centre_types))

    # Finite case split: n0 + n3 + n5 = 5 and the count equation.
    solutions = []
    for centre_count, remainder in ((0, 6), (2, 4)):
        for n5 in range(6):
            for n3 in range(6):
                n0 = 5 - n3 - n5
                if n0 < 0:
                    continue
                if 3 * n3 + 5 * n5 == remainder:
                    solutions.append((centre_count, n0, n3, n5))
    if solutions != [(0, 3, 2, 0)]:
        fail('case split changed: ' + str(solutions))
    predicted = K * math.comb(5, 2)
    if predicted != 60:
        fail('multinomial prediction changed: %s' % predicted)

    found = []
    weights = {}
    frozen = 0
    for counts in itertools.product(range(C + 1), repeat=K):
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
            frozen += sum(1 for value in summed if value == 10)
            others = tuple(sorted(counts[j] for j in range(K) if j != centre))
            values = tuple(sorted(summed))
            if counts[centre] != 0 or others != (0, 0, 0, 3, 3) or values != (0, 0, 0, 1, 6, 6):
                fail('legal centre outside the unique shape: q=%s centre=%s sum=%s' % (counts, centre, summed))
            if summed[centre] != 1 or weight != 3:
                fail('centre letter is not the unique 1 of a weight-3 mask')
            found.append((counts, centre, summed))

    if weights != {3: predicted} or len(found) != predicted or frozen != 0:
        fail('census mismatch: weights %s found %s frozen %s' % (weights, len(found), frozen))

    immovable = [v for v in ALLOWED if v + 1 not in MASK_BIT and v - 1 not in MASK_BIT]
    increments = [v for v in ALLOWED if v + 1 in MASK_BIT]
    decrements = [v for v in ALLOWED if v - 1 in MASK_BIT]
    if immovable != [10] or increments != [0, 5] or decrements != [1, 6]:
        fail('move table changed: immovable %s +%s -%s' % (immovable, increments, decrements))
    if MASK_BIT[10] != 0 or 1 not in decrements:
        fail('10 is not a 0-bit, or 1 cannot decrease inside A')
    share_total = math.comb(K, 3)
    share_hit = math.comb(K - 1, 2)
    if share_total != 20 or share_hit != 10:
        fail('weight-3 share changed: %s of %s' % (share_hit, share_total))

    # Every one of the 60 count vectors is a prefix of a floor word.
    for counts, centre, summed in found:
        order = []
        for source, count in enumerate(counts):
            order.extend([source] * count)
        if len(order) != CENTRE_S or centre in order:
            fail('centre letter already occurs in q_6')
        q7 = list(counts)
        q7[centre] += 1
        if any(value > C for value in q7):
            fail('q_7 exceeds five')
        rest = []
        for source, count in enumerate(q7):
            rest.extend([source] * (C - count))
        if sum(C - count for count in q7) != LENGTH - (CENTRE_S + 1):
            fail('residual quota does not fill the word')
        word = tuple(order + [centre] + rest)
        require_floor(word, 'realized centre')
        pref = prefixes(word)
        if pref[CENTRE_S] != counts or pref[CENTRE_S + 1][centre] != 1:
            fail('realized prefix left the centre shape')
        if centre_sum(pref[CENTRE_S], centre) != summed:
            fail('realized centre sum changed')

    # Exhaustive one-step neighborhood. A subtraction is realizable only when
    # that source occurs in q_6. Every addition is count-feasible on this shape.
    legal_steps = 0
    moving_steps = 0
    for counts, centre, summed in found:
        q7 = list(counts)
        q7[centre] += 1
        local_legal = 0
        local_moving = 0
        realizable_subs = [source for source in range(K) if counts[source] >= 1]
        if realizable_subs != [source for source in range(K) if counts[source] == 3]:
            fail('realizable subtraction letters are not the two triple sources')
        for sub in realizable_subs:
            for add in range(K):
                if q7[add] >= C:
                    fail('a count-feasible addition was rejected by the shape')
                image = list(summed)
                image[sub] -= 1
                image[add] += 1
                if mask_weight(image) is None:
                    continue
                if image[centre] != 1:
                    fail('legal one-step image moved the centre coordinate: %s' % image)
                local_legal += 1
                if any(summed[j] == 6 and image[j] == 5 for j in range(K)):
                    local_moving += 1
        if local_legal != 8 or local_moving != 6:
            fail('one-step counts changed: legal %s moving %s' % (local_legal, local_moving))
        legal_steps += local_legal
        moving_steps += local_moving
    if legal_steps != 480 or moving_steps != 360:
        fail('neighborhood totals changed: %s %s' % (legal_steps, moving_steps))

    controls = 0

    # Sum 6 can still leave A. Three 2s with centre letter 0 is one example.
    near = (2, 2, 2, 0, 0, 0)
    if sum(near) != CENTRE_S or mask_weight(centre_sum(near, 0)) is not None:
        fail('near-miss centre was accepted')
    controls += 1

    # Pair geometry: (6, 7) is the only adjacent pair on sum 13, and sum 28
    # has none. This package does not classify the repeated index (14, 14).
    adjacent_13 = []
    adjacent_28 = []
    slots_13 = 0
    slots_28 = 0
    for left in range(LENGTH):
        for right in range(left, LENGTH):
            if left + right == 13:
                slots_13 += 1
                if right - left == 1:
                    adjacent_13.append((left, right))
            if left + right == 28:
                slots_28 += 1
                if right - left == 1:
                    adjacent_28.append((left, right))
    if slots_13 != 7 or adjacent_13 != [(6, 7)] or slots_28 != 15 or adjacent_28 != []:
        fail('adjacent-pair geometry changed: %s %s %s %s' % (slots_13, adjacent_13, slots_28, adjacent_28))
    controls += 1

    # Full diagonal: every sum-13 pair is legal and the centre coordinate stays 1.
    require_floor(DIAGONAL, 'diagonal witness')
    pref = prefixes(DIAGONAL)
    if pref[6] != (0, 3, 3, 0, 0, 0) or pref[7] != (1, 3, 3, 0, 0, 0):
        fail('diagonal witness left the centre shape')
    seen = set()
    for slot in range(7):
        summed = tuple(pref[slot][j] + pref[13 - slot][j] for j in range(K))
        if summed != DIAGONAL_SUMS[slot] or mask_weight(summed) != 3 or summed[0] != 1:
            fail('diagonal slot %s changed: %s' % (slot, summed))
        seen.add(mask_of(summed))
    for slot in range(1, 7):
        current = tuple(pref[slot][j] + pref[13 - slot][j] for j in range(K))
        previous = tuple(pref[slot - 1][j] + pref[14 - slot][j] for j in range(K))
        sub = DIAGONAL[slot - 1]
        add = DIAGONAL[13 - slot]
        if sub == 0:
            fail('a downward step subtracted the centre letter')
        expected = list(current)
        expected[sub] -= 1
        expected[add] += 1
        if tuple(expected) != previous or previous[0] != 1:
            fail('diagonal recurrence broke at slot %s' % slot)
    if seen != {(1, 1, 1, 0, 0, 0), (1, 1, 0, 1, 0, 0), (1, 0, 0, 1, 1, 0)}:
        fail('diagonal masks changed: %s' % (seen,))
    controls += 1

    # One legal step can move a 6 to a 5 and a 0 to a 1. The centre bit stays 1.
    require_floor(STEP, 'step witness')
    pref = prefixes(STEP)
    top = tuple(pref[6][j] + pref[7][j] for j in range(K))
    nxt = tuple(pref[5][j] + pref[8][j] for j in range(K))
    if top != (1, 6, 6, 0, 0, 0) or nxt != (1, 6, 5, 1, 0, 0):
        fail('step witness sums changed: %s -> %s' % (top, nxt))
    if mask_weight(top) != 3 or mask_weight(nxt) != 3 or nxt[0] != 1:
        fail('step witness left A or moved the centre bit')
    if not any(top[j] == 6 and nxt[j] == 5 for j in range(K)):
        fail('step witness did not move a 6')
    if not any(top[j] == 0 and nxt[j] == 1 for j in range(K)):
        fail('step witness did not move a 0')
    controls += 1

    # Replacing that added letter by the centre letter sends 1 to 2.
    bumped = list(top)
    bumped[STEP[5]] -= 1  # undo w_5, which is not the centre letter
    bumped[0] += 1
    if STEP[5] == 0 or mask_weight(bumped) is not None or bumped[0] != 2:
        fail('adding the centre letter did not exit A')
    controls += 1

    # The published sum-13 witness realizes a 10 off the adjacent pair.
    # Its own adjacent centre is illegal, so a weight-3 mask at sum 13 does
    # not make (6, 7) legal.
    require_floor(PUBLISHED, 'published witness')
    pref = prefixes(PUBLISHED)
    adjacent = tuple(pref[6][j] + pref[7][j] for j in range(K))
    off = tuple(pref[5][j] + pref[8][j] for j in range(K))
    if adjacent != (10, 2, 1, 0, 0, 0) or mask_weight(adjacent) is not None:
        fail('published adjacent centre became legal: %s' % (adjacent,))
    if off != (10, 1, 1, 1, 0, 0) or mask_weight(off) != 3 or 5 + 8 != 13:
        fail('published off-adjacent pair changed: %s' % (off,))
    if off[0] != 10:
        fail('published off-adjacent pair lost its 10')
    controls += 1

    if controls != 6:
        fail('control count changed: %s' % controls)

    print(
        'PASS_C5_SUM13_ADJACENT_CENTRE '
        'centres=60 weight3=60 frozen10=0 immovable=[10] mask_bit10=0 '
        'share=10/20 adjacent_pair=(6,7) sum28_adjacent_pairs=0 '
        'legal_steps=480 moving_steps=360 diagonal_slots=7 centre_bit=1 '
        'published_adjacent=illegal controls=6'
    )


if __name__ == '__main__':
    main()
