"""Sequential opaque-record tapes with explicit bit-volume charges.

Every payload record has32 bits. Block copies stand for sequential binary
copies, not unit-cost bulk movement. Routing never inspects record values.
"""
from array import array
from collections import Counter
from dataclasses import dataclass
from math import prod

from algebra import need


class RecordMeter(Counter):
    def __init__(self):
        super().__init__()
        self.copied = 0
        self.extra_moves = 0
        self.erased = 0

    def summary(self):
        return {**dict(self), "read_bits": 32 * self.copied,
                "write_bits": 32 * self.copied,
                "head_bits": 32 * (2 * self.copied + self.extra_moves),
                "erased_bits": 32 * self.erased}


class Tape:
    def __init__(self, meter, records=()):
        self.meter, self.records, self.head = meter, array("I", records), 0

    def rewind(self):
        self.meter.extra_moves += self.head
        self.head = 0

    def skip(self, count):
        need(0 <= count <= len(self.records) - self.head, "sequential skip extent")
        self.meter.extra_moves += count
        self.head += count

    def erase(self):
        self.rewind()
        self.meter.erased += len(self.records)
        self.meter.extra_moves += 2 * len(self.records)
        self.records = array("I")
        self.head = 0

    def finished(self):
        need(self.head == len(self.records), "complete tape consumption")


def copy(source, destination, count):
    need(destination.head == len(destination.records) and 0 <= count <= len(source.records) - source.head,
         "sequential block-copy boundary")
    destination.records.extend(source.records[source.head:source.head + count])
    source.head += count
    destination.head += count
    source.meter.copied += count


def blocks(source, destination, count, size):
    # A macro for the same adjacent block copies; every copied bit is charged.
    # Its tape lowering uses a block counter and a local suffix counter.
    copy(source, destination, count * size)


@dataclass(frozen=True)
class Shape:
    atoms: int
    modulus: int
    unused: int = 1
    gap: int = 1
    suffix: int = 1

    def __post_init__(self):
        need(self.atoms >= 1 and self.modulus >= 3 and
             min(self.unused, self.gap, self.suffix) >= 1, "positive complete shape")

    @property
    def radices(self): return (self.modulus,) * self.atoms + (self.gap,) + (self.modulus,) * self.atoms
    @property
    def records(self): return self.unused * prod(self.radices) * self.suffix
    def axis(self, atom): return atom + int(atom >= self.atoms)

    def child(self, first, second, width):
        a, b, radices = self.axis(first), self.axis(second), self.radices
        need(0 <= first and 0 < width and first + width <= second and second + width <= 2 * self.atoms,
             "ordered embedded child blocks")
        need(not (first < self.atoms < first + width) and not (second < self.atoms < second + width),
             "child chunks do not cross the old gap")
        out = Shape(width, self.modulus, self.unused * prod(radices[:a]),
                    prod(radices[a + width:b]), self.suffix * prod(radices[b + width:]))
        need(out.records == self.records, "descriptor-only child volume equality")
        return out


def add_pass(source, shape, contexts, first, second, coefficient):
    a, b, radices = shape.axis(first), shape.axis(second), shape.radices
    need(a < b, "later-target ADD")
    before, middle = shape.unused * prod(radices[:a]), prod(radices[a + 1:b])
    suffix, B = shape.suffix * prod(radices[b + 1:]), shape.modulus
    need(len(source.records) == len(contexts) * shape.records, "complete controlled packet")
    left, right, out = Tape(source.meter), Tape(source.meter), Tape(source.meter)
    source.rewind()
    for context in contexts:
        c = coefficient(context) % B
        for _ in range(before):
            for x in range(B):
                cut = c * x % B
                for _ in range(middle):
                    blocks(source, left, B - cut, suffix)
                    blocks(source, right, cut, suffix)
    source.finished()
    left.rewind(); right.rewind()
    for context in contexts:
        c = coefficient(context) % B
        for _ in range(before):
            for x in range(B):
                cut = c * x % B
                for _ in range(middle):
                    blocks(right, out, cut, suffix)
                    blocks(left, out, B - cut, suffix)
    left.finished(); right.finished()
    left.erase(); right.erase(); source.erase(); out.rewind()
    source.meter["ordered_add_passes"] += 1
    return out


def digit_swap(source, shape, first, second, q, width, digit):
    n = shape.atoms
    radices = (q,) * (n * width) + (shape.gap,) + (q,) * (n * width)
    a = first * width + digit + int(first >= n)
    b = second * width + digit + int(second >= n)
    middle, suffix = prod(radices[a + 1:b]), shape.suffix * prod(radices[b + 1:])
    slab = q * q * middle * suffix
    need(a < b and len(source.records) % slab == 0, "complete digit-swap slabs")
    buckets = [Tape(source.meter) for _ in range(q * q)]
    out = Tape(source.meter)
    source.rewind()
    for _ in range(len(source.records) // slab):
        for x in range(q):
            for _ in range(middle):
                for y in range(q):
                    copy(source, buckets[x * q + y], suffix)
        for bucket in buckets: bucket.rewind()
        for y in range(q):
            for _ in range(middle):
                for x in range(q):
                    copy(buckets[x * q + y], out, suffix)
        for bucket in buckets:
            bucket.finished(); bucket.erase()
    source.finished(); source.erase(); out.rewind()
    source.meter["digit_swaps"] += 1
    return out


def ordinary_swap(source, shape, first, second, q, width):
    need(shape.modulus == q**width, "atom digit format")
    for digit in range(width):
        source = digit_swap(source, shape, first, second, q, width, digit)
    return source


def sign_pass(source, shape, atom):
    axis = shape.axis(atom)
    suffix = shape.suffix * prod(shape.radices[axis + 1:])
    B = shape.modulus
    need(len(source.records) % (B * suffix) == 0, "complete sign slabs")
    out, reverse = Tape(source.meter), Tape(source.meter)
    source.rewind()
    for _ in range(len(source.records) // (B * suffix)):
        copy(source, out, suffix)
        blocks(source, reverse, B - 1, suffix)
        for _ in range(B - 1):
            # Seek back one whole block, copy it forward, erase it, return.
            reverse.head -= suffix
            reverse.meter.extra_moves += suffix
            copy(reverse, out, suffix)
            reverse.meter.extra_moves += 2 * suffix
            reverse.meter.erased += suffix
            del reverse.records[-suffix:]
            reverse.head -= suffix
        need(not reverse.records and reverse.head == 0, "sign scratch closure")
    source.finished(); source.erase(); out.rewind()
    source.meter["sign_passes"] += 1
    return out
