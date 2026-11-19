"""Directed price bounds for the release of the two private slots and one exterior slot."""
from fractions import Fraction
from functools import cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from word import require


# Rigorous price intervals adapted from the rational checks in #7808 and #7814.
@cache
def price(d):
    if d == 0:
        return Fraction(0), Fraction(0)

    def log_bounds(x):
        z = (x - 1) / (x + 1)
        u, total = z, Fraction(0)
        for j in range(45):
            total += 2 * u / (2 * j + 1)
            u *= z * z
        return total, total + 2 * u / (91 * (1 - z*z))

    def exp_neg_bounds(x):
        require(0 <= x < Fraction(1, 50), 'alternating exponential terms decrease')
        u = total = Fraction(1)
        for j in range(1, 14):
            u *= -x / j
            total += u
        return total, total - u * x / 14

    k = d.bit_length() - 1
    base, rest = log_bounds(Fraction(2)), log_bounds(Fraction(d, 1 << k))
    low, high = (Fraction('0.00387981257853') * (k*base[i] + rest[i]) for i in (0, 1))
    return d * exp_neg_bounds(high)[0], d * exp_neg_bounds(low)[1]


def main():
    p = [price(i) for i in range(10)]
    # delta prices the compulsory side information after extraction of two
    # independent lower-source paths. For grade >=8 reserve delta per edge.
    dl,dh = p[2][0]+p[5][0]-p[7][1],p[2][1]+p[5][1]-p[7][0]
    c = p[9][0]/9
    require(0 < dl <= dh < p[1][0], 'strict splitting surcharge')
    require(all(p[g][0] >= g*c for g in range(1,10)), 'all directed grade prices')
    require(8*(c-dh) > p[7][1], 'one detour pays for each exit')
    require(15*c > 2*p[1][1]+p[5][1]+p[7][1], 'outside minimal grade exceeds runner-up')
    for d, value in ((1,'285.472830172972358520270568'),(5,'94.966797106425725799489376')):
        base = Fraction(value)
        require(base < 48*(p[7][0]-p[d][1]) <= 48*(p[7][1]-p[d][0]) <
                base + Fraction(1,10**24), 'net funded surcharge')
    runner = Fraction('0.257824154185337662623932')
    require(runner < 48*(2*p[1][0]-p[2][1]) <= 48*(2*p[1][1]-p[2][0]) <
            runner + Fraction(1,10**24), 'runner-up')
    print('PASS protected side-exit charge, nonminimal path and network gaps, '
          '48-call tariff differences in rational intervals of width 10^-24.')


if __name__ == '__main__':
    main()
