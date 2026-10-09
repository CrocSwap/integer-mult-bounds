#!/usr/bin/env python3
"""Finite diagnostics for the packed-movement audit; no new exponent certificate.

These model the existing rotation order and complete permutation interfaces.
They do not implement tape operations or exclude other algorithms.
"""
from fractions import Fraction as Q
from itertools import permutations

TARGETS = ('y', 'z', 'y', 'z', 'z', 'y', 'z', 'y')
ORDERS = tuple(permutations(('x', 'y', 'z')))


def swap_distance(left, right):
    """Minimum number of unrestricted whole-field swaps for three names."""
    state = list(left)
    count = 0
    for i, name in enumerate(right):
        if state[i] != name:
            j = state.index(name)
            state[i], state[j] = state[j], state[i]
            count += 1
    return count


def minimum_swaps(initial):
    """Allow every intermediate layout, preserve rotation order, restore input."""
    costs = {initial: 0}
    for target in TARGETS:
        costs = {order: min(cost+swap_distance(previous, order)
                            for previous, cost in costs.items())
                 for order in ORDERS if order[-1] == target}
    return min(cost+swap_distance(order, initial) for order, cost in costs.items())


def retained_schedule(initial):
    """Swap each target into the rightmost slot; undo the resulting layout last."""
    order = list(initial)
    swaps = []
    for target in TARGETS:
        i = order.index(target)
        if i != 2:
            swaps.append((i, 2))
            order[i], order[2] = order[2], order[i]
    for i, name in enumerate(initial):
        if order[i] != name:
            j = order.index(name)
            swaps.append((i, j))
            order[i], order[j] = order[j], order[i]
    assert tuple(order) == initial
    return swaps


def original_swap_count(initial):
    return 2*sum(target != initial[-1] for target in TARGETS)


def cn_basis_permutation(x):
    """The GF(2) basis map (u,v) -> (u,v xor u), encoded in two bits."""
    return x ^ ((x >> 1) & 1)


def C_on_bit(state, mask):
    """Exact Gaussian-integer numerator 2*C; inputs are small exact integers."""
    return [(1+1j)*state[x]+(1-1j)*state[x ^ mask] for x in range(4)]


def permute(state):
    out = [0]*4
    for x, value in enumerate(state):
        out[cn_basis_permutation(x)] = value
    return out


def recurrence_example(levels, stop_level, K):
    """Exact example: m=4, tau=1/2, branch ratio 3/2, square K.

    F(4^k)=(3/2) F(4^(k-1))+sqrt(4^k K), stopping at 4^stop_level.
    The root-normalized internal work is a geometric sum with ratio 3/4.
    """
    from math import isqrt
    sqrt_K = isqrt(K)
    assert sqrt_K*sqrt_K == K and 0 <= stop_level <= levels
    value = Q(4**stop_level)
    for k in range(stop_level+1, levels+1):
        value = Q(3,2)*value+2**k*sqrt_K
    depth = levels-stop_level
    leaf = Q(3,2)**depth * 4**stop_level
    internal = 2**levels*sqrt_K*sum((Q(3,4)**j for j in range(depth)), Q(0))
    return value, leaf+internal


if __name__ == '__main__':
    for order in ORDERS:
        print(''.join(order), 'original:', original_swap_count(order),
              'retained:', len(retained_schedule(order)),
              'optimal in this finite model:', minimum_swaps(order))
    print('These are constant-factor counts, not an asymptotic exponent improvement.')
