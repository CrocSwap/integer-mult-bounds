#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Directed arithmetic replay of the credited finite BIT compiler and bootstrap."""
from collections import Counter
from fractions import Fraction as F
from functools import cache

from literal import ALI, CANONICAL_WORD, OLD_RESULT_SHA, PR7776_HEAD, histogram, need, pinned

GRID = 10**72
TRIAL = F('0.00386970000')
TARGET_TEXT = '0.00386380485468'
TARGET = F(TARGET_TEXT)
LOSS = F(1, 10**10)
CLAIM_SHA = '3f8add8252adb223b60418ec69351a69b6b5edfe601ec1c6b4b65cd9e2afd9b2'
OLD_COMPLEX_SHA = '145853ea4d35e6b82ad08f9bacb9f4c655dc139c2fb4e11339e198e9b8c46eb7'
CLAIMS = ('0.00386963090', '0.00386969950', '0.00386969970')


def ceiling(num, den):
    return -((-num) // den)


def point(x):
    q = F(x)
    return q.numerator * GRID // q.denominator, ceiling(q.numerator * GRID, q.denominator)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[1], a[1] - b[0]


def mul(a, b):
    products = [x * y for x in a for y in b]
    return min(products) // GRID, ceiling(max(products), GRID)


def scale(a, x):
    return mul(a, point(x))


def invert(a):
    need(a[0] > 0, 'strictly positive interval denominator')
    return GRID * GRID // a[1], ceiling(GRID * GRID, a[0])


def divide(a, b):
    return mul(a, invert(b))


def decimal_interval(a, digits=39):
    display = 10**digits

    def fixed(n):
        integer, tail = divmod(abs(n), display)
        return f'{"-" if n<0 else ""}{integer}.{tail:0{digits}}'

    return [fixed(a[0] * display // GRID), fixed(ceiling(a[1] * display, GRID))]


def rational_display(q, digits=18):
    return decimal_interval(point(q), digits)


def log_taylor(t):
    total = F(0)
    factor = t
    square = t * t
    for j in range(85):
        total += 2 * factor / (2 * j + 1)
        factor *= square
    tail = 2 * factor / (171 * (1 - square))
    return point(total)[0], point(total + tail)[1]


@cache
def ln(rank):
    need(isinstance(rank, int) and rank >= 1, 'positive integer rank')
    bit = rank.bit_length() - 1
    scaled = F(rank, 1 << bit)
    return add(scale(log_taylor(F(1, 3)), bit), log_taylor((scaled - 1) / (scaled + 1)))


def positive_exp(x):
    # With x<2, each term after degree 101 is at most half its predecessor.
    need(0 <= x[0] <= x[1] < 2 * GRID, 'positive exponential Taylor interval')
    term = total = point(1)
    for j in range(1, 101):
        term = scale(mul(term, x), F(1, j))
        total = add(total, term)
    following = scale(mul(term, x), F(1, 101))
    return total[0], total[1] + 2 * following[1]


@cache
def exp_log(rank, scale_factor):
    positive = positive_exp(scale(ln(rank), abs(scale_factor)))
    return invert(positive) if scale_factor < 0 else positive


def raise_interval(base, n):
    product = point(1)
    while n:
        if n & 1:
            product = mul(product, base)
        base = mul(base, base)
        n //= 2
    return product


@cache
def price(rank, k, offset=F(0)):
    return scale(exp_log(rank, offset - k), rank)


def moment(hist, k, offset=F(0)):
    out = (0, 0)
    for rank, amount in hist.items():
        if amount:
            out = add(out, scale(price(rank, k, offset), amount))
    return out


def signed_profile(targets, paid):
    out = Counter(targets)
    out.subtract(paid)
    return out


def derivative_bound(signed, cap):
    # Positive coefficients contribute their least negative term at cap.
    # Negative coefficients contribute their greatest positive term at zero.
    bound = (0, 0)
    for rank, count in signed.items():
        if count:
            power = price(rank, cap if count > 0 else F(0))
            bound = add(bound, scale(mul(power, ln(rank)), -count))
    need(bound[1] < 0, 'strictly decreasing complete signed tariff on the comparison interval')
    return bound[1]


def crossing(signed):
    scale = 10**15
    low, high = int(TARGET * scale), int(F('0.0039') * scale)
    need(
        moment(signed, F(low, scale))[0] > 0 and moment(signed, F(high, scale))[1] < 0,
        'positive and negative signed crossing endpoints',
    )
    derivative = derivative_bound(signed, F(high, scale))

    def str_rank(k):
        return f'0.{k:015}'

    while high - low > 1:
        mid = (low + high) // 2
        test = moment(signed, F(mid, scale))
        need(test[0] > 0 or test[1] < 0, 'decisive interval sign at crossing grid point')
        if test[0] > 0:
            low = mid
        else:
            high = mid
    return dict(
        bracket=[str_rank(low), str_rank(high)],
        endpoint_margins=[decimal_interval(moment(signed, F(k, scale))) for k in (low, high)],
        derivative_upper=decimal_interval((derivative, derivative), 12)[1],
    )


def compiler(paid, targets, trial):
    v, c, b, m = 768, 15, 16, 134
    offset = F(1, 5)
    need(
        offset >= trial and max(paid) < max(targets) <= m and 1 < c < b < max(targets),
        'separated rank cutoffs',
    )
    total_targets = moment(targets, trial)
    ratios = (
        divide(moment(paid, trial), total_targets),
        divide(moment(paid, trial, offset), mul(exp_log(c, offset), total_targets)),
        divide(mul(exp_log(b, offset), moment(targets, trial, -offset)), total_targets),
    )
    bound_grid = 10**22
    alpha, gamma, lam = (F(ceiling(z[1] * bound_grid, GRID), bound_grid) for z in ratios)
    need(all(0 < r < 1 for r in (alpha, gamma, lam)), 'three finite-product tail bounds below one')
    volume = 1 / (1 + v * (1 - alpha)) + 2 * gamma**v + lam**v
    need(volume < 1, 'strict complete paid and discarded productive moment')
    theta = F(42, 43)
    need(
        c**43 < b**42 and c**42 >= b**41 and 2 * c ** (v * 43) <= m ** (v * 42),
        'actual ambient and both separated shifted-log bounds',
    )
    base = raise_interval(exp_log(m, trial), v)
    eta = scale(invert(base), 1 - trial)
    power = 1

    def threshold_passes(k):
        return theta**k < F(eta[0], GRID) and F(base[1], GRID) < 2**k

    while not threshold_passes(power):
        power += 1
    need(
        theta ** (power - 1) >= F(eta[1], GRID) or F(base[0], GRID) >= 2 ** (power - 1),
        'preceding shifted-log power excluded',
    )
    step = LOSS.denominator

    def carrier_passes(test):
        return (step * test + 1) ** power < 2**test

    lo, hi = 1, 2
    while not carrier_passes(hi):
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        mid = (hi + lo) // 2
        if carrier_passes(mid):
            hi = mid
        else:
            lo = mid
    need(
        carrier_passes(hi) and not carrier_passes(hi - 1),
        'uniform integer threshold and preceding grid point',
    )
    return dict(
        trial=str(trial),
        product_exponent=v,
        cutoff=c,
        productive_floor=b,
        ambient_base=m,
        paid_offset=str(offset),
        target_offset=str(offset),
        upper_ratios=[str(alpha), str(gamma), str(lam)],
        ratio_intervals=[decimal_interval(z) for z in ratios],
        normalized_separation_slack=rational_display(1 - volume),
        theta=str(theta),
        logarithm_power=power,
        H=step * hi,
        N=f'2^{step*hi}',
        eta=decimal_interval(eta),
        previous_power_failed=True,
        preceding_grid_failed=True,
        lost_low_targets='charged owned zero specializations',
        maximum_productive_rank=f'{max(targets)}^{v}',
        working_ambient=f'{m}^{v}',
    )


def bootstrap(start, covered, steps):
    rho = F(1, 250)
    stages = []
    old = start
    for step in steps:
        k = F(step)
        envelope = (1 - rho) * covered + rho * old
        need(
            old < k < envelope < rho < 1 - envelope,
            'literal ordinary stage estimate and stock inequalities',
        )
        stages.append(
            dict(
                previous=str(old),
                claim=str(step),
                envelope=rational_display(envelope, 18),
                slack=rational_display(envelope - k, 18),
            )
        )
        old = k
    return old, stages


def verify(source_root, word, literal_receipt_sha256):
    need(
        word['candidate_canonical_sha256'] == CANONICAL_WORD and word['native_calls'] == 36,
        'independently replayed 36-call source word',
    )
    paid, targets = map(histogram, (word['paid'], word['targets']))
    signed = signed_profile(targets, paid)
    old = pinned(source_root / ALI / 'BIT-RESULT.json', OLD_RESULT_SHA)
    old_complex = pinned(source_root / ALI / 'complex' / 'RESULT.json', OLD_COMPLEX_SHA)[
        'application'
    ]
    before = signed_profile(histogram(old['targets']), histogram(old['paid']))
    complex_invoice = old_complex['invoice']
    complex_signed = signed_profile(
        histogram(complex_invoice['targets']), histogram(complex_invoice['paid'])
    )
    old_bracket = old['compiler']['raw_bracket']
    complex_bracket = old_complex['bracket']
    need(
        moment(before, F(old_bracket[0]))[0] > 0 and moment(before, F(old_bracket[1]))[1] < 0,
        'independent signs for original binary crossing',
    )
    need(
        moment(complex_signed, F(complex_bracket[0]))[0] > 0
        and moment(complex_signed, F(complex_bracket[1]))[1] < 0,
        'independent signs for original complex crossing',
    )
    derivative_bound(before, F('0.0039'))
    derivative_bound(complex_signed, F('0.0039'))
    old_joint_raw_upper = min(old_bracket[1], complex_bracket[1], key=F)
    need(
        moment(before, TARGET)[1] < 0
        and moment(signed, TARGET)[0] > 0
        and moment(signed, TRIAL)[0] > 0,
        'old negative and new positive full invoice at frozen target and finite trial',
    )
    crossing_report = crossing(signed)
    proof = compiler(paid, targets, TRIAL)
    start = F(
        pinned(source_root / 'certificates' / 'frontier7000' / 'CLAIM.json', CLAIM_SHA)[
            'admitted_BIT_saving'
        ]
    )
    need(start == F('0.00385248'), 'selected completed base backend')
    covered = TRIAL - 2 * LOSS
    final, stages = bootstrap(start, covered, CLAIMS)
    old_finite = F(old['compiler']['ordinary_admitted'])
    need(F('0.00385896149') == old_finite < F(old_bracket[1]), 'old finite ordinary BIT')
    published = F(CLAIMS[1])
    need(
        final > published > TARGET
        and published - old_finite > F('0.00001')
        and published - F(old_joint_raw_upper) > F('0.00001'),
        'strict published ordinary improvement and original target clearance',
    )
    return dict(
        status='PASS_INDEPENDENT_BINARY_FINITE_AND_ORDINARY',
        candidate_canonical_sha256=CANONICAL_WORD,
        independent_literal_receipt_sha256=literal_receipt_sha256,
        target=TARGET_TEXT,
        old_7776_binary_margin=decimal_interval(moment(before, TARGET)),
        new_binary_signed_margin=decimal_interval(moment(signed, TARGET)),
        binary_signed_gain=decimal_interval(sub(moment(signed, TARGET), moment(before, TARGET))),
        margin_at_finite_trial=decimal_interval(moment(signed, TRIAL)),
        raw_crossing=crossing_report,
        old_public_binary_bracket=old_bracket,
        old_public_complex_bracket=complex_bracket,
        old_source_head=PR7776_HEAD,
        old_joint_raw_upper=old_joint_raw_upper,
        old_conditional_lower=old_complex['claim'],
        complete_binary_paid=paid,
        complete_productive=targets,
        compiler=proof,
        per_phase_uniform_and_cover_loss=str(LOSS),
        after_uniform=str(TRIAL - LOSS),
        after_delayed_cover=str(covered),
        ordinary_stages=stages,
        published_ordinary_admitted=CLAIMS[1],
        ordinary_admitted=CLAIMS[-1],
        above_previous_ordinary=rational_display(final - old_finite),
        above_public_7776_joint_raw_upper=rational_display(final - F(old_joint_raw_upper)),
        above_frozen_target=rational_display(final - TARGET),
        stock=dict(
            rho='1/250',
            w='ceil(e^rho)',
            D='2+ceil(log_N(max(1,ceil(e/w))))',
            small_width_backing='W(w)^D * predecessor',
            high_digit_backing='O_fixed(w log e)',
        ),
        record_scope='Conditional ordinary BIT under inherited physical, finite compiler, cover and stock theorems.',
    )
