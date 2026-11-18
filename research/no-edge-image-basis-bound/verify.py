"""Exact checks for the image-basis bound over F2.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The normal triple is due to unpaidmoon; see PROOF.md for source links.
"""

import itertools
import json
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


def unit_free(pattern_basis):
    return all(value.bit_count() != 1 for value in span(pattern_basis))


def gram(pairs):
    return [sum(parity(y & x) << j for j, (x, _) in enumerate(pairs))
            for _, y in pairs]


def irreducible(pairs):
    """For independent images, use full covector rank and strong incidence."""
    n = len(pairs)
    require(len(basis(x for x, _ in pairs)) == n, 'images are not independent')
    rows = gram(pairs)
    if len(basis(rows)) != n:
        return False
    for start in range(n):
        reached = 1 << start
        while True:
            new = reached
            for j, row in enumerate(rows):
                if row & reached:
                    new |= 1 << j
            if new == reached:
                break
            reached = new
        if reached != (1 << n) - 1:
            return False
    return True


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


def diagonal_kernel(pairs, width):
    pivots, relations = {}, []
    for i, value in enumerate(patterns(pairs, width)):
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
    matrices = [outer(x, y, width) for x, y in pairs]
    for relation in relations:
        value = 0
        for i, matrix in enumerate(matrices):
            if (relation >> i) & 1:
                value ^= matrix
        require(value != 0 and off(value, width) == 0, 'diagonal kernel')
    groups = {}
    for i in range(len(pairs)):
        character = sum(((relation >> i) & 1) << j
                        for j, relation in enumerate(relations))
        groups.setdefault(character, []).append(i)
    return relations, groups


def family(blocks, fresh_x, fresh_y, fresh_width):
    require(blocks >= 2 and blocks % 2 == 0, 'even block count')
    require(0 < fresh_x < 1 << fresh_width, 'fresh image')
    require(0 < fresh_y < 1 << fresh_width, 'fresh covector')
    require(parity(fresh_x & fresh_y), 'fresh pairing')
    pairs = []
    hub = 0
    for j in range(blocks):
        shift = 3 * j
        pairs.extend((x << shift, y << shift) for x, y in ((6, 5), (5, 6), (7, 7)))
        hub |= 4 << shift
    pairs.append((hub | (fresh_x << (3 * blocks)),
                  hub | (fresh_y << (3 * blocks))))
    return pairs, 3 * blocks + fresh_width


def check_family(blocks, fresh_x, fresh_y, fresh_width):
    pairs, width = family(blocks, fresh_x, fresh_y, fresh_width)
    ps = patterns(pairs, width)
    n, k = len(pairs), len(basis(ps))
    require(all(parity(x & y) for x, y in pairs), 'idempotence')
    require(all(ps) and unit_free(ps), 'unit-free noncoordinate patterns')
    require(n == 3 * blocks + 1 and k == 2 * blocks + 1, 'family dimensions')
    require(pool(ps, width) == sorted(pairs), 'complete pool')
    require(irreducible(pairs), 'irreducible family')
    if n <= 7:
        require(orbit_irreducible(pairs), 'independent orbit check')
    relations, groups = diagonal_kernel(pairs, width)
    require(len(relations) == blocks, 'diagonal dimension')
    require(len(groups[0]) == 1, 'one zero character')
    supports = []
    for character, indices in groups.items():
        if not character:
            continue
        require(len(indices) == 3, 'three projectors per nonzero sector')
        matrix = 0
        for i in indices:
            matrix ^= outer(*pairs[i], width)
        require(off(matrix, width) == 0 and matrix.bit_count() == 3, 'coordinate sector')
        support = sum(((matrix >> (i * width + i)) & 1) << i for i in range(width))
        require(all(not support & old for old in supports), 'disjoint sectors')
        supports.append(support)
    require(2 * n == 3 * k - 1, 'sharp bound')
    return {'blocks': blocks, 'width': width, 'fresh_x': fresh_x, 'fresh_y': fresh_y,
            'projectors': n, 'pattern_dimension': k, 'diagonal_dimension': len(relations),
            'patterns_checked': (1 << k) - 1, 'sector_supports': supports,
            'pairs': pairs}


