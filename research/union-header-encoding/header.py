"""One-microbox header reference codec, not a fixed-tape implementation.

Mihir Srivastava with substantial OpenAI Codex assistance. Apache-2.0.
"""
from bisect import bisect_left
from dataclasses import dataclass


def require(ok, message):
    if not ok:
        raise ValueError(message)


def bits(value, width):
    require(type(value) is int and 0 <= value < 1 << width, "field overflow")
    return format(value, f"0{width}b")


@dataclass(frozen=True)
class Header:
    coordinates: tuple
    flags: tuple
    ordinals: tuple
    count: int
    tag: int


class Layout:
    """L, g, and E_i are shared context. Finite E_i lists are test oracles.

    The all-size statement retains the source's carving/rank producer;
    these explicit lists are not proposed large-core tables.
    """
    def __init__(self, side, boundaries):
        require(type(side) is int and side >= 2, "side must be at least two")
        self.side = side
        self.boundaries = tuple(tuple(e) for e in boundaries)
        self.g = len(self.boundaries)
        require(self.g > 0, "empty axis group")
        for e in self.boundaries:
            require(all(type(x) is int and 0 <= x < side for x in e), "bad boundary coordinate")
            require(e == tuple(sorted(set(e))), "boundary must be strictly sorted")
        self.h = (side - 1).bit_length()
        self.b = self.g.bit_length()  # ceil(log2(g+1)), including sentinel g
        self.width = 2 + 2*self.g*self.h + self.g + 2*self.b
        self.offsets = {"coordinates": 2, "flags": 2+self.g*self.h,
                        "ordinals": 2+self.g*self.h+self.g,
                        "count": 2+2*self.g*self.h+self.g,
                        "tag": 2+2*self.g*self.h+self.g+self.b}

    def expected(self, coordinates, tag=None):
        x = tuple(coordinates)
        require(len(x) == self.g, "wrong coordinate count")
        flags, ordinals = [], []
        for value, e in zip(x, self.boundaries):
            require(type(value) is int and 0 <= value < self.side, "coordinate out of range")
            rank = bisect_left(e, value)
            member = rank < len(e) and e[rank] == value
            flags.append(int(member))
            ordinals.append(rank if member else 0)
        tag = self.g if tag is None else tag
        require(type(tag) is int and 0 <= tag <= self.g, "tag out of range")
        require(tag == self.g or flags[tag] == 1, "tag is not a flagged axis")
        return Header(x, tuple(flags), tuple(ordinals), sum(flags), tag)

    def encode(self, coordinates, tag=None):
        record = self.expected(coordinates, tag)
        return ("01" + "".join(bits(x, self.h) for x in record.coordinates)
                + "".join(str(f) for f in record.flags)
                + "".join(bits(o, self.h) for o in record.ordinals)
                + bits(record.count, self.b) + bits(record.tag, self.b))

    def decode(self, encoded, round_index=None):
        require(isinstance(encoded, str) and len(encoded) == self.width, "wrong header length")
        require(set(encoded) <= {"0", "1"} and encoded[:2] == "01", "bad record framing")
        pos = 2
        def take(width):
            nonlocal pos
            value = int(encoded[pos:pos+width], 2)
            pos += width
            return value
        x = tuple(take(self.h) for _ in range(self.g))
        flags = tuple(take(1) for _ in range(self.g))
        ordinals = tuple(take(self.h) for _ in range(self.g))
        record = Header(x, flags, ordinals, take(self.b), take(self.b))
        require(record == self.expected(x, record.tag), "inconsistent header metadata")
        if round_index is not None:
            require(record.tag == self.axis(record, round_index), "tag does not match this round")
        return record

    @staticmethod
    def axis(record, round_index):
        require(type(round_index) is int and 0 <= round_index < record.count, "inactive round")
        remaining = round_index
        for i, flag in enumerate(record.flags):
            if flag:
                if remaining == 0:
                    return i
                remaining -= 1
        raise ValueError("inconsistent flag count")

    def retag(self, encoded, round_index):
        record = self.decode(encoded)
        tag = self.axis(record, round_index)
        return encoded[:self.offsets["tag"]] + bits(tag, self.b)

    def line_key(self, encoded, round_index):
        record = self.decode(encoded, round_index)
        f = record.tag
        return record.coordinates[:f], record.ordinals[f]
