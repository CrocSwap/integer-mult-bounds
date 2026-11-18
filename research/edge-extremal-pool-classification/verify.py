"""Exact checks for all-dimension extremal projector pools.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Matrix, lift, orbit and subspace primitives are reused from PR7692.
See CREDITS.md for exact sources and predecessor support arguments.
"""

import hashlib
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

def coordinates(vectors, value):
    pivots = {}
    for i, row in enumerate(vectors):
        label = 1 << i
        while row:
            bit = row.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = row, label
                break
            other, old = pivots[bit]
            row ^= other
            label ^= old
        require(row != 0, 'coordinate basis independence')
    label = 0
    while value:
        bit = value.bit_length() - 1
        require(bit in pivots, 'vector is in the image basis')
        row, old = pivots[bit]
        value ^= row
        label ^= old
    return label


def invariant_certificate(pairs):
    """Use the common kernel and every image orbit; no generator is omitted."""
    vectors = basis(x for x, _ in pairs)
    n = len(vectors)
    if not n:
        return False, 'empty', ()
    rows = basis(sum(parity(y & x) << i for i, x in enumerate(vectors)) for _, y in pairs)
    if len(rows) < n:
        pivots = {row.bit_length() - 1: row for row in rows}
        value = 1 << next(i for i in range(n) if i not in pivots)
        for i, row in sorted(pivots.items()):
            if parity(row & value):
                value ^= 1 << i
        require(value and all(not parity(row & value) for row in rows), 'restricted kernel vector')
        witness = 0
        for i, vector in enumerate(vectors):
            if value >> i & 1:
                witness ^= vector
        require(witness and all(not parity(y & witness) for _, y in pairs), 'common kernel witness')
        return False, 'common_kernel', (witness,)
    for start in sorted({x for x, _ in pairs}):
        orbit = basis([start])
        while True:
            new = basis((*orbit, *(x for x, y in pairs if any(parity(y & v) for v in orbit))))
            if len(new) == len(orbit):
                break
            orbit = new
        if len(orbit) < n:
            subspace = set(span(orbit))
            require(all(not parity(y & v) or x in subspace for x, y in pairs for v in orbit),
                    'proper orbit is invariant under the whole pool')
            return False, 'proper_image_orbit', orbit
    return True, 'irreducible', ()


def directed_units(ps, width):
    return sorted(divmod(p.bit_length() - 1, width) for p in span(ps) if p.bit_count() == 1)


def edge_projectors(edge_list):
    return [(x, y) for a, b in edge_list
            for x, y in [((1 << a), (1 << a) | (1 << b)),
                         ((1 << a) | (1 << b), (1 << b))]]


def normal_form(pairs, ps, width):
    k = len(basis(ps))
    n = len(basis(x for x, _ in pairs))
    require(k >= 2 and n == 2 * k - 1, 'extremal dimensions')
    units = directed_units(ps, width)
    require(len(units) == k - 1, 'exactly k-1 directed units')
    endpoints = {v for edge in units for v in edge}
    require(len(endpoints) == 2 * k - 2, 'disjoint edge endpoints')
    core = sum(1 << i for i in endpoints)
    old = edge_projectors(units)
    remainder = set(pairs) - set(old)
    require(set(old) <= set(pairs) and len(remainder) == 1, 'complete pool contains one link')
    x, y = next(iter(remainder))
    hx = sum(1 << b for _, b in units)
    hy = sum(1 << a for a, _ in units)
    require(x & core == hx and y & core == hy, 'forced old-coordinate factors')
    a, b = x & ~core, y & ~core
    require(a and b and parity(a & b), 'fresh pairing one')
    image_basis = [xx for xx, _ in old] + [a]
    expected = [1 << (i * n + i) for i in range(n - 1)] + [(1 << (n * n)) - 1]
    restrictions = [outer(coordinates(image_basis, xx),
                          sum(parity(yy & v) << i for i, v in enumerate(image_basis)), n)
                    for xx, yy in old + [(x, y)]]
    require(restrictions == expected, 'coordinate projectors plus J normal form')
    require(len(pairs) == n, 'image-basis completeness is forced')
    return {'k': k, 'n': n, 'edges': units, 'fresh_image': a, 'fresh_covector': b}


