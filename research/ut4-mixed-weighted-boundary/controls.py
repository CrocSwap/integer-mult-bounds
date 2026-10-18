#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate algebra and coverage controls for the new weighted boundary.

No predecessor scalar multiplication, reduction or group multiplication is
used by the dense/subsequence and literal-matrix oracles below. These controls
corroborate the written argument; they do not enumerate arbitrary role counts.
"""
from collections import defaultdict
from itertools import combinations, combinations_with_replacement, product
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ut4_controls_census', HERE / 'census.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
P, source = C.load()
require = C.require


def matmul(a, b):
    aa = [[(a >> (2*i+j)) & 1 for j in range(2)] for i in range(2)]
    bb = [[(b >> (2*i+j)) & 1 for j in range(2)] for i in range(2)]
    cc = [[sum(aa[i][k]*bb[k][j] for k in range(2)) % 2 for j in range(2)] for i in range(2)]
    return sum(cc[i][j] << (2*i+j) for i in range(2) for j in range(2))


def quotient_classes():
    words = [''.join(w) for n in range(4) for w in product('abc', repeat=n)]
    result = {}
    for word in words:
        orbit, queue = {word}, [word]
        for w in queue:
            for i in range(len(w)-1):
                if w[i:i+2] in ('ac', 'ca'):
                    changed = w[:i] + w[i:i+2][::-1] + w[i+2:]
                    if changed not in orbit:
                        orbit.add(changed)
                        queue.append(changed)
        zero = any(any(w[i] == w[i+1] for i in range(len(w)-1)) for w in orbit)
        result[word] = None if zero else min(orbit)
    require(len(set(result.values()) - {None}) == 17, 'independent quotient dimension')
    return result


CLASSES = quotient_classes()
MM = [[matmul(a, b) for b in range(16)] for a in range(16)]


def quotient(word):
    result = {'': 9}
    for degree in range(1, min(3, len(word))+1):
        for indices in combinations(range(len(word)), degree):
            name = CLASSES[''.join(word[i][0] for i in indices)]
            if name is None:
                continue
            coefficient = 9
            for i in indices:
                coefficient = MM[coefficient][word[i][1]]
            result[name] = result.get(name, 0) ^ coefficient
    return {k: v for k, v in result.items() if v}


def address(g):
    a, b, c, d, e, f = [(g >> i) & 1 for i in range(6)]
    return (1 | (a << 1) | (d << 2) | (f << 3), 2 | (b << 2) | (e << 3), 4 | (c << 3), 8)


def binary_product(a, b):
    rows = []
    for row in a:
        value = 0
        for j in range(4):
            if (row >> j) & 1:
                value ^= b[j]
        rows.append(value)
    return tuple(rows)


ADDRESSES = [address(g) for g in range(64)]
INDEX = {matrix: g for g, matrix in enumerate(ADDRESSES)}
GROUP = [[INDEX[binary_product(a, b)] for b in ADDRESSES] for a in ADDRESSES]
GENERATORS = dict(a=1, b=2, c=4)


def formal(word, roles):
    result = [[{0} if i == j else set() for j in range(roles)] for i in range(roles)]
    for letter, mask in word:
        old = [[set(entry) for entry in row] for row in result]
        for i, j, k in product(range(roles), repeat=3):
            if (mask >> (roles*k+j)) & 1:
                result[i][j].symmetric_difference_update(old[i][k])
                result[i][j].symmetric_difference_update(GROUP[g][GENERATORS[letter]] for g in old[i][k])
    return result


def outer(x, y, roles):
    return sum(((x >> i) & (y >> j) & 1) << (roles*i+j)
               for i in range(roles) for j in range(roles))


def project(mask):
    return sum(((mask >> (3*i+j)) & 1) << (2*i+j) for i in range(2) for j in range(2))


def main():
    for g, h in product(range(64), repeat=2):
        require(GROUP[g][h] == P.group_product(g, h), 'literal group law disagreement')
    alphabet = tuple(product('abc', P.COUPLINGS))
    short = 0
    for length in range(4):
        for word in product(alphabet, repeat=length):
            require(quotient(word) == P.quotient(word), 'independent quotient disagreement')
            short += 1
    require(short == 20440, 'short-word coverage')
    result = json.loads((HERE / 'RESULT.json').read_text())
    cat5, zeros = C.catalogue(P, 5)
    seen = defaultdict(set)
    for profile, realizations in cat5.items():
        for ns, slots in realizations:
            require(slots not in seen[ns], 'duplicate outer realization')
            seen[ns].add(slots)
            independent = []
            for j in range(5):
                value = 0
                for n, position in zip(ns, slots):
                    if position <= j:
                        value ^= n
                independent.append(value)
            require(tuple(independent) == profile, 'five-call prefix profile disagreement')
    positions = set(combinations_with_replacement(range(6), 5))
    zero_sequences = {ns for ns in product(P.COUPLINGS, repeat=5) if not P.total(ns)}
    require(set(seen) == zero_sequences and len(seen) == zeros == 3600
            and all(slots == positions for slots in seen.values()), 'complete five-call gap coverage')
    require(sum(map(len, seen.values())) == 907200, 'five-call realization count')
    cat4, _ = C.catalogue(P, 4)
    require((cat4, 441) == P.gap_catalogue(), 'unchanged four-call catalogue control')
    catalogues = {4: cat4, 5: cat5}
    for key, fixture in result['planted_reconstruction_controls'].items():
        word = tuple(map(tuple, fixture['word']))
        middle = tuple(fixture['middle'])
        na, _, nc = map(int, key.split(','))
        pa, pc = tuple(fixture['a_profile']), tuple(fixture['c_profile'])
        ra = tuple(map(tuple, fixture['a_realization']))
        rc = tuple(map(tuple, fixture['c_realization']))
        require(ra in catalogues[na][pa] and rc in catalogues[nc][pc], 'planted profile lost')
        require(word in P.expanded_words(middle, ra, rc), 'planted interleaving lost')
        require(quotient(word) == dict(fixture['quotient']) == P.quotient(word), 'long-word oracle disagreement')
        ka, kc = P.profile_key(middle, pa), P.profile_key(middle, pc)
        require((ka, kc) in P.compatible_keys({ka: [pa]}, {kc: [pc]}), 'planted cross join lost')
    positive = [tuple(step) for step in result['positive']['full_word']]
    require(quotient(positive) == P.TARGET, 'positive quotient control')
    columns = 0
    for role, h in product(range(3), range(64)):
        state = [set() for _ in range(3)]
        state[role].add(h)
        for letter, n in reversed(positive):
            old = [set(s) for s in state]
            for i, j in product(range(2), repeat=2):
                if (n >> (2*i+j)) & 1:
                    state[i].symmetric_difference_update(old[j])
                    state[i].symmetric_difference_update(GROUP[GENERATORS[letter]][g] for g in old[j])
        expected = [set() for _ in range(3)]
        expected[role].add(GROUP[(32, 40, 0)[role]][h])
        require(state == expected, 'faithful full dirty-column control')
        columns += 1
    oriented_pairs = 0
    for orientation in ('row', 'column'):
        masks = [outer(x, y, 3) for x, y in product(range(1, 8), repeat=2)
                 if (y < 4 if orientation == 'row' else x < 4)]
        for n, m in product(masks, repeat=2):
            word = [('a', n), ('b', m)]
            actual = formal(word, 3)
            compressed = formal([(letter, project(mask)) for letter, mask in word if project(mask)], 2)
            require([row[:2] for row in actual[:2]] == compressed, 'common-orientation projection')
            oriented_pairs += 1
    mixed = formal([('a', outer(1, 4, 3)), ('b', outer(4, 1, 3))], 3)
    require(mixed[0][0] != {0}, 'mixed orientations incorrectly compress')
    span_profiles = 0
    for ranks in product(range(2, 5), repeat=6):
        if 1 + sum(ranks) <= 14:
            require(sum(rank-2 for rank in ranks) <= 1, 'one-excess rank forcing')
            require(all(ranks[i] == 2 for i in (0, 2, 4))
                    or all(ranks[i] == 2 for i in (1, 3, 5)), 'common span orientation')
            span_profiles += 1
    require(span_profiles == 7, 'complete six-span one-excess profiles')
    price_cases = 0
    for alpha, beta, gamma in product(range(5), repeat=3):
        direct = 4*alpha + 6*beta + 4*gamma
        bound = min(direct, 4*alpha + 5*beta + 4*gamma + 2*min(alpha, gamma))
        relaxed = min(a*alpha+b*beta+c*gamma for a, b, c in product(range(4, 11), range(5, 11), range(4, 11))
                      if b >= 6 or a+c >= 10)
        require(bound == relaxed, 'weighted lower-envelope arithmetic')
        if beta <= 2*min(alpha, gamma):
            require(bound == direct, 'sharp price cone')
        price_cases += 1
    require(min(4+18+4, 4+15+4+2) == 25 < 26, 'outside-cone false sharpness control')
    print('PASS_UT4_WEIGHTED_BOUNDARY_CONTROLS', json.dumps(dict(
        literal_group_products=4096, short_quotient_words=short, five_call_gap_realizations=907200,
        planted_domains=3, faithful_dirty_columns=columns, common_orientation_pairs=oriented_pairs,
        mixed_orientation_rejected=True, span_profiles=span_profiles, price_grids=price_cases,
        outside_cone_sharpness_rejected=True), sort_keys=True))


if __name__ == '__main__':
    main()
