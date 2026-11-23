"""Store independent fixed-grid Gaussian fields and scan them in order."""

from contextlib import ExitStack, contextmanager
from fractions import Fraction
from functools import cache
from math import gcd
from tempfile import TemporaryFile


def transfer(source, target, count):
    while count:
        block = source.read(min(count, 1 << 16))
        if not block:
            raise EOFError("The source field ended inside its declared extent")
        target.write(block)
        count -= len(block)


def zero_bytes(target, count):
    block = bytes(1 << 16)
    while count:
        size = min(count, len(block))
        target.write(block[:size])
        count -= size


@contextmanager
def scratch():
    with TemporaryFile() as tape:
        try:
            yield tape
        finally:
            tape.seek(0, 2)
            size = tape.tell()
            tape.seek(0)
            zero_bytes(tape, size)
            tape.truncate(0)


class Segment:
    def __init__(self, arena, slot):
        self.arena, self.slot = arena, slot
        self.pos = self.length = 0

    def seek(self, position):
        if not 0 <= position <= self.arena.extent:
            raise ValueError("Owner position is outside its frame")
        self.pos = position

    def tell(self):
        return self.pos

    def truncate(self):
        self.length = self.pos

    def read(self, size):
        available = min(size, self.length - self.pos)
        if available <= 0:
            return b""
        self.arena.tape.seek(self.arena.start + self.slot * self.arena.extent + self.pos)
        data = self.arena.tape.read(available)
        self.pos += len(data)
        return data

    def write(self, data):
        if self.pos + len(data) > self.arena.extent:
            raise ValueError("Write outside the owned complete field")
        self.arena.tape.seek(self.arena.start + self.slot * self.arena.extent + self.pos)
        self.arena.tape.write(data)
        self.pos += len(data)
        self.length = max(self.pos, self.length)

    def close(self):
        if self.slot is None:
            raise ValueError("Owner released twice")
        self.arena.free.append(self.slot)
        self.arena.live -= 1
        self.slot = None


class Arena:
    """Keep the fields of one active fixed-rank cohort in a tape interval."""

    def __init__(self, bits, component_bytes, tape=None, start=0):
        self.bits, self.component_bytes = bits, component_bytes
        self.tape, self.start = TemporaryFile() if tape is None else tape, start
        self.own_tape = tape is None
        self.extent = (1 << bits) * 2 * component_bytes
        self.free, self.high, self.live = [], 0, 0
        self.child_active = False

    def field(self):
        if self.child_active:
            raise ValueError("The parent frame is suspended until the child returns")
        if self.free:
            slot = self.free.pop()
        else:
            slot = self.high
            self.high += 1
        self.live += 1
        return Field(self.bits, self.component_bytes, Segment(self, slot), self)

    @contextmanager
    def child(self, ambient_bits):
        if self.child_active:
            raise ValueError("Two live children cannot share the next stack interval")
        self.child_active = True
        child = Arena(
            ambient_bits, self.component_bytes, self.tape, self.start + self.high * self.extent
        )
        try:
            yield child
            if child.live:
                raise ValueError("A completed child still owns a field")
        finally:
            self.child_active = False
            self.tape.truncate(child.start)

    def close(self):
        if self.live or self.child_active:
            raise ValueError("The arena still has live owners")
        if self.own_tape:
            self.tape.close()


@contextmanager
def snapshot(stream, size):
    """Stage one whole owner. The arena head then remains at its next operand."""
    with scratch() as work:
        stream.seek(0)
        transfer(stream, work, size)
        work.seek(0)
        yield work


def cold_swap(source, target, bits, prefix, gap, suffix_bytes):
    """Exchange two complete binary fields by ordinary four-bucket passes.

    The prefix and gap are cardinalities. A suffix is measured in bytes.
    Source and destination are seekable, independent open binary streams.
    """
    if min(bits, prefix, gap, suffix_bytes) < 1 or source is target:
        raise ValueError("The two streams and all physical extents are required")
    with ExitStack() as files:
        buckets = [files.enter_context(scratch()) for _ in range(4)]
        work = [files.enter_context(scratch()) for _ in range(2)]
        current = source
        for k in range(bits):
            out = target if k == bits - 1 else work[k % 2]
            current.seek(0)
            out.seek(0)
            head = prefix << (bits - k - 1)
            middle = gap << (bits - 1)
            tail = suffix_bytes << k
            for _ in range(head):
                for bucket in buckets:
                    bucket.seek(0)
                for x in (0, 1):
                    for _ in range(middle):
                        for y in (0, 1):
                            transfer(current, buckets[2 * x + y], tail)
                for bucket in buckets:
                    bucket.seek(0)
                for y in (0, 1):
                    for _ in range(middle):
                        for x in (0, 1):
                            transfer(buckets[2 * x + y], out, tail)
            current = out
        target.truncate()
        target.seek(0)


@cache
def short_divisors(value):
    """Use at most 24-bit factors of a fixed source scalar denominator."""
    factors = []
    for known in (1 << 23, 15658669, 13190315, 15217125, 243, 2025):
        while value >= 1 << 24:
            common = gcd(value, known)
            if common == 1:
                break
            factors.append(common)
            value //= common
    candidate = 2
    while value >= 1 << 24:
        if candidate * candidate > value or candidate >= 1 << 24:
            raise ValueError("The scalar source contains a factor above 24 bits")
        if value % candidate:
            candidate = 3 if candidate == 2 else candidate + 2
        else:
            factors.append(candidate)
            value //= candidate
    if value != 1:
        factors.append(value)
    return tuple(factors)