def small_pattern_census():
    positions = [i * 3 + j for i in range(3) for j in range(3) if i != j]
    raw = [(x, y, off(outer(x, y, 3), 3)) for x, y in itertools.product(range(1, 8), repeat=2)
           if parity(x & y) and off(outer(x, y, 3), 3)]
    counts, positives = Counter(), []
    for compressed in all_subspaces(6):
        literal = {sum(((v >> i) & 1) << pos for i, pos in enumerate(positions)) for v in compressed}
        ps = basis(sorted(literal))
        actual = sorted((x, y) for x, y, pattern in raw if pattern in literal)
        require(actual == pool(ps, 3), 'small raw pool agrees with lifting')
        action, reason, witness = invariant_certificate(actual)
        if actual:
            require(action == orbit_irreducible(actual), 'image-orbit test agrees with all-vector test')
        counts['spaces'] += 1
        counts[reason] += 1
        k, n = len(ps), len(basis(x for x, _ in actual))
        if action and k >= 2 and n == 2 * k - 1:
            positives.append(normal_form(actual, ps, 3))
    require(counts['spaces'] == 2825 and len(positives) == 6, 'complete width-three extremal census')
    return {'counts': dict(sorted(counts.items())), 'extremizers': positives}


def pure_unit_graph_census(width):
    positions = [(i, j) for i in range(width) for j in range(width) if i != j]
    raw = [(x, y, off(outer(x, y, width), width))
           for x, y in itertools.product(range(1, 1 << width), repeat=2)
           if parity(x & y) and off(outer(x, y, width), width)]
    counts = Counter()
    for mask in range(1 << len(positions)):
        selected = [edge for i, edge in enumerate(positions) if mask >> i & 1]
        allowed = sum(1 << (a * width + b) for a, b in selected)
        vertices = {v for edge in selected for v in edge}
        actual = [(x, y) for x, y, pattern in raw if not pattern & ~allowed]
        n = len(vertices)
        require(len(basis(x for x, _ in actual)) == n, 'pure graph joint image is its endpoint space')
        strong = bool(vertices)
        for start in sorted(vertices):
            reached = {start}
            while True:
                new = reached | {a for a, b in selected if b in reached}
                if new == reached:
                    break
                reached = new
            if reached != vertices:
                strong = False
                coordinate_subspace = sum(1 << i for i in reached)
                require(all(not (y & coordinate_subspace) or not (x & ~coordinate_subspace)
                            for x, y in actual), 'predecessor-closed invariant coordinate space')
                break
        irreducible, _, _ = invariant_certificate(actual)
        require(irreducible == (strong and n >= 3), 'pure-unit graph criterion')
        if irreducible:
            require(len(selected) >= n, 'irreducible pure-unit edge floor')
        if n == 2:
            ones = sum(1 << i for i in vertices)
            require(all(not parity(y & ones) or x == ones for x, y in actual), 'two-vertex invariant line')
        counts['graphs'] += 1
        counts['irreducible'] += irreducible
        counts['strong_two_vertex_exception'] += strong and n == 2
    return {'width': width, 'counts': dict(sorted(counts.items()))}


def link_domain(t, width):
    edge_list = [(2 * i, 2 * i + 1) for i in range(t)]
    unit_patterns = [1 << (a * width + b) for a, b in edge_list]
    edge_mask = sum(unit_patterns)
    core = (1 << (2 * t)) - 1
    buckets, candidates = {}, set()
    raw_count = 0
    for x in range(1, 1 << width):
        for y in range(1, 1 << width):
            if not parity(x & y):
                continue
            raw_count += 1
            p = off(outer(x, y, width), width)
            if not p:
                continue
            key = p & ~edge_mask
            buckets.setdefault(key, []).append((x, y))
            if x & ~core:
                candidates.add(key)
    require(sorted(buckets.get(0, [])) == sorted(edge_projectors(edge_list)), 'old complete edge pool')
    counts, examples = Counter(), {}
    digest = hashlib.sha256()
    for key in sorted(candidates):
        require(key, 'outside image cannot have an old-span pattern')
        ps = unit_patterns + [key]
        actual = sorted(buckets[0] + buckets[key])
        require(actual == pool(ps, width), 'all odd-coset members agree with literal lifts')
        n = len(basis(x for x, _ in actual))
        require(n in (2 * t + 1, 2 * t + 2), 'complete quotient-image dimensions')
        irreducible, reason, invariant = invariant_certificate(actual)
        counts['spaces'] += 1
        counts[reason] += 1
        counts['extra_pool_members'] += len(actual) > 2 * t + 1
        counts['maximum_pool_size'] = max(counts['maximum_pool_size'], len(actual))
        if irreducible:
            require(n == 2 * t + 1, 'extremal image dimension')
            form = normal_form(actual, ps, width)
            require(orbit_irreducible(actual), 'positive all-vector orbit replay')
            counts['direct_positive_orbits'] += (1 << n) - 1
            examples.setdefault('positive', {'key': key, 'pairs': actual, 'normal_form': form})
        else:
            examples.setdefault(reason, {'key': key, 'pairs': actual, 'invariant_basis': invariant})
        digest.update((json.dumps({'key': key, 'n': n, 'reason': reason, 'invariant': invariant},
                                 sort_keys=True) + '\n').encode())
    r = width - 2 * t
    expected = ((1 << r) - 1) * (1 << (r - 1))
    require(counts['irreducible'] == expected, 'all and only fresh pairing-one links')
    return {'edge_pairs': t, 'width': width, 'raw_idempotents': raw_count,
            'counts': dict(sorted(counts.items())), 'expected_extremizers': expected,
            'case_certificate_sha256': digest.hexdigest(), 'examples': examples}


