#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the equality classification for binary edge-matching bounds.

Binary matrix, pool-lifting and orbit primitives are adapted from PR7692.
See CREDITS.md for exact source pins and prior mathematical results.
"""
from collections import Counter
from hashlib import sha256
import itertools
import json
from math import factorial, prod
from pathlib import Path

HERE = Path(__file__).resolve().parent

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


def invariant(pairs, width):
    for start in range(1, 1 << width):
        vectors = basis([start])
        while True:
            larger = basis((*vectors, *(x for x, y in pairs
                                       if any(parity(y & v) for v in vectors))))
            if len(larger) == len(vectors):
                break
            vectors = larger
        if len(vectors) < width:
            space = set(span(vectors))
            require(all((x if parity(y & v) else 0) in space
                        for x, y in pairs for v in space), 'invariant action')
            return list(vectors)
    raise ValueError('exceptional block is irreducible')


def small_blocks():
    summaries = []
    certificates = []
    for width, k, nu in ((3, 2, 1), (4, 3, 0)):
        raw = [(x, y) for x in range(1, 1 << width) for y in range(1, 1 << width)
               if parity(x & y)]
        count = eligible = 0
        sizes = Counter()
        spaces = set()
        for images in itertools.combinations(range(1, 1 << width), width):
            if len(basis(images)) != width:
                continue
            count += 1
            dual = [next(y for y in range(1, 1 << width)
                         if all(parity(y & x) == (i == j) for j, x in enumerate(images)))
                    for i in range(width)]
            selected = list(zip(images, dual, strict=True))
            ps = patterns(selected, width)
            hb = basis(ps)
            if 0 in ps or len(hb) != k or len(matching(edges(hb, width))) != nu:
                continue
            eligible += 1
            hs = sorted(span(hb))
            members = sorted((x, y) for x, y in raw if off(outer(x, y, width), width) in hs[1:])
            require(members == pool(hb, width), 'raw scan and literal lifting differ')
            require(not orbit_irreducible(members), 'all-vector orbit control')
            inv = invariant(members, width)
            sizes[len(members)] += 1
            spaces.add(tuple(hs))
            certificates.append({'width': width, 'basis_images': images, 'basis_dual': dual,
                                 'patterns': hs[1:], 'pool': members, 'invariant_basis': inv})
        require(count == prod((1 << width) - (1 << i) for i in range(width)) // factorial(width),
                'complete invertible-basis count')
        summaries.append({'width': width, 'k': k, 'nu': nu, 'unordered_bases': count,
                          'eligible_bases': eligible, 'distinct_spaces': len(spaces),
                          'pool_sizes': dict(sorted(sizes.items()))})
    require([s['eligible_bases'] for s in summaries] == [18, 339], 'nonempty exhaustive exceptions')
    return summaries, certificates


def normal_triples():
    normal = ((6, 5), (5, 6), (7, 7))
    versions = set()
    for permutation in itertools.permutations(range(3)):
        def permute(value):
            return sum(((value >> i) & 1) << permutation[i] for i in range(3))
        versions.add(tuple(sorted((permute(x), permute(y)) for x, y in normal)))
    found = set()
    for images in itertools.combinations(range(1, 8), 3):
        if len(basis(images)) != 3:
            continue
        dual = [next(y for y in range(1, 8)
                     if all(parity(y & x) == (i == j) for j, x in enumerate(images)))
                for i in range(3)]
        pairs = tuple(sorted(zip(images, dual, strict=True)))
        ps = patterns(pairs, 3)
        hb = basis(ps)
        if 0 not in ps and len(hb) == 2 and not edges(hb, 3):
            require(pool(hb, 3) == list(pairs), 'normal triple complete pool')
            found.add(pairs)
    require(found == versions and len(found) == 3, 'complete normal-triple classification')
    return sorted(found)


def core(t, r):
    pairs = []
    offset = 0
    for _ in range(t):
        pairs += [(1 << offset, 3 << offset), (3 << offset, 2 << offset)]
        offset += 2
    for _ in range(r):
        pairs += [(6 << offset, 5 << offset), (5 << offset, 6 << offset),
                  (7 << offset, 7 << offset)]
        offset += 3
    hx = hy = 0
    for x, y in pairs:
        hx ^= x
        hy ^= y
    return pairs, hx, hy, offset


def family(t, r, a=1, b=1):
    if t == r == 0:
        return [(a, b)], max(a.bit_length(), b.bit_length())
    pairs, hx, hy, offset = core(t, r)
    pairs.append((hx | (a << offset), hy | (b << offset)))
    return pairs, offset + max(a.bit_length(), b.bit_length())


def positive_families():
    domains = [(t, r, 1, 7 if t == r == 0 else 1) for t in range(5) for r in (0, 2, 4)]
    domains += [(t, r, a, b) for t, r in ((1, 0), (0, 2), (2, 2), (0, 4))
                for a, b in ((3, 1), (3, 2), (7, 7))]
    receipts = []
    total_patterns = 0
    for t, r, a, b in domains:
        pairs, width = family(t, r, a, b)
        require(all(parity(x & y) for x, y in pairs), 'idempotent family')
        hb = basis(patterns(pairs, width))
        k = t + 2 * r + 1
        n = 2 * t + 3 * r + 1
        require(len(hb) == k and len(basis(x for x, _ in pairs)) == n, 'family dimensions')
        complete = pool(hb, width)
        require(complete == sorted(pairs), 'complete attaining pool')
        unit_edges = edges(hb, width)
        require(len(unit_edges) == len(matching(unit_edges)) == t, 'exact matching number')
        require(2 * n == 3 * k + t - 1 and n % 2 == 1, 'equality parameters')
        gram = [sum(parity(y & x) << j for j, (x, _) in enumerate(pairs)) for _, y in pairs]
        require(len(basis(gram)) == n, 'no common covector kernel')
        if n > 1:
            require(all(parity(pairs[-1][1] & x) and parity(y & pairs[-1][0])
                        for x, y in pairs[:-1]), 'connected star action')
        if n <= 9:
            require(orbit_irreducible(pairs), 'every nonzero vector orbit')
        total_patterns += (1 << k) - 1
        receipts.append({'t': t, 'r': r, 'a': a, 'b': b, 'width': width, 'k': k, 'nu': t,
                         'image': n, 'pool_size': len(complete), 'all_vector_orbits': n <= 9})
    return {'families': receipts, 'nonzero_patterns_lifted': total_patterns}


def column_controls():
    results = []
    for t in (0, 1):
        selected = [(7, 1), (11, 1), (13, 1)]
        if t:
            selected += [(16, 48), (48, 32)]
        width = 4 + 2 * t
        old_image = set(span(x for x, _ in selected))
        raw = [(x, y) for x in range(1, 1 << width) for y in range(1, 1 << width)
               if parity(x & y)]
        index = {}
        for pair in raw:
            index.setdefault(off(outer(*pair, width), width), []).append(pair)
        count = 0
        spaces = set()
        sizes = Counter()
        maximum_covectors = 0
        for x, y in raw:
            if x in old_image:
                continue
            hb = basis(patterns(selected + [(x, y)], width))
            if len(hb) != t + 3 or len(matching(edges(hb, width))) != t:
                continue
            complete = pool(hb, width)
            hs = sorted(span(hb))
            require(complete == sorted(p for h in hs if h for p in index.get(h, [])), 'column raw pool')
            n = len(basis(xx for xx, _ in complete))
            cov_rank = len(basis(yy for _, yy in complete))
            require(n == 2 * t + 4 and cov_rank <= 2 * t + 3, 'column rank obstruction')
            common = next((v for v in span(xx for xx, _ in complete) if v
                           and all(not parity(yy & v) for _, yy in complete)), None)
            require(common is not None, 'complete-pool common kernel')
            count += 1
            spaces.add(tuple(hs))
            sizes[len(complete)] += 1
            maximum_covectors = max(maximum_covectors, cov_rank)
        require(count > 0, 'nonempty column-triple domain')
        results.append({'edge_pairs': t, 'width': width, 'candidate_links': count,
                        'distinct_spaces': len(spaces), 'pool_sizes': dict(sorted(sizes.items())),
                        'maximum_covector_rank': maximum_covectors})
    return results


def improved_attainment():
    receipts = []
    total_patterns = 0
    for t in range(5):
        for r in (1, 3):
            if t == 0 and r == 1:
                pairs = [(7, 63), (56, 504), (448, 511)]
                width = 9
            else:
                pairs, hx, hy, width = core(t, r)
                pairs.append((hx, hy))
            require(all(parity(x & y) for x, y in pairs), 'odd-core idempotence')
            hb = basis(patterns(pairs, width))
            k, n = t + 2 * r + 1, 2 * t + 3 * r
            require(len(hb) == k and len(basis(x for x, _ in pairs)) == n, 'improved dimensions')
            require(pool(hb, width) == sorted(pairs), 'complete improved pool')
            require(len(edges(hb, width)) == len(matching(edges(hb, width))) == t, 'improved matching')
            require(2 * n == 3 * k + t - 3, 'improved sharpness')
            gram = [sum(parity(y & x) << j for j, (x, _) in enumerate(pairs)) for _, y in pairs]
            require(len(basis(gram)) == n, 'improved common kernel')
            for start in range(len(pairs)):
                seen = {start}
                while True:
                    new = seen | {j for i in seen for j, (_, y) in enumerate(pairs)
                                  if parity(y & pairs[i][0])}
                    if new == seen:
                        break
                    seen = new
                require(len(seen) == len(pairs), 'strongly connected projector action')
            if n <= 9:
                require(orbit_irreducible(pairs), 'improved all-vector orbits')
            total_patterns += (1 << k) - 1
            receipts.append({'t': t, 'r': r, 'k': k, 'nu': t, 'image': n,
                             'width': width, 'pool_size': len(pairs), 'all_vector_orbits': n <= 9})
    return {'families': receipts, 'nonzero_patterns_lifted': total_patterns}


def parity_controls():
    receipts = []
    for t, r in ((0, 1), (1, 1), (0, 3)):
        pairs, width = family(t, r, 1, 2)
        require(all(parity(x & y) for x, y in pairs), 'odd-triple idempotence')
        hb = basis(patterns(pairs, width))
        require(pool(hb, width) == sorted(pairs), 'odd-triple complete pool')
        a = 1 << (2 * t + 3 * r)
        require(all(not parity(y & a) for _, y in pairs), 'odd-triple common kernel')
        bad, _ = family(t, r, 1, 1)
        require(not parity(bad[-1][0] & bad[-1][1]), 'trace-zero link rejection')
        receipts.append({'t': t, 'r': r, 'image': len(pairs), 'common_kernel': a})
    even = [(7, 7), (63, 56), (56, 63)]
    hb = basis(patterns(even, 6))
    require(pool(hb, 6) == sorted(even) and orbit_irreducible(even), 'even image remains possible away from equality')
    require(len(basis(x for x, _ in even)) == 2 and len(hb) == 3 and not edges(hb, 6), 'even control dimensions')
    return {'odd_triple_controls': receipts, 'irreducible_even_image_control': {'k': 3, 'nu': 0, 'image': 2}}


def result():
    small, certificates = small_blocks()
    normalized = json.loads(json.dumps(certificates))
    require(normalized == json.loads((HERE / 'EXCEPTIONS.json').read_text()), 'exception certificates')
    return {'small_blocks': small, 'exception_certificates_sha256': sha256(
                json.dumps(normalized, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'normal_triples': normal_triples(),
            'attaining': positive_families(), 'column_triple_controls': column_controls(),
            'improved_attainment': improved_attainment(),
            'parity_controls': parity_controls(),
            'scope': 'Equality in 2n <= 3k+nu-1 for noncoordinate irreducible binary projector collections.'}


def main():
    receipt = json.loads(json.dumps(result()))
    require(receipt == json.loads((HERE / 'RESULT.json').read_text()), 'receipt mismatch')
    print('PASS_EDGE_MATCHING_EQUALITY_CLASSIFICATION')


if __name__ == '__main__':
    main()
