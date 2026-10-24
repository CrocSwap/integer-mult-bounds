#!/usr/bin/env python3
"""Integer envelopes for #4507's fixed-rule chronological widths.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
The universal result is proved in README.md; this module has no flow evaluator.
"""
from math import prod


def require(condition, message):
    if not condition:
        raise ValueError(message)


def factor(value):
    require(type(value) is int and value >= 1, 'positive factor input')
    result = {}
    divisor = 2
    while divisor * divisor <= value:
        while value % divisor == 0:
            result[divisor] = result.get(divisor, 0) + 1
            value //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1:
        result[value] = result.get(value, 0) + 1
    return result


def valuation(value, prime):
    require(value > 0 and prime >= 2, 'valuation domain')
    result = 0
    while value % prime == 0:
        value //= prime
        result += 1
    return result


def rank_primes(targets, paid):
    require(bool(targets) and bool(paid), 'nonempty fixed rule')
    require(all(type(k) is int and type(v) is int and v > 0
                for hist in (targets, paid) for k, v in hist.items()), 'integer rule')
    require(min(targets) >= 2 and min(paid) >= 1
            and max(paid) < max(targets), 'strict rank contract')
    return sorted({p for rank in targets.keys() | paid.keys() for p in factor(rank)})


def smooth_numbers(primes, cap):
    """All products of the supplied distinct primes up to cap, including 1."""
    require(type(cap) is int and cap >= 1, 'positive cap')
    require(primes == sorted(set(primes))
            and all(factor(p) == {p: 1} for p in primes), 'distinct ordered primes')
    values = [1]
    for prime in primes:
        following = []
        for old in values:
            value = old
            while value <= cap:
                following.append(value)
                value *= prime
        values = following
    return sorted(values)


def floor_log(base, value):
    require(base >= 2 and value >= 1, 'integer logarithm domain')
    count, power = 0, 1
    while power <= value // base:
        power *= base
        count += 1
    return count


def depth_bound(n, m):
    require(type(n) is int and n >= 0 and type(m) is int and m >= 2, 'depth domain')
    depth = 0
    while n >= m:
        n = (m - 1) * n // m
        depth += 1
    return depth


def check_descent(rows, n, m):
    require(n >= m >= 2 and bool(rows), 'nonbase batches')
    require(all(type(e) is int and 0 <= e <= (m-1)*n//m
                and type(q) is int and q > 0 for e, q in rows),
            'uniform rank contraction')


def next_valuations(previous, rows, source_factors):
    """Independent max-plus evaluation of v_p(S*lcm(B_e/gcd(B_e,q)))."""
    repayment = {}
    for e, count in rows:
        require(0 <= e < len(previous) and count > 0, 'smaller positive batch')
        for prime, exponent in previous[e].items():
            need = max(0, exponent - valuation(count, prime))
            repayment[prime] = max(repayment.get(prime, 0), need)
    for prime, exponent in source_factors.items():
        repayment[prime] = repayment.get(prime, 0) + exponent
    return {p: e for p, e in repayment.items() if e}


def from_valuations(powers):
    return prod(p ** e for p, e in powers.items())


def join_valuations(*maps):
    result = {}
    for powers in maps:
        for prime, exponent in powers.items():
            result[prime] = max(result.get(prime, 0), exponent)
    return result


def check_envelope(powers, source_lcm, depth):
    require(all(e <= depth * source_lcm.get(p, 0) for p, e in powers.items()),
            'source LCM depth envelope')


def universal_parameters(targets, paid, maximum):
    primes = rank_primes(targets, paid)
    m, kmin = max(targets), min(targets)
    require(maximum >= m, 'nonbase maximum')
    cap = maximum // m
    height = floor_log(kmin, cap)
    W, P = sum(targets.values()), sum(paid.values())
    ceiling = W * (W + P + 1) ** (height + 1)
    grid = prod(1 + floor_log(p, cap) for p in primes)
    depth = depth_bound(maximum, m)
    ceiling_log2 = (ceiling - 1).bit_length()
    return {'rank_primes': primes, 'd': len(primes), 'log_degree': len(primes)+2,
            'cap': cap, 'height': height, 'source_ceiling': ceiling,
            'prime_box_count': grid, 'depth': depth,
            'power_of_two_exponent': depth * grid * ceiling_log2}
