"""Exact checks for the general no-edge total-image bound.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Matrix, lift and orbit primitives are reused from PR7686 and PR7688.
See CREDITS.md for exact sources and predecessor support arguments.
"""

import itertools
import json
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


def unit_free(values):
    return all(x.bit_count() != 1 for x in span(values))


def relation_structure(pairs, width):
    n = len(pairs)
    require(len(basis(x for x, _ in pairs)) == n, 'independent images')
    ps = patterns(pairs, width)
    require(all(ps) and unit_free(ps), 'nonzero unit-free patterns')
    require(all(parity(x & y) for x, y in pairs), 'idempotence')
    pivots, relations = {}, []
    for i, value in enumerate(ps):
        label = 1 << i
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                old, old_label = pivots[pivot]
                value ^= old
                label ^= old_label
            else:
                pivots[pivot] = value, label
                break
        if not value:
            relations.append(label)
    groups = {}
    for i in range(n):
        character = sum(((r >> i) & 1) << j for j, r in enumerate(relations))
        groups.setdefault(character, []).append(i)
    nonzero = {c: indices for c, indices in groups.items() if c}
    d, k = len(relations), len(pivots)
    require(len(nonzero) == d and len(basis(nonzero)) == d, 'independent nonzero characters')
    class_relations, supports, sizes = [], [], []
    for indices in nonzero.values():
        require(len(indices) >= 3, 'minimum class size')
        label = sum(1 << i for i in indices)
        matrix = 0
        for i in indices:
            matrix ^= outer(*pairs[i], width)
        require(matrix and off(matrix, width) == 0, 'class has its own diagonal sum')
        support = sum(((matrix >> (i * width + i)) & 1) << i for i in range(width))
        require(all(not support & other for other in supports), 'disjoint active coordinates')
        require(all(not pairs[i][1] & ~support for i in indices), 'class covector support')
        require(support.bit_count() <= len(indices), 'diagonal rank')
        require((support.bit_count() - len(indices)) % 2 == 0, 'trace parity')
        supports.append(support)
        sizes.append(len(indices))
        class_relations.append(label)
    require(set(span(class_relations)) == set(span(relations)), 'entire relation code')
    require(2 * n <= 3 * k, 'total-image bound')
    return {'n': n, 'k': k, 'diagonal_dimension': d,
            'circuit_sizes': sorted(sizes), 'active_supports': supports,
            'free_projectors': len(groups.get(0, []))}


def small_image_basis_census(width, maximum_n):
    counts = Counter()
    circuits = Counter()
    for n in range(1, maximum_n + 1):
        for images in itertools.combinations(range(1, 1 << width), n):
            if len(basis(images)) != n:
                continue
            choices = [[y for y in range(1, 1 << width) if parity(x & y)] for x in images]
            for covectors in itertools.product(*choices):
                counts['collections'] += 1
                pairs = list(zip(images, covectors))
                ps = patterns(pairs, width)
                if not all(ps) or not unit_free(ps):
                    continue
                counts['nonzero_unit_free'] += 1
                row = relation_structure(pairs, width)
                circuits[str(row['diagonal_dimension'])] += 1
    return {'width': width, 'maximum_n': maximum_n,
            'counts': dict(sorted(counts.items())), 'diagonal_dimension_counts': dict(sorted(circuits.items()))}


