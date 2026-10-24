"""Exact inclusion predicates for immutable integer row tuples.

Apache-2.0. Prepared for @CubeJerry with substantial OpenAI Codex assistance.
See README.md for the annihilator identity and the precise reference semantics.
"""
from functools import lru_cache
from math import gcd, lcm


def _width(rows):
    if type(rows) is not tuple or any(type(row) is not tuple for row in rows):
        raise TypeError('Expected immutable tuples of integer rows')
    width = len(rows[0]) if rows else None
    if any(len(row) != width for row in rows):
        raise ValueError('Inconsistent row widths')
    if any(type(value) is not int for row in rows for value in row):
        raise TypeError('Expected built-in integers')
    return width


def _prepare(rows):
    """Return sparse annihilators, or None for a noncanonical target basis.

    The caller validates immutable, rectangular integer input before cache lookup.
    Canonical means primitive rows, positive increasing pivots, and zero entries
    in every other row's pivot column: exactly the reference basis convention.
    """
    if not rows:
        return ()
    pivots = []
    for row in rows:
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is None or row[pivot] < 0 or gcd(*row) != 1:
            return None
        pivots.append(pivot)
    if pivots != sorted(set(pivots)):
        return None
    if any(row[p] for i, row in enumerate(rows)
           for j, p in enumerate(pivots) if i != j):
        return None
    scale = lcm(*(row[p] for row, p in zip(rows, pivots)))
    checks = []
    for free in sorted(set(range(len(rows[0]))) - set(pivots)):
        entries = [(free, scale)]
        entries.extend((p, -row[free] * (scale // row[p]))
                       for row, p in zip(rows, pivots) if row[free])
        divisor = gcd(*(value for _, value in entries))
        checks.append(tuple((i, value // divisor) for i, value in entries))
    return tuple(checks)


class Containment:
    """Bounded cache of target equations; no whole-audit verdict is cached."""

    def __init__(self, capacity=8192):
        if type(capacity) is not int or capacity < 0:
            raise ValueError('Cache capacity must be a nonnegative integer')
        self._prepared = lru_cache(maxsize=capacity)(_prepare)

    def __call__(self, source, target):
        source_width, target_width = _width(source), _width(target)
        if (source_width is not None and target_width is not None
                and source_width != target_width):
            raise ValueError('Source/target widths differ')
        equations = self._prepared(target)
        if equations is None:
            # join(source, target) is canonical, so cannot equal this target.
            return False
        if not target:
            return all(not any(row) for row in source)
        return all(sum(row[i] * value for i, value in equation) == 0
                   for row in source for equation in equations)

    def cache_info(self):
        return self._prepared.cache_info()

    def cache_clear(self):
        self._prepared.cache_clear()
