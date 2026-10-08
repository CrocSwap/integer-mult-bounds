#!/usr/bin/env python3
"""Exact three-class rank-moment certificate for the existing F3 producer.

This calculation uses the PR #7 producer unchanged. It groups the middle
identity pivots of three large-projector edge classes into contiguous chunk
interchanges. The geometric rank classes are proved in the accompanying note;
the general projector batching and arbitrary-width transfer are separate lemmas.
"""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import argparse
import json

H = 28
ROLES_PER_INVOCATION = 11840940
BIT_SAVING = Q(177, 1000000000)


def rational_log_bounds(value, terms=16):
    """Positive rational enclosure of log(value) for 1 <= value <= 2."""
    value = Q(value)
    if not 1 <= value <= 2:
        raise ValueError('Logarithm argument is outside [1, 2]')
    z = (value - 1) / (value + 1)
    lo = 2 * sum((z ** (2 * j + 1) / (2 * j + 1)
                  for j in range(terms)), Q(0))
    error = 2 * z ** (2 * terms + 1) / ((2 * terms + 1) * (1 - z * z))
    return lo, lo + error


def log_integer_upper(n):
    k = n.bit_length() - 1
    return k * rational_log_bounds(2)[1] + rational_log_bounds(Q(n, 2 ** k))[1]


def counts(h=H, roles=ROLES_PER_INVOCATION):
    v = comb(h, 5)
    m = h ** 3
    N = v ** 3
    W = 2 * v * v * (v + roles)
    L = 3 * v * v * comb(h, 2) * (h - 2)
    deficit = N - 2 * L
    s = W * m - deficit
    copies = v * v * roles
    bulk = [
        dict(name='first_third_stage_auxiliary_joins',
             copies=copies, original_rank=m - 2 * h,
             singleton_pivots=2 * h, chunk_digits=m - 4 * h),
        dict(name='second_stage_auxiliary_sink_edges',
             copies=copies, original_rank=m - h * h,
             singleton_pivots=h * h, chunk_digits=m - 2 * h * h),
        dict(name='third_stage_data_entrance_edges',
             copies=2 * N, original_rank=(h * h - 1) * (h - 1),
             singleton_pivots=h * h + h - 1,
             chunk_digits=m - 2 * h * h - 2 * h + 2),
    ]
    for row in bulk:
        assert 0 < row['chunk_digits'] < m
        assert row['original_rank'] > m / 2
        assert row['original_rank'] == row['singleton_pivots'] + row['chunk_digits']
    singleton_calls = s - sum(row['copies'] * row['chunk_digits'] for row in bulk)
    assert singleton_calls > 0
    assert singleton_calls + sum(row['copies'] * row['chunk_digits'] for row in bulk) == s
    return dict(h=h, v=v, m=m, N=N, W=W, decreasing_dimension=L,
                deficit=deficit, original_rank_sum=s,
                roles_per_invocation=roles, bulk_classes=bulk,
                singleton_calls=singleton_calls, eta=Q(deficit, W * m))


def certificate(a=BIT_SAVING, roles=ROLES_PER_INVOCATION):
    n = counts(roles=roles)
    m = n['m']
    W = n['W']
    logarithms = [Q(9997, 1000), Q(512, 100000), Q(7411, 100000), Q(768, 10000)]
    ratios = [Q(1, m)] + [Q(row['chunk_digits'], m) for row in n['bulk_classes']]
    weights = [Q(n['singleton_calls'], W * m)] + [
        Q(row['copies'] * row['chunk_digits'], W * m) for row in n['bulk_classes']]
    log_enclosures = [log_integer_upper(m)] + [rational_log_bounds(1 / x)[1] for x in ratios[1:]]
    for enclosure, simple in zip(log_enclosures, logarithms):
        assert enclosure < simple
        assert 0 <= a * simple < 1
    assert sum(weights) == 1 - n['eta']
    # exp(t) <= 1/(1-t) for 0 <= t < 1, with strict inequality for t > 0.
    moment_upper = sum((w / (1 - a * bound)
                        for w, bound in zip(weights, logarithms)), Q(0))
    assert moment_upper < 1, 'The proposed bit saving exceeds this conservative certificate'
    return dict(status='EXACT RATIONAL RANK-MOMENT WITNESS',
                bit_saving=a, tau=1 - a, counts=n,
                normalized_widths=ratios, rank_mass_weights=weights,
                logarithm_upper_bounds=logarithms,
                logarithm_enclosures=log_enclosures,
                moment_upper=moment_upper, strict_gap=1 - moment_upper,
                formula='sum_i weight_i * ratio_i^(-bit_saving) < 1',
                bound='exp(x) <= 1/(1-x), for 0 <= x < 1',
                dependencies=[
                    'Existing PR #7 scalar producer, retained-total frame schedule and bank matching',
                    'Width padding given identity gates at the ordinary D0 and D1 bank boundaries',
                    'Large-projector lower-triangular factorization with a contiguous middle block',
                    'Arbitrary-width finite-tape recurrence using the resulting mixed child widths',
                ])


def serializable(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {key: serializable(val) for key, val in value.items()}
    if isinstance(value, (tuple, list)):
        return [serializable(val) for val in value]
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = serializable(certificate())
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end='')
