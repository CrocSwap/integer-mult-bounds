"""Exact port incidence and native translation-polynomial calculations."""
from fractions import Fraction as Q
from itertools import combinations


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return (a & b).bit_count() & 1


def dimensions(blocks, labels):
    need(sorted(i for group in blocks for i in group) == list(range(len(labels))),
         'port partition')
    dims = [0] * len(labels)
    for group in blocks:
        vectors = [labels[i] for i in group]
        need(all(dot(a, b) == int(i == j) for i, a in enumerate(vectors)
                 for j, b in enumerate(vectors)), 'orthonormal port block')
        # Orthonormal columns are independent over F2.
        for i in group:
            dims[i] = len(group)
    return dims


def coverage(dims, dimension=73, pairs=4, stages=9):
    need(dims and all(type(d) is int and 1 <= d < dimension for d in dims),
         'port dimensions')
    multiplicity = 2 * pairs
    families = multiplicity * len(dims)
    unpaid = multiplicity * sum(dims)
    return {'families': families, 'family_multiplicity': multiplicity,
            'unpaid_per_replica': unpaid,
            'pending_per_replica': dimension * families - unpaid,
            'weighted_unpaid': Q(sum(dims), len(dims)),
            'pending_per_call': Q(dimension * families - unpaid, stages)}


def require_uniform(dims, declared):
    need(all(d == declared for d in dims), 'uniform unpaid premise is not supplied')


def times(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def kernel(vectors):
    """Numerators of product C_q on delta_0, denominator 2**len(vectors)."""
    result = {}
    for mask in range(1 << len(vectors)):
        address, coefficient = 0, (1, 0)
        for i, vector in enumerate(vectors):
            chosen = mask >> i & 1
            if chosen:
                address ^= vector
            coefficient = times(coefficient, (1, -1) if chosen else (1, 1))
        old = result.get(address, (0, 0))
        result[address] = (old[0]+coefficient[0], old[1]+coefficient[1])
    return {x: z for x, z in result.items() if z != (0, 0)}


def compose(left, right):
    result = {}
    for x, a in left.items():
        for y, b in right.items():
            z = times(a, b)
            old = result.get(x ^ y, (0, 0))
            result[x ^ y] = old[0]+z[0], old[1]+z[1]
    return {x: z for x, z in result.items() if z != (0, 0)}


def comparison_completion(pair, labels):
    """One five-frame for a boundary comparison, not a supplied physical repair."""
    available = [i for i in range(len(labels)) if i not in pair
                 and all(dot(labels[i], labels[j]) == 0 for j in pair)]
    for extra in combinations(available, 3):
        if all(dot(labels[i], labels[j]) == 0 for i, j in combinations(extra, 2)):
            return pair + list(extra)
    raise ValueError('no diagnostic five-frame completion')


def endpoint_witness(pair, labels):
    completed = comparison_completion(pair, labels)
    old_vectors, new_vectors = [labels[i] for i in pair], [labels[i] for i in completed]
    old, new = kernel(old_vectors), kernel(new_vectors)
    need(len(old) == 4 and len(new) == 32, 'native support sizes')
    outside = labels[completed[2]]
    need(outside not in old and new[outside] != (0, 0), 'missing native coefficient')
    old_shift = 0
    new_shift = 0
    for x in old_vectors:
        old_shift ^= x
    for x in new_vectors:
        new_shift ^= x
    need(compose(old, old) == {old_shift: (16, 0)}, 'literal squared endpoint')
    need(compose(new, new) == {new_shift: (1024, 0)}, 'comparison squared endpoint')
    need(old_shift != new_shift, 'completion changes aggregate correction')
    # Translate the kernels to each basis column; exact linearity then covers
    # arbitrary complex dirty amplitudes and unchanged spectator tensor factors.
    for start in range(512):
        actual = {x ^ start: z for x, z in old.items()}
        required = {x ^ start: z for x, z in new.items()}
        need((outside ^ start) not in actual and required[outside ^ start] != (0, 0),
             'native basis-column mismatch')
        need((start ^ old_shift) != (start ^ new_shift), 'squared endpoint mismatch')
    return {'residual_ports': pair, 'residual_labels': old_vectors,
            'comparison_completion_ports': completed, 'comparison_labels': new_vectors,
            'literal_support': len(old), 'comparison_support': len(new),
            'witness_column': 0, 'witness_row': outside,
            'literal_coefficient': [0, 0], 'comparison_numerator': list(new[outside]),
            'comparison_denominator': 32,
            'literal_shift': old_shift, 'comparison_shift': new_shift,
            'different_columns': 512,
            'completion_status': 'diagnostic comparison only; no physical implementation or zero-cost repair'}
