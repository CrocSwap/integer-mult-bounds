"""Complete atom swaps and address signs, using fixed-radix digit passes."""
from cardinality import Natural, digit_suffix, radix_power
from records import Tape
from stream import Counter, copy_blocks, one_bit_suffix, positive_extent
from words import BLANK, ONE, ZERO, need


def unobserved(_counter):
    pass


def copy_bits(source, target, length):
    if one_bit_suffix(length):
        bit = source.read()
        need(bit in (ZERO, ONE), "opaque single payload bit")
        target.append(bit)
        source.step(1)
        return
    count = Counter(length)
    while not count.finished:
        bit = source.read()
        need(bit in (ZERO, ONE), "opaque stream bit")
        target.append(bit)
        source.step(1)
        count.decrement()
    count.close()


def digit_swap(source, q, before, middle, suffix):
    buckets = [[Tape() for _ in range(q)] for _ in range(q)]
    outer = Counter(before)
    while not outer.finished:
        for a in range(q):
            between = Counter(middle)
            while not between.finished:
                for b in range(q):
                    copy_bits(source, buckets[a][b], suffix)
                between.decrement()
            between.close()
        outer.decrement()
    outer.close()
    need(source.read() == BLANK, "complete digit-swap input")
    source.rewind()
    for row in buckets:
        for tape in row:
            tape.rewind()
    out, outer = Tape(), Counter(before)
    while not outer.finished:
        for a in range(q):
            between = Counter(middle)
            while not between.finished:
                for b in range(q):
                    copy_bits(buckets[b][a], out, suffix)
                between.decrement()
            between.close()
        outer.decrement()
    outer.close()
    for row in buckets:
        for tape in row:
            need(tape.read() == BLANK, "complete transposed digit bucket")
            tape.clear()
    out.rewind()
    return out


def digit_complement(source, q, before, suffix):
    buckets, outer = [Tape() for _ in range(q)], Counter(before)
    while not outer.finished:
        for digit in range(q):
            copy_bits(source, buckets[digit], suffix)
        outer.decrement()
    outer.close()
    need(source.read() == BLANK, "complete digit-complement input")
    source.rewind()
    for tape in buckets:
        tape.rewind()
    out, outer = Tape(), Counter(before)
    while not outer.finished:
        for digit in range(q):
            copy_bits(buckets[q-1-digit], out, suffix)
        outer.decrement()
    outer.close()
    for tape in buckets:
        need(tape.read() == BLANK, "complete complemented digit bucket")
        tape.clear()
    out.rewind()
    return out


def atom_swap(source, ring, q, before, middle, suffix):
    for value in (before, middle, suffix):
        positive_extent(value)
    pre, gap, tail = Natural(before), Natural(middle), Natural(suffix)
    digit_suffix(gap, ring, q)
    digit_suffix(tail, ring, q)
    current, first = source, True
    try:
        for _ in radix_power(ring, q):
            if not first:
                pre.multiply_small(q)
                need(tail.divide_small(q) == 0, "exact next digit suffix")
            following = digit_swap(current, q, pre, gap, tail)
            if current is not source:
                current.clear()
            current, first = following, False
        return current
    finally:
        pre.close()
        gap.close()
        tail.close()


def translate_one(source, ring, before, suffix):
    leading = ring.raw.subtract_exact(ring.modulus, ring.one)
    left, right, output = Tape(), Tape(), Tape()
    outer = Counter(before)
    while not outer.finished:
        copy_blocks(source, left, leading, suffix, unobserved)
        copy_blocks(source, right, ring.one, suffix, unobserved)
        outer.decrement()
    outer.close()
    need(source.read() == BLANK, "complete translation input")
    source.rewind()
    left.rewind()
    right.rewind()
    outer = Counter(before)
    while not outer.finished:
        copy_blocks(right, output, ring.one, suffix, unobserved)
        copy_blocks(left, output, leading, suffix, unobserved)
        outer.decrement()
    outer.close()
    need(left.read() == right.read() == BLANK, "complete translation buckets")
    left.clear()
    right.clear()
    ring.arena.free(leading)
    output.rewind()
    return output


def sign_address(source, ring, q, before, suffix):
    for value in (before, suffix):
        positive_extent(value)
    pre, tail = Natural(before), Natural(suffix)
    digit_suffix(tail, ring, q)
    current, first = source, True
    try:
        for _ in radix_power(ring, q):
            if not first:
                pre.multiply_small(q)
                need(tail.divide_small(q) == 0, "exact complemented suffix")
            following = digit_complement(current, q, pre, tail)
            if current is not source:
                current.clear()
            current, first = following, False
        result = translate_one(current, ring, before, suffix)
        current.clear()
        return result
    finally:
        pre.close()
        tail.close()
