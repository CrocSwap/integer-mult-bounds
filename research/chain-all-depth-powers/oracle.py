"""Independent literal oracles. No import of the repetition formula.
SHIN09-git with OpenAI Codex assistance. Apache-2.0.
"""
from bisect import bisect_left
from itertools import accumulate


def balanced_words(depth, copies):
    """Enumerate the multiset permutations in lexicographic order."""
    word = [letter for letter in range(1, depth + 1) for _ in range(copies)]
    while True:
        yield tuple(word)
        pivot = len(word) - 2
        while pivot >= 0 and word[pivot] >= word[pivot + 1]:
            pivot -= 1
        if pivot < 0:
            return
        successor = len(word) - 1
        while word[successor] <= word[pivot]:
            successor -= 1
        word[pivot], word[successor] = word[successor], word[pivot]
        word[pivot + 1:] = reversed(word[pivot + 1:])


def positional_counts(word, depth):
    """Integer subsequence counts from the position sets of successive labels."""
    positions = [[] for _ in range(depth + 1)]
    for index, label in enumerate(word):
        positions[label].append(index)
    intervals = {}
    for start in range(1, depth + 1):
        weights = [1] * len(positions[start])
        intervals[start, start] = len(weights)
        for end in range(start + 1, depth + 1):
            prefix = [0, *accumulate(weights)]
            weights = [prefix[bisect_left(positions[end - 1], pos)]
                       for pos in positions[end]]
            intervals[start, end] = sum(weights)
    return intervals


def literal_matrix(word, depth):
    """Execute every call on the integer basis of all dirty scalar roles."""
    rows = [[int(i == j) for j in range(depth + 1)] for i in range(depth + 1)]
    for label in word:
        source, target = rows[label - 1], rows[label]
        for j in range(label):
            target[j] += source[j]
    return rows


def matrix_target(rows, modulus):
    depth = len(rows) - 1
    for end in range(1, depth + 1):
        for column in range(end):
            if (end, column) != (depth, 0) and rows[end][column] % modulus:
                return None
    return rows[depth][0] % modulus


def position_target(counts, depth, modulus):
    if any(value % modulus for key, value in counts.items() if key != (1, depth)):
        return None
    return counts[1, depth] % modulus


def primitive_period(word):
    return next(k for k in range(1, len(word) + 1) if word[k:] + word[:k] == word)


def canonical_rotation(word):
    return min(word[k:] + word[:k] for k in range(len(word)))


def phi(n):
    from math import gcd
    return sum(gcd(k, n) == 1 for k in range(1, n + 1))


def map_vector(label, vector, modulus, singular):
    first, second = vector
    if singular and label == 1:
        return (first % modulus, 0)
    if label % 2:
        return ((first + second) % modulus, second)
    return (first, (first + second) % modulus)


def dirty_basis(word, depth, modulus, target):
    """Two families of noncommuting 2x2 maps, every dirty input basis vector."""
    cases = 0
    for singular in (False, True):
        for column in range(2 * (depth + 1)):
            initial = [(int(column == 2*j), int(column == 2*j + 1))
                       for j in range(depth + 1)]
            actual = list(initial)
            for label in word:
                add = map_vector(label, actual[label - 1], modulus, singular)
                actual[label] = tuple((x + y) % modulus for x, y in zip(actual[label], add))
            expected, product = list(initial), initial[0]
            for label in range(1, depth + 1):
                product = map_vector(label, product, modulus, singular)
            expected[depth] = tuple((x + target*y) % modulus for x, y in zip(initial[depth], product))
            if actual != expected:
                raise ValueError("noncommuting dirty endpoint")
            cases += 1
    return cases
