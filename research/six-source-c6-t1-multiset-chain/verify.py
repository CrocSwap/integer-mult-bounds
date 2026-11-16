#!/usr/bin/env python3
"""Witness that one c=6 floor word keeps the multiset (6,6,6,7,7,7).

The written argument is in README.md. This program exhausts the endpoint
split domains and checks the constant-mask family together with one
mask-changing word. It does not search depth-two words and it does not
call a SAT solver.
"""
import itertools
from collections import Counter

K = 6
C = 6
LENGTH = K * C
TARGET = (6, 6, 6, 7, 7, 7)
TARGET_COUNT = Counter(TARGET)
ALLOWED = {0, 1, 6, 7, 12}
MASK_BIT = {0: 0, 1: 1, 6: 0, 7: 1, 12: 0}

# Displayed witnesses. Both are rebuilt by the constructors below.
CONSTANT_WORD = "012300112233444555012555444332211003"
MOVING_WORD = "012340011223344555014555443322110023"


def fail(message):
    raise SystemExit("FAIL: " + message)


def digits(word):
    return [int(character) for character in word]


def prefix_counts(word, length):
    counts = [0] * K
    for source in word[:length]:
        counts[source] += 1
    return counts


def diagonal_sum(word, index):
    early = prefix_counts(word, index)
    late = prefix_counts(word, 39 - index)
    return tuple(early[j] + late[j] for j in range(K))


def is_floor(word):
    if len(word) != LENGTH:
        return False
    counts = prefix_counts(word, LENGTH)
    return counts == [C] * K


def weight3(sum_vec):
    bits = 0
    for value in sum_vec:
        if value not in ALLOWED:
            return False
        bits += MASK_BIT[value]
    return bits == 3


def keeps_multiset(word):
    if not is_floor(word):
        return False
    for index in range(4, 19):
        if Counter(diagonal_sum(word, index)) != TARGET_COUNT:
            return False
    return True


def mask_of(sum_vec):
    return tuple(source for source, value in enumerate(sum_vec) if value == 7)


def constant_mask_word(mask, deficit):
    """Pure-slide word whose diagonal mask is `mask` at every s=4..18."""
    chosen = tuple(sorted(mask))
    if len(chosen) != 3 or len(set(chosen)) != 3 or deficit not in range(K):
        fail(f"bad constant-mask parameters {mask} {deficit}")
    complement = [source for source in range(K) if source not in chosen]
    if deficit in chosen:
        others = [source for source in chosen if source != deficit]
        prefix = [deficit, deficit, others[0], others[1]]
        early = [deficit]
        for source in others:
            early.extend((source, source))
        for source in complement:
            early.extend((source, source, source))
    else:
        carriers = sorted(list(chosen) + [deficit])
        prefix = list(carriers)
        early = []
        for source in carriers:
            early.extend((source, source))
        for source in complement:
            if source != deficit:
                early.extend((source, source, source))
    bridge = list(chosen)
    late = list(reversed(early))
    word = prefix + early + bridge + late + [deficit]
    if (len(prefix), len(early), len(bridge), len(late), len(word)) != (4, 14, 3, 14, 36):
        fail(f"block lengths changed for mask {chosen} deficit {deficit}")
    return word


def moving_word():
    """One slide-free first step, then thirteen slides.

    The mask is {0,1,2} at s=4 and {0,1,4} at s=5..18.
    """
    prefix = [0, 1, 2, 3]
    rest = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5]
    early = [4] + rest
    late = list(reversed(rest)) + [2]
    bridge = [0, 1, 4]
    return prefix + early + bridge + late + [3]


def layered_slot_word():
    """A floor word with the T1 count pair at s=18 and a different s=4 sum."""
    word = []
    for counts in ((3, 3, 3, 3, 3, 3), (1, 1, 1, 0, 0, 0), (2, 2, 2, 3, 3, 3)):
        for source, count in enumerate(counts):
            word.extend([source] * count)
    return word


def legal_rows():
    rows = []
    for early in range(C + 1):
        for bridge in range(4):
            if early + bridge <= C and (2 * early + bridge) in (6, 7):
                rows.append((early, bridge, 2 * early + bridge))
    return rows


