"""Move a native matcher on the two actual bodies when the column count is bounded."""

from fractions import Fraction
from functools import partial
from math import prod

from factored_frames import apply_row, inverse_word
from growing_binary import pipe
from module_atoms import component_widths, lower_tape, pair_shape, total_width, weighted_pair
from five_exchange import direct_line, same_order_line
from streaming_routes import copy_bytes, erase, integer_scale, negate_field, work_tapes
from ternary_frames import residue
from ternary_leaf import select_pivot


def scale_atom(source, target, layout, prefix, suffix, factor):
    """Apply a fixed native unit to every cyclic component of the selected atom."""
    width = total_width(layout)
    numerator, denominator = factor.numerator, factor.denominator
    if max(abs(numerator), denominator) > 20:
        raise ValueError("Scaling exceeds the proved raw factor alphabet")
    volume = prefix * 3**width * suffix
    with work_tapes(22) as (current, other, *buckets):
        copy_bytes(source, current, volume)

        def step(operation, *args):
            nonlocal current, other
            current.seek(0)
            operation(current, other, *args)
            erase(current)
            current, other = other, current

        before = 0
        for size in component_widths(layout):
            side = 3**size
            extent = prefix * 3**before, side, suffix * 3 ** (width - before - size)
            if abs(numerator) > 1:
                step(integer_scale, buckets, *extent, abs(numerator), False)
            if numerator < 0:
                step(negate_field, buckets[0], *extent)
            if denominator > 1:
                step(integer_scale, buckets, *extent, denominator, True)
            before += size
        current.seek(0)
        copy_bytes(current, target, volume)


def direct_actions(word, f):
    """Convert each right matrix to its inverse action on the two body columns."""
    for gate, i, *args in word:
        for tail in (False, True):
            for column in range(f):
                src = i * f + column
                if gate == "scale":
                    yield gate, tail, src, None, 1 / Fraction(args[0])
                elif gate == "swap":
                    left, right = sorted((src, args[0] * f + column))
                    yield gate, tail, left, right, 1
                elif gate == "add":
                    yield gate, tail, src, args[0] * f + column, -args[1]
                else:
                    raise ValueError("The native body matcher has an unknown operation")


def direct_route(core, source, target, word, f, unused, older, gap, suffix, weight):
    """For a right word S, move head addresses by A S⁻¹ A⁻¹ and tails by S⁻¹."""
    n, atom, modulus = core.n, core.atom, core.modulus
    width = total_width(core.layout)
    dims = [unused, older] + [atom] * (n * f) + [gap] + [atom] * (n * f)

    def runs(left, scalar, numerator, denominator):
        visible = prod(dims[2:left])
        for _ in range(unused):
            for old in range(older):
                if numerator is None:
                    value = scalar
                else:
                    value = (
                        scalar * weight(old, numerator) * pow(weight(old, denominator), -1, modulus)
                    )
                yield visible, value % modulus

    def schedule():
        for gate, tail, a, b, factor in direct_actions(word, f):
            start = 3 + n * f if tail else 2
            x = start + a
            if gate == "scale":
                yield partial(
                    scale_atom,
                    layout=core.layout,
                    prefix=prod(dims[:x]),
                    suffix=suffix * prod(dims[x + 1 :]),
                    factor=factor,
                )
                continue
            y = start + b
            left, right = sorted((x, y))
            p, g, s = pair_shape(dims, left, right, suffix)

            def exchange(src, dst, p=p, g=g, s=s):
                core.previous(src, dst, width, p, g, s)

            if gate == "swap":
                if tail:
                    yield exchange
                else:
                    coeffs = partial(runs, left, 1, a, b)
                    yield partial(
                        weighted_pair,
                        layout=core.layout,
                        prefix=p,
                        gap=g,
                        suffix_bytes=s,
                        weight=None,
                        previous_swap=core.previous,
                        runs=coeffs,
                    )
                continue
            if x > y:
                yield exchange
            value = residue(factor, modulus)
            coeffs = partial(runs, left, value, None if tail else b, None if tail else a)
            yield partial(
                lower_tape, layout=core.layout, prefix=p, gap=g, suffix_bytes=s, runs=coeffs
            )
            if x > y:
                yield exchange

    with core.storage() as arena:
        pipe(arena, "matcher", source, target, prod(dims) * suffix, schedule())


def direct_factors(frame, modulus):
    """Return F e and eᵗ F⁻¹ at the one selected coordinate."""
    if len(frame.mask) != 1:
        raise ValueError("A terminal leaf must have rank one")
    unit = [int(i == frame.mask[0]) for i in range(frame.size)]

    def transpose_word():
        for op, i, *args in reversed(frame.word):
            if op == "add":
                yield op, args[0], i, args[1]
            else:
                yield (op, i, *args)

    return apply_row(transpose_word(), unit, modulus), apply_row(
        inverse_word(frame.word), unit, modulus
    )

