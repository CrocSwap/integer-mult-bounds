#!/usr/bin/env python3
"""Independent exhaustive set census for the seed-48 five-subset class.

Copyright 2026 Eva Ayala. SPDX-License-Identifier: Apache-2.0.
Written with substantial OpenAI Codex assistance.

This implementation uses coordinate sets, literal real parts of powers of i,
integer 2-by-2 determinants, and explicit nonzero binary-span nodes. It does
not import the primary verifier or use its bit-mask or canonical-frame code.
Source and target sides are distinguished; each side is an unordered pair of
five-element subsets of a labeled h-element coordinate set. The complete
finite domain is h in {8, 9}; this is not a theorem about other dimensions or
other decoder classes.
"""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path


def kernel(intersection_size):
    """The integer real part of i**intersection_size, without complex floats."""
    return (1, 0, -1, 0)[intersection_size % 4]


def census(dimension):
    subsets = tuple(frozenset(coords) for coords in combinations(range(dimension), 5))
    # Every cached value is computed directly from coordinate-set intersection.
    overlap = tuple(tuple(len(left & right) for right in subsets) for left in subsets)
    odd_pairs = tuple(
        (i, j, overlap[i][j])
        for i, j in combinations(range(len(subsets)), 2)
        if overlap[i][j] % 2 == 1
    )
    spans = {
        (i, j): frozenset((subsets[i], subsets[j], subsets[i] ^ subsets[j]))
        for i, j, _ in odd_pairs
    }
    by_source = Counter({str(size): 0 for _, _, size in odd_pairs})
    by_target = Counter({str(size): 0 for _, _, size in odd_pairs})
    by_pair = Counter()
    by_cross_overlap = Counter()
    by_common_core_overlap = Counter()
    source_degrees = defaultdict(Counter)
    rank_zero_before_span_check = 0
    rejected_span_overlap = 0

    for i, j, source_size in odd_pairs:
        # This only discards targets that already violate a required cross-even
        # condition. Every permissible target pair remains in this list.
        compatible = tuple(
            k for k in range(len(subsets))
            if overlap[i][k] % 2 == 0 and overlap[j][k] % 2 == 0
        )
        source_span = spans[i, j]
        source_core = subsets[i] & subsets[j]
        degree = 0
        for k, l in combinations(compatible, 2):
            target_size = overlap[k][l]
            if target_size % 2 == 0:
                continue
            crossing = (overlap[i][k], overlap[i][l], overlap[j][k], overlap[j][l])
            matrix = ((kernel(crossing[0]), kernel(crossing[1])),
                      (kernel(crossing[2]), kernel(crossing[3])))
            if matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0] != 0:
                continue
            rank_zero_before_span_check += 1
            # Zero is omitted from both spans, so this tests E intersect T = {0}
            # directly, without replacing it with a specialized parity shortcut.
            if source_span & spans[k, l]:
                rejected_span_overlap += 1
                continue
            degree += 1
            by_source[str(source_size)] += 1
            by_target[str(target_size)] += 1
            by_pair['{},{}'.format(source_size, target_size)] += 1
            by_cross_overlap[','.join(map(str, sorted(crossing)))] += 1
            by_common_core_overlap[str(len(source_core & (subsets[k] & subsets[l])))] += 1
        source_degrees[str(source_size)][str(degree)] += 1

    # Reversing the two distinguished sides is a bijection of this same domain.
    # Check the stronger pair-stratified symmetry, not only the total count.
    if by_source != by_target:
        raise ValueError('source/target intersection totals are asymmetric')
    for pair, count in by_pair.items():
        source_size, target_size = pair.split(',')
        if by_pair['{},{}'.format(target_size, source_size)] != count:
            raise ValueError('source/target swap fails for intersection stratum ' + pair)

    return {
        'total': sum(by_source.values()),
        'five_subsets': len(subsets),
        'odd_source_pairs': len(odd_pairs),
        'by_source_intersection': dict(sorted(by_source.items())),
        'by_target_intersection': dict(sorted(by_target.items())),
        'by_intersection_pair': dict(sorted(by_pair.items())),
        'source_pair_target_degree_histograms': {
            size: dict(sorted(histogram.items(), key=lambda item: int(item[0])))
            for size, histogram in sorted(source_degrees.items())
        },
        'by_sorted_cross_intersections': dict(sorted(by_cross_overlap.items())),
        'by_common_core_intersection': dict(sorted(by_common_core_overlap.items())),
        'rank_zero_before_span_check': rank_zero_before_span_check,
        'rejected_nonzero_span_overlap': rejected_span_overlap,
        'source_target_swap_checked': True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path,
                        default=Path(__file__).with_name('CERTIFICATE.json'))
    args = parser.parse_args()
    certificate = json.loads(args.certificate.read_text(encoding='utf-8'))
    results = {str(dimension): census(dimension) for dimension in (8, 9)}
    totals = {dimension: result['total'] for dimension, result in results.items()}
    by_source = {
        dimension: result['by_source_intersection']
        for dimension, result in results.items()
    }
    if totals != certificate['labeled_rectangles']:
        raise ValueError('labeled rectangle census disagrees with certificate: ' + repr(totals))
    if by_source != certificate['labeled_by_source_intersection']:
        raise ValueError('source-intersection census disagrees with certificate: ' + repr(by_source))
    verify_fixture(certificate['fixture'])
    print(json.dumps(results, indent=2, sort_keys=True))
    print('PASS_INDEPENDENT_FIVE_SUBSET_RECTANGLES h8={} h9={}'.format(totals['8'], totals['9']))
    print('PASS_INDEPENDENT_RESIDUAL_BASES dimensions=3,3,4,4')


