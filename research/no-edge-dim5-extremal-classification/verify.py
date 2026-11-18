"""Exact checks for the full pattern-five extremal classification.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Binary matrix, lift and orbit primitives are reused from PR7690.
See CREDITS.md for exact source pins and predecessor constructions.
"""

import hashlib
import itertools
import json
from collections import Counter, defaultdict
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



def unit_free(values):
    return all(x.bit_count() != 1 for x in span(values))



def normal_block(shift):
    return [(x << shift, y << shift) for x, y in ((6, 5), (5, 6), (7, 7))]


def column_triple(anchor, a, b, c):
    t, u = (1 << a) | (1 << c), (1 << b) | (1 << c)
    return [((1 << anchor) | v, 1 << anchor) for v in (t, u, t ^ u)]


def raw_idempotents(width):
    return [(x, y, off(outer(x, y, width), width))
            for x, y in itertools.product(range(1, 1 << width), repeat=2)
            if parity(x & y)]


def invariant_column_kernel(pairs, active):
    image_space = span(x for x, _ in pairs)
    kernel = {v for v in image_space if not v & active}
    require(1 < len(kernel) < len(image_space), 'proper nonzero coordinate kernel')
    for vector in basis(sorted(kernel)):
        for x, y in pairs:
            require(not parity(y & vector) or x in kernel, 'complete-pool invariant kernel')
    return list(basis(sorted(kernel)))


