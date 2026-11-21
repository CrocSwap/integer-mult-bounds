"""Execute serial type-major child batches with physically top-only stacks."""

from dataclasses import dataclass

HEAD = object()


class Stack:
    def __init__(self):
        self.cells = []
        self.moves = self.high = 0

    def write(self, value):
        self.cells.append(value)
        self.moves += 2
        self.high = max(self.high, len(self.cells))

    def take(self):
        self.moves += 2
        return self.cells.pop()

    def enter(self):
        self.write(HEAD)

    def leave(self):
        if self.take() is not HEAD:
            raise ValueError("A child crossed its frame marker")


@dataclass(frozen=True)
class Cut:
    lows: int
    repeats: int


def flags(lows, repeats, bit):
    """Read low bits in their true order after all preceding stable passes."""
    radix = 1 << bit
    short, extra = divmod(lows, radix)
    for residues, length in ((extra, short + 1), (radix - extra, short)):
        for _ in range(residues):
            for _ in range(repeats):
                for z in range(length):
                    yield z % 2


def transpose(packet, lows, repeats, inverse=False):
    """Stable radix transport using sequential FIFO scans. No packet carries its key."""
    block, leftover = divmod(len(packet), lows * repeats)
    if not block or leftover:
        raise ValueError("The geometry needs positive whole blocks")
    current = packet
    powers = range((lows - 1).bit_length())
    for bit in reversed(powers) if inverse else powers:
        src = iter(current)
        banks = ([], [])
        if inverse:
            zero_blocks = sum(f == 0 for f in flags(lows, repeats, bit))
            banks[0].extend(next(src) for _ in range(zero_blocks * block))
            banks[1].extend(src)
            readers = tuple(map(iter, banks))
            current = [next(readers[f]) for f in flags(lows, repeats, bit)
                       for _ in range(block)]
        else:
            for f in flags(lows, repeats, bit):
                banks[f].extend(next(src) for _ in range(block))
            current = banks[0] + banks[1]
    return tuple(current)


class Dispatch:
    """The two scratch payload streams are empty between sibling calls."""

    def __init__(self, cuts):
        self.cuts = cuts
        self.pending = Stack()
        self.returned = Stack()
        self.serial_volume = 0
        self.groups = 0

    def visit(self, packet, depth, path):
        if depth == len(self.cuts):
            # A returned packet differs from the parent's copied original.
            return tuple((x + 1 + sum((i + 1) * a for i, a in enumerate(path))) % 257
                         for x in packet)
        cut = self.cuts[depth]
        length, rem = divmod(len(packet), cut.repeats * cut.lows)
        assert not rem and length > 0
        self.groups += cut.lows
        self.serial_volume += len(packet)
        type_major = transpose(packet, cut.lows, cut.repeats)
        self.pending.enter()
        self.returned.enter()
        for x in reversed(type_major):
            self.pending.write(x)
        group_size = cut.repeats * length
        for low in range(cut.lows):
            group = tuple(self.pending.take() for _ in range(group_size))
            result = self.visit(group, depth + 1, path + (low,))
            for x in result:
                self.returned.write(x)
        # Pop and erase, then read the temporary output stream backwards.
        reverse = tuple(self.returned.take() for _ in packet)
        self.pending.leave()
        self.returned.leave()
        received = reverse[::-1]
        return transpose(received, cut.lows, cut.repeats, inverse=True)


def expected(index, size, cuts):
    add = 1
    for depth, cut in enumerate(cuts):
        run = size // (cut.repeats * cut.lows)
        a, rest = divmod(index, cut.lows * run)
        low, offset = divmod(rest, run)
        index = a * run + offset
        add += (depth + 1) * low
        size //= cut.lows
    return add


def main():
    layouts = 0
    for lows in range(1, 69):
        for repeats in range(1, 5):
            for block in (1, 3):
                data = tuple(range(lows * repeats * block))
                encoded = tuple((i + 7) * (i + 11) % 419 for i in data)
                direct = tuple((r * lows + l) * block + j for l in range(lows)
                               for r in range(repeats) for j in range(block))
                assert transpose(data, lows, repeats) == direct
                assert transpose(tuple(encoded[i] for i in direct), lows, repeats, inverse=True) == encoded
                layouts += 1
    print("binary stable forward/changed-return layouts", layouts)
    tested = 0
    for lows in ((1,), (2, 3), (3, 2, 5), (5, 2, 3), (7, 4, 1, 2)):
        for extra in (1, 3, 8):
            sizes = tuple(Cut(q, 2 if i % 2 else 3) for i, q in enumerate(lows))
            n = 6 * extra
            for q in lows:
                n *= q
            data = tuple((37 * j) % 257 for j in range(n))
            call = Dispatch(sizes)
            result = call.visit(data, 0, ())
            assert not call.pending.cells and not call.returned.cells
            assert result == tuple((v + expected(j, n, sizes)) % 257 for j, v in enumerate(data))
            count = 1
            nodes = 0
            for q in lows:
                nodes += count
                count *= q
            assert call.pending.moves + call.returned.moves == 8 * (call.serial_volume + nodes)
            tested += 1
    print("serial type-major stack checks", tested, "exact moves 8*(sum node volumes + nodes)")


if __name__ == "__main__":
    main()
