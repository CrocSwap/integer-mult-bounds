"""Exact checks for edge-matching image bounds.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Matrix, lift, orbit and subspace primitives are reused from PR7690.
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

def edges(pattern_basis, width):
    return sorted({tuple(sorted(divmod(p.bit_length() - 1, width)))
                   for p in span(pattern_basis) if p.bit_count() == 1})


def matching(edge_list):
    best = ()
    def visit(i, used, chosen):
        nonlocal best
        if len(chosen) + len(edge_list) - i <= len(best):
            return
        if i == len(edge_list):
            best = chosen
            return
        a, b = edge_list[i]
        mask = (1 << a) | (1 << b)
        if not used & mask:
            visit(i + 1, used | mask, chosen + ((a, b),))
        visit(i + 1, used, chosen)
    visit(0, 0, ())
    return best


def relation_structure(pairs, width):
    """Check the disjoint relation code, including its two-member groups."""
    n = len(pairs)
    require(len(basis(x for x, _ in pairs)) == n, 'independent images')
    ps = patterns(pairs, width)
    require(all(ps), 'nonzero patterns')
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
    require(len(nonzero) == d and len(basis(nonzero)) == d,
            'independent nonzero characters')
    labels, supports, sizes, pair_edges = [], [], [], []
    for indices in nonzero.values():
        require(len(indices) >= 2, 'minimum circuit size')
        matrix = 0
        for i in indices:
            matrix ^= outer(*pairs[i], width)
        require(matrix and not off(matrix, width), 'nonzero diagonal sum')
        support = sum(((matrix >> (i * width + i)) & 1) << i for i in range(width))
        require(all(not support & other for other in supports), 'disjoint active supports')
        require(all(not pairs[i][1] & ~support for i in indices), 'covector support')
        require(support.bit_count() <= len(indices), 'diagonal rank')
        require((support.bit_count() - len(indices)) % 2 == 0, 'trace parity')
        image = set(span(pairs[i][0] for i in indices))
        require(all((1 << j) in image for j in range(width) if support >> j & 1),
                'active coordinates belong to the group image')
        if len(indices) == 2:
            i, j = indices
            require(ps[i] == ps[j] and ps[i].bit_count() == 1, 'edge-pair circuit')
            a, b = divmod(ps[i].bit_length() - 1, width)
            require(support == (1 << a) | (1 << b), 'edge endpoints are active')
            require(set(lifts(ps[i], width)) == {pairs[i], pairs[j]}, 'complete edge fiber')
            pair_edges.append(tuple(sorted((a, b))))
        supports.append(support)
        sizes.append(len(indices))
        labels.append(sum(1 << i for i in indices))
    require(set(span(labels)) == set(span(relations)), 'entire relation code')
    edge_list = edges(ps, width)
    nu = len(matching(edge_list))
    t = len(pair_edges)
    require(all(e in edge_list for e in pair_edges), 'pair edges are in H')
    require(len({v for edge in pair_edges for v in edge}) == 2 * t, 'circuit matching')
    require(t <= nu and n >= 3 * d - t and 2 * n <= 3 * k + nu, 'matching bound')
    return {'n': n, 'k': k, 'nu': nu, 'diagonal_dimension': d,
            'circuit_sizes': sorted(sizes), 'active_supports': supports,
            'pair_circuits': t, 'free_projectors': len(groups.get(0, []))}


def small_image_basis_census(width, maximum_n):
    counts = Counter()
    circuit_sizes = Counter()
    for n in range(1, maximum_n + 1):
        for images in itertools.combinations(range(1, 1 << width), n):
            if len(basis(images)) != n:
                continue
            choices = [[y for y in range(1, 1 << width) if parity(x & y)] for x in images]
            for covectors in itertools.product(*choices):
                counts['collections'] += 1
                pairs = list(zip(images, covectors))
                if not all(patterns(pairs, width)):
                    continue
                counts['nonzero_patterns'] += 1
                row = relation_structure(pairs, width)
                counts['with_pair_circuit'] += bool(row['pair_circuits'])
                counts['total_equality'] += 2 * n == 3 * row['k'] + row['nu']
                circuit_sizes[str(row['circuit_sizes'])] += 1
    return {'width': width, 'maximum_n': maximum_n, 'counts': dict(sorted(counts.items())),
            'circuit_size_counts': dict(sorted(circuit_sizes.items()))}


def three_width_pattern_census():
    positions = [i * 3 + j for i in range(3) for j in range(3) if i != j]
    def decode(value):
        return sum(((value >> i) & 1) << pos for i, pos in enumerate(positions))
    raw = [(x, y, off(outer(x, y, 3), 3))
           for x, y in itertools.product(range(1, 8), repeat=2)
           if parity(x & y) and off(outer(x, y, 3), 3)]
    counts, profile = Counter(), Counter()
    spaces = all_subspaces(6)
    require(len(spaces) == 2825, 'all width-three pattern spaces')
    for space in spaces:
        literal = {decode(p) for p in space}
        ps = basis(sorted(literal))
        actual = sorted((x, y) for x, y, p in raw if p in literal)
        require(pool(ps, 3) == actual, 'raw pool and four-trial lift agree')
        k, n = len(ps), len(basis(x for x, _ in actual))
        edge_list = edges(ps, 3)
        nu = len(matching(edge_list))
        brute = max((len(s) for size in range(len(edge_list) + 1)
                     for s in itertools.combinations(edge_list, size)
                     if len({v for e in s for v in e}) == 2 * len(s)), default=0)
        require(nu == brute, 'independent matching enumeration')
        require(2 * n <= 3 * k + nu and n <= 2 * k, 'total image bounds')
        counts['spaces'] += 1
        counts['empty_pools'] += not n
        if not n:
            continue
        irreducible = orbit_irreducible(actual)
        counts['irreducible'] += irreducible
        counts['total_equality'] += 2 * n == 3 * k + nu
        if irreducible:
            require(2 * n <= 3 * k + nu - 1 and n <= 2 * k - 1, 'strict bound')
        profile[str((k, nu, n, irreducible))] += 1
    return {'counts': dict(sorted(counts.items())), 'profile': dict(sorted(profile.items()))}


def normal_block(shift):
    return [(x << shift, y << shift) for x, y in ((6, 5), (5, 6), (7, 7))]


def edge_block(shift):
    return [(1 << shift, 3 << shift), (3 << shift, 2 << shift)]


def sharp_total(k, nu):
    pairs = [p for j in range(nu) for p in edge_block(2 * j)]
    shift = 2 * nu
    for j in range((k - nu) // 2):
        pairs += normal_block(shift)
        shift += 3
    if (k - nu) % 2:
        pairs.append((1 << shift, 7 << shift))
        shift += 3
    ps = patterns(pairs, shift)
    row = relation_structure(pairs, shift)
    require(row['k'] == k and row['nu'] == nu, 'prescribed k and matching number')
    require(row['n'] == (3 * k + nu) // 2, 'refined bound is sharp')
    require(pool(ps, shift) == sorted(pairs), 'sharp total complete pool')
    return {'k': k, 'nu': nu, 'width': shift, 'pairs': pairs, 'certificate': row,
            'patterns_checked': (1 << k) - 1}


def sharp_irreducible(k):
    if k == 1:
        width, pairs = 3, [(1, 7)]
    else:
        t = k - 1
        width = 2 * t + 1
        old = [p for j in range(t) for p in edge_block(2 * j)]
        hx = sum(1 << (2 * j + 1) for j in range(t))
        hy = sum(1 << (2 * j) for j in range(t))
        pairs = old + [(hx | (1 << (2 * t)), hy | (1 << (2 * t)))]
        gram = [[parity(y & x) for x, _ in old] for _, y in old]
        require(gram == [[int(i == j) for j in range(2 * t)] for i in range(2 * t)],
                'old edge projectors are orthogonal')
        require(all(parity(y & pairs[-1][0]) and parity(pairs[-1][1] & x)
                    for x, y in old), 'all old-link incidences are one')
        require(len(basis(sum(value << j for j, value in enumerate(row))
                          for row in [[parity(y & x) for x, _ in pairs] for _, y in pairs]))
                == len(pairs), 'star Gram matrix is nonsingular')
    ps = patterns(pairs, width)
    row = relation_structure(pairs, width)
    require(row['k'] == k and row['n'] == 2 * k - 1, 'universal irreducible maximum')
    require(pool(ps, width) == sorted(pairs), 'sharp irreducible complete pool')
    require(row['nu'] == max(0, k - 1), 'exact edge matching number')
    if row['n'] <= 9:
        require(orbit_irreducible(pairs), 'every nonzero orbit fills the image')
    return {'k': k, 'width': width, 'pairs': pairs, 'certificate': row,
            'direct_orbits': (1 << row['n']) - 1 if row['n'] <= 9 else 0,
            'star_certificate': k > 1, 'patterns_checked': (1 << k) - 1}


def boundary_controls():
    # A pure unit star distinguishes edge count from matching number.
    width = 5
    ps = [1 << j for j in range(1, width)]
    actual = pool(ps, width)
    require(len(edges(ps, width)) == 4 and len(matching(edges(ps, width))) == 1,
            'four overlapping edges have matching number one')
    require(len(basis(x for x, _ in actual)) == 5, 'unit-star image')
    require(not orbit_irreducible(actual), 'unit-star invariant')
    # The credited three-dimensional core is retained without relabelling.
    prior = [(1, 3), (3, 2), (4, 12), (12, 8), (26, 21)]
    require(sharp_irreducible(3)['pairs'] == prior, 'PR6782 exact witness')
    # Coordinate projectors would violate any bound depending only on H.
    coordinate = [(1 << j, 1 << j) for j in range(4)]
    require(len(basis(patterns(coordinate, 4))) == 0
            and len(basis(x for x, _ in coordinate)) == 4, 'zero-pattern counterexample')
    rejected = False
    try:
        relation_structure(coordinate, 4)
    except ValueError as e:
        rejected = str(e) == 'nonzero patterns'
    require(rejected, 'coordinate-projector guard')
    # Replacing maximum matching by zero fails on each edge pair.
    edge = relation_structure(edge_block(0), 2)
    require(2 * edge['n'] > 3 * edge['k'], 'edge allowance is necessary')
    # Equality can have column triples, whose complete pool stays reducible.
    column = [(11, 1), (13, 1), (7, 1)]
    mixed = column + edge_block(4)
    ps = patterns(mixed, 6)
    row = relation_structure(mixed, 6)
    actual = pool(ps, 6)
    require(2 * row['n'] == 3 * row['k'] + row['nu'] and not orbit_irreducible(actual),
            'column-triple equality remains reducible')
    # An orthogonal triple can contain edges. Equality must rule this out.
    triple = [(1, 5), (2, 6), (7, 4)]
    row = relation_structure(triple, 3)
    require(row['nu'] == 1 and row['pair_circuits'] == 0, 'extra edge in a three-circuit')
    require(2 * row['n'] < 3 * row['k'] + row['nu'], 'extra edge prevents equality')
    return {'unit_star': {'k': 4, 'edge_count': 4, 'nu': 1, 'image': 5,
                          'refined_upper': 6, 'universal_upper': 8},
            'prior_6782_exact_witness': prior, 'zero_pattern_counterexample_image': 4,
            'column_equality_pool_size': len(actual), 'extra_edge_triple': triple}


def result():
    small = [small_image_basis_census(3, 3), small_image_basis_census(4, 3)]
    total = [sharp_total(k, nu) for k in range(1, 11) for nu in range(k + 1)]
    irreducible = [sharp_irreducible(k) for k in range(1, 9)]
    return {'status': 'PASS_EDGE_MATCHING_IMAGE_BOUND',
            'scope': 'Binary rank-one idempotents with nonzero patterns; arbitrary width and pattern dimension.',
            'claims': {'total': '2 dim(V) <= 3k+nu; dim(V) <= 2k',
                       'irreducible': '2 dim(V) <= 3k+nu-1; dim(V) <= 2k-1',
                       'sharpness': 'Total bound for every (k,nu); universal irreducible bound for every k>=1.'},
            'small_image_basis_censuses': small, 'width_three_complete_pools': three_width_pattern_census(),
            'sharp_total_families': total, 'sharp_irreducible_families': irreducible,
            'boundary_controls': boundary_controls(),
            'limitations': ['No sharp irreducible bound for every fixed (k,nu) is claimed.',
                            'No sharpness for a prescribed edge graph is claimed.',
                            'No paid word, native implementation, complete invoice or kappa improvement.']}


if __name__ == '__main__':
    actual = json.loads(json.dumps(result()))
    expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    require(actual == expected, 'committed exact receipt')
    print(actual['status'])
    print(json.dumps({'basis_collections': sum(r['counts']['collections'] for r in actual['small_image_basis_censuses']),
                      'pattern_spaces': actual['width_three_complete_pools']['counts']['spaces'],
                      'total_families': len(actual['sharp_total_families']),
                      'irreducible_families': len(actual['sharp_irreducible_families'])}, sort_keys=True))
