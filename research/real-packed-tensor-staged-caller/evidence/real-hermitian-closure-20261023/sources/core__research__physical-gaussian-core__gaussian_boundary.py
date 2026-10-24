"""Sequential banded forward/backward solve with complete dot-product rounding."""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import copy_bits
from encoded import compare, subtract
from fft_arithmetic import Arithmetic
from fft_word_engine import FftWord
from gaussian_rationals import Rational
from gaussian_rows import reverse_records
from records import Tape
from ring_words import Signed, difference, read_signed, scaled, truncate, write_signed
from router_metadata import ceiling_log, indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, need


def prepare_bands(lower, upper, band, width, precision, pool):
    """Round exact factors only after the caller has rounded S and computed LU."""
    positive(band)
    length = lower.rows
    need(compare(lower.columns, length) == 0 and compare(upper.rows, length) == 0
         and compare(upper.columns, length) == 0, "matching square boundary factors")
    first, second = pool.acquire(), pool.acquire()
    succeeded = False
    try:
        for i in indices(length):
            for j in indices(length):
                with owned(lower.get(i, j)) as (low,):
                    with owned(upper.get(i, j)) as (high,):
                        if compare(i, j) > 0:
                            with owned(subtract(i, j)) as (distance,):
                                need(high.numerator.magnitude.zero()
                                     and (compare(distance, band) <= 0 or low.numerator.magnitude.zero()),
                                     "exact lower factor band")
                        elif compare(i, j) < 0:
                            with owned(subtract(j, i)) as (distance,):
                                need(low.numerator.magnitude.zero()
                                     and (compare(distance, band) <= 0 or high.numerator.magnitude.zero()),
                                     "exact upper factor band")
                        else:
                            with owned(Rational.literal(1)) as (one,):
                                need(low.compare(one) == 0, "unit exact lower diagonal")
            for offset in indices(band):
                with owned(subtract(band, offset)) as (distance,):
                    if compare(i, distance) >= 0:
                        with owned(subtract(i, distance)) as (j,):
                            coefficient = lower.get(i, j)
                    else:
                        coefficient = Rational.literal(0)
                with owned(coefficient):
                    with owned(coefficient.rounded(precision)) as (rounded,):
                        write_signed(rounded, first, width)
        with owned(Count.literal(1)) as (one,):
            with owned(subtract(length, one)) as (last,):
                for offset in indices(length):
                    with owned(subtract(last, offset)) as (i,):
                        for step in indices(band):
                            with owned(Count(i)) as (j,):
                                j.add(step)
                                j.increment()
                                coefficient = upper.get(i, j) if compare(j, length) < 0 else Rational.literal(0)
                            with owned(coefficient):
                                with owned(coefficient.rounded(precision)) as (rounded,):
                                    write_signed(rounded, second, width)
                        with owned(upper.get(i, i)) as (diagonal,):
                            need(not diagonal.numerator.negative and not diagonal.numerator.magnitude.zero(),
                                 "positive exact boundary pivot")
                            with owned(diagonal.reciprocal()) as (reciprocal,):
                                with owned(reciprocal.rounded(precision)) as (rounded,):
                                    write_signed(rounded, second, width)
        first.rewind()
        second.rewind()
        succeeded = True
        return first, second
    finally:
        if not succeeded:
            first.clear()
            second.clear()


def subtract_row(arithmetic, right_hand, coefficients, values, length, width, precision):
    """Return the exact 2P-grid residual; advance only the coefficient bank."""
    total = scaled(right_hand, precision)
    values.rewind()
    try:
        for _ in indices(length):
            with owned(read_signed(coefficients, width)) as (coefficient,):
                with owned(read_signed(values, width)) as (value,):
                    with owned(arithmetic.multiply(coefficient, value, width)) as (product,):
                        following = difference(total, product)
            total.close()
            total = following
        need(values.read() == BLANK, "complete banded row buffer")
        result, total = total, None
        return result
    finally:
        if total is not None:
            total.close()
        values.rewind()


def push_window(source, destination, value, length, width, prepend=False):
    """Move one bounded O(w)-record buffer per solved row."""
    source.rewind()
    borrowed_tape(destination).clear()
    try:
        with owned(Count.literal(1)) as (one,):
            with owned(subtract(length, one)) as (remaining,):
                with owned(Count.product(remaining, width)) as (bits,):
                    if prepend:
                        write_signed(value, destination, width)
                        copy_bits(source, destination, bits)
                        for _ in indices(width):
                            need(source.read() in (0, 1), "complete discarded future-buffer record")
                            source.step(1)
                    else:
                        for _ in indices(width):
                            need(source.read() in (0, 1), "complete discarded past-buffer record")
                            source.step(1)
                        copy_bits(source, destination, bits)
                        write_signed(value, destination, width)
        need(source.read() == BLANK, "exact bounded row-buffer extent")
    finally:
        source.rewind()
        destination.rewind()


