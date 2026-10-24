"""Sequential rounded inverse-block pages on the retained physical word runtime.

Classical products are a charged fallback. They do not implement the proposed
seven-product asymptotic boundary improvement.
"""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import copy_bits
from encoded import compare, divide, subtract
from fft_arithmetic import Arithmetic
from fft_word_engine import FftWord
from gaussian_matrix import Matrix, inverse
from gaussian_rationals import Rational
from gaussian_rows import reverse_records
from records import Tape
from ring_words import Signed, add, difference, read_signed, scaled, truncate, write_signed
from router_metadata import ceiling_log, indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, need


def ceiling_division(value, divisor):
    quotient, remainder = divide(value, divisor)
    try:
        if not remainder.zero():
            quotient.increment()
        return quotient
    except BaseException:
        quotient.close()
        raise
    finally:
        remainder.close()


def prepare_pages(lower, upper, block, width, precision, pool):
    """Exact-reference inverse and preceding-block pages, then one P rounding."""
    positive(block)
    need(compare(lower.rows, lower.columns) == 0
         and compare(upper.rows, lower.rows) == 0
         and compare(upper.columns, lower.rows) == 0, 'square matching factors')
    pages = tuple(pool.acquire() for _ in (0, 1, 2, 3))
    success = False
    try:
        with owned(ceiling_division(lower.rows, block)) as (blocks,):
            with owned(Count.product(blocks, block)) as (padded,):
                for reverse, source, diagonal, coupling in (
                        (False, lower, pages[0], pages[1]), (True, upper, pages[2], pages[3])):
                    def original(r, c):
                        if compare(r, lower.rows) >= 0 or compare(c, lower.rows) >= 0:
                            return Rational.literal(1 if compare(r, c) == 0 else 0)
                        return source.get(r, c)

                    def entry(row, column):
                        if not reverse:
                            return original(row, column)
                        with owned(Count.literal(1)) as (one,):
                            with owned(subtract(padded, one)) as (last,):
                                with owned(subtract(last, row), subtract(last, column)) as (r, c):
                                    return original(r, c)

                    # Reject omitted earlier-block or upper-block couplings.
                    for i in indices(padded):
                        ib, remainder = divide(i, block)
                        remainder.close()
                        with owned(ib):
                            for j in indices(padded):
                                jb, remainder = divide(j, block)
                                remainder.close()
                                with owned(jb):
                                    with owned(Count(jb)) as (next_block,):
                                        next_block.increment()
                                        if compare(jb, ib) > 0 or compare(ib, next_block) > 0:
                                            with owned(entry(i, j)) as (value,):
                                                need(value.numerator.magnitude.zero(),
                                                     'exact adjacent-block factor support')

                    for b in indices(blocks):
                        with owned(Count.product(b, block)) as (start,):
                            def diagonal_entry(i, j):
                                with owned(Count(start), Count(start)) as (r, c):
                                    r.add(i)
                                    c.add(j)
                                    return entry(r, c)
                            matrix = Matrix(block, block, pool, diagonal_entry)
                            result = None
                            try:
                                result = inverse(matrix)
                                for i in indices(block):
                                    for j in indices(block):
                                        with owned(result.get(i, j)) as (value,):
                                            with owned(value.rounded(precision)) as (rounded,):
                                                write_signed(rounded, diagonal, width)
                            finally:
                                matrix.close()
                                if result is not None:
                                    result.close()
                            if not b.zero():
                                with owned(subtract(start, block)) as (previous,):
                                    for i in indices(block):
                                        for j in indices(block):
                                            with owned(Count(start), Count(previous)) as (r, c):
                                                r.add(i)
                                                c.add(j)
                                                with owned(entry(r, c)) as (value,):
                                                    with owned(value.rounded(precision)) as (rounded,):
                                                        write_signed(rounded, coupling, width)
                for page in pages:
                    page.rewind()
        success = True
        return pages
    finally:
        if not success:
            for page in pages:
                page.clear()


