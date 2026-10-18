#!/usr/bin/env python3
"""Code-disjoint multiset-recursion replay of the Q5 mask census."""
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
CERT = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
LABELS = (1, 2, 4, 8, 16)
Q5 = 31
CASES = (
    ("m7_one_triple", (3, 1, 1, 1, 1), 5),
    ("m9_one_quintuple", (5, 1, 1, 1, 1), 5),
    ("m9_two_triples", (3, 3, 1, 1, 1), 10),
)


def multiset_orders(counts):
    left = list(counts)
    prefix = []

    def visit():
        if not any(left):
            yield tuple(prefix)
            return
        for i, amount in enumerate(left):
            if amount:
                left[i] -= 1
                prefix.append(LABELS[i])
                yield from visit()
                prefix.pop()
                left[i] += 1

    yield from visit()


def set_of_pair_differences(word):
    points = [0]
    for step in word:
        points.append(points[-1] ^ step)
    if points[-1] != 0:
        raise AssertionError("restoration parity failed")
    distinct = set()
    for later in range(1, len(points)):
        for earlier in range(later):
            value = points[later] ^ points[earlier]
            if value:
                distinct.add(value)
    return distinct


def replay_case(name, counts, orbit_size):
    histogram = Counter()
    number = 0
    maximum = -1
    witness = None
    singleton_calls = sum(counts)
    for order in multiset_orders(counts):
        for position in range(singleton_calls + 1):
            word = order[:position] + (Q5,) + order[position:]
            coverage = len(set_of_pair_differences(word))
            histogram[coverage] += 1
            number += 1
            if coverage > maximum:
                maximum, witness = coverage, list(word)
    return {
        "case": name,
        "representative_words": number,
        "labeled_words": number * orbit_size,
        "representative_histogram": dict(sorted(histogram.items())),
        "max_nonzero_pair_differences": maximum,
        "maximizing_word": witness,
    }


def main():
    recorded = CERT["one_q5_source_walks"]
    actual_cases = [replay_case(*case) for case in CASES]
    expected_cases = [recorded["m7_census"], *recorded["m9_censuses"]]
    for actual, expected in zip(actual_cases, expected_cases):
        for key, value in actual.items():
            expected_value = expected.get(key)
            if key == "representative_histogram" and expected_value is not None:
                expected_value = {int(k): v for k, v in expected_value.items()}
            if expected_value != value:
                raise AssertionError("%s mismatch for %s: %r != %r" % (actual["case"], key, value, expected_value))
    if sum(case["labeled_words"] for case in actual_cases[:1]) != 33600:
        raise AssertionError("m=7 orbit count")
    if sum(case["labeled_words"] for case in actual_cases[1:]) != 1159200:
        raise AssertionError("m=9 orbit count")
    if max(case["max_nonzero_pair_differences"] for case in actual_cases[:1]) != 20:
        raise AssertionError("m=7 maximum")
    if max(case["max_nonzero_pair_differences"] for case in actual_cases[1:]) != 27:
        raise AssertionError("m=9 maximum")
    print("PASS_QUINT_TOGGLE_INDEPENDENT m7=33600:max20 m9=1159200:max27")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
