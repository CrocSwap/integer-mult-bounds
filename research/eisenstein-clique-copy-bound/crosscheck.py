#!/usr/bin/env python3
"""Independent arithmetic cross-check of the replayed certificate.

No geometry/verifier code is imported. Integer root generators are used
directly. Modular ranks LOWER-bound rational ranks for the primal check;
Fraction elimination certifies exact costs for the dual. Run verify.py too:
it supplies the geometry, enumeration completeness, and full receipt binding.

Jonathan Lam, with substantial OpenAI Codex assistance; Apache-2.0.
"""

from fractions import Fraction
import json
from pathlib import Path


def check(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def rank(rows, prime=None):
    if not rows:
        return 0
    matrix = [[x % prime for x in row] if prime else list(map(Fraction, row))
              for row in rows]
    result = 0
    for column in range(len(matrix[0])):
        pivot = next((i for i in range(result, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[result], matrix[pivot] = matrix[pivot], matrix[result]
        inverse = (pow(matrix[result][column], prime - 2, prime)
                   if prime else 1 / matrix[result][column])
        matrix[result] = [(x * inverse) % prime if prime else x * inverse
                          for x in matrix[result]]
        for i in range(result + 1, len(matrix)):
            coefficient = matrix[i][column]
            matrix[i] = [(x - coefficient * y) % prime if prime else x - coefficient * y
                         for x, y in zip(matrix[i], matrix[result])]
        result += 1
        if result == len(matrix):
            break
    return result


def main():
    certificate = json.loads(Path(__file__).with_name('certificate.json').read_text())
    roots = certificate['geometry']['representatives']
    images = certificate['geometry']['J_images']
    flats = certificate['geometry']['flats']
    cliques = certificate['primal']['maximum_cliques']
    bases = [[vector for i in flat['generators'] for vector in (roots[i], images[i])]
             for flat in flats]
    check(len(flats) == 772, 'flat count')
    for basis, flat in zip(bases, flats):
        check(rank(basis, 101) == 2 * flat['rank'], 'modular generator rank')
    adjacent = [sum(1 << k for k in range(40) if i != k and
                    (dot(roots[i], roots[k]) or dot(roots[i], images[k])))
                for i in range(40)]
    check(adjacent == certificate['geometry']['nonorthogonality_masks'], 'adjacency')
    check(len(cliques) == len(set(cliques)) == 2880, 'clique count')
    for clique in cliques:
        check(clique.bit_count() == 7 and all(not ((clique ^ (1 << i)) & ~adjacent[i])
              for i in range(40) if clique >> i & 1), 'clique admission')
    hits = [sum(1 << i for i, clique in enumerate(cliques) if clique & flat['mask'])
            for flat in flats]
    count = 0
    for i, (basis, flat) in enumerate(zip(bases, flats)):
        for k in range(i + 1):
            gram = [[dot(x, y) for y in bases[k]] for x in basis]
            # Integer minors nonzero mod 101 are nonzero over Q. No equality
            # of the two ranks is assumed or needed in this inequality.
            modular_rank = rank(gram, 101)
            lhs = (24 * (flat['mask'] & flats[k]['mask']).bit_count()
                   + (hits[i] & hits[k]).bit_count())
            check(2 * lhs <= 960 * modular_rank, 'modular primal bound')
            count += 1
    check(count == 298378, 'complete primal pair count')
    lookup = {flat['mask']: basis for flat, basis in zip(flats, bases)}
    dual = certificate['dual']['flat_pairs']
    check(len(dual) == 240, 'dual count')
    for left, right in dual:
        check(rank([[dot(x, y) for y in lookup[right]] for x in lookup[left]]) == 4,
              'exact dual pair cost')
    full = lookup[(1 << 40) - 1]
    check(rank([[dot(x, y) for y in full] for x in full]) == 8, 'exact full-pair cost')
    print('PASS_EISENSTEIN_CROSSCHECK: 298378 modular primal bounds; 241 exact dual costs')


if __name__ == '__main__':
    main()
