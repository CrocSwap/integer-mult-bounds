#!/usr/bin/env python3
"""Independent exact cost-alphabet review; no supplier or kappa claim.

Ross Richardson with substantial OpenAI Codex assistance, including an
independent internal mathematical specialist. New code Apache-2.0.
Uses Python standard-library rational arithmetic only, imports no project engine.
Logarithms use a positive atanh series after reducing the argument to [1,2).
Exponentials use a positive Taylor series and an explicit geometric tail.
These are the inherited standard log/exp methods used by Douglas Colkitt's
PR1240 engine, implemented independently here; no predecessor code is imported.
"""
from fractions import Fraction as F
from functools import lru_cache
import json

M, W, IDLE = 73, F(896, 9), 1646
A = F(21, 20) * F(1690054109089, 10**15)
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
GRID = 1 << 200


def need(p, msg):
    if not p:
        raise AssertionError(msg)


def floor(x):
    return x.numerator // x.denominator


def ceil(x):
    return -floor(-x)


def rounded(lo, hi):
    return F(floor(lo * GRID), GRID), F(ceil(hi * GRID), GRID)


@lru_cache(None)
def log_near(x):
    need(F(1) <= x <= F(2), 'log range')
    z = (x - 1) / (x + 1)
    power, total, terms = z, F(0), 80
    for k in range(terms):
        total += 2 * power / (2*k + 1)
        power *= z*z
    # First omitted power is z^(2*terms+1); subsequent denominators increase.
    tail = 2 * power / ((2*terms + 1) * (1-z*z))
    return rounded(total, total + tail)


@lru_cache(None)
def log_ratio(r):
    need(type(r) is int and 1 <= r <= M, 'rank domain')
    x, j = F(M, r), 0
    while x >= 2:
        x /= 2
        j += 1
    near, two = log_near(x), log_near(F(2))
    return rounded(near[0] + j*two[0], near[1] + j*two[1])


def exp_at(x):
    need(F(0) <= x <= 5, 'exp range')
    term, total, degree = F(1), F(1), 96
    for k in range(1, degree + 1):
        term = term * x / k
        total += term
    nxt = term * x / (degree + 1)
    # All later term ratios are bounded by x/(degree+2) < 1.
    tail = nxt / (1 - x/F(degree+2))
    return rounded(total, total + tail)


@lru_cache(None)
def cost(r, a=A):
    need(F(0) <= a < 1, 'saving domain')
    ll, lu = log_ratio(r)
    low = exp_at(a*ll)[0]
    high = exp_at(a*lu)[1]
    return rounded(F(r, M)*low, F(r, M)*high)


def mixed(q):
    need(type(q) is int and 0 <= q <= 6, 'mixed family domain')
    h = dict(WORD)
    del h[1]
    h[16] = 150
    rem = 12 - 2*q
    if rem:
        h[rem] = h.get(rem, 0) + 1
    # q rank-two payload children, each with one rank-two paid transport.
    h[2] = h.get(2, 0) + 2*q
    return h


def added(profile, extra):
    h = dict(profile)
    for r, n in extra.items():
        h[r] = h.get(r, 0) + n
    return h


def moment(h, idle=IDLE, a=A):
    need(all(type(r) is int and 1 <= r <= 51 and type(n) is int and n >= 0
             for r, n in h.items()), 'histogram domain')
    lower = upper = F(0)
    for r, n in h.items():
        l, u = cost(r, a)
        lower += n*l
        upper += n*u
    l, u = cost(51, a)
    lower += F(idle, 51)*l
    upper += F(idle, 51)*u
    return lower/W, upper/W


def decbounds(bounds, places=30):
    scale = 10**places
    def show(n):
        sign = '-' if n < 0 else ''
        n = abs(n)
        return sign + str(n//scale) + '.' + str(n%scale).zfill(places)
    return [show(floor(bounds[0]*scale)), show(ceil(bounds[1]*scale))]


def passed(bounds):
    return bounds[1] < 1


def failed(bounds):
    return bounds[0] > 1


def mass(h):
    return sum(r*n for r, n in h.items())


def main():
    checks = []
    def check(p, name):
        need(p, name)
        checks.append(name)

    check(A == F(35491136290869, 20000000000000000), 'target exact')
    # A rational oracle: at a=0, every cost is exactly r/73.
    for r in range(1, 74):
        lo, hi = cost(r, F(0))
        check(lo <= F(r, M) <= hi, 'zero exponent oracle rank ' + str(r))
    # A distinct algebraic oracle: at a=1/2, square the positive endpoints.
    for r in range(1, 74):
        lo, hi = cost(r, F(1, 2))
        check(0 <= lo and lo*lo <= F(r, M) <= hi*hi,
              'square root oracle rank ' + str(r))
    results = {}
    baseline = moment(WORD)
    check(failed(baseline), 'baseline fails target')
    results['baseline'] = decbounds(baseline)
    for q in range(7):
        h = mixed(q)
        check(mass(h) == 5586 + 2*q, 'mixed mass q=' + str(q))
        value = moment(h)
        check(passed(value) if q <= 5 else failed(value),
              'mixed sign q=' + str(q))
        check(failed(moment(h, a=F(1, 99))),
              'mixed planning target fails q=' + str(q))
        results['mixed_' + str(q)] = {
            'histogram': dict(sorted(h.items())), 'mass': mass(h),
            'moment': decbounds(value),
            'one_minus_moment': decbounds((1-value[1], 1-value[0]))}
    full = mixed(0)
    full_three = moment(added(full, {1: 3}))
    check(passed(full_three), 'full plus three rank one calls passes')
    results['full_plus_three'] = decbounds(full_three)
    shared = moment(added(full, {16: 1}))
    check(failed(shared), 'full plus one rank16 transport fails')
    results['full_plus_one_rank16'] = decbounds(shared)
    # Each of the 151 output groups charged once at its own payload rank.
    uniform = moment(added(full, {16: 150, 12: 1}))
    check(failed(uniform), 'uniform one transport per group fails')
    results['uniform_charged'] = decbounds(uniform)
    # Deliberately bad old-idle credit hides added mass and reverses q=6.
    bad = moment(mixed(6), idle=IDLE-12)
    check(passed(bad), 'wrong old idle credit false pass q6')
    results['invalid_idle_credit_q6'] = decbounds(bad)
    # The target point has 10+2*2^q < 12^q+3 in rank-one units.
    c1, c2, c10, c12 = [cost(r) for r in (1, 2, 10, 12)]
    comparison = (c10[0]+2*c2[0]-c12[1]-3*c1[1],
                  c10[1]+2*c2[1]-c12[0]-3*c1[0])
    check(comparison[1] < 0, 'candidate cheaper than full plus3')
    results['candidate_minus_full_plus_three_unnormalized'] = decbounds(comparison)
    # 3 is the smallest integer allowance valid for every 0<a<1:
    # at a=1/2 the analogous allowance 2 fails.
    c1, c2, c10, c12 = [cost(r, F(1, 2)) for r in (1, 2, 10, 12)]
    wrong_two = (c10[0]+2*c2[0]-c12[1]-2*c1[1],
                 c10[1]+2*c2[1]-c12[0]-2*c1[0])
    check(wrong_two[0] > 0, 'uniform allowance two fails at half')
    results['candidate_minus_full_plus_two_at_half_unnormalized'] = decbounds(wrong_two)
    print(json.dumps({'status':'PASS_INDEPENDENT_MIXED_PROFILE',
                      'target':str(A), 'checks':len(checks),
                      'results':results}, indent=2))


if __name__ == '__main__':
    main()
