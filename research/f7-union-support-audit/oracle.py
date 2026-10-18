"""Unpruned slot-partition oracle, independent of prefix-search pruning.

Nick Petalas. Apache-2.0.
"""
from collections import Counter
from itertools import combinations

MAX_ORACLE_STATES = 2_000_000


def restored_words(n, length):
    """Partition slots into n positive even blocks, ordered by their minima."""
    if not (2 <= n <= 5 and 2 * n <= length <= 12 and length % 2 == 0):
        raise ValueError("oracle domain is 2<=n<=5, even 2n<=L<=12")
    work = [((-1,) * length, tuple(range(length)), 0)]
    for _ in range(MAX_ORACLE_STATES):
        if not work:
            return
        word, free, label = work.pop()
        if label == n:
            if not free:
                yield word
            continue
        # The smallest free slot must start the next block in canonical order.
        maximum = len(free) - 2 * (n - label - 1)
        for size in range(2, maximum + 1, 2):
            for rest in combinations(free[1:], size - 1):
                slots = (free[0], *rest)
                new_word = tuple(label if i in slots else x for i, x in enumerate(word))
                new_free = tuple(i for i in free if i not in slots)
                work.append((new_word, new_free, label + 1))
        if len(work) > MAX_ORACLE_STATES:
            raise RuntimeError("oracle work capacity exceeded")
    raise RuntimeError("oracle iteration limit exceeded")


def describe(word, n):
    if not (2 <= n <= 7 and 2 * n <= len(word) <= 24):
        raise ValueError("invalid word size")
    if any(type(j) is not int or not 0 <= j < n for j in word):
        raise ValueError("invalid label")
    counts = Counter(word)
    if set(counts) != set(range(n)) or any(c % 2 for c in counts.values()):
        raise ValueError("word must use every label a positive even number of times")
    path, position = [], 0
    for label in word:
        path.append(position)
        position ^= 1 << label
    if position != 0:
        raise RuntimeError("restoration invariant failed")
    points = set(path)
    groups = [{x for x in points if x.bit_count() % 2 == side} for side in range(2)]
    bit0 = [{x for x in points if x % 2 == side} for side in range(2)]
    wrong_excess = sum(len(g) * (len(g) - 1) // 2 - len({a ^ b for a, b in combinations(g, 2)})
                       for g in bit0)
    split = tuple(map(len, groups))
    budget = sum(s * (s - 1) // 2 for s in split) - ((1 << (n - 1)) - 1)
    return {"path": path, "split": split, "bit0_split": tuple(map(len, bit0)),
            "coverage": len({a ^ b for a in points for b in points}),
            "wrong_excess": wrong_excess, "weight_budget": budget,
            "simple": len(points) == len(word)}


def census(n, length):
    all_words, hits = {}, {}
    wrong_simple = 0
    for word in restored_words(n, length):
        info = describe(word, n)
        split = info["split"]
        all_words[split] = all_words.get(split, 0) + 1
        if info["coverage"] == 1 << n:
            encoded = "".join(map(str, word))
            hits.setdefault(split, set()).add(encoded)
            wrong_simple += info["simple"] and info["wrong_excess"] > info["weight_budget"]
    return all_words, hits, wrong_simple


def admissible_splits(length):
    """Basic pair counting followed by the collision-product identity, n=7."""
    possible = []
    for s in range(1, length // 2 + 1):
        for t in range(1, s + 1):
            budget = s * (s - 1) // 2 + t * (t - 1) // 2 - 63
            if budget < 0 or s * t < 64:
                continue
            need = (s * t - 64 + 1) // 2
            if any(budget + a * b >= need for a in range(budget + 1)
                   for b in range(budget + 1 - a)):
                possible.append((s, t))
    return possible
