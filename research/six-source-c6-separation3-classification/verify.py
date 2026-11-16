#!/usr/bin/env python3
"""Classification of separation-3 pairs on the c=6 diagonal s+t=39.

The written argument is in README.md. This program exhausts a finite domain
of count pairs. It does not search depth-two words and it does not call a
SAT solver. Failures raise SystemExit, so Python -O cannot silence them.
"""
import itertools
import math
from collections import Counter

K = 6
C = 6
ALLOWED = (0, 1, 6, 7, 12)
ALLOWED_SET = set(ALLOWED)
MASK_BIT = {0: 0, 1: 1, 6: 0, 7: 1, 12: 0}
# (n01, n31, n00, n30, n60, n22, n23) after the letter-budget reduction.
TYPES = {
    (0, 3, 0, 3, 0, 0, 0): 20,
    (0, 3, 1, 1, 1, 0, 0): 120,
    (1, 2, 0, 2, 1, 0, 0): 180,
    (1, 2, 1, 0, 2, 0, 0): 180,
    (2, 1, 0, 1, 2, 0, 0): 180,
    (3, 0, 0, 0, 3, 0, 0): 20,
}
EXPLICIT = (1, 1, 1, 6, 0, 0)
PRICE_TYPES = {
    (0, 3, 1, 1, 1, 0, 0): (8, 2),
    (1, 2, 0, 2, 1, 0, 0): (12, 0),
    (1, 2, 1, 0, 2, 0, 0): (6, 0),
    (2, 1, 0, 1, 2, 0, 0): (6, 0),
}


def fail(msg):
    raise SystemExit("FAIL: " + msg)


def check(cond, msg):
    if not cond:
        fail(msg)


def mask_weight(sum_vec):
    bits = 0
    for value in sum_vec:
        if value not in ALLOWED_SET:
            return None
        bits += MASK_BIT[value]
    return bits


def weight3(sum_vec):
    return mask_weight(sum_vec) == 3


def signature(counts, delta):
    seen = Counter(zip(counts, delta))

    def n(count, step):
        return seen[(count, step)]

    return (
        n(0, 1),
        n(3, 1),
        n(0, 0),
        n(3, 0),
        n(6, 0),
        n(2, 2),
        n(2, 3),
    )


def caps_for(counts, limit):
    return tuple(min(3, limit - counts[i]) for i in range(K))


def deltas_product(cap):
    for delta in itertools.product(*(range(bound + 1) for bound in cap)):
        if sum(delta) == 3:
            yield delta


def deltas_recursive(cap):
    buf = [0] * K

    def rec(index, left):
        if index == K - 1:
            if 0 <= left <= cap[index]:
                buf[index] = left
                yield tuple(buf)
            return
        for step in range(min(cap[index], left) + 1):
            buf[index] = step
            yield from rec(index + 1, left - step)

    yield from rec(0, 3)


def prefix_counts(word, length):
    counts = [0] * K
    for source in word[:length]:
        counts[source] += 1
    return counts


def letters(counts):
    out = []
    for source, count in enumerate(counts):
        out.extend([source] * count)
    return out


def layered_word(*layers):
    word = []
    for layer in layers:
        word.extend(letters(layer))
    return word


def is_floor(word):
    return len(word) == K * C and sorted(word) == sorted(
        source for source in range(K) for _ in range(C)
    )


def add_signature(found, counts, delta):
    summed = tuple(2 * counts[i] + delta[i] for i in range(K))
    if not weight3(summed):
        return
    sig = signature(counts, delta)
    found[sig] += 1
    mask = [i for i, value in enumerate(summed) if value in (1, 7)]
    check(len(mask) == 3, f"weight drifted: {summed}")
    for source in range(K):
        if source in mask:
            check(delta[source] == 1, f"mask source missed the bridge: {counts} {delta}")
        else:
            check(delta[source] == 0, f"non-mask source used the bridge: {counts} {delta}")
    check(sig[5] == 0 and sig[6] == 0, f"repeated bridge letter survived: {sig}")


