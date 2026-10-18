#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent, exhaustive finite replay; imports no discovery code.

Discovery enumerates RREF bases and tests odd residual vectors. This replay
generates subspaces by closure, tests Gram ranks, and explicitly constructs
orthonormal bases of the four residuals. All arithmetic is exact.
"""
from collections import Counter
from functools import cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
BASE = '66849e1475c930fd7732b1a0067ffee7e1e95f60'
SEED = 35


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pairing(x, y):
    # Intentionally avoid the discovery implementation's popcount expression.
    parity = 0
    while x and y:
        parity ^= (x & 1) & (y & 1)
        x >>= 1
        y >>= 1
    return parity


def closure(generators):
    result = {0}
    for g in generators:
        result.update(x ^ g for x in tuple(result))
    return frozenset(result)


def all_spaces(n):
    """Generate every subspace by adjoining one vector to smaller spaces."""
    level = {frozenset({0})}
    result = set(level)
    for _ in range(n):
        following = set()
        for v in level:
            for x in range(1, 1 << n):
                if x not in v:
                    following.add(v | frozenset(y ^ x for y in v))
        result.update(following)
        level = following
    return result


def dimension(space):
    require(len(space) > 0 and len(space) & (len(space) - 1) == 0,
            'space size is not a power of two')
    return len(space).bit_length() - 1


def basis(space):
    generators = []
    generated = frozenset({0})
    for x in sorted(space):
        if x not in generated:
            generators.append(x)
            generated = closure(generators)
    require(generated == space, 'input is not a subspace')
    return generators


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            lead = row.bit_length() - 1
            if lead in pivots:
                row ^= pivots[lead]
            else:
                pivots[lead] = row
                break
    return len(pivots)


def nondegenerate(space):
    b = basis(space)
    gram = [sum(pairing(x, y) << j for j, y in enumerate(b)) for x in b]
    return rank(gram) == len(b)


def perpendicular(space, n):
    b = basis(space)
    return frozenset(x for x in range(1 << n) if not any(pairing(x, y) for y in b))


@cache
def orthonormal_basis(space):
    """Complete backtracking; None means no orthonormal basis exists."""
    if space == frozenset({0}):
        return ()
    for x in sorted(space):
        if not pairing(x, x):
            continue
        rest = frozenset(y for y in space if not pairing(x, y))
        tail = orthonormal_basis(rest)
        if tail is not None:
            answer = (x,) + tail
            require(closure(answer) == space, 'basis does not span residual')
            require(all(pairing(a, b) == (i == j)
                        for i, a in enumerate(answer) for j, b in enumerate(answer)),
                    'constructed basis is not orthonormal')
            return answer
    return None


def edge_basis(space, label):
    return orthonormal_basis(frozenset(x for x in space if not pairing(x, label)))


def coefficient(s, t):
    intersection = sum((s >> j & 1) * (t >> j & 1)
                       for j in range(max(s, t).bit_length()))
    return (1, 0, -1, 0)[intersection]


def scalar_matrix(a, b):
    return [[coefficient(s, t) for s in a] for t in b]


def scalar_rank_one(matrix):
    return all(x for row in matrix for x in row) and (
        matrix[0][0] * matrix[1][1] == matrix[0][1] * matrix[1][0])


def replay():
    n = 2 * (2 + SEED % 2)  # Seed 35 selects h=6 from the two small even domains.
    labels = [x for x in range(1 << n) if sum(int(b) for b in bin(x)[2:]) == 3]
    pairs = list(combinations(labels, 2))
    admissible = {(a, b): set() for a in pairs for b in pairs
                  if not any(pairing(s, t) for s in a for t in b)}
    separating = {r: set() for r in admissible}
    spaces = all_spaces(n)
    by_dim = Counter(dimension(u) for u in spaces)
    # Independent closed enumeration counts: the Gaussian binomial coefficients.
    expected_dims = [1, 63, 651, 1395, 651, 63, 1]
    require([by_dim[i] for i in range(n + 1)] == expected_dims,
            'subspace coverage differs from Gaussian binomial counts')
    good_frames = 0
    for u in spaces:
        if not nondegenerate(u):
            continue
        good_frames += 1
        v = perpendicular(u, n)
        ss = [s for s in labels if s in u]
        tt = [t for t in labels if t in v]
        d = dimension(u)
        for a in combinations(ss, 2):
            for b in combinations(tt, 2):
                separating[a, b].add(d)
        ss = [s for s in ss if edge_basis(u, s) is not None]
        tt = [t for t in tt if edge_basis(v, t) is not None]
        for a in combinations(ss, 2):
            for b in combinations(tt, 2):
                admissible[a, b].add(d)
    groups = Counter()
    records = []
    for (a, b), dims in admissible.items():
        scalar = bool(scalar_rank_one(scalar_matrix(a, b)))
        common = len(closure(a) & closure(b)) > 1
        key = (pairing(*a), pairing(*b), scalar, common,
               tuple(sorted(separating[a, b])), tuple(sorted(dims)))
        groups[key] += 1
        records.append([list(a), list(b), scalar, common,
                        sorted(separating[a, b]), sorted(dims)])
    payload = json.dumps(sorted(records), separators=(',', ':')).encode('ascii')
    return {
        'schema': 'complex-parity-frame-census-v1', 'base_commit': BASE,
        'assignment_seed': SEED, 'ambient_dimension': n, 'labels': labels,
        'pair_convention': 'unordered within each side; source and target sides distinguished',
        'subspaces': {'all': len(spaces), 'nondegenerate': good_frames},
        'orthogonal_rectangles': len(admissible),
        'scalar_rank_one_rectangles': sum(v for k, v in groups.items() if k[2]),
        'admissible_rank_one_rectangles': sum(v for k, v in groups.items() if k[2] and k[-1]),
        'classes': [dict(source_pair_dot=k[0], target_pair_dot=k[1],
                         scalar_rank_one=k[2], common_span_nonzero=k[3],
                         separating_dimensions=list(k[4]), admissible_dimensions=list(k[5]),
                         count=v) for k, v in sorted(groups.items())],
        'all_rectangle_records_sha256': sha256(payload).hexdigest(),
        'coverage': 'All 2825 subspaces and all ordered pairs of unordered triple pairs in F2^6; no timeout or sampling.',
        'kappa_claim': None,
    }


def frame_ok(n, sources, targets, generators, *, require_residuals=True):
    u = closure(generators)
    if not nondegenerate(u):
        return False
    v = perpendicular(u, n)
    if not set(sources) <= u or not set(targets) <= v:
        return False
    if not all(pairing(x, x) for x in (*sources, *targets)):
        return False
    return not require_residuals or (
        all(edge_basis(u, s) is not None for s in sources)
        and all(edge_basis(v, t) is not None for t in targets))


def controls():
    # Genuine scalar rank-one map and no common-span obstruction.
    a, b = (7, 25), (11, 19)
    require(scalar_matrix(a, b) == [[-1, -1], [-1, -1]], 'wrong kernel fixture')
    require(closure(a) & closure(b) == {0}, 'positive fixture has common span')
    u3, u4 = (25, 26, 4), (25, 26, 4, 32)
    require(frame_ok(6, a, b, u4), 'dimension-four completion rejected')
    require(frame_ok(6, a, b, u3, require_residuals=False), 'relaxed control is not separating')
    require(not frame_ok(6, a, b, u3), 'alternating incoming residual accepted')
    residual = frozenset(x for x in closure(u3) if not pairing(x, 7))
    require(residual == frozenset({0, 3, 29, 30}), 'unexpected residual witness')
    require(all(not pairing(x, x) for x in residual), 'negative residual is not alternating')
    require(not frame_ok(6, a, b, a), 'degenerate source-span frame accepted')
    require(not frame_ok(6, a, (11, 7), u4), 'source/target nonorthogonality accepted')
    # The five-point obstruction, embedded in six coordinates.
    require(closure((7, 25)) & closure((11, 21)) == {0, 30}, 'missing common radical')
    # Rank-one scalar arithmetic must be checked independently of binary geometry.
    require(not scalar_rank_one([[1, -1], [-1, -1]]), 'corrupted scalar sign accepted')
    require(not scalar_rank_one(scalar_matrix((7, 25), (11, 38))),
            'rank-two rectangle mistaken for one shared sum')
    # A sharp dimension-eight control for arbitrary norm-one labels, NOT four triples.
    require(frame_ok(8, (1, 7), (16, 112), (1, 2, 4, 8)), 'sharp eight-dimensional control failed')
    # A triple-only positive control in ten dimensions, with reproducible seed permutation.
    permutation = list(range(10))
    random.Random(SEED).shuffle(permutation)
    def permute(x):
        return sum(((x >> i) & 1) << permutation[i] for i in range(10))
    aa = tuple(map(permute, (7, 25)))
    bb = tuple(map(permute, (224, 800)))
    uu = tuple(map(permute, (7, 25, 4, 16)))
    require(frame_ok(10, aa, bb, uu), 'ten-dimensional triple control failed')
    require(pairing(*aa) == pairing(*bb) == 1, 'higher control lost degenerate pairs')
    require(scalar_rank_one(scalar_matrix(aa, bb)), 'higher control is not scalar-shareable')
    return {'dimension_four_basis': list(u4), 'forbidden_dimension_three_basis': list(u3),
            'alternating_residual': sorted(residual), 'ten_dimensional_permutation': permutation,
            'ten_dimensional_sources': aa, 'ten_dimensional_targets': bb,
            'ten_dimensional_basis': uu}


def main():
    expected_path = Path(sys.argv[1]) if len(sys.argv) == 2 else HERE / 'CERTIFICATE.json'
    require(len(sys.argv) <= 2, 'usage: check.py [certificate.json]')
    expected = json.loads(expected_path.read_text(encoding='utf-8'))
    actual = replay()
    require(actual == expected, 'certificate differs from independent exhaustive replay')
    witnesses = controls()
    print('PASS_COMPLEX_PARITY_FRAME_CENSUS subspaces=2825 rectangles=1890 '
          'rank_one=1170 admissible=900 controls=PASS')
    print(json.dumps(witnesses, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'FAIL_COMPLEX_PARITY_FRAME_CENSUS: {error}', file=sys.stderr)
        sys.exit(1)
