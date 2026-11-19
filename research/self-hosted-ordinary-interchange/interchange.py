"""Reference dispatcher for the ordinary ports of a stopped interchange word."""

from collections.abc import Callable, Generator, Iterator, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Port:
    q: int
    width: int
    prefix: int
    gap: int
    suffix: int

    def __post_init__(self):
        if self.q < 2 or self.width < 0 or min(self.spectators) < 1:
            raise ValueError("invalid complete field shape")

    @property
    def spectators(self):
        return self.prefix, self.gap, self.suffix

    @property
    def side(self):
        return self.q**self.width

    @property
    def volume(self):
        return self.prefix * self.gap * self.suffix * self.side**2

    def digit_pair(self, left, right):
        """Select two positions, indexed from the most significant digit."""
        if not (0 <= left < self.width and 0 <= right < self.width):
            raise ValueError("digit position outside the field")
        return Port(self.q, 1, self.prefix * self.q**left,
                    self.gap * self.q**(self.width - left - 1 + right),
                    self.suffix * self.q**(self.width - right - 1))


def swap_digits(port, source):
    """Split into q squared streams and read them in swapped address order."""
    if port.width != 1:
        raise ValueError("elementary swap requires one digit")
    q = port.q
    output = []
    read = iter(source)
    for _ in range(port.prefix):
        banks = [[] for _ in range(q*q)]
        for left in range(q):
            for _ in range(port.gap):
                for right in range(q):
                    bank = banks[left*q + right]
                    for _ in range(port.suffix):
                        bank.append(next(read))
        streams = [iter(bank) for bank in banks]
        for right in range(q):
            for _ in range(port.gap):
                for left in range(q):
                    bank = streams[left*q + right]
                    for _ in range(port.suffix):
                        output.append(next(bank))
    return output


def elementary(port, source):
    result = list(source)
    for index in range(port.width):
        result = swap_digits(port.digit_pair(index, index), result)
    return result


@dataclass(frozen=True)
class Request:
    port: Port
    source: Sequence


class Slabs:
    """Stable scan of contiguous intervals in one complete spectator."""

    def __init__(self, port, fanout):
        sizes = port.spectators
        self.axis = max(range(3), key=sizes.__getitem__)
        length = sizes[self.axis]
        count = min(length, fanout)
        quotient, extra = divmod(length, count)
        self.widths = [quotient + (i < extra) for i in range(count)]
        self.ports = []
        for width in self.widths:
            piece = list(sizes)
            piece[self.axis] = width
            self.ports.append(Port(port.q, port.width, *piece))
        dims = (port.prefix, port.side, port.gap, port.side, port.suffix)
        axis = 2*self.axis
        self.outer = 1
        self.inner = 1
        for dim in dims[:axis]:
            self.outer *= dim
        for dim in dims[axis+1:]:
            self.inner *= dim

    def runs(self) -> Iterator[tuple[int, int]]:
        for _ in range(self.outer):
            for index, width in enumerate(self.widths):
                yield index, width * self.inner

    def split(self, source):
        banks = [[] for _ in self.widths]
        read = iter(source)
        for index, count in self.runs():
            bank = banks[index]
            for _ in range(count):
                bank.append(next(read))
        return banks

    def merge(self, banks):
        result = []
        readers = [iter(bank) for bank in banks]
        for index, count in self.runs():
            read = readers[index]
            for _ in range(count):
                result.append(next(read))
        return result


OpenWord = Callable[[Port, Sequence], Generator[Request, list, list]]


def atom_width(e, numerator, denominator):
    """Return the least integer w with w^denominator >= e^numerator."""
    if e < 1 or not 0 < numerator < denominator:
        raise ValueError("invalid atom rule")
    target = e**numerator
    low, high = 0, e
    while high-low > 1:
        mid = (low+high)//2
        if mid**denominator < target:
            low = mid
        else:
            high = mid
    return high


def block_word(numerator, denominator) -> OpenWord:
    """Build a cover-free entry that swaps disjoint consecutive digit blocks."""
    def word(port, data):
        width = atom_width(port.width, numerator, denominator)
        if width == port.width:
            return elementary(port, data)
        for start in range(0, port.width, width):
            length = min(width, port.width-start)
            part = Port(port.q, length, port.prefix*port.q**start,
                        port.gap*port.q**(port.width-length),
                        port.suffix*port.q**(port.width-start-length))
            data = yield Request(part, data)
        return data
    return word


def close_cycle(words: Sequence[OpenWord], entry, port, source, *, cutoff, fanout, observe=None):
    """Start one wrapper. Each open ordinary request enters the next wrapper."""
    if not 0 <= entry < len(words):
        raise ValueError("unknown cycle entry")
    if cutoff < 1 or fanout < 2:
        raise ValueError("invalid closure parameters")
    if len(source) != port.volume:
        raise ValueError("incomplete entry stream")

    def run(tag, current, data, depth):
        if observe is not None:
            observe(tag, current, depth)
        if current.width <= cutoff:
            return elementary(current, data)
        program = words[tag](current, data)
        response = None
        while True:
            try:
                request = program.send(response)
            except StopIteration as end:
                if len(end.value) != current.volume:
                    raise ValueError("incomplete ordinary return")
                return end.value
            child = request.port
            if child.q != current.q or child.width >= current.width:
                raise ValueError("ordinary width must decrease in the same radix")
            if len(request.source) != child.volume:
                raise ValueError("incomplete ordinary request")
            parts = Slabs(child, fanout)
            if any(2*part.volume > current.volume for part in parts.ports):
                # The proof puts every such case below a fixed width.
                response = elementary(child, request.source)
                continue
            banks = parts.split(request.source)
            for i, part in enumerate(parts.ports):
                banks[i] = run((tag+1) % len(words), part, banks[i], depth + 1)
            response = parts.merge(banks)

    return run(entry, port, source, 0)


def exchange_range(words, entry, q, size, prefix, gap, suffix, source, *, cutoff, fanout):
    """Pad two equal numerical ranges, run the closed word and restrict."""
    if min(size, prefix, gap, suffix) < 1 or q < 2:
        raise ValueError("invalid public field shape")
    if len(source) != prefix*gap*suffix*size**2:
        raise ValueError("incomplete public input")
    width, side = 0, 1
    while side < size:
        width += 1
        side *= q
    port = Port(q, width, prefix, gap, suffix)
    reader = iter(source)
    padded = []
    for _ in range(prefix):
        for head in range(side):
            for _ in range(gap):
                live = size*suffix if head < size else 0
                padded.extend(next(reader) for _ in range(live))
                padded.extend([0]*(side*suffix-live))
    result = close_cycle(words, entry, port, padded, cutoff=cutoff, fanout=fanout)
    output = []
    offset = 0
    for _ in range(prefix):
        for head in range(side):
            for _ in range(gap):
                if head < size:
                    output.extend(result[offset:offset+size*suffix])
                offset += side*suffix
    return output
