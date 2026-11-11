#!/usr/bin/env python3
"""The other 61 nonzero masks on the PR #7041 block word.

The word is 3,5,0,1, 2^7, 4^7, 0^6, 1^6, 3^6, 5^6. Every pair
0 <= s <= t <= 41 is read with the same predicate as PR #7041.
The two named targets stay in the census as a predicate control.
The claim is the realized/missed split of the other 61 masks.

Evidence class: exhaustive finite census of the 63 nonzero masks on
this one word, plus a direct level-set argument that the weight-6 mask
is missed. Not a census of floor words, and not a selected-kappa change.
"""

K = 6
C = 7
LENGTH = 42
LITERAL = "350122222224444444000000111111333333555555"
WITNESS = "023514103524310254054123145203452034213150"
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
ALLOWED = {0: 0, 1: 1, 7: 0, 8: 1, 14: 0}
PAIR_COUNT = LENGTH * (LENGTH + 1) // 2
FULL = (1, 1, 1, 1, 1, 1)
# Pair sets recorded by PR #7041 for the two named targets.
TARGET_PAIRS = {
    (3, 5): ((0, 2), (0, 30), (1, 36)),
    (0, 1, 3, 5): ((0, 4), (0, 11), (0, 18)),
}
# Exact realizing pairs of the other 11 masks, with the prefix sums.
OTHER_HITS = {
    (3,): (
        ((0, 1), (0, 0, 0, 1, 0, 0)),
        ((2, 41), (7, 7, 7, 8, 7, 7)),
        ((30, 41), (14, 14, 14, 8, 14, 7)),
    ),
    (5,): (
        ((0, 36), (7, 7, 7, 7, 7, 1)),
        ((1, 35), (7, 7, 7, 7, 7, 1)),
        ((37, 41), (14, 14, 14, 14, 14, 8)),
        ((38, 40), (14, 14, 14, 14, 14, 8)),
        ((39, 39), (14, 14, 14, 14, 14, 8)),
    ),
    (0, 3): (
        ((3, 41), (8, 7, 7, 8, 7, 7)),
    ),
    (1, 3): (
        ((24, 41), (14, 8, 14, 8, 14, 7)),
    ),
    (0, 3, 5): (
        ((0, 3), (1, 0, 0, 1, 0, 1)),
    ),
    (1, 3, 5): (
        ((0, 24), (7, 1, 7, 1, 7, 1)),
    ),
    (0, 1, 3): (
        ((4, 41), (8, 8, 7, 8, 7, 7)),
        ((11, 41), (8, 8, 14, 8, 7, 7)),
        ((18, 41), (8, 8, 14, 8, 14, 7)),
    ),
    (0, 1, 2, 3): (
        ((5, 41), (8, 8, 8, 8, 7, 7)),
    ),
    (0, 1, 3, 4): (
        ((12, 41), (8, 8, 14, 8, 8, 7)),
    ),
    (0, 1, 2, 3, 5): (
        ((0, 5), (1, 1, 1, 1, 0, 1)),
    ),
    (0, 1, 3, 4, 5): (
        ((0, 12), (1, 1, 7, 1, 1, 1)),
    ),
}
# The two targets, with the same sums, kept only as a predicate control.
TARGET_HITS = {
    (3, 5): (
        ((0, 2), (0, 0, 0, 1, 0, 1)),
        ((0, 30), (7, 7, 7, 1, 7, 1)),
        ((1, 36), (7, 7, 7, 8, 7, 1)),
    ),
    (0, 1, 3, 5): (
        ((0, 4), (1, 1, 0, 1, 0, 1)),
        ((0, 11), (1, 1, 7, 1, 0, 1)),
        ((0, 18), (1, 1, 7, 1, 7, 1)),
    ),
}
MISSED = (
    (0,),
    (1,),
    (2,),
    (4,),
    (0, 1),
    (0, 2),
    (0, 4),
    (0, 5),
    (1, 2),
    (1, 4),
    (1, 5),
    (2, 3),
    (2, 4),
    (2, 5),
    (3, 4),
    (4, 5),
    (0, 1, 2),
    (0, 1, 4),
    (0, 1, 5),
    (0, 2, 3),
    (0, 2, 4),
    (0, 2, 5),
    (0, 3, 4),
    (0, 4, 5),
    (1, 2, 3),
    (1, 2, 4),
    (1, 2, 5),
    (1, 3, 4),
    (1, 4, 5),
    (2, 3, 4),
    (2, 3, 5),
    (2, 4, 5),
    (3, 4, 5),
    (0, 1, 2, 4),
    (0, 1, 2, 5),
    (0, 1, 4, 5),
    (0, 2, 3, 4),
    (0, 2, 3, 5),
    (0, 2, 4, 5),
    (0, 3, 4, 5),
    (1, 2, 3, 4),
    (1, 2, 3, 5),
    (1, 2, 4, 5),
    (1, 3, 4, 5),
    (2, 3, 4, 5),
    (0, 1, 2, 3, 4),
    (0, 1, 2, 4, 5),
    (0, 2, 3, 4, 5),
    (1, 2, 3, 4, 5),
    (0, 1, 2, 3, 4, 5),
)
ZERO_PAIRS = (
    ((0, 0), (0, 0, 0, 0, 0, 0)),
    ((36, 41), (14, 14, 14, 14, 14, 7)),
    ((37, 40), (14, 14, 14, 14, 14, 7)),
    ((38, 39), (14, 14, 14, 14, 14, 7)),
)
MISSED_BY_WEIGHT = {1: 4, 2: 12, 3: 17, 4: 12, 5: 4, 6: 1}
LATE_FULL_OBSTRUCTION = ((37, 41), (38, 40), (39, 39))
CONTROLS = (
    "floor-word",
    "closed-form",
    "hand-sums",
    "pair-scan",
    "target-controls",
    "other-61",
    "zero-pairs",
    "weight-six",
    "rejected-edit",
    "rejected-inventory",
)


