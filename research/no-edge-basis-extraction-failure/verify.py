"""Exact checks for the no-edge basis-extraction counterexample.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Binary matrix and four-trial lift primitives are reused from PR7686.
See CREDITS.md for the exact source and mathematical predecessors.
"""

import itertools
import json
import math
from collections import Counter
from pathlib import Path


def require(value, message):
    if not value:
        raise ValueError(message)



def parity(value):
    return value.bit_count() & 1



def basis(values):
    pivots = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return tuple(pivots.values())



def span(values):
    result = [0]
    for value in basis(values):
        result += [old ^ value for old in result]
    return result



def outer(x, y, width):
    result = 0
    while x:
        bit = x & -x
        result |= y << ((bit.bit_length() - 1) * width)
        x ^= bit
    return result



def off(matrix, width):
    for i in range(width):
        matrix &= ~(1 << (i * width + i))
    return matrix



def patterns(pairs, width):
    return [off(outer(x, y, width), width) for x, y in pairs]



def lifts(pattern, width):
    """An off-diagonal one fixes all factor bits except two."""
    require(pattern != 0, 'zero pattern is outside the pool')
    i, j = divmod((pattern & -pattern).bit_length() - 1, width)
    require(i != j, 'diagonal pattern entry')
    x = sum(((pattern >> (r * width + j)) & 1) << r for r in range(width))
    y = (pattern >> (i * width)) & ((1 << width) - 1)
    result = []
    for xj, yi in itertools.product((0, 1), repeat=2):
        xx, yy = x | (xj << j), y | (yi << i)
        if parity(xx & yy) and off(outer(xx, yy, width), width) == pattern:
            result.append((xx, yy))
    return result



def pool(pattern_basis, width):
    return sorted(pair for pattern in span(pattern_basis) if pattern
                  for pair in lifts(pattern, width))



def orbit_irreducible(pairs):
    """Check all nonzero vectors for small fixtures by direct closure."""
    image_space = span(x for x, _ in pairs)
    n = len(basis(image_space))
    for value in image_space[1:]:
        vectors = basis([value])
        while True:
            expanded = basis((*vectors, *(x for x, y in pairs
                              if any(parity(y & v) for v in vectors))))
            if len(expanded) == len(vectors):
                break
            vectors = expanded
        if len(vectors) != n:
            return False
    return True


def replicate_vector(value, copies=3):
    mask = (1 << copies) - 1
    return sum(mask << (copies * i) for i in range(value.bit_length())
               if (value >> i) & 1)


def replicate_matrix(matrix, width, copies=3):
    result = 0
    for i in range(width):
        for j in range(width):
            if (matrix >> (i * width + j)) & 1:
                result ^= outer(replicate_vector(1 << i, copies),
                                replicate_vector(1 << j, copies), copies * width)
    return result


def multiply(left, right, width):
    result = 0
    mask = (1 << width) - 1
    for i in range(width):
        row = 0
        for j in range(width):
            if (left >> (i * width + j)) & 1:
                row ^= (right >> (j * width)) & mask
        result |= row << (i * width)
    return result


def all_subspaces(width):
    spaces = {frozenset({0})}
    frontier = list(spaces)
    while frontier:
        old = frontier.pop()
        for value in range(1, 1 << width):
            if value not in old:
                new = frozenset(old | {x ^ value for x in old})
                if new not in spaces:
                    spaces.add(new)
                    frontier.append(new)
    return sorted(spaces, key=lambda x: (len(x), sorted(x)))


def strong_incidence(pairs):
    for start in range(len(pairs)):
        reached = {start}
        while True:
            new = reached | {j for j, (_, y) in enumerate(pairs)
                             if any(parity(y & pairs[i][0]) for i in reached)}
            if new == reached:
                break
            reached = new
        if len(reached) != len(pairs):
            return False
    return True


def family(n):
    require(n >= 3, 'dimension at least three')
    small = [(1 << i, (1 << i) | (1 << ((i + 1) % n))) for i in range(n)]
    small.append((1, 1))
    return [(replicate_vector(x), replicate_vector(y)) for x, y in small]


def weight_formula(n):
    result = Counter()
    for j in range(n):
        for offset in (0, 6, 9, 15):
            result[15 * j + offset] += math.comb(n - 1, j)
    return result


