"""Exact NTT leaves for ordinary signed binary multiplication."""

from ctypes import CDLL, POINTER, c_int, c_size_t, c_uint8
from pathlib import Path

MODULI = ((2013265921, 31), (1811939329, 13))
MAX_TRANSFORM = 1 << 26
DIGIT_MASK = (1 << 16) - 1


def transform(values, prime, generator, inverse):
    n = len(values)
    h = 1 if inverse else n // 2
    while 0 < h < n:
        exponent = (prime - 1) // (2 * h)
        root = pow(generator, prime - 1 - exponent if inverse else exponent, prime)
        for start in range(0, n, 2 * h):
            phase = 1
            left = values[start:start+h]
            right = values[start+h:start+2*h]
            for j, (a, b) in enumerate(zip(left, right, strict=True)):
                if inverse:
                    b = b * phase % prime
                values[start+j] = (a+b) % prime
                diff = (a-b) % prime
                left[j] = diff if inverse else diff * phase % prime
                phase = phase * root % prime
            values[start+h:start+2*h] = left
        h = h * 2 if inverse else h // 2
    if inverse:
        scale = pow(n, -1, prime)
        for i, value in enumerate(values):
            values[i] = value * scale % prime


def digits(raw):
    return [int.from_bytes(raw[i:i+2], "little") for i in range(0, len(raw), 2)]


def reference_product(a, b):
    """Read unsigned packed bytes and return their full-width product."""
    if not a or not b:
        return bytes(len(a)+len(b))
    left, right = digits(a), digits(b)
    count = len(left)+len(right)-1
    length = 1 << (count-1).bit_length()
    if length > MAX_TRANSFORM:
        raise ValueError("Convolution exceeds the shorter prime root order")
    residues = []
    for prime, generator in MODULI:
        x = left+[0]*(length-len(left))
        y = right+[0]*(length-len(right))
        transform(x, prime, generator, False)
        transform(y, prime, generator, False)
        for i, value in enumerate(y):
            x[i] = x[i] * value % prime
        transform(x, prime, generator, True)
        residues.append(x)
    p, q = (pair[0] for pair in MODULI)
    inv = pow(p, -1, q)
    out = bytearray()
    carry = 0
    for i in range(count):
        u, v = residues[0][i], residues[1][i]
        carry += u + p * (((v-u) * inv) % q)
        out.extend((carry & DIGIT_MASK).to_bytes(2, "little"))
        carry >>= 16
    out.extend(carry.to_bytes(len(a)+len(b)-len(out), "little"))
    return bytes(out)


def native_product(library):
    """Load the optional C implementation of the same finite transform."""
    kernel = CDLL(str(Path(library).resolve())).short_product
    ptr = POINTER(c_uint8)
    kernel.argtypes = (ptr, c_size_t, ptr, c_size_t, ptr, c_size_t)
    kernel.restype = c_int

    def multiply(a, b):
        data_a = (c_uint8 * len(a)).from_buffer_copy(a)
        data_b = (c_uint8 * len(b)).from_buffer_copy(b)
        out = (c_uint8 * (len(a)+len(b)))()
        status = kernel(data_a, len(a), data_b, len(b), out, len(out))
        if status == 2:
            raise MemoryError("Cannot allocate the complete transform")
        if status:
            raise ValueError("Invalid transform or output extent")
        return bytes(out)

    return multiply
