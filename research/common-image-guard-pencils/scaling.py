"""Exact integer bracketing examples for three different limit regimes."""
from fractions import Fraction
from math import isqrt

from laws import direction
from windows import sign_window


def last_size(q, m):
    left, right = 2, q + 1
    while right - left > 1:
        mid = (left + right)//2
        if direction(q, mid, m) > 0:
            left = mid
        else:
            right = mid
    if direction(q, left, m) <= 0 or (left < q and direction(q, left + 1, m) > 0):
        raise ValueError("size cutoff endpoints")
    return left


def brackets():
    fixed_m, fixed_k, joint = [], [], []
    for q in (16, 64, 256, 1024, 4096):
        for m in (2, 3, 6, 11):
            last = last_size(q, m)
            fixed_m.append(dict(q=q, m=m, last_k=last, k_over_q=str(Fraction(last, q))))
        if q <= 1024:
            for k in (3, 4, 7):
                upper = sign_window(q, k)["positive"][-1]
                fixed_k.append(dict(q=q, k=k, last_m=upper, m_over_q=str(Fraction(upper, q))))
        k = isqrt(q)
        top = sign_window(q, k)["positive"][-1]
        joint.append(dict(q=q, k=k, last_m=top, d_k_over_q=str(Fraction((top - 1)*k, q))))
    return dict(fixed_dimension=fixed_m, fixed_size=fixed_k, growing_size_and_dimension=joint)
