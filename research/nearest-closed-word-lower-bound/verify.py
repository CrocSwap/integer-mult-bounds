#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check quadratic error under actual nearest coefficient rounding."""
from fractions import Fraction as Q
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def mul(a, b):
    return [[sum(x*y for x, y in zip(r, c)) for c in zip(*b)] for r in a]


def norm(a):
    return max(sum(abs(x) for x in r) for r in a)


def inv(a):
    x, y = a[0]; z, w = a[1]
    d = x*w-y*z
    need(d != 0, 'singular gate')
    return [[w/d, -y/d], [-z/d, x/d]]


I = [[Q(1), Q(0)], [Q(0), Q(1)]]
S = [[Q(1, 2), Q(0)], [Q(0), Q(2)]]


def shear(t):
    return [[Q(1), t], [Q(0), Q(1)]]


def nearest(t, h):
    v = t/h + Q(1, 2)
    return h * (v.numerator // v.denominator)


def run():
    cases = prefixes = small = 0
    for q in range(1, 13):
        for m in (1, 2, 5, q):
            for p in (1, 3, 2*q + m.bit_length() + 4):
                for kind in ("dyadic", "thirds"):
                    h = Q(1, 1 << p); s = Q(1 << q)
                    a = 3*h/8 if kind == "dyadic" else Q(1, 3)
                    sign = -1 if kind == "dyadic" else (-1)**(p+1)
                    gates = [S]*q + [shear(a), shear(a), shear(-2*a)]*m + [inv(S)]*q
                    exact = I; changed = I; b = Q(1)
                    for gate in gates:
                        need(norm(gate) <= 2 and norm(inv(gate)) <= 2, 'bounded exact gates')
                        rounded = [[nearest(v, h) for v in row] for row in gate]
                        need(all((v/h) % 1 != Q(1, 2) for row in gate for v in row), 'no rounding ties')
                        need(norm(rounded) <= 2 and norm(inv(rounded)) <= 2, 'bounded rounded gates')
                        need(rounded[0][0]*rounded[1][1]-rounded[0][1]*rounded[1][0] == 1, 'determinant')
                        exact = mul(gate, exact); changed = mul(rounded, changed)
                        b = max(b, norm(exact), norm(inv(exact)))
                        prefixes += 1
                    need(exact == I, 'closed exact word')
                    need(changed == shear(sign*m*h*s*s), 'literal nearest-rounding endpoint')
                    need(b == s*(1+2*a), 'literal prefix/inverse maximum')
                    need(len(gates) == 2*q+3*m, 'gate count')
                    need(norm([[changed[i][j]-I[i][j] for j in range(2)] for i in range(2)]) == m*h*s*s, 'exact error')
                    small += m*h*s*s <= Q(1, 16)
                    cases += 1
    h = Q(1, 8); a = 3*h/8
    need(nearest(a, h) + nearest(a, h) + nearest(-2*a, h) == -h, 'three-shear defect')
    need(nearest(a, h) + nearest(-a, h) == 0, 'opposite pair cancels')
    need(nearest(Q(1, 2), h) == Q(1, 2), 'scales are exact')
    need(mul(shear(a), shear(a)) != I, 'missing closing shear')
    return dict(status='PASS_DETERMINISTIC_CLOSED_WORD', cases=cases,
                literal_prefixes=prefixes, small_error_cases=small, controls=4,
                no_new_kappa=True)


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
