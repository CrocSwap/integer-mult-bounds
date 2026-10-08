"""Portable little-endian arrays for the archived producer interchange format.

Copyright 2026 icekylinx. Apache-2.0; written with AI assistance.
"""
import array
import sys


def read_array(stream, code, count):
    result = array.array(code)
    expected_size = {'I': 4, 'Q': 8, 'B': 1, 'b': 1}[code]
    if result.itemsize != expected_size:
        raise RuntimeError('Unsupported native array width')
    raw = stream.read(count * expected_size)
    if len(raw) != count * expected_size:
        raise ValueError('Truncated producer array')
    result.frombytes(raw)
    if sys.byteorder != 'little' and result.itemsize > 1:
        result.byteswap()
    return result


def write_array(stream, values):
    if values.itemsize != {'I': 4, 'Q': 8, 'B': 1, 'b': 1}[values.typecode]:
        raise RuntimeError('Unsupported native array width')
    if sys.byteorder != 'little' and values.itemsize > 1:
        values = array.array(values.typecode, values)
        values.byteswap()
    values.tofile(stream)
