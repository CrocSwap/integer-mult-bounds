"""Count-driven exact multiplication by ((1-i)/2)**D on physical tapes.

The algebra and source tape framework are credited predecessors. This module
implements the variable-rank streaming boundary. Tekalign/Codex, Apache-2.0.
"""
import norm_sources
norm_sources.activate()
from cardinal_counts import Count, positive
from compact_counts import copy_bits
from encoded import compare, divide
from records import Tape
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_tape, erase_marker, initialize_marker,
                     sealed_constructors)
from stream import Counter
from words import BLANK, LEFT, RIGHT, need


class NormalizationError(ValueError):
    pass


def phase_rows(odd, phase):
    """One of eight compiled two-input signed row pairs, never a rank-sized word."""
    rows = ((1, 1), (-1, 1)) if odd else ((1, 0), (0, 1))
    real, imag = rows
    neg = lambda row: tuple(-entry for entry in row)
    return ((real, imag), (imag, neg(real)), (neg(real), neg(imag)),
            (neg(imag), real))[phase]


def low_phase(value):
    """Read two low bits of an encoded Count into four-state control."""
    value.rewind()
    phase = 0
    for position in range(2):
        if value.read() == RIGHT:
            break
        bit = value.read()
        need(bit in (0, 1), 'phase Count digit')
        phase |= bit << position
        value.step(1)
    value.rewind()
    return phase


def component(buffers, output, width, shift, signs):
    """Append exactly N/2**shift, or reject its divisibility/signed width.

N is a fixed signed sum of two width-bit inputs. Two extension digits suffice;
there is no materialized h-bit sum and no repeated HALF traversal.
"""
    incoming, skip, outgoing = Counter(width), Counter(shift), Counter(width)
    carry, output_sign = 0, 0
    sign_bits = (0, 0)

    def emit(digit):
        nonlocal output_sign
        if not skip.finished:
            if digit:
                raise NormalizationError('inexact normalization shift')
            skip.decrement()
        elif not outgoing.finished:
            output.append(digit)
            output_sign = digit
            outgoing.decrement()
        elif digit != output_sign:
            raise NormalizationError('normalization signed headroom')

    for source in buffers:
        source.rewind()
    try:
        while not incoming.finished:
            bits = tuple(source.read() for source in buffers)
            need(all(bit in (0, 1) for bit in bits), 'complete normalization words')
            for source in buffers:
                source.step(1)
            total = carry+sum(sign*bit for sign, bit in zip(signs, bits))
            digit, carry = total % 2, total // 2
            need(-2 <= carry <= 1, 'bounded normalization carry')
            emit(digit)
            sign_bits = bits
            incoming.decrement()
        need(all(source.read() == BLANK for source in buffers), 'exact normalization widths')
        for _ in range(2):
            total = carry+sum(sign*bit for sign, bit in zip(signs, sign_bits))
            digit, carry = total % 2, total // 2
            emit(digit)
        need(skip.finished, 'normalization shift bounded by input width')
        # The final extension digit is the exact numerator's sign.
        while not outgoing.finished:
            emit(digit)
    finally:
        for counter in (incoming, skip, outgoing):
            counter.close()
        for source in buffers:
            source.rewind()


class Normalizer:
    def __init__(self):
        # Four retained setup Counts, N countdown, two component buffers and
        # three local countdowns. Encoded division's separate setup peak is 5.
        self.pool = ScratchPool(10)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)
        self.closed = True

    def rearm(self):
        need(self.closed and self.output.read() == BLANK, 'consume normalization output')
        self.output.step(-1)
        marker = self.output.read()
        need(marker in (LEFT, BLANK), 'normalization output origin')
        if marker == BLANK:
            self.output.write(LEFT)
        self.output.step(1)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        self.closed = False

    def run(self, payload, width, gaussians, degree):
        """Borrow N h-bit Gaussian words; return owned b**D output at its origin.

Descriptors are canonical, disjoint Counts; h>=2, N>=1 and 0<=D<=h.
Named arithmetic rejection also erases partial output and permits reuse.
"""
        positive(width)
        positive(gaussians)
        need(isinstance(degree, Count), 'encoded normalization degree')
        source = borrowed_tape(payload)
        need(source is not self.output and all(source is not t for t in self.pool.tapes),
             'distinct normalization source and owned roles')
        self.rearm()
        two = half = remainder = shift = remaining = None
        buffers = ()
        error = None
        with sealed_constructors(), self.scope.installed():
            try:
                two = Count.literal(2)
                if compare(width, two) < 0 or compare(degree, width) > 0:
                    raise NormalizationError('normalization parameter domain')
                half, remainder = divide(degree, two)
                odd = not remainder.zero()
                rows = phase_rows(odd, low_phase(half))
                shift = Count(half)
                if odd:
                    shift.increment()
                remaining = Counter(gaussians)
                buffers = tuple(self.pool.acquire() for _ in range(2))
                source.rewind()
                while not remaining.finished:
                    for buffer in buffers:
                        copy_bits(source, buffer, width)
                        buffer.rewind()
                    for signs in rows:
                        component(buffers, self.output, width, shift, signs)
                    for buffer in buffers:
                        borrowed_tape(buffer).clear()
                    remaining.decrement()
                need(source.read() == BLANK, 'complete normalization packet')
            except NormalizationError as failure:
                error = failure
            finally:
                source.rewind()
                for buffer in buffers:
                    buffer.clear()
                for value in (two, half, remainder, shift, remaining):
                    if value is not None:
                        value.close()
                self.pool.empty()
        for tape in self.pool.tapes:
            erase_marker(tape)
        self.output.rewind()
        self.closed = True
        if error is not None:
            self.output.clear()
            erase_marker(self.output)
            raise error
        return self.output
