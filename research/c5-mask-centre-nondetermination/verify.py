#!/usr/bin/env python3
"""The sixteen c=5 masks do not force a legal sum-33 centre.

Evidence class: exhaustive finite census. The human completeness argument
is in README.md. This program enumerates every admissible all-ones window,
builds a floor word for every window with an illegal centre, and checks the
explicit weight-2 witnesses. It does not call a SAT solver and it does not
search the joint sixteen-mask fibre.
"""

import itertools
import math

K = 6
C = 5
LENGTH = K * C
ALLOWED = (0, 1, C, C + 1, 2 * C)
MASK_BIT = {0: 0, 1: 1, 5: 0, 6: 1, 10: 0}
# (q_s, q_t, delta) for a coordinate whose sum is 1 or 6.
TYPES = {
    'A': (0, 1, 1),
    'B': (1, 5, 4),
    'C': (2, 4, 2),
    'D': (3, 3, 0),
}

# Discovery of the two legal-centre words used a local CaDiCaL search.
# The checks below do not call that solver.
SORTED = '000001111122222333334444455555'
WEIGHT2_LEGAL = '001211112322203343354444555500'
WEIGHT6_LEGAL = '012300333300112241122545545544'
# Weight 6 at the repeated boundary (18, 18), plus 13 weight-2 masks.
JOINT = '102431540325045231253054314120'
# Same all-ones window as WEIGHT6_LEGAL, with an illegal centre.
WEIGHT6_TWIN = '012311222233334500001144445555'
JOINT_MISSING = ((0, 0, 1, 0, 1, 0), (0, 1, 0, 0, 0, 1))


def fail(msg):
    raise SystemExit('FAIL: ' + msg)


def prefixes(word):
    counts = [0] * K
    out = [tuple(counts)]
    for letter in word:
        counts[letter] += 1
        out.append(tuple(counts))
    return out


def mask_of(sum_vec):
    bits = []
    for value in sum_vec:
        bit = MASK_BIT.get(value)
        if bit is None:
            return None
        bits.append(bit)
    return tuple(bits)


def centre_sum(q16, letter):
    return tuple(2 * q16[j] + (1 if j == letter else 0) for j in range(K))


def legal_letters(q16):
    if sum(q16) != 16:
        return []
    letters = []
    for letter in range(K):
        if q16[letter] >= C:
            continue
        if mask_of(centre_sum(q16, letter)) is not None:
            letters.append(letter)
    return letters


def expand(counts):
    return [j for j in range(K) for _ in range(counts[j])]


def build_word(qs, delta, s, t, q16, letter):
    """Schedule one all-ones window with a prescribed q_16 and centre letter."""
    qt = tuple(qs[j] + delta[j] for j in range(K))
    if t <= 16:
        extras = tuple(q16[j] - qt[j] for j in range(K))
        rest = expand(tuple(5 - q16[j] for j in range(K)))
        rest.remove(letter)
        return expand(qs) + expand(delta) + expand(extras) + [letter] + rest
    if s >= 16:
        rest = expand(tuple(5 - qt[j] for j in range(K)))
        if s > 16:
            drop = expand(tuple(qs[j] - q16[j] for j in range(K)))
            drop.remove(letter)
            return expand(q16) + [letter] + drop + expand(delta) + rest
        window = expand(delta)
        window.remove(letter)
        return expand(q16) + [letter] + window + rest
    consumed = tuple(q16[j] - qs[j] for j in range(K))
    if t > 16:
        remaining = expand(tuple(delta[j] - consumed[j] for j in range(K)))
        remaining.remove(letter)
        after = expand(tuple(5 - qt[j] for j in range(K)))
        return expand(qs) + expand(consumed) + [letter] + remaining + after
    after = expand(tuple(5 - q16[j] for j in range(K)))
    after.remove(letter)
    return expand(qs) + expand(consumed) + [letter] + after


