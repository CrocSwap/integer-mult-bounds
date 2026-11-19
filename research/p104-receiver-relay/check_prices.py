"""Exact rational bounds for the three surcharges and the off-path lower floor."""
from fractions import Fraction as F
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from word import require


def logarithm(x):
    # Sum 2 atanh((x-1)/(x+1)) on [1,2], with a geometric upper tail.
    require(1 <= x <= 2, 'logarithm reduction')
    z = (x - 1) / (x + 1)
    z2 = z*z
    term = z
    total = F(0)
    for n in range(45):
        total += 2*term / (2*n + 1)
        term *= z2
    return total, total + 2*term / (91*(1-z2))


def exp_bounds(x):
    require(0 <= x <= F(1, 50), 'alternating exponential range')
    total = term = F(1)
    for j in range(1, 14):
        term *= -x/j
        total += term
    return total, total - term*x/14


def price(d):
    k = d.bit_length() - 1
    base = logarithm(F(2))
    rem = logarithm(F(d, 1 << k))
    kappa = F('0.00387981257853')
    left, right = (kappa * (k*base[i] + rem[i]) for i in (0, 1))
    return d*exp_bounds(right)[0], d*exp_bounds(left)[1]


def main():
    tariff = {d: price(d) for d in (1, 2, 4, 5, 7)}
    # Coefficients of the change relative to grades 2,5. In the last row
    # the comparison price is p(1)+p(7), a certified lower bound.
    cases = [
        ('split lower', {1: 2, 2: -1}, '0.257824154185337662623932'),
        ('split upper', {1: 1, 4: 1, 5: -1}, '0.464055177013712144726725'),
        ('split both', {1: 3, 2: -1, 4: 1, 5: -1}, '0.721879331199049807350658'),
        ('outside floor', {1: 1, 7: 1, 2: -1, 5: -1}, '47.224621260611063462113308'),
    ]
    previous = F(0)
    for name, coeffs, expected in cases:
        low = 48*sum(n*tariff[d][n < 0] for d, n in coeffs.items())
        high = 48*sum(n*tariff[d][n > 0] for d, n in coeffs.items())
        require(previous < low and F(expected) < low <= high < F(expected) + F(1, 10**24),
                name + ' price enclosure')
        previous = high
        print('PASS:', name, '48-call change in', expected, '+ (0, 1e-24)')


if __name__ == '__main__':
    main()
