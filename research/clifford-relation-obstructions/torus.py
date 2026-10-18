"""Exact torus equations on one Boolean support; no general Groebner search."""
from fractions import Fraction as Q
from itertools import product, permutations

from model import Engine, generic_paths, coefficient_records


def equations(program, selection):
    ring = Engine()
    rows, blocks = generic_paths(ring, program, 3)
    records, _ = coefficient_records(ring, rows)
    nonzero = [9*k+i for k, block in enumerate(selection['entry_support']) for i, v in enumerate(block) if v]
    allowed = sum(1 << i for i in nonzero)
    equations, equations_seen = [], set()
    for record in records:
        if record['frame'] == selection['frames'][record['column']]:
            continue
        terms = [(mask, value) for mask, value in record['poly'].items() if not mask & ~allowed]
        if not terms:
            continue
        assert len(terms) != 1, 'Boolean support should exclude lone unwanted terms'
        if len(terms) > 2:
            return {'status': 'nonbinomial', 'largest_active_sum': len(terms)}
        assert all(coefficient == 1 for _, coefficient in terms)
        a, b = terms[0][0], terms[1][0]
        row = tuple(((a >> i) & 1)-((b >> i) & 1) for i in nonzero)
        if next(v for v in row if v) < 0:
            row = tuple(-v for v in row)
        if row not in equations_seen:
            equations_seen.add(row)
            equations.append(list(row))
    return {'status': 'binomial', 'matrix': equations, 'rhs_parity': [1]*len(equations),
            'nonzero_entries': nonzero, 'blocks': blocks}


