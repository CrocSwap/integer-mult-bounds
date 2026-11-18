"""Reversible CLEAR for (x0+x1+x2+x3-x4-x5-x6-x7)/2.

Wires store little-endian bits. A gate tuple contains its controls followed
by its XOR target. The first 8*w wires are immutable inputs, followed by the
w target wires and the diagnostic. All remaining wires start and end zero.
"""


def compile_row(width):
    if width < 1:
        raise ValueError("positive signed width required")
    size = width + 3
    next_wire = 9 * width + 1
    gates = []

    def allocate(length):
        nonlocal next_wire
        block = range(next_wire, next_wire + length)
        next_wire += length
        return block

    def signed_operand(index):
        start = index * width
        return [start + min(bit, width - 1) for bit in range(size)]

    total = signed_operand(0)
    for index in range(1, 8):
        operand = signed_operand(index)
        result = allocate(size)
        carries = allocate(size - 1)
        for bit, (a, b, out) in enumerate(zip(total, operand, result, strict=True)):
            gates.extend(((a, out), (b, out)))  # propagate bit p = a XOR b
            if bit + 1 < size:
                carry = carries[bit]
                gates.append((a, b, carry))
                if index >= 4:
                    gates.append((b, carry))
                if bit:
                    gates.append((carries[bit - 1], out, carry))
                    if index >= 4:
                        gates.append((carries[bit - 1], carry))
            if bit:
                gates.append((carries[bit - 1], out))
        total = result

    mismatch = allocate(2)
    for offset, flag in enumerate(mismatch):
        gates.extend(((total[width], flag), (total[width + offset + 1], flag)))

    def boolean_or(left, right):
        out, = allocate(1)
        gates.extend(((left, out), (right, out), (left, right, out)))
        return out

    overflow = boolean_or(*mismatch)
    invalid = boolean_or(total[0], overflow)
    copy_outputs = [(total[bit + 1], 8 * width + bit) for bit in range(width)]
    copy_outputs.append((invalid, 9 * width))
    return next_wire, gates + copy_outputs + gates[::-1]