class BoundaryPages:
    def __init__(self):
        self.word = FftWord(base_bits=4096)
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.arithmetic = Arithmetic(self.word, self.scope)
        self.output = Tape()
        self.closed = True
        self.products = self.batches = 0
        for value in (*self.pool.tapes, self.output):
            erase_marker(value)

    def idle(self):
        self.word.idle()
        need(self.word.closed and not self.word.pool.live and self.word.output.read() == BLANK,
             'consumed physical scalar-product child')

    def transpose(self, source, destination, block, width):
        """Pay B full sequential scans; no indexed matrix get on online data."""
        for column in indices(block):
            source.rewind()
            for _ in indices(block):
                for j in indices(block):
                    with owned(read_signed(source, width)) as (value,):
                        if compare(j, column) == 0:
                            write_signed(value, destination, width)
            need(source.read() == BLANK, 'complete transpose matrix')
        source.rewind()
        destination.rewind()

    def product(self, first, second, destination, block, width, wide):
        transposed, row = self.pool.acquire(), self.pool.acquire()
        try:
            self.transpose(second, transposed, block, width)
            first.rewind()
            for _ in indices(block):
                with owned(Count.product(block, width)) as (row_bits,):
                    copy_bits(first, row, row_bits)
                row.rewind()
                transposed.rewind()
                for _ in indices(block):
                    total = Signed(Count.literal(0))
                    try:
                        for _ in indices(block):
                            with owned(read_signed(row, width), read_signed(transposed, width)) as (a, b):
                                with owned(self.arithmetic.multiply(a, b, width)) as (term,):
                                    following = add(total, term)
                            total.close()
                            total = following
                        need(row.read() == BLANK, 'complete scalar row product')
                        write_signed(total, destination, wide)
                    finally:
                        total.close()
                        row.rewind()
                need(transposed.read() == BLANK, 'complete transposed factor')
                borrowed_tape(row).clear()
            need(first.read() == BLANK, 'complete first product matrix')
            self.products += 1
        finally:
            transposed.clear()
            row.clear()
            first.rewind()
            second.rewind()
            destination.rewind()

    def pass_blocks(self, diagonals, couplings, rhs, output, blocks, block, width, wide, precision):
        previous, current, diagonal, coupling, temporary, residual = (self.pool.acquire() for _ in range(6))
        try:
            with owned(Count.product(block, block)) as (entries,):
                with owned(Count.product(entries, width)) as (bits,):
                    for b in indices(blocks):
                        copy_bits(diagonals, diagonal, bits)
                        copy_bits(rhs, current, bits)
                        diagonal.rewind()
                        current.rewind()
                        if b.zero():
                            copy_bits(current, residual, bits)
                        else:
                            copy_bits(couplings, coupling, bits)
                            coupling.rewind()
                            self.product(coupling, previous, temporary, block, width, wide)
                            for _ in indices(entries):
                                with owned(read_signed(current, width), read_signed(temporary, wide)) as (y, term):
                                    with owned(scaled(y, precision)) as (shifted,):
                                        with owned(difference(shifted, term)) as (value,):
                                            with owned(truncate(value, precision)) as (rounded,):
                                                write_signed(rounded, residual, width)
                            need(current.read() == temporary.read() == BLANK, 'complete rounded RHS update')
                            borrowed_tape(temporary).clear()
                        residual.rewind()
                        self.product(diagonal, residual, temporary, block, width, wide)
                        borrowed_tape(previous).clear()
                        for _ in indices(entries):
                            with owned(read_signed(temporary, wide)) as (value,):
                                with owned(truncate(value, precision)) as (rounded,):
                                    write_signed(rounded, previous, width)
                                    write_signed(rounded, output, width)
                        need(temporary.read() == BLANK, 'complete rounded solved block')
                        previous.rewind()
                        for value in (current, diagonal, coupling, temporary, residual):
                            borrowed_tape(value).clear()
                    need(diagonals.read() == couplings.read() == rhs.read() == BLANK,
                         'complete inverse/coupling/RHS page extents')
        finally:
            for value in (previous, current, diagonal, coupling, temporary, residual):
                value.clear()
            diagonals.rewind()
            couplings.rewind()
            rhs.rewind()
            output.rewind()

    def run(self, lower_d, lower_b, upper_d, upper_b, rhs, length, columns, block, width, precision):
        sources = tuple(borrowed_tape(t) for t in (lower_d, lower_b, upper_d, upper_b, rhs))
        metadata = tuple(borrowed_count(c) for c in (length, columns, block, width, precision))
        length, columns, block, width, precision = metadata
        forbidden = (*self.pool.tapes, self.output, *self.word.pool.tapes,
                     self.word.output, *self.word.canonical)
        need(all(t not in forbidden for t in sources) and len(set(sources)) == 5
             and all(c.tape not in forbidden and c.tape not in sources for c in metadata),
             'external distinct boundary page ports')
        for value in (length, columns, block, width):
            positive(value)
        need(compare(precision, width) < 0, 'physical boundary fractional width')
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             'consume previous boundary-page output')
        self.idle()
        for value in (*self.pool.tapes, self.output):
            initialize_marker(value)
        self.closed = False
        success = False
        try:
            with sealed_constructors(), self.scope.installed():
                with owned(ceiling_division(length, block), ceiling_division(columns, block),
                           Count(width)) as (blocks, batches, wide):
                    with owned(ceiling_log(block)) as (logarithm,):
                        wide.multiply_small(2)
                        wide.add(logarithm)
                        with owned(Count.literal(2)) as (guard,):
                            wide.add(guard)
                    with owned(Count.product(blocks, block), Count.product(block, width)) as (rows, row_bits):
                        with owned(Count.product(rows, row_bits)) as (batch_bits,):
                            for batch in indices(batches):
                                packed, forward, reverse_rhs, backward, returned = (self.pool.acquire() for _ in range(5))
                                try:
                                    copy_bits(sources[4], packed, batch_bits)
                                    packed.rewind()
                                    with owned(Count.product(batch, block)) as (start,):
                                        for i in indices(rows):
                                            for j in indices(block):
                                                with owned(Count(start)) as (column,):
                                                    column.add(j)
                                                    with owned(read_signed(packed, width)) as (value,):
                                                        if compare(i, length) >= 0 or compare(column, columns) >= 0:
                                                            need(value.magnitude.zero(), 'zero incomplete row/RHS padding')
                                    packed.rewind()
                                    self.pass_blocks(sources[0], sources[1], packed, forward,
                                                     blocks, block, width, wide, precision)
                                    reverse_records(forward, reverse_rhs, rows, row_bits)
                                    self.pass_blocks(sources[2], sources[3], reverse_rhs, backward,
                                                     blocks, block, width, wide, precision)
                                    reverse_records(backward, returned, rows, row_bits)
                                    copy_bits(returned, self.output, batch_bits)
                                    self.batches += 1
                                finally:
                                    for value in (packed, forward, reverse_rhs, backward, returned):
                                        value.clear()
                            need(sources[4].read() == BLANK, 'complete boundary RHS batches')
                self.idle()
                success = True
        finally:
            for value in sources + metadata:
                value.rewind()
            self.pool.empty()
            for value in self.pool.tapes:
                erase_marker(value)
            self.output.rewind()
            if not success:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output