def three_width_pattern_census():
    positions = [i * 3 + j for i in range(3) for j in range(3) if i != j]
    def encode(matrix):
        return sum(((matrix >> bit) & 1) << i for i, bit in enumerate(positions))
    candidates = [(x, y, encode(off(outer(x, y, 3), 3)))
                  for x, y in itertools.product(range(1, 8), repeat=2)
                  if parity(x & y) and off(outer(x, y, 3), 3)]
    spaces = all_subspaces(6)
    require(len(spaces) == 2825, 'all width-three pattern spaces')
    counts = Counter()
    equality = Counter()
    for space in spaces:
        if any(x.bit_count() == 1 for x in space):
            continue
        counts['unit_free_spaces'] += 1
        k = len(basis(space))
        pairs = [(x, y) for x, y, pattern in candidates if pattern in space]
        n = len(basis(x for x, _ in pairs))
        require(2 * n <= 3 * k, 'complete-pool total bound')
        if not n:
            counts['empty_pools'] += 1
            continue
        action = orbit_irreducible(pairs)
        if action:
            counts['irreducible_pools'] += 1
            require(2 * n <= 3 * k - 1, 'irreducible full-pool bound')
        if 2 * n == 3 * k:
            require(not action, 'even equality must be reducible')
            equality[str(k)] += 1
    return {'all_pattern_spaces': len(spaces), 'counts': dict(sorted(counts.items())),
            'nonempty_total_equality_by_k': dict(sorted(equality.items()))}


def normal_block(shift):
    return [(x << shift, y << shift) for x, y in ((6, 5), (5, 6), (7, 7))]