def integer_scale(value, ratio):
    """Divide before multiplying. Keep the fixed coefficient limbs small."""
    ratio = Fraction(ratio)
    dividend = value
    for divisor in short_divisors(ratio.denominator):
        dividend, remainder = divmod(dividend, divisor)
        if remainder:
            raise ArithmeticError("The prescribed scalar division is inexact")
    n = abs(ratio.numerator)
    answer = 0
    for offset in reversed(range(0, n.bit_length(), 23)):
        answer = (answer << 23) + dividend * ((n >> offset) & ((1 << 23) - 1))
    return -answer if ratio.numerator < 0 else answer


def quarter(value, exponent):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


class Field:
    def __init__(self, ambient_bits, component_bytes, stream=None, arena=None):
        if ambient_bits < 0 or component_bytes < 1:
            raise ValueError("Invalid fixed-grid field shape")
        self.ambient_bits = ambient_bits
        self.component_bytes = component_bytes
        self.stream = TemporaryFile() if stream is None else stream
        self.arena = arena

    @property
    def count(self):
        return 1 << self.ambient_bits

    @property
    def record(self):
        return 2 * self.component_bytes

    def blank(self):
        return (
            self.arena.field()
            if self.arena is not None
            else Field(self.ambient_bits, self.component_bytes)
        )

    def copy(self):
        result = self.blank()
        with snapshot(self.stream, self.count * self.record) as work:
            transfer(work, result.stream, self.count * self.record)
        return result

    def clear(self):
        self.stream.seek(0)
        zero_bytes(self.stream, self.count * self.record)
        self.stream.truncate()

    def retire(self):
        self.clear()
        self.stream.close()

    def records(self, staged):
        for _ in range(self.count):
            a = staged.read(self.component_bytes)
            b = staged.read(self.component_bytes)
            yield int.from_bytes(a, "little", signed=True), int.from_bytes(b, "little", signed=True)

    def values(self):
        with snapshot(self.stream, self.count * self.record) as inp:
            yield from self.records(inp)

    def write(self, values):
        self.stream.seek(0)
        count = 0
        for a, b in values:
            self.stream.write(a.to_bytes(self.component_bytes, "little", signed=True))
            self.stream.write(b.to_bytes(self.component_bytes, "little", signed=True))
            count += 1
        if count != self.count:
            raise ValueError("Gaussian field count differs from its declared extent")
        self.stream.truncate()

    def replace(self, other):
        if (other.ambient_bits, other.component_bytes) != (self.ambient_bits, self.component_bytes):
            raise ValueError("Cannot return unlike physical fields")
        if self.arena is not other.arena:
            raise ValueError("A returned slot must belong to the destination arena")
        old, self.stream = self.stream, other.stream
        other.stream = old
        other.retire()

    def scale_add(self, other, real=1, imag=0):
        def result():
            for (a, b), (c, d) in zip(self.values(), other.values(), strict=True):
                yield (
                    a + integer_scale(c, real) - integer_scale(d, imag),
                    b + integer_scale(d, real) + integer_scale(c, imag),
                )

        if self is other:
            self.scale(real + 1, imag)
            return
        work = self.blank()
        work.write(result())
        self.replace(work)

    def scale(self, real, imag=0):
        work = self.blank()
        work.write(
            (
                integer_scale(a, real) - integer_scale(b, imag),
                integer_scale(b, real) + integer_scale(a, imag),
            )
            for a, b in self.values()
        )
        self.replace(work)

    def phase(self, exponent, suffix=0):
        if not 0 <= suffix <= self.ambient_bits:
            raise ValueError("Phase grouping leaves the complete field")
        work = self.blank()
        with snapshot(self.stream, self.count * self.record) as staged:
            values = self.records(staged)

            def phases():
                for prefix in range(self.count >> suffix):
                    angle = exponent(prefix << suffix)
                    for _ in range(1 << suffix):
                        yield quarter(next(values), angle)

            work.write(phases())
        self.replace(work)

    def swap(self, a, b, bits, service):
        if a == b:
            return
        lo, hi = sorted((a, b))
        if lo < 0 or lo + bits > hi or hi + bits > self.ambient_bits:
            raise ValueError("The physical equal fields overlap or leave the tape")
        result = self.blank()
        with snapshot(self.stream, self.count * self.record) as inp:
            service(
                inp,
                result.stream,
                bits,
                1 << (self.ambient_bits - hi - bits),
                1 << (hi - lo - bits),
                self.record << lo,
            )
        self.replace(result)

    def rotate(self, lo, width, amount):
        """Rotate a full target per prefix. 'amount' only reads that prefix."""
        tail = self.record << lo
        size = 1 << width
        out = self.blank()
        with snapshot(self.stream, self.count * self.record) as inp, scratch() as first:
            for prefix in range(1 << (self.ambient_bits - lo - width)):
                offset = amount(prefix << (lo + width)) % size
                first.seek(0)
                split = (size - offset) * tail
                transfer(inp, first, split)
                transfer(inp, out.stream, offset * tail)
                first.seek(0)
                transfer(first, out.stream, split)
        self.replace(out)
