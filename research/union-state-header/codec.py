"""Exact joint headers, produced by Nick Petalas. Apache-2.0.

This is an information codec, not a fixed-tape implementation.
"""

from bisect import bisect_left
from dataclasses import dataclass


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Header:
    coordinates: tuple
    flags: tuple
    ordinals: tuple
    count: int
    tag: int


class Layout:
    """At most 32 axes, 4096 side bits and 128 boundary entries per axis."""

    def __init__(self, side, boundaries):
        require(type(side) is int and 2 <= side <= 1 << 4096, "side domain")
        require(type(boundaries) in (tuple, list), "boundary container")
        require(1 <= len(boundaries) <= 32, "axis capacity")
        for boundary in boundaries:
            require(type(boundary) in (tuple, list), "boundary container")
            require(len(boundary) <= 128, "boundary capacity")
            require(all(type(v) is int and 0 <= v < side for v in boundary),
                    "boundary coordinate")
            require(tuple(boundary) == tuple(sorted(set(boundary))),
                    "boundary ordering")
        self.side = side
        self.boundaries = tuple(tuple(e) for e in boundaries)
        self.g = len(self.boundaries)
        self.plane = side ** (self.g - 1)
        self.sentinel_size = side * self.plane
        self.states = self.plane * (side + sum(map(len, self.boundaries)))
        self.index_bits = (self.states - 1).bit_length()
        self.width = self.index_bits + 2

    def describe(self, coordinates, tag=None):
        require(type(coordinates) in (tuple, list), "coordinate container")
        require(len(coordinates) == self.g, "coordinate count")
        require(all(type(v) is int and 0 <= v < self.side for v in coordinates),
                "coordinate domain")
        tag = self.g if tag is None else tag
        require(type(tag) is int and 0 <= tag <= self.g, "tag domain")
        flags, ordinals = [], []
        for value, boundary in zip(coordinates, self.boundaries):
            rank = bisect_left(boundary, value)
            member = rank < len(boundary) and boundary[rank] == value
            flags.append(int(member))
            ordinals.append(rank if member else 0)
        require(tag == self.g or flags[tag] == 1, "unflagged tag")
        return Header(tuple(coordinates), tuple(flags), tuple(ordinals),
                      sum(flags), tag)

    def rank(self, coordinates, tag=None):
        record = self.describe(coordinates, tag)
        value = 0
        for axis, coordinate in enumerate(record.coordinates):
            radix = self.side
            if axis == record.tag:
                radix = len(self.boundaries[axis])
                coordinate = record.ordinals[axis]
            value = value * radix + coordinate
        if record.tag < self.g:
            before = sum(len(e) for e in self.boundaries[:record.tag])
            value += self.sentinel_size + before * self.plane
        require(0 <= value < self.states, "internal rank range")
        return value

    def unrank(self, value):
        require(type(value) is int and 0 <= value < self.states, "index domain")
        tag = self.g
        if value >= self.sentinel_size:
            value -= self.sentinel_size
            for axis, boundary in enumerate(self.boundaries):
                size = len(boundary) * self.plane
                if value < size:
                    tag = axis
                    break
                value -= size
            require(tag < self.g, "internal block selection")
        coordinates = [0] * self.g
        for axis in range(self.g - 1, -1, -1):
            radix = len(self.boundaries[axis]) if axis == tag else self.side
            value, digit = divmod(value, radix)
            coordinates[axis] = self.boundaries[axis][digit] if axis == tag else digit
        require(value == 0, "internal mixed-radix remainder")
        return self.describe(coordinates, tag)

    def encode(self, coordinates, tag=None):
        value = self.rank(coordinates, tag)
        return "01" + format(value, f"0{self.index_bits}b")

    def decode(self, encoded):
        require(type(encoded) is str and len(encoded) == self.width, "header length")
        require(set(encoded) <= {"0", "1"} and encoded[:2] == "01", "header marker")
        return self.unrank(int(encoded[2:], 2))

    def retag(self, encoded, round_index):
        record = self.decode(encoded)
        require(type(round_index) is int and 0 <= round_index < record.count,
                "inactive round")
        axes = tuple(axis for axis, flag in enumerate(record.flags) if flag)
        return self.encode(record.coordinates, axes[round_index])

    def line_key(self, encoded, round_index):
        updated = self.retag(encoded, round_index)
        record = self.decode(updated)
        require(record.tag == self.decode(encoded).tag, "wrong round tag")
        return record.coordinates[:record.tag], record.ordinals[record.tag]