def fail(message):
    raise SystemExit("FAIL: " + message)


def support(mask):
    return tuple(index for index, bit in enumerate(mask) if bit)


def mask_of(support_indices):
    bits = [0] * K
    for index in support_indices:
        bits[index] = 1
    return tuple(bits)


def expand(blocks):
    letters = []
    for source, count in blocks:
        if source not in range(K) or count < 1:
            fail("bad block %s" % ((source, count),))
        letters.extend([source] * count)
    return letters


def prefix_counts(t):
    """Closed form of q_t for the block word, including the final count t=42."""
    if not 0 <= t <= LENGTH:
        fail("prefix index %s is outside 0..42" % t)
    if t <= 2:
        count0 = 0
    elif t <= 18:
        count0 = 1
    elif t <= 24:
        count0 = t - 17
    else:
        count0 = C
    if t <= 3:
        count1 = 0
    elif t <= 24:
        count1 = 1
    elif t <= 30:
        count1 = t - 23
    else:
        count1 = C
    if t <= 4:
        count2 = 0
    elif t <= 11:
        count2 = t - 4
    else:
        count2 = C
    if t == 0:
        count3 = 0
    elif t <= 30:
        count3 = 1
    elif t <= 36:
        count3 = t - 29
    else:
        count3 = C
    if t <= 11:
        count4 = 0
    elif t <= 18:
        count4 = t - 11
    else:
        count4 = C
    if t <= 1:
        count5 = 0
    elif t <= 36:
        count5 = 1
    else:
        count5 = t - 35
    return (count0, count1, count2, count3, count4, count5)


def prefix_table(letters):
    if len(letters) != LENGTH or any(letter not in range(K) for letter in letters):
        fail("not a length-42 word on sources 0..5")
    if any(letters.count(source) != C for source in range(K)):
        fail("not a floor word: a source is not called seven times")
    running = [0] * K
    table = [tuple(running)]
    for letter in letters:
        running[letter] += 1
        table.append(tuple(running))
    if table[-1] != (C,) * K:
        fail("final count is not seven calls of each source")
    return table