def sharp_family(k):
    pairs = [p for j in range(k // 2) for p in normal_block(3 * j)]
    width = 3 * (k // 2)
    if k % 2:
        pairs.append((1 << width, 7 << width))
        width += 3
    ps = patterns(pairs, width)
    row = relation_structure(pairs, width)
    require(row['n'] == (3 * k) // 2 and row['k'] == k, 'sharp dimensions')
    require(pool(ps, width) == sorted(pairs), 'sharp complete pool')
    if k > 1:
        # A normal-block image line is invariant under every pool member.
        line = pairs[0][0]
        require(all(not parity(y & line) or x == line for x, y in pairs), 'sharp reducibility witness')
    return {'k': k, 'width': width, 'pairs': pairs, 'certificate': row,
            'patterns_checked': (1 << k) - 1}


def odd_column_circuit(m, shift=0):
    require(m >= 3 and m % 2 == 1, 'odd circuit length')
    t = [(1 << i) | (1 << m) for i in range(1, m)]
    last = 0
    for value in t:
        last ^= value
    t.append(last)
    return [((1 | value) << shift, 1 << shift) for value in t], m + 1


def even_orthogonal_circuit(m, shift=0):
    require(m >= 4 and m % 2 == 0, 'even circuit length')
    ones = (1 << m) - 1
    return [((ones ^ (1 << i)) << shift, (ones ^ (1 << i)) << shift)
            for i in range(m)], m


def compute():
    small = [small_image_basis_census(3, 3), small_image_basis_census(4, 3)]
    pattern_census = three_width_pattern_census()
    sharp = [sharp_family(k) for k in range(1, 13)]
    varied = []
    for m in (3, 5, 7):
        pairs, width = odd_column_circuit(m)
        varied.append({'kind': 'column', 'm': m, 'certificate': relation_structure(pairs, width)})
    for m in (4, 6, 8):
        pairs, width = even_orthogonal_circuit(m)
        varied.append({'kind': 'orthogonal', 'm': m, 'certificate': relation_structure(pairs, width)})
    mixed, width = odd_column_circuit(3)
    part, size = even_orthogonal_circuit(4, width)
    mixed += part
    width += size
    part, size = odd_column_circuit(5, width)
    mixed += part
    width += size
    mixed.append((1 << width, 7 << width))
    width += 3
    varied.append({'kind': 'mixed', 'certificate': relation_structure(mixed, width)})

    # Three equality geometries from the prior dimension-four analysis.
    equality_controls = []
    for kinds in (('column', 'column'), ('normal', 'column'), ('normal', 'normal')):
        pairs, width = [], 0
        for kind in kinds:
            if kind == 'column':
                part, size = odd_column_circuit(3, width)
            else:
                part, size = normal_block(width), 3
            pairs += part
            width += size
        require(pool(patterns(pairs, width), width) == sorted(pairs), 'mixed equality complete pool')
        require(not orbit_irreducible(pairs), 'mixed equality reducible')
        equality_controls.append({'kinds': kinds, 'certificate': relation_structure(pairs, width),
                                  'covector_rank': len(basis(y for _, y in pairs))})

    for kind in ('overlapping_columns', 'overlapping_mixed'):
        if kind == 'overlapping_columns':
            pairs = []
            for anchor, a, b in ((0, 2, 3), (1, 4, 5)):
                t, u = (1 << a) | 64, (1 << b) | 64
                pairs += [((1 << anchor) | v, 1 << anchor) for v in (t, u, t ^ u)]
            width = 7
        else:
            pairs = normal_block(0)
            t, u = 1 | 16, 2 | 32
            pairs += [(8 | v, 8) for v in (t, u, t ^ u)]
            width = 6
        require(pool(patterns(pairs, width), width) == sorted(pairs), 'overlapping-support complete pool')
        require(not orbit_irreducible(pairs), 'overlapping-support reducibility')
        equality_controls.append({'kinds': [kind], 'certificate': relation_structure(pairs, width),
                                  'covector_rank': len(basis(y for _, y in pairs))})

    seven = normal_block(0) + normal_block(3) + [(100, 100)]
    seven_ps = patterns(seven, 7)
    require(pool(seven_ps, 7) == sorted(seven) and orbit_irreducible(seven), 'prior sharp seven-image witness')
    require(len(basis(seven_ps)) == 5, 'seven-image pattern dimension')
    seven_certificate = relation_structure(seven, 7)

    with_unit = [(1, 3), (3, 2)]
    require(len(basis(x for x, _ in with_unit)) == 2, 'unit control image rank')
    require(len(basis(patterns(with_unit, 2))) == 1, 'unit control pattern rank')
    require(not unit_free(patterns(with_unit, 2)), 'unit control outside hypothesis')
    non_idempotent = [(6, 1), (7, 1)]
    require(len(basis(x for x, _ in non_idempotent)) == 2, 'nilpotent control image rank')
    require(len(basis(patterns(non_idempotent, 3))) == 1 and unit_free(patterns(non_idempotent, 3)), 'nilpotent unit-free control')
    require(not parity(6 & 1) and parity(7 & 1), 'nilpotent premise failure')
    require(patterns([(1, 1)], 1) == [0], 'coordinate projector control')

    return {'statement': 'For every binary rank-one idempotent collection with nonzero unit-free pattern span H, 2 dim(V) <= 3 dim(H). The total bound is sharp for each k. Irreducible action gives 2 dim(V) <= 3 dim(H)-1.',
            'small_image_basis_censuses': small, 'complete_width_three_pattern_census': pattern_census,
            'sharp_total_families': sharp, 'larger_circuit_controls': varied,
            'even_equality_controls': equality_controls,
            'prior_irreducible_seven_witness': {'pairs': seven, 'certificate': seven_certificate},
            'hypothesis_controls': {'with_matrix_unit': {'n': 2, 'k': 1},
                                    'without_idempotence': {'n': 2, 'k': 1},
                                    'with_zero_pattern': {'n': 1, 'k': 0}},
            'scope': 'The k=5 maximum is seven; coordinate classification of all attaining pools and paid-word consequences remain open.',
            'kappa_change': None}


def main():
    actual = json.loads(json.dumps(compute()))
    expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    require(actual == expected, 'receipt mismatch')
    print('PASS_NO_EDGE_TOTAL_IMAGE_BOUND')
    print(json.dumps({'small_collections': sum(x['counts']['collections'] for x in actual['small_image_basis_censuses']),
                      'pattern_spaces': 2825, 'sharp_k_values': 12,
                      'sharp_patterns': sum(x['patterns_checked'] for x in actual['sharp_total_families'])}, sort_keys=True))


if __name__ == '__main__':
    main()
