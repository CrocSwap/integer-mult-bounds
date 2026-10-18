"""Finite bit-stream execution of the retained signed packing boundary.

The integer-product backend uses Python multiplication for these small tests.
The written complexity proof uses the published fixed-tape multiplier.
"""


def need(value, message):
    if not value:
        raise ValueError(message)


def bits(value, width):
    need(0 <= value < 1 << width, "unsigned field extent")
    return [(value >> j) & 1 for j in range(width)]


def complement_increment(stream):
    carry = 1
    out = []
    for bit in stream:
        digit = 1 - bit + carry
        out.append(digit & 1)
        carry = digit >> 1
    return out


def signed_words(values, width):
    out = []
    for value in values:
        need(-(1 << (width - 1)) <= value < 1 << (width - 1), "signed field extent")
        out.extend(reversed(bits(value % (1 << width), width)))
    return out


def read_signed(stream, width):
    need(len(stream) % width == 0, "complete component words")
    out = []
    for start in range(0, len(stream), width):
        value = 0
        for bit in stream[start:start + width]:
            need(bit in (0, 1), "binary word")
            value = 2 * value + bit
        if stream[start]:
            value -= 1 << width
        out.append(value)
    return out


def unsigned_value(stream):
    value = 0
    for bit in reversed(stream):
        value = 2 * value + bit
    return value


def pack(values, p, receipt):
    """Read MSB component words, emit LSB packing blocks, then sign/magnitude."""
    width = 4 * p
    base = 1 << width
    carry = 0
    out = []
    for value in read_signed(signed_words(values, p + 2), p + 2):
        digit = (value + carry) % base
        carry = (value + carry - digit) // base
        need(carry in (-1, 0), "packing carry")
        out.extend(bits(digit, width))
    receipt["packed_fields"] += len(values)
    receipt["negative_evaluations"] += int(carry == -1)
    magnitude = complement_increment(out) if carry else out
    return (-1 if carry else 1), unsigned_value(magnitude)


def extract(sign, magnitude, r, p, receipt, fault=None):
    width = 4 * p
    base = 1 << width
    stream = bits(magnitude, 2 * r * width)
    extension = -1 if sign < 0 and magnitude else 0
    if extension:
        stream = complement_increment(stream)
    if fault == "omit_sign_extension":
        extension = 0
    carry = 0
    out = []
    for start in range(0, len(stream), width):
        block = unsigned_value(stream[start:start + width])
        value = block + carry
        centered = value % base
        if centered >= base // 2:
            centered -= base
        carry = (value - centered) // base
        need(carry in (0, 1), "extraction carry")
        out.append(centered)
    need(carry + extension == 0, "final extraction carry cancels sign extension")
    need(out[-1] == 0, "padded final ordinary coefficient")
    receipt["extracted_fields"] += len(out)
    receipt["negative_product_end_carries"] += carry
    return out


def ordinary_product(a, b, p, receipt, fault=None):
    r = len(a)
    need(r == len(b) and r >= 2 and r & (r - 1) == 0 and r < 1 << p,
         "ring product domain")
    sa, aa = pack(a, p, receipt)
    sb, bb = pack(b, p, receipt)
    # This is the separately specified exact integer-product call.
    return extract(sa * sb, aa * bb, r, p, receipt, fault)


def trunc_shift(value, shift):
    return -(abs(value) >> shift) if value < 0 else value >> shift


def ring_product(f, g, p, receipt, fault=None):
    r = len(f)
    need(len(g) == r, "aligned polynomial records")
    need(all(x * x + y * y <= 1 << (2 * p) for x, y in f + g), "disk input")
    a, b = [z[0] for z in f], [z[1] for z in f]
    c, e = [z[0] for z in g], [z[1] for z in g]
    ac = ordinary_product(a, c, p, receipt, fault)
    be = ordinary_product(b, e, p, receipt, fault)
    ae = ordinary_product(a, e, p, receipt, fault)
    bc = ordinary_product(b, c, p, receipt, fault)
    real = [x - y for x, y in zip(ac, be)]
    imag = [x + y for x, y in zip(ae, bc)]
    sign = 1 if fault == "cyclic_wrap" else -1
    exact = [(real[j] + sign * real[j + r], imag[j] + sign * imag[j + r])
             for j in range(r)]
    shift = p + r.bit_length() - 1
    if fault == "omit_r_normalization":
        shift = p
    output = [(trunc_shift(x, shift), trunc_shift(y, shift)) for x, y in exact]
    if fault != "omit_r_normalization":
        need(all(x * x + y * y <= 1 << (2 * p) for x, y in output), "disk output")
    serialized = signed_words([v for z in output for v in z], p + 2)
    need(read_signed(serialized, p + 2) == [v for z in output for v in z],
         "opposite-transform component boundary")
    return exact, output


def receipt():
    return {"packed_fields": 0, "extracted_fields": 0,
            "negative_evaluations": 0, "negative_product_end_carries": 0}