def readings(total):
    """Binary mask, or None when a coordinate is outside {0,1} mod 7.

    The two readings are the allowed set {0,1,7,8,14} and the residue
    modulo 7. They disagree on some integers outside that set. A
    disagreement fails the predicate rather than choosing a reading.
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


def add(left, right):
    return tuple(left[source] + right[source] for source in range(K))


def expected_rows():
    rows = []
    for support_indices, pairs in OTHER_HITS.items():
        rows.append((support_indices, pairs))
    for support_indices, pairs in TARGET_HITS.items():
        rows.append((support_indices, pairs))
    return rows


def check_floor(done):
    letters = expand(BLOCKS)
    literal = "".join(str(source) for source in letters)
    if literal != LITERAL:
        fail("block literal changed")
    if literal == WITNESS:
        fail("block word is the #7037 witness")
    if sum(count for _, count in BLOCKS) != LENGTH:
        fail("blocks do not have length 42")
    if sorted(source for source, _ in BLOCKS) != [0, 0, 1, 1, 2, 3, 3, 4, 5, 5]:
        fail("block sources changed")
    table = prefix_table(letters)
    done.append("floor-word")
    for index in range(LENGTH + 1):
        if table[index] != prefix_counts(index):
            fail("q_%s is %s, closed form %s" % (index, table[index], prefix_counts(index)))
    done.append("closed-form")
    return letters, table


def check_hand_sums(table, done):
    seen = {}
    for support_indices, pairs in expected_rows():
        if support_indices in seen:
            fail("support %s is listed twice" % (support_indices,))
        weight = len(support_indices)
        for (left, right), total in pairs:
            if not (0 <= left <= right <= LENGTH - 1):
                fail("pair %s is outside 0..41" % ((left, right),))
            if add(table[left], table[right]) != total:
                fail("prefix sum at %s is %s, expected %s" % ((left, right), add(table[left], table[right]), total))
            mask = readings(total)
            if mask != mask_of(support_indices) or support(mask) != support_indices:
                fail("sum %s does not read as %s" % (total, support_indices))
            if (left + right - weight) % C:
                fail("pair %s breaks the weight identity" % ((left, right),))
        seen[support_indices] = tuple(pair for pair, _total in pairs)
    if len(seen) != 13:
        fail("hand table has %s masks, expected 13" % len(seen))
    pair_count = sum(len(pairs) for pairs in seen.values())
    if pair_count != 25:
        fail("hand table has %s pairs, expected 25" % pair_count)
    done.append("hand-sums")
    return seen


def scan(table):
    hits = {}
    zeros = []
    nonreadings = 0
    examined = 0
    for left in range(LENGTH):
        for right in range(left, LENGTH):
            examined += 1
            total = add(table[left], table[right])
            mask = readings(total)
            if mask is None:
                nonreadings += 1
                continue
            weight = sum(mask)
            if (left + right - weight) % C:
                fail("weight identity failed at s=%s t=%s mask=%s" % (left, right, mask))
            if weight == 0:
                zeros.append(((left, right), total))
                continue
            key = support(mask)
            hits.setdefault(key, []).append(((left, right), total))
    if examined != PAIR_COUNT:
        fail("pair enumeration visited %s pairs, expected %s" % (examined, PAIR_COUNT))
    frozen = {key: tuple(pairs) for key, pairs in hits.items()}
    return frozen, tuple(zeros), nonreadings


def check_scan(table, hand, done):
    hits, zeros, nonreadings = scan(table)
    found_pairs = {key: tuple(pair for pair, _total in pairs) for key, pairs in hits.items()}
    if found_pairs != hand:
        missing = sorted(set(hand) - set(found_pairs))
        extra = sorted(set(found_pairs) - set(hand))
        fail("scan masks differ; missing %s extra %s" % (missing, extra))
    embedded = {}
    for support_indices, pairs in expected_rows():
        embedded[support_indices] = pairs
    for key, pairs in hits.items():
        if pairs != embedded[key]:
            fail("scan rows for %s differ from the embedded sums" % (key,))
    if nonreadings != 874 or len(zeros) != 4:
        fail("partition is nonzero-pairs=%s zeros=%s nonreadings=%s" % (25, len(zeros), nonreadings))
    if sum(len(pairs) for pairs in hits.values()) + len(zeros) + nonreadings != PAIR_COUNT:
        fail("pair partition does not add to 903")
    done.append("pair-scan")
    return hits, zeros


def check_targets(hand, done):
    for support_indices, pairs in TARGET_PAIRS.items():
        if hand.get(support_indices) != pairs:
            fail("target %s pairs are %s" % (support_indices, hand.get(support_indices)))
    done.append("target-controls")


def all_nonzero_supports():
    supports = []
    for code in range(1, 1 << K):
        supports.append(tuple(index for index in range(K) if code & (1 << index)))
    return tuple(supports)


def check_other(hand, done):
    universe = set(all_nonzero_supports())
    if len(universe) != 63:
        fail("nonzero mask count is %s" % len(universe))
    realized_other = set(OTHER_HITS)
    missed = set(MISSED)
    targets = set(TARGET_PAIRS)
    if realized_other & targets or realized_other & missed or targets & missed:
        fail("realized, missed and target lists overlap")
    if realized_other | missed | targets != universe:
        fail("the three lists are not every nonzero mask")
    if len(realized_other) != 11 or len(missed) != 50 or len(targets) != 2:
        fail("split is realized %s missed %s targets %s" % (len(realized_other), len(missed), len(targets)))
    if set(hand) != realized_other | targets:
        fail("hand masks are not the 13 realized masks")
    weights = {}
    for support_indices in MISSED:
        weights[len(support_indices)] = weights.get(len(support_indices), 0) + 1
    if weights != MISSED_BY_WEIGHT:
        fail("missed weights are %s" % (weights,))
    if any(hand.get(support_indices) for support_indices in MISSED):
        fail("a missed mask has a realizing pair")
    done.append("other-61")


def check_zeros(table, zeros, done):
    if zeros != ZERO_PAIRS:
        fail("zero-mask pairs are %s" % (tuple(pair for pair, _total in zeros),))
    for (left, right), total in ZERO_PAIRS:
        if add(table[left], table[right]) != total or readings(total) != (0, 0, 0, 0, 0, 0):
            fail("zero pair %s does not read as the zero mask" % ((left, right),))
    done.append("zero-pairs")


def source_five_levels():
    levels = {value: [] for value in range(C)}
    for index in range(LENGTH):
        value = prefix_counts(index)[5]
        if value not in levels:
            fail("source 5 count %s at t=%s is outside 0..6" % (value, index))
        levels[value].append(index)
    expected = {
        0: [0, 1],
        1: list(range(2, 37)),
        2: [37],
        3: [38],
        4: [39],
        5: [40],
        6: [41],
    }
    if levels != expected:
        fail("source-5 level sets are %s" % (levels,))
    covered = [index for value in range(C) for index in levels[value]]
    if covered != list(range(LENGTH)):
        fail("source-5 level sets do not cover 0..41")
    return levels


def level_candidates(levels):
    candidates = []
    for left in levels[0]:
        for right in levels[1]:
            if left <= right:
                candidates.append((left, right))
    for low in range(C):
        high = 8 - low
        if high < low or high not in levels:
            continue
        if low == high:
            for left in levels[low]:
                for right in levels[low]:
                    if left <= right:
                        candidates.append((left, right))
        else:
            for left in levels[low]:
                for right in levels[high]:
                    if left <= right:
                        candidates.append((left, right))
    return tuple(candidates)


def rule_candidates():
    pairs = [(0, index) for index in range(2, 37)]
    pairs += [(1, index) for index in range(2, 37)]
    pairs += list(LATE_FULL_OBSTRUCTION)
    return tuple(pairs)


def check_weight_six(table, hits, done):
    for index in range(LENGTH + 1):
        if table[index][5] != prefix_counts(index)[5]:
            fail("source 5 at t=%s disagrees with the closed form" % index)
    levels = source_five_levels()
    candidates = level_candidates(levels)
    ruled = rule_candidates()
    if candidates != ruled:
        fail("level-set candidates differ from the source-5 rule")
    if len(candidates) != 73:
        fail("source-5 candidate count is %s" % len(candidates))
    scanned = tuple(
        (left, right)
        for left in range(LENGTH)
        for right in range(left, LENGTH)
        if table[left][5] + table[right][5] in (1, 8)
    )
    if scanned != candidates:
        fail("pairs with source-5 sum in {1,8} are not the 73 candidates")
    for pair in LATE_FULL_OBSTRUCTION:
        total = add(table[pair[0]], table[pair[1]])
        if total != (14, 14, 14, 14, 14, 8) or readings(total) != (0, 0, 0, 0, 0, 1):
            fail("late pair %s is not the mask (5)" % (pair,))
    for right in range(2, 37):
        total = table[right]
        if right != 12:
            if total[4] in (1, 8):
                fail("q_%s has source 4 in {1,8}" % right)
        elif total != (1, 1, 7, 1, 1, 1) or readings(total) == FULL:
            fail("q_12 is not the recorded non-full vector")
    if table[1] != (0, 0, 0, 1, 0, 0):
        fail("q_1 changed")
    for right in range(2, 37):
        total = add(table[1], table[right])
        if total[0] in (1, 8) and total[1] in (1, 8) and total[4] in (1, 8):
            if right != 12 or total != (1, 1, 7, 2, 1, 1) or readings(total) is not None:
                fail("(1, %s) was expected to be the unique non-reading obstruction" % right)
    for left, right in candidates:
        if readings(add(table[left], table[right])) == FULL:
            fail("candidate %s realizes the full mask" % ((left, right),))
    full_support = (0, 1, 2, 3, 4, 5)
    if full_support in hits:
        fail("census realized the full mask")
    for support_indices, pairs in hits.items():
        contains_five = 5 in support_indices
        for (left, right), _total in pairs:
            inside = (left, right) in set(candidates)
            if contains_five != inside:
                fail("pair %s has source-5 bit %s" % ((left, right), contains_five))
    done.append("weight-six")


def check_rejected_edit(letters, done):
    edited = letters[:]
    if edited[0] != 3:
        fail("block word does not start with source 3")
    edited[0] = 2
    try:
        prefix_table(edited)
    except SystemExit as error:
        if not str(error).startswith("FAIL: not a floor word"):
            raise
    else:
        fail("a word that calls source 3 six times was accepted")
    done.append("rejected-edit")


def require_rows(found, expected, label):
    if found != expected:
        fail(label)


def check_rejected_inventory(hits, zeros, done):
    """A dropped realizing pair, and a dropped missed mask, must both fail."""
    if len(zeros) != 4 or len(hits[(5,)]) != 5:
        fail("inventory control lost the recorded rows")
    shortened = dict(hits)
    shortened[(5,)] = hits[(5,)][:-1]
    try:
        require_rows(hits, shortened, "shortened mask (5) matched the scan")
    except SystemExit as error:
        if not str(error).startswith("FAIL: shortened mask (5)"):
            raise
    else:
        fail("a four-pair mask (5) was accepted")
    omitted = tuple(item for item in MISSED if item != (4,))
    if len(omitted) != 49 or (4,) not in MISSED:
        fail("miss list lost the weight-1 mask (4)")
    covered = set(hits) | set(omitted)
    if covered == set(all_nonzero_supports()) or (4,) in covered:
        fail("omitting (4) still covered every nonzero mask")
    done.append("rejected-inventory")


def main():
    if PAIR_COUNT != 903:
        fail("complete pair count is not 903")
    if support(FULL) != (0, 1, 2, 3, 4, 5):
        fail("full mask changed")
    for support_indices, pairs in TARGET_PAIRS.items():
        if tuple(pair for pair, _total in TARGET_HITS[support_indices]) != pairs:
            fail("target pair list drifted from the embedded sums")
    done = []
    letters, table = check_floor(done)
    hand = check_hand_sums(table, done)
    hits, zeros = check_scan(table, hand, done)
    check_targets(hand, done)
    check_other(hand, done)
    check_zeros(table, zeros, done)
    check_weight_six(table, hits, done)
    check_rejected_edit(letters, done)
    check_rejected_inventory(hits, zeros, done)
    if tuple(done) != CONTROLS:
        fail("controls ran as %s" % (done,))
    other_pairs = sum(len(pairs) for pairs in OTHER_HITS.values())
    if other_pairs != 19:
        fail("the other 11 masks have %s pairs" % other_pairs)
    print(
        "PASS_SIX_SOURCE_C7_BLOCK_WORD_MASK_INVENTORY"
        " pairs=903 nonzero_masks=63 realized=13 missed=50"
        " other61_realized=11 other61_missed=50"
        " other61_pairs=%s target_controls=2"
        " weight6=miss source5_candidates=73"
        " zero_pairs=4 nonreadings=874 controls=%s"
        % (other_pairs, len(done))
    )


if __name__ == "__main__":
    main()
