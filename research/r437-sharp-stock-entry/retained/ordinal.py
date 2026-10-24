"""PR4734 exact ordinal adapter, codyw912/OpenAI Codex, Apache-2.0.

install_ordinal_counts is extracted byte-for-byte from source head
4c1a746590ec97fa84537da43dc662775a5b72e7; helpers below retain its semantics.
"""
from types import MethodType


def need(ok, message):
    if not ok:
        raise ValueError(message)


def reject(label, operation, controls):
    try:
        operation()
    except ValueError:
        controls.append(label)
    else:
        raise ValueError("accepted negative control: " + label)


def install_ordinal_counts(codes):
    """Sum the literal codec's skipped candidates; preserve its GL ordering."""
    import low_codes

    def prefix(constraints, reduced, stop, total):
        if constraints.inconsistent:
            excluded = 0
        elif reduced[2] is not None:
            excluded = stop * constraints.q ** (len(constraints.rows) - len(constraints.basis) - 1)
        else:
            excluded = int(reduced[1] < stop) * constraints.q ** (len(constraints.rows) - len(constraints.basis))
        return stop * total - excluded

    def rank(self, rows, vector):
        constraints, ordinal = low_codes.Constraints(rows, self.q), 0
        for column, value in enumerate(vector):
            reduced = constraints.next(column)
            ordinal += prefix(constraints, reduced, value, self.q ** (self.dimension - column - 1))
            constraints.choose(reduced, value)
        need(constraints.inconsistent, "independent low row")
        return ordinal

    def unrank(self, rows, ordinal):
        constraints, vector = low_codes.Constraints(rows, self.q), []
        for column in range(self.dimension):
            reduced = constraints.next(column)
            total = self.q ** (self.dimension - column - 1)
            need(0 <= ordinal < prefix(constraints, reduced, self.q, total), "low-row rank range")
            lo, hi = 0, self.q
            while lo < hi:
                mid = (lo + hi) // 2
                if prefix(constraints, reduced, mid + 1, total) <= ordinal:
                    lo = mid + 1
                else:
                    hi = mid
            need(lo < self.q, "low-row rank range")
            ordinal -= prefix(constraints, reduced, lo, total)
            constraints.choose(reduced, lo)
            vector.append(lo)
        need(ordinal == 0 and constraints.inconsistent, "complete independent low row")
        return tuple(vector)

    finite = low_codes.LowCodes(3, 2)
    import itertools
    vectors = list(itertools.product(range(3), repeat=2))
    checks = []
    prefixes = [[]] + [[v] for v in vectors if v != (0, 0)]
    for rows in prefixes:
        for vector in vectors:
            try:
                original = finite.vector_rank(rows, vector)
            except ValueError:
                reject("dependent_row", lambda r=rows, v=vector: rank(finite, r, v), checks)
            else:
                need(rank(finite, rows, vector) == original, "ordinal prefix sum matches exhaustive codec")
                need(unrank(finite, rows, original) == finite.vector_unrank(rows, original) == vector, "ordinal inverse matches exhaustive codec")
        total = 3**2 - 3**len(rows)
        for ordinal in range(total):
            need(unrank(finite, rows, ordinal) == finite.vector_unrank(rows, ordinal), "all finite inverse intervals including plateaus")
        for ordinal in (-1, total):
            reject("invalid_ordinal", lambda r=rows, o=ordinal: unrank(finite, r, o), checks)
    codes.vector_rank = MethodType(rank, codes)
    codes.vector_unrank = MethodType(unrank, codes)
    # Repeated source resolution has the same complete GL ordinal. Cache only
    # exact pure codec results, never source authentication or admission.
    from functools import lru_cache
    codes.rank = lru_cache(maxsize=32)(codes.rank)
    codes.unrank = lru_cache(maxsize=32)(codes.unrank)