class BandedSolve:
    def __init__(self, word=None):
        self.word = FftWord(base_bits=4096) if word is None else word
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.arithmetic = Arithmetic(self.word, self.scope)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        for value in (*self.pool.tapes, self.output):
            erase_marker(value)

    def idle(self):
        self.word.idle()
        need(self.word.closed and not self.word.pool.live and self.word.output.read() == BLANK,
             "consumed banded-solve word child")

    def run(self, lower, upper_reverse, right_hand, length, band, width, precision):
        lower, upper_reverse, right_hand = (borrowed_tape(v) for v in (lower, upper_reverse, right_hand))
        length, band, width, precision = (borrowed_count(v) for v in (length, band, width, precision))
        for value in (length, band, width):
            positive(value)
        need(compare(precision, width) < 0, "banded-solve fractional width")
        forbidden = (*self.pool.tapes, self.output, *self.word.pool.tapes,
                     self.word.output, *self.word.canonical)
        need(all(v not in forbidden for v in (lower, upper_reverse, right_hand))
             and all(v.tape not in forbidden for v in (length, band, width, precision)),
             "external banded-solve ports")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior banded-solve output")
        self.idle()
        for value in (*self.pool.tapes, self.output):
            initialize_marker(value)
        self.closed = False
        past = work = forward = reverse_rhs = backward = wide = double_precision = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    past, work, forward, reverse_rhs, backward = (self.pool.acquire() for _ in range(5))
                    wide, double_precision = Count(width), Count(precision)
                    wide.multiply_small(2)
                    double_precision.multiply_small(2)
                    with owned(Count(band), Count.literal(2)) as (terms, guard):
                        terms.increment()
                        with owned(ceiling_log(terms)) as (logarithm,):
                            wide.add(logarithm)
                            wide.add(guard)
                    with owned(Signed(Count.literal(0))) as (zero,):
                        for _ in indices(band):
                            write_signed(zero, past, width)
                    past.rewind()
                    lower.rewind()
                    right_hand.rewind()
                    for _ in indices(length):
                        with owned(read_signed(right_hand, width)) as (rhs,):
                            with owned(subtract_row(self.arithmetic, rhs, lower, past,
                                                    band, width, precision)) as (residual,):
                                with owned(truncate(residual, precision)) as (value,):
                                    write_signed(value, forward, width)
                                    push_window(past, work, value, band, width)
                        past, work = work, past
                        borrowed_tape(work).clear()
                    need(lower.read() == right_hand.read() == BLANK, "complete banded forward pass")
                    reverse_records(forward, reverse_rhs, length, width)
                    borrowed_tape(past).clear()
                    with owned(Signed(Count.literal(0))) as (zero,):
                        for _ in indices(band):
                            write_signed(zero, past, width)
                    past.rewind()
                    upper_reverse.rewind()
                    for _ in indices(length):
                        with owned(read_signed(reverse_rhs, width)) as (rhs,):
                            with owned(subtract_row(self.arithmetic, rhs, upper_reverse, past,
                                                    band, width, precision)) as (residual,):
                                with owned(read_signed(upper_reverse, width)) as (reciprocal,):
                                    need(not reciprocal.negative and not reciprocal.magnitude.zero(),
                                         "positive rounded boundary pivot reciprocal")
                                    with owned(self.arithmetic.multiply(residual, reciprocal, wide)) as (product,):
                                        with owned(truncate(product, double_precision)) as (value,):
                                            write_signed(value, backward, width)
                                            push_window(past, work, value, band, width, True)
                        past, work = work, past
                        borrowed_tape(work).clear()
                    need(upper_reverse.read() == reverse_rhs.read() == BLANK, "complete banded backward pass")
                    reverse_records(backward, self.output, length, width)
                    self.idle()
                    self.calls += 1
                    succeeded = True
                finally:
                    for value in (past, work, forward, reverse_rhs, backward):
                        if value is not None:
                            value.clear()
                    for value in (wide, double_precision):
                        if value is not None:
                            value.close()
                    for value in (lower, upper_reverse, right_hand, length, band, width, precision):
                        value.rewind()
                    self.pool.empty()
        finally:
            for value in self.pool.tapes:
                erase_marker(value)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output
