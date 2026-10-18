"""Two-field padding adapter and a slow, completed binary reference callee.

New code: Apache-2.0. This is a stream-level reference implementation, not
the fast recursive supplier or a finite-alphabet transition-table compiler.
Only the binary callback is an abstract interface in the conditional proof.
The supplied callback actually executes digit bucket interchanges.
"""
from dataclasses import dataclass, field
from math import gcd, prod


class ContractError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise ContractError(message)


@dataclass
class Stream:
    data: list
    head: int = 0

    def read(self):
        need(self.head < len(self.data), "read past complete stream")
        value = self.data[self.head]
        self.head += 1
        return value

    def write(self, value):
        self.data.append(value)

    def close_input(self):
        need(self.head == len(self.data), "unconsumed input")
        self.data.clear()
        self.head = 0


@dataclass
class BinaryReturn:
    stream: Stream
    scratch_empty: bool = True
    parking_restored: bool = True


@dataclass
class Meter:
    calls: list = field(default_factory=list)
    digit_swaps: int = 0
    pad_reads: int = 0
    pad_writes: int = 0
    crop_reads: int = 0
    crop_writes: int = 0
    zero_width: int = 0


def copy(source, target, count):
    for _ in range(count):
        target.write(source.read())


def digit_exchange(source, before, middle, suffix, radix, meter):
    """Sequentially transpose two digit fields, leaving the gap in place."""
    need(source.head == 0, "digit entry origin")
    need(len(source.data) == before * radix**2 * middle * suffix,
         "complete digit extent")
    out = Stream([])
    for _ in range(before):
        buckets = [Stream([]) for _ in range(radix**2)]
        for x in range(radix):
            for _gap in range(middle):
                for y in range(radix):
                    copy(source, buckets[x * radix + y], suffix)
        for y in range(radix):
            for _gap in range(middle):
                for x in range(radix):
                    copy(buckets[x * radix + y], out, suffix)
        for bucket in buckets:
            bucket.close_input()
    source.close_input()
    meter.digit_swaps += 1
    return out


def binary_reference(source, bits, before, middle, suffix, meter):
    """A completed, slow binary callee; no direct address-permutation oracle."""
    need(bits >= 1, "positive binary width")
    need(len(source.data) == before * (1 << (2 * bits)) * middle * suffix,
         "complete binary rectangle")
    for position in range(bits):
        source = digit_exchange(
            source,
            before * (1 << position),
            (1 << (bits - 1)) * middle,
            suffix * (1 << (bits - position - 1)),
            2, meter,
        )
    return BinaryReturn(source)


def pad(source, radix, enlarged, before, middle, suffix, meter):
    need(source.head == 0, "padding entry origin")
    need(1 <= radix <= enlarged and min(before, middle, suffix) >= 1,
         "positive complete field extents")
    need(len(source.data) == before * radix**2 * middle * suffix,
         "complete genuine rectangle")
    out = Stream([])
    for _ in range(before):
        for x in range(enlarged):
            for _gap in range(middle):
                for y in range(enlarged):
                    for _ in range(suffix):
                        if x < radix and y < radix:
                            out.write(source.read())
                            meter.pad_reads += 1
                        else:
                            out.write(0)  # owned zero bits, also for an actual binary callee
                        meter.pad_writes += 1
    source.close_input()
    return out


def restrict(source, radix, enlarged, before, middle, suffix, meter):
    need(source.head == 0, "restriction entry origin")
    need(len(source.data) == before * enlarged**2 * middle * suffix,
         "complete returned binary rectangle")
    out = Stream([])
    for _ in range(before):
        for x in range(enlarged):
            for _gap in range(middle):
                for y in range(enlarged):
                    for _ in range(suffix):
                        value = source.read()
                        meter.crop_reads += 1
                        if x < radix and y < radix:
                            out.write(value)
                            meter.crop_writes += 1
                        else:
                            need(value == 0, "payload escaped genuine rectangle")
    source.close_input()
    return out


