#!/usr/bin/env python3
"""Adjacent swaps of the PR #7041 block word miss the weight-1 mask (4).

The word is 3,5,0,1, 2^7, 4^7, 0^6, 1^6, 3^6, 5^6. Swapping string
indices 17 and 18 exchanges the last 4 with the following 0. Every
adjacent transposition, including that one, is checked. Evidence class:
exhaustive finite census of a 42-letter word and its 41 adjacent
transpositions. Not a search over floor words, and not a kappa change.
"""

K = 6
C = 7
LENGTH = 42
BLOCKS = (
    (3, 1),
    (5, 1),
    (0, 1),
    (1, 1),
    (2, 7),
    (4, 7),
    (0, 6),
    (1, 6),
    (3, 6),
    (5, 6),
)
LITERAL = "350122222224444444000000111111333333555555"
NAMED_INDEX = 17
ALLOWED = {0: 0, 1: 1, 7: 0, 8: 1, 14: 0}
MASK4 = (0, 0, 0, 0, 1, 0)
PAIR_COUNT = LENGTH * (LENGTH + 1) // 2
# The nine places where consecutive letters differ. Each row is
# (index, left letter, right letter, changed prefix q'_{index+1}).
BOUNDARIES = (
    (0, 3, 5, (0, 0, 0, 0, 0, 1)),
    (1, 5, 0, (1, 0, 0, 1, 0, 0)),
    (2, 0, 1, (0, 1, 0, 1, 0, 1)),
    (3, 1, 2, (1, 0, 1, 1, 0, 1)),
    (10, 2, 4, (1, 1, 6, 1, 1, 1)),
    (17, 4, 0, (2, 1, 7, 1, 6, 1)),
    (23, 0, 1, (6, 2, 7, 1, 7, 1)),
    (29, 1, 3, (7, 6, 7, 2, 7, 1)),
    (35, 3, 5, (7, 7, 7, 6, 7, 2)),
)
NAMED_CHANGED = (
    ((0, 18), (1, 1, 0, 1, 0, 1), None, (2, 1, 7, 1, 6, 1)),
    ((18, 41), (1, 1, 0, 1, 0, 0), None, (9, 8, 14, 8, 13, 7)),
)
# Arithmetic targets that would read as mask (4) against q'_18.
CANDIDATES = (
    (25, (5, 6, 0, 6, 2, 6)),
    (32, (5, 6, 7, 6, 2, 6)),
)


def fail(message):
    raise SystemExit("FAIL: " + message)


def expand(blocks):
    letters = []
    for source, count in blocks:
        if source not in range(K) or count < 1:
            fail("bad block %s" % ((source, count),))
        letters.extend([source] * count)
    return tuple(letters)


def prefix_table(letters):
    if len(letters) != LENGTH or any(letter not in range(K) for letter in letters):
        fail("not a length-42 word on sources 0..5")
    running = [0] * K
    table = [tuple(running)]
    for letter in letters:
        running[letter] += 1
        table.append(tuple(running))
    if table[-1] != (C,) * K:
        fail("final count is not seven calls of each source")
    if any(letters.count(source) != C for source in range(K)):
        fail("not a floor word")
    return tuple(table)


def add(left, right):
    return tuple(left[source] + right[source] for source in range(K))


def readings(total):
    """Mask from {0,1,7,8,14}, or None when a coordinate is outside it.

    The residue reading modulo 7 must agree. A disagreement is a predicate
    failure, not a choice of reading.
    """
    allowed_bits = []
    modular_bits = []
    allowed_ok = True
    modular_ok = True
    for value in total:
        if value not in ALLOWED:
            allowed_ok = False
        else:
            allowed_bits.append(ALLOWED[value])
        residue = value % C
        if residue not in (0, 1):
            modular_ok = False
        else:
            modular_bits.append(residue)
    allowed_mask = tuple(allowed_bits) if allowed_ok else None
    modular_mask = tuple(modular_bits) if modular_ok else None
    if allowed_mask != modular_mask:
        fail("allowed-set and mod-7 readings disagree on " + str(total))
    return allowed_mask


