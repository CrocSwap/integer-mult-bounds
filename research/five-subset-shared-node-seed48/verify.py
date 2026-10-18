#!/usr/bin/env python3
"""Five-subset shared-node geometry. Apache-2.0; prepared for ToikY with Codex.
No predecessor implementation imports. Exact local class, not a supplier.
"""
from collections import Counter
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = 'ce7ad1b6ab09452c3478723a2e96ed5ff212dc08'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pc(x):
    return bin(x).count('1')


def dot(x, y):
    return pc(x & y) % 2


def span(basis):
    result = {0}
    for b in basis:
        result |= {x ^ b for x in result}
    return result


def kernel(a, b):
    return (1, 0, -1, 0)[pc(a & b) % 4]


def rectangle(a, b, c, d):
    return (a != b and c != d and dot(a, b) == dot(c, d) == 1
            and all(dot(s, t) == 0 for s in (a, b) for t in (c, d))
            and kernel(a, c) * kernel(b, d) == kernel(a, d) * kernel(b, c)
            and not ({a, b, a ^ b} & {c, d, c ^ d}))


def solve_characteristic(basis):
    n = len(basis)
    rows = [sum(dot(x, y) << j for j, y in enumerate(basis))
            | (dot(x, x) << n) for x in basis]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i] & (1 << j)), None)
        if pivot is None:
            return None
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(n):
            if i != j and rows[i] & (1 << j):
                rows[i] ^= rows[j]
    w = 0
    for j, x in enumerate(basis):
        if rows[j] & (1 << n):
            w ^= x
    return w


def frame_candidates(h, a, b, c, d):
    E = span([a, b])
    ambient = [v for v in range(1 << h) if not dot(v, c) and not dot(v, d)]
    need(len(ambient) == 1 << (h - 2), 'target annihilator rank')
    cosets = sorted({min(v ^ x for x in E) for v in ambient})
    quotient_planes = {}
    for u, v in combinations(cosets[1:], 2):
        key = tuple(sorted((u, v, min((u ^ v) ^ x for x in E))))
        quotient_planes.setdefault(key, (u, v))
    need(len(quotient_planes) == ((1 << (h - 4)) - 1) * ((1 << (h - 4)) - 2) // 6,
         'complete quotient two-subspace count')
    for key in sorted(quotient_planes):
        u, v = quotient_planes[key]
        yield [a, b, u, v]


def inspect_frames(h, a, b, c, d):
    total, nondegenerate, legal = 0, 0, 0
    first = None
    for basis in frame_candidates(h, a, b, c, d):
        total += 1
        w = solve_characteristic(basis)
        if w is None:
            continue
        nondegenerate += 1
        # The ambient characteristic is all ones. Orthogonal splitting gives
        # w_(U-perp) = all_ones XOR w_U, avoiding a second elimination engine.
        if w not in (a, b) and (((1 << h) - 1) ^ w) not in (c, d):
            legal += 1
            if first is None:
                first = basis
    return total, nondegenerate, legal, first


def check_basis(basis, space):
    need(span(basis) == space, 'residual basis span')
    need(all(dot(x, y) == int(i == j)
             for i, x in enumerate(basis) for j, y in enumerate(basis)),
         'residual basis orthonormality')


def fixture_check():
    h, sources, targets, basis = 9, [31, 481], [47, 87], [31, 481, 3, 40]
    need(all(pc(x) == 5 for x in sources + targets), 'five-subset fixture')
    need(rectangle(*sources, *targets), 'fixture rectangle conditions')
    U = span(basis)
    W = {x for x in range(1 << h) if all(dot(x, y) == 0 for y in basis)}
    need(len(U) == 16 and len(W) == 32 and U & W == {0}, 'orthogonal decomposition')
    need(solve_characteristic(basis) == 40, 'source characteristic')
    need(all(dot(471, x) == dot(x, x) for x in W), 'target characteristic')
    incoming = [[52, 457, 458], [28, 55, 482]]
    outgoing = [[59, 67, 131, 259], [131, 279, 367, 379]]
    for label, rows in zip(sources, incoming):
        check_basis(rows, {x for x in U if not dot(x, label)})
    for label, rows in zip(targets, outgoing):
        check_basis(rows, {x for x in W if not dot(x, label)})
    check_basis([28, 55, 481, 482], U)
    check_basis([47, 59, 67, 131, 259], W)
    return {'h': h, 'sources': sources, 'targets': targets,
            'kernel': [[kernel(s, t) for t in targets] for s in sources],
            'frame_basis': basis, 'frame_characteristic': 40,
            'complement_characteristic': 471,
            'incoming_residual_bases': incoming, 'outgoing_residual_bases': outgoing,
            'incident_residual_dimensions': [3, 3, 4, 4]}