def check_family(n):
    pairs = family(n)
    width = 3 * n
    ps = patterns(pairs, width)
    pattern_space = span(ps)
    require(len(basis(ps)) == n + 1, 'pattern dimension')
    require(Counter(p.bit_count() for p in pattern_space) == weight_formula(n), 'weight enumerator')
    require(min(p.bit_count() for p in pattern_space if p) == 6, 'minimum pattern weight')
    require(pool(ps, width) == sorted(pairs), 'complete pool')
    require(all(parity(x & y) for x, y in pairs), 'idempotence')
    require(len(basis(x for x, _ in pairs)) == n, 'joint image')
    restricted_rows = [sum(parity(y & replicate_vector(1 << i)) << i for i in range(n))
                       for _, y in pairs]
    require(len(basis(restricted_rows)) == n and strong_incidence(pairs), 'full irreducibility certificate')
    require(len(basis(restricted_rows[:-1])) == n - 1, 'cycle covector rank')
    require(len(basis(restricted_rows[1:])) == n, 'broken-cycle covector rank')

    cycle = pairs[:-1]
    kernel = replicate_vector((1 << n) - 1)
    require(all(parity(y & kernel) == 0 for _, y in cycle), 'cycle common kernel')
    broken = pairs[1:]
    line = replicate_vector(2)
    require(all(not parity(y & line) or x == line for x, y in broken), 'broken-cycle invariant line')
    require(parity(pairs[0][1] & line) and pairs[0][0] != line, 'extra cycle row breaks invariant line')
    require(parity(pairs[-1][1] & kernel), 'extra projector breaks common kernel')
    if n <= 8:
        require(orbit_irreducible(pairs), 'direct full orbit check')
        require(not orbit_irreducible(cycle), 'direct cycle orbit control')
        require(not orbit_irreducible(broken), 'direct broken-cycle orbit control')

    full_image_subsets = []
    for mask in range(1 << len(pairs)):
        subset = [p for i, p in enumerate(pairs) if (mask >> i) & 1]
        if len(basis(x for x, _ in subset)) == n:
            full_image_subsets.append(mask)
    expected = [(1 << n) - 1, ((1 << (n + 1)) - 1) ^ 1, (1 << (n + 1)) - 1]
    require(sorted(full_image_subsets) == sorted(expected), 'all full-image subcollections')
    return {'image_dimension': n, 'ambient_width': width, 'pattern_dimension': n + 1,
            'complete_pool_size': n + 1, 'patterns_checked': len(pattern_space) - 1,
            'all_subsets_checked': 1 << len(pairs), 'full_image_subsets': full_image_subsets,
            'cycle_kernel': kernel, 'broken_cycle_line': line,
            'cycle_covector_rank': n - 1, 'broken_cycle_covector_rank': n,
            'minimum_pattern_weight': 6, 'pairs': pairs,
            'weight_histogram': {str(k): v for k, v in sorted(weight_formula(n).items())}}


def compute():
    # Every matrix subspace of M_2(F2), including coordinate and nilpotent parts.
    matrix_spaces = all_subspaces(4)
    require(len(matrix_spaces) == 67, 'complete matrix-subspace count')
    original_idempotents = [(x, y) for x, y in itertools.product(range(1, 4), repeat=2)
                            if parity(x & y)]
    pool_total = 0
    dimensions = Counter()
    for space in matrix_spaces:
        matrices = basis(space)
        lifted_patterns = [off(replicate_matrix(a, 2), 6) for a in matrices]
        require(len(basis(lifted_patterns)) == len(matrices), 'replication preserves dimension')
        require(all(p.bit_count() >= 6 for p in span(lifted_patterns) if p), 'replication removes units')
        expected = sorted((replicate_vector(x), replicate_vector(y)) for x, y in original_idempotents
                          if outer(x, y, 2) in space)
        actual = pool(lifted_patterns, 6)
        require(actual == expected, 'replication retains the exact complete pool')
        pool_total += len(actual)
        dimensions[len(matrices)] += 1
    product_checks = 0
    for a, b in itertools.product(range(16), repeat=2):
        require(multiply(replicate_matrix(a, 2), replicate_matrix(b, 2), 6)
                == replicate_matrix(multiply(a, b, 2), 2), 'algebra homomorphism')
        product_checks += 1

    # Even replication changes idempotents into nilpotents.
    q = outer(1, 1, 2)
    even = replicate_matrix(q, 2, copies=2)
    require(even != 0 and multiply(even, even, 4) == 0, 'even replication control')
    require(off(q, 2) == 0, 'single-copy diagonal information loss')
    require(off(outer(1, 2, 2), 2).bit_count() == 1, 'single-copy matrix unit')

    cases = [check_family(n) for n in range(3, 13)]
    return {'statement': 'For every n>=3, a complete unit-free pool of n+1 projectors acts irreducibly on an n-dimensional image but has no irreducible image-basis subcollection.',
            'replication_lemma_checks': {'all_M2_subspaces': len(matrix_spaces),
                                         'subspaces_by_dimension': {str(k): v for k, v in sorted(dimensions.items())},
                                         'pool_memberships': pool_total, 'product_pairs': product_checks},
            'family_checks': cases,
            'hypothesis_controls': ['Two-fold replication is nilpotent.',
                                    'One-fold off projection loses diagonal information and can contain units.',
                                    'Deleting the extra projector leaves a common kernel.',
                                    'Replacing the first cycle projector leaves an invariant line.'],
            'scope': 'At image dimension seven this family has pattern dimension eight; it does not settle the pattern-dimension-five extraction question.',
            'kappa_change': None}


def main():
    actual = json.loads(json.dumps(compute()))
    expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    require(actual == expected, 'receipt mismatch')
    print('PASS_NO_EDGE_BASIS_EXTRACTION_FAILURE')
    print(json.dumps({'matrix_subspaces': 67, 'family_dimensions': 10,
                      'patterns_checked': sum(x['patterns_checked'] for x in actual['family_checks']),
                      'subsets_checked': sum(x['all_subsets_checked'] for x in actual['family_checks'])}, sort_keys=True))


if __name__ == '__main__':
    main()
