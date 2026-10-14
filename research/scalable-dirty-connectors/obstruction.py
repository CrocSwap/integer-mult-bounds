"""Exact finite facts for the two-dirty-root scalability obstruction.

Two word generators and two difference-set implementations are compared per
word, not merely against a common histogram. Apache-2.0; AI-assisted.
"""

from collections import Counter
from math import factorial


def growth_words(n):
    word, counts = [], []

    def visit():
        if len(word) == 2 * n:
            yield tuple(word)
            return
        for label in range(len(counts) + (len(counts) < n)):
            fresh = label == len(counts)
            if fresh:
                counts.append(0)
            if counts[label] < 2:
                counts[label] += 1
                word.append(label)
                yield from visit()
                word.pop()
                counts[label] -= 1
            if fresh:
                counts.pop()

    yield from visit()


def matching_words(n):
    word = [-1] * (2 * n)

    def pair(remaining, label):
        if not remaining:
            yield tuple(word)
            return
        first = remaining[0]
        for index in range(1, len(remaining)):
            second = remaining[index]
            word[first] = word[second] = label
            yield from pair(remaining[1:index] + remaining[index + 1 :], label + 1)
            word[first] = word[second] = -1

    yield from pair(tuple(range(2 * n)), 0)


def differences(word):
    points, state = [0], 0
    for label in word:
        state ^= 1 << label
        points.append(state)
    covered = {a ^ b for a in points for b in points}
    return sum(1 << mask for mask in covered)


def dual_differences(word, n):
    # Compute every prefix parity directly from its substring, then use the
    # dual membership criterion instead of pairwise-XOR construction.
    points = {
        sum((word[:boundary].count(j) % 2) << j for j in range(n))
        for boundary in range(len(word) + 1)
    }
    return sum(
        1 << mask for mask in range(1 << n)
        if any(point ^ mask in points for point in points)
    )


def census():
    result = {}
    for n, maximum in ((5, 31), (6, 49)):
        primary = {word: differences(word) for word in growth_words(n)}
        independent = {word: dual_differences(word, n) for word in matching_words(n)}
        expected_count = factorial(2 * n) // (2**n * factorial(n))
        if len(primary) != expected_count or primary != independent:
            raise ValueError("closed-word generators or difference engines disagree")
        histogram = Counter(coverage.bit_count() for coverage in primary.values())
        if max(histogram) != maximum:
            raise ValueError("closed-word maximum changed")
        result[str(n)] = {
            "words": len(primary), "max_coverage": max(histogram),
            "maximizers": histogram[maximum],
            "histogram": {str(size): count for size, count in sorted(histogram.items())},
        }
    return result


if __name__ == "__main__":
    import json
    print(json.dumps(census(), indent=2))
