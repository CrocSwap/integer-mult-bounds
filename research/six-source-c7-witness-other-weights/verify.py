#!/usr/bin/env python3
"""Exhaustive mask census of the recorded six-source c=7 witness.

The word is the length-42 floor word recorded in PR #7016. A pair
0 <= s <= t <= 41 realizes a binary mask when q_s + q_t is congruent to
that mask modulo 7. This program classifies all 903 such pairs.

Evidence class: exhaustive finite census of this one word. The domain is
finite, every pair is visited, and the visit count is checked against
42*43/2. This is not a depth-two block, not an unrestricted nonexistence
claim at c=7, and not a change of the selected conditional kappa.
"""

import itertools
import math

K = 6
C = 7
LENGTH = 42
WITNESS = "023514103524310254054123145203452034213150"
# Nonzero masks with no realizing pair. (1, 3, 5) is the weight-3 gap
# already recorded for this word. The other two are the census result.
MISSING = {(1, 3, 5), (3, 5), (0, 1, 3, 5)}
OTHER_MISSING = ((3, 5), (0, 1, 3, 5))
ALLOWED = {0, 1, 7, 8, 14}
MASK_BIT = {0: 0, 1: 1, 7: 0, 8: 1, 14: 0}
# Realizing pairs of each nonzero weight, from the same 903-pair census.
HIT_PAIRS = {1: 16, 2: 19, 3: 19, 4: 19, 5: 15, 6: 8}
ZERO_PAIRS = 8
PAIR_COUNT = LENGTH * (LENGTH + 1) // 2


def fail(message):
    raise SystemExit("FAIL: " + message)


def support(mask):
    return tuple(index for index, bit in enumerate(mask) if bit)


def fmt(groups):
    return ";".join("(" + ",".join(str(index) for index in group) + ")" for group in groups)


def prefixes(letters):
    """Prefix counts q_0, ..., q_42. Reject a word that is not a floor word."""
    if len(letters) != LENGTH or any(letter not in range(K) for letter in letters):
        fail("not a length-42 word on sources 0..5")
    if any(letters.count(source) != C for source in range(K)):
        fail("not a floor word: a source is not called seven times")
    running = [0] * K
    table = [tuple(running)]
    for letter in letters:
        running[letter] += 1
        table.append(tuple(running))
    if len(table) != LENGTH + 1 or table[-1] != (C,) * K:
        fail("final count is not seven calls of each source")
    return table


