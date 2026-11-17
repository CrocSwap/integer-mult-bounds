"""Exact finite translation-kernel words. Nick Petalas. Apache-2.0."""
from fractions import Fraction
from math import lcm

from kernels import require, sparse_add


def packed_source(columns, directions):
    require(len(columns) == 30 and len(directions) == 112, 'source dimensions')
    return [{512 * port + directions[port]: c for port, c in col.items()}
            for col in columns]


def translated(kernel, shift):
    require(type(shift) is int and 0 <= shift < 512, 'translation range')
    return {key ^ shift: c for key, c in kernel.items()}


def prior_basis(source, reader):
    """Construct the cited PR6677 input basis, without running its verifier."""
    source[1] = sparse_add(source[1], translated(source[4], 258), Fraction(-2))
    reader[4] = sparse_add(reader[4], translated(reader[1], 258), Fraction(2))


def change(source, reader, coefficient=Fraction(-1, 5)):
    """New step: L0 += c L1 and J1 -= c J0, zero-based indices."""
    require(len(source) == len(reader) == 30, 'factor dimensions')
    require(isinstance(coefficient, Fraction), 'exact rational coefficient')
    reader[0] = sparse_add(reader[0], reader[1], coefficient)
    source[1] = sparse_add(source[1], source[0], -coefficient)


def metrics(source, reader):
    rows = source + reader
    require(len(source) == len(reader) == 30, 'factor dimensions')
    require(all(0 <= key < 112 * 512 for row in rows for key in row), 'kernel keys')
    source_l1 = [Fraction(0)] * 112
    for col in source:
        for key, c in col.items():
            source_l1[key // 512] += abs(c)
    coefficients = [c for row in rows for c in row.values()]
    denominator = lcm(*(c.denominator for c in coefficients))
    shift_weights = [0] * 10
    for row in rows:
        for key in row:
            shift_weights[(key % 512).bit_count()] += 2
    return {'source_coefficients': sum(map(len, source)),
            'reader_coefficients': sum(map(len, reader)),
            'coefficient_adds': 2 * sum(map(len, rows)),
            'nonidentity_shift_adds': 2 * sum(key % 512 != 0 for row in rows for key in row),
            'shift_weight_histogram': shift_weights,
            'axis_translation_units': sum(i * count for i, count in enumerate(shift_weights)),
            'common_denominator': denominator,
            'maximum_coefficient': str(max(map(abs, coefficients))),
            'source_row_l1': str(max(source_l1)),
            'reader_row_l1': str(max(sum(map(abs, row.values())) for row in reader))}


def pair_product(source, reader):
    """Multiply the two changed factors in the exact XOR group algebra."""
    result = {}
    for mode in (0, 1):
        for output, a in source[mode].items():
            out_port, out_shift = divmod(output, 512)
            for entry, b in reader[mode].items():
                in_port, in_shift = divmod(entry, 512)
                key = (out_port, in_port, out_shift ^ in_shift)
                result[key] = result.get(key, 0) + a * b
    return {key: value for key, value in result.items() if value}


def gather(reader, data, bank, denominator, sign):
    result = [[denominator * value for value in row] for row in bank]
    count = 0
    for mode, row in enumerate(reader):
        for key, c in row.items():
            port, shift = divmod(key, 512)
            numerator = c * denominator
            require(numerator.denominator == 1, 'gather integer scale')
            for address in range(512):
                result[mode][address] += sign * int(numerator) * data[port][address ^ shift]
            count += 1
    return result, count


def scatter(source, data, bank, denominator, sign):
    result = [[denominator * value for value in row] for row in data]
    count = 0
    for mode, column in enumerate(source):
        for key, c in column.items():
            port, shift = divmod(key, 512)
            numerator = c * denominator
            require(numerator.denominator == 1, 'scatter integer scale')
            for address in range(512):
                result[port][address] += sign * int(numerator) * bank[mode][address ^ shift]
            count += 1
    return result, count


def apply_word(source, reader, data, bank):
    require(len(source) == len(reader) == 30, 'factor count')
    require(len(data) == 112 and len(bank) == 30, 'payload dimensions')
    require(all(len(row) == 512 for row in data + bank), 'address count')
    denominator = lcm(*(c.denominator for row in source + reader for c in row.values()))
    centre, result = [row[:] for row in bank], [row[:] for row in data]
    count, scale = 0, 1
    for sign in (1, -1):
        centre, used = gather(reader, result, centre, denominator, sign)
        count += used
        result = [[denominator * value for value in row] for row in result]
        scale *= denominator
        result, used = scatter(source, result, centre, denominator, sign)
        count += used
        centre = [[denominator * value for value in row] for row in centre]
        scale *= denominator
    return result, centre, count, scale