def wider_forms():
    result = []
    for t in (1, 2, 3, 4, 6, 8):
        for a, b, r in ((1, 1, 1), (1, 3, 2), (3, 1, 2), (3, 5, 3)):
            width = 2 * t + r
            edge_list = [(2 * i, 2 * i + 1) for i in range(t)]
            old = edge_projectors(edge_list)
            hx = sum(1 << v for _, v in edge_list)
            hy = sum(1 << u for u, _ in edge_list)
            link = (hx | (a << (2 * t)), hy | (b << (2 * t)))
            pairs = old + [link]
            ps = patterns(pairs, width)
            require(pool(ps, width) == sorted(pairs), 'wider complete pool')
            form = normal_form(pairs, ps, width)
            require(invariant_certificate(pairs)[0], 'wider full action')
            # Every deletion loses one independent image.
            for i in range(len(pairs)):
                subset = pairs[:i] + pairs[i + 1:]
                require(len(basis(x for x, _ in subset)) == len(pairs) - 1, 'one omitted member loses image rank')
            result.append({'width': width, 'pairs': pairs, 'normal_form': form,
                           'nonzero_patterns': (1 << (t + 1)) - 1})
    return result


def boundary_controls():
    single = [(1, 3)]
    ps = patterns(single, 2)
    require(len(basis(ps)) == 1 and invariant_certificate(single)[0], 'k=1 irreducible example')
    require(len(pool(ps, 2)) == 2, 'k=1 completion is larger')
    rejected = False
    try:
        normal_form(single, ps, 2)
    except ValueError as e:
        rejected = str(e) == 'extremal dimensions'
    require(rejected, 'k>=2 guard')
    reducible = []
    for k in range(2, 7):
        pairs = edge_projectors([(2 * i, 2 * i + 1) for i in range(k)])[:-1]
        ps = patterns(pairs, 2 * k)
        require(len(basis(ps)) == k and len(basis(x for x, _ in pairs)) == 2 * k - 1,
                'reducible extremal dimensions')
        require(not invariant_certificate(pairs)[0], 'irreducibility is necessary')
        require(len(directed_units(ps, 2 * k)) == k, 'reducible example has k edges')
        reducible.append({'k': k, 'image': 2 * k - 1, 'edge_count': k})
    return {'k_one_incomplete_example': single, 'reducible_examples': reducible}


def compute():
    return {'status': 'PASS_EDGE_EXTREMAL_POOL_CLASSIFICATION',
            'scope': 'Every irreducible binary noncoordinate projector collection with pattern dimension k>=2 and image dimension 2k-1.',
            'claim': 'The collection is complete: k-1 disjoint edge pairs and one link with the forced old factors and fresh pairing one.',
            'small_pattern_census': small_pattern_census(),
            'pure_unit_graphs': [pure_unit_graph_census(w) for w in (2, 3, 4)],
            'complete_link_domains': [link_domain(t, w) for t, w in ((1, 3), (1, 4), (1, 5), (2, 5), (2, 6), (3, 7), (3, 8))],
            'wider_forms': wider_forms(),
            'boundary_controls': boundary_controls(),
            'limitations': ['Uses the pinned all-width matching bound in PR7692.',
                            'The k=3 two-edge restricted normal form is prior work from PR6782.',
                            'This is not a coordinate-orbit count or a free physical change of basis.',
                            'No paid word, native realization, complete invoice or kappa improvement.']}


if __name__ == '__main__':
    actual = json.loads(json.dumps(compute()))
    expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    require(actual == expected, 'committed exact receipt')
    print(actual['status'])
    print(json.dumps({'pattern_spaces': actual['small_pattern_census']['counts']['spaces'],
                      'pure_graphs': sum(r['counts']['graphs'] for r in actual['pure_unit_graphs']),
                      'link_spaces': sum(r['counts']['spaces'] for r in actual['complete_link_domains']),
                      'positive_links': sum(r['counts']['irreducible'] for r in actual['complete_link_domains']),
                      'wider_forms': len(actual['wider_forms'])}, sort_keys=True))