def census(name, old, width, active, raw, zero_fresh_covector=False):
    old_ps = patterns(old, width)
    old_h = span(old_ps)
    old_v = set(span(x for x, _ in old))
    require(len(old_h) == 16 and len(old_v) == 64 and unit_free(old_ps), 'old six-image pool')
    by_pattern = defaultdict(list)
    for x, y, pattern in raw:
        if pattern:
            by_pattern[pattern].append((x, y))
    old_pool = sorted(p for pattern in old_h if pattern for p in by_pattern[pattern])
    require(old_pool == sorted(old), 'complete even pool')
    require(all(not y & ~active for _, y in old_pool), 'even covectors use active columns')
    counts = Counter()
    spaces = {}
    rejected = set()
    for x, y, pattern in raw:
        if x in old_v or not pattern:
            continue
        if zero_fresh_covector and y & ~active:
            continue
        counts['candidate_links'] += 1
        representative = min(pattern ^ h for h in old_h)
        require(representative, 'new image cannot have old nonzero pattern')
        if representative in rejected:
            continue
        if representative not in spaces:
            odd = [representative ^ h for h in old_h]
            if any(p.bit_count() == 1 for p in odd):
                rejected.add(representative)
                continue
            spaces[representative] = (x, y)
        counts['unit_free_candidate_links'] += 1
    counts['distinct_unit_free_spaces'] = len(spaces)
    counts['distinct_rejected_spaces'] = len(rejected)
    case_counts = Counter()
    examples = {}
    digest = hashlib.sha256()
    max_pool = 0
    outside_mask = ((1 << width) - 1) ^ active
    for representative, link in sorted(spaces.items()):
        odd_patterns = [representative ^ h for h in old_h]
        odd_pool = sorted(p for pattern in odd_patterns for p in by_pattern[pattern])
        complete = sorted(old_pool + odd_pool)
        require(pool(old_ps + [representative], width) == complete, 'raw scan and four-trial pools agree')
        require(len(basis(x for x, _ in complete)) == 7, 'complete image has dimension seven')
        max_pool = max(max_pool, len(complete))
        outside_columns = [j for j in range(width) if (outside_mask >> j) & 1
                           and any((representative >> (i * width + j)) & 1 for i in range(width))]
        if not outside_columns:
            case = 'zero_outside_columns'
            witness = invariant_column_kernel(complete, active)
        else:
            limit = 2 if len(outside_columns) == 1 else 1
            case = 'one_outside_column' if limit == 2 else 'multiple_outside_columns'
            require(len({x for x, _ in odd_pool}) <= limit, 'odd image alternatives')
            restrictions = {y & outside_mask for _, y in odd_pool}
            require(len(restrictions) <= limit, 'odd covector restrictions')
            require(len(basis(y for _, y in complete)) <= active.bit_count() + limit, 'ambient covector rank bound')
            image_space = span(x for x, _ in complete)
            vector = next((v for v in image_space if v and all(not parity(y & v) for _, y in complete)), None)
            require(vector is not None, 'nonzero full common kernel')
            witness = [vector]
        case_counts[case] += 1
        record = {'representative': representative, 'link': link, 'pool': complete,
                  'outside_columns': outside_columns, 'invariant_basis': witness}
        digest.update((json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n').encode())
        examples.setdefault(case, record)
    return {'name': name, 'width': width, 'active_columns': active, 'old_pairs': old,
            'raw_idempotents': len(raw), 'counts': dict(sorted(counts.items())),
            'proof_case_counts': dict(sorted(case_counts.items())), 'maximum_complete_pool_size': max_pool,
            'all_space_certificates_sha256': digest.hexdigest(), 'one_example_per_case': examples}


def triple_quad_fixtures():
    quads = [([(15 ^ (1 << i), 15 ^ (1 << i)) for i in range(4)], 4, 15),
             ([(25, 1), (13, 1), (23, 2), (21, 3)], 5, 3)]
    result = []
    for quad, width, active in quads:
        for kind in ('normal', 'column'):
            if kind == 'normal':
                triple = normal_block(width)
                full_width, full_active = width + 3, active | (7 << width)
            else:
                triple = column_triple(width, width + 1, width + 2, width + 3)
                full_width, full_active = width + 4, active | (1 << width)
            pairs = quad + triple
            ps = patterns(pairs, full_width)
            require(len(basis(x for x, _ in pairs)) == 7, 'triple-quad image basis')
            require(len(basis(ps)) == 5 and unit_free(ps), 'triple-quad pattern space')
            complete = pool(ps, full_width)
            require(len(basis(x for x, _ in complete)) == 7, 'triple-quad full image')
            if full_active.bit_count() < 7:
                witness = invariant_column_kernel(complete, full_active)
            else:
                block = set(range(1 << width))
                require(all(not parity(y & v) or x in block for v in basis(sorted(block)) for x, y in complete), 'coordinate block invariant')
                witness = list(basis(sorted(block)))
            require(not orbit_irreducible(complete), 'triple-quad direct orbit control')
            result.append({'quad_active_rank': active.bit_count(), 'triple_kind': kind,
                           'width': full_width, 'active_columns': full_active, 'pool': complete,
                           'invariant_basis': witness})
    return result


def normal_form_census():
    count = survivors = 0
    triples = set()
    for images in itertools.permutations(range(1, 8), 3):
        if len(basis(images)) != 3:
            continue
        count += 1
        covectors = [next(y for y in range(1, 8)
                         if all(parity(x & y) == (i == j) for j, x in enumerate(images)))
                     for i in range(3)]
        pairs = tuple(zip(images, covectors))
        ps = patterns(pairs, 3)
        if all(ps) and unit_free(ps):
            survivors += 1
            require(sorted(x.bit_count() for x in images) == [2, 2, 3], 'normal-form weights')
            require(pool(ps, 3) == sorted(pairs), 'normal triple complete pool')
            triples.add(tuple(sorted(pairs)))
    require(count == 168 and survivors == 18 and len(triples) == 3, 'normal-form complete census')
    return {'ordered_bases': count, 'ordered_survivors': survivors, 'unordered_triples': sorted(triples)}


def compute():
    raw7, raw8 = raw_idempotents(7), raw_idempotents(8)
    require(len(raw7) == 8128 and len(raw8) == 32640, 'complete raw domains')
    mixed = normal_block(0) + column_triple(3, 4, 5, 6)
    columns = column_triple(0, 1, 2, 3) + column_triple(4, 5, 6, 7)
    normal = normal_block(0) + normal_block(3)
    censuses = [census('normal_and_column', mixed, 7, 15, raw7),
                census('two_columns', columns, 8, 17, raw8),
                census('normal_zero_fresh_covector', normal, 7, 63, raw7, True)]
    positive = []
    for fresh_width, a, b in ((1, 1, 1), (2, 1, 3), (2, 3, 1), (3, 3, 5), (3, 7, 7), (4, 9, 5)):
        require(parity(a & b), 'positive fresh pairing')
        link = (36 | (a << 6), 36 | (b << 6))
        pairs = normal + [link]
        ps = patterns(pairs, 6 + fresh_width)
        require(len(basis(ps)) == 5 and unit_free(ps), 'positive pattern space')
        require(pool(ps, 6 + fresh_width) == sorted(pairs), 'positive complete pool')
        require(orbit_irreducible(pairs), 'positive full orbit check')
        positive.append({'width': 6 + fresh_width, 'a': a, 'b': b, 'link': link})
    extra = pool(patterns(normal + [(64, 69)], 7), 7)
    require(len(extra) == 8 and (70, 5) in extra and (64, 69) in extra, 'extra-pool predecessor control')
    require(invariant_column_kernel(extra, 63) == [64], 'extra-pool line invariant')
    return {'statement': 'Every complete unit-free pattern-five pool with irreducible image seven is two disjoint normal triples plus one hub link with nonzero fresh factors of pairing one.',
            'normal_form': normal_form_census(), 'excluded_link_censuses': censuses,
            'triple_quad_controls': triple_quad_fixtures(), 'prior_positive_families': positive,
            'extra_pool_control': extra,
            'scope': 'All-width written classification; finite scans cover the stated canonical excluded geometries, not all coordinate embeddings.',
            'kappa_change': None}


def main():
    actual = json.loads(json.dumps(compute()))
    expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    require(actual == expected, 'receipt mismatch')
    print('PASS_NO_EDGE_DIM5_EXTREMAL_CLASSIFICATION')
    print(json.dumps({'raw_idempotents': 40768,
                      'candidate_links': sum(x['counts']['candidate_links'] for x in actual['excluded_link_censuses']),
                      'complete_spaces': sum(x['counts']['distinct_unit_free_spaces'] for x in actual['excluded_link_censuses'])}, sort_keys=True))


if __name__ == '__main__':
    main()
