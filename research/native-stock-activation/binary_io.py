"""Read little-endian input intervals and send the carried product to its owner."""


def magnitude_bits(source, octets):
    """Find the significant length. Ignore high zero bytes and restore the input head."""
    if octets < 0:
        raise ValueError("The input extent must be nonnegative")
    origin = source.tell()
    done = significant = 0
    try:
        while done < octets:
            block = source.read(min(octets - done, 65536))
            if not block:
                raise EOFError("The input magnitude ended before its declared extent")
            used = block.rstrip(b"\x00")
            if used:
                significant = 8 * (done + len(used) - 1) + used[-1].bit_length()
            done += len(block)
    finally:
        source.seek(origin)
    return significant


def magnitude_limbs(source, length, bits):
    """Read the low length bits in base 2^bits and restore the input head."""
    if length < 0 or bits < 1:
        raise ValueError("Use a nonnegative magnitude length and a positive radix width")
    origin = source.tell()
    buffer = available = 0
    try:
        while length:
            width = min(bits, length)
            while available < width:
                block = source.read((width - available + 7) // 8)
                if not block:
                    raise EOFError("The input ended inside a magnitude digit")
                buffer |= int.from_bytes(block, "little") << available
                available += 8 * len(block)
            yield buffer & ((1 << width) - 1)
            buffer >>= width
            available -= width
            length -= width
    finally:
        source.seek(origin)


def carry_to_tape(target, coefficients, bits):
    """Write a canonical unsigned magnitude. Leave its neighboring intervals intact."""
    if bits < 1:
        raise ValueError("Use a positive output radix width")
    origin = target.tell()
    mask = (1 << bits) - 1
    zeroes = bytes(4096)
    deferred = carry = buffer = available = 0

    def emit(block):
        nonlocal deferred
        used = block.rstrip(b"\x00")
        if used:
            while deferred:
                take = min(deferred, len(zeroes))
                target.write(zeroes[:take])
                deferred -= take
            target.write(used)
        deferred += len(block) - len(used)

    for value in coefficients:
        if value < 0:
            raise ArithmeticError("A recovered unsigned convolution coefficient is negative")
        word = value + carry
        digit = word & mask
        carry = word >> bits
        buffer |= digit << available
        available += bits
        octets, available = divmod(available, 8)
        emit((buffer & ((1 << (8 * octets)) - 1)).to_bytes(octets, "little"))
        buffer >>= 8 * octets
    buffer |= carry << available
    emit(buffer.to_bytes((buffer.bit_length() + 7) // 8, "little"))
    if target.tell() == origin:
        target.write(b"\x00")
    return target.tell() - origin
