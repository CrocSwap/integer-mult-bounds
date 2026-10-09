#!/usr/bin/env python3
"""Exact rank moment after controlled changes of rational tensor coordinates.

The same finite scalar producer is used. A simultaneous rational basis keeps
both previously batched high-rank classes valid and converts the stage-two
sink corner pivots into one contiguous block. See the written basis theorem.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
from batched_bit_rank_moment import (
    H, ROLES_PER_INVOCATION, counts as original_counts,
    rational_log_bounds, log_integer_upper, serializable,
)

BIT_SAVING = Q(246, 1000000000)


def counts(h=H, roles=ROLES_PER_INVOCATION):
    n = original_counts(h=h, roles=roles)
    width = h * h
    copies = n['v'] * n['v'] * roles
    n['singleton_calls'] -= copies * width
    n['recursive_blocks'] = [
        dict(name=row['name'] + '_middle', copies=row['copies'],
             chunk_digits=row['chunk_digits']) for row in n['bulk_classes']
    ]
    n['recursive_blocks'].append(dict(
        name='second_stage_auxiliary_sink_corner', copies=copies,
        chunk_digits=width))
    n['bulk_classes'][1]['singleton_pivots'] = 0
    n['bulk_classes'][1]['additional_corner_chunk_digits'] = width
    assert n['singleton_calls'] > 0
    assert n['singleton_calls'] + sum(
        row['copies'] * row['chunk_digits'] for row in n['recursive_blocks']
    ) == n['original_rank_sum']
    return n


def certificate(a=BIT_SAVING, roles=ROLES_PER_INVOCATION):
    n = counts(roles=roles)
    m = n['m']
    W = n['W']
    logarithms = [Q(9997, 1000), Q(512, 100000), Q(7411, 100000),
                  Q(768, 10000), Q(33323, 10000)]
    ratios = [Q(1, m)] + [
        Q(row['chunk_digits'], m) for row in n['recursive_blocks']]
    weights = [Q(n['singleton_calls'], W * m)] + [
        Q(row['copies'] * row['chunk_digits'], W * m)
        for row in n['recursive_blocks']]
    log_enclosures = [log_integer_upper(m)] + [
        rational_log_bounds(1 / x)[1] if 1 / x <= 2
        else log_integer_upper((1 / x).numerator)
        for x in ratios[1:]]
    assert 1 / ratios[-1] == n['h']
    for enclosure, simple in zip(log_enclosures, logarithms):
        assert enclosure < simple
        assert 0 <= a * simple < 1
    assert sum(weights) == 1 - n['eta']
    moment_upper = sum((w / (1 - a * bound)
                        for w, bound in zip(weights, logarithms)), Q(0))
    assert moment_upper < 1, 'The proposed saving exceeds this rank-moment certificate'
    return dict(
        status='EXACT RATIONAL CONTROLLED-BASIS RANK-MOMENT WITNESS',
        bit_saving=a, tau=1 - a, counts=n,
        normalized_widths=ratios, rank_mass_weights=weights,
        logarithm_upper_bounds=logarithms, logarithm_enclosures=log_enclosures,
        moment_upper=moment_upper, strict_gap=1 - moment_upper,
        formula='sum_i weight_i * ratio_i^(-bit_saving) < 1',
        bound='exp(x) <= 1/(1-x), for 0 <= x < 1',
        dependencies=[
            'Existing PR #7 producer and the three geometric edge-rank classes',
            'Controlled simultaneous basis theorem in notes/controlled-projector-basis.tex',
            'Large-projector factorization with a contiguous middle identity block',
            'Arbitrary integer-width recurrence and row-reservation interface',
        ],
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    encoded = json.dumps(serializable(certificate()), indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end='')
