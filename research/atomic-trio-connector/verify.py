#!/usr/bin/env python3
"""Atomic triple-sum connector: charged budget does not beat the known repairs.

No imports from research/universal-connector-boundary. Python 3.10+.
"""

from collections import Counter
from itertools import combinations, permutations


def need(condition, message):
    if not condition:
        raise ValueError(message)


def prefixes(steps):
    point = 0
    found = [0]
    for step in steps:
        point ^= step
        found.append(point)
    return found


def difference_mask(steps):
    found = prefixes(steps)
    mask = 0
    for left in found:
        for right in found:
            mask |= 1 << (left ^ right)
    return mask


def popcount(value):
    return value.bit_count()


def missing_bits(mask, width):
    return [bit for bit in range(width) if (mask >> bit & 1) == 0]


def factorial(n):
    result = 1
    for value in range(2, n + 1):
        result *= value
    return result


def three_source_orders():
    """Every order of one triple-sum and one toggle of each source."""
    labels = (("T", 7), ("S", 1), ("S", 2), ("S", 4))
    for order in permutations(labels):
        yield [step for _, step in order]


def check_three_source_obstruction():
    """The only leaf-tied shape misses a weight-2 mask in every order."""
    seen = 0
    missed = Counter()
    for steps in three_source_orders():
        seen += 1
        found = prefixes(steps)
        distinct = found[:-1]
        need(found[-1] == 0, "three-source word does not restore the connector")
        need(len(set(distinct)) == 4, "unexpected prefix collision")
        pairs = {left ^ right for left in distinct for right in distinct if left != right}
        need(len(pairs) == 6, "pairwise differences are not simple")
        mask = difference_mask(steps)
        absent = missing_bits(mask, 8)
        need(absent and absent != [0], "zero is not a realized difference")
        absent.remove(0) if 0 in absent else None
        need(len(absent) == 1, "expected exactly one missing nonzero mask")
        missing = absent[0]
        need(missing == 0 ^ distinct[0] ^ distinct[1] ^ distinct[2] ^ distinct[3],
             "missing mask is not the sum of the prefixes")
        need(popcount(missing) == 2, "missing mask is not weight two")
        missed[missing] += 1
    need(seen == 24, "three-source order count")
    need(set(missed) == {3, 5, 6} and sum(missed.values()) == 24,
         "weight-2 miss histogram")
    # Hand-checkable witness: T, e0, e1, e2 has prefixes 0,7,6,4 and misses 5.
    witness = difference_mask((7, 1, 2, 4))
    need(missing_bits(witness, 8) == [5], "published three-source witness changed")
    return missed


def candidate_shapes(sources, classic_calls, classic_appearances):
    """Shapes with at least one TRIO that could tie the known source-side bill."""
    need_nonzero = (1 << sources) - 1
    found = []
    for trios in range(1, classic_calls + 1):
        for calls in range(trios, classic_calls + 1):
            singles = calls - trios
            appearances = 3 * trios + singles
            if calls % 2 or appearances % 2:
                continue
            if calls * (calls - 1) // 2 < need_nonzero:
                continue
            if appearances > classic_appearances or calls > classic_calls:
                continue
            found.append((trios, calls, appearances))
    return found


def appearance_patterns():
    """Ten-call, one-TRIO, five-source patterns with appearances 4,2,2,2,2."""
    patterns = []
    for triple in combinations(range(5), 3):
        trio = 0
        for source in triple:
            trio |= 1 << source
        inside = set(triple)
        for heavy in range(5):
            counts = {source: (1 if source in inside else 2) for source in range(5)}
            counts[heavy] += 2
            appearances = {
                source: counts[source] + (1 if source in inside else 0)
                for source in range(5)
            }
            need(sorted(appearances.values()) == [2, 2, 2, 2, 4], "appearance partition")
            need(sum(counts.values()) == 9, "single-toggle count")
            patterns.append((trio, counts))
    need(len(patterns) == 50, "pattern inventory")
    return patterns


