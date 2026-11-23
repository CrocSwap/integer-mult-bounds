"""Execute ternary product-module address operations on complete payload tapes."""

from math import prod

from streaming_routes import copy_bytes, erase, negate_field, shift_field, work_tapes
from ternary_leaf import lower_coefficient, lower_slot, ordered_chart, pivot_pairs, select_pivot


def ceil_root(value, degree):
    if value < 1 or degree < 1:
        raise ValueError("The root needs a positive input and degree")
    lower, upper = 0, 1 << ((value.bit_length() + degree - 1) // degree)
    while upper - lower > 1:
        middle = (upper + lower) // 2
        if middle**degree < value:
            lower = middle
        else:
            upper = middle
    return upper


def balanced_widths(width, predecessor_floor=1):
    """Return the number of long and short contiguous components and their widths."""
    if not 1 <= predecessor_floor <= width:
        raise ValueError("The predecessor floor must fit the atom")
    count = min(ceil_root(width**3, 100), width // predecessor_floor)
    short, long_count = divmod(width, count)
    return long_count, short + 1, count - long_count, short


def stage_layout(digits, predecessor_threshold=None):
    """The caller uses the cold stage at the first level and the stated floor later."""
    minimum = 1 if predecessor_threshold is None else predecessor_threshold + 1
    width = max(ceil_root(digits, 250), minimum)
    return balanced_widths(width, minimum)


def component_widths(layout):
    long_count, long_size, short_count, short_size = layout
    for count, size in ((long_count, long_size), (short_count, short_size)):
        for _ in range(count):
            yield size


def total_width(layout):
    a, b, c, d = layout
    return a * b + c * d


def chart_width(layout):
    long_count, long_size, _, short_size = layout
    return long_size if long_count else short_size


def lower_tape(source, target, layout, prefix, gap, suffix_bytes, coefficient=None, *, runs=None):
    """Apply (x,y) -> (x,y+a*x) on the whole module. Expose a once per outer prefix."""
    width = total_width(layout)
    volume = prefix * gap * suffix_bytes * 3 ** (2 * width)
    with work_tapes(3) as (current, other, scratch):
        copy_bytes(source, current, volume)
        before = 0
        for size in component_widths(layout):
            side = 3**size
            after = width - before - size
            prefixes = 3**before
            middle = gap * 3 ** (width - size)
            piece = suffix_bytes * 3**after
            current.seek(0)
            factors = ((1, coefficient(p)) for p in range(prefix)) if runs is None else runs()
            for length, value in factors:
                shift_field(
                    current, other, scratch, length * prefixes, side, middle, piece, value % side, 0
                )
            erase(current)
            current, other = other, current
            before += size
        current.seek(0)
        copy_bytes(current, target, volume)


def negate_tape(source, target, layout, prefix, suffix_bytes):
    """Negate the complete target one contiguous component at a time."""
    width = total_width(layout)
    volume = prefix * 3**width * suffix_bytes
    with work_tapes(3) as (current, other, scratch):
        copy_bytes(source, current, volume)
        before = 0
        for size in component_widths(layout):
            current.seek(0)
            piece = suffix_bytes * 3 ** (width - before - size)
            negate_field(current, other, scratch, prefix * 3**before, 3**size, piece)
            erase(current)
            current, other = other, current
            before += size
        current.seek(0)
        copy_bytes(current, target, volume)


def pair_shape(dimensions, left, right, suffix_bytes):
    return (
        prod(dimensions[:left]),
        prod(dimensions[left + 1 : right]),
        suffix_bytes * prod(dimensions[right + 1 :]),
    )


def weighted_pair(
    source, target, layout, prefix, gap, suffix_bytes, weight, previous_swap, *, runs=None
):
    """Interchange two complete atoms with reciprocal unit weights. Keep the gap fixed."""
    width = total_width(layout)
    modulus = 3 ** chart_width(layout)
    volume = prefix * gap * suffix_bytes * 3 ** (2 * width)
    with work_tapes(2) as (current, other):
        copy_bytes(source, current, volume)

        def step(operation, *args):
            nonlocal current, other
            current.seek(0)
            operation(current, other, *args)
            erase(current)
            current, other = other, current

        def swap():
            step(previous_swap, width, prefix, gap, suffix_bytes)

        def lower(function):
            if runs is None:
                step(lower_tape, layout, prefix, gap, suffix_bytes, lambda p: function(weight(p)))
            else:

                def grouped(s, t):
                    def values():
                        for length, value in runs():
                            yield length, function(value)

                    lower_tape(s, t, layout, prefix, gap, suffix_bytes, runs=values)

                step(grouped)

        lower(lambda a: pow(a, -1, modulus))
        swap()
        lower(lambda a: -a)
        swap()
        lower(lambda a: pow(a, -1, modulus))
        step(negate_tape, layout, prefix, gap * 3**width * suffix_bytes)
        current.seek(0)
        copy_bytes(current, target, volume)


def rank_one_packet(
    source,
    target,
    layout,
    u,
    v,
    columns,
    weight,
    suffix_bytes,
    previous_swap,
    *,
    prefix=1,
    gap=1,
    stopped_limit,
):
    """Run a placed rank-one leaf when its paid packets fit the stated stopped base."""
    if not 1 <= columns < stopped_limit:
        raise ValueError("Use the compiled weighted receiver for a non-stopped paid packet")
    n = len(u)
    modulus = 3 ** chart_width(layout)
    order, b, c = ordered_chart(u, v, select_pivot(u, v), modulus)
    pivot = order[0]
    pairs = pivot_pairs(n, pivot)
    side = 3 ** total_width(layout)
    dims = [prefix] + [side] * (n * columns) + [gap] + [side] * (n * columns)
    volume = prod(dims) * suffix_bytes

    def physical(block, column):
        if block < n:
            return 1 + block * columns + column
        return 2 + block * columns + columns - 1 - column

    with work_tapes(2) as (current, other):
        copy_bytes(source, current, volume)

        def step(operation, *args):
            nonlocal current, other
            current.seek(0)
            operation(current, other, *args)
            erase(current)
            current, other = other, current

        def child(left, right, factor):
            for j in range(columns):
                shape = pair_shape(dims, physical(left, j), physical(right, j), suffix_bytes)
                a = factor(j)
                step(weighted_pair, layout, *shape, lambda p: a, previous_swap)

        for left, right in pairs:
            child(left, right, lambda j: 1)
        h_inverse = pow(c[0], -1, modulus)
        slots = range(4 * (n - 1))
        for undo in (False, True):
            if undo:
                child(0, 2 * n - 1, lambda j: weight(j, pivot) * c[0])
            for slot in reversed(slots) if undo else slots:
                dest, src, i = lower_slot(n, slot)
                for j in range(columns):
                    factor = lower_coefficient(
                        slot // (n - 1),
                        i,
                        b,
                        c,
                        weight(j, pivot),
                        weight(j, order[i]),
                        h_inverse,
                        modulus,
                    )
                    if undo:
                        factor = -factor
                    shape = pair_shape(dims, physical(src, j), physical(dest, j), suffix_bytes)
                    step(lower_tape, layout, *shape, lambda p: factor)
        for left, right in reversed(pairs):
            child(left, right, lambda j: 1)
        current.seek(0)
        copy_bytes(current, target, volume)


def rank_one_column(
    source, target, layout, u, v, weights, suffix_bytes, previous_swap, *, prefix=1, gap=1
):
    """Execute one rank-one column with stopped one-atom children."""
    rank_one_packet(
        source,
        target,
        layout,
        u,
        v,
        1,
        lambda j, i: weights[i],
        suffix_bytes,
        previous_swap,
        prefix=prefix,
        gap=gap,
        stopped_limit=2,
    )


def ordinary_shell(source, target, layout, atoms, prefix, gap, suffix_bytes, reversed_call):
    """Run both reversed returns and all three updates, including the last target negation."""
    side = 3 ** total_width(layout)
    dims = [prefix] + [side] * atoms + [gap] + [side] * atoms
    volume = prod(dims) * suffix_bytes
    with work_tapes(2) as (current, other):
        copy_bytes(source, current, volume)

        def step(operation, *args):
            nonlocal current, other
            current.seek(0)
            operation(current, other, *args)
            erase(current)
            current, other = other, current

        for phase in range(3):
            for j in range(atoms):
                src, dest = 1 + j, 2 + atoms + j
                if phase == 2:
                    step(
                        negate_tape,
                        layout,
                        prod(dims[:dest]),
                        suffix_bytes * prod(dims[dest + 1 :]),
                    )
                shape = pair_shape(dims, src, dest, suffix_bytes)
                step(lower_tape, layout, *shape, lambda p: -1 if phase == 0 else 1)
            if phase < 2:
                step(reversed_call)
        current.seek(0)
        copy_bytes(current, target, volume)
