"""Four exact signed Kronecker products with one completed-coordinate rounding."""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import read_fixed, write_fixed
from encoded import compare, subtract
from fft_word_engine import FftWord
from gaussian_rows import magnitude_length
from records import Tape
from ring_words import Signed, add, power_two, read_signed, truncate, write_signed
from router_metadata import ceiling_log, indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, RIGHT, need


def measure(source, length, width):
    largest = Count.literal(1)
    source.rewind()
    try:
        for _ in indices(length):
            with owned(read_signed(source, width)) as (value,):
                with owned(magnitude_length(value.magnitude)) as (size,):
                    if compare(size, largest) > 0:
                        following = Count(size)
                        largest.close()
                        largest = following
        need(source.read() == BLANK, "complete Gaussian convolution input")
        return largest
    except BaseException:
        largest.close()
        raise
    finally:
        source.rewind()


def pack_signs(source, length, width, slot):
    plus, minus = Count.literal(0), Count.literal(0)
    borrowed_tape(plus.tape).clear()
    borrowed_tape(minus.tape).clear()
    source.rewind()
    try:
        with owned(Count.literal(0)) as (zero,):
            for _ in indices(length):
                with owned(read_signed(source, width)) as (value,):
                    chosen, other = (minus, plus) if value.negative else (plus, minus)
                    write_fixed(value.magnitude, chosen.tape, slot)
                    write_fixed(zero, other.tape, slot)
        need(source.read() == BLANK, "exact Gaussian packing extent")
        for value in (plus, minus):
            value.tape.append(RIGHT)
            value.normalize()
        return plus, minus
    except BaseException:
        plus.close()
        minus.close()
        raise
    finally:
        source.rewind()


class ConvolutionPlan:
    def __init__(self, length, width, precision):
        self.length, self.width, self.precision = length, width, precision
        self.fields = {}

    def keep(self, name, value):
        need(name not in self.fields, "one convolution numerical role")
        self.fields[name] = value
        return value

    def __getattr__(self, name):
        return self.fields[name]

    def compile(self, first, second):
        positive(self.length)
        positive(self.width)
        need(compare(self.precision, self.width) < 0, "Gaussian grid below signed width")
        self.keep("first_bits", measure(first, self.length, self.width))
        self.keep("second_bits", measure(second, self.length, self.width))
        self.keep("log_length", ceiling_log(self.length))
        self.keep("slot", Count(self.first_bits))
        self.slot.add(self.second_bits)
        self.slot.add(self.log_length)
        self.slot.increment()
        self.keep("operand_width", Count.product(self.length, self.slot))
        self.keep("accumulator_width", Count(self.slot))
        with owned(Count.literal(3), Count.literal(1)) as (three, one):
            self.accumulator_width.add(three)
            with owned(subtract(self.slot, one)) as (exponent,):
                self.keep("coefficient_limit", power_two(exponent))

    def close(self):
        for value in reversed(tuple(self.fields.values())):
            value.close()
        self.fields.clear()


class Convolution:
    def __init__(self, word=None):
        # A fixed crossover changes implementation constants only. PR3787's
        # separate checks exercise its FFT branch above its default cutoff.
        self.word = FftWord(base_bits=4096) if word is None else word
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        for value in (*self.pool.tapes, self.output):
            erase_marker(value)

    def idle(self):
        self.word.idle()
        need(self.word.closed and not self.word.pool.live and self.word.output.read() == BLANK,
             "consumed Gaussian convolution word child")

    def run(self, first, second, length, width, precision):
        first, second = borrowed_tape(first), borrowed_tape(second)
        length, width, precision = (borrowed_count(v) for v in (length, width, precision))
        forbidden = (*self.pool.tapes, self.output, *self.word.pool.tapes,
                     self.word.output, *self.word.canonical)
        need(first not in forbidden and second not in forbidden
             and all(v.tape not in forbidden for v in (length, width, precision)),
             "external Gaussian convolution ports")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior Gaussian convolution output")
        self.idle()
        for value in (*self.pool.tapes, self.output):
            initialize_marker(value)
        self.closed = False
        plan = accumulator = scratch = None
        first_plus = first_minus = second_plus = second_minus = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    plan = ConvolutionPlan(length, width, precision)
                    plan.compile(first, second)
                    first_plus, first_minus = pack_signs(first, length, width, plan.slot)
                    second_plus, second_minus = pack_signs(second, length, width, plan.slot)
                    accumulator, scratch = self.pool.acquire(), self.pool.acquire()
                    with owned(Signed(Count.literal(0))) as (zero,):
                        for _ in indices(length):
                            write_signed(zero, accumulator, plan.accumulator_width)
                    accumulator.rewind()
                    for a, b, negative in ((first_plus, second_plus, False),
                                           (first_minus, second_minus, False),
                                           (first_plus, second_minus, True),
                                           (first_minus, second_plus, True)):
                        with self.scope.suspended():
                            returned = self.word.run(*(borrowed_count(v) for v in
                                                       (a, b, plan.operand_width)))
                        try:
                            accumulator.rewind()
                            borrowed_tape(scratch).clear()
                            for _ in indices(length):
                                with owned(read_signed(accumulator, plan.accumulator_width)) as (previous,):
                                    with owned(read_fixed(returned, plan.slot)) as (coefficient,):
                                        need(compare(coefficient, plan.coefficient_limit) < 0,
                                             "strict signed-convolution coefficient separation")
                                        with owned(Signed(Count(coefficient), negative)) as (term,):
                                            with owned(add(previous, term)) as (following,):
                                                write_signed(following, scratch, plan.accumulator_width)
                            need(accumulator.read() == BLANK, "complete convolution accumulator")
                            for _ in indices(plan.operand_width):
                                need(returned.read() in (0, 1), "complete convolution word return")
                                returned.step(1)
                            need(returned.read() == BLANK, "exact convolution word-return extent")
                        finally:
                            returned.clear()
                            erase_marker(returned)
                        accumulator, scratch = scratch, accumulator
                        borrowed_tape(scratch).clear()
                        accumulator.rewind()
                        self.idle()
                    for _ in indices(length):
                        with owned(read_signed(accumulator, plan.accumulator_width)) as (value,):
                            with owned(truncate(value, precision)) as (rounded,):
                                write_signed(rounded, self.output, width)
                    need(accumulator.read() == BLANK, "complete rounded convolution")
                    self.calls += 1
                    succeeded = True
                finally:
                    for value in (first_plus, first_minus, second_plus, second_minus):
                        if value is not None:
                            value.close()
                    for value in (accumulator, scratch):
                        if value is not None:
                            value.clear()
                    if plan is not None:
                        plan.close()
                    for value in (first, second, length, width, precision):
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
