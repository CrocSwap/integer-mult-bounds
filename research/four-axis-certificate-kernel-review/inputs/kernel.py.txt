"""Indexed four-axis Gaussian grid map and its literal inverse.

Produced by Nick Petalas. Apache-2.0.
"""
from construction import SIZE, need, walsh

MAX_BITS = 4096


def rotate(value, exponent):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def validate(values):
    need(type(values) in (tuple, list) and len(values) == SIZE,
         "Sixteen Gaussian integer inputs")
    need(all(type(z) in (tuple, list) and len(z) == 2 for z in values),
         "Real/imaginary component pairs")
    need(all(type(v) is int and v.bit_length() <= MAX_BITS
             for z in values for v in z), "At most 4096 bits per component")


def real_map(values, table):
    numerator = walsh(values)
    key = tuple(v % 4 for v in numerator)
    need(key in table, "Known Walsh quotient")
    shifted = tuple(a + b for a, b in zip(numerator, table[key]))
    need(all(v % 4 == 0 for v in shifted), "Exact quarter shifts")
    return tuple(v // 4 for v in shifted)


def block(values, tables, inverse=False):
    """Return a new block. Input and table values are never modified."""
    validate(values)
    need(type(inverse) is bool, "Boolean inverse selector")
    if inverse:
        rotated = tuple(rotate((-a, -b), j.bit_count())
                        for j, (a, b) in enumerate(values))
    else:
        rotated = tuple(rotate(z, -j.bit_count()) for j, z in enumerate(values))
    table = tables[1 if inverse else 0]
    real = real_map(tuple(z[0] for z in rotated), table)
    imag = real_map(tuple(z[1] for z in rotated), table)
    if inverse:
        return tuple(rotate((a, b), j.bit_count())
                     for j, (a, b) in enumerate(zip(real, imag)))
    return tuple(rotate((-a, -b), -j.bit_count())
                 for j, (a, b) in enumerate(zip(real, imag)))
