#!/usr/bin/env python3
"""Check dyadic rank attainment and the strict-gap completion.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def power_two(n):
    return n > 0 and n & (n-1) == 0


def dyadic(x):
    return power_two(F(x).denominator)


def unit(x):
    x = F(x)
    return power_two(abs(x.numerator)) and power_two(x.denominator)


def determinant(p):
    return p[0][0]*p[1][1]-p[0][1]*p[1][0]


def rank(matrix):
    a = [[F(x) for x in row] for row in matrix]
    pivot = 0
    for column in range(len(a[0])):
        found = next((i for i in range(pivot, len(a)) if a[i][column]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        value = a[pivot][column]
        a[pivot] = [x/value for x in a[pivot]]
        for i in range(len(a)):
            if i != pivot:
                value = a[i][column]
                a[i] = [x-value*y for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def correction_rank(p):
    return rank([[x-int(i == j) for j, x in enumerate(row)] for i, row in enumerate(p)])


def rank_mod_three(matrix):
    a = [[int(x) % 3 for x in row] for row in matrix]
    pivot = 0
    for column in range(len(a[0])):
        found = next((i for i in range(pivot, len(a)) if a[i][column]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        a[pivot] = [(x*a[pivot][column]) % 3 for x in a[pivot]]
        for i in range(len(a)):
            if i != pivot:
                value = a[i][column]
                a[i] = [(x-value*y) % 3 for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def completion(a, b, t):
    return ((b[0], -t*a[1]), (b[1], t*a[0]))


def classify(a, b):
    a, b = tuple(map(F, a)), tuple(map(F, b))
    require(len(a) == len(b) == 2 and all(dyadic(x) for x in (*a, *b)), 'dyadic pair')
    require(sum(x*y for x, y in zip(a, b)) == 1, 'normalized pair')
    if a == b == (1, 0):
        return 0, 0, F(1)
    if a[0] == b[0] == 1:
        return 1, 1, F(1)
    if a[0] == 1 or b[0] == 1:
        return 2, 2, F(1)
    t = (b[0]-1)/(1-a[0])
    return 1, (1 if unit(t) else 2), (t if unit(t) else F(1))


def validate(a, b, p):
    require(all(dyadic(x) for row in p for x in row), 'nondyadic coefficient')
    require(unit(determinant(p)), 'nonunit determinant')
    require(tuple(row[0] for row in p) == tuple(b), 'primal endpoint')
    require(tuple(sum(a[i]*p[i][j] for i in range(2)) for j in range(2)) == (1, 0),
            'dual endpoint')


def matrix_word(n, instructions):
    p = [[F(int(i == j)) for j in range(n)] for i in range(n)]
    for target, source, coefficient in instructions:
        p[target] = [x+coefficient*y for x, y in zip(p[target], p[source])]
    return p


def verify():
    contracts = set()
    literal_matrices = 0
    grid = [F(i, 2) for i in range(-4, 5)]
    for entries in product(grid, repeat=4):
        p = (entries[:2], entries[2:])
        det = determinant(p)
        if not unit(det):
            continue
        a = (p[1][1]/det, -p[0][1]/det)
        b = (p[0][0], p[1][0])
        contracts.add((a, b))
        _, required, _ = classify(a, b)
        require(correction_rank(p) >= required, 'literal matrix below claimed minimum')
        validate(a, b, p)
        literal_matrices += 1
    integer_pairs = 0
    for values in product(range(-5, 6), repeat=4):
        a, b = tuple(map(F, values[:2])), tuple(map(F, values[2:]))
        if sum(x*y for x, y in zip(a, b)) == 1:
            contracts.add((a, b))
            integer_pairs += 1
    cases = Counter()
    for a, b in sorted(contracts):
        field_min, dyadic_min, t = classify(a, b)
        p = completion(a, b, t)
        validate(a, b, p)
        require(correction_rank(p) == dyadic_min, 'attaining completion rank')
        published_field_formula = (int(a != (1, 0))+int(b != (1, 0))
                                   - min(int(a[0] != 1), int(b[0] != 1)))
        require(field_min == published_field_formula, 'field formula')
        field_t = (b[0]-1)/(1-a[0]) if a[0] != 1 and b[0] != 1 else F(1)
        require(correction_rank(completion(a, b, field_t)) == field_min,
                'field attainment')
        cases[(field_min, dyadic_min)] += 1
    a, b = (F(0), F(1)), (F(4), F(1))
    rational = completion(a, b, F(3))
    require(rational == ((4, -3), (1, 0)) and determinant(rational) == 3
            and correction_rank(rational) == 1, 'rational gap witness')
    shapes = []
    for m, extra in product(range(1, 5), range(4)):
        n = 2*m+extra
        word = [(t, s, F(c)) for i in range(m)
                for t, s, c in [(i, m+i, -1), (m+i, i, 1), (i, m+i, 3)]]
        inverse = [(t, s, -c) for t, s, c in reversed(word)]
        p = matrix_word(n, word)
        rational = [[F(int(i == j)) for j in range(n)] for i in range(n)]
        for i in range(m):
            rational[i][i] = 4; rational[i][m+i] = -3
            rational[m+i][i] = 1; rational[m+i][m+i] = 0
        for matrix in (p, rational):
            require(all(matrix[j][i] == 4*int(j == i)+int(j == m+i)
                        and matrix[m+i][j] == int(j == i)
                        for i in range(m) for j in range(n)), 'family endpoint')
        require(correction_rank(p) == 2*m and correction_rank(rational) == m,
                'family rank gap')
        q = matrix_word(n, inverse)
        require(all(sum(p[i][k]*q[k][j] for k in range(n)) == int(i == j)
                    for i in range(n) for j in range(n)), 'inverse word')
        shapes.append([m, extra])
    modular_counts = {}
    for m, extra in [(1, 0), (1, 1), (1, 2), (2, 0)]:
        size, n, count = m+extra, 2*m+extra, 0
        for entries in product(range(3), repeat=size*size):
            jmatrix = [entries[i*size:(i+1)*size] for i in range(size)]
            if rank_mod_three(jmatrix) != size:
                continue
            p = [[0]*n for _ in range(n)]
            for i in range(m):
                p[i][i] = p[m+i][i] = 1
            rows = list(range(m))+list(range(2*m, n))
            for i, row in enumerate(rows):
                for j in range(size):
                    p[row][m+j] = jmatrix[i][j]
            require(rank_mod_three(p) == n, 'complete modular parameterization')
            require(rank_mod_three([[x-int(i == j) for j, x in enumerate(row)]
                                    for i, row in enumerate(p)]) >= 2*m,
                    'modular fixed-space floor')
            count += 1
        modular_counts[f'{m},{extra}'] = count
    rational = completion(a, b, F(3))
    word = [(0, 1, F(-1)), (1, 0, F(1)), (0, 1, F(3))]
    controls = [
        ('integer nonunit', a, b, rational),
        ('dropped dual', a, b, ((F(4), F(-9)), (F(1), F(-2)))),
        ('dropped primal', a, b, ((F(1), F(0)), (F(0), F(1)))),
        ('odd denominator', (F(-2), F(5)), (F(2), F(1)),
         ((F(2), F(-5, 3)), (F(1), F(-2, 3)))),
    ]
    for name, row, column, p in controls:
        try:
            validate(row, column, p)
        except ValueError:
            pass
        else:
            raise ValueError('accepted control: '+name)
    for bad in [((0, 0), (1, 0)), ((F(1, 3), 0), (3, 0))]:
        try:
            classify(*bad)
        except ValueError:
            pass
        else:
            raise ValueError('accepted invalid pair')
    result = {
        'status': 'PASS_DYADIC_CORRECTION_RANK_GAP',
        'literal_grid_matrices_examined': len(grid)**4,
        'literal_dyadic_invertible_matrices': literal_matrices,
        'normalized_integer_pairs': integer_pairs,
        'distinct_contracts': len(contracts),
        'field_and_dyadic_minimum_counts': {f'{x},{y}': count for (x, y), count in sorted(cases.items())},
        'strict_gap_witness': {'row': [0, 1], 'column': [4, 1],
                              'rational_matrix': [[4, -3], [1, 0]],
                              'rational_determinant': 3, 'field_minimum': 1,
                              'dyadic_matrix': [[4, -1], [1, 0]],
                              'dyadic_determinant': 1, 'dyadic_minimum': 2},
        'literal_add_word': [[t, s, str(c)] for t, s, c in word],
        'family_pair_and_extra_shapes': shapes,
        'complete_modular_completion_counts': modular_counts,
        'rejected_controls': [name for name, *_ in controls]+['unnormalized pair', 'nondyadic pair'],
    }
    require(json.loads((ROOT/'RESULT.json').read_text()) == result, 'retained receipt')
    return result


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True, indent=2))
