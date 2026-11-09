#!/usr/bin/env python3
"""Finite check of the c=7 diagonal equality obstruction.

The written argument is in README.md. This program exhausts the centre
classification and the one-step move table that the argument uses, and it
rejects four near-miss controls. It does not search words.
"""
import itertools

K = 6
C = 7
ALLOWED = (0, 1, 7, 8, 14)
MASK_BIT = {0: 0, 1: 1, 7: 0, 8: 1, 14: 0}


def fail(msg):
    raise SystemExit('FAIL: ' + msg)


def weight3(sum_vec):
    """True when every coordinate lies in ALLOWED and exactly three are mask bits."""
    bits = 0
    for value in sum_vec:
        if value not in MASK_BIT:
            return False
        bits += MASK_BIT[value]
    return bits == 3


def centre_realizations():
    """Every q_22 and centre letter whose pair (q_22, q_22+e_c) is weight 3."""
    found = []
    for counts in itertools.product(range(C + 1), repeat=K):
        if sum(counts) != 22:
            continue
        for centre in range(K):
            if counts[centre] >= C:
                continue
            total = [counts[j] + (1 if j == centre else 0) for j in range(K)]
            summed = [counts[j] + total[j] for j in range(K)]
            if weight3(summed):
                found.append((counts, centre, summed))
    return found


def main():
    found = centre_realizations()
    if len(found) != 300:
        fail(f'expected 300 weight-3 centre realizations, found {len(found)}')
    frozen = 0
    type01 = 0
    type31 = 0
    for counts, centre, summed in found:
        n14 = 0
        for j, value in enumerate(summed):
            if value == 14:
                # Both sides of a 14 are exactly 7, so the centre letter is elsewhere.
                if counts[j] != 7 or counts[j] + (j == centre) != 7:
                    fail(f'14 is not a pair of sevens: q={counts} centre={centre}')
                n14 += 1
                frozen += 1
        if counts[centre] == 0 and summed[centre] == 1 and n14 == 2:
            type01 += 1
        elif counts[centre] == 3 and summed[centre] == 7 and n14 == 1:
            type31 += 1
        else:
            fail(
                f'unexpected centre type: q={counts} centre={centre} '
                f'sum={summed} fourteens={n14}'
            )
    # Type (0,1) freezes two coordinates and type (3,1) freezes one: 2*180+120=480.
    if type01 != 180 or type31 != 120 or frozen != 480:
        fail(
            f'expected type01=180 type31=120 frozen=480, '
            f'found {type01}, {type31}, {frozen}'
        )

    # Move table: a coordinate equal to 14 cannot be the unique +1 or -1 of a step.
    increments = [v for v in ALLOWED if v + 1 in ALLOWED]
    decrements = [v for v in ALLOWED if v - 1 in ALLOWED]
    if increments != [0, 7] or decrements != [1, 8]:
        fail(f'move table changed: +{increments} -{decrements}')
    if 14 in increments or 14 in decrements:
        fail('14 is movable')

    controls = 0
    # Near-miss centre: five 4s and a 2 sum to 22, but 2+2+1 is not an allowed value.
    near = (4, 4, 4, 4, 4, 2)
    near_sum = [2 * near[j] + (1 if j == 5 else 0) for j in range(K)]
    if weight3(near_sum):
        fail('near-miss centre was accepted')
    controls += 1
    # All-lambda-one cannot occur: every non-centre coordinate would need mask bit 1.
    if any(14 not in summed for _, _, summed in found):
        fail('all-lambda-one centre exists')
    controls += 1
    # Decrementing 14 leaves the allowed set.
    if 13 in ALLOWED:
        fail('13 became allowed')
    controls += 1
    # A length-4 prefix cannot already contain a finished source.
    for prefix in itertools.product(range(C + 1), repeat=K):
        if sum(prefix) == 4 and max(prefix) >= 7:
            fail('length-4 prefix contains a 7')
    controls += 1

    print(
        'PASS_SIX_SOURCE_C7_DIAGONAL_OBSTRUCTION '
        f'centres=300 type01={type01} type31={type31} '
        f'frozen_coordinates={frozen} '
        f'moves=+{increments}/-{decrements} controls={controls}'
    )


if __name__ == '__main__':
    main()