def expected_word_count():
    """10! / multiplicities, split by whether the quadruple source is in the triple."""
    inside = 30 * factorial(10) // (factorial(3) * factorial(2) * factorial(2))
    outside = 20 * factorial(10) // (factorial(4) * factorial(2))
    return inside + outside


def record(steps, histogram):
    mask = difference_mask(steps)
    size = popcount(mask)
    histogram[size] += 1
    return size


def census_by_permutation(trio, counts):
    histogram = [0] * 33
    best = 0
    singles = []
    for source in range(5):
        singles.extend([1 << source] * counts[source])
    orders = set(permutations(singles))
    words = 0
    for order in orders:
        for slot in range(10):
            steps = list(order)
            steps.insert(slot, trio)
            best = max(best, record(steps, histogram))
            words += 1
    return words, histogram, best


def census_by_placement(trio, counts):
    """Choose positions independently of itertools.permutations."""
    histogram = [0] * 33
    best = 0
    words = 0
    sequence = [None] * 10
    items = [(1 << source, counts[source]) for source in range(5) if counts[source]]

    def place(index, free):
        nonlocal best, words
        if index == len(items):
            steps = list(sequence)
            best = max(best, record(steps, histogram))
            words += 1
            return
        step, count = items[index]
        for chosen in combinations(free, count):
            for position in chosen:
                sequence[position] = step
            remaining = [position for position in free if position not in chosen]
            place(index + 1, remaining)
            for position in chosen:
                sequence[position] = None

    for trio_at in range(10):
        sequence[trio_at] = trio
        free = [position for position in range(10) if position != trio_at]
        place(0, free)
        sequence[trio_at] = None
    return words, histogram, best


def add_histograms(left, right):
    return [a + b for a, b in zip(left, right)]


PINNED_HISTOGRAM = {
    16: 140400,
    19: 878400,
    21: 1162800,
    22: 208800,
    23: 993600,
    24: 1022400,
    25: 399600,
    26: 658800,
    28: 396000,
    29: 57600,
    30: 129600,
}


def check_five_source_census():
    need(expected_word_count() == 6048000, "closed-form word count")
    need(candidate_shapes(5, 12, 12) == [(1, 10, 12)], "five-source candidate shape")
    first = [0] * 33
    second = [0] * 33
    best = 0
    total = 0
    for trio, counts in appearance_patterns():
        words_a, hist_a, best_a = census_by_permutation(trio, counts)
        words_b, hist_b, best_b = census_by_placement(trio, counts)
        need(words_a == words_b and hist_a == hist_b and best_a == best_b,
             "permutation and placement censuses disagree")
        total += words_a
        best = max(best, best_a)
        first = add_histograms(first, hist_a)
        second = add_histograms(second, hist_b)
    need(total == 6048000 and first == second, "census coverage of the candidate shape")
    observed = {size: count for size, count in enumerate(first) if count}
    need(observed == PINNED_HISTOGRAM, "coverage histogram changed")
    need(best == 30 and sum(PINNED_HISTOGRAM.values()) == 6048000, "unexpected full cover")
    need(first[32] == 0, "a ten-call TRIO word covered every mask")
    return best


def positive_three_word():
    return [0, 1, 0, 1, 2, 2]


def ten_toggle_word():
    return [0, 1, 2, 0, 3, 1, 4, 2, 3, 4]


def twelve_toggle_word():
    return [2, 0, 2, 1, 2, 0, 3, 1, 4, 2, 3, 4]


def check_known_repairs():
    three = [1 << source for source in positive_three_word()]
    need(difference_mask(three) == (1 << 8) - 1, "three-source repair lost full coverage")
    ten = [1 << source for source in ten_toggle_word()]
    ten_mask = difference_mask(ten)
    need(missing_bits(ten_mask, 32) == [21], "ten-toggle control must miss only mask 21")
    twelve = [1 << source for source in twelve_toggle_word()]
    need(prefixes(twelve)[-1] == 0, "twelve-toggle word does not restore")
    need(difference_mask(twelve) == (1 << 32) - 1, "twelve-toggle repair lost full coverage")


