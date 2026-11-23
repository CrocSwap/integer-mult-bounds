"""Execute weighted equal-order atom exchanges on arbitrary complete tape records."""

from functools import lru_cache, partial
from math import prod

from growing_binary import one_weight, pipe
from module_atoms import lower_tape, pair_shape, weighted_pair
from ternary_leaf import lower_coefficient


def switch(position, left, right):
    if position == left:
        return right
    if position == right:
        return left
    return position


def pivot_exchanges(n, pivot):
    """Return opposite-bank pairs. Move the pivot to the first head and last tail."""
    last = n - 1
    if n == 1:
        return ()
    if pivot == 0:
        return ((0, 0), (0, last), (0, 0))
    if pivot == last:
        return ((0, last), (last, last), (0, last))
    return ((0, pivot), (pivot, last), (0, last), (pivot, pivot))


def leaf_slots(n, pivot, undo):
    """Return the ordered source, destination, sweep and original coordinate."""
    last = n - 1
    sweeps = range(3, -1, -1) if undo else range(4)
    order = range(n - 1, -1, -1) if undo else range(n)
    for sweep in sweeps:
        for i in order:
            if i != pivot:
                head = switch(i, 0, pivot)
                tail = n + switch(i, pivot, last)
                source, target = ((0, head), (tail, 2 * n - 1), (0, tail), (head, 2 * n - 1))[sweep]
                yield source, target, sweep, i


def chart_factors(u, v, pivot, modulus):
    unit = u[pivot]
    reciprocal = pow(unit, -1, modulus)
    b = tuple(x * reciprocal % modulus for x in u)
    c = tuple(x * unit % modulus for x in v)
    return b, c, pow(c[pivot], -1, modulus)


def same_order_line(
    core, source, target, *, pivot, factors, f, unused, heights, older, gap, suffix, weight
):
    """The fixed low chart supplies one pivot. Each high ordinal supplies its two vectors."""
    n, atom, modulus = core.n, core.atom, core.modulus
    rows = heights * older
    dims = [unused, rows] + [atom] * (n * f) + [gap] + [atom] * (n * f)
    pairs = pivot_exchanges(n, pivot)

    @lru_cache(maxsize=1)
    def lifted(high):
        u, v = factors(high)
        return chart_factors(u, v, pivot, modulus)

    def physical(block, j):
        return (2 if block < n else 3) + block * f + j

    def child(left, right, central):
        start = left * f
        end = (n + right) * f
        front = atom**start
        middle = gap * atom ** (end - start - f)
        last = suffix * atom ** (2 * n * f - end - f)
        if central:

            def child_weight(row, j):
                high, old = divmod(row // front, older)
                _, c, _ = lifted(high)
                return weight(old, pivot * f + j) * c[pivot] % modulus
        else:
            child_weight = one_weight
        return partial(
            core.weighted,
            atoms=f,
            available=unused,
            older=rows * front,
            gap=middle,
            suffix=last,
            weight=child_weight,
        )

    def shear(src, dst, sweep, i, j, undo):
        x, y = physical(src, j), physical(dst, j)
        visible = prod(dims[2:x])

        def coefficients():
            for _ in range(unused):
                for high in range(heights):
                    b, c, inv = lifted(high)
                    for old in range(older):
                        a = lower_coefficient(
                            sweep,
                            i,
                            b,
                            c,
                            weight(old, pivot * f + j),
                            weight(old, i * f + j),
                            inv,
                            modulus,
                        )
                        yield visible, -a if undo else a

        p, g, s = pair_shape(dims, x, y, suffix)
        return partial(
            lower_tape, layout=core.layout, prefix=p, gap=g, suffix_bytes=s, runs=coefficients
        )

    def schedule():
        for left, right in pairs:
            yield child(left, right, False)
        for undo in (False, True):
            if undo:
                yield child(0, n - 1, True)
            for src, dst, sweep, i in leaf_slots(n, pivot, undo):
                for j in range(f):
                    yield shear(src, dst, sweep, i, j, undo)
        for left, right in reversed(pairs):
            yield child(left, right, False)

    with core.storage() as arena:
        pipe(arena, "exposed-leaf", source, target, prod(dims) * suffix, schedule())


class SameOrderBody:
    """Both banks have the same order at every recursive boundary."""

    def weighted(self, source, target, *, atoms, available, older, gap, suffix, weight=one_weight):
        f, remainder = divmod(atoms, self.n)
        unused = 0
        if f:
            unused, rem = divmod(available, self.stock)
            if rem or not unused:
                raise ValueError("The active call lacks a complete independent fresh stock")
        dims = [available * older] + [self.atom] * atoms + [gap] + [self.atom] * atoms

        def stopped(j):
            axis = self.n * f + j
            shape = pair_shape(dims, 1 + axis, 2 + atoms + axis, suffix)
            visible = self.atom**axis

            def coefficients():
                for _ in range(available):
                    for old in range(older):
                        yield visible, weight(old, axis)

            return partial(
                weighted_pair,
                layout=self.layout,
                prefix=shape[0],
                gap=shape[1],
                suffix_bytes=shape[2],
                weight=None,
                previous_swap=self.previous,
                runs=coefficients,
            )

        def schedule():
            for j in range(remainder):
                yield stopped(j)
            if f:
                extra = self.atom**remainder
                yield partial(
                    self.compiled,
                    f=f,
                    unused=unused,
                    older=older,
                    gap=gap * extra,
                    suffix=suffix * extra,
                    weight=weight,
                )

        with self.storage() as arena:
            pipe(arena, "weighted", source, target, prod(dims) * suffix, schedule())

    def body_ordinary(self, source, target, atoms, available, older, gap, suffix):
        self.weighted(
            source, target, atoms=atoms, available=available, older=older, gap=gap, suffix=suffix
        )
