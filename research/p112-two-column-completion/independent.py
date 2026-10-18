#!/usr/bin/env python3
"""Independent integer-minor audit; imports no primary/predecessor checker.
Apache-2.0. Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
from collections import Counter
from hashlib import sha256
from fractions import Fraction
from itertools import combinations, product
from math import gcd
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json'
SOURCE_SHA = '327d2a868043e846381aa58a33053c24425e8cad522ff401b10ec8af1d649a3f'


def check(ok, message):
    if not ok:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def determinant(rows):
    """Bareiss determinant over Z, including row swaps and divisibility checks."""
    a = [list(r) for r in rows]
    n = len(a)
    check(all(len(r) == n for r in a), 'square minor')
    previous, sign = 1, 1
    for col in range(n - 1):
        pivot = next((i for i in range(col, n) if a[i][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            sign = -sign
        value = a[col][col]
        for i in range(col + 1, n):
            for j in range(col + 1, n):
                numerator = a[i][j] * value - a[i][col] * a[col][j]
                check(numerator % previous == 0, 'Bareiss exact division')
                a[i][j] = numerator // previous
            a[i][col] = 0
        previous = value
    return sign * (a[-1][-1] if n else 1)


def rational_rank(rows):
    """Exact row rank by integral elimination with primitive-row reduction."""
    if not rows:
        return 0
    a = [list(r) for r in rows]
    width, height = len(a[0]), len(a)
    check(all(len(r) == width for r in a), 'rectangular integer matrix')
    r = 0
    for col in range(width):
        pivot = next((i for i in range(r, height) if a[i][col]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        p = a[r][col]
        for i in range(r + 1, height):
            q = a[i][col]
            if not q:
                continue
            tail = [p * a[i][j] - q * a[r][j] for j in range(col, width)]
            divisor = 0
            for value in tail:
                divisor = gcd(divisor, value)
            if divisor:
                tail = [v // divisor for v in tail]
            a[i][col:] = tail
        r += 1
        if r == min(width, height):
            break
    return r


def independent_roots(source):
    # The standard E8 model used by PR1447, at squared norm eight.
    standard = set()
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            x = [0] * 8; x[i], x[j] = a, b
            standard.add(max(tuple(x), tuple(-v for v in x)))
    for x in product((-1, 1), repeat=8):
        if sum(v < 0 for v in x) % 2 == 0:
            standard.add(max(x, tuple(-v for v in x)))
    # Block matrix H/2 takes (2,+/-2) frame roots to the coordinate axes.
    rotated = set()
    for x in standard:
        y = tuple(v for i in range(0, 8, 2)
                  for v in ((x[i] + x[i + 1]) // 2, (x[i] - x[i + 1]) // 2))
        check(all((x[i] + x[i + 1]) % 2 == 0 for i in range(0, 8, 2)), 'integral rotation')
        rotated.add(max(y, tuple(-v for v in y)))
    exported = [tuple(x) for x in source['root_lines']]
    check(len(standard) == len(rotated) == 120, 'complete independent E8 enumeration')
    check(len(exported) == 120 and set(exported) == rotated, 'source root-set isometry')
    check(exported[:8] == [tuple(2 * int(i == j) for j in range(8)) for i in range(8)],
          'same punctured frame')
    return exported[8:]


def check_minor(roots, rows, columns, allowed, size):
    check(len(rows) == len(set(rows)) == size, 'minor row multiplicity')
    check(len(columns) == len(set(columns)) == size, 'minor column multiplicity')
    check(all(type(i) is int and i in allowed for i in rows), 'minor outside required roots')
    check(all(type(j) is int and 0 <= j < 8 for j in columns), 'minor coordinate range')
    value = determinant([[roots[i][j] for j in columns] for i in rows])
    check(value != 0, 'singular claimed minor')
    return abs(value)


def audit_census(roots, gram, cert):
    singles, pairs = cert['singletons'], cert['pairs']
    check(len(singles) == 112 and len(pairs) == 6216, 'complete census cardinality')
    determinants = Counter()
    histogram = Counter()
    for j, record in enumerate(singles):
        check(len(record) == 4 and record[0] == j, 'singleton coverage')
        allowed = {i for i in range(112) if gram[i][j] not in (-2, 2)}
        check(record[1] == len(allowed) == 60, 'singleton constrained row count')
        determinants[check_minor(roots, record[2], record[3], allowed, 8)] += 1
    for (j, k), record in zip(combinations(range(112), 2), pairs):
        check(len(record) == 8 and record[:3] == [j, k, gram[j][k]], 'pair coverage and parity')
        allowed = {i for i in range(112) if gram[i][j] not in (-2, 2) and gram[i][k] not in (-2, 2)}
        odd = gram[j][k] in (-2, 2)
        size = 6 if odd else 8
        check(record[3] == len(allowed), 'common constrained row count')
        if odd:
            check(all(dot(roots[i], roots[j]) == dot(roots[i], roots[k]) == 0 for i in allowed),
                  'complex-rank-six upper-bound premise')
            check(16 - gram[j][k] ** 2 != 0, 'independent normals')
        determinants[check_minor(roots, record[4], record[5], allowed, size)] += 1
        determinants[check_minor(roots, record[6], record[7], set(range(112)) - {j, k}, 8)] += 1
        histogram[('odd' if odd else 'orthogonal') + '|' + str(len(allowed)) + '|' + str(size)] += 1
    expected_pairs = [(j, k) for j, k in combinations(range(112), 2) if gram[j][k] in (-2, 2)]
    check(len(cert['odd_pencils']) == 2912, 'all odd pencils')
    for (j, k), record in zip(expected_pairs, cert['odd_pencils']):
        check(len(record) == 4 and record[:2] == [j, k], 'pencil coverage')
        active = sum(bool(row[j] or row[k]) for row in gram)
        check(record[2] == active, 'pencil generic support')
        # Independent classification by finite slopes b/a, with None for infinity.
        slopes = {(-Fraction(row[j], row[k]) if row[k] else None)
                  for row in gram if row[j] or row[k]}
        seen = set()
        supports = []
        for a, b, size in record[3]:
            check(type(a) is int and type(b) is int and (a or b), 'nonzero pencil direction')
            check(gcd(a, b) == 1 and (a > 0 or (a == 0 and b > 0)), 'canonical direction')
            slope = Fraction(b, a) if a else None
            check(slope not in seen, 'duplicate pencil stratum')
            seen.add(slope)
            actual = sum(a * row[j] + b * row[k] != 0 for row in gram)
            check(size == actual and size >= 53, 'exact pencil support floor')
            supports.append(size)
        check(seen == slopes and min(supports) == 53, 'complete projective exceptional slopes')
        check(Fraction(3) not in slopes and sum(row[j] + 3 * row[k] != 0 for row in gram) == active,
              'generic complex-direction support')
    return dict(sorted(histogram.items())), dict(sorted(determinants.items()))


def audit_result(roots, gram, result, cert):
    canonical = json.dumps(cert, sort_keys=True, separators=(',', ':')).encode()
    check(sha256(canonical).hexdigest() == result['census_sha256'], 'census commitment')
    check(result['source_sha256'] == SOURCE_SHA, 'result source binding')
    check(result['singletons_checked'] == 112 and result['unordered_pairs_checked'] == 6216,
          'reported census size')
    check(result['odd_pairs'] == 2912 and result['orthogonal_pairs'] == 3304, 'pair class counts')
    check(result['odd_pencils_checked'] == 2912 and result['two_column_failure_row_floor'] == 53, 'pencil summary')
    check(result['gram_rank'] == rational_rank(gram) == 8, 'Gram rank')
    check(result['odd_degree'] == 52 and all(sum(v in (-2, 2) for v in row) == 52 for row in gram),
          'rank-one rectangle cardinality bound')
    check(result['frame_constant'] == 56, 'projection factor')
    check([[sum(r[a] * r[b] for r in roots) for b in range(8)] for a in range(8)] ==
          [[56 * int(a == b) for b in range(8)] for a in range(8)], 'projection kernel')
    expected_names = ['odd_pair_rank9', 'odd_pair_rank10', 'orthogonal_pair_rank10',
                      'maximal_one_column_rank9', 'wide_rank1_rectangle']
    check([w['name'] for w in result['witnesses']] == expected_names, 'witness inventory')
    for w in result['witnesses']:
        q = [[0] * 112 for _ in range(112)]
        seen = set()
        for i, j, value in w['nonzero_entries']:
            check(type(value) is int and value != 0, 'nonzero integer witness entry')
            check(0 <= i < 112 and 0 <= j < 112 and (i, j) not in seen, 'unique witness entry')
            check(gram[i][j] in (-2, 2), 'witness violates odd mask')
            seen.add((i, j)); q[i][j] = value
        cols = sorted({j for i, j in seen})
        check(cols == w['columns'] and len({i for i, j in seen}) == w['row_support'], 'witness support')
        y = [[row[j] for j in cols] for row in q]
        total = [[gram[i][j] + q[i][j] for j in range(112)] for i in range(112)]
        check(rational_rank(y) == w['correction_rank'], 'independent correction rank')
        check(rational_rank(total) == w['completion_rank'], 'independent completion rank')
        residual = [[56 * y[i][a] - sum(gram[i][t] * y[t][a] for t in range(112))
                     for a in range(len(cols))] for i in range(112)]
        check(rational_rank(residual) == w['projection_rank'], 'independent projection rank')
    sharp = result['witnesses'][0]
    j, k = sharp['columns']
    supports = [([i for i in range(112) if roots[i][a]],
                 [i for i in range(112) if roots[i][a] and i != j]) for a in range(8)]
    supports.append(([j], [j, k]))
    copy_ranks = []
    for left, right in supports:
        # Set symmetric differences, with smallest pivots, instead of bit elimination.
        basis = {}
        for i in left:
            row = {col for col in right if (gram[i][col] // 2 + 1) % 2}
            while row and min(row) in basis:
                row ^= basis[min(row)]
            if row:
                basis[min(row)] = row
        copy_ranks.append(len(basis))
    check(copy_ranks == sharp['displayed_factorization_copy_ranks'] == [8] * 8 + [1] and
          sharp['displayed_factorization_copy_total'] == sum(copy_ranks) == 65, 'separate COPY invoice')
    check(sharp['row_support'] == 53 and len(sharp['columns']) == 2 and
          sharp['correction_rank'] == 2 and sharp['completion_rank'] == 9, 'sharp masked boundary')


def run():
    raw = (ROOT / SOURCE).read_bytes()
    check(sha256(raw).hexdigest() == SOURCE_SHA, 'input bytes')
    source = json.loads(raw)
    roots = independent_roots(source)
    gram = [[dot(x, y) for y in roots] for x in roots]
    cert = json.loads((HERE / 'CENSUS.json').read_text())
    result = json.loads((HERE / 'RESULT.json').read_text())
    hist, determinants = audit_census(roots, gram, cert)
    check(hist == result['pair_class_histogram'], 'reported class histogram')
    check(sum(determinants.values()) == 12544, 'all exact minors')
    audit_result(roots, gram, result, cert)
    return {'integer_minors': 12544, 'witnesses': len(result['witnesses']),
            'absolute_determinant_histogram': determinants}


if __name__ == '__main__':
    out = run()
    print('PASS_P112_TWO_COLUMN_INDEPENDENT integer_minors=12544 pencils=2912 witnesses=5 root_isometry=120')
