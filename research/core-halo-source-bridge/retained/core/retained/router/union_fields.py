"""Short tape fields and raw long-prefix comparisons.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from cardinal_counts import Count
from compact_counts import copy_bits
from encoded import compare, subtract
from router_metadata import indices, owned, ceiling_log
from words import BLANK, need
from union_bits import bit, big, put_big, move, skip_bits


class Geometry:
    def __init__(self, axes, h, tag_bits, width):
        self.axes, self.h, self.tag_bits, self.width = axes, h, tag_bits, width
        self.coordinates = Count.product(axes, h)
        self.flags_at = Count(self.coordinates)
        self.flags_at.increment(); self.flags_at.increment()
        self.ordinals_at = Count(self.flags_at); self.ordinals_at.add(axes)
        self.count_at = Count(self.ordinals_at); self.count_at.add(self.coordinates)
        self.tag_at = Count(self.count_at); self.tag_at.add(tag_bits)
        self.header = Count(self.tag_at); self.header.add(tag_bits)
        self.payload = Count(width); self.payload.multiply_small(2)
        self.record = Count(self.header); self.record.add(self.payload)
        self.key_gap = Count(self.coordinates); self.key_gap.add(axes)

    def close(self):
        for value in (self.coordinates, self.flags_at, self.ordinals_at,
                      self.count_at, self.tag_at, self.header, self.payload,
                      self.record, self.key_gap):
            value.close()

    def field(self, source, offset, width):
        skip_bits(source, offset)
        result = big(source, width)
        with owned(Count(offset)) as (distance,):
            distance.add(width)
            move(source, distance, -1)
        return result

    def tag(self, source):
        return self.field(source, self.tag_at, self.tag_bits)

    def count(self, source):
        return self.field(source, self.count_at, self.tag_bits)

    def radix_bit(self, source, position):
        with owned(Count(self.tag_bits), Count.literal(1)) as (extent, one):
            with owned(subtract(extent, one)) as (last,):
                with owned(subtract(last, position), Count(self.tag_at)) as (reverse, offset):
                    offset.add(reverse)
                    skip_bits(source, offset)
                    value = bit(source)
                    offset.increment()
                    move(source, offset, -1)
                    return value

    def retag(self, source, target, round_index):
        copy_bits(source, target, self.flags_at)
        tag = Count.literal(0)
        found = False
        try:
            with owned(Count.literal(0)) as (seen,):
                for axis in indices(self.axes):
                    flag = bit(source, target)
                    if flag:
                        if compare(seen, round_index) == 0:
                            tag.close(); tag = Count(axis); found = True
                        seen.increment()
                need(found, 'round visits a live flagged record')
                copy_bits(source, target, self.coordinates)
                with owned(big(source, self.tag_bits, target)) as (count,):
                    need(compare(count, seen) == 0, 'stored count equals emitted flags')
                skip_bits(source, self.tag_bits)
                put_big(tag, target, self.tag_bits)
                copy_bits(source, target, self.payload)
        finally:
            tag.close()

    def key(self, source, prefix_bits, saved=None, equal=None):
        """Return active ordinal and a finite equality flag; restore local head."""
        need(bit(source) == 0 and bit(source) == 1, 'union record marker')
        same = True
        if equal is not None:
            equal.rewind()
        for _ in indices(prefix_bits):
            digit = bit(source)
            if saved is not None:
                saved.append(digit)
            if equal is not None:
                same = (bit(equal) == digit) and same
        if equal is not None:
            need(equal.read() == BLANK, 'complete raw prefix comparison')
            equal.rewind()
        skip_bits(source, self.key_gap)
        ordinal = big(source, self.h)
        with owned(Count(prefix_bits)) as (distance,):
            distance.add(self.key_gap); distance.add(self.h)
            distance.increment(); distance.increment()
            move(source, distance, -1)
        return ordinal, same


def unit(ordinal, length, level):
    """Balanced #4327 row-range tree, computed from O(log L)-bit descriptors."""
    lo, size = Count.literal(0), Count(length)
    try:
        need(compare(ordinal, length) < 0, 'active ordinal in source E')
        while True:
            with owned(ceiling_log(size)) as (height,):
                order = compare(height, level)
            if order <= 0:
                half = Count(size)
                half.divide_small(2)
                if order < 0:
                    return lo, size, half, 0
                with owned(Count(lo)) as (cut,):
                    cut.add(half)
                    role = 1 if compare(ordinal, cut) < 0 else 2
                return lo, size, half, role
            with owned(Count(size), Count(lo)) as (half, cut):
                half.divide_small(2); cut.add(half)
                if compare(ordinal, cut) < 0:
                    size.close(); size = Count(half)
                else:
                    following = subtract(size, half)
                    size.close(); size = following
                    lo.close(); lo = Count(cut)
    except BaseException:
        lo.close(); size.close()
        raise