def main():
    controls = 0

    rows = legal_rows()
    if rows != [(2, 2, 6), (2, 3, 7), (3, 0, 6), (3, 1, 7)]:
        fail(f"local row table changed: {rows}")
    controls += 1

    splits18 = 0
    for choice in itertools.product(rows, repeat=K):
        if sum(row[0] for row in choice) != 18:
            continue
        if sum(row[1] for row in choice) != 3:
            continue
        summed = tuple(row[2] for row in choice)
        if Counter(summed) != TARGET_COUNT:
            continue
        splits18 += 1
        if sorted(row[:2] for row in choice) != [(3, 0), (3, 0), (3, 0), (3, 1), (3, 1), (3, 1)]:
            fail(f"unexpected s=18 split: {choice}")
    if splits18 != 20:
        fail(f"s=18 split count changed: {splits18}")
    controls += 1

    type_a = 0
    type_b = 0
    other = 0
    domain4 = 0
    vectors4 = 0
    for early in itertools.product(range(C + 1), repeat=K):
        if sum(early) != 4:
            continue
        vectors4 += 1
        for deficit in range(K):
            domain4 += 1
            summed = tuple(early[source] + (5 if source == deficit else 6) for source in range(K))
            if Counter(summed) != TARGET_COUNT:
                continue
            mask = mask_of(summed)
            expected_a = tuple(1 if source in mask or source == deficit else 0 for source in range(K))
            expected_b = tuple(2 if source == deficit else 1 if source in mask else 0 for source in range(K))
            if deficit not in mask and early == expected_a:
                type_a += 1
            elif deficit in mask and early == expected_b:
                type_b += 1
            else:
                other += 1
    if (vectors4, domain4, type_a, type_b, other) != (126, 756, 60, 60, 0):
        fail(
            "s=4 split census changed: "
            f"vectors={vectors4} domain={domain4} A={type_a} B={type_b} other={other}"
        )
    controls += 1

    family_a = 0
    family_b = 0
    for mask in itertools.combinations(range(K), 3):
        for deficit in range(K):
            word = constant_mask_word(mask, deficit)
            if not is_floor(word):
                fail(f"constant-mask word is not a floor word: {mask} {deficit}")
            if any(word[4 + step] != word[34 - step] for step in range(14)):
                fail(f"constant-mask word is not a pure slide: {mask} {deficit}")
            if prefix_counts(word, 18) != [3] * K:
                fail(f"q_18 moved off 3: {mask} {deficit}")
            for index in range(4, 19):
                summed = diagonal_sum(word, index)
                expected = tuple(7 if source in mask else 6 for source in range(K))
                if summed != expected:
                    fail(f"constant mask drifted at s={index}: {mask} {deficit} {summed}")
            if deficit in mask:
                family_b += 1
            else:
                family_a += 1
    if (family_a, family_b) != (60, 60):
        fail(f"constant-mask family split changed: A={family_a} B={family_b}")
    controls += 1

    displayed = constant_mask_word((0, 1, 2), 3)
    broken = list(displayed)
    broken[21:35] = displayed[4:18]
    if not is_floor(broken):
        fail("reordered late block stopped being a floor word")
    broken_sum = diagonal_sum(broken, 5)
    if keeps_multiset(broken) or 8 not in broken_sum:
        fail(f"reordered late block still looked legal: {broken_sum}")
    controls += 1

    layered = layered_slot_word()
    if not is_floor(layered):
        fail("layered T1 slot word is not a floor word")
    layered_18 = diagonal_sum(layered, 18)
    layered_4 = diagonal_sum(layered, 4)
    if Counter(layered_18) != TARGET_COUNT or prefix_counts(layered, 18) != [3] * K:
        fail(f"layered word lost the T1 slot: {layered_18}")
    if Counter(layered_4) == TARGET_COUNT or keeps_multiset(layered):
        fail(f"layered slot word unexpectedly kept the chain: {layered_4}")
    controls += 1

    moving = moving_word()
    if "".join(str(source) for source in moving) != MOVING_WORD:
        fail("moving word string drifted")
    if not keeps_multiset(moving):
        fail("moving word lost the multiset")
    masks = [mask_of(diagonal_sum(moving, index)) for index in range(4, 19)]
    if masks[0] != (0, 1, 2) or any(item != (0, 1, 4) for item in masks[1:]):
        fail(f"moving mask pattern changed: {masks}")
    if moving[4] == moving[34] or any(moving[5 + step] != moving[33 - step] for step in range(13)):
        fail("moving word step pattern changed")
    controls += 1

    if "".join(str(source) for source in displayed) != CONSTANT_WORD:
        fail("constant word string drifted")
    prefix9 = tuple(prefix_counts(displayed, 9))
    if prefix9 != (3, 3, 2, 1, 0, 0) or weight3(prefix9):
        fail(f"displayed word met the (0, 9) shape: {prefix9}")
    controls += 1

    over_called = [0] * 7 + [1] * 6 + [2] * 6 + [3] * 6 + [4] * 6 + [5] * 5
    if len(over_called) != LENGTH or is_floor(over_called) or keeps_multiset(over_called):
        fail("seven calls of one source were accepted")
    controls += 1

    if sum(TARGET) != 39 or not weight3(TARGET):
        fail("target multiset is not a weight-3 sum of 39")
    for index in range(4, 18):
        current = diagonal_sum(moving, index)
        step = diagonal_sum(moving, index + 1)
        predicted = list(current)
        predicted[moving[index]] += 1
        predicted[moving[38 - index]] -= 1
        if tuple(predicted) != step:
            fail(f"one-step identity failed at s={index}")
    controls += 1

    if controls != 10:
        fail(f"control count changed: {controls}")
    print(
        "PASS_SIX_SOURCE_C6_T1_MULTISET_CHAIN "
        f"rows=4 splits18={splits18} splits4={type_a + type_b} "
        f"domain4={domain4} constant_words={family_a + family_b} "
        f"moving_mask_changes=1 controls={controls}"
    )


if __name__ == "__main__":
    main()
