#!/usr/bin/env python3
"""Independent interval replay of native + Walsh historical endpoint, all rational."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import count

SCALE = 1 << 112
TERMS = 52
GAMMA = F(33,4)


@lru_cache(maxsize=200)
def ln_range(r):
    z = (r-1)/(r+1)
    a = z*z
    p = z
    s = F(0)
    for j in range(TERMS):
        s += p/(2*j+1)
        p *= a
    return 2*s, 2*(s+p/((2*TERMS+1)*(1-a)))


@lru_cache(maxsize=200)
def log_range(n):
    e = n.bit_length()-1
    l,u = ln_range(F(n,1 << e))
    a,b = ln_range(F(2))
    return e+l/b, e+u/a


def cube_floor(n):
    if n == 0:
        return 0
    x = 1 << ((n.bit_length()+2)//3)
    while not (x**3 <= n < (x+1)**3):
        y = (2*x+n//(x*x))//3
        x = min(x-1, y) if y == x else y
    return x


@lru_cache(maxsize=200)
def phi_range(n):
    l,u = log_range(n+2)
    def scaled_root(x):
        a = x*n*n*SCALE**3
        return cube_floor(a.numerator//a.denominator)
    return F(scaled_root(l),SCALE), F(scaled_root(u)+1,SCALE)


def q(j):
    s = 3*j+3
    return 3*j+(s-1).bit_length()+2


def letter_slopes(j):
    d = 1 << j
    upper_e = F(j+(8*q(j+1)).bit_length()+3, q(j))
    return [(a, (3+upper_e/a)/d) for a in (1,2,4)]


def knots_to(x):
    y = 240*(2**17+2)
    h = F(y,2)
    yield 0, F(0)
    if x <= y:
        yield x, F(x,2)
        return
    yield y,h
    slope = letter_slopes(4)[0][1]
    for j in count(4):
        d = 1 << j
        slopes = letter_slopes(j)
        for a, next_slope in slopes:
            end = 240*(a*q(j)*d**3+2)
            if end < y:
                continue
            if x <= end:
                yield x, h+(x-y)*slope
                return
            h += (end-y)*slope
            y, slope = end, next_slope
            yield y,h
    raise ValueError(x)


def invoice(z):
    x = z+2
    knots = list(knots_to(x))
    surplus = []
    for t,h in knots:
        pl,pu = phi_range(t)
        surplus.append((h-(48-GAMMA)*pu, h-(48-GAMMA)*pl, t))
    floor_index = max(range(len(surplus)), key=lambda i: surplus[i][0])
    slo, shi, winner = surplus[floor_index]
    assert all(uh < slo for i,(_,uh,_) in enumerate(surplus) if i != floor_index)
    pl,pu = phi_range(x)
    ll,lu = log_range(x)
    return (F(z,1000)-183-4*lu-48*pu-shi,
            F(z,1000)-183-4*ll-48*pl-slo, winner, len(knots))


def verify(z):
    for point in (z-1,z):
        lo,hi,winner,total=invoice(point)
        assert (hi < 0) if point < z else (lo > 0)
        assert winner == 6201245580657120 and total == 30
        assert hi-lo < F(1,10**28)
        print(point, "residual × 10^12 in",
              (lo*10**12).__floor__(), (hi*10**12).__ceil__(),
              "winning native width", winner, "of", total, "knots")


if __name__ == "__main__":
    verify(7519517465920988)