def mask4_hits(table):
    hits = []
    examined = 0
    for left in range(LENGTH):
        for right in range(left, LENGTH):
            examined += 1
            total = add(table[left], table[right])
            mask = readings(total)
            if mask is None:
                continue
            weight = sum(mask)
            if (left + right - weight) % C:
                fail("weight identity failed at %s mask %s" % ((left, right), mask))
            if mask == MASK4:
                hits.append((left, right, total))
    if examined != PAIR_COUNT:
        fail("visited %s pairs, expected %s" % (examined, PAIR_COUNT))
    return tuple(hits)


def changed_readings(original, swapped):
    rows = []
    for left in range(LENGTH):
        for right in range(left, LENGTH):
            before = readings(add(original[left], original[right]))
            after_total = add(swapped[left], swapped[right])
            after = readings(after_total)
            if before != after:
                rows.append(((left, right), before, after, after_total))
    return tuple(rows)


def swap(letters, index):
    if not 0 <= index < LENGTH - 1:
        fail("swap index %s is outside 0..40" % index)
    swapped = list(letters)
    swapped[index], swapped[index + 1] = swapped[index + 1], swapped[index]
    return tuple(swapped)


def check_word(done):
    letters = expand(BLOCKS)
    literal = "".join(str(source) for source in letters)
    if literal != LITERAL:
        fail("block literal changed")
    if len(BOUNDARIES) != 9:
        fail("boundary table length changed")
    seen = []
    for index, left, right, _prefix in BOUNDARIES:
        if letters[index] != left or letters[index + 1] != right or left == right:
            fail("boundary %s is not letters %s,%s" % (index, left, right))
        seen.append(index)
    computed = [index for index in range(LENGTH - 1) if letters[index] != letters[index + 1]]
    if computed != seen:
        fail("boundaries are %s, word has %s" % (seen, computed))
    if letters[NAMED_INDEX] != 4 or letters[NAMED_INDEX + 1] != 0:
        fail("index 17 is not the last 4 followed by 0")
    # Seven 4s occupy indices 11..17, so 17 is the last one.
    if letters[11:18] != (4,) * 7 or letters[18:24] != (0,) * 6:
        fail("the 4-block or the following 0-block moved")
    table = prefix_table(letters)
    if mask4_hits(table):
        fail("the unswapped word already realizes mask (4)")
    done.append("floor-word")
    return letters, table


def check_named_obstruction(letters, table, done):
    swapped_letters = swap(letters, NAMED_INDEX)
    swapped = prefix_table(swapped_letters)
    if "".join(str(source) for source in swapped_letters) != "350122222224444440400000111111333333555555":
        fail("named swap literal changed")
    diffs = [index for index in range(LENGTH + 1) if table[index] != swapped[index]]
    if diffs != [NAMED_INDEX + 1]:
        fail("named swap moves prefixes %s" % (diffs,))
    expected = (2, 1, 7, 1, 6, 1)
    manual = tuple(
        table[18][source] + (1 if source == 0 else -1 if source == 4 else 0)
        for source in range(K)
    )
    if swapped[18] != expected or manual != expected:
        fail("q'_18 is %s, not q_18 - e_4 + e_0" % (swapped[18],))
    for endpoint, vector in CANDIDATES:
        if sum(vector) != endpoint:
            fail("candidate %s does not sum to its index" % (vector,))
        total = add(expected, vector)
        if readings(total) != MASK4:
            fail("candidate sum %s does not read as mask (4)" % (total,))
        if table[endpoint][0] != C or table[endpoint][4] != C:
            fail("q_%s does not have sources 0 and 4 equal to 7" % endpoint)
        if table[endpoint] == vector or swapped[endpoint] == vector:
            fail("candidate %s occurs as a prefix" % (vector,))
        # These indices are not 18, so the swapped word keeps the original prefix.
        if swapped[endpoint] != table[endpoint]:
            fail("candidate index %s was moved by the named swap" % endpoint)
    double = add(expected, expected)
    if readings(double) == MASK4 or double[4] in (1, 8):
        fail("the doubled changed prefix reads as mask (4)")
    incident = []
    for other in range(LENGTH):
        left, right = sorted((18, other))
        total = add(swapped[left], swapped[right])
        if readings(total) == MASK4:
            incident.append((left, right, total))
    if incident:
        fail("an incident pair realizes mask (4): %s" % (incident,))
    if len({(18, other) for other in range(LENGTH)}) != LENGTH:
        fail("incident endpoint count changed")
    hits = mask4_hits(swapped)
    if hits:
        fail("named swap realizes mask (4) at %s" % (hits,))
    changed = changed_readings(table, swapped)
    if changed != NAMED_CHANGED:
        fail("named reading changes are %s" % (changed,))
    done.append("named-obstruction")
    return swapped


