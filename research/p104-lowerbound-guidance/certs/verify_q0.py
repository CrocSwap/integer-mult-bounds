#!/usr/bin/env python3
"""Exact weak-duality verifier for the Q = 0 RC2 caller LP (the 'CC model' of notes/callercut.md, notes/kasym.md).
Standard library only.  [C] exact: rational duals + exhaustive partition DP; (8L)^0.99 and (8D+1)^0.99 are evaluated
with decimal at 60 digits (error far below 1e-50), and the printed bound is rounded UP by 1e-30.

LP (types t = (D, P, mf): a role of degree D, piece multiset P, parts <= min(D, k-2), D = 2..k;
mf = 1 only when P contains a 1; if P has no 1 all parts are >= 2):
  max  sum_t x_t val(t),  val = (8D+1)^s - sum_{L in P} (8L)^s,  s = 0.99
  s.t. sum x_t = n = 2k-2 ;  sum_t mf(t) x_t = 2k ;  sum_t a_i(t) x_t >= b_i  for every row i (rows below), x >= 0.
Rows (sep, e, ones, ell, coord, shal, pfix, dyadic dm, RC_l, RC2_l) are the laws of notes/callercut.md (RC2: [P], Lean:
rc2_pair in #7852's CallerRC2; coord/pfix/shal/dyadic: [P] on paper, notes/scherk.md, notes/bilinear.md).  Every row is
re-derived HERE from its definition.  Weak duality: for dual w >= 0 (inequality rows), y, wm free,
  chat = 104 B / k,   B = n (M - y) - sum_i w_i b_i - 2k wm,   M = max_t [ val + sum_i w_i a_i(t) + wm mf(t) + y ].
usage: verify_q0.py [k ...]   (default: every q0_k*.json beside this file)"""
import json, os, sys
from decimal import Decimal, getcontext
from fractions import Fraction as Fr
from math import comb

getcontext().prec = 60
HERE = os.path.dirname(os.path.abspath(__file__))
S = Decimal('0.99')
BAR = Decimal('128.891')
_pw = {}


def pw(x):  # x ** 0.99
    if x not in _pw:
        _pw[x] = (S * Decimal(x).ln()).exp()
    return _pw[x]


def dec(q):
    return Decimal(q.numerator) / Decimal(q.denominator)


