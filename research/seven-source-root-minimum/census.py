"""Independent exact Python census. Mason Hale, with OpenAI Codex assistance.

Apache-2.0. No predecessor implementation is imported. The reduction from
arbitrary frame schedules to this finite domain is proved in README.md.
"""
from collections import Counter
from itertools import product
import json


def source_words(n):
    """Restricted-growth words: each introduced label occurs exactly twice."""
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


def partitions(n):
    """Set partitions into three or four nonempty blocks, as source bitmasks."""
    def insert(j, blocks):
        if j == n:
            if 3 <= len(blocks) <= 4:
                yield tuple(blocks)
            return
        for i in range(len(blocks)):
            extended = list(blocks)
            extended[i] |= 1 << j
            yield from insert(j + 1, extended)
        if len(blocks) < 4:
            yield from insert(j + 1, [*blocks, 1 << j])

    yield from insert(0, [])


def mandatory(blocks):
    """All masks meeting >=3 classes, by a product of within-class subsets."""
    choices = []
    for block in blocks:
        subsets, sub = [0], block
        while sub:
            subsets.append(sub)
            sub = (sub - 1) & block
        choices.append(subsets)
    result = 0
    for selection in product(*choices):
        if sum(bool(x) for x in selection) >= 3:
            result |= 1 << sum(selection)  # blocks are disjoint
    return result


def interval_differences(word):
    """Parity of each contiguous substring; no prefix-difference generator."""
    result = 1
    for start in range(len(word)):
        parity = 0
        for label in word[start:]:
            parity ^= 1 << label
            result |= 1 << parity
    return result


def census(n=7):
    prepared, groups = [], {}
    for blocks in partitions(n):
        key = "+".join(map(str, sorted((x.bit_count() for x in blocks), reverse=True)))
        if key not in groups:
            groups[key] = {"partitions": 0, "missing_histogram": Counter()}
        groups[key]["partitions"] += 1
        prepared.append((mandatory(blocks), groups[key]["missing_histogram"]))
    words = 0
    differences = Counter()
    for word in source_words(n):
        words += 1
        have = interval_differences(word)
        differences[have.bit_count()] += 1
        for required, histogram in prepared:
            histogram[(required & ~have).bit_count()] += 1
    return {
        "sources": n,
        "words": words,
        "partitions": len(prepared),
        "cases": words * len(prepared),
        "difference_histogram": dict(sorted(differences.items())),
        "groups": {
            key: {"partitions": entry["partitions"],
                  "missing_histogram": dict(sorted(entry["missing_histogram"].items()))}
            for key, entry in sorted(groups.items())
        },
    }


if __name__ == "__main__":
    print(json.dumps(census(), indent=2, sort_keys=True))
