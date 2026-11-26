"""Exact rational enclosures of the 29-row Walsh clock, in binary log units."""
from fractions import Fraction
from functools import cache
from itertools import count

F = Fraction
GRID = 1 << 80
SURPLUS = F(159, 4)
Z = 7_519_517_465_920_988
ANCHOR = 6_201_245_580_657_120


def log_ratio_interval(t):
    """Return lower/upper bounds on log((1+t)/(1-t)), 0 <= t <= 1/3."""
    assert 0 <= t <= Fraction(1, 3)
    square = t * t
    power = t
    total = Fraction(0)
    for index in range(24):
        total += 2 * power / (2 * index + 1)
        power *= square
    tail = 2 * power / (49 * (1 - square))
    return total, total + tail


LOG_TWO = log_ratio_interval(Fraction(1, 3))


def log_two_interval(value):
    exponent = value.bit_length() - 1
    unit = 1 << exponent
    lower, upper = log_ratio_interval(Fraction(value - unit, value + unit))
    return exponent + lower / LOG_TWO[1], exponent + upper / LOG_TWO[0]


log_interval = cache(log_two_interval)


def icbrt(n):
    if n < 2:
        return n
    v = 1 << ((n.bit_length() + 2) // 3)
    while True:
        w = (2*v + n//(v*v)) // 3
        if w >= v:
            assert v**3 <= n < (v+1)**3
            return v
        v = w


@cache
def phi(x):
    lower, upper = log_interval(x+2)
    a = x*x*GRID**3
    lo = icbrt(a*lower.numerator//lower.denominator)
    hi = icbrt(a*upper.numerator//upper.denominator) + 1
    return F(lo, GRID), F(hi, GRID)


def q(j):
    return 3*j+(3*j+2).bit_length()+2


def e_upper(j):
    return F(j+(8*q(j+1)).bit_length()+3, q(j))


def edges():
    yield 0, F(1, 2)
    yield 240*(2**17+2), (3+e_upper(4))/16
    for j in count(4):
        for a in (1, 2, 4):
            if j == 4 and a == 1:
                continue
            yield 240*(a*q(j)*8**j+2), (3+e_upper(j)/a)/2**j


def vertices(x):
    height = F(0)
    prev, slope = 0, F(0)
    for start, next_slope in edges():
        if start > x:
            break
        height += slope*(start-prev)
        yield start, height, next_slope
        prev, slope = start, next_slope
    if prev != x:
        yield x, height+slope*(x-prev), slope


def check_adjacent(z):
    data = list(vertices(z+2))
    intervals = []
    for x, h, _ in data:
        lower, upper = phi(x)
        intervals.append((h-SURPLUS*upper, h-SURPLUS*lower, x))
    lower, upper, arg = max(intervals)
    assert arg == ANCHOR
    assert all(a_high < lower for _, a_high, v in intervals if v != ANCHOR)
    pl, ph = phi(z+2)
    ll, lh = log_interval(z+2)
    residual = (F(z,1000)-183-4*lh-48*ph-upper, F(z,1000)-183-4*ll-48*pl-lower)
    return residual, data, (lower,upper)


if __name__ == "__main__":
    for z, lower, upper in ((Z-1, -325836553, -325836552), (Z, 53248687, 53248688)):
        gap, knots, peak = check_adjacent(z)
        assert len(knots) == 30     # includes the test point itself
        height = next(h for width, h, _ in knots if width == ANCHOR)
        assert height == F(890362700843914785456, 158055205)
        assert lower < gap[0]*10**12 <= gap[1]*10**12 < upper
        print(f"t={z}   residual × 10^12 in ({lower}, {upper})   peak width={ANCHOR}")