def canonical_census():
    census, records = {}, []
    labeled, by_source = {}, {}
    for h in (8, 9):
        labels = [sum(1 << i for i in t) for t in combinations(range(h), 5)]
        labeled[str(h)] = 0
        by_source[str(h)] = {}
        for overlap in (1, 3):
            if 10 - overlap > h:
                continue
            a = 31
            b = (1 << overlap) - 1 | sum(1 << i for i in range(5, 10 - overlap))
            targets = [t for t in labels if not dot(a, t) and not dot(b, t)]
            good = [(c, d) for c, d in combinations(targets, 2) if rectangle(a, b, c, d)]
            source_pairs = comb(h, 10 - overlap) * comb(10 - overlap, overlap) * comb(10 - 2 * overlap, 5 - overlap) // 2
            stats = {'target_labels': len(targets), 'target_pairs_tested': comb(len(targets), 2),
                     'rectangles': len(good), 'labeled_source_pairs': source_pairs,
                     'target_intersection_histogram': dict(sorted(Counter(str(pc(c & d)) for c, d in good).items()))}
            if h == 9:
                histogram = Counter()
                tested = 0
                for c, d in good:
                    n, nondeg, legal, witness = inspect_frames(h, a, b, c, d)
                    tested += n
                    histogram[str(legal)] += 1
                    need(legal > 0, 'rectangle lacks a dimension-four legal frame')
                    records.append([overlap, c, d, n, nondeg, legal, witness])
                stats['dimension_four_frames_tested'] = tested
                stats['legal_frame_count_histogram'] = dict(sorted(histogram.items()))
            census[str(h) + '_source_intersection_' + str(overlap)] = stats
            count = source_pairs * len(good)
            labeled[str(h)] += count
            by_source[str(h)][str(overlap)] = count
    need(labeled == {'8': 0, '9': 453600}, 'rectangle census total')
    digest = hashlib.sha256(json.dumps(records, separators=(',', ':')).encode()).hexdigest()
    return census, labeled, by_source, digest


def controls():
    def reject(fn, name):
        try:
            fn()
        except ValueError:
            return
        raise ValueError('negative control accepted: ' + name)
    # Legal separators can fail the stronger incident-residual contract.
    U = span([25, 26, 4])
    bad_residual = {x for x in U if not dot(x, 7)}
    need(len(bad_residual) == 4 and all(dot(x, x) == 0 for x in bad_residual),
         'PR920 alternating residual control')
    reject(lambda: check_basis([3, 29], bad_residual), 'alternating residual')
    reject(lambda: check_basis([52, 457, 459], {x for x in span([31, 481, 3, 40]) if not dot(x, 31)}),
           'corrupted residual vector')
    reject(lambda: need(rectangle(31, 481, 47, 31), 'cross orthogonality'), 'wrong endpoint')
    need(all(dot(s, t) == 0 for s in (31, 103) for t in (47, 155))
         and dot(31, 103) == dot(47, 155) == 1, 'rank control premises')
    need(kernel(31, 47) * kernel(103, 155) != kernel(31, 155) * kernel(103, 47)
         and not rectangle(31, 103, 47, 155), 'signed rank-two control')
    need({31, 481, 31 ^ 481} & {47, 465, 47 ^ 465}
         and not rectangle(31, 481, 47, 465), 'common-span control')
    need(solve_characteristic([31, 481]) is None, 'degenerate source-span control')
    # Exhaust the complement isometry independently on all 256 vectors.
    w = 255
    J = lambda x: x ^ (w if dot(x, w) else 0)
    for x in range(256):
        need(J(J(x)) == x, 'complement involution')
        for y in range(256):
            need(J(x ^ y) == J(x) ^ J(y) and dot(J(x), J(y)) == dot(x, y),
                 'complement linear isometry')
    labels = [x for x in range(256) if pc(x) == 5]
    for s in labels:
        need(pc(J(s)) == 3, 'five to triple complement')
        for t in labels:
            need(kernel(J(s), J(t)) == -kernel(s, t), 'kernel complement sign')
    return {'semantic_controls': 6, 'isometry_vector_pairs': 65536, 'five_subset_kernel_pairs': 3136}


def main():
    need(sys.argv[1:] in ([], ['--write-certificate']), 'arguments')
    f = fixture_check()
    census, labeled, by_source, digest = canonical_census()
    result = {'format': 'five-subset-shared-node-seed48-v1', 'base_commit': BASE,
              'seed': 48, 'new_kappa': False, 'sharp_ambient_threshold': 9,
              'canonical_census': census, 'labeled_rectangles': labeled,
              'labeled_by_source_intersection': by_source,
              'canonical_frame_records_sha256': digest, 'fixture': f, 'controls': controls()}
    target = HERE / 'CERTIFICATE.json'
    if sys.argv[1:]:
        target.write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(json.loads(target.read_text()) == result, 'certificate mismatch')
    print('PASS_FIVE_SUBSET_SHARED_NODE threshold=9 rectangles_h9=453600 canonical_frames=59520 residual_bases=4 no_new_kappa')


if __name__ == '__main__':
    main()
