"""Run an ordinary projective line with one direct child or at most five per low."""

from functools import lru_cache, partial
from math import prod

from growing_binary import pipe
from module_atoms import lower_tape, pair_shape


def corner_exchanges(u, v, pivot):
    """Choose the shortest corner-exposure itinerary from the common low."""
    last = len(u) - 1
    first_unit, last_unit = bool(u[0] % 3), bool(v[-1] % 3)
    if first_unit and last_unit:
        return ()
    if last_unit:
        for i in range(last):
            if u[i] % 3:
                return ((0, i),)
    if first_unit:
        for i in range(1, last + 1):
            if v[i] % 3:
                return ((i, last),)
    if u[last] % 3 and v[0] % 3:
        return ((0, last),)
    if pivot == 0:
        return ((0, last), (0, 0))
    if pivot == last:
        return ((0, last), (last, last))
    return ((0, pivot), (pivot, last))


def direct_line(core, source, target, frame, f, unused, older, gap, suffix, weight):
    """Move the supplied native basis to coordinates and restore it after one call."""
    from direct_body import direct_route
    from factored_frames import inverse_word

    (axis,) = frame.mask
    head = core.atom ** (axis * f)
    middle = core.atom ** ((core.n - 1) * f) * gap
    tail = core.atom ** ((core.n - axis - 1) * f) * suffix
    volume = unused * older * core.atom ** (2 * core.n * f) * gap * suffix

    def coordinate_weight(row, j):
        return weight(row // head, axis * f + j)

    def move(word):
        return partial(direct_route, core, word=word, f=f, unused=unused, older=older,
                       gap=gap, suffix=suffix, weight=weight)

    def schedule():
        if frame.word:
            yield move(frame.word)
        yield partial(core.weighted, atoms=f, available=unused, older=older * head,
                      gap=middle, suffix=tail, weight=coordinate_weight)
        if frame.word:
            yield move(inverse_word(frame.word))

    with core.storage() as arena:
        pipe(arena, "direct-coordinate", source, target, volume, schedule())


def same_order_line(core, source, target, *, pivot, factors, f, unused,
                    heights, older, gap, suffix, weight):
    """Execute and restore one full low packet, including all its high lifts."""
    n, atom, modulus = core.n, core.atom, core.modulus
    rows = heights * older
    dims = [unused, rows] + [atom] * (n * f) + [gap] + [atom] * (n * f)
    last = 2 * n - 1

    @lru_cache(maxsize=1)
    def line(high):
        return factors(high)

    pairs = corner_exchanges(*line(0), pivot)
    origins = {}
    for left, right in pairs:
        right += n
        origins[left], origins[right] = origins.get(right, right), origins.get(left, left)

    def value(position, dual, j, old, high):
        """Read D times the permuted primal, or D inverse times the permuted dual."""
        origin = origins.get(position, position)
        primal, covector = line(high)
        vector = covector if dual else primal
        entry = vector[origin] if origin < n else -vector[origin - n]
        if position < n:
            factor = weight(old, position * f + j)
            entry *= pow(factor, -1, modulus) if dual else factor
        return entry % modulus

    def coefficient(src, dest, j, old, high):
        if src == 0:
            first_inverse = pow(value(0, False, j, old, high), -1, modulus)
            if dest == last:
                end_inverse = pow(value(last, True, j, old, high), -1, modulus)
                return (end_inverse - value(last, False, j, old, high)) * first_inverse % modulus
            return -value(dest, False, j, old, high) * first_inverse % modulus
        end_inverse = pow(value(last, True, j, old, high), -1, modulus)
        return value(src, True, j, old, high) * end_inverse % modulus

    def child(left, right, central):
        start = left * f
        end = (n + right) * f
        front = atom**start

        def child_weight(row, j):
            high, old = divmod(row // front, older)
            if central:
                return -value(0, False, j, old, high) * value(last, True, j, old, high) % modulus
            return weight(old, left * f + j)

        return partial(
            core.weighted, atoms=f, available=unused, older=rows * front,
            gap=gap * atom ** (end - start - f), suffix=suffix * atom ** (2 * n * f - end - f),
            weight=child_weight,
        )

    def shear(src, dest, j, undo):
        x = (2 if src < n else 3) + src * f + j
        y = (2 if dest < n else 3) + dest * f + j
        visible = prod(dims[2:x])

        def coefficients():
            for _ in range(unused):
                for high in range(heights):
                    for old in range(older):
                        scalar = coefficient(src, dest, j, old, high)
                        yield visible, -scalar if undo else scalar

        prefix, middle, tail = pair_shape(dims, x, y, suffix)
        return partial(lower_tape, layout=core.layout, prefix=prefix, gap=middle,
                       suffix_bytes=tail, runs=coefficients)

    def sweeps(undo):
        middle = range(last - 1, 0, -1) if undo else range(1, last)
        columns = range(f - 1, -1, -1) if undo else range(f)
        if undo:
            for j in columns:
                yield shear(0, last, j, True)
        for tail in ((True, False) if undo else (False, True)):
            for i in middle:
                src, dest = (i, last) if tail else (0, i)
                for j in columns:
                    yield shear(src, dest, j, undo)
        if not undo:
            for j in columns:
                yield shear(0, last, j, False)

    def schedule():
        for left, right in pairs:
            yield child(left, right, False)
        yield from sweeps(False)
        yield child(0, n - 1, True)
        yield from sweeps(True)
        for left, right in reversed(pairs):
            yield child(left, right, False)

    with core.storage() as arena:
        pipe(arena, "exposed-leaf", source, target, prod(dims) * suffix, schedule())
