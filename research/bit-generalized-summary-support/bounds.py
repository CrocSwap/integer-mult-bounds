"""Exact necessary rank and support bounds for the fixed catalogue."""
from fractions import Fraction
from itertools import combinations_with_replacement
from math import comb

CAP = 4096
TARGET = Fraction("0.0040075385047236")
CAPACITY = {1: 1, 2: 2, 4: 12, 6: 30, 7: 62, 8: 111}
RANKS = sorted(CAPACITY)


def ceil(q):
    return -(-q.numerator // q.denominator)


def profiles(k):
    limit = 7 * k - 2
    for largest in RANKS:
        tail_ranks = [r for r in RANKS if r <= largest]
        capacity = [0]
        for m in range(1, limit + 1):
            capacity.append(max(capacity[m-r] + CAPACITY[r] for r in tail_ranks if r <= m))

        def finish(i, remaining, support, tail):
            if support + capacity[remaining] < 48:
                return
            if i == len(tail_ranks):
                if support >= 48:
                    yield tuple(tail)
                return
            rank = tail_ranks[i]
            for count in range(remaining // rank + 1):
                yield from finish(i + 1, remaining - count * rank,
                                  support + count * CAPACITY[rank], [*tail, *([rank] * count)])

        for first in combinations_with_replacement([r for r in RANKS if r >= largest], k - 1):
            remaining = limit - sum(first) - largest
            if remaining < 0:
                break
            for tail in finish(0, remaining, CAPACITY[largest], []):
                yield (*reversed(first), largest, *reversed(tail))


def incidence_lower(collectors, dimension):
    fiber = 2**(9 - dimension)
    nonzero = 112 - fiber
    represented = total = 0
    for degree in range(collectors + 1):
        if degree:
            represented += comb(collectors, degree)
        total += max(0, nonzero - fiber * represented)
    return total
