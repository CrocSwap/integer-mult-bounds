#!/usr/bin/env python3
"""Exact source-destination grid identity and optimistic recursive-cost screen."""

from decimal import Decimal, getcontext
from fractions import Fraction


def add_poly(dst, src):
    for monomial, coefficient in src.items():
        dst[monomial] = dst.get(monomial, 0) + coefficient
        if dst[monomial] == 0:
            del dst[monomial]


def mul_poly(left, right):
    out = {}
    for a, ca in left.items():
        for b, cb in right.items():
            monomial = tuple(sorted(a + b))
            out[monomial] = out.get(monomial, 0) + ca * cb
    return out


def formal_grid(r, n, bad_b_row=False, permute_y=False):
    """Return the exact scalar-polynomial product of the sparse block inputs."""
    size = r * n
    left = [[{} for _ in range(size)] for _ in range(size)]
    right = [[{} for _ in range(size)] for _ in range(size)]

    for i in range(r):
        for p in range(n):
            for q in range(n):
                left[i * n + p][q] = {(('x', i, p, q),): 1}

    row_offset = n if bad_b_row else 0
    for j in range(r):
        y_index = (j + 1) % r if permute_y else j
        for p in range(n):
            for q in range(n):
                right[row_offset + p][j * n + q] = {(('y', y_index, p, q),): 1}

    product = [[{} for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for k in range(size):
            if not left[i][k]:
                continue
            for j in range(size):
                if right[k][j]:
                    add_poly(product[i][j], mul_poly(left[i][k], right[k][j]))
    return product


def expected_grid(r, n):
    size = r * n
    expected = [[{} for _ in range(size)] for _ in range(size)]
    for i in range(r):
        for j in range(r):
            for p in range(n):
                for q in range(n):
                    out = expected[i * n + p][j * n + q]
                    for k in range(n):
                        monomial = tuple(sorted((('x', i, p, k), ('y', j, k, q))))
                        out[monomial] = 1
    return expected


def integer_nth_root_floor(value, degree):
    lo, hi = 0, 1
    while hi**degree <= value:
        hi *= 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid**degree <= value:
            lo = mid
        else:
            hi = mid
    return lo


def decimal_fraction(value, digits=32):
    getcontext().prec = digits + 8
    return format(Decimal(value.numerator) / Decimal(value.denominator), f'.{digits}f')


def main():
    identity_fixtures = 0
    for r in range(2, 7):
        for n in range(1, 4):
            want = expected_grid(r, n)
            got = formal_grid(r, n)
            assert got == want, (r, n, 'Cartesian block identity')
            identity_fixtures += 1

    want = expected_grid(3, 2)
    assert formal_grid(3, 2, bad_b_row=True) != want
    assert formal_grid(3, 2, permute_y=True) != want

    # A generic width-r product at exponent 2-a costs r^(2-a) child units;
    # the r^2 separate products cost r^2. The best ratio in the bounded domain
    # occurs at r=51 and a=1/99.
    numerator = 20**99
    denominator = 19**99
    assert 51 * denominator < numerator
    assert 160 * denominator < numerator <= 161 * denominator

    # Certify a decimal bracket for 51^(-1/99) using only integer arithmetic.
    digits = 30
    scale = 10**digits
    power_scale = scale**99
    root_floor = integer_nth_root_floor(power_scale // 51, 99)
    assert 51 * root_floor**99 <= power_scale
    assert power_scale < 51 * (root_floor + 1) ** 99
    ratio_lo = Fraction(root_floor, scale)
    ratio_hi = Fraction(root_floor + 1, scale)
    saving_lo = 100 * (1 - ratio_hi)
    saving_hi = 100 * (1 - ratio_lo)
    assert saving_hi < 5

    print(
        'PASS_CARTESIAN_GRID_COST_SCREEN',
        f'identity_fixtures={identity_fixtures}',
        'rank_domain=2..51',
        'exponent_domain=0..1/99',
        'max_saving_percent=(' + decimal_fraction(saving_lo) + ',' + decimal_fraction(saving_hi) + ')',
        'first_width_at_5_percent=161',
        'controls=4',
    )


if __name__ == '__main__':
    main()
