#!/usr/bin/env python3
"""Weight-3 sums at (1, 14), and one shape against the six families.

The written argument is in README.md. This program enumerates every legal
pair (q_14, q_1) and every cap-respecting bridge from the shape
(0, 0, 1, 1, 6, 7) to the slot (18, 21). It does not search depth-two words
and it does not call a SAT solver.
"""

import itertools
from math import comb

K = 6
CAP = 6
LENGTH = 14
GAP_TO_18 = 4
GAP_TO_21 = 3
ALLOWED = (0, 1, 6, 7, 12)
ALLOWED_SET = set(ALLOWED)
MASK_BIT = {0: 0, 1: 1, 6: 0, 7: 1, 12: 0}

# Tested shape of q_1 + q_14, and the length-14 prefix it determines.
SHAPE = (7, 6, 1, 1, 0, 0)
SORTED_SHAPE = tuple(sorted(SHAPE))
Q14 = (6, 6, 1, 1, 0, 0)
SORTED_Q14 = tuple(sorted(Q14))

# The other weight-3 shape at this pair. Counted in the list, not extended.
SHAPE_A = (6, 6, 1, 1, 1, 0)
SORTED_SHAPE_A = tuple(sorted(SHAPE_A))
Q14_A = (6, 5, 1, 1, 1, 0)
SORTED_Q14_A = tuple(sorted(Q14_A))

# Recorded q_18 multisets of the six separation-3 families in PR #7029.
# T2 and T3 share a multiset, as do T4 and T5.
FAMILY_Q18 = {
    "T1": (3, 3, 3, 3, 3, 3),
    "T2": (0, 3, 3, 3, 3, 6),
    "T3": (0, 3, 3, 3, 3, 6),
    "T4": (0, 0, 3, 3, 6, 6),
    "T5": (0, 0, 3, 3, 6, 6),
    "T6": (0, 0, 0, 6, 6, 6),
}

# One floor word realizing the tested shape, the (0, 9) mask, and a 12 at
# (18, 21). It is a witness for the extension, not a depth-two word.
WITNESS = "000000123111112233234223344444555555"
# Separation-3 witness from the c=6 centre note. Its q_14 is not this shape.
SEPARATION3_WORD = "333333444444555555012000001111122222"
# Off-diagonal witness. Weight 3 at (0, 9), not at (18, 21).
PAIR09_WORD = "333333012000001111122222444444555555"

ZERO_PREFIX = (0, 0, 1, 4, 4, 5)
T1_PREFIX = (2, 2, 2, 2, 3, 3)
T1_EPSILON = (1, 1, 1, 1, 0, 0)
T1_DELTA = (1, 1, 1, 0, 0, 0)

WITNESS_HITS = (
    ((0, 0, 2, 2, 0, 0), (0, 0, 0, 1, 1, 1)),
    ((0, 0, 2, 2, 0, 0), (0, 0, 1, 0, 1, 1)),
    ((0, 0, 2, 2, 0, 0), (0, 0, 1, 1, 0, 1)),
    ((0, 0, 2, 2, 0, 0), (0, 0, 1, 1, 1, 0)),
)
EXPECTED_SUMS = {
    (0, 1, 7, 7, 12, 12): 2,
    (1, 1, 6, 7, 12, 12): 2,
}
EXPECTED_ROWS = {
    ((0, 0), (0, 1), (3, 1), (3, 1), (6, 0), (6, 0)): 2,
    ((0, 1), (0, 1), (3, 0), (3, 1), (6, 0), (6, 0)): 2,
}


def fail(message):
    raise SystemExit("FAIL: " + message)


def mask_weight(values):
    bits = 0
    for value in values:
        if value not in ALLOWED_SET:
            return None
        bits += MASK_BIT[value]
    return bits


def weight3(values):
    return mask_weight(values) == 3


