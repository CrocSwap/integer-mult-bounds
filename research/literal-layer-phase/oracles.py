"""Independent exact arithmetic and explicit-address verification oracles.

These are test-only Python computations, never executed by the literal table.
They enumerate the source Cartesian address space rather than simulate carries.
"""
from itertools import product


def gamma(value):
    bits = bin(value)[2:]
    return '0'*(len(bits)-1)+bits


def header(parameters):
    return ''.join(gamma(v) for v in parameters)


def cardinality(parameters):
    _, _, r, dimension, outer, spectator, block, _, _ = parameters
    return r*outer*spectator*(1 << (dimension*block))


def phase_codes(parameters):
    _, _, r, dimension, outer, spectator, block, offset1, _ = parameters
    for _ in range(outer):
        for coordinate in product(range(1 << block), repeat=dimension):
            phase = sum((x >> (offset1-1)) & 1 for x in coordinate)
            for _ in range(spectator):
                for _ in range(r):
                    yield phase


def rotate(pair, phase):
    a, c = pair
    for _ in range(phase):
        a, c = -c, a
    return a, c


def expected(parameters, values):
    return [rotate(pair, phase) for pair, phase in zip(values, phase_codes(parameters))]


def encode(values, width):
    return ''.join(format(x % (1 << width), f'0{width}b') for pair in values for x in pair)


def decode(word, width):
    values = []
    for start in range(0, len(word), width):
        value = int(word[start:start+width], 2)
        values.append(value-(1 << width) if value >= 1 << (width-1) else value)
    return list(zip(values[::2], values[1::2]))


def fits(values, width):
    return all(-(1 << (width-1)) <= x < (1 << (width-1)) for pair in values for x in pair)
