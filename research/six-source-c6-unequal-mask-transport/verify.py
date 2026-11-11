#!/usr/bin/env python3
"""Every T1 endpoint pair has a monotone chain.

The argument is in README.md. This program re-enumerates the two endpoint
domains and checks the explicit word for every pair. Failures raise
SystemExit, so optimized mode cannot silence them.
"""
from collections import Counter

K = 6
CALLS = 6
LENGTH = K * CALLS
TARGET = Counter((6, 6, 6, 7, 7, 7))
NAMED_WORD = "012334500112234455345554432211002103"
MOVING_WORD = "012340011223344555014555443322110023"


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(condition, message):
    if not condition:
        fail(message)


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
    return tuple(early[source] + late[source] for source in range(K))


def mask_of(sum_vector):
    return tuple(source for source, value in enumerate(sum_vector) if value == 7)


def is_floor(word):
    return len(word) == LENGTH and prefix_counts(word, LENGTH) == [CALLS] * K


def keeps_multiset(word):
    if not is_floor(word):
        return False
    for index in range(4, 19):
        if Counter(diagonal_sum(word, index)) != TARGET:
            return False
    return True


def three_subsets():
    subsets = []
    for bits in range(1 << K):
        chosen = tuple(source for source in range(K) if bits >> source & 1)
        if len(chosen) == 3:
            subsets.append(chosen)
    return subsets


