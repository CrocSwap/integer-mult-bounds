"""A streaming three-block composition of source-restoring additive shears.

The leaf callback must add a deterministic function of its source to its target,
restore its source, and implement its exact inverse when sign is -1. Its
increment must not depend on the target. Coefficients and read-only data must
stay fixed throughout a call. See README.md for the proof and charged scope.
"""

from functools import lru_cache


def need(condition, message):
    if not condition:
        raise ValueError(message)


def split(n):
    """Contiguous block sizes; extra factors go to the less-repeated ends."""
    need(type(n) is int and n >= 3, "ternary split requires at least three factors")
    q, remainder = divmod(n, 3)
    return q + (remainder > 0), q, q + (remainder > 1)


def resources(n):
    """Return (executed leaf calls, simultaneously borrowed arrays)."""
    need(type(n) is int and n >= 1, "positive integer factor count")

    @lru_cache(maxsize=None)
    def count(size):
        if size == 1:
            return 1, 0
        if size == 2:
            return 4, 1
        a, b, c = (count(k) for k in split(size))
        return 2 * a[0] + 4 * b[0] + 2 * c[0], 2 + max(a[1], b[1], c[1])

    return count(n)


def word(n, sign=1):
    """Yield (factor_index, source_array, target_array, sign) in execution order.

    Array 0 is the source, array 1 the target, and arrays 2 onward are borrowed.
    Only O(log n) control frames are live; the expanded word is never stored.
    Negative calls reverse the instruction order as well as the signs.
    """
    need(type(n) is int and n >= 1, "positive integer factor count")
    need(type(sign) is int and sign in (-1, 1), "sign must be +1 or -1")

    def emit(lo, hi, source, target, depth, direction):
        size = hi - lo
        if size == 1:
            yield lo, source, target, direction
            return
        u = 2 + depth
        if size == 2:
            operations = [
                (lo, lo + 1, source, u, 1),
                (lo + 1, hi, u, target, 1),
                (lo, lo + 1, source, u, -1),
                (lo + 1, hi, u, target, -1),
            ]
            child_depth = depth + 1
        else:
            a, b, _ = split(size)
            v = u + 1
            # PR673's echo at fanout 3, with longer blocks at the ends.
            # Chronological order: A B C B^-1 A^-1 B C^-1 B^-1.
            A = (lo, lo + a, source, u)
            B = (lo + a, lo + a + b, u, v)
            C = (lo + a + b, hi, v, target)
            operations = [
                (*A, 1), (*B, 1), (*C, 1), (*B, -1),
                (*A, -1), (*B, 1), (*C, -1), (*B, -1),
            ]
            child_depth = depth + 2
        if direction == -1:
            operations = [(*op[:-1], -op[-1]) for op in reversed(operations)]
        for left, right, src, dst, child_sign in operations:
            yield from emit(left, right, src, dst, child_depth, child_sign)

    yield from emit(0, n, 0, 1, 0, sign)


def compose(source, target, factors, scratch, leaf, sign=1):
    """Run the word using leaf(source, target, factor, sign).

    Scratch arrays are caller-supplied arbitrary data, not initialized copies.
    Extra supplied arrays are admitted but untouched. Array aliasing is rejected
    before the first leaf. Overlapping views and hidden mutable dependencies
    are outside this contract; the reference uses ordinary lists of scalars.
    """
    n = len(factors)
    _, required = resources(n)
    need(type(sign) is int and sign in (-1, 1), "sign must be +1 or -1")
    need(len(scratch) >= required, "insufficient distinct dirty arrays")
    arrays = [source, target, *scratch]
    need(len({id(a) for a in arrays}) == len(arrays), "source, target and scratch must be distinct")
    need(len(source) > 0 and all(len(a) == len(source) for a in arrays), "equal positive array lengths")
    for factor, src, dst, direction in word(n, sign):
        leaf(arrays[src], arrays[dst], factors[factor], direction)
