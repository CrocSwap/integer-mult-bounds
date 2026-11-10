"""Complete fine-gap run inverse on the authenticated encoded tape cohort.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
All numerical data and variable loop bounds are encoded Count/Signed objects.
Host counters are passive diagnostics. Gaussian and convolution identities
are inherited from CrocSwap/integer-mult-bounds#5571, #3851 and #3787.
"""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import copy_bits
from encoded import compare, subtract
from fft_arithmetic import Arithmetic
from fft_word_engine import FftWord
from gaussian_convolution import Convolution
from gaussian_rows import reverse_records
from records import Tape
from ring_words import Signed, difference, power_two, read_signed, scaled, truncate, write_signed
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, need


class RunInverse:
    def __init__(self):
        self.scalar_word = FftWord(base_bits=4096)
        self.convolution = Convolution()
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.arithmetic = Arithmetic(self.scalar_word, self.scope)
        self.output = Tape()
        self.closed = True
        self.calls = self.blocks = self.recurrence_rows = 0
        self.diagonal_rows = self.reversals = 0
        self.singletons = 0
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        self.scalar_word.idle()
        self.convolution.idle()
        need(self.scalar_word.closed and not self.scalar_word.pool.live
             and self.scalar_word.output.read() == BLANK, "consumed scalar word owner")
        need(self.convolution.closed and not self.convolution.pool.live
             and self.convolution.output.read() == BLANK, "consumed residual convolution")

    def forbidden(self):
        def word_roles(word):
            # Fixed structural inventory, including inactive descendants.
            return (*word.pool.tapes, word.output, *word.canonical,
                    *word.base.pool.tapes, *word.product.pool.tapes,
                    *word.product.word.pool.tapes, *word.product.twiddles.pool.tapes)
        return (*self.pool.tapes, self.output, *self.convolution.pool.tapes,
                self.convolution.output, *word_roles(self.convolution.word),
                *word_roles(self.scalar_word))

    def diagonal(self, source, coefficients, destination, n, width, precision):
        source.rewind(); coefficients.rewind()
        try:
            for _ in indices(n):
                with owned(read_signed(source, width), read_signed(coefficients, width)) as (x, a):
                    need(not a.negative and not a.magnitude.zero(), "positive run diagonal")
                    with owned(self.arithmetic.multiply(x, a, width)) as (product,):
                        with owned(truncate(product, precision)) as (rounded,):
                            write_signed(rounded, destination, width)
                self.diagonal_rows += 1
            need(source.read() == coefficients.read() == BLANK, "complete run diagonal ports")
        finally:
            source.rewind(); coefficients.rewind(); destination.rewind()

    def recurrence(self, source, coefficients, destination, n, width, precision):
        source.rewind(); coefficients.rewind()
        previous = Signed(Count.literal(0))
        following = None
        first = True
        try:
            with owned(power_two(precision)) as (unit,):
                for _ in indices(n):
                    with owned(read_signed(source, width), read_signed(coefficients, width)) as (rhs, mu):
                        need(not mu.negative and compare(mu.magnitude, unit) < 0,
                             "inward stable recurrence coefficient")
                        need(not first or mu.magnitude.zero(), "zero first recurrence coefficient")
                        with owned(scaled(rhs, precision), self.arithmetic.multiply(mu, previous, width)) as (wide_rhs, product):
                            with owned(difference(wide_rhs, product)) as (residual,):
                                following = truncate(residual, precision)
                        write_signed(following, destination, width)
                    previous.close(); previous, following = following, None
                    first = False
                    self.recurrence_rows += 1
            need(source.read() == coefficients.read() == BLANK, "complete run recurrence ports")
        finally:
            previous.close()
            if following is not None:
                following.close()
            source.rewind(); coefficients.rewind(); destination.rewind()

    def residual_block(self, source, page, destination, size, crop, block, width, precision):
        data, kernel = self.pool.acquire(), self.pool.acquire()
        try:
            for _ in indices(size):
                with owned(read_signed(source, width), read_signed(page, width)) as (x, gauge):
                    need(not gauge.negative and not gauge.magnitude.zero(), "positive inverse local gauge")
                    with owned(self.arithmetic.multiply(x, gauge, width)) as (product,):
                        with owned(truncate(product, precision)) as (rounded,):
                            write_signed(rounded, data, width)
            data.rewind()
            with owned(Count.product(size, width)) as (bits,):
                copy_bits(page, kernel, bits)
            kernel.rewind()
            with self.scope.suspended():
                returned = self.convolution.run(data, kernel, size, width, precision)
            try:
                with owned(Count.product(crop, width)) as (bits,):
                    for _ in indices(bits):
                        need(returned.read() in (0, 1), "complete cropped residual prefix")
                        returned.step(1)
                for _ in indices(block):
                    with owned(read_signed(returned, width), read_signed(page, width)) as (x, gauge):
                        need(not gauge.negative and not gauge.magnitude.zero(), "positive output local gauge")
                        with owned(self.arithmetic.multiply(x, gauge, width)) as (product,):
                            with owned(truncate(product, precision)) as (rounded,):
                                write_signed(rounded, destination, width)
                need(returned.read() == BLANK, "complete residual convolution return")
            finally:
                returned.clear(); erase_marker(returned)
            self.blocks += 1
        finally:
            data.clear(); kernel.clear()

    def residual(self, source, page, destination, n, cutoff, width, precision):
        source.rewind(); page.rewind()
        position, remaining = Count.literal(0), Count(n)
        try:
            while not remaining.zero():
                block = Count(cutoff if compare(cutoff, remaining) <= 0 else remaining)
                crop = Count(cutoff if compare(cutoff, position) <= 0 else position)
                size = Count(crop)
                try:
                    size.add(block)
                    self.residual_block(source, page, destination, size, crop, block, width, precision)
                    position.add(block)
                    following = subtract(remaining, block)
                    remaining.close(); remaining = following
                    if not remaining.zero():
                        with owned(Count(cutoff if compare(cutoff, position) <= 0 else position)) as (back,):
                            with owned(Count.product(back, width)) as (bits,):
                                for _ in indices(bits):
                                    source.step(-1)
                finally:
                    size.close(); crop.close(); block.close()
            need(source.read() == page.read() == BLANK, "complete run residual ports")
            need(compare(position, n) == 0, "complete residual output rows")
        finally:
            position.close(); remaining.close()
            source.rewind(); page.rewind(); destination.rewind()

    def singleton(self, source, streams, width, precision):
        """The one-row Gaussian block is exactly one; check its short pages."""
        with owned(power_two(precision)) as (unit,):
            for tape in (streams[0], streams[1]):
                with owned(read_signed(tape, width)) as (value,):
                    need(not value.negative and compare(value.magnitude, unit) == 0,
                         "singleton unit diagonal")
                need(tape.read() == BLANK, "singleton complete diagonal")
            for tape in (streams[2], streams[3]):
                with owned(read_signed(tape, width)) as (value,):
                    need(value.magnitude.zero(), "singleton zero recurrence")
                need(tape.read() == BLANK, "singleton complete recurrence")
            for tape in (streams[4], streams[5]):
                for _ in (0, 1, 2):
                    with owned(read_signed(tape, width)) as (value,):
                        need(not value.negative and compare(value.magnitude, unit) == 0,
                             "singleton unit residual page")
                need(tape.read() == BLANK, "singleton complete residual page")
        copy_bits(source, self.output, width)
        need(source.read() == BLANK, "singleton complete source")
        self.singletons += 1

    def run(self, source, finv, f, mu_minus, mu_plus, residual_minus,
            residual_plus, n, cutoff, width, precision):
        """Borrow seven full streams and four canonical counts; return one body.

        Coefficient production and its source/error certificate are separate
        paid preparation. Streams are two's-complement Signed records; every
        complete port begins and returns at its origin. The caller consumes,
        clears and erases the protected output before another invocation.
        """
        source = borrowed_tape(source)
        streams = tuple(borrowed_tape(v) for v in
                        (finv, f, mu_minus, mu_plus, residual_minus, residual_plus))
        n, cutoff, width, precision = tuple(borrowed_count(v) for v in
                                          (n, cutoff, width, precision))
        ports = (source, *streams)
        descriptor_tapes = tuple(v.tape for v in (n, cutoff, width, precision))
        all_ports = (*ports, *descriptor_tapes)
        forbidden = self.forbidden()
        need(all(t not in forbidden for t in all_ports), "external run ports")
        need(all(all_ports[i] is not all_ports[j] for i in range(11) for j in range(i)),
             "pairwise disjoint run and descriptor ports")
        positive(n); positive(cutoff); positive(width)
        need(compare(cutoff, n) <= 0 and compare(precision, width) < 0,
             "capped positive run cutoff and signed grid width")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior run output")
        self.idle()
        for value in (*self.pool.tapes, self.output):
            initialize_marker(value)
        self.closed = False
        first = second = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    for value in ports:
                        value.rewind()
                    with owned(Count.literal(1)) as (one,):
                        single = compare(n, one) == 0
                    if single:
                        self.singleton(source, streams, width, precision)
                    else:
                        first, second = self.pool.acquire(), self.pool.acquire()
                        self.diagonal(source, streams[0], first, n, width, precision)
                        self.residual(first, streams[4], second, n, cutoff, width, precision)
                        borrowed_tape(first).clear()
                        self.recurrence(second, streams[2], first, n, width, precision)
                        borrowed_tape(second).clear()
                        self.diagonal(first, streams[1], second, n, width, precision)
                        borrowed_tape(first).clear()
                        reverse_records(second, first, n, width)
                        self.reversals += 1
                        borrowed_tape(second).clear()
                        self.residual(first, streams[5], second, n, cutoff, width, precision)
                        borrowed_tape(first).clear()
                        self.recurrence(second, streams[3], first, n, width, precision)
                        borrowed_tape(second).clear()
                        reverse_records(first, second, n, width)
                        self.reversals += 1
                        borrowed_tape(first).clear()
                        self.diagonal(second, streams[0], self.output, n, width, precision)
                    self.idle()
                    self.calls += 1
                    succeeded = True
                finally:
                    for value in (first, second):
                        if value is not None:
                            value.clear()
                    for value in (*ports, n, cutoff, width, precision):
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
