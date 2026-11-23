"""Scan low-first binary counters and restore signed-magnitude input heads."""


from contextlib import closing


class LowCounter:
    """Keep canonical binary digits with the low bit at the active end."""

    def __init__(self, value=0):
        if value < 0:
            raise ValueError("Use a nonnegative counter")
        self.digits = bytearray()
        for octet in value.to_bytes((value.bit_length() + 7) // 8, "little"):
            self.digits.extend((octet >> bit) & 1 for bit in range(8))
        while self.digits and not self.digits[-1]:
            self.digits.pop()

    def take(self):
        if not self.digits:
            return False
        i = 0
        while not self.digits[i]:
            self.digits[i] = 1
            i += 1
        self.digits[i] = 0
        if i + 1 == len(self.digits):
            self.digits.pop()
        return True

    def add_one(self):
        i = 0
        while i < len(self.digits) and self.digits[i]:
            self.digits[i] = 0
            i += 1
        if i == len(self.digits):
            self.digits.append(1)
        else:
            self.digits[i] = 1

    def value(self):
        data = bytearray((len(self.digits) + 7) // 8)
        for bit, value in enumerate(self.digits):
            data[bit // 8] |= value << (bit % 8)
        result = int.from_bytes(data, "little")
        data[:] = bytes(len(data))
        return result

    def clear(self):
        while self.digits:
            self.digits[-1] = 0
            self.digits.pop()


def slab_indices(count):
    """Yield once per complete slab. Retire the counter on an early exit."""
    remaining = LowCounter(count)
    try:
        while remaining.take():
            yield None
    finally:
        remaining.clear()


def magnitude_bits(source, octets):
    """Read the declared byte interval and return to its original boundary."""
    if octets < 0:
        raise ValueError("The input extent must be nonnegative")
    remaining = LowCounter(octets)
    trailing = LowCounter()
    last = 0
    origin = source.tell()
    try:
        while remaining.take():
            byte = source.read(1)
            if not byte:
                raise EOFError("The input magnitude ended before its declared extent")
            if byte[0]:
                last = byte[0]
                trailing.clear()
            else:
                trailing.add_one()
        return 8 * (octets - trailing.value() - 1) + last.bit_length() if last else 0
    finally:
        remaining.clear()
        trailing.clear()
        source.seek(origin)


BLOCK = 1 << 16
ZERO_BLOCK = bytes(BLOCK)


def _block_sizes(count):
    blocks, last = divmod(count, BLOCK)
    remaining = LowCounter(blocks)
    try:
        while remaining.take():
            yield BLOCK
        if last:
            yield last
    finally:
        remaining.clear()


def transfer(source, target, count):
    """Copy exactly one interval, or consume it when the target is absent."""
    with closing(_block_sizes(count)) as sizes:
        for size in sizes:
            while size:
                block = source.read(size)
                if not block:
                    raise EOFError("The source field ended inside its declared extent")
                if target is not None:
                    target.write(block)
                size -= len(block)


def zero_bytes(target, count):
    """Fill one declared interval with zeroes in forward order."""
    with closing(_block_sizes(count)) as sizes:
        for size in sizes:
            target.write(ZERO_BLOCK[:size])


def rectangle_slab(source, target, small, big, gap, suffix, *, restrict=False):
    """Extend or restrict two address fields in one contiguous prefix slab."""
    real = small * suffix
    pad = (big - small) * suffix
    with closing(slab_indices(small)) as rows:
        for _ in rows:
            with closing(slab_indices(gap)) as intervals:
                for _ in intervals:
                    transfer(source, target, real)
                    if restrict:
                        transfer(source, None, pad)
                    else:
                        zero_bytes(target, pad)
    tail = (big - small) * gap * big * suffix
    if restrict:
        transfer(source, None, tail)
    else:
        zero_bytes(target, tail)
