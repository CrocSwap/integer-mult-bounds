"""Directed arithmetic for the complete signed price."""
from fractions import Fraction as F
from functools import cache

TARGET = F(10018846261809, 2500000000000000)
GRID = 10**48


def round_interval(a, b):
    a, b = a*GRID, b*GRID
    return F(a.numerator//a.denominator, GRID), F(-((-b.numerator)//b.denominator), GRID)


@cache
def log_unit(x):
    y = (x-1)/(x+1)
    p = sum((2*y**j/j for j in range(1, 111, 2)), F(0))
    return round_interval(p, p+2*y**111/(111*(1-y*y)))


@cache
def power(rank, k):
    e = rank.bit_length()-1
    lo,hi = [q+e*d for q,d in zip(log_unit(F(rank, 2**e)),log_unit(F(2)),strict=True)]

    def exp_negative(x, n):
        term = total = F(1)
        assert 0 <= x < 1
        for i in range(1,n+1):
            term *= -x/i
            total += term
        return total

    return round_interval(rank*exp_negative(k*hi, 39), rank*exp_negative(k*lo, 40))


def moment(P, T, k):
    lower = upper = F(0)
    for r in P.keys()|T.keys():
        n = T[r]-P[r]
        lo,hi = power(r,k)
        if n < 0:
            lo,hi = hi,lo
        lower += n*lo
        upper += n*hi
    return lower,upper
