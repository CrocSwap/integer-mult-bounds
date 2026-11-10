"""New finite scanner for the source q^2-bucket elementary digit swap.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is corroboration of the source algorithm, not the production multiplier.
Shape arithmetic is observer/driver code; its physical cost is not measured.
"""
from dataclasses import dataclass, field


def require(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass
class Tape:
    cells: dict = field(default_factory=dict)
    visited: set = field(default_factory=lambda: {0})
    head: int = 0
    reads: int = 0
    writes: int = 0
    moves: int = 0

    def seek(self, target):
        require(target >= 0, "one-sided tape")
        while self.head != target:
            self.head += 1 if target > self.head else -1
            self.visited.add(self.head)
            self.moves += 1

    def read(self):
        self.visited.add(self.head)
        self.reads += 1
        return self.cells.get(self.head)

    def write(self, bit):
        require(bit in (None, 0, 1), "finite alphabet")
        self.visited.add(self.head)
        self.writes += 1
        if bit is None:
            self.cells.pop(self.head, None)
        else:
            self.cells[self.head] = bit

    def erase(self, origin, extent):
        self.seek(origin)
        for _ in range(extent):
            self.write(None)
            self.seek(self.head + 1)
        self.seek(origin)


class Buckets:
    def __init__(self, q):
        require(q >= 2, "fixed radix")
        self.q = q
        self.tapes = [Tape() for _ in range(q*q+2)]
        self.active = 0
        self.volume = 0
        self.origin = 0

    def load(self, bits, origin=0):
        require(all(not t.cells for t in self.tapes[2:]), "bucket closure")
        for t in self.tapes[:2]:
            t.erase(self.origin, self.volume)
        self.origin, self.volume = origin, len(bits)
        self.active = 0
        for t in self.tapes:
            t.seek(origin)
        for b in bits:
            self.tapes[0].write(b)
            self.tapes[0].seek(self.tapes[0].head+1)
        self.tapes[0].seek(origin)

    def exchange(self, e, digit, prefix=1, gap=1, suffix=1, wrong_order=False):
        q, origin = self.q, self.origin
        side = q**e
        require(e >= 1 and 0 <= digit < e, "digit domain")
        require(prefix*gap*suffix*side*side == self.volume, "complete rectangle")
        src, dst = self.tapes[self.active], self.tapes[1-self.active]
        require(not dst.cells, "empty output")
        bins = self.tapes[2:]
        lengths = [0]*(q*q)
        src.seek(origin)
        for index in range(self.volume):
            d = (index//suffix) % side
            h = (index//(suffix*side*gap)) % side
            key = ((h//q**digit)%q)*q + (d//q**digit)%q
            b = bins[key]
            b.write(src.read())
            b.seek(b.head+1)
            src.seek(src.head+1)
            lengths[key] += 1
        for b in bins:
            b.seek(origin)
        dst.seek(origin)
        for index in range(self.volume):
            d = (index//suffix) % side
            h = (index//(suffix*side*gap)) % side
            a, b = (h//q**digit)%q, (d//q**digit)%q
            key = a*q+b if wrong_order else b*q+a
            require(bins[key].read() is not None, "complete bucket read")
            dst.write(bins[key].read())
            dst.seek(dst.head+1)
            bins[key].seek(bins[key].head+1)
        src.erase(origin, self.volume)
        for b, length in zip(bins, lengths):
            b.erase(origin, length)
        dst.seek(origin)
        self.active = 1-self.active
        require(all(t.head == origin for t in self.tapes), "returned heads")
        require(all(not t.cells for t in self.tapes[2:]), "erased buckets")
        return lengths

    def values(self):
        """Read-only observer, excluded from movement counts."""
        t = self.tapes[self.active]
        return [t.cells.get(self.origin+i) for i in range(self.volume)]

    def backing(self):
        return sum(len(t.visited) for t in self.tapes)

    def live(self):
        return sum(len(t.cells) for t in self.tapes)


def reference(bits, q, e, prefix, gap, suffix, digit=None):
    """Independent tuple-coordinate forward action, no bucket code."""
    side = q**e
    out = [None]*len(bits)
    index = 0
    for p in range(prefix):
        for h in range(side):
            for g in range(gap):
                for d in range(side):
                    for z in range(suffix):
                        if digit is None:
                            hh, dd = d, h
                        else:
                            power = q**digit
                            a, b = (h//power)%q, (d//power)%q
                            hh, dd = h+(b-a)*power, d+(a-b)*power
                        target = ((((p*side+hh)*gap+g)*side+dd)*suffix+z)
                        out[target] = bits[index]
                        index += 1
    return out
