"""Generate dense repeated words and multiply their sparse quadratic defects."""

from dataclasses import dataclass
from operand import recognise_sparse


def trim(data):
    end = len(data)
    while end and not data[end - 1]:
        end -= 1
    return bytes(data[:end]) if end else b"\0"


def pack(data):
    """Convert literal low-first bits with one linear scan."""
    packed = bytearray((len(data) + 7) // 8)
    for k, bit in enumerate(data):
        packed[k // 8] |= bit << (k % 8)
    return int.from_bytes(packed, "little")


def unpack(value, width):
    if value < 0 or value.bit_length() > width:
        raise ValueError("The nonnegative value must fit the literal word")
    packed = value.to_bytes((width + 7) // 8, "little")
    return bytes((packed[k // 8] >> (k % 8)) & 1 for k in range(width))


def plus(a, b):
    out = bytearray()
    carry = 0
    for i in range(max(len(a), len(b))):
        if i < len(a):
            carry += a[i]
        if i < len(b):
            carry += b[i]
        out.append(carry & 1)
        carry >>= 1
    if carry:
        out.append(carry)
    return trim(out)


def difference(a, b):
    """Return the sign and magnitude of a minus b by literal-bit scans."""
    a, b = trim(a), trim(b)
    if len(a) != len(b):
        negative = len(a) < len(b)
    else:
        negative = next((x < y for x, y in zip(reversed(a), reversed(b), strict=True)
                         if x != y), False)
    if negative:
        a, b = b, a
    out = bytearray()
    borrow = 0
    for i, bit in enumerate(a):
        delta = bit - borrow - (b[i] if i < len(b) else 0)
        out.append(delta & 1)
        borrow = int(delta < 0)
    return (-1 if negative else 1), trim(out)


@dataclass(frozen=True)
class Expansion:
    short: bytes
    residual: bytes
    chart: object
    shift: int
    sign: int


def admit(raw, m, width, count, fit=recognise_sparse):
    direct = fit(raw, m)
    if direct is not None:
        return Expansion(b"\0", raw, direct, 0, 1)
    short = raw[:width].ljust(width, b"\0")
    sign, defect = difference(raw, short * count)
    if any(defect[:width]):
        return None
    residual = trim(defect[width:])
    chart = fit(residual, m)
    if chart is None:
        return None
    return Expansion(trim(short), residual, chart, width, sign)


def sparse_times_short(sparse, short):
    """Add the short word once at each occupied bit on the long tape."""
    if short == b"\0":
        return b"\0"
    out = bytearray(len(sparse) + len(short) + 1)
    head = 0
    for occupied in sparse:
        if occupied:
            mark = head
            carry = 0
            for bit in short:
                s = out[head] + bit + carry
                out[head] = s & 1
                carry = s >> 1
                head += 1
            while carry:
                s = out[head] + 1
                out[head] = s & 1
                carry = s >> 1
                head += 1
            while head > mark:
                head -= 1
        head += 1
    return trim(out)


def repeat_sum(data, width, count):
    """Multiply by the finite geometric sum on a sliding window of limbs."""
    if data == b"\0" or count == 1:
        return data
    length = (len(data) + width - 1) // width
    out = bytearray()
    running = carry = 0
    mask = (1 << width) - 1
    delayed = bytearray(data)
    for i in range(length + count - 1):
        if i < length:
            running += pack(data[i * width:(i + 1) * width])
        if i >= count:
            j = i - count
            running -= pack(delayed[j * width:(j + 1) * width])
        carry += running
        out.extend(unpack(carry & mask, width))
        carry >>= width
    if carry:
        out.extend(unpack(carry, carry.bit_length()))
    delayed[:] = bytes(len(delayed))
    return trim(out)


def assemble(sparse, a, b, width, count):
    """Use decoded defects and include both cross terms and the dense product."""
    if a.shift == b.shift == 0:
        return sparse
    short_product = sparse_times_short(a.short, b.short)
    positive = repeat_sum(repeat_sum(short_product, width, count), width, count)
    negative = b"\0"
    terms = [(a.sign * b.sign, a.shift + b.shift, sparse)]
    for x, y in ((a, b), (b, a)):
        cross = sparse_times_short(x.residual, y.short)
        terms.append((x.sign, x.shift, repeat_sum(cross, width, count)))
    for sign, shift, magnitude in terms:
        if magnitude == b"\0":
            continue
        field = b"\0" * shift + magnitude
        if sign > 0:
            positive = plus(positive, field)
        else:
            negative = plus(negative, field)
    sign, result = difference(positive, negative)
    if sign < 0:
        raise ArithmeticError("The completed product has negative magnitude")
    return result
