#!/usr/bin/env python3
"""Check formal-group spans for kind A removal.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def apply(matrix, value):
    result = 0
    while value:
        bit = value & -value
        result ^= matrix[bit.bit_length()-1]
        value ^= bit
    return result


def product(left, right):
    return tuple(apply(left, column) for column in right)


def identity(width):
    return tuple(1 << i for i in range(width))


def inverse(matrix):
    size = len(matrix)
    rows = [sum(((matrix[j] >> i) & 1) << j for j in range(size)) | (1 << (size+i))
            for i in range(size)]
    for j in range(size):
        pivot = next(i for i in range(j, size) if rows[i] & (1 << j))
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(size):
            if i != j and rows[i] & (1 << j):
                rows[i] ^= rows[j]
    return tuple(sum(((rows[i] >> (size+j)) & 1) << i for i in range(size))
                 for j in range(size))


def free(matrix):
    m = len(matrix)//2
    return all(not (column & ((1 << m)-1)) for column in matrix[m:])


def pairing(x, y, m):
    mask = (1 << m)-1
    return (((x & mask) & (y >> m)) ^ ((y & mask) & (x >> m))).bit_count() & 1


def transvection(m, normal):
    return tuple((1 << i) ^ (normal if pairing(1 << i, normal, m) else 0)
                 for i in range(2*m))


def level(matrix):
    m = len(matrix)//2
    values = {0}
    for column in matrix[m:]:
        values |= {v ^ (column & ((1 << m)-1)) for v in values}
    return len(values).bit_length()-1


def general_linear(m):
    def extend(columns, space):
        if len(columns) == m:
            yield tuple(columns)
        else:
            for v in range(1, 1 << m):
                if v not in space:
                    yield from extend(columns+[v], space | {x ^ v for x in space})
    return tuple(extend([], {0}))


def parabolic(m):
    positions = tuple((i, j) for i in range(m) for j in range(i, m))
    result = []
    for a in general_linear(m):
        ai = inverse(a)
        b = tuple(sum(((ai[i] >> j) & 1) << i for i in range(m)) for j in range(m))
        for bits in range(1 << len(positions)):
            s = [0]*m
            for k, (i, j) in enumerate(positions):
                if bits & (1 << k):
                    s[j] |= 1 << i
                    s[i] |= 1 << j
            matrix = tuple(a[i] | (apply(b, s[i]) << m) for i in range(m)) + tuple(x << m for x in b)
            require(free(matrix), 'generated element is not free')
            require(all(pairing(matrix[i], matrix[j], m) == int(abs(i-j) == m)
                        for i in range(2*m) for j in range(2*m)), 'symplectic basis pairing')
            result.append(matrix)
    require(len(set(result)) == len(result), 'duplicate free element')
    return tuple(result)


def right_orbit(start, gamma):
    result = [start]
    current = product(start, gamma)
    while current != start:
        require(current not in result, 'orbit entered a different cycle')
        result.append(current)
        current = product(current, gamma)
    return result


def contains(columns, target):
    pivots = {}
    for vector in columns:
        row = [Q(v) for v in vector]
        for i in range(len(row)):
            if not row[i]:
                continue
            if i not in pivots:
                scale = row[i]
                pivots[i] = [v/scale for v in row]
                break
            scale = row[i]
            row = [a-scale*b for a, b in zip(row, pivots[i], strict=True)]
    row = [Q(v) for v in target]
    for i in sorted(pivots):
        scale = row[i]
        row = [a-scale*b for a, b in zip(row, pivots[i], strict=True)]
    return not any(row)


def columns_on_cycle(cycle, c, singleton, edge, omitted=None):
    size = len(cycle)
    columns = []
    for j, g in enumerate(cycle):
        if singleton(g):
            row = [Q(0)]*size
            row[j] = 1
            columns.append(row)
        if edge(g) and g != omitted:
            row = [Q(0)]*size
            row[j] = 1
            row[(j+1) % size] += c
            columns.append(row)
    return columns


def removal(cycle, c, first, shared, last, literal=None, keep_identity=False):
    if literal is None:
        singleton = lambda g: any(free(h) for h in
                                  (g, product(g, first), product(last, g), product(product(last, g), first)))
        old = lambda g: free(product(g, shared))
        paid = lambda g: free(product(product(last, g), shared))
    else:
        singles, old_starts, paid_starts = literal
        singleton = lambda g: g in singles
        old = lambda g: g in old_starts
        paid = lambda g: g in paid_starts
    cols = columns_on_cycle(cycle, c, singleton, paid)
    cols += columns_on_cycle(cycle, c, lambda g: False, old,
                             omitted=None if keep_identity else shared)
    target = [Q(0)]*len(cycle)
    target[0] = 1
    target[1 % len(cycle)] += c
    return contains(cols, target)


def literal_sets(group, first, shared, last):
    singles = set(group) | {product(p, first) for p in group}
    singles |= {product(last, p) for p in tuple(singles)}
    return singles, {product(p, shared) for p in group}, {product(product(last, p), shared) for p in group}


def census():
    m = 3
    group = parabolic(m)
    require(len(group) == 10752, 'complete free group cardinality')
    first, shared, last = (transvection(m, 1 << i) for i in range(3))
    literal = literal_sets(group, first, shared, last)
    require(level(product(shared, first)) == level(product(last, shared)) == 2, 'call premises')
    coefficients = (Q(1), Q(-1), Q(2), Q(1, 2))
    counts = {str(c): Counter() for c in coefficients}
    all_outcomes = {str(c): Counter() for c in coefficients}
    order_histogram = Counter()
    singular_relations = 0
    for gamma in group:
        cycle = right_orbit(shared, gamma)
        n = len(cycle)
        order_histogram[n] += 1
        same = free(product(product(shared, gamma), shared))
        extra = product(product(shared, gamma), first)
        plain = gamma == identity(2*m) or free(extra)
        for c in coefficients:
            got = removal(cycle, c, first, shared, last, literal)
            require(got == (same and (-c)**n == 1), 'finite span differs from theorem')
            all_outcomes[str(c)]['removable' if got else 'not removable'] += 1
            if not plain:
                counts[str(c)]['removable' if got else 'not removable'] += 1
            if got:
                relation = [Q(0)]*n
                for j in range(n):
                    relation[j] += (-c)**j
                    relation[(j+1) % n] += c*(-c)**j
                require(not any(relation), 'explicit cyclic deletion relation')
                singular_relations += 1
    require([counts[str(c)]['removable'] for c in coefficients] == [639, 767, 0, 0], 'source-domain counts')
    require(all(sum(row.values()) == 9983 for row in counts.values()), 'source nonplain domain')
    return {'free_elements': len(group), 'coefficient_contracts': len(group)*len(coefficients),
            'nonplain_elements': 9983, 'nonplain_outcomes': counts, 'all_outcomes': all_outcomes,
            'order_histogram': {str(k): v for k, v in sorted(order_histogram.items())},
            'explicit_singular_relations': singular_relations}, (first, shared, last, literal)


def axis_permutation(axes):
    m = len(axes)
    return tuple(1 << (axis+shift) for shift in (0, m) for axis in axes)


def wider_cases():
    cases = 0
    counts = Counter()
    for m in (4, 5, 6):
        first, shared = (transvection(m, 1 << i) for i in range(2))
        gammas = [transvection(m, 1 << (m+1)), transvection(m, 1 << (m+3)),
                  axis_permutation(tuple([0, 2, 1]+list(range(3, m))))]
        if m == 6:
            gammas.append(axis_permutation((0, 1, 2, 4, 5, 3)))
        for normal in (1 << 2, (1 << 2) | (1 << m), (1 << 2) | (1 << (m+2))):
            last = transvection(m, normal)
            require(level(product(last, shared)) == 2, 'wider removing call')
            for gamma in gammas:
                require(free(gamma), 'wider free element')
                cycle = right_orbit(shared, gamma)
                same = free(product(product(shared, gamma), shared))
                for c in (Q(1), Q(-1), Q(2), Q(1, 2), Q(-2, 3)):
                    got = removal(cycle, c, first, shared, last)
                    require(got == (same and (-c)**len(cycle) == 1), 'wider literal membership')
                    counts['removable' if got else 'not removable'] += 1
                    cases += 1
    return {'contracts': cases, 'outcomes': counts}


def controls(context):
    first, shared, last, literal = context
    gamma = transvection(3, 1 << 4)
    cycle = right_orbit(shared, gamma)
    require(not free(product(product(shared, gamma), shared)), 'control must have distinct frames')
    require(not removal(cycle, Q(1), first, shared, last, literal), 'valid call control')
    require(removal(cycle, Q(1), first, shared, last, literal, True), 'identity-preparation control')
    bad_calls = []
    for normal in range(1, 64):
        if not normal & 7:
            continue
        candidate = transvection(3, normal)
        if level(product(candidate, shared)) == 1 and removal(cycle, Q(1), first, shared, candidate):
            bad_calls.append(normal)
    require(bad_calls == [18, 26, 50, 58], 'level-one boundary counterexamples')
    same_gamma = transvection(3, 1 << 5)
    same_cycle = right_orbit(shared, same_gamma)
    require(removal(same_cycle, Q(1), first, shared, last, literal), 'singular positive control')
    require(not removal(same_cycle, Q(2), first, shared, last, literal), 'nonsingular coefficient control')
    require(not removal(cycle, Q(0), first, shared, last, literal), 'zero coefficient is outside theorem')
    return {'distinct_frame_gamma': list(gamma), 'inadmissible_removing_normals': bad_calls,
            'controls': 5}


def verify():
    data, context = census()
    result = {'status': 'PASS_KIND_A_REMOVABILITY_COSET', 'three_bit_census': data,
              'wider_cases': wider_cases(), 'boundary_controls': controls(context)}
    require(json.loads((ROOT/'RESULT.json').read_text()) == result, 'retained receipt')
    return result


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
