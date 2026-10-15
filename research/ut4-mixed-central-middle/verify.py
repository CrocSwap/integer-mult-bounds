#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact z/uz UT4 tariff census. No physical supplier or kappa claim.

The profile-screen method is credited to Aaron Wang's PR1690. This implementation
uses concrete gap placements rather than its recursive profile reconstruction.
Every loop has a fixed finite domain: two roles, four outer calls, five middle
calls, the 64-element group and the degree-three quotient.
"""
from collections import defaultdict
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, product
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASIS = ('', 'a', 'b', 'c', 'ab', 'ac', 'ba', 'bc', 'cb',
         'aba', 'abc', 'acb', 'bab', 'bac', 'bcb', 'cba', 'cbc')
TARGET = {'': 9, 'ab': 8, 'ba': 8, 'aba': 8, 'bab': 8,
          'abc': 9, 'acb': 9, 'bac': 9, 'cba': 9}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def mm(a, b):
    """Binary 2x2 product, with bit 2*i+j encoding entry i,j."""
    return sum(((sum(((a >> (2 * i + k)) & 1) * ((b >> (2 * k + j)) & 1)
                     for k in range(2)) & 1) << (2 * i + j))
               for i in range(2) for j in range(2))


MULT = tuple(tuple(mm(a, b) for b in range(16)) for a in range(16))
OUTER = {(x, y): sum((((x >> i) & 1) * ((y >> j) & 1)) << (2 * i + j)
                     for i in range(2) for j in range(2))
         for x in range(1, 4) for y in range(1, 4)}
SPLIT = {n: pair for pair, n in OUTER.items()}
COUPLINGS = tuple(sorted(SPLIT))


def total(sequence):
    value = 0
    for n in sequence:
        value ^= n
    return value


def reduced(word):
    if len(word) > 3:
        return None
    for _ in range(3):
        word = word.replace('ca', 'ac')
    require('ca' not in word, 'quotient reduction bound')
    if any(word[i] == word[i + 1] for i in range(len(word) - 1)):
        return None
    require(word in BASIS, 'quotient basis')
    return word


def q_product(left, right):
    result = set()
    for a in left:
        for b in right:
            word = reduced(a + b)
            if word is not None:
                result.symmetric_difference_update((word,))
    return frozenset(result)


def group_product(g, h):
    a, b, c, d, e, f = ((g >> i) & 1 for i in range(6))
    aa, bb, cc, dd, ee, ff = ((h >> i) & 1 for i in range(6))
    values = (a ^ aa, b ^ bb, c ^ cc, d ^ dd ^ (a & bb),
              e ^ ee ^ (b & cc), f ^ ff ^ (a & ee) ^ (d & cc))
    return sum(value << i for i, value in enumerate(values))


def fixed_algebra():
    """Construct the group-to-quotient map and check every multiplication."""
    images = {0: frozenset(('',))}
    queue = [0]
    for index in range(64):
        require(index < len(queue), 'group generation')
        g = queue[index]
        for letter, generator in zip('abc', (1, 2, 4)):
            h = group_product(g, generator)
            value = q_product(images[g], frozenset(('', letter)))
            if h not in images:
                images[h] = value
                queue.append(h)
            require(images[h] == value, 'consistent group image')
    require(len(images) == 64, 'all group elements')
    for g, h in product(range(64), repeat=2):
        require(q_product(images[g], images[h]) == images[group_product(g, h)],
                'quotient homomorphism')
    for a, b, c in product(BASIS, repeat=3):
        aa, bb, cc = (frozenset((s,)) for s in (a, b, c))
        require(q_product(q_product(aa, bb), cc) == q_product(aa, q_product(bb, cc)),
                'quotient associativity')
    require(images[32] == frozenset(('', 'abc', 'acb', 'bac', 'cba')), 'z image')
    require(images[40] == frozenset(TARGET), 'uz image')
    return {'group_products': 4096, 'quotient_associativity': 4913}


def quotient(word):
    require(len(word) <= 14, 'word length bound')
    result = {'': 9}
    for letter, n in word:
        require(letter in 'abc' and n in SPLIT, 'paid alphabet')
        updated = dict(result)
        for monomial, matrix in result.items():
            name = reduced(monomial + letter)
            if name is not None:
                updated[name] = updated.get(name, 0) ^ MULT[matrix][n]
        result = {name: matrix for name, matrix in updated.items() if matrix}
    return result


def gap_catalogue():
    """All four-call outer words, in all six gaps, retaining realizations."""
    catalogue = defaultdict(list)
    zero_sequences = 0
    for ns in product(COUPLINGS, repeat=4):
        if total(ns):
            continue
        zero_sequences += 1
        for positions in combinations_with_replacement(range(6), 4):
            sums = [0] * 6
            for n, gap in zip(ns, positions):
                sums[gap] ^= n
            profile, running = [], 0
            for gap in range(5):
                running ^= sums[gap]
                profile.append(running)
            catalogue[tuple(profile)].append((ns, positions))
    return dict(catalogue), zero_sequences


def side_table(middle):
    """Packed AB, BA, ABA, BAB coefficients of a zero-total outer profile."""
    result = []
    for j, n in enumerate(middle):
        left, right = total(middle[:j]), total(middle[j + 1:])
        row = []
        for p in range(16):
            pn, np = MULT[p][n], MULT[n][p]
            bab = MULT[MULT[left][p]][n] ^ MULT[np][right]
            row.append(pn | (np << 4) | (MULT[pn][p] << 8) | (bab << 12))
        result.append(row)
    return result


def profile_key(middle, profile):
    """Column/row bit strings for each transported middle coupling."""
    u0 = u1 = w0 = w1 = 0
    for j, (n, p) in enumerate(zip(middle, profile)):
        x, y = SPLIT[n]
        px = ((p & 1) * (x & 1)) ^ (((p >> 1) & 1) * ((x >> 1) & 1))
        px |= ((((p >> 2) & 1) * (x & 1)) ^ (((p >> 3) & 1) * ((x >> 1) & 1))) << 1
        yp = ((y & 1) * (p & 1)) ^ (((y >> 1) & 1) * ((p >> 2) & 1))
        yp |= (((y & 1) * ((p >> 1) & 1)) ^ (((y >> 1) & 1) * ((p >> 3) & 1))) << 1
        u0 |= (px & 1) << j
        u1 |= (px >> 1) << j
        w0 |= (yp & 1) << j
        w1 |= (yp >> 1) << j
    return u0, u1, w0, w1


def cross_key(a, c):
    abc = cba = 0
    for i, j in product(range(2), repeat=2):
        abc |= ((a[i] & c[2 + j]).bit_count() & 1) << (2 * i + j)
        cba |= ((c[i] & a[2 + j]).bit_count() & 1) << (2 * i + j)
    return abc, cba


def screened_profiles(middle, profiles):
    table = side_table(middle)
    a, c = defaultdict(list), defaultdict(list)
    for profile in profiles:
        value = table[0][profile[0]] ^ table[1][profile[1]] ^ table[2][profile[2]]
        value ^= table[3][profile[3]] ^ table[4][profile[4]]
        if value == 0x8888:
            a[profile_key(middle, profile)].append(profile)
        if value == 0:
            c[profile_key(middle, profile)].append(profile)
    return dict(a), dict(c)


def compatible_keys(a_keys, c_keys):
    by_rows = defaultdict(list)
    for key in c_keys:
        by_rows[key[2:]].append(key)
    for a in a_keys:
        first = [m for m in range(32) if (a[0] & m).bit_count() % 2 == 1
                 and (a[1] & m).bit_count() % 2 == 0]
        second = [m for m in range(32) if (a[0] & m).bit_count() % 2 == 0
                  and (a[1] & m).bit_count() % 2 == 1]
        for m0, m1 in product(first, second):
            for c in by_rows.get((m0, m1), ()):
                if cross_key(a, c) == (9, 9):
                    yield a, c


def gap_words(realization, letter):
    ns, positions = realization
    return tuple(tuple((letter, n) for n, position in zip(ns, positions) if position == gap)
                 for gap in range(6))


def interleavings(a, c):
    result = []
    for positions in combinations(range(len(a) + len(c)), len(a)):
        chosen = set(positions)
        ia = ic = 0
        word = []
        for index in range(len(a) + len(c)):
            if index in chosen:
                word.append(a[ia])
                ia += 1
            else:
                word.append(c[ic])
                ic += 1
        result.append(tuple(word))
    return tuple(result)


def expanded_words(middle, a_realization, c_realization):
    a, c = gap_words(a_realization, 'a'), gap_words(c_realization, 'c')
    alternatives = tuple(interleavings(aa, cc) for aa, cc in zip(a, c))
    for parts in product(*alternatives):
        word = []
        for j in range(6):
            word.extend(parts[j])
            if j < 5:
                word.append(('b', middle[j]))
        yield tuple(word)


def census():
    catalogue, zero_sequences = gap_catalogue()
    profiles = tuple(sorted(catalogue))
    counts = dict(middles=0, outer_zero_sequences=zero_sequences, profiles=len(profiles),
                  a_pass=0, c_pass=0, key_pairs=0, profile_pairs=0, words=0, q_pass=0)
    digest = sha256()
    failures = defaultdict(int)
    for middle in product(COUPLINGS, repeat=5):
        if total(middle):
            continue
        counts['middles'] += 1
        a, c = screened_profiles(middle, profiles)
        counts['a_pass'] += sum(len(ps) for ps in a.values())
        counts['c_pass'] += sum(len(ps) for ps in c.values())
        for ka, kc in compatible_keys(a, c):
            counts['key_pairs'] += 1
            for pa, pc in product(a[ka], c[kc]):
                counts['profile_pairs'] += 1
                for ra, rc in product(catalogue[pa], catalogue[pc]):
                    for word in expanded_words(middle, ra, rc):
                        image = quotient(word)
                        counts['words'] += 1
                        counts['q_pass'] += image == TARGET
                        differing = [s for s in BASIS if image.get(s, 0) != TARGET.get(s, 0)]
                        require(differing, 'unexpected 13-call quotient solution')
                        failures[differing[0]] += 1
                        digest.update(canonical([word, sorted(image.items())]) + b'\n')
    counts['expanded_transcript_sha256'] = digest.hexdigest()
    counts['first_differing_coefficient'] = dict(sorted(failures.items()))
    return counts


def formal(word, roles=3):
    """Full group-ring operator, including one arbitrary dirty role by default."""
    require(2 <= roles <= 5 and len(word) <= 14, 'formal fixture bound')
    result = [[{0} if i == j else set() for j in range(roles)] for i in range(roles)]
    generators = {'a': 1, 'b': 2, 'c': 4}
    for letter, n in word:
        require(letter in generators and n in SPLIT, 'paid formal alphabet')
        x, y = SPLIT[n]
        for i in range(roles):
            increment = set()
            for k in range(2):
                if (x >> k) & 1:
                    for g in result[i][k]:
                        increment.symmetric_difference_update((g, group_product(g, generators[letter])))
            for j in range(2):
                if (y >> j) & 1:
                    result[i][j].symmetric_difference_update(increment)
    return [[sorted(entry) for entry in row] for row in result]


def positive_and_controls():
    word = tuple((letter, n) for letters, n in (('abcbabcb', 1), ('acbabc', 8))
                 for letter in letters)
    expected = [[([32, 40, 0][i:i + 1] if i == j else []) for j in range(3)] for i in range(3)]
    require(formal(word) == expected and quotient(word) == TARGET, '14-call full formal witness')
    for index in range(14):
        omitted = word[:index] + word[index + 1:]
        require(formal(omitted) != expected, 'omitted-call control')
    changed = list(word)
    changed[0] = ('c', changed[0][1])
    require(formal(changed) != expected, 'wrong-letter control')
    return {'full_word': [list(step) for step in word], 'formal_roles': 3, 'formal_basis_columns': 192,
            'omitted_call_controls': 14, 'wrong_letter_controls': 1}


def check_sources():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    for item in sources['files']:
        if item['usage'] == 'input':
            data = (ROOT / item['path']).read_bytes()
            require(sha256(data).hexdigest() == item['sha256'], 'source digest: ' + item['path'])


def check_receipt(actual, path):
    expected = json.loads(path.read_text())
    require(canonical(actual) == canonical(expected), 'receipt mismatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', type=Path, help='write a receipt to a new path')
    args = parser.parse_args()
    if args.emit:
        require(not args.emit.exists(), 'refuse existing receipt')
    check_sources()
    result = {'algebra': fixed_algebra(), 'positive': positive_and_controls(), 'census': census()}
    if args.emit:
        payload = json.dumps(result, sort_keys=True, indent=2) + '\n'
        with args.emit.open('x') as output:
            require(output.write(payload) == len(payload), 'receipt write length')
    else:
        check_receipt(result, HERE / 'EXPECTED.json')
    counts = result['census']
    print('PASS_UT4_MIXED_CENTRAL_MIDDLE minimum=14 '
          f"middles={counts['middles']} words={counts['words']} q_pass={counts['q_pass']} no_new_kappa")


if __name__ == '__main__':
    main()
