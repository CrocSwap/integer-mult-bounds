#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check exact unit-cost fractional-bit allocation."""
from fractions import Fraction as Q
from itertools import product
import heapq
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def allocate(weights, lower, tolerance):
    need(len(weights) == len(lower) > 0, 'matching nonempty inputs')
    need(all(w > 0 for w in weights) and tolerance > 0, 'positive weights and tolerance')
    need(all(type(p) is int and p >= 0 for p in lower), 'integer lower bounds')
    p = list(lower)
    heap = [(-Q(w) / (1 << b), i) for i, (w, b) in enumerate(zip(weights, p))]
    heapq.heapify(heap)
    total = -sum(x for x, _ in heap)
    while total > tolerance:
        negative, i = heapq.heappop(heap)
        total += negative / 2
        p[i] += 1
        heapq.heappush(heap, (negative / 2, i))
    return p, total


def compositions(k, n):
    if n == 1:
        yield (k,)
    else:
        for first in range(k + 1):
            for rest in compositions(k - first, n - 1):
                yield (first,) + rest


def error(weights, bits):
    return sum(Q(w) / (1 << b) for w, b in zip(weights, bits))


def run():
    instances = enumerated = 0
    for n in (1, 2, 3, 4):
        for weights in product((1, 3, 8), repeat=n):
            lower = tuple(i % 2 for i in range(n))
            initial = error(weights, lower)
            for ratio in (Q(1), Q(3, 4), Q(1, 2), Q(1, 4)):
                eps = ratio * initial
                p, achieved = allocate(weights, lower, eps)
                k = sum(p) - sum(lower)
                vals = []
                for delta in compositions(k, n):
                    vals.append(error(weights, [a + b for a, b in zip(lower, delta)]))
                    enumerated += 1
                need(achieved == min(vals) and achieved <= eps, 'fixed-budget optimum')
                if k:
                    need(all(error(weights, [a + b for a, b in zip(lower, d)]) > eps
                             for d in compositions(k - 1, n)), 'minimum total bit count')
                instances += 1
    weights = (256, 1, 1, 1)
    p, residual = allocate(weights, (0, 0, 0, 0), Q(1, 8))
    need(p == [13, 5, 5, 5] and residual == Q(1, 8), 'nonuniform fixture')
    need(sum(p) == 28 and error(weights, (11,) * 4) > Q(1, 8)
         and error(weights, (12,) * 4) <= Q(1, 8), 'uniform guard needs 48 bits')
    # Benefit per cost fails once bit prices differ.
    need(Q(7, 4) > Q(4, 3), 'ratio chooses second coordinate')
    need(Q(8) + Q(7, 2) > 11 and Q(4) + Q(7) == 11, 'weighted-cost counterexample')
    bad = [((), (), Q(1)), ((0,), (0,), Q(1)), ((1,), (-1,), Q(1)),
           ((1,), (Q(1, 2),), Q(1)), ((1,), (0,), Q(0))]
    for args in bad:
        try:
            allocate(*args)
        except ValueError:
            pass
        else:
            raise ValueError('invalid allocation input accepted')
    return dict(status='PASS_DYADIC_BIT_ALLOCATION', instances=instances,
                exhaustive_allocations=enumerated, fixture_bits=p,
                fixture_total_bits=28, least_uniform_total_bits=48,
                invalid_inputs=5, weighted_cost_control=True, no_new_kappa=True)


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
