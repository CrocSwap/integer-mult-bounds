"""Chafik Boukhalfa's two-convolution local inverse on encoded physical rows."""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import append_bits, copy_bits
from encoded import compare
from fft_arithmetic import Arithmetic
from fft_word_engine import FftWord
from gaussian_convolution import Convolution
from gaussian_rationals import Rational
from gaussian_rows import reverse_records
from records import Tape
from ring_words import Signed, power_two, read_signed, truncate, write_signed
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, need


class InteriorFactors:
    names = ("weights", "inva", "f", "invf", "h")

    def __init__(self, length, width, precision, pool):
        positive(length)
        self.streams = {}
        self.length = self.width = self.precision = self.volume = None
        try:
            self.length, self.width, self.precision = Count(length), Count(width), Count(precision)
            self.volume = Count.product(length, width)
            for name in self.names:
                self.streams[name] = pool.acquire()
        except BaseException:
            self.close()
            raise

    def close(self):
        for value in self.streams.values():
            value.clear()
        self.streams.clear()
        for value in (self.length, self.width, self.precision, self.volume):
            if value is not None:
                value.close()
        self.length = self.width = self.precision = self.volume = None

    def rewind(self):
        for value in self.streams.values():
            value.rewind()

    def dump(self, destination):
        for name in self.names:
            append_bits(self.streams[name], destination)

    def load(self, source):
        for name in self.names:
            borrowed_tape(self.streams[name]).clear()
            copy_bits(source, self.streams[name], self.volume)
        self.rewind()

    def prepare(self, q_numerator, weights):
        weights.rewind()
        f = even_power = signed_power = None
        try:
            with owned(power_two(self.precision)) as (unit,):
                with owned(Count(unit)) as (quarter,):
                    quarter.divide_small(4)
                    need(not q_numerator.zero() and compare(q_numerator, quarter) <= 0,
                         "positive local Gaussian q at most one quarter")
                with owned(Rational(Signed(Count(q_numerator)), Count(unit))) as (q,):
                    with owned(q.times(q)) as (square,):
                        with owned(q.negated(), Rational.literal(1)) as (negative_q, one):
                            f = Rational.literal(1)
                            even_power = Rational.literal(1)
                            signed_power = Rational.literal(1)
                            for j in indices(self.length):
                                if not j.zero():
                                    following = even_power.times(square)
                                    even_power.close()
                                    even_power = following
                                    with owned(one.minus(even_power)) as (factor,):
                                        following = f.times(factor)
                                    f.close()
                                    f = following
                                    following = signed_power.times(negative_q)
                                    signed_power.close()
                                    signed_power = following
                                with owned(read_signed(weights, self.width)) as (weight,):
                                    need(not weight.negative and not weight.magnitude.zero()
                                         and compare(weight.magnitude, unit) <= 0,
                                         "positive retained Gaussian similarity weight")
                                    write_signed(weight, self.streams["weights"], self.width)
                                    with owned(Rational(Signed(Count(unit)), Count(weight.magnitude))) as (inva,):
                                        with owned(inva.rounded(self.precision)) as (value,):
                                            write_signed(value, self.streams["inva"], self.width)
                                with owned(f.rounded(self.precision)) as (value,):
                                    write_signed(value, self.streams["f"], self.width)
                                with owned(f.reciprocal()) as (reciprocal,):
                                    with owned(reciprocal.rounded(self.precision)) as (value,):
                                        write_signed(value, self.streams["invf"], self.width)
                                with owned(signed_power.over(f)) as (coefficient,):
                                    with owned(coefficient.rounded(self.precision)) as (value,):
                                        write_signed(value, self.streams["h"], self.width)
            need(weights.read() == BLANK, "complete local Gaussian weights")
        finally:
            for value in (f, even_power, signed_power):
                if value is not None:
                    value.close()
            weights.rewind()
            self.rewind()


class Interior:
    def __init__(self, word=None):
        self.word = FftWord(base_bits=4096) if word is None else word
        self.convolution = Convolution(self.word)
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.arithmetic = Arithmetic(self.word, self.scope)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        for value in (*self.pool.tapes, self.output):
            erase_marker(value)

    def idle(self):
        self.convolution.idle()
        need(self.convolution.closed and not self.convolution.pool.live
             and self.convolution.output.read() == BLANK, "consumed local Gaussian convolution")

    def diagonal(self, source, coefficients, target, length, width, precision):
        source.rewind()
        coefficients.rewind()
        try:
            for _ in indices(length):
                with owned(read_signed(source, width)) as (value,):
                    with owned(read_signed(coefficients, width)) as (factor,):
                        with owned(self.arithmetic.multiply(value, factor, width)) as (product,):
                            with owned(truncate(product, precision)) as (rounded,):
                                write_signed(rounded, target, width)
            need(source.read() == coefficients.read() == BLANK, "complete Gaussian diagonal pass")
        finally:
            source.rewind()
            coefficients.rewind()
            target.rewind()

    def lower(self, coefficients, source, target, length, width, precision, reverse=False):
        with self.scope.suspended():
            returned = self.convolution.run(coefficients, source, length, width, precision)
        try:
            if reverse:
                reverse_records(returned, target, length, width)
            else:
                append_bits(returned, target)
        finally:
            returned.clear()
            erase_marker(returned)
        target.rewind()

    def run(self, factors, source):
        source = borrowed_tape(source)
        length, width, precision = (borrowed_count(v) for v in
                                    (factors.length, factors.width, factors.precision))
        streams = {name: borrowed_tape(factors.streams[name]) for name in factors.names}
        forbidden = (*self.pool.tapes, self.output, *self.convolution.pool.tapes,
                     self.convolution.output, *self.word.pool.tapes, self.word.output,
                     *self.word.canonical)
        need(source not in forbidden and all(t not in forbidden for t in streams.values()),
             "external Gaussian interior ports")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior Gaussian interior output")
        self.idle()
        for value in (*self.pool.tapes, self.output):
            initialize_marker(value)
        self.closed = False
        first = second = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    first, second = self.pool.acquire(), self.pool.acquire()
                    self.diagonal(source, streams["inva"], first, length, width, precision)
                    self.diagonal(first, streams["invf"], second, length, width, precision)
                    borrowed_tape(first).clear()
                    self.lower(streams["h"], second, first, length, width, precision)
                    borrowed_tape(second).clear()
                    self.diagonal(first, streams["f"], second, length, width, precision)
                    borrowed_tape(first).clear()
                    reverse_records(second, first, length, width)
                    borrowed_tape(second).clear()
                    self.lower(streams["h"], first, second, length, width, precision, True)
                    borrowed_tape(first).clear()
                    self.diagonal(second, streams["invf"], first, length, width, precision)
                    self.diagonal(first, streams["weights"], self.output, length, width, precision)
                    self.idle()
                    self.calls += 1
                    succeeded = True
                finally:
                    for value in (first, second):
                        if value is not None:
                            value.clear()
                    source.rewind()
                    factors.rewind()
                    for value in (length, width, precision):
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