def qadic_exchange(source, q, width, before, middle, suffix, meter,
                   callee=binary_reference):
    """Replace a whole q-adic field swap by exactly one completed binary call.

    Prefix/gap/suffix cardinalities are passed through verbatim. The caller
    must supply a callee with the *swap* endpoint, not just a clean return.
    Runtime boundary checks cannot certify that semantic premise for it.
    """
    need(type(q) is int and q >= 2 and type(width) is int and width >= 0,
         "radix/width domain")
    radix = q**width
    need(all(type(x) is int and x >= 1 for x in (before, middle, suffix)) and source.head == 0 and
         len(source.data) == before * radix**2 * middle * suffix,
         "whole q-adic exchange domain")
    if width == 0:
        meter.zero_width += 1
        return source
    bits = (radix - 1).bit_length()
    enlarged = 1 << bits
    original_volume = len(source.data)
    source = pad(source, radix, enlarged, before, middle, suffix, meter)
    padded_volume = len(source.data)
    need(original_volume <= padded_volume < 4 * original_volume,
         "two-field volume bound")
    meter.calls.append({"q": q, "width": width, "binary_width": bits,
                        "before": before, "middle": middle, "suffix": suffix,
                        "volume": original_volume, "padded_volume": padded_volume})
    result = callee(source, bits, before, middle, suffix, meter)
    need(isinstance(result, BinaryReturn), "completed callee return type")
    need(result.scratch_empty and result.parking_restored, "callee cleanup/locality boundary")
    need(result.stream.head == 0, "callee return origin")
    return restrict(result.stream, radix, enlarged, before, middle, suffix, meter)


def field_exchange(source, radices, first, second, q, width, meter):
    need(0 <= first < second < len(radices), "ordered equal-width fields")
    need(radices[first] == radices[second] == q**width, "field radix binding")
    return qadic_exchange(source, q, width, prod(radices[:first]),
                          prod(radices[first + 1:second]), prod(radices[second + 1:]), meter)


def later_shift(source, radices, first, second, coefficient):
    """Sequential rotation of complete later-target fibres; source unchanged."""
    need(first < second and radices[first] == radices[second], "later shift fields")
    radix = radices[first]
    before, middle, suffix = (prod(radices[:first]), prod(radices[first + 1:second]),
                              prod(radices[second + 1:]))
    need(len(source.data) == prod(radices) and source.head == 0, "complete shift stream")
    out = Stream([])
    for prefix in range(before):
        for x in range(radix):
            c = coefficient(prefix) % radix
            for _gap in range(middle):
                left, right = Stream([]), Stream([])
                cut = (c * x) % radix
                copy(source, left, (radix - cut) * suffix)
                copy(source, right, cut * suffix)
                copy(right, out, cut * suffix)
                copy(left, out, (radix - cut) * suffix)
                left.close_input()
                right.close_input()
    source.close_input()
    return out


def sign(source, radices, axis):
    """Reverse the nonzero target blocks, retaining each block's internal order.

    Python lists model two sequential reversal scratch tapes here. This code
    makes no stronger physical cost claim than the inherited sign primitive.
    """
    radix, before, suffix = radices[axis], prod(radices[:axis]), prod(radices[axis + 1:])
    need(len(source.data) == prod(radices), "complete sign stream")
    out = Stream([])
    for _ in range(before):
        copy(source, out, suffix)
        blocks = []
        for _ in range(radix - 1):
            blocks.append([source.read() for _ in range(suffix)])
        for block in reversed(blocks):
            for value in block:
                out.write(value)
    source.close_input()
    return out


def weighted_leaf(raw, q, width, weights, gap=1, suffix=1, wrong_inverse=False,
                  omit_sign=False):
    """Successor of the PR2234 leaf schedule, using completed whole-field calls.

    weights[parent][i] is a unit independent of this node's changing fields.
    Arbitrary legal descriptors may provide these values; their realization
    and cost are separate premises, not inferred from this finite fixture.
    """
    need(bool(weights) and width >= 1, "nonempty ancestor domain")
    n = len(weights[0])
    radix = q**width
    need(0 <= n < 64 and all(len(row) == n for row in weights), "stopped leaf width")
    need(all(gcd(value, radix) == 1 for row in weights for value in row), "unit weights")
    radices = [len(weights)] + [radix] * n + [gap] + [radix] * n + [suffix]
    need(len(raw) == prod(radices), "complete leaf payload")
    source, meter = Stream(list(raw)), Meter()
    for i in range(n):
        first, second = 1 + i, 2 * n + 1 - i
        parent_divisor = prod(radices[1:first])
        def coefficient(prefix, inverse=False):
            a = weights[prefix // parent_divisor][i]
            return -pow(a, -1, radix) if inverse and not wrong_inverse else (-a if inverse else a)
        source = field_exchange(source, radices, first, second, q, width, meter)
        source = later_shift(source, radices, first, second, coefficient)
        source = field_exchange(source, radices, first, second, q, width, meter)
        source = later_shift(source, radices, first, second, lambda p: coefficient(p, True))
        source = field_exchange(source, radices, first, second, q, width, meter)
        source = later_shift(source, radices, first, second, coefficient)
        source = field_exchange(source, radices, first, second, q, width, meter)
        if not omit_sign:
            source = sign(source, radices, second)
    need(len(meter.calls) == 4 * n, "completed leaf call count")
    need(source.head == 0 and len(source.data) == len(raw), "leaf return boundary")
    return source.data, meter
