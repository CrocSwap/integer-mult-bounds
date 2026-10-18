#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact support-matching cost controls; no predecessor code is imported."""
import argparse
from fractions import Fraction as Q
import hashlib
import io
import itertools
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDIT = 'research/kport-group-scalar-endpoint-audit/'
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
PAYLOAD_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sources():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    bound = {}
    for pin in manifest['files']:
        if pin['usage'] != 'input':
            continue
        raw = (ROOT / pin['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256: ' + pin['path'])
        blob = hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest()
        need(blob == pin['git_blob'], 'source Git blob: ' + pin['path'])
        bound[pin['path']] = raw
    # Authenticate every external input before parsing any scientific data.
    with tarfile.open(fileobj=io.BytesIO(bound[ARCHIVE]), mode='r:gz') as archive:
        stream = archive.extractfile(MEMBER)
        need(stream is not None, 'selected member missing')
        payload = stream.read(2_000_001)
    need(len(payload) <= 2_000_000, 'selected member capacity')
    need(hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA, 'selected member SHA256')
    recipes = sorted(json.loads(payload)['recipes'], key=lambda x: x['port'])
    need([r['port'] for r in recipes] == list(range(112)), '112 selected ports')
    labels = [r['q'] for r in recipes]
    need(len(set(labels)) == 112 and all(type(q) is int and 0 < q < 512 for q in labels), 'labels')
    return bound, labels


def dot(a, b):
    return (a & b).bit_count() % 2


def span(vectors):
    values = {0}
    for vector in vectors:
        values |= {x ^ vector for x in values}
    return values


def binary_rank(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def dense_rank(matrix, binary=False):
    a = [[Q(x) for x in row] for row in matrix]
    rank = 0
    for col in range(len(a[0]) if a else 0):
        pivot = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        scale = a[rank][col]
        a[rank] = [x / scale for x in a[rank]]
        for i in range(rank + 1, len(a)):
            scale = a[i][col]
            a[i] = [x - scale * y for x, y in zip(a[i], a[rank])]
            if binary:
                a[i] = [Q(int(x) % 2) for x in a[i]]
        rank += 1
        if rank == len(a):
            break
    return rank


def pairing(left, right):
    matrix = [[dot(a, b) for b in right] for a in left]
    packed = [sum(x << j for j, x in enumerate(row)) for row in matrix]
    rank = binary_rank(packed)
    need(rank == dense_rank(matrix, binary=True), 'independent binary ranks disagree')
    return rank


def injection(matrix):
    """Return distinct nonzero columns for all rows, or fail (augmenting paths)."""
    owner = {}

    def augment(row, seen):
        for col, value in enumerate(matrix[row]):
            if not value or col in seen:
                continue
            seen.add(col)
            if col not in owner or augment(owner[col], seen):
                owner[col] = row
                return True
        return False

    need(all(augment(i, set()) for i in range(len(matrix))), 'no full support matching')
    result = [next(c for c, r in owner.items() if r == i) for i in range(len(matrix))]
    need(len(set(result)) == len(matrix), 'matching injectivity')
    return result


def analyze_cover(pr, bound, labels):
    candidate = json.loads(bound[AUDIT + 'fixtures/' + pr + '-CANDIDATE.json'])
    candidate = candidate.get('candidate', candidate)
    groups = candidate.get('blocks', candidate.get('groups'))
    need(sorted(p for group in groups for p in group) == list(range(112)), 'partition')
    spaces = [[labels[p] for p in group] for group in groups]
    for group in spaces:
        need(all(dot(a, b) == (i == j) for i, a in enumerate(group) for j, b in enumerate(group)), 'orthonormal port space')
        need(pairing(group, group) == len(group), 'nondegenerate port space')
    orthogonal = [(i, j) for i in range(len(groups)) for j in range(i + 1, len(groups))
                  if pairing(spaces[i], spaces[j]) == 0]
    if pr == 'PR2297':
        chosen = list(range(len(groups)))
        need(not orthogonal, 'five-port mask must have no free pairs')
    else:
        triples = [i for i, g in enumerate(groups) if len(g) == 3]
        conflicts = [(i, j) for i, j in orthogonal if i in triples and j in triples]
        need(conflicts == [(6, 13), (7, 12), (9, 19), (22, 25)], 'triad conflict witness')
        chosen = [i for i in triples if i not in {a for a, _ in conflicts}]
    need(all((min(i, j), max(i, j)) not in orthogonal for i in chosen for j in chosen if i != j), 'principal set has a free pair')
    ports = sorted(p for i in chosen for p in groups[i])
    dimensions = {p: len(group) for group in groups for p in group}
    floor = sum(dimensions[p] for p in ports)
    direct = sum(len(group) * pairing(space, space) for group, space in zip(groups, spaces))
    budget = Q(8, 9) * sum(dimensions.values())
    expected_floor = 554 if pr == 'PR2297' else 297
    need(floor == expected_floor and floor > budget, 'unfavorable exact relaxed budget')
    required_credit = floor - (budget.numerator // budget.denominator)
    necessary_terms = 1
    if pr == 'PR2297':
        max_credit = max(dimensions[p] for p in ports) - 1
        necessary_terms = (required_credit + max_credit - 1) // max_credit
        need(required_credit == 62 and necessary_terms == 16, 'asymmetry budget')
        need(floor-15*max_credit > budget, 'fifteen low-rank asymmetric terms cannot suffice')
    return dict(pr=pr, group_sizes=sorted(map(len, groups)), nonfree_groups=chosen,
                nonfree_ports=ports, principal_rank=len(ports), matched_span_floor=floor,
                direct_charge=direct, unpaid_budget=str(budget), deficit_upper=str(budget-floor),
                orthogonal_group_pairs=[list(x) for x in orthogonal],
                required_asymmetry_credit=required_credit,
                # The max-credit bound uses a globally nonfree mask for k=5.
                necessary_low_rank_asymmetric_terms=necessary_terms,
                sharp=(pr == 'PR2297'))


def decoder_fixture(a, b, weights, spaces):
    n, terms = len(a), len(weights)
    need(len(b) == n and all(len(row) == terms for row in a+b), 'factor shape')
    for t in range(terms):
        need(weights[t] != 0, 'zero term')
        left = [v for i in range(n) if a[i][t] for v in spaces[i]]
        right = [v for i in range(n) if b[i][t] for v in spaces[i]]
        need(span(left) == span(right), 'unequal complete port spans')
    k = [[sum(weights[t]*a[i][t]*b[j][t] for t in range(terms)) for j in range(n)] for i in range(n)]
    need(k == [[Q(i == j) for j in range(n)] for i in range(n)], 'strict scalar identity')
    need(dense_rank(k) == n and dense_rank(a) == n, 'full rational rank')
    matched = injection(a)
    prices = []
    for t in range(terms):
        left = [v for i in range(n) if a[i][t] for v in spaces[i]]
        right = [v for i in range(n) if b[i][t] for v in spaces[i]]
        prices.append(pairing(left, right))
    dims = [pairing(s, s) for s in spaces]
    need(all(dims[i] == len(s) for i, s in enumerate(spaces)), 'degenerate port space')
    need(all(prices[matched[i]] >= dims[i] for i in range(n)), 'matched port cost')
    need(sum(prices) >= sum(dims), 'matching floor')
    return dict(terms=terms, weights=list(map(str, weights)), matching=matched, cost=sum(prices))


def controls():
    fixtures = []
    spaces = [[1], [1]]  # nonfree mask; each line is nondegenerate.
    fixtures.append(decoder_fixture([[1, 1], [1, -1]], [[1, 1], [1, -1]], [Q(1, 2)]*2, spaces))
    fixtures.append(decoder_fixture([[1, 1], [1, 2]], [[2, -1], [-1, 1]], [Q(1)]*2, spaces))
    fixtures.append(decoder_fixture([[1, 1], [0, 1]], [[1, 0], [-1, 1]], [Q(1)]*2, spaces))
    quarter = [[1, 1, 1, 1, 1, 1], [1, 1, -1, -1, 1, 1]]
    fixtures.append(decoder_fixture(quarter, quarter, [Q(1, 4)]*4+[Q(1, 3), -Q(1, 3)], spaces))
    full_rank = 0
    for bits in itertools.product((0, 1), repeat=9):
        a = [bits[i:i+3] for i in range(0, 9, 3)]
        x, y, z = a
        determinant = x[0]*(y[1]*z[2]-y[2]*z[1])-x[1]*(y[0]*z[2]-y[2]*z[0])+x[2]*(y[0]*z[1]-y[1]*z[0])
        nonsingular = dense_rank(a) == 3
        need(nonsingular == (determinant != 0), 'rational rank versus literal determinant')
        if nonsingular:
            injection(a)
            full_rank += 1
    need(full_rank == 174, 'complete 3x3 binary rational-rank census')
    rejected = []

    def rejects(name, fn):
        try:
            fn()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('control accepted: ' + name)

    rejects('unmatched_row', lambda: injection([[1, 0], [1, 0]]))
    rejects('unequal_complete_port_spans', lambda: decoder_fixture([[1, 1], [0, 1]], [[1, 0], [-1, 1]], [Q(1)]*2, [[1, 2], [1]]))
    rejects('wrong_diagonal', lambda: decoder_fixture([[1]], [[1]], [Q(1, 4)], [[1]]))
    rejects('forbidden_scalar_cross_entry', lambda: decoder_fixture([[1], [1]], [[1], [1]], [Q(1)], spaces))
    rejects('degenerate_space', lambda: decoder_fixture([[1]], [[1]], [Q(1)], [[3]]))
    rejects('label_only_undercharge', lambda: need(sum(pairing([q], [q]) for q in (1, 2, 4)) == 1, 'three-dimensional port costs three'))
    # A valid free-pair mask need not force a nonsingular principal matrix.
    need(dot(1, 2) == 0 and dense_rank([[1, 1], [1, 1]]) == 1, 'free-pair escape')
    rejects('free_pair_in_fullrank_argument', lambda: need(dense_rank([[1, 1], [1, 1]]) == 2, 'free pair does not force full rank'))
    # This exact identity is outside the equal-span class. One term loses
    # its source port's own Gram minor; (2) remains valid and is only necessary.
    a, b = [[1, 1], [0, 1]], [[1, 0], [-1, 1]]
    asymmetric_spaces = [[1, 2], [1]]
    k = [[sum(a[i][t]*b[j][t] for t in range(2)) for j in range(2)] for i in range(2)]
    need(k == [[1, 0], [0, 1]], 'asymmetric identity control')
    prices, credit = [], []
    for t in range(2):
        left = [v for i in range(2) if a[i][t] for v in asymmetric_spaces[i]]
        right = [v for i in range(2) if b[i][t] for v in asymmetric_spaces[i]]
        price = pairing(left, right)
        prices.append(price)
        credit.append(max([0]+[len(asymmetric_spaces[i])-price for i in range(2) if a[i][t]]))
    need(prices == [2, 1] and credit == [0, 1], 'asymmetry-credit control')
    need(sum(prices) >= 3-sum(credit), 'asymmetric matching bound')
    return dict(fixtures=fixtures, full_rank_binary_3x3=full_rank, controls=rejected,
                asymmetric_fixture=dict(costs=prices, credit=credit, cost=sum(prices), dimension_sum=3))


def compute():
    bound, labels = sources()
    results = [analyze_cover(pr, bound, labels) for pr in ('PR2297', 'PR2041')]
    old = json.loads(bound[AUDIT+'RESULT.json'])['results']
    need([r['direct_charge'] for r in results] == [r['direct_charge'] for r in old], 'predecessor direct-price cross-check')
    return dict(schema_version=1, status='SCOPED_MATCHED_PORT_SPAN_OBSTRUCTION',
                results=results, tests=controls(), no_new_kappa=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = compute()
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.write:
        with args.write.open('x') as stream:
            stream.write(encoded)
    else:
        need(encoded == (HERE/'RESULT.json').read_text(), 'complete typed result mismatch')
    print('PASS_MATCHED_PORT_SPAN_FLOOR k5>=554 k3>=297 deficits<=-554/9,-1/9 no_new_kappa')


if __name__ == '__main__':
    main()
