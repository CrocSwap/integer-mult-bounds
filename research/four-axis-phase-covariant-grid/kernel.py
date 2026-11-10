"""Literal forward/inverse Gaussian block; @CubeJerry/AI, Apache-2.0.

Diagonal phases and the endpoint convention follow Nick Petalas #6574,
Ali Romman's Gaussian rounding lineage, and David Ganz / Dugongue.
"""
from construction import SIZE, need, source_key, target_key, walsh

MAX_BITS = 4096


def rotate(value, exponent):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def real_map(values, table, inverse=False):
    key = target_key(values) if inverse else source_key(values)
    need(key in table, 'Known real quotient class')
    numerator = tuple(a + b for a, b in zip(walsh(values), table[key]))
    need(all(x % 4 == 0 for x in numerator), 'Exact quarter shift')
    return tuple(x // 4 for x in numerator)


def block(values, tables, inverse=False):
    """Return sixteen Gaussian pairs; never mutate inputs or correction tables."""
    need(type(values) in (tuple, list) and len(values) == SIZE,
         'Sixteen Gaussian integer inputs')
    need(all(type(z) in (tuple, list) and len(z) == 2 for z in values),
         'Real/imaginary component pairs')
    need(all(type(v) is int and v.bit_length() <= MAX_BITS
             for z in values for v in z), 'At most 4096 bits per component')
    need(type(inverse) is bool, 'Boolean inverse selector')
    if inverse:
        rotated = tuple(rotate((-a, -b), j.bit_count())
                        for j, (a, b) in enumerate(values))
    else:
        rotated = tuple(rotate(z, -j.bit_count()) for j, z in enumerate(values))
    table = tables[1 if inverse else 0]
    real = real_map(tuple(z[0] for z in rotated), table, inverse)
    imag = real_map(tuple(z[1] for z in rotated), table, inverse)
    if inverse:
        return tuple(rotate((a, b), j.bit_count())
                     for j, (a, b) in enumerate(zip(real, imag)))
    return tuple(rotate((-a, -b), -j.bit_count())
                 for j, (a, b) in enumerate(zip(real, imag)))
