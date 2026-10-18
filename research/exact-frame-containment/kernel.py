"""Exact containment of integer row spans, with the historical canonical-V rule.

Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
The cache stores equations for immutable matrix contents, never audit verdicts.
"""
from functools import lru_cache
from math import gcd, lcm


def _checked_width(identity, rows):
    """Validate an immutable matrix before using numeric-equality cache keys.

    The key retains rows itself, so a cached object's id cannot be recycled.
    Including id distinguishes equal-valued int/bool/float representations.
    """
    if type(rows) is not tuple or any(type(row) is not tuple for row in rows):
        raise TypeError("containment requires immutable tuple rows")
    if any(type(x) is not int for row in rows for x in row):
        raise TypeError("containment requires integer entries")
    width = len(rows[0]) if rows else None
    if any(len(row) != width for row in rows):
        raise ValueError("inconsistent row widths")
    return width


def _prepare(rows):
    """Return (width, equations) for a canonical primitive reduced row basis.

    None means a noncanonical presentation. The original predicate
    basis(sorted(set(U + V))) == V also rejects every such V.
    """
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("inconsistent row widths")
    if any(type(x) is not int for row in rows for x in row):
        raise TypeError("containment requires integer entries")
    pivots = []
    for row in rows:
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is None or (pivots and pivot <= pivots[-1]):
            return None
        if row[pivot] < 0 or gcd(*row) != 1:
            return None
        pivots.append(pivot)
    if any(row[p] for i, row in enumerate(rows)
           for j, p in enumerate(pivots) if i != j):
        return None
    scale = lcm(*(row[p] for row, p in zip(rows, pivots)))
    equations = []
    for free in range(width):
        if free not in pivots:
            terms = tuple((p, row[free] * (scale // row[p]))
                          for row, p in zip(rows, pivots) if row[free])
            equations.append((free, scale, terms))
    return width, tuple(equations)


class ExactContainment:
    """Drop-in predicate on rectangular tuple-of-tuples of built-in integers.

    V must have exactly the original canonical representation to be accepted.
    U may have dependent/zero/scaled rows. Malformed shapes/types fail explicitly.
    Cache lifetime is this instance, and its size is bounded by cache_size.
    """

    def __init__(self, cache_size=4096):
        if type(cache_size) is not int or cache_size < 0:
            raise ValueError("cache_size must be a nonnegative integer")
        self.prepare = lru_cache(maxsize=cache_size)(_prepare)
        self.checked_width = lru_cache(maxsize=cache_size)(_checked_width)

    def __call__(self, source, target):
        source_width = self.checked_width(id(source), source)
        target_width = self.checked_width(id(target), target)
        if source and target and source_width != target_width:
            raise ValueError("inconsistent row widths")
        if not target:
            return not any(x for row in source for x in row)
        # Validation precedes this content cache, including on equal-valued hits.
        prepared = self.prepare(target)
        if prepared is None:
            return False
        if not source or source is target:
            return True
        _, equations = prepared
        return all(row[free] * scale == sum(row[p] * coeff for p, coeff in terms)
                   for row in source for free, scale, terms in equations)