def feasible_centres(qs, delta, s, t):
    """Count vectors q_16 compatible with the window, and letters available at 16."""
    qt = tuple(qs[j] + delta[j] for j in range(K))
    found = {}

    def add(q16, available):
        if sum(q16) != 16 or any(value < 0 or value > 5 for value in q16):
            fail(f'feasible vector left the cube: {q16}')
        found.setdefault(q16, set()).update(available)

    if t <= 16:
        need = 16 - t
        rooms = [5 - qt[j] for j in range(K)]

        def rec(i, left, acc):
            if i == K - 1:
                if 0 <= left <= rooms[i]:
                    acc[i] = left
                    q16 = tuple(qt[j] + acc[j] for j in range(K))
                    add(q16, [j for j in range(K) if q16[j] < 5])
                return
            for value in range(min(rooms[i], left) + 1):
                acc[i] = value
                rec(i + 1, left - value, acc)

        rec(0, need, [0] * K)
        return found
    if s >= 16:
        need = s - 16

        def rec(i, left, acc):
            if i == K - 1:
                if 0 <= left <= qs[i]:
                    acc[i] = qs[i] - left
                    q16 = tuple(acc)
                    if s > 16:
                        available = [j for j in range(K) if qs[j] - q16[j] > 0]
                    else:
                        available = [j for j in range(K) if delta[j] > 0]
                    add(q16, available)
                return
            for drop in range(min(qs[i], left) + 1):
                acc[i] = qs[i] - drop
                rec(i + 1, left - drop, acc)

        rec(0, need, [0] * K)
        return found
    need = 16 - s

    def rec(i, left, acc):
        if i == K - 1:
            if 0 <= left <= delta[i]:
                acc[i] = left
                consumed = tuple(acc)
                q16 = tuple(qs[j] + consumed[j] for j in range(K))
                if t > 16:
                    available = [j for j in range(K) if delta[j] - consumed[j] > 0]
                else:
                    available = [j for j in range(K) if q16[j] < 5]
                add(q16, available)
            return
        for value in range(min(delta[i], left) + 1):
            acc[i] = value
            rec(i + 1, left - value, acc)

    rec(0, need, [0] * K)
    return found


def extensions(options):
    legal = []
    illegal = []
    for q16, available in options.items():
        good = [letter for letter in available if letter in legal_letters(q16)]
        if good:
            legal.append((q16, min(good)))
        if not legal_letters(q16):
            if available:
                illegal.append((q16, min(available)))
        else:
            bad = [letter for letter in available if letter not in legal_letters(q16)]
            if bad:
                illegal.append((q16, min(bad)))
    return legal, illegal


def weight_masks(word):
    pref = prefixes(word)
    found = set()
    for s in range(LENGTH):
        for t in range(s, LENGTH):
            mask = mask_of(tuple(pref[s][j] + pref[t][j] for j in range(K)))
            if mask is not None and sum(mask) in (2, 6):
                found.add(mask)
    return found


