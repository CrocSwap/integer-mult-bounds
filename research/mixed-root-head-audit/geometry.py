"""Literal character checks for one mixed root. Ali Romman, with Codex. Apache-2.0."""

from itertools import combinations


def apply(columns, value):
    result = 0
    while value:
        bit = value & -value
        result ^= columns[bit.bit_length() - 1]
        value -= bit
    return result


def transpose(columns):
    return [sum(((value >> j) & 1) << i for i, value in enumerate(columns))
            for j in range(len(columns))]


def phase(terms, character):
    return sum(coefficient * ((direction & character).bit_count() % 2)
               for direction, coefficient in terms) % 4


def difference(before, after, columns):
    result = {}
    for direction, coefficient in [*after, *[(apply(columns, v), -c) for v, c in before]]:
        result[direction] = (result.get(direction, 0) + coefficient) % 4
    return [(v, c) for v, c in result.items() if v and c]


def translation(terms, ambient):
    """Recover all degree-two coefficients through character evaluations."""
    if phase(terms, 0):
        raise ValueError('nonzero constant phase')
    singles = [phase(terms, 1 << j) for j in range(ambient)]
    if any(value % 2 for value in singles):
        raise ValueError('odd linear phase')
    for i, j in combinations(range(ambient), 2):
        if (phase(terms, (1 << i) | (1 << j)) - singles[i] - singles[j]) % 4:
            raise ValueError('nonzero quadratic phase')
    return sum((value // 2) << j for j, value in enumerate(singles))


def native_route(frame, color, ambient=137):
    head, *basis = frame
    body = [1 << (9 + 8 * color + j) for j in range(8)]
    active = 511 | sum(body)
    columns = []
    for axis in range(ambient):
        value = 1 << axis
        output = value & ~active
        if (value & head).bit_count() % 2:
            output ^= head
        for central, fresh in zip(basis, body, strict=True):
            if (value & central).bit_count() % 2:
                output ^= fresh
            if value & fresh:
                output ^= central
        columns.append(output)
    return columns


def native_boundaries(head, color):
    before = [(1 << j, 1) for j in range(9 + 8 * color)]
    after = [(1 << j, 1) for j in range(9 + 8 * (color + 1))]
    spectators = [(1 << j, 1) for j in range(9, 9 + 8 * (color + 1))]
    native_x_in = [*spectators, (head, 1)]
    native_y_in = spectators
    native_x_out = [*spectators, *[(1 << j, 1) for j in range(9)]]
    native_y_out = [*native_x_out, (head, -1)]
    return [(before, native_x_in), ([*before, (head, -1)], native_y_in),
            (native_x_out, after), (native_y_out, [*after, (head, -1)])]