def readings(total):
    """Binary mask of one sum, or None if any coordinate fails.

    The allowed values {0, 1, 7, 8, 14} are exactly the integers in
    {0, ..., 14} whose residue modulo 7 is 0 or 1. Both readings are
    computed, and a disagreement is a failed control.
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


def census(letters):
    """Classify every pair 0 <= s <= t <= 41. Return hits, zero count, visits."""
    table = prefixes(letters)
    bounds = table[:LENGTH]
    hits = {}
    zero = 0
    examined = 0
    for left in range(LENGTH):
        for right in range(left, LENGTH):
            examined += 1
            total = tuple(
                bounds[left][source] + bounds[right][source] for source in range(K)
            )
            mask = readings(total)
            if mask is None:
                continue
            if not any(mask):
                zero += 1
                continue
            weight = sum(mask)
            if (left + right - weight) % C:
                fail(
                    "weight identity failed at s=%s t=%s mask=%s"
                    % (left, right, mask)
                )
            hits.setdefault(mask, []).append((left, right))
    if examined != PAIR_COUNT:
        fail("pair enumeration visited %s pairs, expected %s" % (examined, PAIR_COUNT))
    return table, hits, zero


def classify(hits):
    """Split all 63 nonzero masks into hits and misses."""
    missing = []
    hit_masks = {weight: 0 for weight in range(1, 7)}
    pair_counts = {weight: 0 for weight in range(1, 7)}
    universe = 0
    for mask in itertools.product((0, 1), repeat=K):
        if not any(mask):
            continue
        universe += 1
        weight = sum(mask)
        found = hits.get(mask, ())
        if found:
            hit_masks[weight] += 1
            pair_counts[weight] += len(found)
        else:
            missing.append(support(mask))
    if universe != (1 << K) - 1:
        fail("nonzero mask count is %s" % universe)
    return missing, hit_masks, pair_counts


def hand_examples(table):
    """Pairs a reviewer can check from the first six letters 023514."""
    if table[1] != (1, 0, 0, 0, 0, 0):
        fail("q_1 is not e_0")
    if table[3] != (1, 0, 1, 1, 0, 0):
        fail("q_3 is not e_0 + e_2 + e_3")
    if table[6] != (1, 1, 1, 1, 1, 1):
        fail("q_6 is not the all-ones vector")
    examples = (
        (table[1], (0,)),
        (table[3], (0, 2, 3)),
        (table[6], (0, 1, 2, 3, 4, 5)),
    )
    for total, expect in examples:
        mask = readings(total)
        if mask is None or support(mask) != expect:
            fail("hand example %s classified as %s" % (expect, mask))


def boundary_adds_nothing(table, hits):
    """q_42 = 7*1 is outside the depth-two range. It adds no new mask."""
    fresh = 0
    for left in range(LENGTH):
        total = tuple(table[left][source] + table[LENGTH][source] for source in range(K))
        mask = readings(total)
        if mask is not None and any(mask) and mask not in hits:
            fresh += 1
    if fresh:
        fail("boundary 42 realized %s new nonzero masks" % fresh)
    return fresh


def superset_corollary(hits):
    """Masks containing {3, 5}, other than the three misses, are realized.

    This is a restatement of the missing set. It blocks reading the census
    as 'every mask that contains sources 3 and 5 is missed.'
    """
    family = 0
    realized = 0
    for mask in itertools.product((0, 1), repeat=K):
        if mask[3] != 1 or mask[5] != 1:
            continue
        family += 1
        if support(mask) in MISSING:
            if mask in hits:
                fail("listed miss %s was realized" % (support(mask),))
        else:
            if mask not in hits:
                fail("mask %s contains {3, 5} and was not realized" % (support(mask),))
            realized += 1
    if family != 16 or realized != 13:
        fail("superset family %s realized %s" % (family, realized))
    return realized


def transposition_differs(witness_other):
    """One adjacent swap stays a floor word and changes the missing set."""
    letters = [int(character) for character in WITNESS]
    if letters[1] == letters[2]:
        fail("positions 1 and 2 are the same source")
    letters[1], letters[2] = letters[2], letters[1]
    _, hits, _ = census(letters)
    missing, _, _ = classify(hits)
    other = tuple(sorted(
        (mask for mask in missing if len(mask) != 3),
        key=lambda mask: (len(mask), mask),
    ))
    if other == witness_other:
        fail("transposed word has the same non-weight-3 missing set")


def reject_call_count_change():
    """The recorded one-letter edit is not a floor word."""
    letters = [int(character) for character in WITNESS]
    if letters[0] != 0:
        fail("witness does not start with source 0")
    letters[0] = 1
    try:
        prefixes(letters)
    except SystemExit as error:
        if str(error).startswith("FAIL: not a floor word"):
            return
        raise
    fail("a word that calls source 0 six times was accepted")


def main():
    if WITNESS != "023514103524310254054123145203452034213150":
        fail("witness literal changed")
    if PAIR_COUNT != 903:
        fail("complete pair count is not 903")
    letters = [int(character) for character in WITNESS]
    table, hits, zero = census(letters)
    if zero != ZERO_PAIRS:
        fail("zero-mask pair count %s" % zero)
    hand_examples(table)
    fresh = boundary_adds_nothing(table, hits)
    missing, hit_masks, pair_counts = classify(hits)
    if set(missing) != MISSING:
        fail("missing masks changed: " + str(missing))
    if pair_counts != HIT_PAIRS:
        fail("realizing-pair counts changed: " + str(pair_counts))
    for weight in range(1, 7):
        expect = math.comb(K, weight) - (1 if weight in (2, 3, 4) else 0)
        if hit_masks[weight] != expect:
            fail("weight %s hit %s masks, expected %s" % (weight, hit_masks[weight], expect))
    other = tuple(sorted(
        (mask for mask in missing if len(mask) != 3),
        key=lambda mask: (len(mask), mask),
    ))
    weight3 = tuple(sorted(mask for mask in missing if len(mask) == 3))
    if other != OTHER_MISSING:
        fail("non-weight-3 missing set changed: " + str(other))
    if weight3 != ((1, 3, 5),):
        fail("weight-3 missing set changed: " + str(weight3))
    realized_superset = superset_corollary(hits)
    transposition_differs(other)
    reject_call_count_change()
    nonzero_hit = sum(hit_masks.values())
    other_hit = nonzero_hit - hit_masks[3]
    other_total = ((1 << K) - 1) - math.comb(K, 3)
    print(
        "PASS_SIX_SOURCE_C7_WITNESS_OTHER_WEIGHTS"
        " pairs=%s nonzero_hit=%s/63 other_hit=%s/%s"
        " missing_other=%s weight3_missing=%s"
        " zero_pairs=%s boundary42_new=%s superset_realized=%s/16 controls=7"
        % (
            PAIR_COUNT,
            nonzero_hit,
            other_hit,
            other_total,
            fmt(other),
            fmt(weight3),
            zero,
            fresh,
            realized_superset,
        )
    )


if __name__ == "__main__":
    main()