def compute():
    gl_count = 0
    survivors = []
    triples = set()
    for images in itertools.permutations(range(1, 8), 3):
        if len(basis(images)) != 3:
            continue
        gl_count += 1
        covectors = [next(y for y in range(1, 8)
                         if all(parity(x & y) == (i == j) for j, x in enumerate(images)))
                     for i in range(3)]
        pairs = tuple(zip(images, covectors))
        ps = patterns(pairs, 3)
        if all(ps) and unit_free(ps):
            require(sorted(x.bit_count() for x in images) == [2, 2, 3], 'normal weights')
            require(len(basis(ps)) == 2, 'normal pattern dimension')
            require(pool(ps, 3) == sorted(pairs), 'normal triple complete pool')
            survivors.append(images)
            triples.add(tuple(sorted(pairs)))
    require(gl_count == 168 and len(survivors) == 18 and len(triples) == 3, 'triple census')

    small_count = valid_count = irreducible_count = 0
    for n in (1, 2, 3):
        for images in itertools.combinations(range(1, 8), n):
            if len(basis(images)) != n:
                continue
            choices = [[y for y in range(1, 8) if parity(x & y)] for x in images]
            for covectors in itertools.product(*choices):
                small_count += 1
                pairs = list(zip(images, covectors))
                ps = patterns(pairs, 3)
                if not all(ps) or not unit_free(ps):
                    continue
                valid_count += 1
                action = irreducible(pairs)
                require(action == orbit_irreducible(pairs), 'small incidence/orbit agreement')
                if action:
                    irreducible_count += 1
                    require(2 * n <= 3 * len(basis(ps)) - 1, 'small complete bound check')

    # Compare the four-trial lift method with every small idempotent.
    lift_counts = []
    for width in (2, 3, 4):
        direct = {}
        for x, y in itertools.product(range(1, 1 << width), repeat=2):
            if parity(x & y):
                pattern = off(outer(x, y, width), width)
                if pattern:
                    direct.setdefault(pattern, []).append((x, y))
        for pattern, values in direct.items():
            require(sorted(lifts(pattern, width)) == sorted(values), 'complete lift comparison')
        lift_counts.append({'width': width, 'patterns': len(direct),
                            'idempotents': sum(map(len, direct.values()))})

    cases = [check_family(b, a, c, r) for b in (2, 4, 6)
             for a, c, r in ((1, 1, 1), (1, 3, 2), (3, 5, 3))]

    old, width = family(2, 1, 1, 1)
    old = old[:-1]
    old_k = len(basis(patterns(old, width)))
    require(unit_free(patterns(old, width)) and not irreducible(old), 'reducible control')
    require(2 * len(old) > 3 * old_k - 1, 'irreducibility is necessary')
    require(not orbit_irreducible(old), 'reducible orbit control')

    edge_pairs = [(1, 3), (3, 2), (6, 5)]
    edge_k = len(basis(patterns(edge_pairs, 3)))
    require(irreducible(edge_pairs) and orbit_irreducible(edge_pairs), 'edge control')
    require(not unit_free(patterns(edge_pairs, 3)), 'edge must be present')
    require(2 * len(edge_pairs) > 3 * edge_k - 1, 'no-unit hypothesis is necessary')

    odd_cases = []
    for blocks in (1, 3, 5):
        pairs = [(x << (3 * j), y << (3 * j)) for j in range(blocks)
                 for x, y in ((6, 5), (5, 6), (7, 7))]
        hub = sum(4 << (3 * j) for j in range(blocks))
        pairs.append((hub | (1 << (3 * blocks)), hub | (2 << (3 * blocks))))
        require(all(parity(x & y) for x, y in pairs), 'odd star is idempotent')
        require(not irreducible(pairs), 'odd equality star must be reducible')
        require(len(basis(gram(pairs))) == len(pairs) - 1, 'odd-star kernel')
        odd_cases.append({'blocks': blocks, 'projectors': len(pairs), 'gram_nullity': 1})

    return {'statement': '2n <= 3k-1 for irreducible image-basis collections with nonzero unit-free patterns',
            'triple_census': {'invertible_bases': gl_count, 'ordered_survivors': len(survivors),
                              'unordered_triples': len(triples), 'triples': sorted(triples)},
            'complete_width_three_census': {'image_basis_collections': small_count,
                                            'nonzero_unit_free': valid_count,
                                            'irreducible': irreducible_count},
            'lift_cross_checks': lift_counts, 'sharp_complete_families': cases,
            'controls': {'without_irreducibility': {'n': len(old), 'k': old_k},
                         'with_matrix_unit': {'n': len(edge_pairs), 'k': edge_k},
                         'odd_stars': odd_cases},
            'scope': 'Finite checks support the all-width proof; larger dependent-image pools remain outside the theorem.',
            'kappa_change': None}


def main():
    actual = json.loads(json.dumps(compute()))
    expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    require(actual == expected, 'receipt mismatch')
    print('PASS_NO_EDGE_IMAGE_BASIS_BOUND')
    print(json.dumps({'triple_bases': 168, 'sharp_families': len(actual['sharp_complete_families']),
                      'patterns_checked': sum(x['patterns_checked'] for x in actual['sharp_complete_families'])}, sort_keys=True))


if __name__ == '__main__':
    main()
