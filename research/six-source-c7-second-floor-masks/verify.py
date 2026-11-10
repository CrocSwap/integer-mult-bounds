#!/usr/bin/env python3
"""Two named masks on one length-42 floor word other than the #7037 witness.

The word is the block string 3,5,0,1, 2^7, 4^7, 0^6, 1^6, 3^6, 5^6.
Every pair 0 <= s <= t <= 41 is evaluated with the same predicate as
PR #7037. For the masks (3, 5) and (0, 1, 3, 5) only, the realizing
pairs are recorded and checked against the prefix table.

Evidence class: exhaustive finite census of these two masks on this one
word, plus an explicit realizing pair for each. The four-prefix lemma
is a direct count, not a search. This is not a depth-two block, not a
census of floor words, and not a change of the selected conditional kappa.
"""

K = 6
C = 7
LENGTH = 42
WITNESS = "023514103524310254054123145203452034213150"
TRANSPOSITION = "032514103524310254054123145203452034213150"
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
# Prefixes at the block boundaries used in the hand calculation.
BOUNDARY = {
    0: (0, 0, 0, 0, 0, 0),
    1: (0, 0, 0, 1, 0, 0),
    2: (0, 0, 0, 1, 0, 1),
    3: (1, 0, 0, 1, 0, 1),
    4: (1, 1, 0, 1, 0, 1),
    11: (1, 1, 7, 1, 0, 1),
    18: (1, 1, 7, 1, 7, 1),
    24: (7, 1, 7, 1, 7, 1),
    30: (7, 7, 7, 1, 7, 1),
    36: (7, 7, 7, 7, 7, 1),
    42: (7, 7, 7, 7, 7, 7),
}
MASK_35 = (0, 0, 0, 1, 0, 1)
MASK_0135 = (1, 1, 0, 1, 0, 1)
TARGETS = {MASK_35: (3, 5), MASK_0135: (0, 1, 3, 5)}
# Every realizing pair of the two targets on the block word.
EXPECTED = {
    MASK_35: {
        (0, 2): (0, 0, 0, 1, 0, 1),
        (0, 30): (7, 7, 7, 1, 7, 1),
        (1, 36): (7, 7, 7, 8, 7, 1),
    },
    MASK_0135: {
        (0, 4): (1, 1, 0, 1, 0, 1),
        (0, 11): (1, 1, 7, 1, 0, 1),
        (0, 18): (1, 1, 7, 1, 7, 1),
    },
}
ALLOWED = {0, 1, 7, 8, 14}
MASK_BIT = {0: 0, 1: 1, 7: 0, 8: 1, 14: 0}
PAIR_COUNT = LENGTH * (LENGTH + 1) // 2
# First two letters a permutation of {3, 5}, next two a permutation of {0, 1}.
LEMMA_PREFIXES = ("3501", "3510", "5301", "5310")
CONTROLS = (
    "floor-word",
    "boundary-prefixes",
    "six-sums",
    "pair-scan",
    "lemma-prefixes",
    "witness-miss",
    "transposition-miss",
    "rejected-edit",
)


def fail(message):
    raise SystemExit("FAIL: " + message)


def support(mask):
    return tuple(index for index, bit in enumerate(mask) if bit)


def expand(blocks):
    letters = []
    for source, count in blocks:
        if source not in range(K) or count < 1:
            fail("bad block %s" % ((source, count),))
        letters.extend([source] * count)
    return letters