def sk2RJ(k, J):
    return sum(2 * (len(range(j, k, 2 ** l)) // 2) for l in range(J + 1) for j in range(2 ** l))


def rowdefs(k, J):
    """[(b, c0(D), f(D, l), z(D))]: a(D, P) = c0(D) + sum_{l in P} f(D, l) + z(D) [1 not in P]; order = dual order."""
    n = 2 * k - 2
    out = [(Fr(k * (k - 1)), lambda D: Fr(D * D, 2), lambda D, l: Fr(-l * l, 2), lambda D: Fr(0)),   # sep
           (Fr(2 * k - 2), lambda D: Fr(-1), lambda D, l: Fr(1), lambda D: Fr(0)),                   # e
           (Fr(2 * k), lambda D: Fr(0), lambda D, l: Fr(int(l == 1)), lambda D: Fr(0))]              # ones
    for ll in range(2, k - 1):                                                                       # ell_2..ell_{k-2}
        out.append((Fr(k * (k - 1)), lambda D, ll=ll: Fr((ll <= D <= k - 1) * D * (k - D)),
                    lambda D, l, ll=ll: Fr(l * (D - l) * (l < ll), 2), lambda D: Fr(0)))
    for th in range(2, k + 1):                                                                       # coord
        out.append((Fr(0), lambda D: Fr(0),
                    lambda D, l, th=th: Fr(2 * l * (2 <= l <= th) + (1 if (l == 1 and D > th) else 0)),
                    lambda D: Fr(-1)))
    out.append((Fr(k), lambda D: Fr(0), lambda D, l: Fr(2 * (l == 2) + (1 if (l == 1 and D >= 3) else 0)),
                lambda D: Fr(0)))                                                                    # shal
    for x in range(1, k):                                                                            # pfix
        ck = comb(k, x)
        out.append((Fr(-(n - 2 * x)), lambda D, x=x, ck=ck: Fr(-comb(k - D, x), ck),
                    lambda D, l, x=x, ck=ck: (Fr(-comb(l, x), ck) if l >= 2 else Fr(0)), lambda D: Fr(0)))
    for a in range(1, J + 1):                                                                        # dyadic dm_a
        out.append((Fr(sk2RJ(k, a)), lambda D, a=a: Fr(min(D, 2 ** (a + 1)) - 1), lambda D, l: Fr(0),
                    lambda D: Fr(0)))
    for a in range(3, k + 1):                                                                        # RC_a
        out.append((Fr(2 * k), lambda D, a=a: (Fr(0) if D >= a else Fr(D * (D - 1), k - 1)),
                    lambda D, l, a=a: (Fr(l * (l < a)) if D >= a else Fr(0)), lambda D: Fr(0)))
    for a in range(3, k + 1):                                                                        # RC2_a
        out.append((Fr(2 * k), lambda D, a=a: (Fr(0) if D >= a else Fr(D * D, k - 1)),
                    lambda D, l, a=a: (Fr(l * (k - l) * (l < a), k - 1) if D >= a else Fr(-l * l, k - 1)),
                    lambda D: Fr(0)))
    return out


def bound(k, du, y, wm, J):
    """returns (chat upper bound as Decimal, argmax (D, mf, hasone))"""
    n = 2 * k - 2
    rd = rowdefs(k, J)
    assert len(rd) == len(du), (len(rd), len(du))
    assert all(d >= 0 for d in du)
    act = [(d, r) for d, r in zip(du, rd) if d != 0]
    Lmax = k - 2
    M = None
    arg = None
    for D in range(2, k + 1):
        Lm = min(D, Lmax)
        C0 = sum((d * c0(D) for d, (b, c0, f, z) in act), Fr(0)) + y
        Z = sum((d * z(D) for d, (b, c0, f, z) in act), Fr(0))
        g = [None] + [dec(sum((d * f(D, l) for d, (b, c0, f, z) in act), Fr(0))) - pw(8 * l) for l in range(1, Lm + 1)]
        for mf, hasone in ((0, 0), (0, 1), (1, 1)):
            gg = list(g)
            if mf:
                gg[1] += dec(wm)
            best = [Decimal(0)] + [None] * D
            for d in range(1, D + 1):
                c = [best[d - l] + gg[l] for l in range(1 if hasone else 2, min(d, Lm) + 1) if best[d - l] is not None]
                best[d] = max(c) if c else None
            if hasone:
                if best[D - 1] is None:
                    continue
                tot = gg[1] + best[D - 1]
            else:
                if best[D] is None:
                    continue
                tot = best[D] + dec(Z)
            sc = tot + pw(8 * D + 1) + dec(C0)
            if M is None or sc > M:
                M, arg = sc, (D, mf, hasone)
    bsum = sum((d * b for d, (b, c0, f, z) in zip(du, rd)), Fr(0))
    B = n * (M - dec(y)) - dec(bsum) - dec(wm * 2 * k)
    return Decimal(104) * B / k + Decimal('1e-30'), arg


def check(path):
    c = json.load(open(path))
    k = c['k']
    du = [Fr(s) for s in c['dual']]
    J = len(du) - (5 * k - 5)
    assert 1 <= J <= 12, J
    chat, arg = bound(k, du, Fr(c['y']), Fr(c['wm']), J)
    print('Q0-RC2-LP k=%d rows=%d  certified chat <= %s  argmax(D,mf,hasone)=%s  bar 128.891: %s' % (
        k, len(du), format(chat, '.10f'), arg, 'BELOW' if chat < BAR else 'ABOVE'))
    return k, chat, du, Fr(c['y']), Fr(c['wm']), J


if __name__ == '__main__':
    ks = [int(a) for a in sys.argv[1:]] or [71, 72, 73]
    res = {}
    for k in ks:
        kk, chat, du, y, wm, J = check(os.path.join(HERE, 'q0_k%d.json' % k))
        res[k] = chat
        if k == 71:
            assert chat > BAR       # k = 71 stays above the bar: the open window
        else:
            assert chat < BAR, 'bound not below bar'
        # tolerance for the documented float values
    assert abs(res.get(72, Decimal('128.8500719')) - Decimal('128.85007')) < Decimal('1e-4')
    assert abs(res.get(73, Decimal('128.6813251')) - Decimal('128.68133')) < Decimal('1e-4')
    # negative control: all-zero duals (y = wm = 0) must NOT certify the bar
    k = ks[-1]
    du = [Fr(0)] * len(json.load(open(os.path.join(HERE, 'q0_k%d.json' % k)))['dual'])
    J = len(du) - (5 * k - 5)
    ch, _ = bound(k, du, Fr(0), Fr(0), J)
    assert ch > BAR, ch
    print('control (zero dual, k=%d): bound %s > bar, as required' % (k, format(ch, '.4f')))
    print('PASS')
