"""Run the authenticated two-call body with the four-bucket outer digit exchange."""
from contextlib import ExitStack

from cardinal_counts import Count
from compact_digits import atom_swap
from encoded import compare
from ordinary import outer, radix_power, ring_from_count, unit_program
from session import borrowed_count, borrowed_tape


def swap_chunks(source, ring, q, before, middle, suffix, factory):
    extents = [value.marginal() for value in (before, middle, suffix)]
    try:
        return atom_swap(source, ring, q, *extents, factory)
    finally:
        for extent in extents:
            extent.close()


def swap_remainder(source, ring, q, prefixes, shape, suffix, factory):
    pre = Count.product(prefixes, shape.rows)
    rem_pre = Count.product(pre, shape.body_width)
    rem_gap = Count.product(shape.gap, shape.body_width)
    try:
        return swap_chunks(source, ring, q, rem_pre, rem_gap, suffix, factory)
    finally:
        pre.close()
        rem_pre.close()
        rem_gap.close()


def interchange(source, atoms, ring, high_ring, q, prefixes, spectators, suffix,
                stock, callee, remainder_ring, factory):
    """Execute the optional remainder, the two completed roots, then the high field."""
    current = source
    with outer.borrowing_shape(atoms, ring, high_ring, q, prefixes, spectators,
                               suffix, stock, remainder_ring) as shape:
        try:
            if remainder_ring is not None:
                current = swap_remainder(current, remainder_ring, q, prefixes,
                                         shape, suffix, factory)
            following = outer.body_ordinary(current, atoms, ring, q, prefixes,
                                            shape.rows, stock, shape.actual_gap,
                                            shape.actual_suffix, callee)
            current = outer.replace(current, following, source)
            following = swap_chunks(current, high_ring, q, prefixes, shape.high_gap,
                                    shape.high_suffix, factory)
            current = outer.replace(current, following, source)
            result, current = current, None
            return result
        finally:
            if current is not None and current is not source:
                current.clear()


class CompactFitted:
    """Keep the source's encoded ownership, ROOT construction and callee boundary."""

    def fitted(self, payload, plan, prefixes, gap, suffix):
        with ExitStack() as cleanup:
            modulus = radix_power(plan["width"], self.q)
            remainder = radix_power(plan["remainder"], self.q)
            one = Count.literal(1)
            for value in (modulus, remainder, one):
                cleanup.callback(value.close)
            ring = ring_from_count(self.banks[0], modulus, cleanup)
            high = ring_from_count(self.banks[1], plan["rows"], cleanup)
            tail = (None if plan["remainder"].zero() else
                    ring_from_count(self.banks[2], remainder, cleanup))
            index_maximum = Count(plan["body"])
            cleanup.callback(index_maximum.close)
            if self.fixture_index_floor:
                floor = Count.literal(self.fixture_index_floor)
                if compare(index_maximum, floor) < 0:
                    index_maximum.close()
                    index_maximum = Count(floor)
                    cleanup.callback(index_maximum.close)
                floor.close()
            indices = self.banks[3]
            indices.prepare(index_maximum)
            size, depth = indices.load(plan["body"]), indices.zero()
            cleanup.callback(indices.free_many, size, depth)
            self.runtime.arena.prepare(modulus)
            self.runtime.indices.prepare(index_maximum)
            program = unit_program(indices, ring, size, depth, self.binding.codes.bits)
            directory = self.pool.acquire()
            cleanup.callback(program.tape.clear)
            cleanup.callback(directory.clear)
            actual_gap = Count.product(remainder, gap)
            following = Count.product(actual_gap, plan["rows"])
            actual_gap.close()
            actual_gap = following
            actual_suffix = Count.product(remainder, suffix)
            cleanup.callback(actual_gap.close)
            cleanup.callback(actual_suffix.close)

            def callee(padded, rows):
                if self.observe is not None:
                    self.observe("before", borrowed_tape(padded), None)
                with self.scope.suspended():
                    returned = self.runtime.run(
                        borrowed_tape(padded), borrowed_tape(directory), borrowed_tape(program.tape),
                        ring.modulus, size, depth, borrowed_count(prefixes), borrowed_count(rows),
                        borrowed_count(one), borrowed_count(actual_gap), borrowed_count(actual_suffix))
                if self.observe is not None:
                    self.observe("after", borrowed_tape(padded), returned)
                return returned

            return interchange(payload, size, ring, high, self.q, prefixes, gap, suffix,
                               plan["stock"], callee, tail, self.pool.acquire)
