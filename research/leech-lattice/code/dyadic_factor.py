#!/usr/bin/env python3
"""An explicit 2600-center dyadic factorization of the Leech cubic kernel."""
import argparse
from itertools import combinations
import json
from pathlib import Path
import numpy as np
from leech_geometry import require


def factors(vectors):
    x = vectors.astype(np.int64)
    require(np.all((x * x).sum(axis=1) == 32), 'Integer norm must be32')
    f = (x**3 - x) // 3
    require(np.array_equal(3*f, x**3-x), 'Integer-valued cubic')
    left = [f - 10*x]
    right = [32*x**3 - 256*x]
    for i in range(24):
        for j in range(24):
            if i != j:
                left.append((x[:, i]*x[:, j]**2)[:, None])
                right.append((x[:, i]*x[:, j]**2 + 10*x[:, i]**3
                              + f[:, i] - 85*x[:, i])[:, None])
    for i, j, k in combinations(range(24), 3):
        term = (x[:, i]*x[:, j]*x[:, k])[:, None]
        left.append(term)
        right.append(2*term)
    a, b = np.concatenate(left, axis=1), np.concatenate(right, axis=1)
    require(a.shape == b.shape == (len(x), 2600), 'Factor dimensions')
    return a, b


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    path = parser.parse_args().output
    vectors = np.load(path/'minimal_lines.npy').astype(np.int64)
    indices = np.unique(np.concatenate((np.arange(16),
                         np.linspace(0, len(vectors)-1, 256, dtype=int))))
    sample = vectors[indices]
    left, right = factors(sample)
    dot = sample @ sample.T
    require(np.all(dot % 8 == 0), 'Integral normalized pairings')
    cubic_numerator = dot**3 - 256*dot
    require(np.array_equal(3*(left @ right.T), cubic_numerator),
            'Dyadic factorization failed')
    require(np.all(np.diag(left @ right.T) == 8192), 'Normalized diagonal')
    off = dot.copy()
    np.fill_diagonal(off, 0)
    require(set(map(int, np.unique(off))).issubset({-16, -8, 0, 8, 16}),
            'Off-diagonal inner products')
    values = {t: (t**3-4*t)//3 for t in (-4, -2, -1, 0, 1, 2, 4)}
    # The integer coefficients are precomputed scalar constants. There is
    # no division by3 in the run-time scalar word; its only scale is2^-13.
    report = {
        'centers': 2600, 'scale_denominator': 8192,
        'identity': 'A(x) B(y)^T /8192 = ((x.y/8)^3-4*(x.y/8))/48',
        'source_features': {'(x_i^3-31*x_i)/3': 24,
                            'x_i*x_j^2, i!=j': 552,
                            'x_i*x_j*x_k, i<j<k': 2024},
        'sampled_pairs': len(indices)**2,
        'kernel_times_16_by_inner_product': values,
        'support_argument': 'On coordinates0,+/-1,+/-2,+/-3,+/-4, '
            '(x_i^3-31*x_i)/3 vanishes iff x_i=0. Every source feature '
            'therefore has the same support as its homogeneous monomial; '
            'CENTER-SUPPORTS.json proves all2600 source spans have rank25.',
        'scope': 'Exact symbolic factorization with sampled arithmetic checks; '
            'not an emitted supplier, helper schedule, or kappa certificate.'}
    (path/'DYADIC-FACTOR.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
