"""Exact leading-principal determinant reuse for the pinned Gram checker.

This module has no dependencies outside Python. See PROOF.md for the integer
identity, cache contract, and the zero-pivot fallback.
"""

from itertools import chain


class PrefixDeterminant:
    """Callable determinant with one bounded cache of leading principal minors.

    ``reference_det`` must compute exact determinants of square integer matrices.
    A miss replaces the cache. A hit retains the previous cache, so a full-matrix
    request followed by all its leading prefixes requires one elimination pass.
    Only built-in ``int`` entries are accepted; bool and float are rejected.
    Instances are intended for sequential use, as in the pinned checker.
    """

    def __init__(self, reference_det):
        if not callable(reference_det):
            raise TypeError("reference_det must be callable")
        self.reference_det = reference_det
        self.stats = {"calls": 0, "hits": 0, "fallbacks": 0}
        self._cache = {}

    @property
    def cache_size(self):
        """Number of stored determinants, bounded by the last missed dimension."""
        return len(self._cache)

    def __call__(self, matrix):
        self.stats["calls"] += 1
        key = tuple(map(tuple, matrix))
        n = len(key)
        if set(map(len, key)) - {n}:
            raise ValueError("determinant requires a square matrix")
        if set(map(type, chain.from_iterable(key))) - {int}:
            raise TypeError("matrix entries must be built-in integers")

        cached = self._cache.get(key)
        if cached is not None:
            self.stats["hits"] += 1
            return cached

        # Evict the old root before computation. Never combine unrelated roots.
        self._cache = {}
        if not n:
            return 1

        work = [list(row) for row in key]
        minors = []
        previous = 1
        result = None
        for k in range(n - 1):
            pivot = work[k][k]
            minors.append(pivot)
            if pivot == 0:
                self.stats["fallbacks"] += 1
                # Pass a separate mutable copy to preserve both the input and
                # the immutable cache keys, even if the reference mutates it.
                result = self.reference_det([list(row) for row in key])
                break
            if previous == 0:
                raise ArithmeticError("zero Bareiss divisor")
            for i in range(k + 1, n):
                for j in range(k + 1, n):
                    numerator = work[i][j] * pivot - work[i][k] * work[k][j]
                    quotient, remainder = divmod(numerator, previous)
                    if remainder != 0:
                        raise ArithmeticError("non-exact Bareiss division")
                    work[i][j] = quotient
                work[i][k] = 0
            previous = pivot
        else:
            result = work[-1][-1]
            minors.append(result)

        # Each key contains every entry of the corresponding requested matrix.
        # Mutable caller objects and their identities never serve as cache keys.
        self._cache = {
            tuple(row[:size] for row in key[:size]): value
            for size, value in enumerate(minors, start=1)
            if size < n
        }
        self._cache[key] = result
        return result