def main():
    # The four types are every pair of counts in 0..5 that sums to 1 or 6.
    found_types = []
    for x in range(C + 1):
        for y in range(x, C + 1):
            if x + y in (1, 6):
                found_types.append((x, y, y - x))
    expected_types = sorted(TYPES.values())
    if sorted(found_types) != expected_types:
        fail(f'coordinate types changed: {found_types}')

    legal_pairs = []
    for counts in itertools.product(range(C + 1), repeat=K):
        if sum(counts) != 16:
            continue
        for letter in legal_letters(counts):
            legal_pairs.append((counts, letter))
    if len(legal_pairs) != 300:
        fail(f'legal centre count changed: {len(legal_pairs)}')
    if any(0 not in counts for counts, _letter in legal_pairs):
        fail('a legal centre has no coordinate 0')
    controls = 0

    near = (3, 3, 3, 3, 3, 1)
    if legal_letters(near):
        fail('near-miss centre was accepted')
    controls += 1

    assignments = 0
    multinomial_total = 0
    class_early = 0
    class_cover = 0
    class_tight = 0
    illegal_only = 0
    both = 0
    legal_only = 0
    no_zero = 0
    zero_but_illegal = 0
    constructed = 0
    for counts in itertools.product(range(7), repeat=4):
        if sum(counts) != K:
            continue
        n_a, n_b, n_c, n_d = counts
        s = n_b + 2 * n_c + 3 * n_d
        d = n_a + 4 * n_b + 2 * n_c
        t = s + d
        if not (0 <= s <= t <= LENGTH - 1) or s + t != 36 - 5 * n_a:
            continue
        ways = math.factorial(K) // (
            math.factorial(n_a) * math.factorial(n_b)
            * math.factorial(n_c) * math.factorial(n_d)
        )
        multinomial_total += ways
        # Human no-zero classes. They are disjoint: a window counted here
        # cannot place a coordinate 0 in q_16, for the reason in README.md.
        if t <= 16:
            class_early += ways
        elif n_a == 0 and s <= 16 <= t:
            class_cover += ways
        elif n_a == n_b == 0 and (n_c, n_d) in ((1, 5), (0, 6)):
            class_tight += ways
        labels = ('A',) * n_a + ('B',) * n_b + ('C',) * n_c + ('D',) * n_d
        for perm in set(itertools.permutations(labels)):
            assignments += 1
            qs = tuple(TYPES[perm[j]][0] for j in range(K))
            delta = tuple(TYPES[perm[j]][2] for j in range(K))
            qt = tuple(qs[j] + delta[j] for j in range(K))
            if any(value > 5 for value in qt):
                fail(f'type assignment exceeded 5: {perm}')
            options = feasible_centres(qs, delta, s, t)
            if not options:
                fail(f'window has no q_16: s={s} t={t} {perm}')
            if any(not available for available in options.values()):
                fail(f'a feasible q_16 has no letter at position 16: s={s} t={t}')
            legal_ext, illegal_ext = extensions(options)
            human_no_zero = (
                t <= 16
                or (n_a == 0 and s <= 16 <= t)
                or (n_a == n_b == 0 and (n_c, n_d) in ((1, 5), (0, 6)))
            )
            enumeration_no_zero = all(0 not in q16 for q16 in options)
            if human_no_zero != enumeration_no_zero:
                fail(f'no-zero class disagreed with the vectors at s={s} t={t} {perm}')
            if enumeration_no_zero:
                no_zero += 1
                if legal_ext:
                    fail('a window with no zero coordinate was called legal')
            if legal_ext and illegal_ext:
                both += 1
                kind = 'both'
            elif illegal_ext and not legal_ext:
                illegal_only += 1
                kind = 'illegal'
                if not enumeration_no_zero:
                    zero_but_illegal += 1
            elif legal_ext:
                legal_only += 1
                kind = 'legal'
            else:
                fail(f'window has no placeable centre letter: s={s} t={t} {perm}')
            for want_legal, choices in ((False, illegal_ext), (True, legal_ext)):
                if not choices:
                    continue
                q16, letter = min(choices)
                word = build_word(qs, delta, s, t, q16, letter)
                pref = prefixes(word)
                if (
                    len(word) != LENGTH
                    or any(word.count(source) != C for source in range(K))
                    or pref[s] != qs
                    or pref[t] != qt
                    or pref[16] != q16
                    or word[16] != letter
                ):
                    fail(f'construction failed for s={s} t={t} {perm}')
                summed = tuple(pref[s][j] + pref[t][j] for j in range(K))
                if summed != tuple(TYPES[perm[j]][0] + TYPES[perm[j]][1] for j in range(K)):
                    fail('all-ones sum drifted')
                if any(value not in (1, 6) for value in summed):
                    fail(f'constructed window is not all-ones: {summed}')
                legal = mask_of(centre_sum(q16, letter)) is not None
                if legal != want_legal:
                    fail(f'polarity failed on a {kind} window')
                constructed += 1

    if assignments != 4095 or multinomial_total != 4095:
        fail(f'assignment count changed: loop {assignments}, multinomial {multinomial_total}')
    if (class_early, class_cover, class_tight) != (845, 721, 7):
        fail(f'human no-zero classes changed: {class_early}, {class_cover}, {class_tight}')
    if (illegal_only, both, legal_only, no_zero, zero_but_illegal, constructed) != (
        2364, 1731, 0, 1573, 791, 5826
    ):
        fail(
            'census counts changed: '
            f'illegal_only={illegal_only} both={both} legal_only={legal_only} '
            f'no_zero={no_zero} zero_but_illegal={zero_but_illegal} '
            f'constructed={constructed}'
        )
    if no_zero != class_early + class_cover + class_tight:
        fail('the enumeration and the human classes count different windows')
    if illegal_only != no_zero + zero_but_illegal:
        fail('illegal windows were not partitioned')
    controls += 1

    # Midpoint all-ones: q_18 is all threes, so q_16 cannot contain a zero.
    midpoint_q = []
    for first in range(K):
        for second in range(first, K):
            q16 = [3] * K
            q16[first] -= 1
            q16[second] -= 1
            midpoint_q.append(tuple(q16))
    if len(midpoint_q) != 21 or any(legal_letters(q16) for q16 in midpoint_q):
        fail('midpoint all-ones no longer forces an illegal centre')
    if any(min(q16) < 1 for q16 in midpoint_q):
        fail('midpoint q_16 acquired a zero')
    controls += 1

    # Weight identity: sum 33 admits only weight 3 inside the allowed alphabet.
    for values in itertools.product(ALLOWED, repeat=K):
        weight = sum(MASK_BIT[value] for value in values)
        if sum(values) % C != weight % C:
            fail(f'weight identity failed on {values}')
    if any(weight % C == 3 for weight in (0, 1, 2, 4, 5, 6)):
        fail('another weight in 0..6 is congruent to 3')
    controls += 1

    def require_floor(text):
        word = [int(ch) for ch in text]
        if len(word) != LENGTH or any(word.count(source) != C for source in range(K)):
            fail(f'witness is not a floor word: {text}')
        return word

    # Sorted staircase: every pair of blocks realizes one weight-2 mask.
    sorted_word = require_floor(SORTED)
    sorted_pref = prefixes(sorted_word)
    staircase = set()
    for left in range(K):
        for right in range(left + 1, K):
            s = 5 * left + 1
            t = 5 * right + 1
            summed = tuple(sorted_pref[s][j] + sorted_pref[t][j] for j in range(K))
            mask = mask_of(summed)
            if mask is None or sum(mask) != 2 or mask[left] != 1 or mask[right] != 1:
                fail(f'staircase missed {(left, right)} at {(s, t)} sum {summed}')
            staircase.add(mask)
    if len(staircase) != 15:
        fail(f'staircase realized {len(staircase)} masks')
    sorted_centre = centre_sum(sorted_pref[16], sorted_word[16])
    if sorted_pref[16] != (5, 5, 5, 1, 0, 0) or sorted_centre != (10, 10, 10, 3, 0, 0):
        fail(f'sorted centre changed: {sorted_pref[16]} {sorted_centre}')
    if mask_of(sorted_centre) is not None:
        fail('sorted centre became legal')
    if weight_masks(sorted_word) != staircase:
        fail('sorted word realizes a weight-2 or weight-6 mask outside the staircase')
    controls += 1

    swapped = sorted_word[:]
    swapped[0], swapped[5] = swapped[5], swapped[0]
    swapped_masks = weight_masks(swapped)
    if len([mask for mask in swapped_masks if sum(mask) == 2]) >= 15:
        fail('swapping the sorted word kept every weight-2 mask')
    controls += 1

    legal_word = require_floor(WEIGHT2_LEGAL)
    legal_pref = prefixes(legal_word)
    legal_found = weight_masks(legal_word)
    if sum(1 for mask in legal_found if sum(mask) == 2) != 15:
        fail('legal-centre weight-2 witness missed a mask')
    if any(sum(mask) == 6 for mask in legal_found):
        fail('legal-centre weight-2 witness realized weight 6')
    legal_centre = centre_sum(legal_pref[16], legal_word[16])
    if legal_pref[16] != (3, 5, 5, 3, 0, 0) or legal_word[16] != 4:
        fail(f'weight-2 legal prefixes changed: {legal_pref[16]} letter {legal_word[16]}')
    legal_mask = mask_of(legal_centre)
    if legal_centre != (6, 10, 10, 6, 1, 0) or legal_mask is None or sum(legal_mask) != 3:
        fail(f'weight-2 legal centre changed: {legal_centre}')
    controls += 1

    weight6 = require_floor(WEIGHT6_LEGAL)
    weight6_pref = prefixes(weight6)
    pair = tuple(weight6_pref[4][j] + weight6_pref[22][j] for j in range(K))
    if pair != (6, 6, 6, 6, 1, 1) or any(value not in (1, 6) for value in pair):
        fail(f'weight-6 legal window changed: {pair}')
    weight6_centre = centre_sum(weight6_pref[16], weight6[16])
    if weight6_pref[16] != (5, 3, 3, 5, 0, 0) or weight6[16] != 4:
        fail(f'weight-6 legal prefixes changed: {weight6_pref[16]}')
    if weight6_centre != (10, 6, 6, 10, 1, 0) or mask_of(weight6_centre) is None:
        fail(f'weight-6 legal centre changed: {weight6_centre}')
    # Same window, opposite centre. Types are read off the witness prefixes.
    qs = weight6_pref[4]
    qt = weight6_pref[22]
    delta = tuple(qt[j] - qs[j] for j in range(K))
    _legal_ext, illegal_ext = extensions(feasible_centres(qs, delta, 4, 22))
    if not illegal_ext:
        fail('the exhibited flexible window has no illegal extension')
    q16, letter = min(illegal_ext)
    twin = build_word(qs, delta, 4, 22, q16, letter)
    if ''.join(str(letter) for letter in twin) != WEIGHT6_TWIN:
        fail('illegal twin of the flexible window changed')
    twin_pref = prefixes(twin)
    if twin_pref[4] != qs or twin_pref[22] != qt:
        fail('illegal twin lost the flexible all-ones window')
    if mask_of(centre_sum(twin_pref[16], twin[16])) is not None:
        fail('illegal twin centre became legal')
    controls += 1

    joint = require_floor(JOINT)
    joint_pref = prefixes(joint)
    joint_pair = tuple(2 * joint_pref[18][j] for j in range(K))
    if joint_pref[18] != (3, 3, 3, 3, 3, 3) or joint_pair != (6, 6, 6, 6, 6, 6):
        fail(f'joint witness is not all-ones at (18, 18): {joint_pref[18]}')
    joint_centre = centre_sum(joint_pref[16], joint[16])
    if joint_centre != (6, 4, 6, 5, 6, 6) or mask_of(joint_centre) is not None:
        fail(f'joint centre changed: {joint_centre}')
    joint_found = weight_masks(joint)
    missing = tuple(sorted(
        mask for mask in itertools.product((0, 1), repeat=K)
        if sum(mask) in (2, 6) and mask not in joint_found
    ))
    if missing != JOINT_MISSING:
        fail(f'joint missing masks changed: {missing}')
    if sum(1 for mask in joint_found if sum(mask) == 2) != 13:
        fail('joint witness no longer realizes 13 weight-2 masks')
    controls += 1

    print(
        'PASS_C5_MASK_CENTRE_NONDETERMINATION '
        f'assignments=4095 illegal_only={illegal_only} both={both} '
        f'legal_only={legal_only} no_zero={no_zero} '
        f'zero_but_illegal={zero_but_illegal} '
        f'classes={class_early}+{class_cover}+{class_tight} '
        f'constructed={constructed} midpoint_q16=21 '
        f'weight2_polarities=2 weight6_forces_legal=0 '
        f'joint_weight2=13 joint_missing=2 controls={controls}'
    )


if __name__ == '__main__':
    main()
