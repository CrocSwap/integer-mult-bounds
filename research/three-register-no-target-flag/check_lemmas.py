#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent finite and symbolic checks for the three-register corank-two lemma.

Python 3.9+, standard library only. No original search implementation is imported.
The bounded word census checks the stated bilinear gap criterion on words through
length eight by default; it is not a proof of the all-length mathematical lemma.

Run this file to emit a compact deterministic JSON certificate. Import
build_certificate() to obtain the same JSON-compatible object. Explicit checks
remain active under python -O. All matrix encodings use row-major binary bits.
"""
import argparse
from collections import Counter
from copy import deepcopy
from itertools import combinations, permutations, product
import json
from pathlib import Path

IDENTITY = 0b100010001
J = 511
COORDINATES = (1, 16, 256)
OFF_MASK = 0b011101110
LOWER_MASK = (1 << 3) | (1 << 6) | (1 << 7)
REPRESENTATIVE = (3, 18, 360)


class CheckFailure(ValueError):
    """A supplied claim or certificate failed an exact check."""


def require(condition, message):
    if not condition:
        raise CheckFailure(message)


def parity(value):
    return bin(value).count('1') % 2


def action(matrix, vector):
    return sum(parity((matrix >> (3 * i)) & vector) << i for i in range(3))


def multiply(a, b):
    return sum((sum(((a >> (3 * i + k)) & 1) * ((b >> (3 * k + j)) & 1)
                    for k in range(3)) % 2) << (3 * i + j)
               for i in range(3) for j in range(3))


def outer(x, y):
    return sum(((x >> i) & 1) * ((y >> j) & 1) << (3 * i + j)
               for i in range(3) for j in range(3))


def basis(a, b, c):
    return sum(((x >> i) & 1) << (3 * i + j)
               for j, x in enumerate((a, b, c)) for i in range(3))


def independent(a, b, c):
    return len({0, a, b, c, a ^ b, a ^ c, b ^ c, a ^ b ^ c}) == 8


def binary_rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def scalar_universe():
    """Construct projectors as outer products and flags from invertible bases."""
    projectors = sorted({outer(x, y) for x in range(1, 8) for y in range(1, 8)
                         if parity(x & y)})
    require(len(projectors) == 28, 'projector count')
    require(all(multiply(p, p) == p for p in projectors), 'projector idempotence')
    patterns = sorted({p & OFF_MASK for p in projectors} - {0})
    planes = sorted({tuple(sorted((0, p, q, p ^ q)))
                     for p, q in combinations(patterns, 2)})
    require(len(patterns) == 19 and len(planes) == 129, 'pattern counts')
    gl = sorted({basis(a, b, c) for a, b, c in product(range(1, 8), repeat=3)
                 if independent(a, b, c)})
    require(len(gl) == 168, 'GL(3,2) count')
    inverses = {s: next(t for t in gl if multiply(s, t) == IDENTITY
                       and multiply(t, s) == IDENTITY) for s in gl}
    flags = {}
    for s in gl:
        a, b = (action(s, x) for x in (1, 2))
        key = (a, tuple(sorted((0, a, b, a ^ b))))
        flags.setdefault(key, s)
    require(len(flags) == 21, 'complete flag count')
    return projectors, patterns, planes, gl, inverses, list(flags.values())


def conjugates(pool, s, inverses):
    require(s in inverses, 'flag/conjugation basis must be invertible')
    return [multiply(multiply(inverses[s], p), s) for p in pool]


def flag_witness(pool, inverses, flag_bases):
    return next((s for s in flag_bases
                 if all(p & LOWER_MASK == 0 for p in conjugates(pool, s, inverses))), None)


def expected_exceptions(inverses):
    coordinate_permutations = [basis(*(1 << i for i in perm))
                               for perm in permutations(range(3))]
    return {tuple(sorted(conjugates(REPRESENTATIVE, s, inverses)))
            for s in coordinate_permutations}


def build_scalar_certificate(universe):
    projectors, _, planes, _, inverses, flag_bases = universe
    records = []
    for plane in planes:
        pool = [p for p in projectors if (p & OFF_MASK) in plane and (p & OFF_MASK)]
        s = flag_witness(pool, inverses, flag_bases)
        record = {'pattern_plane': list(plane), 'pool': pool, 'flag_basis': s}
        if s is None:
            record['proper_subset_flag_bases'] = [
                flag_witness(pool[:j] + pool[j + 1:], inverses, flag_bases)
                for j in range(len(pool))]
        else:
            record['upper_triangular_conjugates'] = conjugates(pool, s, inverses)
        records.append(record)
    s = basis(1, 3, 4)
    return {'planes': records,
            'exceptional_normalization': {
                'basis': s, 'projectors': list(REPRESENTATIVE),
                'conjugates': conjugates(REPRESENTATIVE, s, inverses)}}


def verify_scalar_certificate(certificate, universe=None):
    """Validate complete plane coverage and every supplied matrix witness."""
    if universe is None:
        universe = scalar_universe()
    projectors, _, planes, _, inverses, flag_bases = universe
    records = certificate['planes']
    require(len(records) == len(planes), 'complete pattern-plane coverage')
    require([tuple(r['pattern_plane']) for r in records] == planes,
            'canonical complete pattern-plane list')
    exceptions = []
    for record, plane in zip(records, planes):
        pool = [p for p in projectors if (p & OFF_MASK) in plane and (p & OFF_MASK)]
        require(record['pool'] == pool, 'complete nonzero-pattern projector pool')
        s = record['flag_basis']
        if s is None:
            require(flag_witness(pool, inverses, flag_bases) is None, 'exception has no flag')
            require(len(pool) == 3, 'exception pool size')
            proper = record['proper_subset_flag_bases']
            require(len(proper) == 3, 'proper-subset witness count')
            for j, witness in enumerate(proper):
                images = conjugates(pool[:j] + pool[j + 1:], witness, inverses)
                require(all(p & LOWER_MASK == 0 for p in images), 'proper-subset flag')
            exceptions.append(tuple(pool))
        else:
            images = conjugates(pool, s, inverses)
            require(record['upper_triangular_conjugates'] == images, 'flag conjugation values')
            require(all(p & LOWER_MASK == 0 for p in images), 'common-flag triangularity')
    require(set(exceptions) == expected_exceptions(inverses) and len(exceptions) == 6,
            'exact exceptional coordinate-permutation orbit')
    normalization = certificate['exceptional_normalization']
    require(normalization['projectors'] == list(REPRESENTATIVE), 'exception representative')
    images = conjugates(REPRESENTATIVE, normalization['basis'], inverses)
    require(normalization['conjugates'] == images == [COORDINATES[0], COORDINATES[1], J],
            'exceptional conjugation certificate')
    return len(exceptions)


def bilinear_factor(columns):
    """Return pure-set linear factors, () for zero, or None for rank >= 2."""
    support = [(i, column) for i, column in enumerate(columns) if column]
    if not support:
        return ()
    left = support[0][1]
    if any(column != left for _, column in support):
        return None
    return left, sum(1 << i for i, _ in support)


def bilinear_word_claim(word, claimed_common_divisor=None):
    """Check the quadratic gap criterion for one word (0=J; 1,2,3=E0,E1,E2)."""
    require(all(type(label) is int and 0 <= label <= 3 for label in word), 'word alphabet')
    h = word.count(0)
    require(h > 0, 'word must contain J')
    prefix_count = 0
    f, g, gaps = [], [], set()
    for label in word:
        if label == 0:
            prefix_count += 1
        else:
            # Eliminate the last J variable by L=0. The complete prefix vanishes.
            prefix = (1 << prefix_count) - 1 if prefix_count < h else 0
            f.append(prefix if label in (1, 2) else 0)
            g.append(prefix if label in (1, 3) else 0)
            if 0 < prefix_count < h:
                gaps.add(prefix_count)
    ff, gg = bilinear_factor(f), bilinear_factor(g)
    if ff is None or gg is None:
        common = False
    elif not ff or not gg:
        common = True
    else:
        common = ff[0] == gg[0] or ff[1] == gg[1]
    require(common == (len(gaps) <= 1), 'bilinear common-divisor gap criterion')
    if claimed_common_divisor is not None:
        require(claimed_common_divisor is common, 'claimed common linear divisor')
    return common


def word_census(max_length):
    require(type(max_length) is int and 0 <= max_length <= 10, 'word census length 0..10')
    counts, passing = Counter(), Counter()
    for length in range(1, max_length + 1):
        for word in product(range(4), repeat=length):
            if 0 not in word:
                continue
            counts[length] += 1
            passing[length] += bilinear_word_claim(word)
    return {'maximum_length': max_length, 'words_checked': sum(counts.values()),
            'words_by_length': {str(n): counts[n] for n in sorted(counts)},
            'words_with_common_divisor': sum(passing.values()),
            'common_divisor_words_by_length': {str(n): passing[n] for n in sorted(passing)},
            'scope': 'bounded consistency check; not the all-length proof'}


# Exact polynomial ring F2[b,c,d0,d1,d2], represented by sets of monomials.
ZERO = frozenset()
ONE = frozenset({(0, 0, 0, 0, 0)})


def poly_add(*polynomials):
    result = set()
    for polynomial in polynomials:
        result.symmetric_difference_update(polynomial)
    return frozenset(result)


def poly_multiply(a, b):
    result = set()
    for m in a:
        for n in b:
            monomial = tuple(x + y for x, y in zip(m, n))
            if monomial in result:
                result.remove(monomial)
            else:
                result.add(monomial)
    return frozenset(result)


def variable(i):
    return frozenset({tuple(int(i == j) for j in range(5))})


def poly_matrix_multiply(a, b):
    return [[poly_add(*(poly_multiply(a[i][k], b[k][j]) for k in range(3)))
             for j in range(3)] for i in range(3)]


def common_j_factor(z):
    return [[poly_add(ONE if i == j else ZERO, z, ONE)
             for j in range(3)] for i in range(3)]


def check_product_formula(include_cross_term=True):
    """Verify all nine entries of U(b)DU(c), plus three matrix identities."""
    b, c, *diagonal = [variable(i) for i in range(5)]
    d = [[diagonal[i] if i == j else ZERO for j in range(3)] for i in range(3)]
    actual = poly_matrix_multiply(poly_matrix_multiply(common_j_factor(b), d), common_j_factor(c))
    for i in range(3):
        for j in range(3):
            terms = [diagonal[i] if i == j else ZERO,
                     poly_multiply(poly_add(b, ONE), diagonal[j]),
                     poly_multiply(poly_add(c, ONE), diagonal[i])]
            if include_cross_term:
                terms.append(poly_multiply(poly_multiply(poly_add(b, ONE), poly_add(c, ONE)),
                                           poly_add(*diagonal)))
            require(actual[i][j] == poly_add(*terms), 'U(b)DU(c) entry formula')
    require(poly_add(actual[1][0], actual[2][0]) ==
            poly_multiply(poly_add(c, ONE), poly_add(diagonal[1], diagonal[2])),
            '10/20 difference identity')
    require(poly_add(actual[0][2], actual[1][2]) ==
            poly_multiply(poly_add(c, ONE), poly_add(diagonal[0], diagonal[1])),
            '02/12 difference identity')
    require(poly_matrix_multiply(common_j_factor(b), common_j_factor(c)) ==
            common_j_factor(poly_multiply(b, c)), 'U(b)U(c)=U(bc)')
    return 12


def check_quotient_matrices():
    k = [(multiply(J, e) ^ multiply(e, J)) & OFF_MASK for e in COORDINATES]
    require(k[0] ^ k[1] ^ k[2] == 0, 'K0+K1+K2=0')
    require(binary_rank([k[0], k[1], J & OFF_MASK, 1 << 1]) == 4,
            'K0,K1 independent modulo span(Joff,E01)')
    return {'K': k, 'J_off': J & OFF_MASK, 'E01': 1 << 1, 'combined_rank': 4}


def expect_rejected(name, operation):
    try:
        operation()
    except CheckFailure:
        return name
    raise CheckFailure('negative control was accepted: ' + name)


def negative_controls(scalar_certificate, universe):
    rejected = []
    corrupt = deepcopy(scalar_certificate)
    next(record for record in corrupt['planes'] if record['flag_basis'] is not None)['flag_basis'] = 0
    rejected.append(expect_rejected('corrupt_flag_basis',
                    lambda: verify_scalar_certificate(corrupt, universe)))
    corrupt = deepcopy(scalar_certificate)
    corrupt['exceptional_normalization']['conjugates'][-1] ^= 1
    rejected.append(expect_rejected('corrupt_exceptional_conjugation',
                    lambda: verify_scalar_certificate(corrupt, universe)))
    corrupt = deepcopy(scalar_certificate)
    index = next(i for i, record in enumerate(corrupt['planes']) if record['flag_basis'] is None)
    del corrupt['planes'][index]
    rejected.append(expect_rejected('missing_exceptional_plane',
                    lambda: verify_scalar_certificate(corrupt, universe)))
    rejected.append(expect_rejected('false_common_divisor_on_two_gap_word',
                    lambda: bilinear_word_claim((0, 1, 0, 2, 0), True)))
    rejected.append(expect_rejected('omitted_U_D_U_cross_term',
                    lambda: check_product_formula(include_cross_term=False)))
    return rejected


def build_certificate(max_word_length=8):
    """Return independently checked, deterministic, JSON-compatible evidence."""
    universe = scalar_universe()
    scalar = build_scalar_certificate(universe)
    exceptions = verify_scalar_certificate(scalar, universe)
    projectors, patterns, planes, gl, _, flags = universe
    return {'format_version': 1,
            'summary': {'projectors': len(projectors), 'nonzero_patterns': len(patterns),
                        'GL3_F2': len(gl), 'complete_flags': len(flags),
                        'pattern_planes': len(planes), 'common_flag_planes': len(planes) - exceptions,
                        'exceptional_planes': exceptions,
                        'polynomial_identities_verified': check_product_formula()},
            'scalar_certificate': scalar,
            'quotient_matrices': check_quotient_matrices(),
            'word_census': word_census(max_word_length),
            'negative_controls_rejected': negative_controls(scalar, universe)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='write JSON here instead of standard output')
    parser.add_argument('--max-word-length', type=int, default=8,
                        help='bounded consistency census length, default 8 (maximum 10)')
    args = parser.parse_args()
    data = json.dumps(build_certificate(args.max_word_length), sort_keys=True,
                      separators=(',', ':')) + '\n'
    if args.output:
        args.output.write_text(data, encoding='utf-8')
    else:
        print(data, end='')


if __name__ == '__main__':
    main()