def census():
    by_product = Counter()
    by_recursive = Counter()
    vectors = 0
    bridges = 0
    widened_only = 0
    for counts in itertools.product(range(C + 1), repeat=K):
        if sum(counts) != 18:
            continue
        vectors += 1
        strict = caps_for(counts, C)
        loose = caps_for(counts, C + 1)
        for delta in deltas_product(strict):
            bridges += 1
            add_signature(by_product, counts, delta)
        recursive_hits = 0
        for delta in deltas_recursive(strict):
            recursive_hits += 1
            add_signature(by_recursive, counts, delta)
        check(recursive_hits == sum(1 for _ in deltas_product(strict)), "bridge enumerators diverged")
        for delta in deltas_product(loose):
            if any(counts[i] + delta[i] > C for i in range(K)):
                summed = [2 * counts[i] + delta[i] for i in range(K)]
                if weight3(summed):
                    widened_only += 1
    check(by_product == by_recursive, "signature censuses diverged")
    return vectors, bridges, by_product, widened_only


def price_prefix(prefix):
    ones = [i for i, value in enumerate(prefix) if value == 1]
    zeros = [i for i, value in enumerate(prefix) if value == 0]
    heavy = [i for i, value in enumerate(prefix) if value == 6]
    check(len(ones) == 3 and len(zeros) == 2 and len(heavy) == 1, f"not the explicit shape: {prefix}")
    totals = Counter()
    same = Counter()
    frozen = 0
    extensions = 0
    for add_one in itertools.product(range(C), repeat=3):
        for add_zero in itertools.product(range(C + 1), repeat=2):
            if sum(add_one) + sum(add_zero) != 9:
                continue
            counts = [0] * K
            counts[heavy[0]] = C
            for offset, source in enumerate(ones):
                counts[source] = 1 + add_one[offset]
            for offset, source in enumerate(zeros):
                counts[source] = add_zero[offset]
            if sum(counts) != 18 or any(value > C for value in counts):
                continue
            for delta in deltas_product(caps_for(counts, C)):
                summed = tuple(2 * counts[i] + delta[i] for i in range(K))
                if not weight3(summed):
                    continue
                extensions += 1
                sig = signature(counts, delta)
                totals[sig] += 1
                mask = tuple(i for i, value in enumerate(summed) if value in (1, 7))
                if mask == tuple(ones):
                    same[sig] += 1
                check(summed[heavy[0]] == 12 and delta[heavy[0]] == 0, "exhausted source did not freeze")
                check(12 in summed, "priced extension carries no 12")
                frozen += 1
    return extensions, totals, same, frozen