def prefix_table(letters):
    """q_0, ..., q_n for one word. Reject a full word that is not a floor word."""
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
    """Binary mask of one sum, or None when a coordinate is outside {0,1} mod 7.

    The allowed values {0, 1, 7, 8, 14} are the integers in {0, ..., 14}
    whose residue modulo 7 is 0 or 1. Both readings are computed. A
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
            allowed_bits.append(MASK_BIT[value])
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


def scan(letters):
    """Visit every pair 0 <= s <= t <= 41. Return hits of the two target masks."""
    table = prefix_table(letters)
    hits = {mask: {} for mask in TARGETS}
    examined = 0
    for left in range(LENGTH):
        for right in range(left, LENGTH):
            examined += 1
            total = tuple(
                table[left][source] + table[right][source] for source in range(K)
            )
            mask = readings(total)
            if mask is None or not any(mask):
                continue
            if (left + right - sum(mask)) % C:
                fail(
                    "weight identity failed at s=%s t=%s mask=%s"
                    % (left, right, mask)
                )
            if mask in hits:
                hits[mask][(left, right)] = total
    if examined != PAIR_COUNT:
        fail("pair enumeration visited %s pairs, expected %s" % (examined, PAIR_COUNT))
    return table, hits


def add(left, right):
    return tuple(left[source] + right[source] for source in range(K))


def check_word(done):
    letters = expand(BLOCKS)
    literal = "".join(str(source) for source in letters)
    if literal != "350122222224444444000000111111333333555555":
        fail("block literal changed")
    if literal == WITNESS:
        fail("block word is the #7037 witness")
    table = prefix_table(letters)
    done.append("floor-word")
    for index, expect in BOUNDARY.items():
        if table[index] != expect:
            fail("q_%s is %s, expected %s" % (index, table[index], expect))
    done.append("boundary-prefixes")
    for mask, pairs in EXPECTED.items():
        weight = sum(mask)
        for (left, right), total in pairs.items():
            if not (0 <= left <= right <= LENGTH - 1):
                fail("pair %s is outside 0..41" % ((left, right),))
            if add(table[left], table[right]) != total:
                fail("prefix sum at %s is not %s" % ((left, right), total))
            if readings(total) != mask or support(mask) != TARGETS[mask]:
                fail("sum %s does not read as %s" % (total, TARGETS[mask]))
            if (left + right - weight) % C:
                fail("pair %s breaks the weight identity" % ((left, right),))
    done.append("six-sums")
    return letters, table


def check_scan(letters, done):
    _, hits = scan(letters)
    for mask, pairs in EXPECTED.items():
        if hits[mask] != pairs:
            fail(
                "scan hits for %s are %s"
                % (TARGETS[mask], sorted(hits[mask]))
            )
    done.append("pair-scan")


def check_lemma_prefixes(done):
    """Either order of {3, 5} then either order of {0, 1} has the same counts."""
    if len(LEMMA_PREFIXES) != 4 or len(set(LEMMA_PREFIXES)) != 4:
        fail("lemma prefix list is not the four orders")
    for text in LEMMA_PREFIXES:
        letters = [int(character) for character in text]
        if sorted(letters[:2]) != [3, 5] or sorted(letters[2:]) != [0, 1]:
            fail("prefix %s is not {3,5} followed by {0,1}" % text)
        running = [0] * K
        table = [tuple(running)]
        for letter in letters:
            running[letter] += 1
            table.append(tuple(running))
        if table[2] != BOUNDARY[2] or table[4] != BOUNDARY[4]:
            fail("prefix %s has counts %s, %s" % (text, table[2], table[4]))
        if readings(table[2]) != MASK_35 or readings(table[4]) != MASK_0135:
            fail("prefix %s does not realize both masks at (0, 2) and (0, 4)" % text)
    done.append("lemma-prefixes")


def misses_both(letters):
    _, hits = scan(letters)
    for mask in TARGETS:
        if hits[mask]:
            fail("a control word realized %s" % (TARGETS[mask],))


def check_controls(letters, done):
    witness = [int(character) for character in WITNESS]
    if "".join(str(source) for source in witness) != WITNESS:
        fail("witness literal changed")
    misses_both(witness)
    done.append("witness-miss")
    swapped = witness[:]
    if swapped[1] == swapped[2]:
        fail("witness positions 1 and 2 are the same source")
    swapped[1], swapped[2] = swapped[2], swapped[1]
    transposed = "".join(str(source) for source in swapped)
    if transposed != TRANSPOSITION:
        fail("transposition literal is not the swap of positions 1 and 2")
    if transposed == WITNESS or transposed == "".join(str(source) for source in letters):
        fail("transposition is not a third word")
    misses_both(swapped)
    done.append("transposition-miss")
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


def mask_text(mask):
    return "(" + ",".join(str(index) for index in support(mask)) + ")"


def pair_text(mask):
    pairs = ",".join("(%s,%s)" % pair for pair in sorted(EXPECTED[mask]))
    return "%s=%s:%s" % (mask_text(mask), len(EXPECTED[mask]), pairs)


def main():
    if PAIR_COUNT != 903:
        fail("complete pair count is not 903")
    if support(MASK_35) != (3, 5) or support(MASK_0135) != (0, 1, 3, 5):
        fail("target supports changed")
    done = []
    letters, _ = check_word(done)
    check_scan(letters, done)
    check_lemma_prefixes(done)
    check_controls(letters, done)
    if tuple(done) != CONTROLS:
        fail("controls ran as %s" % (done,))
    # The two target families are disjoint, so no pair is counted twice.
    if set(EXPECTED[MASK_35]) & set(EXPECTED[MASK_0135]):
        fail("one pair was assigned to both masks")
    print(
        "PASS_SIX_SOURCE_C7_SECOND_FLOOR_MASKS"
        " pairs=%s %s %s"
        " witness_both=miss transposition_both=miss"
        " lemma_prefixes=4 controls=%s"
        % (PAIR_COUNT, pair_text(MASK_35), pair_text(MASK_0135), len(done))
    )


if __name__ == "__main__":
    main()
