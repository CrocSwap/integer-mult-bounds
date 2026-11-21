#!/usr/bin/env python3
"""Exact weak-duality verifier for the Q >= 1, e = 0 thin-column caller LP (notes/leanthin.md, notes/thinq.md).
Standard library only.  [C] exact: integer duals y/2^110, exhaustive integer partition DP over ALL (D, P), D <= k;
(8D+1)^0.99 is rounded UP and (8p)^0.99 rounded DOWN (decimal at 80 digits, plus one unit of 2^-110 of slack).
LP: roles x_{D,P} with rows DEEP, SET-RC2 (c <= 3), count n >= 2k-1, LEAFAVG, LC, TRIPLE-in-class; objective
F = 2k-2 + sum x (val - 1), val = (8D+1)^s - sum_p (8p)^s, s = 0.99, chat = 104 F / k.
Weak duality: y >= 0.  For every type j: val_j - 1 + y.A_j <= eps.  Then F <= 2k-2 - y.b + max(eps,0) nmax (F >= 0) with
nmax = (2k-2)/(1-(9^s-8^s)); eps is absorbed by lowering the LEAFAVG dual when possible ('leafshift').
usage: verify_q1.py [k ...]   (default: every q1_k*.json beside this file)"""
import glob, json, os, sys
from decimal import Decimal, getcontext
from fractions import Fraction
from math import comb

getcontext().prec = 80
HERE = os.path.dirname(os.path.abspath(__file__))
SC = Decimal('0.99')
BAR = Fraction(128891, 1000)


def pwd(x):
    return (SC * Decimal(x).ln()).exp()


def rows_of(k):
    return [(l, c) for c in range(1, min(3, k - 1) + 1) for l in range(2, k + 1)]


def verify(k):
    J = json.load(open(os.path.join(HERE, 'q1_k%d.json' % k)))
    S = J['S']
    Y = [int(t) for t in J['y']]
    assert J['k'] == k and all(t >= 0 for t in Y)
    rows = rows_of(k)
    nr = len(rows)
    assert len(Y) == 2 + nr + 4
    one = 1 << S
    D1 = Decimal(one)
    up = lambda x: int((x * D1).to_integral_value(rounding='ROUND_CEILING')) + 1
    lo = lambda x: int((x * D1).to_integral_value(rounding='ROUND_FLOOR')) - 1
    ubA = {D: up(pwd(8 * D + 1)) for D in range(1, k + 1)}
    lbB = {L: lo(pwd(8 * L)) for L in range(1, k + 1)}
    y0, y1 = Y[0], Y[1]
    yr = Y[2:2 + nr]
    yc, yl, ylc, yt = Y[2 + nr:]
    eps = None
    arg = None
    for D in range(1, k + 1):
        g = [None]
        for L in range(1, D + 1):
            t = -lbB[L]
            for q, (l, c) in enumerate(rows):
                if yr[q] == 0:
                    continue
                av = comb(k - L, c)
                if D >= l:
                    if L < l:
                        t += yr[q] * L * av
                else:
                    t += yr[q] * L * (av - comb(k - D, c))
            if L == 1:
                t += y0 + (y1 if D >= 2 else 0)
            g.append(t)
        best = [0] + [None] * D
        for d in range(1, D + 1):
            best[d] = max(best[d - L] + g[L] for L in range(1, d + 1))
        rc = ubA[D] + best[D] - one + yc + yl * (k - (1 if D == 1 else 0)) + (ylc if D >= 2 else 0) \
            + yt * (comb(D, 3) + comb(D, 2) * (k - D))
        if eps is None or rc > eps:
            eps, arg = rc, D
    b = [2 * k, 2 * k] + [2 * k * comb(k - 1, c) for (l, c) in rows] + [2 * k - 1, k * (2 * k - 2), k - 2, 3 * comb(k, 3)]
    ileaf = 2 + nr + 1
    Y = list(Y)
    mode, eps_used = 'none', 0
    if eps > 0:
        delta = -((-eps) // (k - 1))
        if Y[ileaf] >= delta:
            Y[ileaf] -= delta
            mode = 'leafshift'
        else:
            eps_used, mode = eps, 'nmax'
    yb = sum(Fraction(Y[i] * b[i], one) for i in range(len(b)))
    F = 2 * k - 2 - yb
    if eps_used > 0:
        v1 = Fraction(up(pwd(9)), one) - Fraction(lo(pwd(8)), one)
        assert v1 < 1
        F += Fraction(eps_used, one) * Fraction(2 * k - 2) / (1 - v1)
    chat = Fraction(104) * F / k
    return chat, eps, arg, J['float_chat'], mode


if __name__ == '__main__':
    ks = [int(a) for a in sys.argv[1:]] or sorted(int(os.path.basename(p)[4:-5]) for p in glob.glob(HERE + '/q1_k*.json'))
    res = {}
    for k in ks:
        chat, eps, arg, fl, mode = verify(k)
        res[k] = chat
        print('Q1-thin-LP k%d [%s]: float %.6f  EXACT chat <= %.6f  (%s bar 128.891; margin %.4f)' % (
            k, mode, fl, float(chat), 'BELOW' if chat < BAR else 'ABOVE', float(BAR - chat)), flush=True)
        assert abs(float(chat) - fl) < 1e-2, 'certificate far from the float optimum'
    if 77 in res:
        assert all(res[k] < BAR for k in res if k >= 77), 'a k >= 77 certificate is not below the bar'
    if 76 in res:
        assert res[76] >= BAR
    print('PASS')