def readout_slots(steps):
    found = prefixes(steps)
    slots = {}
    for left, prefix in enumerate(found):
        for right in range(left + 1, len(found)):
            mask = prefix ^ found[right]
            if mask and mask not in slots:
                slots[mask] = (left, right)
    nonzero = popcount(difference_mask(steps)) - 1
    need(len(slots) == nonzero, "readout assignment does not match the difference set")
    return slots


def schedule(word, slots, rows):
    events = []
    for slot in range(len(word) + 1):
        for row, mask in rows:
            pair = slots[mask]
            if slot in pair:
                events.append(("A", row))
        if slot < len(word):
            events.append(("B", word[slot]))
    return events


def xor_apply(matrix, vector):
    x = vector & 1
    y = (vector >> 1) & 1
    ((a, b), (c, d)) = matrix
    return (a & x ^ b & y) | ((c & x ^ d & y) << 1)


def run_identity(events, values, connector, outputs):
    connector = connector
    outputs = list(outputs)
    for kind, index in events:
        if kind == "B":
            connector ^= values[index]
        else:
            outputs[index] ^= connector
    return outputs, connector


def run_matrices(events, values, dirt, rows, source_maps, output_maps):
    connector = dirt
    outputs = [0] * rows
    for kind, index in events:
        if kind == "B":
            connector ^= xor_apply(source_maps[index], values[index])
        else:
            outputs[index] ^= xor_apply(output_maps[index], connector)
    return outputs, connector


def expected_identity_row(mask, values):
    total = 0
    for source, value in enumerate(values):
        if mask >> source & 1:
            total ^= value
    return total


def check_identity_batch(word, width, dirt_values, samples):
    steps = [1 << source for source in word]
    slots = readout_slots(steps)
    rows = [(mask - 1, mask) for mask in range(1, 1 << width)]
    events = schedule(word, slots, rows)
    for dirt in dirt_values:
        for values in samples:
            outputs, connector = run_identity(events, values, dirt, [0] * len(rows))
            need(connector == dirt, "identity schedule does not restore the connector")
            for mask in range(1, 1 << width):
                need(outputs[mask - 1] == expected_identity_row(mask, values),
                     "identity batch missed a realized mask")
            reversed_outputs, reversed_connector = run_identity(
                events[::-1], values, connector, outputs)
            need(reversed_connector == dirt, "identity inverse disturbed the connector")
            need(reversed_outputs == [0] * len(rows), "identity inverse left an output")


def check_missing_mask_has_no_readout(word_steps, missing):
    found = prefixes(word_steps)
    need(all(found[left] ^ found[right] != missing
             for left, right in combinations(range(len(found)), 2)),
         "paired readout exists for a missing mask")
    # Every boundary pair, on a dirty connector and a one-hot source, fails to
    # emit the missing mask. This is the same difference test evaluated as a
    # one-row schedule rather than as a set membership check.
    for left, right in combinations(range(len(found)), 2):
        connector = 1
        output = 0
        for slot in range(len(found)):
            if slot in (left, right):
                output ^= connector
            if slot < len(found) - 1:
                connector ^= found[slot] ^ found[slot + 1]
        need(output != missing, "a readout pair reproduced a missing mask from the all-ones input")


