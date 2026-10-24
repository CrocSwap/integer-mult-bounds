# SPDX-License-Identifier: Apache-2.0
"""Exact native K_G columns, following the credited PR2226 phase convention."""
from collections import defaultdict
from algebra import modular_rank, need

IDENTITY = tuple(1 << i for i in range(9))


def linear(columns, x):
    value = 0
    for i, column in enumerate(columns):
        if x >> i & 1:
            value ^= column
    return value


def inverse(columns):
    pivots = {}
    for i, value in enumerate(columns):
        coefficient = 1 << i
        for p in sorted(pivots, reverse=True):
            if value >> p & 1:
                value ^= pivots[p][0]
                coefficient ^= pivots[p][1]
        need(value != 0, 'invertible binary map')
        pivots[value.bit_length() - 1] = (value, coefficient)
    result = []
    for i in range(9):
        value, coefficient = 1 << i, 0
        for p in sorted(pivots, reverse=True):
            if value >> p & 1:
                value ^= pivots[p][0]
                coefficient ^= pivots[p][1]
        need(value == 0, 'binary inverse')
        result.append(coefficient)
    return result


def monomial(columns):
    """K_G |x> = i^q(Gx) |Gx>; q uses Q = I + G^-T G^-1 over F2."""
    need(len(columns) == 9 and all(type(c) is int and 0 <= c < 512 for c in columns),
         'nine-bit map')
    inv = inverse(columns)
    transpose = [sum(((inv[j] >> i) & 1) << j for j in range(9)) for i in range(9)]
    quadratic = [(1 << j) ^ linear(transpose, inv[j]) for j in range(9)]
    need(all((quadratic[j] >> i & 1) == (quadratic[i] >> j & 1)
             for i in range(9) for j in range(9)), 'symmetric quadratic')
    result = []
    for x in range(512):
        y = linear(columns, x)
        phase = sum((quadratic[i] >> i & 1) * (y >> i & 1) for i in range(9))
        phase += 2 * sum((quadratic[j] >> i & 1) * (y >> i & 1) * (y >> j & 1)
                         for i in range(9) for j in range(i + 1, 9))
        result.append((y, phase % 4))
    return result


def direct_columns(columns):
    """Separate inverse-permutation/Gram-column evaluation of the same formula."""
    permutation = [linear(columns, x) for x in range(512)]
    need(len(set(permutation)) == 512, 'permutation inverse exists')
    back = {y: x for x, y in enumerate(permutation)}
    gi = [back[1 << i] for i in range(9)]
    result = []
    for y in permutation:
        active = [i for i in range(9) if y >> i & 1]
        diagonal = sum(1 ^ (gi[i].bit_count() & 1) for i in active)
        cross = sum((gi[i] & gi[j]).bit_count() & 1 for i in active for j in active if i < j)
        result.append((y, (diagonal + 2 * cross) % 4))
    return result


def operator_rows(operators):
    rows = defaultdict(dict)
    units = ((1, 0), (0, 1), (-1, 0), (0, -1))
    for operator, columns in enumerate(operators):
        need(len(columns) == 512, 'all native columns')
        for x, (y, phase) in enumerate(columns):
            need(0 <= y < 512 and 0 <= phase < 4, 'native column range')
            for component, coefficient in enumerate(units[phase]):
                if coefficient:
                    rows[x, y, component][operator] = coefficient
    labels = sorted(rows)
    return labels, [rows[label] for label in labels]


def certify(word):
    maps, aliases = [IDENTITY], {0: 0}
    groups = defaultdict(list)
    for operator, record in enumerate(word['warps'], 1):
        columns = tuple(record[2])
        if columns not in maps:
            maps.append(columns)
        aliases[operator] = maps.index(columns)
        groups[aliases[operator]].append(operator)
    matrices = []
    for columns in maps:
        matrix = monomial(columns)
        need(matrix == direct_columns(columns), 'independent phase/column agreement')
        matrices.append(matrix)
    labels, rows = operator_rows(matrices)
    rank, selected = modular_rank(rows, range(len(maps)))
    need(rank == len(maps), 'native operators not independently certified')
    return aliases, {'distinct_including_identity': len(maps), 'rank': rank,
                     'coordinate_equations': len(rows),
                     'minor_rows': [list(labels[i]) for i in selected],
                     'equal_operator_groups': [v for v in groups.values() if len(v) > 1]}
