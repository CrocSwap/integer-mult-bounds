"""Gather/scatter one low class at its original positions in a complete family."""
from bitstream import copy_bits
from counts import Count, high_power
from records import Tape
from routes import copy_rows
from stream import Counter
from words import BLANK, ONE, ZERO, need


def discard_rows(source, count, fibre):
    rows = Counter(count)
    try:
        while not rows.finished:
            bits = Counter(fibre)
            while not bits.finished:
                need(source.read() in (ZERO, ONE), "complete skipped payload")
                source.step(1)
                bits.decrement()
            bits.close()
            rows.decrement()
    finally:
        rows.close()


def packet_operation(source, context, old_count, low, fibre, replacement=None, factory=Tape):
    # The ordinal and vocabulary cardinality belong to fixed-q compilation.
    ordinal = context.codes.rank(low)
    before = Count.literal(ordinal)
    after = Count.literal(context.codes.size-ordinal-1)
    high_power(before, context.ring, context.q, context.dimension)
    high_power(after, context.ring, context.q, context.dimension)
    outer, output = Counter(old_count), factory()
    source.rewind()
    if replacement is not None:
        replacement.rewind()
    try:
        need(not outer.finished, "positive physical old-prefix count")
        while not outer.finished:
            if replacement is None:
                discard_rows(source, before, fibre)
                copy_rows(source, output, context.highs, fibre)
                discard_rows(source, after, fibre)
            else:
                copy_rows(source, output, before, fibre)
                discard_rows(source, context.highs, fibre)
                copy_rows(replacement, output, context.highs, fibre)
                copy_rows(source, output, after, fibre)
            outer.decrement()
        need(source.read() == BLANK, "complete selected family")
        if replacement is not None:
            need(replacement.read() == BLANK, "complete packet replacement")
        output.rewind()
        return output
    except ValueError:
        output.clear()
        raise
    finally:
        before.close()
        after.close()
        outer.close()
        source.rewind()
        if replacement is not None:
            replacement.rewind()


def gather(source, context, old_count, low, fibre, factory=Tape):
    return packet_operation(source, context, old_count, low, fibre, factory=factory)


def scatter(source, replacement, context, old_count, low, fibre, factory=Tape):
    return packet_operation(source, context, old_count, low, fibre, replacement, factory)
