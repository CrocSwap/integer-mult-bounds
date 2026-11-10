"""Literal interleaved nilpotent lift for an encoded banded forward action.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import copy_bits
from encoded import compare, subtract
from records import Tape
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, need
from boundary_pages import ceiling_division
from fast_boundary import FastBoundaryPages, origin, dyadic


def bit(tape):
    value = tape.read()
    need(value in (0, 1), 'complete band-action binary field')
    tape.step(1)
    return value


def zeroes(tape, length):
    for _ in indices(length):
        tape.append(0)


def zero_field(tape, length):
    for _ in indices(length):
        need(bit(tape) == 0, 'zero band-action padding')


class BandedAction:
    def __init__(self):
        self.child = FastBoundaryPages()
        self.pool = ScratchPool(128)
        self.scope = OuterScope(self.pool)
        self.dilated, self.output = Tape(), Tape()
        self.closed, self.pending = True, False
        self.calls = 0
        for tape in (*self.pool.tapes, self.dilated, self.output):
            erase_marker(tape)

    def forbidden(self):
        return (*self.pool.tapes, self.dilated, self.output, *self.child.forbidden())

    def idle(self):
        need(self.closed and not self.pending and not self.pool.live
             and self.output.read() == BLANK, 'consume prior band-action return')
        self.child.idle()
        need(self.child.closed and not self.child.pending and not self.child.pool.live,
             'consumed band-action child')

    def consume(self):
        need(self.closed and self.pending, 'one pending band-action return')
        self.output.clear()
        erase_marker(self.output)
        self.pending = False
        self.idle()

    def run(self, source, pages, length, columns, block, width, precision):
        need(len(pages) == 4, 'four nilpotent action page banks')
        source = borrowed_tape(source)
        pages = tuple(borrowed_tape(tape) for tape in pages)
        metadata = tuple(borrowed_count(value) for value in
                         (length, columns, block, width, precision))
        length, columns, block, width, precision = metadata
        sources = (source, *pages)
        forbidden = self.forbidden()
        need(len(set(sources)) == len(sources)
             and all(tape not in forbidden for tape in sources)
             and all(value.tape not in forbidden and value.tape not in sources
                     for value in metadata), 'external distinct band-action ports')
        self.idle()
        ports = (*sources, *(value.tape for value in metadata))
        for tape in ports:
            origin(tape)
        for value in (length, columns, block, width):
            positive(value)
        dyadic(block)
        need(compare(precision, width) < 0, 'band-action fractional width')
        for tape in (*self.pool.tapes, self.dilated, self.output):
            initialize_marker(tape)
        self.closed = False
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                with owned(Count(length), ceiling_division(length, block),
                           ceiling_division(columns, block),
                           Count.product(block, width)) as (twice, row_blocks, batches, row_bits):
                    twice.multiply_small(2)
                    with owned(ceiling_division(twice, block),
                               Count.product(row_blocks, block)) as (lift_blocks, padded):
                        with owned(Count.product(lift_blocks, block)) as (lift_padded,):
                            with owned(subtract(lift_padded, twice),
                                       subtract(padded, length)) as (lift_tail, tail):
                                with owned(Count.product(lift_tail, row_bits),
                                           Count.product(tail, row_bits)) as (lift_bits, tail_bits):
                                    for _ in indices(batches):
                                        for row in indices(padded):
                                            if compare(row, length) < 0:
                                                zeroes(self.dilated, row_bits)
                                                copy_bits(source, self.dilated, row_bits)
                                            else:
                                                zero_field(source, row_bits)
                                        zeroes(self.dilated, lift_bits)
                                    need(source.read() == BLANK, 'complete band-action source batches')
                                    source.rewind()
                                    self.dilated.rewind()
                                    with self.scope.suspended():
                                        returned = self.child.run(*pages, self.dilated, twice,
                                                                  columns, block, width, precision)
                                    try:
                                        for _ in indices(batches):
                                            for _ in indices(length):
                                                copy_bits(returned, self.output, row_bits)
                                                for _ in indices(row_bits):
                                                    need(bit(returned) == bit(source),
                                                         'nilpotent source rows preserved exactly')
                                            zero_field(source, tail_bits)
                                            zero_field(returned, lift_bits)
                                            zeroes(self.output, tail_bits)
                                        need(source.read() == returned.read() == BLANK,
                                             'complete projected band-action return')
                                    finally:
                                        if self.child.pending:
                                            self.child.consume()
                    self.child.idle()
                    self.calls += 1
                    succeeded = self.pending = True
        finally:
            if self.child.pending:
                self.child.consume()
            for tape in ports:
                tape.rewind()
            self.dilated.clear()
            self.pool.empty()
            for tape in (*self.pool.tapes, self.dilated):
                erase_marker(tape)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
                self.pending = False
            self.closed = True
        return self.output
