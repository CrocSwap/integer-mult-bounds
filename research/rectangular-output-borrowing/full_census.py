#!/usr/bin/env python3
"""Direct full-word census replay; Apache-2.0, OpenAI Codex assistance.

Standalone deeper check: no imports from the emitter or other oracles. A/B
encode A0/A1 and C/D encode B0/B1. Query IDs index QUERIES below; the digest
covers sorted 12-byte ID words, with no separators (all words have length 12).
"""
from collections import Counter, defaultdict
import hashlib
from itertools import permutations
from math import comb, factorial


QUERIES = (
    (1, 'A', 3, 2), (-1, 'A', 3, 2),
    (1, 'B', 2, 3), (-1, 'B', 2, 3),
    (1, 'C', 0, 2), (-1, 'C', 0, 2),
    (1, 'C', 0, 3), (-1, 'C', 0, 3),
    (1, 'D', 1, 2), (-1, 'D', 1, 2),
    (1, 'D', 1, 3), (-1, 'D', 1, 3),
)
SINGLE = [{'x': 1}, {'z': 1}, {'u': 1, 'ACx': 1}, {'v': 1, 'BCx': 1}]
FULL = [{'x': 1}, {'z': 1},
        {'u': 1, 'ACx': 1, 'ADz': 1}, {'v': 1, 'BCx': 1, 'BDz': 1}]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def evaluate(word, queries=QUERIES):
    # A monomial is its literal noncommutative factor string plus input letter.
    state = [{letter: 1} for letter in 'xzuv']
    for identifier in word:
        sign, factor, source, target = queries[identifier]
        require(source != target and sign in (-1, 1), 'invalid shear')
        for monomial, coefficient in state[source].items():
            key = factor + monomial
            state[target][key] = state[target].get(key, 0) + sign * coefficient
            if state[target][key] == 0:
                del state[target][key]
    return state


def split(word):
    order, gaps = [], [[]]
    for identifier in word:
        if identifier < 4:
            order.append(identifier)
            gaps.append([])
        else:
            gaps[-1].append(identifier)
    return tuple(order), tuple(tuple(gap) for gap in gaps)


def shuffles(left, right):
    if not left:
        yield right
    elif not right:
        yield left
    else:
        for tail in shuffles(left[1:], right):
            yield left[:1] + tail
        for tail in shuffles(left, right[1:]):
            yield right[:1] + tail


def lifts(order, first, second, gap=0):
    for mixed in shuffles(first[gap], second[gap]):
        if gap == 4:
            yield mixed
        else:
            for rest in lifts(order, first, second, gap + 1):
                yield mixed + (order[gap],) + rest


def replay():
    require(evaluate((6, 0)) == [{'x': 1}, {'z': 1},
            {'u': 1, 'Av': 1, 'ACx': 1}, {'v': 1, 'Cx': 1}],
            'noncommutative interpreter hand check')
    correct, all_patterns = defaultdict(list), defaultdict(Counter)
    for word in permutations(range(8)):
        order, gaps = split(word)
        all_patterns[order][tuple(map(len, gaps))] += 1
        if evaluate(word) == SINGLE:
            correct[order].append(gaps)
    require(sum(map(len, correct.values())) == 224, 'one-source count')
    require(sum(sum(p.values()) for p in all_patterns.values()) == factorial(8),
            'projection-domain coverage')
    covered = 0
    for patterns in all_patterns.values():
        for first, n_first in patterns.items():
            for second, n_second in patterns.items():
                count = n_first * n_second
                for a, b in zip(first, second):
                    count *= comb(a + b, a)
                covered += count
    require(covered == factorial(12), 'full candidate-domain coverage')
    seen = set()
    for order, patterns in correct.items():
        for first in patterns:
            for other in patterns:
                second = tuple(tuple(i + 4 for i in gap) for gap in other)
                for word in lifts(order, first, second):
                    require(evaluate(word) == FULL, 'incorrect full lift')
                    encoded = bytes(word)
                    require(encoded not in seen, 'duplicate lift')
                    seen.add(encoded)
    require(len(seen) == 76032, 'two-source count')
    sample = min(seen)
    require(evaluate(sample[:-1]) != FULL, 'omission control')
    wrong_sign = list(QUERIES)
    sign, factor, source, target = wrong_sign[sample[0]]
    wrong_sign[sample[0]] = (-sign, factor, source, target)
    require(evaluate(sample, wrong_sign) != FULL, 'sign control')
    wrong_source = tuple((s, f, 0 if f == 'D' else src, dst)
                         for s, f, src, dst in QUERIES)
    require(evaluate(sample, wrong_source) != FULL, 'source control')
    digest = hashlib.sha256(b''.join(sorted(seen))).hexdigest()
    require(digest == 'cda0204d55b197ed631cc0a8846fe3e0bbdac216cd68e7a940294df6d349e3e9',
            'full-word digest changed')
    return {'candidate_domain':covered,'projections':factorial(8),
            'direct_full_word_checks':len(seen),'negative_controls':3,'sha256':digest}


if __name__ == '__main__':
    result=replay()
    print('PASS_RECTANGULAR_FULL_CENSUS candidates=479001600 projections=40320 '
          f"full_words=76032 controls=3 sha256={result['sha256']}")
