#!/usr/bin/env python3
"""Exact finite and inductive arithmetic for the three-slope native profile."""
from fractions import Fraction as F

R = 240
NATIVE = F(433, 8)
WALSH = NATIVE + F(33, 4)
AUDIT_SLOPES = (F(17, 4), F(11, 3), F(10, 3))
DIRECT_END = R*((1 << 17)+2)


def ceil_log(u):
    return (u-1).bit_length()


def scale(j):
    return 3*j + ceil_log(3*j+3)+2


def location(j, a):
    return R*(a*scale(j)*(1 << (3*j))+2)


def at_breakpoints(last_j):
    y, height = DIRECT_END, F(DIRECT_END, 2)
    slope = AUDIT_SLOPES[0]/16
    yield "direct", y, height
    for j in range(4, last_j+1):
        d = 1 << j
        for a, c in zip((1, 2, 4), AUDIT_SLOPES):
            nxt = location(j, a)
            if nxt < y:
                continue
            height += slope*(nxt-y)
            y, slope = nxt, c/d
            yield (j, a), y, height


def main():
    first = list(at_breakpoints(5))[:4]
    # Compare each true finite log against a lower rational power certificate.
    for (endpoint, y, h), p, q in zip(first, (124, 25, 26, 1), (5, 1, 1, 1)):
        if endpoint == (5, 1):
            continue
        assert (y+2)**q > 1 << p
        assert h**3 <= NATIVE**3*y*y*F(p, q)
    _, _, h5 = first[-1]
    t5 = h5/(R*scale(5)*2**10)
    assert t5 == F(577283, 67584) < F(43, 5)
    assert 2*AUDIT_SLOPES[2] + F(1, 4)*(F(43, 5)-F(7, 4)) < F(43, 5)
    assert AUDIT_SLOPES[0] + 2*AUDIT_SLOPES[1] - 4*AUDIT_SLOPES[2] == -F(7, 4)
    upper_at = (F(43, 5), F(43, 5)+AUDIT_SLOPES[0],
                F(43, 5)+AUDIT_SLOPES[0]+2*AUDIT_SLOPES[1])
    assert all(R*c**3 < NATIVE**3*a*a for c, a in zip(upper_at, (1, 2, 4)))
    assert WALSH == F(499, 8)
    assert 4098**8 < 2**97 and F(336*97, 8) < 4096
    assert 336**2 > 48**3 and 4096**2*12 >= 576**3
    assert (F(63)-WALSH-F(1,12))*576 >= 182+2*WALSH+1
    assert 64*(1 << 24) >= 64*896
    assert 2000*32 <= 2**(32-7)

    # Check the recurrence on actual breakpoints far beyond its finite inputs.
    prev = None
    for event, _, height in at_breakpoints(180):
        if not isinstance(event, tuple) or event[0] < 5 or event[1] != 1:
            continue
        j = event[0]
        t = height/(R*scale(j)*(1 << (2*j)))
        if prev is not None:
            old_j, old = prev
            assert old_j+1 == j
            assert t == F(20,3) + F(scale(old_j),4*scale(j))*(old-F(7,4))
        assert t <= F(43,5)
        prev = j, t
    print("exact direct/j4/first later gates", [(x, y, str(h)) for x,y,h in first])
    print("staircase induction h5", t5, "and 175 subsequent exact transitions through j=180")
    print("smooth native", NATIVE, "Walsh", WALSH, "whole integer", 63)


if __name__ == "__main__":
    main()
