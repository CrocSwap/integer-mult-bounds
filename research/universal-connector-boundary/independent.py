#!/usr/bin/env python3
"""Independent exact census through matchings of endpoint positions.

No generator or certificate code is imported.  The search objects are perfect
matchings of 2*n numbered positions, not restricted-growth source words.
Each matching is labelled only after it has been completed, in order of its
left endpoints.  Coverage is computed by directly XORing every pair of
prefix states.  A separate scalar replay checks dirty-connector cancellation
for every input and dirty initial value on each reported witness.

This is an exhaustive finite combinatorial verification, not a formal proof
of the conditional integer-multiplication theorem.

SPDX-License-Identifier: Apache-2.0
Contributor: Ross, with substantial OpenAI Codex assistance.
"""

import argparse
from collections import Counter
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def endpoint_matchings(points):
    """Generate each perfect matching once, pairing the least unused point."""
    if not points:
        yield ()
        return
    first = points[0]
    for partner in points[1:]:
        remaining = tuple(p for p in points if p != first and p != partner)
        for tail in endpoint_matchings(remaining):
            yield ((first, partner),) + tail


def matching_word(pairs, n):
    word = [None] * (2 * n)
    for label, (left, right) in enumerate(sorted(pairs)):
        word[left] = label
        word[right] = label
    return tuple(word)


def prefix_states(word, n):
    if n < 1 or len(word) != 2 * n:
        raise ValueError("a source word must contain 2*n positions for n >= 1")
    if Counter(word) != Counter({j: 2 for j in range(n)}):
        raise ValueError("each source label 0,...,n-1 must occur exactly twice")
    states = [0]
    for label in word:
        states.append(states[-1] ^ (1 << label))
    require(states[-1] == 0, "source word failed connector restoration")
    return states


def available(word, n):
    """Return attainable row masks, including the zero mask."""
    states = prefix_states(word, n)
    return {first ^ second for first in states for second in states}


def pairing_covers(n):
    """Yield (canonical word, integer with bit m set for each covered mask m)."""
    if n < 1:
        raise ValueError("n must be positive")
    for pairs in endpoint_matchings(tuple(range(2 * n))):
        word = matching_word(pairs, n)
        covered = available(word, n)
        yield word, sum(1 << mask for mask in covered)


def census(n):
    histogram = Counter()
    total = 0
    best_word = None
    best_cover = 0
    maximum = -1
    for word, covered in pairing_covers(n):
        count = covered.bit_count()
        histogram[count] += 1
        total += 1
        if count > maximum:
            maximum, best_word, best_cover = count, word, covered
    expected = 1
    for factor in range(1, 2 * n, 2):
        expected *= factor
    require(total == expected, ("matching count", total, expected))
    return {
        "pairings": total,
        "histogram": {str(k): histogram[k] for k in sorted(histogram)},
        "max_coverage": maximum,
        "best_word": list(best_word),
        "missing": [mask for mask in range(1 << n) if not best_cover >> mask & 1],
    }


def replay_scalar(word, n):
    """Replay actual bit operations for every input/dirty value on every row.

    For each attainable nonzero row, choose one pair of boundaries, read the
    scalar connector there into a dirty output, and toggle the sources along
    the word.  Test both dirty connector and dirty output initial bits and
    every source assignment.  This intentionally does not update a symbolic
    prefix mask during the replay.
    """
    states = prefix_states(word, n)
    read_pairs = {}
    for first in range(len(states)):
        for second in range(first + 1, len(states)):
            mask = states[first] ^ states[second]
            if mask:
                read_pairs.setdefault(mask, (first, second))
    cases = 0
    for mask, (first, second) in read_pairs.items():
        for source_bits in range(1 << n):
            intended = 0
            for j in range(n):
                if mask >> j & 1:
                    intended ^= source_bits >> j & 1
            for initial_connector in (0, 1):
                for initial_output in (0, 1):
                    connector = initial_connector
                    output = initial_output
                    for boundary in range(len(word) + 1):
                        if boundary == first or boundary == second:
                            output ^= connector
                        if boundary < len(word):
                            connector ^= source_bits >> word[boundary] & 1
                    require(connector == initial_connector, "scalar connector restoration")
                    require(output == initial_output ^ intended, "scalar row mismatch")
                    cases += 1
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=int, default=5, choices=range(1, 7))
    args = parser.parse_args()
    result = census(args.sources)
    result["scalar_replay_cases"] = replay_scalar(result["best_word"], args.sources)
    if args.sources == 5:
        require(result["pairings"] == 945, "five-source pairing count")
        require(result["max_coverage"] == 31, "five-source maximum coverage")
        require(result["histogram"] == {
            "16": 42, "19": 120, "21": 180, "22": 56, "23": 45,
            "24": 220, "26": 110, "28": 150, "31": 22,
        }, "five-source complete coverage histogram")
        universal_four = (0, 1, 0, 1, 2, 3, 2, 3)
        require(available(universal_four, 4) == set(range(16)), "universal four coverage")
        result["universal_four_scalar_replay_cases"] = replay_scalar(universal_four, 4)
        # A legal double-occurrence mutation must be detected as nonuniversal.
        adjacent_pairs = (0, 0, 1, 1, 2, 2, 3, 3)
        require(len(available(adjacent_pairs, 4)) == 11, "legal word mutation control")
        result["legal_word_negative_control_coverage"] = 11
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