def lemma1_splits():
    """Pairs (q_18, bridge counts) whose sum is a permutation of the target."""
    found = []
    # Each coordinate is one of the four rows that can meet {6, 7} inside the cap.
    rows = ((2, 2), (2, 3), (3, 0), (3, 1))
    for assignment in range(4 ** K):
        counts = [0] * K
        bridge = [0] * K
        for source in range(K):
            early, step = rows[(assignment // (4 ** source)) % 4]
            counts[source] = early
            bridge[source] = step
        if sum(counts) != 18 or sum(bridge) != 3:
            continue
        if any(counts[source] + bridge[source] > CALLS for source in range(K)):
            continue
        total = tuple(2 * counts[source] + bridge[source] for source in range(K))
        if Counter(total) != TARGET:
            continue
        found.append((tuple(counts), tuple(bridge), total))
    return found


def q4_for(mask, deficit):
    counts = [0] * K
    if deficit not in mask:
        for source in mask:
            counts[source] = 1
        counts[deficit] = 1
    else:
        counts[deficit] = 2
        for source in mask:
            if source != deficit:
                counts[source] = 1
    return counts


def lemma2_splits():
    """Pairs (q_4, final letter) whose sum with q_35 is the target multiset."""
    type_a = []
    type_b = []
    other = 0
    vectors = 0
    for bits in range(7 ** K):
        counts = [(bits // (7 ** source)) % 7 for source in range(K)]
        if sum(counts) != 4:
            continue
        vectors += 1
        for deficit in range(K):
            total = tuple(
                counts[source] + (5 if source == deficit else 6) for source in range(K)
            )
            if Counter(total) != TARGET:
                other += 1
                continue
            mask = mask_of(total)
            if deficit not in mask and counts == q4_for(mask, deficit):
                type_a.append((tuple(counts), deficit, mask))
            elif deficit in mask and counts == q4_for(mask, deficit):
                type_b.append((tuple(counts), deficit, mask))
            else:
                other += 1
    return vectors, type_a, type_b, other


def build_word(mask4, deficit, mask18):
    """Swaps that trade M4 \\ M18 for M18 \\ M4, then pure slides."""
    mask4 = set(mask4)
    mask18 = set(mask18)
    q4 = q4_for(tuple(sorted(mask4)), deficit)
    if deficit not in mask4:
        prefix = sorted(mask4 | {deficit})
    else:
        prefix = [deficit, deficit] + sorted(mask4 - {deficit})
    require(prefix_counts(prefix, 4) == q4, "prefix does not realize q4")
    exits = sorted(mask4 - mask18)
    entries = sorted(mask18 - mask4)
    require(len(exits) == len(entries), "mask symmetric difference is unbalanced")
    early_budget = [3 - q4[source] for source in range(K)]
    late_budget = [
        3 - (source in mask18) - (source == deficit) for source in range(K)
    ]
    slides = [
        early_budget[source] - (source in set(entries)) for source in range(K)
    ]
    for source in range(K):
        delta = (source in set(exits)) - (source in set(entries))
        require(late_budget[source] - early_budget[source] == delta, "budget identity")
        require(slides[source] == late_budget[source] - (source in set(exits)), "slides")
        require(slides[source] >= 0, "negative slide quota")
    pairs = [(entries[index], exits[index]) for index in range(len(exits))]
    for source in range(K):
        pairs.extend([(source, source)] * slides[source])
    require(len(pairs) == 14, "middle length")
    word = [None] * LENGTH
    word[0:4] = prefix
    word[18:21] = sorted(mask18)
    word[35] = deficit
    for index, (early, late) in enumerate(pairs):
        word[4 + index] = early
        word[34 - index] = late
    require(None not in word, "unfilled position")
    return word


def check_domains():
    splits = lemma1_splits()
    require(len(splits) == 20, f"lemma 1 count {len(splits)}")
    for counts, bridge, total in splits:
        require(counts == (3, 3, 3, 3, 3, 3), f"q18 {counts}")
        require(sum(bridge) == 3 and all(value in (0, 1) for value in bridge), "bridge")
        require(mask_of(total) == tuple(source for source, value in enumerate(bridge) if value), "bridge mask")
    vectors, type_a, type_b, other = lemma2_splits()
    require(vectors == 126, f"sum-4 vectors {vectors}")
    require(len(type_a) == 60 and len(type_b) == 60, f"lemma 2 {(len(type_a), len(type_b))}")
    require(other == 756 - 120, f"rejected endpoint pairs {other}")
    masks = {mask for _, _, mask in type_a + type_b}
    require(len(masks) == 20, f"start masks {len(masks)}")
    return type_a + type_b


def check_transport(starts):
    bridges = three_subsets()
    require(len(bridges) == 20, "bridge subsets")
    unequal = 0
    equal = 0
    named = None
    for _counts, deficit, mask4 in starts:
        for mask18 in bridges:
            word = build_word(mask4, deficit, mask18)
            require(is_floor(word), "constructed word is not a floor word")
            require(keeps_multiset(word), "constructed word leaves the multiset")
            require(mask_of(diagonal_sum(word, 4)) == tuple(mask4), "start mask")
            require(mask_of(diagonal_sum(word, 18)) == tuple(mask18), "end mask")
            if tuple(mask4) == tuple(mask18):
                equal += 1
            else:
                unequal += 1
            if mask4 == (0, 1, 2) and deficit == 3 and mask18 == (3, 4, 5):
                named = "".join(str(source) for source in word)
    require(equal == 120 and unequal == 2280, f"pair split {(equal, unequal)}")
    require(named == NAMED_WORD, f"named word {named}")
    return unequal, equal


def check_controls():
    moving = digits(MOVING_WORD)
    require(keeps_multiset(moving), "predecessor moving word")
    require(mask_of(diagonal_sum(moving, 4)) == (0, 1, 2), "moving start mask")
    require(mask_of(diagonal_sum(moving, 18)) == (0, 1, 4), "moving end mask")
    require(moving[-1] == 3, "moving final letter")

    named = digits(NAMED_WORD)
    require(keeps_multiset(named), "named word")
    # Exchange the first exit 0 with a later slide of 4. Counts stay six,
    # but the first step subtracts a source outside the start mask.
    broken = named[:]
    require(broken[4] == 3 and broken[34] == 0 and broken[14] == 4 and broken[24] == 4,
            "named pairing changed")
    broken[34], broken[24] = broken[24], broken[34]
    require(is_floor(broken), "broken word should stay a floor word")
    require(not keeps_multiset(broken), "illegal first exit was accepted")
    require(Counter(diagonal_sum(broken, 5)) != TARGET, "s=5 still matches")

    over_call = named[:]
    over_call[1] = over_call[0]
    require(not is_floor(over_call), "seven-call word was accepted")
    require(not keeps_multiset(over_call), "seven-call word kept the multiset")


def main():
    starts = check_domains()
    unequal, equal = check_transport(starts)
    check_controls()
    print(
        "PASS_SIX_SOURCE_C6_UNEQUAL_MASK_TRANSPORT"
        f" splits18=20 splits4=120 pairs={equal + unequal}"
        f" unequal={unequal} equal={equal} controls=4"
    )


if __name__ == "__main__":
    main()