def check_adjacent(letters, table, done):
    nontrivial = 0
    identities = 0
    for index in range(LENGTH - 1):
        swapped_letters = swap(letters, index)
        if letters[index] == letters[index + 1]:
            if swapped_letters != letters:
                fail("equal-letter swap at %s changed the word" % index)
            identities += 1
            continue
        nontrivial += 1
        swapped = prefix_table(swapped_letters)
        diffs = [point for point in range(LENGTH + 1) if table[point] != swapped[point]]
        if diffs != [index + 1]:
            fail("swap %s moves prefixes %s" % (index, diffs))
        left, right = letters[index], letters[index + 1]
        manual = list(table[index + 1])
        manual[left] -= 1
        manual[right] += 1
        if swapped[index + 1] != tuple(manual):
            fail("swap %s prefix is not q - e_%s + e_%s" % (index, left, right))
        row = next(item for item in BOUNDARIES if item[0] == index)
        if row[3] != swapped[index + 1]:
            fail("recorded prefix at %s is %s, computed %s" % (index, row[3], swapped[index + 1]))
        hits = mask4_hits(swapped)
        if hits:
            fail("adjacent swap %s realizes mask (4) at %s" % (index, hits))
    if nontrivial != 9 or identities != 32:
        fail("split is boundaries %s identities %s" % (nontrivial, identities))
    done.append("adjacent-census")


def check_controls(done):
    if readings((0, 0, 0, 0, 1, 0)) != MASK4:
        fail("unit source-4 sum does not read as mask (4)")
    if readings((0, 0, 0, 0, 8, 0)) != MASK4:
        fail("coordinate 8 does not read as mask (4)")
    if readings((2, 1, 7, 1, 6, 1)) is not None:
        fail("the changed prefix itself was accepted as a reading")
    if readings((7, 7, 7, 7, 8, 7)) != MASK4:
        fail("the first arithmetic target lost mask (4)")
    if readings((7, 7, 14, 7, 8, 7)) != MASK4:
        fail("the second arithmetic target lost mask (4)")
    # 2 is outside the allowed set and is not 0 or 1 mod 7, so both readings reject.
    if readings((0, 0, 0, 0, 2, 0)) is not None:
        fail("coordinate 2 was accepted")
    # 15 is 1 mod 7 but not in the allowed set, so the two readings split.
    try:
        readings((0, 0, 0, 0, 15, 0))
    except SystemExit as exc:
        if "disagree" not in str(exc):
            fail("coordinate 15 failed for the wrong reason: %s" % exc)
    else:
        fail("coordinate 15 did not split the two readings")
    done.append("predicate-controls")


def main():
    done = []
    letters, table = check_word(done)
    check_named_obstruction(letters, table, done)
    check_adjacent(letters, table, done)
    check_controls(done)
    expected = ["floor-word", "named-obstruction", "adjacent-census", "predicate-controls"]
    if done != expected:
        fail("checks finished as %s" % (done,))
    print(
        "PASS_SIX_SOURCE_C7_BOUNDARY_SWAP_MASK4 "
        "pairs=903 boundaries=9 identities=32 named_index=17 "
        "mask4_pairs=0 adjacent_mask4_pairs=0 changed_readings=2 "
        "positive_targets=2 controls=4 no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
