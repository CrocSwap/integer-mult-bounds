"""Swap two radix-q atoms with four sequential buckets and encoded extents."""
from bitstream import copy_bits
from cardinality import Natural, digit_suffix, radix_power
from stream import Counter, positive_extent
from words import BLANK, ZERO, need


def counted(extent):
    counter = Counter(extent)
    try:
        while not counter.finished:
            yield
            counter.decrement()
    finally:
        counter.close()


def records(before, middle, side):
    for _ in counted(before):
        for a in range(side):
            for _ in counted(middle):
                for b in range(side):
                    yield a, b


def digit_swap(source, q, before, middle, suffix, factory):
    """Pad one digit pair, exchange matching binary positions, then strip the padding."""
    bits = (q - 1).bit_length()
    side = 1 << bits
    current = factory()
    for a, b in records(before, middle, side):
        if a < q and b < q:
            copy_bits(source, current, suffix)
        else:
            for _ in counted(suffix):
                current.append(ZERO)
    need(source.read() == BLANK, "complete radix input")
    source.rewind()
    current.rewind()
    for j in range(bits):
        buckets = [factory() for _ in range(4)]
        for a, b in records(before, middle, side):
            index = 2 * ((a >> j) & 1) + ((b >> j) & 1)
            copy_bits(current, buckets[index], suffix)
        need(current.read() == BLANK, "complete padded input")
        current.clear()
        for tape in buckets:
            tape.rewind()
        current = factory()
        for a, b in records(before, middle, side):
            index = 2 * ((b >> j) & 1) + ((a >> j) & 1)
            copy_bits(buckets[index], current, suffix)
        for tape in buckets:
            need(tape.read() == BLANK, "complete binary digit bucket")
            tape.clear()
        current.rewind()
    result = factory()
    for a, b in records(before, middle, side):
        if a < q and b < q:
            copy_bits(current, result, suffix)
        else:
            for _ in counted(suffix):
                need(current.read() == ZERO, "zero transposed radix padding")
                current.step(1)
    need(current.read() == BLANK, "complete padded result")
    current.clear()
    result.rewind()
    return result


def atom_swap(source, ring, q, before, middle, suffix, factory):
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
            following = digit_swap(current, q, pre, gap, tail, factory)
            if current is not source:
                current.clear()
            current, first = following, False
        return current
    finally:
        pre.close()
        gap.close()
        tail.close()
