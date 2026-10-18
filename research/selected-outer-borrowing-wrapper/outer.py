"""Fresh-output ordinary borrowing wrapper over authenticated binary tapes.

Runtime extents and atom counts stay encoded. The completed F callback is the
only new indirect semantic boundary. It must satisfy the README contract.
"""

from contextlib import ExitStack, contextmanager
from dataclasses import dataclass

import padding
from bitstream import atom_swap
from cardinal_counts import Count, positive
from cardinality import multiply_atom_power, radix_power
from linear_sign import sign_address
from stream import Counter, add_pass
from words import need


def replace(current, following, borrowed):
    need(
        following is not current and following is not borrowed,
        "distinct owned pass output",
    )
    if current is not borrowed:
        current.clear()
    return following


def body_pass(
    source, atoms, ring, q, before, gap, suffix, *, negative=False, sign=False
):
    """One vector ADD or target negation, in at most n complete atom passes."""
    need(not atoms.zero(), "positive whole-atom body")
    for extent in (before, gap, suffix):
        positive(extent)
    current = source
    coefficient = ring.negate if negative else ring.arena.copy
    with ExitStack() as work:
        remaining = Counter(atoms)
        work.callback(remaining.close)
        remaining.decrement()
        pre = Count.product(before, gap) if sign else Count(before)
        tail = Count(suffix)
        work.callback(pre.close)
        work.callback(tail.close)
        multiply_atom_power(tail, remaining.tape, ring, q)
        middle = Count(gap)
        work.callback(middle.close)
        multiply_atom_power(middle, remaining.tape, ring, q)
        if sign:
            multiply_atom_power(pre, atoms, ring, q)
        try:
            for_more = True
            while for_more:
                extents = [value.marginal() for value in (pre, middle, tail)]
                try:
                    if sign:
                        following = sign_address(
                            current, ring, q, extents[0], extents[2]
                        )
                    else:
                        following, _meter = add_pass(
                            current, ring, *extents, lambda: coefficient(ring.one)
                        )
                    current = replace(current, following, source)
                finally:
                    for extent in extents:
                        extent.close()
                for_more = not remaining.finished
                if for_more:
                    remaining.decrement()
                    for _ in radix_power(ring, q):
                        pre.multiply_small(q)
                        need(tail.divide_small(q) == 0, "exact next atom suffix")
            result, current = current, None
            return result
        finally:
            if current is not None and current is not source:
                current.clear()


def swap_chunks(source, ring, q, before, middle, suffix):
    extents = [value.marginal() for value in (before, middle, suffix)]
    try:
        return atom_swap(source, ring, q, *extents)
    finally:
        for extent in extents:
            extent.close()


def body_ordinary(source, atoms, ring, q, prefixes, rows, stock, gap, suffix, callee):
    """D-=H; padded F; D+=H; padded F; D=-D; D+=H, with fresh rows per F."""
    before = Count.product(prefixes, rows)
    body = Count.product(gap, suffix)
    multiply_atom_power(body, atoms, ring, q)
    multiply_atom_power(body, atoms, ring, q)
    current = source
    try:
        current = body_pass(current, atoms, ring, q, before, gap, suffix, negative=True)
        for second in (False, True):
            following = padding.complete(current, prefixes, rows, stock, body, callee)
            current = replace(current, following, source)
            if not second:
                following = body_pass(current, atoms, ring, q, before, gap, suffix)
                current = replace(current, following, source)
        following = body_pass(current, atoms, ring, q, before, gap, suffix, sign=True)
        current = replace(current, following, source)
        following = body_pass(current, atoms, ring, q, before, gap, suffix)
        current = replace(current, following, source)
        result, current = current, None
        return result
    finally:
        if current is not None and current is not source:
            current.clear()
        before.close()
        body.close()


@dataclass(frozen=True)
class Shape:
    rows: Count
    body_width: Count
    gap: Count
    actual_gap: Count
    actual_suffix: Count
    high_gap: Count
    high_suffix: Count


@contextmanager
def borrowing_shape(
    atoms, ring, high_ring, q, prefixes, spectators, suffix, stock, remainder_ring
):
    need(type(q) is int and q >= 2, "fixed radix at least two")
    for extent in (prefixes, spectators, suffix, stock):
        positive(extent)
    need(not atoms.zero(), "positive whole-atom body")
    need(ring.raw.compare(ring.modulus, ring.one) > 0, "nonempty atom field")
    need(
        high_ring.raw.compare(high_ring.modulus, high_ring.one) > 0,
        "nonempty high field",
    )
    if remainder_ring is not None:
        need(
            remainder_ring.raw.compare(remainder_ring.modulus, remainder_ring.one) > 0,
            "use absent remainder for zero residual digits",
        )
    with ExitStack() as work:
        rows = Count(high_ring.modulus)
        remainder = (
            Count.literal(1)
            if remainder_ring is None
            else Count(remainder_ring.modulus)
        )
        body_width = Count.literal(1)
        for value in (rows, remainder, body_width):
            work.callback(value.close)
        multiply_atom_power(body_width, atoms, ring, q)
        chunk = Count.product(body_width, remainder)
        gap = Count.product(spectators, rows)
        actual_gap = Count.product(remainder, gap)
        actual_suffix = Count.product(remainder, suffix)
        high_gap = Count.product(chunk, spectators)
        high_suffix = Count.product(chunk, suffix)
        for value in (chunk, gap, actual_gap, actual_suffix, high_gap, high_suffix):
            work.callback(value.close)
        yield Shape(
            rows, body_width, gap, actual_gap, actual_suffix, high_gap, high_suffix
        )


def swap_remainder(source, ring, q, prefixes, shape, suffix):
    pre = Count.product(prefixes, shape.rows)
    rem_pre = Count.product(pre, shape.body_width)
    rem_gap = Count.product(shape.gap, shape.body_width)
    try:
        return swap_chunks(source, ring, q, rem_pre, rem_gap, suffix)
    finally:
        pre.close()
        rem_pre.close()
        rem_gap.close()


def interchange(
    source,
    atoms,
    ring,
    high_ring,
    q,
    prefixes,
    spectators,
    suffix,
    stock,
    callee,
    remainder_ring=None,
):
    """[P][Hhi][Hbody][Hrem][Z][Dhi][Dbody][Drem][T] -> full chunk swap.

    high_ring.modulus is R=q^k, ring.modulus is M=q^w; n=atoms>0.
    remainder_ring is absent for zero remaining digits, otherwise q^ell.
    All input heads enter at one. The callee preserves its input and heads.
    """
    current = source
    with borrowing_shape(
        atoms, ring, high_ring, q, prefixes, spectators, suffix, stock, remainder_ring
    ) as shape:
        try:
            if remainder_ring is not None:
                current = swap_remainder(
                    current, remainder_ring, q, prefixes, shape, suffix
                )
            following = body_ordinary(
                current,
                atoms,
                ring,
                q,
                prefixes,
                shape.rows,
                stock,
                shape.actual_gap,
                shape.actual_suffix,
                callee,
            )
            current = replace(current, following, source)
            following = swap_chunks(
                current, high_ring, q, prefixes, shape.high_gap, shape.high_suffix
            )
            current = replace(current, following, source)
            result, current = current, None
            return result
        finally:
            if current is not None and current is not source:
                current.clear()
