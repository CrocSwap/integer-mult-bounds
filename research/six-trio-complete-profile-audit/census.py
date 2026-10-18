"""Multiplicity-first complete census, separately written by ywz65/Codex.

Apache-2.0. Does not import a predecessor enumerator.
"""
from collections import Counter
from itertools import combinations_with_replacement
from math import factorial, prod

MASKS = (0x5555555555555555, 0x3333333333333333, 0x0f0f0f0f0f0f0f0f,
         0x00ff00ff00ff00ff, 0x0000ffff0000ffff, 0x00000000ffffffff)
TRANSLATIONS = [[(1 << bit, MASKS[bit]) for bit in range(6) if delta & (1 << bit)]
                for delta in range(64)]


def translate(occupied, delta):
    for step, mask in TRANSLATIONS[delta]:
        occupied = ((occupied & mask) << step) | ((occupied >> step) & mask)
    return occupied


def profiles():
    return [p for p in combinations_with_replacement(range(1, 9), 6)
            if sum(p) == 13 and sum(c % 2 for c in p) == 3]


def profile_size(profile):
    return factorial(13) // (prod(factorial(c) for c in profile)
                             * prod(factorial(m) for m in Counter(profile).values()))


def enumerate_profiles():
    result = []
    for profile in profiles():
        remaining = list(profile)
        histogram = Counter()
        previous_equal = [i-1 if i and profile[i] == profile[i-1] else -1 for i in range(6)]

        def visit(depth, state, occupied, cover):
            if depth == 13:
                histogram[(cover & ~1).bit_count()] += 1
                return
            for label in range(6):
                if not remaining[label]:
                    continue
                previous = previous_equal[label]
                if (previous >= 0 and remaining[label] == profile[label]
                        and remaining[previous] == profile[previous]):
                    continue
                remaining[label] -= 1
                new_state = state ^ (1 << label)
                translated = occupied
                for step, mask in TRANSLATIONS[new_state]:
                    translated = ((translated & mask) << step) | ((translated >> step) & mask)
                visit(depth + 1, new_state, occupied | (1 << new_state), cover | translated)
                remaining[label] += 1

        visit(0, 0, 1, 0)
        if sum(histogram.values()) != profile_size(profile):
            raise ValueError("multiplicity quotient count differs from combinatorial count")
        result.append({"counts": list(profile),
                       "histogram": {str(k): v for k, v in sorted(histogram.items())}})
    return result
