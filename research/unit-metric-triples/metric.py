"""Original-anchor constructions for positive rational unit metric triples.

Produced by Nick Petalas. Apache-2.0. Definitions and coloring are credited
to Sagar Thakrar / PR3612 and JoyboyBrian / PR5213 in PROOF.md.
"""

from fractions import Fraction
from itertools import permutations, product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def valuation(value):
    require(value != 0, "zero has no finite valuation")
    a, b = abs(value.numerator), value.denominator
    return (a & -a).bit_length() - (b & -b).bit_length()


def residue(value):
    require(value.denominator % 2 == 1, "not integral at two")
    return value.numerator * pow(value.denominator, -1, 4) % 4


def weights(values):
    require(len(values) == 3, "three metric coefficients required")
    require(all(type(x) in (int, Fraction) for x in values), "exact coefficients required")
    result = tuple(Fraction(x) for x in values)
    require(all(x > 0 and valuation(x) == 0 for x in result), "positive unit metric required")
    require(all(max(x.numerator.bit_length(), x.denominator.bit_length()) <= 128
                for x in result), "metric coefficient capacity exceeded")
    return result


def universal(values):
    w = weights(values)
    return len({residue(x) for x in w}) == 1


def rows(values):
    require(1 <= len(values) <= 64, "row capacity is 1..64")
    require(all(len(row) == 3 for row in values), "three columns required")
    require(all(type(x) in (int, Fraction) for row in values for x in row),
            "exact row coefficients required")
    result = tuple(tuple(Fraction(x) for x in row) for row in values)
    require(all(any(row) for row in result), "zero row")
    require(all(max(abs(x.numerator).bit_length(), x.denominator.bit_length()) <= 1024
                for row in result for x in row), "row coefficient capacity exceeded")
    return result


def anchors(p, w):
    """Literal whole-instance canonical normalization, with inactive columns deleted."""
    active = tuple(j for j in range(3) if any(row[j] for row in p))
    minima = {j: min(valuation(row[j]) for row in p if row[j]) for j in active}
    gamma = min(2 * minima[j] for j in active)
    a, b = [], []
    for row in p:
        source = sum(1 << j for j in active if row[j] and valuation(row[j]) == minima[j])
        target = sum(1 << j for j in active
                     if row[j] and valuation(w[j] * row[j]) + minima[j] == gamma)
        a.append(source)
        b.append(target)
    return tuple(a), tuple(b), gamma


def gram(p, w):
    return tuple(tuple(sum(w[j] * left[j] * right[j] for j in range(3))
                       for right in p) for left in p)


def dot(left, right):
    return (left & right).bit_count() % 2


def accepts(p, w, order, labels):
    a, b, _ = anchors(p, w)
    if len(order) != len(labels) or len(order) != len(set(order)):
        return False
    if any(type(i) is not int or not 0 <= i < len(p) for i in order):
        return False
    for i, (left, right) in zip(order, labels):
        if type(left) is not int or type(right) is not int:
            return False
        if left <= 0 or right <= 0 or left & ~a[i] or right & ~b[i] or dot(left, right) != 1:
            return False
    m = gram(p, w)
    return all(m[i][j] or not dot(labels[s][0], labels[t][1])
               for s, i in enumerate(order) for t, j in enumerate(order) if s < t)


def witness(values, coefficients):
    w, p = weights(values), rows(coefficients)
    require(universal(w), "metric is outside the universal class")
    a, b, _ = anchors(p, w)
    require(all(x & y for x, y in zip(a, b)), "empty original canonical tie")
    least = min(valuation(x) for row in p for x in row if x)
    scaled = tuple(tuple(x / Fraction(2) ** least for x in row) for row in p)
    first, middle, last = [], [], []
    for i, row in enumerate(scaled):
        support = [j for j in range(3) if row[j] and valuation(row[j]) == 0]
        require(sum(1 << j for j in support) == b[i], "target anchor invariant")
        if len(support) % 2:
            middle.append(i)
        elif residue(row[support[0]] * row[support[1]]) == 1:
            first.append(i)
        else:
            last.append(i)
    order = tuple(first + middle + last)
    labels = tuple((a[i], b[i] & -b[i]) for i in first)
    labels += tuple((a[i], b[i]) for i in middle)
    labels += tuple((b[i] & -b[i], b[i]) for i in last)
    require(accepts(p, w, order, labels), "constructed witness violates the definition")
    return order, labels


def obstruction(values):
    w = weights(values)
    require(not universal(w), "requires two different unit residue classes")
    pairs = tuple((i, j) for i in range(3) for j in range(i + 1, 3)
                  if residue(w[i]) != residue(w[j]))
    i, j = pairs[0]
    k = 3 - i - j
    a, b, c = w[i], w[j], w[k]
    local = ((1, 1, 0), (b, -a, 2),
             (b, -a, -a * b * (a + b) / (2 * c)), (1, 0, 1))
    p = []
    for row in local:
        physical = [Fraction(0)] * 3
        physical[i], physical[j], physical[k] = (Fraction(x) for x in row)
        p.append(tuple(physical))
    p = rows(p)
    order = (0, 1, 3)
    labels = ((1 << i, 1 << i), (1 << j, 1 << j), (1 << i, 1 << i))
    require(accepts(p, w, order, labels), "attaining obstruction witness failed")
    return p, order, labels


def exact_histogram(p, w):
    """Independent finite definition oracle, restricted to at most four rows."""
    require(len(p) <= 4, "exhaustive oracle row capacity exceeded")
    a, b, _ = anchors(p, w)
    choices = tuple(tuple((x, y) for x in range(1, 8) for y in range(1, 8)
                          if not x & ~a[i] and not y & ~b[i] and dot(x, y))
                    for i in range(len(p)))
    require(all(len(entry) <= 28 for entry in choices), "label capacity exceeded")
    m = gram(p, w)
    histogram, attempts = [], 0
    for size in range(len(p) + 1):
        accepted = 0
        for order in permutations(range(len(p)), size):
            for labels in product(*(choices[i] for i in order)):
                attempts += 1
                if all(m[i][j] != 0 or dot(labels[s][0], labels[t][1]) == 0
                       for s, i in enumerate(order) for t, j in enumerate(order) if s < t):
                    accepted += 1
        histogram.append(accepted)
    return tuple(histogram), attempts
