"""Literal GF(2) polynomial matrices, independently of the GF(16) search.

Apache-2.0. Cinna Davis, with substantial OpenAI Codex assistance.
"""
from collections import Counter

EVEN = sum(1 << i for i in range(0, 256, 2))


def query(poly):
    """Multiply by the formal involution Q, without setting Q = 1."""
    return ((poly & EVEN) << 1) | ((poly & (EVEN << 1)) >> 1)


def rank(rows):
    basis = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def gate_inventory():
    """All rank-one nilpotents and their rank-two projector extensions."""
    full, thin = [], []
    for u in range(1, 16):
        for v in range(1, 16):
            if (u & v).bit_count() % 2:
                continue
            nilpotent = tuple(v if u >> i & 1 else 0 for i in range(4))
            thin.append(((0,) * 4, nilpotent))
            seen = set()
            for a in range(1, 16):
                if not (v & a).bit_count() % 2:
                    continue
                for b in range(1, 16):
                    if not (u & b).bit_count() % 2 or (a & b).bit_count() % 2:
                        continue
                    projector = tuple((b if u >> i & 1 else 0) ^
                                      (v if a >> i & 1 else 0) for i in range(4))
                    if projector not in seen:
                        seen.add(projector)
                        full.append((projector, nilpotent))
    return full, thin


FULL, THIN = gate_inventory()


def identity():
    return [[int(i == j) for j in range(4)] for i in range(4)]


def literal(mask, ids):
    """Each bit is a monomial Q^q product(D_s); no D is specialized."""
    matrix = identity()
    for stage, gate_id in enumerate(ids):
        thick = bool(mask >> stage & 1)
        projector, nilpotent = (FULL if thick else THIN)[gate_id]
        sums = [[0] * 4 for _ in range(16)]
        for subset in range(1, 16):
            low = (subset & -subset).bit_length() - 1
            sums[subset] = [a ^ b for a, b in
                            zip(sums[subset & (subset - 1)], matrix[low])]
        changed = [row[:] for row in matrix]
        for i in range(4):
            for j in range(4):
                p = sums[projector[i]][j]
                n = query(sums[nilpotent[i]][j])
                if thick:
                    shift = 1 << (stage + 1)
                    changed[i][j] ^= p ^ (p << shift) ^ (n << shift)
                else:
                    changed[i][j] ^= n
        matrix = changed
    return matrix


def coefficients(matrix):
    result = {}
    groups = {g for row in matrix for poly in row
              for g in range(poly.bit_length()) if poly >> g & 1}
    for g in groups:
        result[g] = [sum(((matrix[i][j] >> g) & 1) << j for j in range(4))
                     for i in range(4)]
    return result


def stats(matrix):
    coeff = coefficients(matrix)
    return {
        'central_query_on_every_output': all(g & 1 for g in coeff),
        'coefficient_rank_sum': sum(rank(rows) for rows in coeff.values()),
        'ranks': dict(sorted((g, rank(rows)) for g, rows in coeff.items())),
    }


def elementary(source, destination):
    nilpotent = tuple((1 << source) if i == destination else 0 for i in range(4))
    projector = tuple((1 << i) if i in (source, destination) else 0 for i in range(4))
    return FULL.index((projector, nilpotent))


def multiply_binary(a, b):
    return [sum(((sum(((row >> k) & 1) * ((b[k] >> j) & 1)
                       for k in range(4))) % 2) << j for j in range(4)) for row in a]