def diagonalize(matrix, rhs, n):
    """Unimodular row/column Euclidean operations, with an explicit trace.

    Divisibility between successive diagonal entries is unnecessary. Column
    operations give x_j=product(z_k**V[j,k]); row operations transform rhs.
    """
    a = [list(row) for row in matrix]
    b = list(rhs)
    v = [[int(i == j) for j in range(n)] for i in range(n)]
    m, steps, k = len(a), [], 0
    def swap_rows(i, j):
        a[i], a[j], b[i], b[j] = a[j], a[i], b[j], b[i]
        steps.append(['row_swap', i, j])
    def swap_columns(i, j):
        for row in a:
            row[i], row[j] = row[j], row[i]
        for row in v:
            row[i], row[j] = row[j], row[i]
        steps.append(['col_swap', i, j])
    while k < min(m, n):
        pivot = next(((i, j) for i in range(k, m) for j in range(k, n) if a[i][j]), None)
        if pivot is None:
            break
        if pivot[0] != k:
            swap_rows(k, pivot[0])
        if pivot[1] != k:
            swap_columns(k, pivot[1])
        while True:
            row = next((i for i in range(k+1, m) if a[i][k]), None)
            if row is not None:
                amount = -(a[row][k] // a[k][k])
                a[row] = [x+amount*y for x, y in zip(a[row], a[k])]
                b[row] += amount*b[k]
                steps.append(['row_add', row, k, amount])
                if a[row][k]:
                    swap_rows(k, row)
                continue
            col = next((j for j in range(k+1, n) if a[k][j]), None)
            if col is not None:
                amount = -(a[k][col] // a[k][k])
                for line in a:
                    line[col] += amount*line[k]
                for line in v:
                    line[col] += amount*line[k]
                steps.append(['col_add', col, k, amount])
                if a[k][col]:
                    swap_columns(k, col)
                continue
            break
        if a[k][k] < 0:
            a[k] = [-x for x in a[k]]
            b[k] = -b[k]
            steps.append(['row_negate', k])
        k += 1
    assert all(not a[i][j] for i in range(m) for j in range(n) if i != j or i >= k)
    return {'rank': k, 'diagonal': [a[i][i] for i in range(k)], 'rhs': b,
            'column_transform': v, 'steps': steps}


def multiply(a, b):
    out = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            exponent = tuple(x+y for x, y in zip(ea, eb))
            out[exponent] = out.get(exponent, 0)+ca*cb
    return {e: c for e, c in out.items() if c}


def determinant_product(equations, diagonal, signs):
    transform = diagonal['column_transform']
    rank = diagonal['rank']
    dimension = len(transform)-rank
    entries = {}
    for i, index in enumerate(equations['nonzero_entries']):
        phase = sum(transform[i][j]*signs[j] for j in range(rank)) % 2
        entries[index] = (tuple(transform[i][rank:]), (-1)**phase)
    total = {(0,)*dimension: 1}
    for k in range(equations['blocks']):
        determinant = {}
        for p in permutations(range(3)):
            factors = [entries.get(9*k+3*r+p[r]) for r in range(3)]
            if any(f is None for f in factors):
                continue
            parity = sum(p[i] > p[j] for i in range(3) for j in range(i+1, 3))
            exponent = tuple(sum(f[0][j] for f in factors) for j in range(dimension))
            coefficient = (-1)**parity
            for factor in factors:
                coefficient *= factor[1]
            determinant[exponent] = determinant.get(exponent, 0)+coefficient
        determinant = {e: c for e, c in determinant.items() if c}
        total = multiply(total, determinant)
        if not total:
            break
    return total, entries


def nonzero_point(polynomial, dimension):
    current, point = polynomial, []
    assert current
    for i in range(dimension):
        degree = max(e[i] for e in current)-min(e[i] for e in current)
        for value in range(1, degree+2):
            substituted = {}
            for exponent, coefficient in current.items():
                e = (*exponent[:i], 0, *exponent[i+1:])
                substituted[e] = substituted.get(e, 0)+coefficient*Q(value)**exponent[i]
            substituted = {e: c for e, c in substituted.items() if c}
            if substituted:
                point.append(value)
                current = substituted
                break
        else:
            raise AssertionError('a nonzero Laurent polynomial lost all degree+1 points')
    assert list(current) == [(0,)*dimension]
    return point


def complete(program, selection):
    eq = equations(program, selection)
    if eq['status'] != 'binomial':
        return None, eq
    diag = diagonalize(eq['matrix'], eq['rhs_parity'], len(eq['nonzero_entries']))
    result = {'equations': eq, 'diagonalization': diag, 'components': []}
    if any(b % 2 for b in diag['rhs'][diag['rank']:]):
        result['status'] = 'inconsistent_torus'
        return None, result
    roots = []
    for d, b in zip(diag['diagonal'], diag['rhs']):
        if d == 1:
            roots.append([b % 2])
        elif d == 2 and b % 2 == 0:
            roots.append([0, 1])
        else:
            result.update(status='nonreal_torsion_pending', pending_diagonal=d, pending_rhs=b)
            return None, result
    if sum(len(r) == 2 for r in roots) > 10:
        result['status'] = 'component_limit'
        return None, result
    for signs in product(*roots):
        polynomial, entries = determinant_product(eq, diag, signs)
        result['components'].append({'signs': list(signs), 'determinant_product_zero': not polynomial})
        if not polynomial:
            continue
        dimension = len(diag['column_transform'])-diag['rank']
        point = nonzero_point(polynomial, dimension)
        matrices = [[Q(0)]*9 for _ in range(eq['blocks'])]
        for index, (exponent, coefficient) in entries.items():
            value = Q(coefficient)
            for z, e in zip(point, exponent):
                value *= Q(z)**e
            assert value
            matrices[index//9][index % 9] = value
        word, k = [], 0
        for gate in program:
            if gate[0] == 'mix3':
                word.append(('mix3', *matrices[k]))
                k += 1
            else:
                word.append(gate)
        result.update(status='exact_rational_point', free_point=point, matrices=[[str(v) for v in m] for m in matrices])
        return tuple(word), result
    result['status'] = 'all_components_singular'
    return None, result