def verify_fixture(fixture):
    """Check every residual vector by coordinate sets, without Gaussian algebra."""
    h = fixture['h']
    if h != 9 or any(len(fixture[key]) != 2 for key in
                     ('sources', 'targets', 'incoming_residual_bases', 'outgoing_residual_bases')):
        raise ValueError('fixture dimension or endpoint count')
    def decode(mask):
        if mask < 0 or mask >= 2 ** h:
            raise ValueError('fixture coordinate outside ambient space')
        return frozenset(i for i in range(h) if (mask // 2 ** i) % 2)
    def orthogonal(x, y):
        return len(x & y) % 2 == 0
    def generated(rows):
        vectors = {frozenset()}
        for row in rows:
            vectors |= {v ^ row for v in vectors}
        return vectors
    sources = list(map(decode, fixture['sources']))
    targets = list(map(decode, fixture['targets']))
    U = generated(list(map(decode, fixture['frame_basis'])))
    ambient = [frozenset(s) for size in range(h + 1)
               for s in combinations(range(h), size)]
    W = {v for v in ambient if all(orthogonal(v, u) for u in U)}
    if len(U) != 16 or len(W) != 32 or U & W != {frozenset()}:
        raise ValueError('fixture orthogonal decomposition')
    if not all(s in U for s in sources) or not all(t in W for t in targets):
        raise ValueError('fixture endpoint containment')
    for space, labels, bases, dimensions in (
            (U, sources, fixture['incoming_residual_bases'], [3, 3]),
            (W, targets, fixture['outgoing_residual_bases'], [4, 4])):
        for label, masks, dimension in zip(labels, bases, dimensions):
            rows = list(map(decode, masks))
            residual = {v for v in space if orthogonal(v, label)}
            if len(rows) != dimension or generated(rows) != residual:
                raise ValueError('fixture residual basis span')
            if any((len(x & y) % 2) != int(i == j)
                   for i, x in enumerate(rows) for j, y in enumerate(rows)):
                raise ValueError('fixture residual basis orthonormality')


if __name__ == '__main__':
    main()