def check_dense_controls():
    check_identity_batch(
        positive_three_word(),
        3,
        (0, 1),
        ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)),
    )
    check_identity_batch(
        twelve_toggle_word(),
        5,
        (0, 1),
        tuple(tuple(1 if source == bit else 0 for source in range(5)) for bit in range(5))
        + ((1, 1, 0, 1, 0), (1, 0, 1, 1, 1)),
    )
    # Noncommuting length-2 maps on the three-source repair.
    word = positive_three_word()
    steps = [1 << source for source in word]
    slots = readout_slots(steps)
    rows = [(mask - 1, mask) for mask in range(1, 8)]
    events = schedule(word, slots, rows)
    source_maps = (
        ((1, 1), (0, 1)),
        ((1, 0), (1, 1)),
        ((0, 1), (1, 1)),
    )
    output_maps = ((((1, 1), (0, 1)),) * 7)
    samples = ((1, 2, 3), (3, 1, 2), (2, 2, 1))
    for dirt in (0, 1, 2, 3):
        for values in samples:
            outputs, connector = run_matrices(
                events, values, dirt, 7, source_maps, output_maps)
            need(connector == dirt, "matrix schedule does not restore the connector")
            for mask in range(1, 8):
                mixed = 0
                for source in range(3):
                    if mask >> source & 1:
                        mixed ^= xor_apply(source_maps[source], values[source])
                expect = xor_apply(output_maps[mask - 1], mixed)
                need(outputs[mask - 1] == expect, "matrix batch missed a mask")
    check_missing_mask_has_no_readout((7, 1, 2, 4), 5)
    sample = (7, 1, 1, 1, 2, 4, 8, 8, 16, 16)
    sample_mask = difference_mask(sample)
    absent = [bit for bit in range(1, 32) if (sample_mask >> bit & 1) == 0]
    need(prefixes(sample)[-1] == 0, "sample ten-call word does not restore")
    need(absent, "sample ten-call word unexpectedly became universal")
    check_missing_mask_has_no_readout(sample, absent[0])
    # Failure control: dropping mask 7 removes its row, so the basis-e0 image is no longer complete.
    broken = schedule(word, slots, rows[:-1])
    outputs, connector = run_identity(broken, (1, 0, 0), 1, [0] * (len(rows) - 1))
    need(connector == 1, "dropping one row changed connector restoration")
    need(outputs[0] == 1, "dropping mask 7 disturbed the scheduled mask-1 row")
    need(len(outputs) == 6, "failure control kept the mask-7 row")


def minimum_leaf_cost(prices, extra_pairs):
    cheapest = min(prices)
    return 2 * sum(prices) + 2 * extra_pairs * cheapest


def check_prices():
    # Four prefixes supply at most six nonzero differences, so no four-call word
    # can cover seven masks. The leaf-tied TRIO shape is not a covering candidate.
    need(candidate_shapes(3, 6, 6) == [], "three-source candidate shape")
    families = (
        (1, 1, 1),
        (1, 1, 1, 1, 1),
        (4, 1, 9, 2, 6),
        (3, 3, 1),
        (8, 5, 5, 2, 2),
    )
    for prices in families:
        prices = tuple(prices)
        if len(prices) == 3:
            classic = minimum_leaf_cost(prices, 0)
            # Covering schedules need at least eight applications: two more than the repair.
            need(minimum_leaf_cost(prices, 1) == classic + 2 * min(prices),
                 "three-source leaf gap")
            improved = minimum_leaf_cost(prices, 1) <= classic
        else:
            classic = minimum_leaf_cost(prices, 1)
            optimistic = minimum_leaf_cost(prices, 2)
            need(optimistic - classic == 2 * min(prices), "five-source leaf gap")
            need(optimistic > classic, "TRIO lower bound did not stay strictly above the repair")
            improved = optimistic <= classic
        need(not improved, "price vector falsely favored the triple sum")
        for frame in (0, 1, 5):
            if len(prices) == 5:
                repair = minimum_leaf_cost(prices, 1) + 12 * frame
                lower = minimum_leaf_cost(prices, 2) + 12 * frame
                need(lower == repair + 2 * min(prices), "frame price changed the leaf gap")


def main():
    check_known_repairs()
    missed = check_three_source_obstruction()
    best = check_five_source_census()
    check_dense_controls()
    check_prices()
    print(
        "PASS_ATOMIC_TRIO_CONNECTOR "
        f"three_source_orders=24 misses={dict(sorted(missed.items()))} "
        f"five_source_words=6048000 full_covers=0 best_coverage={best}"
    )


if __name__ == "__main__":
    main()
