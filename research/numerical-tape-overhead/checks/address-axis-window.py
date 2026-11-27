#!/usr/bin/env python3
"""Exact finite witnesses and inequalities for the k >= 2^32 coprime-axis proof."""
from fractions import Fraction as F
from math import factorial, isqrt, prod


def primes_up_to(n):
    flags = [True] * (n+1)
    flags[:2] = [False, False]
    for p in range(2, isqrt(n)+1):
        if flags[p]:
            for x in range(p*p, n+1, p):
                flags[x] = False
    return [i for i, prime in enumerate(flags) if prime]


def main():
    primes = primes_up_to(65536)
    for extent, reciprocal, expected_count in ((256,10,54), (65536,20,6542)):
        ps = [p for p in primes if p <= extent]
        num = prod(p-1 for p in ps)
        den = prod(ps)
        assert len(ps) == expected_count and reciprocal*num > den
        print('exact survival on primes through', extent, 'exceeds 1/'+str(reciprocal),
              'using', len(ps), 'primes')

    assert sum(F(7,10)**n/factorial(n) for n in range(4)) > 2
    ln2_lo = 2 * (F(1,3) + F(1,3)**3/3)
    ln5_lo = 2 * sum(F(2,3)**(2*j+1)/(2*j+1) for j in range(5))
    assert (F(8,5)*F(65536,65535) < F(1601,1000) < ln5_lo)
    assert F(9,5)*F(256,255) < 3*ln2_lo - F(1,7)
    assert F(11,5)*F(16,15) < 3*ln2_lo + F(1,3)
    assert 4 < 6*ln2_lo
    assert all(F(7,5)+F(3,a) < bound for a,bound in
               ((16,F(8,5)), (8,F(9,5)), (4,F(11,5)), (2,F(3))))
    loss = sum(inv*mass**degree/factorial(degree) for inv,mass,degree in
               ((5,F(8,5),5), (7,F(9,5),7), (12,F(11,5),9), (64,F(3),11)))
    loss += 64*F(3)**13/factorial(13)/(1-F(9,14*15))
    assert loss < F(7,8)
    print('Bonferroni relative loss <=', loss, '< 7/8')

    b = 44  # 11*32/8
    ratio = F(3,2)*b*b/F(2)**12
    assert ratio == F(363,512) < F(3,4)
    assert 24*F(2)**24/F(2)**44 < F(1,1024)
    assert 3*b*b/F(2)**(17*32) < F(1,1024)
    assert F(3,4) + 2*F(1,1024) < 1
    print('main-term fractions: leading large-prime loss at first endpoint is', ratio,
          '; interval discrepancy and final +1 loss are each < 1/1024')


if __name__ == '__main__':
    main()