def main():
    controls = 0

    local = [
        (count, step)
        for count in range(C + 1)
        for step in range(4)
        if count + step <= C and (2 * count + step) in ALLOWED_SET
    ]
    check(local == [(0, 0), (0, 1), (2, 2), (2, 3), (3, 0), (3, 1), (6, 0)], f"local types: {local}")
    controls += 1

    length18 = math.comb(23, 5) - 6 * math.comb(16, 5) + math.comb(6, 2) * math.comb(9, 5)
    check(length18 == 9331, f"inclusion-exclusion changed: {length18}")
    controls += 1

    box = []
    for values in itertools.product(range(K + 1), repeat=7):
        n00, n01, n30, n22, n31, n23, n60 = values
        if n00 + n01 + n30 + n22 + n31 + n23 + n60 != K:
            continue
        if n01 + n31 + n23 != 3:
            continue
        if n01 + 2 * n22 + n31 + 3 * n23 != 3:
            continue
        if 3 * n30 + 2 * n22 + 3 * n31 + 2 * n23 + 6 * n60 != 18:
            continue
        box.append(values)
    expected_box = []
    for sig in TYPES:
        n01, n31, n00, n30, n60, n22, n23 = sig
        expected_box.append((n00, n01, n30, n22, n31, n23, n60))
    check(sorted(box) == sorted(expected_box), f"diophantine box: {box}")
    controls += 1

    vectors, bridges, found, widened_only = census()
    check(vectors == length18, f"length-18 census changed: {vectors}")
    check(bridges == 327216, f"bridge census changed: {bridges}")
    check(found == TYPES, f"type census changed: {dict(found)}")
    check(sum(found.values()) == 700, f"weight-3 total changed: {sum(found.values())}")
    check(widened_only == 0, f"cap-7 weight-3 pairs appeared: {widened_only}")
    controls += 1

    multinomial = {}
    for sig, predicted in TYPES.items():
        n01, n31, n00, n30, n60, n22, n23 = sig
        factors = [n01, n31, n00, n30, n60, n22, n23]
        check(sum(factors) == K and n22 == n23 == 0, f"type does not partition six coordinates: {sig}")
        orbit = math.factorial(K)
        for factor in factors:
            orbit //= math.factorial(factor)
        multinomial[sig] = orbit
        check(orbit == predicted, f"multinomial mismatch: {sig} {orbit} {predicted}")
    check(multinomial == TYPES, "orbit table drifted")
    controls += 1

    shape = Counter(EXPLICIT)
    shape_hits = 0
    for counts in itertools.product(range(C + 1), repeat=K):
        if sum(counts) != 9 or not weight3(counts):
            continue
        shape_hits += 1
        check(Counter(counts) == shape, f"unexpected (0,9) shape: {counts}")
    check(shape_hits == 60, f"(0,9) shape count changed: {shape_hits}")
    controls += 1

    diagonal = [3] * 6 + [4] * 6 + [5] * 6 + [0, 1, 2] + [0] * 5 + [1] * 5 + [2] * 5
    check(is_floor(diagonal), "separation-3 witness is not a floor word")
    q18 = prefix_counts(diagonal, 18)
    q21 = prefix_counts(diagonal, 21)
    sep = tuple(q18[i] + q21[i] for i in range(K))
    check(q18 == [0, 0, 0, 6, 6, 6] and sep == (1, 1, 1, 12, 12, 12), f"type T6 witness moved: {q18} {sep}")
    check(signature(q18, [q21[i] - q18[i] for i in range(K)]) == (3, 0, 0, 0, 3, 0, 0), "type T6 signature moved")
    controls += 1

    off = [3] * 6 + [0, 1, 2] + [0] * 5 + [1] * 5 + [2] * 5 + [4] * 6 + [5] * 6
    check(is_floor(off), "s+t=9 witness is not a floor word")
    q9 = prefix_counts(off, 9)
    off18 = prefix_counts(off, 18)
    off21 = prefix_counts(off, 21)
    off_sum = tuple(off18[i] + off21[i] for i in range(K))
    check(q9 == [1, 1, 1, 6, 0, 0] and weight3(q9), f"explicit mask moved: {q9}")
    check(off_sum == (12, 11, 4, 12, 0, 0) and not weight3(off_sum), f"explicit word gained a separation-3 mask: {off_sum}")
    controls += 1

    same_mask = [int(ch) for ch in "012333333001122444012001122444555555"]
    check(is_floor(same_mask), "same-mask word is not a floor word")
    check(prefix_counts(same_mask, 9) == [1, 1, 1, 6, 0, 0], "same-mask word lost the explicit prefix")
    same18 = prefix_counts(same_mask, 18)
    same21 = prefix_counts(same_mask, 21)
    same_sum = tuple(same18[i] + same21[i] for i in range(K))
    check(same_sum == (7, 7, 7, 12, 6, 0) and weight3(same_sum), f"same-mask sum moved: {same_sum}")
    controls += 1

    other_mask = [int(ch) for ch in "012333333001122444015001122244455555"]
    check(is_floor(other_mask), "different-mask word is not a floor word")
    check(prefix_counts(other_mask, 9) == [1, 1, 1, 6, 0, 0], "different-mask word lost the explicit prefix")
    other18 = prefix_counts(other_mask, 18)
    other21 = prefix_counts(other_mask, 21)
    other_sum = tuple(other18[i] + other21[i] for i in range(K))
    other_bits = tuple(i for i, value in enumerate(other_sum) if value in (1, 7))
    check(other_sum == (7, 7, 6, 12, 6, 1) and other_bits == (0, 1, 5), f"different mask moved: {other_sum}")
    controls += 1

    type1 = layered_word((3, 3, 3, 3, 3, 3), (1, 1, 1, 0, 0, 0), (2, 2, 2, 3, 3, 3))
    check(is_floor(type1), "type T1 word is not a floor word")
    t1_18 = prefix_counts(type1, 18)
    t1_21 = prefix_counts(type1, 21)
    t1_sum = tuple(t1_18[i] + t1_21[i] for i in range(K))
    check(t1_sum == (7, 7, 7, 6, 6, 6) and weight3(t1_sum) and 12 not in t1_sum, f"type T1 moved: {t1_sum}")
    check(not weight3(prefix_counts(type1, 9)), "type T1 word realized the explicit (0,9) mask")
    controls += 1

    orbit = set(itertools.permutations(EXPLICIT))
    check(len(orbit) == 60 and EXPLICIT in orbit, f"explicit orbit changed: {len(orbit)}")
    for prefix in orbit:
        extensions, totals, same, frozen = price_prefix(prefix)
        check(extensions == 32 and frozen == 32, f"price changed for {prefix}: {extensions}")
        check(set(totals) == set(PRICE_TYPES), f"priced types changed for {prefix}: {dict(totals)}")
        for sig, (total, same_count) in PRICE_TYPES.items():
            check(totals[sig] == total and same[sig] == same_count, f"price split changed for {prefix} {sig}")
    controls += 1

    shapes = {
        (0, 3, 0, 3, 0, 0, 0): (6, 6, 6, 7, 7, 7),
        (0, 3, 1, 1, 1, 0, 0): (0, 6, 7, 7, 7, 12),
        (1, 2, 0, 2, 1, 0, 0): (1, 6, 6, 7, 7, 12),
        (1, 2, 1, 0, 2, 0, 0): (0, 1, 7, 7, 12, 12),
        (2, 1, 0, 1, 2, 0, 0): (1, 1, 6, 7, 12, 12),
        (3, 0, 0, 0, 3, 0, 0): (1, 1, 1, 12, 12, 12),
    }
    expected_moves = 0
    for sig, orbit in TYPES.items():
        shape = shapes[sig]
        increasable = sum(1 for value in shape if value in (0, 6))
        decreasable = sum(1 for value in shape if value in (1, 7))
        expected_moves += orbit * increasable * decreasable
    preserved = 0
    type1_moves = 0
    for counts in itertools.product(range(C + 1), repeat=K):
        if sum(counts) != 18:
            continue
        for delta in deltas_product(caps_for(counts, C)):
            summed = [2 * counts[i] + delta[i] for i in range(K)]
            if not weight3(summed):
                continue
            for source in range(K):
                if summed[source] != 12:
                    continue
                for direction in (1, -1):
                    moved = list(summed)
                    moved[source] += direction
                    check(mask_weight(moved) is None, "a frozen 12 moved inside the allowed set")
            for early, late in itertools.product(range(K), repeat=2):
                if early == late:
                    continue
                moved = list(summed)
                moved[early] += 1
                moved[late] -= 1
                if mask_weight(moved) is None:
                    continue
                for source in range(K):
                    if summed[source] == 12:
                        check(moved[source] == 12, "legal diagonal step moved a 12")
                preserved += 1
            if Counter(summed) == Counter((6, 6, 6, 7, 7, 7)):
                for early in range(K):
                    for late in range(K):
                        if summed[early] != 6 or summed[late] != 7:
                            continue
                        moved = list(summed)
                        moved[early] += 1
                        moved[late] -= 1
                        check(Counter(moved) == Counter(summed), "type T1 multiset was not closed")
                        type1_moves += 1
    check(
        preserved == expected_moves and type1_moves == 20 * 3 * 3,
        f"move census changed: preserved={preserved} expected={expected_moves} type1={type1_moves}",
    )
    controls += 1

    short_pairs = 0
    for early in itertools.product(range(5), repeat=K):
        if sum(early) != 4:
            continue
        for missing in range(K):
            short_pairs += 1
            for source in range(K):
                late = 5 if source == missing else 6
                total = early[source] + late
                check(total <= 10 and total != 12, f"length-4 pair reached 12: {early} {missing}")
    check(short_pairs == 126 * 6, f"length-4 domain changed: {short_pairs}")
    controls += 1

    check(not weight3((2, 1, 0, 12, 12, 12)), "a coordinate 2 was accepted")
    check(2 * 5 + 2 == 12 and 5 + 2 > C, "the (5,2) local pair is no longer outside the cap")
    controls += 1

    check(controls == 15, f"control count changed: {controls}")
    print(
        "PASS_SIX_SOURCE_C6_SEPARATION3_CLASSIFICATION "
        f"vectors={vectors} bridges={bridges} weight3={sum(found.values())} "
        f"types=20+120+180+180+180+20 widened_only={widened_only} "
        f"pair09={shape_hits} priced_extensions=32 same_mask=2 orbit=60 "
        f"moves_preserving_12={preserved} type1_moves={type1_moves} "
        f"short_pairs={short_pairs} controls={controls}"
    )


if __name__ == "__main__":
    main()