def bounded_count(total, cap=CAP, slots=K):
    """Inclusion-exclusion count of {0,...,cap}^slots summing to total."""
    found = 0
    for excised in range(total // (cap + 1) + 1):
        rest = total - excised * (cap + 1)
        sign = 1 if excised % 2 == 0 else -1
        found += sign * comb(slots, excised) * comb(rest + slots - 1, slots - 1)
    return found


def compositions(total, caps):
    """Every tuple with 0 <= entry <= caps[i] and coordinate sum total."""

    def rec(index, remain):
        last = index == len(caps) - 1
        if last:
            if 0 <= remain <= caps[index]:
                yield (remain,)
            return
        for value in range(min(caps[index], remain) + 1):
            for tail in rec(index + 1, remain - value):
                yield (value,) + tail

    yield from rec(0, total)


def bridge_caps(prefix, gap):
    caps = tuple(CAP - value for value in prefix)
    if any(cap < 0 for cap in caps):
        return None
    return tuple(min(gap, cap) for cap in caps)


def bridges(prefix, gap):
    caps = bridge_caps(prefix, gap)
    if caps is None:
        return
    yield from compositions(gap, caps)


def product_bridges(prefix, gap):
    caps = bridge_caps(prefix, gap)
    if caps is None:
        return
    ranges = [range(cap + 1) for cap in caps]
    for values in itertools.product(*ranges):
        if sum(values) == gap:
            yield values


def add(left, right):
    return tuple(left[j] + right[j] for j in range(K))


def separation_sum(q18, delta):
    return tuple(2 * q18[j] + delta[j] for j in range(K))


def extension_census(prefix, bridge_fn):
    trials = 0
    hits = 0
    with_twelve = 0
    frozen_ok = 0
    hit_pairs = []
    sum_counts = {}
    row_counts = {}
    frozen = tuple(index for index in range(K) if prefix[index] == CAP)
    for epsilon in bridge_fn(prefix, GAP_TO_18):
        q18 = add(prefix, epsilon)
        for delta in bridge_fn(q18, GAP_TO_21):
            trials += 1
            summed = separation_sum(q18, delta)
            if frozen and all(summed[index] == 12 for index in frozen):
                frozen_ok += 1
            if 12 in summed:
                with_twelve += 1
            if weight3(summed):
                hits += 1
                hit_pairs.append((epsilon, delta))
                key = tuple(sorted(summed))
                sum_counts[key] = sum_counts.get(key, 0) + 1
                rows = tuple(sorted((q18[index], delta[index]) for index in range(K)))
                row_counts[rows] = row_counts.get(rows, 0) + 1
    return {
        "trials": trials,
        "hits": hits,
        "with_twelve": with_twelve,
        "frozen_ok": frozen_ok,
        "hit_pairs": hit_pairs,
        "sums": sum_counts,
        "rows": row_counts,
    }


def prefix_counts(word, length):
    counts = [0] * K
    for source in word[:length]:
        counts[int(source)] += 1
    return tuple(counts)


def reachable(prefix, target, gap):
    for perm in set(itertools.permutations(target)):
        if all(prefix[j] <= perm[j] <= min(CAP, prefix[j] + gap) for j in range(K)):
            return True
    return False


def family_solutions():
    """Nonnegative solutions of the recorded three-letter budget equations."""
    found = []
    for counts in itertools.product(range(K + 1), repeat=5):
        n01, n31, n00, n30, n60 = counts
        if n01 + n31 != 3:
            continue
        if n00 + n30 + n60 != 3:
            continue
        if 3 * n30 + 3 * n31 + 6 * n60 != 18:
            continue
        coords = (
            (0,) * n01
            + (3,) * n31
            + (0,) * n00
            + (3,) * n30
            + (6,) * n60
        )
        if len(coords) != K:
            fail("family coordinate count drifted")
        found.append({"counts": counts, "q18": tuple(sorted(coords))})
    return found


def constructed_pairs():
    shape_b = set()
    for counts in set(itertools.permutations(Q14)):
        for index, value in enumerate(counts):
            if value == CAP:
                shape_b.add((counts, index))
    shape_a = set()
    for counts in set(itertools.permutations(Q14_A)):
        for index, value in enumerate(counts):
            if value == 5:
                shape_a.add((counts, index))
    return shape_b, shape_a


def scan_pairs():
    vectors = 0
    legal_pairs = 0
    shape_b = set()
    shape_a = set()
    other = []
    for counts in itertools.product(range(CAP + 1), repeat=K):
        if sum(counts) != LENGTH:
            continue
        vectors += 1
        for index in range(K):
            if counts[index] < 1:
                continue
            legal_pairs += 1
            summed = list(counts)
            summed[index] += 1
            if not weight3(summed):
                continue
            key = tuple(sorted(summed))
            item = (counts, index)
            if key == SORTED_SHAPE:
                shape_b.add(item)
            elif key == SORTED_SHAPE_A:
                shape_a.add(item)
            else:
                other.append((item, key))
    return vectors, legal_pairs, shape_b, shape_a, other


def main():
    controls = 0

    if not weight3(SHAPE) or tuple(sorted(SHAPE)) != SORTED_SHAPE:
        fail("tested shape is not the named weight-3 mask")
    if add(Q14, (1, 0, 0, 0, 0, 0)) != SHAPE:
        fail("tested prefix does not produce the named shape")
    controls += 1
    if weight3((2, 1, 1, 6, 6, 0)):
        fail("a coordinate equal to 2 was accepted")
    controls += 1
    if weight3((11, 1, 1, 1, 1, 0)) or weight3((13, 1, 1, 0, 0, 0)):
        fail("a coordinate equal to 11 or 13 was accepted")
    controls += 1
    if not weight3(SHAPE_A):
        fail("the other total-15 shape was rejected")
    if not weight3((12, 1, 1, 1, 0, 0)) or max((12, 1, 1, 1, 0, 0)) <= CAP:
        fail("the sum-15 residue with a 12 is not an illegal prefix coordinate")
    controls += 1

    closed_vectors = bounded_count(LENGTH)
    closed_pairs = 6 * (bounded_count(13) - bounded_count(7, slots=5))
    vectors, legal_pairs, shape_b, shape_a, other = scan_pairs()
    if (vectors, closed_vectors) != (6891, 6891):
        fail(f"length-14 census changed: enumerated={vectors} closed={closed_vectors}")
    controls += 1
    if (legal_pairs, closed_pairs) != (32826, 32826):
        fail(f"legal pair census changed: enumerated={legal_pairs} closed={closed_pairs}")
    controls += 1
    built_b, built_a = constructed_pairs()
    if other or shape_b != built_b or shape_a != built_a:
        fail(
            "weight-3 pair list changed: "
            f"B={len(shape_b)} A={len(shape_a)} other={len(other)}"
        )
    if (len(shape_b), len(shape_a)) != (180, 120):
        fail(f"weight-3 orbit sizes changed: B={len(shape_b)} A={len(shape_a)}")
    controls += 1

    solutions = family_solutions()
    got = sorted(item["counts"] for item in solutions)
    expected_counts = [
        (0, 3, 0, 3, 0),
        (0, 3, 1, 1, 1),
        (1, 2, 0, 2, 1),
        (1, 2, 1, 0, 2),
        (2, 1, 0, 1, 2),
        (3, 0, 0, 0, 3),
    ]
    if got != expected_counts:
        fail(f"family equations changed: {got}")
    by_counts = {item["counts"]: item["q18"] for item in solutions}
    if by_counts != {
        (0, 3, 0, 3, 0): FAMILY_Q18["T1"],
        (0, 3, 1, 1, 1): FAMILY_Q18["T2"],
        (1, 2, 0, 2, 1): FAMILY_Q18["T3"],
        (1, 2, 1, 0, 2): FAMILY_Q18["T4"],
        (2, 1, 0, 1, 2): FAMILY_Q18["T5"],
        (3, 0, 0, 0, 3): FAMILY_Q18["T6"],
    }:
        fail(f"q_18 multisets changed: {by_counts}")
    controls += 1

    reached = sorted(name for name, target in FAMILY_Q18.items() if reachable(Q14, target, GAP_TO_18))
    if reached != ["T4", "T5"]:
        fail(f"family reachability changed: {reached}")
    controls += 1

    first_caps = bridge_caps(Q14, GAP_TO_18)
    if first_caps != (0, 0, 4, 4, 4, 4):
        fail(f"first-gap caps changed: {first_caps}")
    first_bridges = list(bridges(Q14, GAP_TO_18))
    if len(first_bridges) != 35 or len(first_bridges) != comb(7, 3):
        fail(f"first-gap bridge count changed: {len(first_bridges)}")
    if set(first_bridges) != set(product_bridges(Q14, GAP_TO_18)):
        fail("composition and product enumerators disagree on the first gap")
    controls += 1

    representative = extension_census(Q14, bridges)
    representative_product = extension_census(Q14, product_bridges)
    if set(representative["hit_pairs"]) != set(representative_product["hit_pairs"]):
        fail("composition and product enumerators disagree on the representative")
    if representative["trials"] != 684 or representative["hits"] != 4:
        fail(
            "representative census changed: "
            f"trials={representative['trials']} hits={representative['hits']}"
        )
    if representative["with_twelve"] != 684 or representative["frozen_ok"] != 684:
        fail(
            "representative 12-count changed: "
            f"with_twelve={representative['with_twelve']} "
            f"frozen_ok={representative['frozen_ok']}"
        )
    if representative["sums"] != EXPECTED_SUMS or representative["rows"] != EXPECTED_ROWS:
        fail(
            "representative hit types changed: "
            f"sums={representative['sums']} rows={representative['rows']}"
        )
    if set(representative["hit_pairs"]) != set(WITNESS_HITS):
        fail(f"representative hit bridges changed: {representative['hit_pairs']}")
    controls += 1

    orbit = set(itertools.permutations(Q14))
    if len(orbit) != 90 or Q14 not in orbit:
        fail(f"q_14 orbit changed: {len(orbit)}")
    orbit_trials = 0
    orbit_hits = 0
    orbit_twelves = 0
    orbit_frozen = 0
    for counts in orbit:
        item = extension_census(counts, bridges)
        orbit_trials += item["trials"]
        orbit_hits += item["hits"]
        orbit_twelves += item["with_twelve"]
        orbit_frozen += item["frozen_ok"]
        if item["trials"] != representative["trials"] or item["hits"] != 4:
            fail(f"orbit member census changed at {counts}")
        if item["sums"] != EXPECTED_SUMS or item["frozen_ok"] != item["trials"]:
            fail(f"orbit member types changed at {counts}")
    if (orbit_trials, orbit_hits, orbit_twelves, orbit_frozen) != (61560, 360, 61560, 61560):
        fail(
            "orbit census changed: "
            f"trials={orbit_trials} hits={orbit_hits} "
            f"twelves={orbit_twelves} frozen={orbit_frozen}"
        )
    controls += 1

    if tuple(sorted(ZERO_PREFIX)) in {SORTED_Q14, SORTED_Q14_A} or sum(ZERO_PREFIX) != LENGTH:
        fail("zero-hit control is not a distinct length-14 vector")
    zero = extension_census(ZERO_PREFIX, bridges)
    zero_product = extension_census(ZERO_PREFIX, product_bridges)
    if (zero["trials"], zero["hits"]) != (3208, 0):
        fail(f"zero-hit control changed: trials={zero['trials']} hits={zero['hits']}")
    if (zero_product["trials"], zero_product["hits"]) != (3208, 0):
        fail("product enumerator disagrees on the zero-hit control")
    controls += 1

    if tuple(sorted(T1_PREFIX)) in {SORTED_Q14, SORTED_Q14_A} or sum(T1_PREFIX) != LENGTH:
        fail("T1 control is not a distinct length-14 vector")
    q18_t1 = add(T1_PREFIX, T1_EPSILON)
    summed_t1 = separation_sum(q18_t1, T1_DELTA)
    if q18_t1 != (3, 3, 3, 3, 3, 3) or summed_t1 != (7, 7, 7, 6, 6, 6) or not weight3(summed_t1):
        fail(f"explicit T1 bridge changed: q18={q18_t1} sum={summed_t1}")
    if 12 in summed_t1:
        fail("explicit T1 bridge contains a 12")
    t1 = extension_census(T1_PREFIX, bridges)
    t1_product = extension_census(T1_PREFIX, product_bridges)
    if (t1["trials"], t1["hits"], t1["with_twelve"]) != (6220, 20, 488):
        fail(
            "T1 control changed: "
            f"trials={t1['trials']} hits={t1['hits']} twelves={t1['with_twelve']}"
        )
    t1_hit_twelves = sum(count for key, count in t1["sums"].items() if 12 in key)
    if t1["sums"] != {(6, 6, 6, 7, 7, 7): 20} or t1_hit_twelves != 0:
        fail(f"T1 hit types changed: {t1['sums']}")
    if (t1_product["trials"], t1_product["hits"], t1_product["sums"]) != (
        t1["trials"],
        t1["hits"],
        t1["sums"],
    ):
        fail("product enumerator disagrees on the T1 control")
    controls += 1

    if len(WITNESS) != 36 or len(SEPARATION3_WORD) != 36 or len(PAIR09_WORD) != 36:
        fail("witness word length changed")
    for word in (WITNESS, SEPARATION3_WORD, PAIR09_WORD):
        if prefix_counts(word, 36) != (CAP,) * K:
            fail(f"witness is not a six-source floor word: {word}")
    controls += 1
    q1 = prefix_counts(WITNESS, 1)
    q4 = prefix_counts(WITNESS, 4)
    q9 = prefix_counts(WITNESS, 9)
    q14 = prefix_counts(WITNESS, 14)
    q18 = prefix_counts(WITNESS, 18)
    q21 = prefix_counts(WITNESS, 21)
    q35 = prefix_counts(WITNESS, 35)
    witness_sum = separation_sum(q18, tuple(q21[j] - q18[j] for j in range(K)))
    shape_sum = add(q1, q14)
    endpoint = add(q4, q35)
    if q14 != Q14 or shape_sum != SHAPE or not weight3(shape_sum):
        fail(f"witness shape changed: q14={q14} sum={shape_sum}")
    if q9 != (6, 1, 1, 1, 0, 0) or not weight3(q9):
        fail(f"witness (0, 9) mask changed: {q9}")
    if witness_sum != (12, 12, 7, 7, 1, 0) or not weight3(witness_sum):
        fail(f"witness separation sum changed: {witness_sum}")
    if endpoint != (10, 6, 6, 6, 6, 5) or weight3(endpoint):
        fail(f"witness S(4) changed: {endpoint}")
    if add(q9, (0, 5, 0, 0, 0, 0)) != q14:
        fail("witness does not realize the recorded five-letter alignment")
    controls += 1

    q14_sep = prefix_counts(SEPARATION3_WORD, 14)
    q18_sep = prefix_counts(SEPARATION3_WORD, 18)
    q21_sep = prefix_counts(SEPARATION3_WORD, 21)
    sep_sum = tuple(q18_sep[j] + q21_sep[j] for j in range(K))
    if q14_sep == Q14 or not weight3(sep_sum) or sep_sum != (1, 1, 1, 12, 12, 12):
        fail(f"separation-3 witness changed: q14={q14_sep} sum={sep_sum}")
    controls += 1
    q9_off = prefix_counts(PAIR09_WORD, 9)
    q18_off = prefix_counts(PAIR09_WORD, 18)
    q21_off = prefix_counts(PAIR09_WORD, 21)
    off_sum = tuple(q18_off[j] + q21_off[j] for j in range(K))
    if q9_off != (1, 1, 1, 6, 0, 0) or weight3(off_sum):
        fail(f"(0, 9) witness changed: q9={q9_off} separation={off_sum}")
    controls += 1

    if 4 + CAP >= 12:
        fail("the s=4 coordinate bound no longer excludes 12")
    controls += 1

    if controls != 19:
        fail(f"control count changed: {controls}")

    print(
        "PASS_SIX_SOURCE_C6_SUM15_PAIR114 "
        f"vectors={vectors} pairs={legal_pairs} "
        f"weight3_shape_b={len(shape_b)} weight3_shape_a={len(shape_a)} "
        f"shape={SORTED_SHAPE} q14={SORTED_Q14} "
        f"families=6 family_hits={len(reached)} "
        f"shape_trials={orbit_trials} shape_extensions={orbit_hits} "
        f"shape_extension_twelves={orbit_hits} "
        f"all_extension_sums_with_twelve={orbit_twelves} "
        f"live_zero_hits={zero['hits']} live_t1_hits={t1['hits']} "
        f"live_t1_twelves={t1_hit_twelves} controls={controls}"
    )


if __name__ == "__main__":
    main()
