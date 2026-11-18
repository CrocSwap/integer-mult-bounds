#!/usr/bin/env python3
"""Check complete binary pools and invariant-subspace certificates.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEFT = ((6, 5), (5, 6), (7, 7))
BLOCKS = LEFT + tuple((x << 3, y << 3) for x, y in LEFT)
HUBS = (1 << 2) | (1 << 5)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return (x & y).bit_count() & 1


def off(x, y, width):
    result = 0
    for i in range(width):
        if x & (1 << i):
            result |= (y & ~(1 << i)) << (width*i)
    return result


def basis(vectors):
    rows = {}
    for value in vectors:
        while value:
            pivot = value.bit_length()-1
            if pivot not in rows:
                rows[pivot] = value
                break
            value ^= rows[pivot]
    return tuple(rows[k] for k in sorted(rows, reverse=True))


def remainder(value, rows):
    for row in rows:
        if value & (1 << (row.bit_length()-1)):
            value ^= row
    return value


def span(vectors):
    values = {0}
    for vector in vectors:
        values |= {value ^ vector for value in values}
    return values


def orbit(vector, pool):
    rows = basis([vector])
    while True:
        more = [x for x, y in pool if any(dot(v, y) for v in rows)]
        new = basis([*rows, *more])
        if len(new) == len(rows):
            return rows
        rows = new


def invariant_certificate(vectors, pool):
    rows = basis(vectors)
    joint = basis(x for x, _ in pool)
    require(0 < len(rows) < len(joint), 'subspace must be nonzero and proper')
    require(all(not remainder(v, joint) for v in rows), 'subspace outside joint image')
    require(all(not dot(v, y) or not remainder(x, rows)
                for v in rows for x, y in pool), 'subspace is not invariant')


def classify(x, y, pool):
    core_x, core_y = x & 63, y & 63
    if not core_y:
        invariant_certificate([u for u, _ in BLOCKS], pool)
        return False, 'zero core covector'
    if not core_x:
        invariant_certificate([x], pool)
        return False, 'zero core image'
    require(set(pool) == set(BLOCKS) | {(x, y)}, 'nondegenerate coset must have one lift')
    alpha = [dot(x, v) for _, v in BLOCKS]
    beta = [dot(u, y) for u, _ in BLOCKS]
    if 0 in beta:
        invariant_certificate([BLOCKS[beta.index(0)][0]], pool)
        return False, 'missing outgoing incidence'
    if 0 in alpha:
        omitted = alpha.index(0)
        invariant_certificate([x]+[u for i, (u, _) in enumerate(BLOCKS) if i != omitted], pool)
        return False, 'missing incoming incidence'
    joint = span(x for x, _ in pool)
    require(len(joint) == 128, 'positive image dimension')
    for value in joint-{0}:
        require(len(orbit(value, pool)) == 7, 'positive orbit does not span')
    return True, 'irreducible'


def census(width):
    hrows = basis(off(x, y, width) for x, y in BLOCKS)
    hspace = span(hrows)
    require(len(hrows) == 4 and all(p.bit_count() >= 3 for p in hspace-{0}), 'base pattern space')
    by_pattern, by_quotient = defaultdict(list), defaultdict(list)
    idempotents = 0
    for x in range(1, 1 << width):
        for y in range(1, 1 << width):
            if not dot(x, y):
                continue
            idempotents += 1
            p = off(x, y, width)
            direct = sum(1 << (width*i+j) for i in range(width) for j in range(width)
                         if i != j and (x >> i) & (y >> j) & 1)
            require(p == direct, 'direct matrix pattern')
            if p:
                by_pattern[p].append((x, y))
                by_quotient[remainder(p, hrows)].append((x, y))
    require(set(by_quotient[0]) == set(BLOCKS), 'complete base pool')
    counts, pool_sizes = Counter(), Counter()
    positives = []
    extra_pool = None
    for key, members in by_quotient.items():
        if key == 0:
            continue
        pool = tuple(sorted(set(BLOCKS) | set(members)))
        for x, y in members:
            if not (x >> 6 and y >> 6):
                continue
            p = off(x, y, width)
            independent_pool = set(BLOCKS)
            for h in hspace:
                independent_pool.update(by_pattern.get(p ^ h, ()))
            require(independent_pool == set(pool), 'quotient and literal coset pools differ')
            if width == 7 and (x, y) == (64, 69):
                require(len(pool) == 8 and (70, 5) in pool, 'degenerate extra projector')
                require(all(v.bit_count() > 1 for v in (hspace | {p ^ h for h in hspace})-{0}),
                        'extra-projector fixture must be unit-free')
                extra_pool = [list(pair) for pair in pool]
            answer, kind = classify(x, y, pool)
            predicted = (x & 63) == (y & 63) == HUBS and dot(x >> 6, y >> 6) == 1
            require(answer == predicted, 'classification differs from exact certificate')
            counts[kind] += 1
            pool_sizes[len(pool)] += 1
            if answer:
                patterns = hspace | {p ^ h for h in hspace}
                require(len(patterns) == 32 and all(v.bit_count() > 1 for v in patterns-{0}),
                        'positive no-edge pattern space')
                positives.append((x, y))
    fresh = width-6
    require(len(positives) == ((1 << fresh)-1)*(1 << (fresh-1)), 'all-size positive count')
    symmetric = sum(x == y for x, y in positives)
    require(symmetric == 1 << (fresh-1), 'symmetric count')
    return {'width': width, 'all_rank_one_idempotents': idempotents,
            'candidate_links': sum(counts.values()), 'outcomes': dict(sorted(counts.items())),
            'complete_pool_sizes': {str(k): v for k, v in sorted(pool_sizes.items())},
            'irreducible_links': [list(pair) for pair in sorted(positives)],
            'symmetric': symmetric, 'nonsymmetric': len(positives)-symmetric,
            'degenerate_extra_pool': extra_pool}


def verify():
    require(all(dot(x, v) == int(i == j)
                for i, (x, _) in enumerate(BLOCKS) for j, (_, v) in enumerate(BLOCKS)),
            'six image/covector pairs are dual')
    require(len(basis(x for x, _ in BLOCKS)) == 6, 'core image basis')
    checks = [census(7), census(8)]
    positive = (HUBS | 64, HUBS | 192)
    pool = BLOCKS + (positive,)
    require(classify(*positive, pool)[0], 'source positive witness')
    disjoint = (6 | 64, 5 | 128)
    require(dot(*disjoint) == 1 and not ((disjoint[0] >> 6) & (disjoint[1] >> 6)),
            'valid disjoint-fresh witness')
    require(not classify(*disjoint, BLOCKS+(disjoint,))[0], 'disjoint-fresh must be reducible')
    bad_spaces = [[BLOCKS[0][0]], [x for x, _ in pool], [1 << 8], []]
    for bad in bad_spaces:
        try:
            invariant_certificate(bad, pool)
        except ValueError:
            pass
        else:
            raise ValueError('invalid invariant certificate accepted')
    require(not dot(positive[0], positive[1] ^ 64), 'idempotence control')
    result = {'status': 'PASS_TWO_BLOCK_FRESH_LINK_CLASSIFICATION',
              'censuses': checks, 'source_nonsymmetric_witness': list(positive),
              'valid_disjoint_fresh_reducible_witness': list(disjoint),
              'census_positive_orbits_checked': 127*sum(len(c['irreducible_links']) for c in checks),
              'rejection_controls': 5}
    require(json.loads((ROOT/'RESULT.json').read_text()) == result, 'retained receipt')
    return result


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True, indent=2))
