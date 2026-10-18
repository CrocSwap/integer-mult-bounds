"""Produce all high fields while preserving physical old-prefix multiplicity."""
from cardinality import radix_power
from counts import Count, high_count, high_power
from records import RECORD_END, Tape, append_finite, append_word, read_finite, read_word
from stream import Counter
from words import BLANK, RIGHT, ZERO, need


class Context:
    def __init__(self, ring, vocabulary):
        self.ring, self.arena, self.raw = ring, ring.arena, ring.raw
        self.codes = vocabulary
        self.q, self.dimension = vocabulary.q, vocabulary.dimension
        for _ in radix_power(ring, self.q):
            pass
        divisor = self.arena.literal(self.q)
        self.cap, remainder = self.raw.divmod(ring.modulus, divisor)
        need(remainder.zero() and not self.cap.zero(), "positive high-field radix")
        self.arena.free_many(divisor, remainder)
        self.highs = high_count(ring, self.q, self.dimension)

    def close(self):
        self.arena.free(self.cap)
        self.highs.close()


class Odometer:
    def __init__(self, context):
        self.context = context
        self.digits = [[context.arena.zero() for _ in range(context.dimension)]
                       for _ in range(context.dimension)]
        self.finished = False

    def advance(self):
        need(not self.finished, "live high odometer")
        context = self.context
        for row in reversed(self.digits):
            for digit in reversed(row):
                context.raw.increment_in_place(digit)
                if context.raw.compare(digit, context.cap) < 0:
                    return
                need(context.raw.compare(digit, context.cap) == 0, "high digit carry")
                while digit.read() != RIGHT:
                    digit.write(ZERO)
                    digit.step(1)
                digit.rewind()
        self.finished = True

    def close(self):
        for row in self.digits:
            self.context.arena.free_many(*row)


def append_tape(source, destination):
    source.rewind()
    while source.read() != BLANK:
        destination.append(source.read())
        source.step(1)
    source.rewind()


def old_prefix(source, field_count, context):
    """Retain one serialized prefix; decode at most one old numerical word."""
    output, remaining = Tape(), Counter(field_count)
    try:
        while not remaining.finished:
            code = read_finite(source, context.codes.bits)
            need(code < context.codes.limit, "old compiled source code")
            append_finite(output, code, context.codes.bits)
            for _ in range(context.dimension*context.dimension):
                word = read_word(source, context.arena)
                try:
                    need(context.raw.compare(word, context.cap) < 0, "old high digit range")
                    append_word(output, word)
                finally:
                    context.arena.free(word)
            need(source.read() == RECORD_END, "old field boundary")
            source.step(1)
            output.append(RECORD_END)
            remaining.decrement()
        output.rewind()
        return output
    except ValueError:
        output.clear()
        raise
    finally:
        remaining.close()


def produce(old, old_fields, old_count, code, context):
    need(0 <= code < context.codes.limit, "new compiled source code")
    expected, emitted = Count(old_count), Count.literal(0)
    high_power(expected, context.ring, context.q, context.dimension)
    outer, output = Counter(old_count), Tape()
    old.rewind()
    try:
        need(not outer.finished, "nonempty old physical prefix domain")
        while not outer.finished:
            saved = old_prefix(old, old_fields, context)
            high = Odometer(context)
            try:
                while not high.finished:
                    append_tape(saved, output)
                    append_finite(output, code, context.codes.bits)
                    for row in high.digits:
                        for digit in row:
                            append_word(output, digit)
                    output.append(RECORD_END)
                    emitted.increment()
                    high.advance()
            finally:
                saved.clear()
                high.close()
            outer.decrement()
        need(old.read() == BLANK and emitted.equals(expected), "complete canonical raw directory")
        old.rewind()
        output.rewind()
        return output, expected
    except ValueError:
        output.clear()
        expected.close()
        old.rewind()
        raise
    finally:
        emitted.close()
        outer.close()
