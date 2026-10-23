#!/usr/bin/env python3
"""Exhaustively audit PR #3818's union-support prune on n=4, L=8.

This enumerates the full 4**8 word domain before applying any word validity
conditions. It then checks every restored canonical completion and every one
of its prefixes against the proposed partial-prefix bound.
"""
from collections import Counter, defaultdict
from itertools import product
import json


def choose2(n):
    return n * (n - 1) // 2


def canonical(word):
    """First-occurrence restricted-growth representative."""
    high = -1
    for label in word:
        if label < 0 or label > high + 1:
            return False
        high = max(high, label)
    return word[0] == 0 and high == max(word)


def path_states(word):
    q = 0
    states = []
    for label in word:
        states.append(q)
        q ^= 1 << label
    return tuple(states), q


def classes(points):
    return tuple({x for x in points if (x.bit_count() & 1) == p}
                 for p in (0, 1))


def within_support(group):
    return {a ^ b for a in group for b in group if a != b}


def pair_supports(points):
    even, odd = classes(points)
    same = within_support(even) | within_support(odd)
    cross = {a ^ b for a in even for b in odd}
    return even, odd, same, cross


def audit_fixture():
    word = tuple(map(int, "01021323"))
    states, final = path_states(word)
    points = set(states)
    assert final == 0 and len(points) == 8
    coverage = {a ^ b for a in points for b in points}
    assert coverage == set(range(16))

    by_weight = [set(x for x in points if (x.bit_count() & 1) == p)
                 for p in (0, 1)]
    by_bit0 = [set(x for x in points if (x & 1) == p) for p in (0, 1)]
    weight_split = tuple(map(len, by_weight))
    bit0_split = tuple(map(len, by_bit0))
    need = (1 << (4 - 1)) - 1
    weight_excess = sum(choose2(len(g)) - len(within_support(g))
                        for g in by_weight)
    bit0_excess = sum(choose2(len(g)) - len(within_support(g))
                      for g in by_bit0)
    substituted_budget = 2 * choose2(len(word) // 2) - need
    actual_bit0_budget = sum(choose2(len(g)) for g in by_bit0) - need
    assert (weight_split, bit0_split) == ((4, 4), (6, 2))
    assert weight_excess <= substituted_budget
    assert bit0_excess == 8 and bit0_excess > substituted_budget == 5
    assert bit0_excess <= actual_bit0_budget == 9
    return {
        "word": "01021323",
        "prefix_states_including_closure": list(states) + [final],
        "distinct_prefix_states": len(points),
        "coverage_masks": len(coverage),
        "weight_split": list(weight_split),
        "weight_excess": weight_excess,
        "bit0_split": list(bit0_split),
        "bit0_excess": bit0_excess,
        "invalid_substituted_budget": substituted_budget,
        "valid_actual_bit0_budget": actual_bit0_budget,
    }


def audit_unpruned_domain():
    n, length = 4, 8
    all_masks = set(range(1 << n))
    need_even = (1 << (n - 1)) - 1
    raw_words = 0
    valid_words = []
    for word in product(range(n), repeat=length):
        raw_words += 1
        if not canonical(word):
            continue
        counts = Counter(word)
        if set(counts) != set(range(n)) or any(c < 2 or c % 2 for c in counts.values()):
            continue
        states, final = path_states(word)
        if final != 0:
            continue
        points = set(states)
        even, odd, same, cross = pair_supports(points)
        universal = {a ^ b for a in points for b in points} == all_masks
        final_split = (len(even), len(odd))
        valid_words.append((word, states, points, final_split, same, cross, universal))

    prefixes = defaultdict(lambda: {"completions": 0, "universal": 0})
    pruned_prefixes = set()
    audits = 0
    max_bound_gap = 0
    universal_words = set()
    universal_by_split = defaultdict(list)

    for word, states, points, (s, t), final_same, final_cross, universal in valid_words:
        if universal:
            universal_words.add(word)
            universal_by_split[(s, t)].append("".join(map(str, word)))
            assert len(final_same) == need_even
            assert len(final_same) + len(final_cross) + 1 == 1 << n

        for k in range(1, length + 1):
            prefix_points = set(states[:k])
            even, odd, current_same, _ = pair_supports(prefix_points)
            e, o = len(even), len(odd)
            future_same = choose2(s) + choose2(t) - choose2(e) - choose2(o)
            assert future_same >= 0

            # This is PR #3818's line 108-109 implication, evaluated against
            # the actual final support of this unpruned completion.
            upper = len(current_same) + future_same
            audits += 1
            max_bound_gap = max(max_bound_gap, len(final_same) - upper)
            assert len(final_same) <= upper

            prefix_labels = word[:k - 1]
            key = ((s, t), prefix_labels)
            prefixes[key]["completions"] += 1
            prefixes[key]["universal"] += int(universal)
            if upper < need_even:
                pruned_prefixes.add(key)

    # A tiny exhaustive domain is useful only if it has both controls.
    assert raw_words == n ** length
    assert len(valid_words) == 105
    assert len(universal_words) == 26
    assert pruned_prefixes
    bad = [(key, prefixes[key]) for key in pruned_prefixes
           if prefixes[key]["universal"]]
    assert not bad, bad[:3]

    unpruned_universal = universal_words
    retained_by_union = {
        word for word, states, points, (s, t), final_same, final_cross, universal in valid_words
        if universal and all(
            len(pair_supports(set(states[:k]))[2])
            + choose2(s) + choose2(t)
            - choose2(len(pair_supports(set(states[:k]))[0]))
            - choose2(len(pair_supports(set(states[:k]))[1])) >= need_even
            for k in range(1, length + 1)
        )
    }
    assert retained_by_union == unpruned_universal

    split_counts = Counter((s, t) for _, _, _, (s, t), *_ in valid_words)
    split_universal = Counter((s, t) for _, _, _, (s, t), _, _, universal in valid_words
                              if universal)
    return {
        "domain": {"n": n, "length": length, "raw_label_words": raw_words},
        "canonical_restored_words": len(valid_words),
        "canonical_universal_words_unpruned": len(unpruned_universal),
        "canonical_universal_words_retained_by_union": len(retained_by_union),
        "prefix_completion_checks": audits,
        "prefix_target_pairs_pruned": len(pruned_prefixes),
        "pruned_prefix_target_pairs_with_universal_completions": len(bad),
        "max_actual_support_minus_bound": max_bound_gap,
        "word_counts_by_final_split": [
            {"split": list(k), "words": v, "universal": split_universal[k],
             "universal_words": sorted(universal_by_split[k])}
            for k, v in sorted(split_counts.items())
        ],
    }


def main():
    fixture = audit_fixture()
    domain = audit_unpruned_domain()
    print(json.dumps({"status": "PASS_F7_L22_UNION_PRUNE_TINY_EXHAUSTIVE",
                      "first_example": fixture, "unpruned_domain": domain}, indent=2))


if __name__ == "__main__":
    main()
