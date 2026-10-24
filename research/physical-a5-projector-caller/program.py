"""Offline fixed-control compilation; no runtime data or width enters here."""
from itertools import product


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def basis_word(u, v):
    if not (1 <= u < 8 and 1 <= v < 8 and (u & v).bit_count() % 2 == 1):
        raise ValueError('rank-one idempotent')
    rows = [v]
    for row in range(1, 8):
        if (u & row).bit_count() % 2 == 0 and rank([*rows, row]) > len(rows):
            rows.append(row)
    if len(rows) != 3:
        raise RuntimeError('basis completion')
    original = tuple(rows)
    reduction = []
    for j in range(3):
        pivot = next(i for i in range(j, 3) if (rows[i] >> j) & 1)
        if pivot != j:
            for a, b in ((pivot, j), (j, pivot), (pivot, j)):
                rows[b] ^= rows[a]
                reduction.append((a, b))
        for i in range(3):
            if i != j and ((rows[i] >> j) & 1):
                rows[i] ^= rows[j]
                reduction.append((j, i))
    if rows != [1, 2, 4]:
        raise RuntimeError('row reduction')
    return original, tuple(reversed(reduction))


def compile_program(source):
    permutations = {}
    for label, matrix in [('x', source.X), ('y', source.Y)]:
        push = tuple(source.address_action(matrix, i, 2) for i in range(256))
        if sorted(push) != list(range(256)):
            raise RuntimeError('source permutation')
        inverse = [0] * 256
        for i, j in enumerate(push):
            inverse[j] = i
        permutations[label] = tuple(inverse)
    bases = {(u, v): basis_word(u, v) for u, v in product(range(1, 8), repeat=2)
             if (u & v).bit_count() % 2}
    return permutations, bases


def caller(machine, permutations, bases):
    # PR4089 algebraic product E00(x) E00(y) E11(y) E11(x).
    # Column-data execution is rightmost first.
    for u, v, label in ((2, 2, 'x'), (2, 2, 'y'), (1, 1, 'y'), (1, 1, 'x')):
        machine.projector(bases[u, v][1], permutations[label])
