#!/usr/bin/env python3
"""Exact checks for two review items on PR #2044 (research/capped-fusion-t74-k554, head 322949a5).

Item 1: the disabled `... or True` assertion at outer/check_gaugefree.py:23 (the s = -dl/lam bracket),
        Lemma 2.1 / Lemma 2.2 of outer/GAUGEFREE-INTERIORS.md, the narrow-kernel completion, the
        normalisation identity and the shrunk-shift coefficients. Exact Laurent-polynomial expansion
        over Q (a certificate), independent Fraction evaluation at random rational points (fixed
        seed) and three mutation controls that must be rejected.
Item 2: every per-record g^2 / g|F| / 2beta / g-fold charge found in the sweep, evaluated exactly at
        the final point rebuilt from this package's POINTS.json (same evaluator and SHA-256
        fingerprints as verify.py), with expected truth values, independent ledger-row formulas
        transcribed from outer/check_ledger.py, and rejecting controls.

Default mode (no arguments) is self-contained: it reads only POINTS.json next to this file.
--source-root DIR (an export containing research/capped-fusion-t74-k554 at #2044 head) adds file
level checks: SHA-256/git-blob pins, exact text of the cited check_gaugefree.py lines, the line-23
bracket parsed by `ast` and compared with the certified bracket, the vacuous-assert scan of outer/*.py,
check_ledger.py / run_outer.py dependence facts, every cited file:line anchor (+-2 lines), and the
LEDGER.json values of every ledger row and rejecting control used below.

Standard library only; Python 3.10+; run as `python3 -I -B review_items.py [--source-root DIR]`.
-O is refused (exit 2). No network, no subprocess, no git. Writes nothing.
"""
import sys

if sys.flags.optimize:
    sys.stderr.write('review_items.py refuses to run under -O/-OO\n')
    sys.exit(2)

import argparse
import ast
import hashlib
import json
import random
import time
from decimal import Decimal, localcontext
from fractions import Fraction as Fr
from pathlib import Path

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

HERE = Path(__file__).resolve().parent
PKG_REL = 'research/capped-fusion-t74-k554'
HEAD = '322949a53488d64023fedb89a6774927707e57ba'
RANDOM_SEED = 20441876
NPTS = 1500

RESULTS = []          # (section, name, ok, info)
SECTION = ['?']


def check(name, ok, info=''):
    RESULTS.append((SECTION[0], name, bool(ok), info))


# ================================================================ exact Laurent polynomials over Q
VARS = ('x', 'y', 'dl', 'lam', 's', 'b0', 'th', 'rho', 'a', 'be0', 'ti', 'h', 'i', 'j', 'c', 'u')
IDX = {v: k for k, v in enumerate(VARS)}
NV = len(VARS)
ZERO = (0,) * NV


class P:
    """Laurent polynomial {exponent tuple (ints, may be negative): Fraction}."""
    __slots__ = ('t',)

    def __init__(self, t=None):
        self.t = {k: Fr(v) for k, v in (t or {}).items() if v != 0}

    @staticmethod
    def lift(o):
        return o if isinstance(o, P) else P({ZERO: Fr(o)})

    def __add__(self, o):
        o = P.lift(o)
        r = dict(self.t)
        for k, v in o.t.items():
            r[k] = r.get(k, 0) + v
        return P(r)
    __radd__ = __add__

    def __neg__(self):
        return P({k: -v for k, v in self.t.items()})

    def __sub__(self, o):
        return self + (-P.lift(o))

    def __rsub__(self, o):
        return P.lift(o) - self

    def __mul__(self, o):
        o = P.lift(o)
        r = {}
        for k1, v1 in self.t.items():
            for k2, v2 in o.t.items():
                k = tuple(p + q for p, q in zip(k1, k2))
                r[k] = r.get(k, 0) + v1 * v2
        return P(r)
    __rmul__ = __mul__

    def __pow__(self, n):
        if not (isinstance(n, int) and n >= 0):
            raise ValueError('only non-negative integer powers')
        r = P.lift(1)
        for _ in range(n):
            r = r * self
        return r

    def inv(self):
        if len(self.t) != 1:
            raise ValueError('only monomials are invertible here')
        (k, v), = self.t.items()
        return P({tuple(-e for e in k): 1 / v})

    def __truediv__(self, o):
        return self * P.lift(o).inv()

    def __rtruediv__(self, o):
        return P.lift(o) * self.inv()

    def iszero(self):
        return not self.t

    def __eq__(self, o):
        return (self - P.lift(o)).iszero()

    __hash__ = None

    def subs(self, name, val):
        val = P.lift(val)
        ix = IDX[name]
        r = P()
        for k, v in self.t.items():
            e = k[ix]
            k0 = list(k)
            k0[ix] = 0
            f = val ** e if e >= 0 else val.inv() ** (-e)
            r = r + P({tuple(k0): v}) * f
        return r

    def coeff(self, name, power):
        ix = IDX[name]
        return P({tuple(0 if n == ix else e for n, e in enumerate(k)): v
                  for k, v in self.t.items() if k[ix] == power})

    def __repr__(self):
        parts = []
        for k, v in sorted(self.t.items()):
            mon = '*'.join(VARS[n] + ('^%d' % e if e != 1 else '') for n, e in enumerate(k) if e)
            parts.append(str(v) + ('*' + mon if mon else ''))
        return ' + '.join(parts) or '0'


V = {n: P({tuple(1 if m == IDX[n] else 0 for m in range(NV)): 1}) for n in VARS}
x, y, dl, lam, s, b0, th, rho, a, be0, ti, h, i_, j_, c_, u = (V[n] for n in VARS)

# Lemma 2.1, general s (the identity asserted live at check_gaugefree.py:21; claim = -b0 * RHS at :20)
LHS = (x - lam * y + dl) ** 2 - lam * (x - y - s) ** 2
RHS = ((1 - lam) * x ** 2 - lam * (1 - lam) * y ** 2 + dl ** 2 - lam * s ** 2
       + 2 * (dl + lam * s) * x - 2 * lam * (dl + s) * y)
# s = -dl/lam: the correct bracket (PR1876, Rohan Arun) and the expression disabled at check_gaugefree.py:23
CORRECT = (1 - lam) * x ** 2 - lam * (1 - lam) * y ** 2 + dl ** 2 - dl ** 2 / lam + 2 * dl * (1 - lam) * y
DISABLED = ((1 - lam) * x ** 2 - lam * (1 - lam) * y ** 2 + dl ** 2 + dl ** 2 / lam + 0 * x
            - 2 * dl * (1 - lam) * y - 2 * dl ** 2 * 0)


def item1_symbolic():
    SECTION[0] = 'item1-symbolic'
    check('Lemma 2.1 identity for general s', LHS == RHS)
    check('Lemma 2.1 has no x*y cross term (separable for every s)', LHS.coeff('x', 1).coeff('y', 1).iszero())
    sub_b = RHS.subs('s', -dl / lam)
    check('s=-dl/lam: RHS.subs == (1-lam)x^2-lam(1-lam)y^2+dl^2-dl^2/lam+2dl(1-lam)y', sub_b == CORRECT)
    check('s=-dl/lam: LHS.subs == same bracket', LHS.subs('s', -dl / lam) == CORRECT)
    diff = CORRECT - DISABLED
    check('disabled bracket differs from the correct one', not diff.iszero(), repr(diff))
    check('correct - disabled == -2 dl^2/lam + 4 dl (1-lam) y', diff == -2 * dl ** 2 / lam + 4 * dl * (1 - lam) * y)
    cc, cd = CORRECT.coeff('x', 0).coeff('y', 0), DISABLED.coeff('x', 0).coeff('y', 0)
    lc, ld = CORRECT.coeff('x', 0).coeff('y', 1), DISABLED.coeff('x', 0).coeff('y', 1)
    check('sign error 1, constant: correct dl^2-dl^2/lam, disabled dl^2+dl^2/lam',
          cc == dl ** 2 - dl ** 2 / lam and cd == dl ** 2 + dl ** 2 / lam)
    check('constant at lam=1/rho, rho=1+th equals -th dl^2', cc.subs('lam', rho.inv()).subs('rho', 1 + th) == -th * dl ** 2)
    check('sign error 2, y-linear: correct +2dl(1-lam), disabled -2dl(1-lam)',
          lc == 2 * dl * (1 - lam) and ld == -2 * dl * (1 - lam))
    check('x-linear and all quadratic parts agree (only the two terms above differ)',
          CORRECT.coeff('x', 1) == DISABLED.coeff('x', 1) and CORRECT.coeff('x', 2) == DISABLED.coeff('x', 2)
          and CORRECT.coeff('x', 0).coeff('y', 2) == DISABLED.coeff('x', 0).coeff('y', 2)
          and CORRECT.coeff('x', 1).iszero())
    resid = (-b0) * sub_b - (-b0) * DISABLED
    check('line-23 residual sub-(-b0)D == 2 b0 dl^2/lam - 4 b0 dl (1-lam) y (non-zero: fails without `or True`)',
          resid == 2 * b0 * dl ** 2 / lam - 4 * b0 * dl * (1 - lam) * y and not resid.iszero())
    sub = (-b0) * sub_b
    lin_x, lin_y = sub.coeff('x', 1).coeff('y', 0), sub.coeff('y', 1).coeff('x', 0)
    check('live line 25: d/dx sub at 0 == 0', lin_x.iszero())
    check('live line 25: d/dy sub at 0 == (-b0)(-2lam(dl-dl/lam)) == -2 b0 dl (1-lam)',
          lin_y == (-b0) * (-2 * lam * (dl - dl / lam)) and lin_y == -2 * b0 * dl * (1 - lam))
    check('line 25 confirms the correct y-sign, contradicts the disabled one', lin_y == (-b0) * lc and not lin_y == (-b0) * ld)
    # shrunk shift s = -dl(1-th), lam = 1/(1+th): Laurent in rho with th = rho-1 (check_gaugefree.py:44-46)
    shr = RHS.subs('s', -dl * (1 - th)).subs('lam', rho.inv()).subs('th', rho - 1)
    cx, cy = shr.coeff('x', 1).coeff('y', 0), shr.coeff('y', 1).coeff('x', 0)
    check('shrunk shift x-linear == 4 dl th/(1+th)', cx * rho == 4 * dl * (rho - 1))
    check('shrunk shift y-linear == -2 dl th/(1+th)', cy * rho == -2 * dl * (rho - 1))
    check('shrunk shift: x-lin = 2(dl+lam s), y-lin = -2 lam th dl (note line 31 form)',
          cx == 2 * dl * (1 - rho.inv() * (1 - (rho - 1))) and cy == -2 * rho.inv() * (rho - 1) * dl)
    check('shrunk shift quadratic: x^2 coeff th/(1+th), y^2 coeff -th/(1+th)^2',
          shr.coeff('x', 2).coeff('y', 0) * rho == rho - 1 and shr.coeff('y', 2).coeff('x', 0) * rho * rho == -(rho - 1))
    # Lemma 2.2 (narrow, check_gaugefree.py:35) and the kernel completion that is only an OUT string (:36)
    bi, bj = be0 + th * ti, be0 + th * (ti + h)
    EN = ((1 + th) * h + bi) ** 2 - bj ** 2
    check('Lemma 2.2: (rho h+beta_i)^2-beta_{i+h}^2 == (1+2th)h^2 + 2 beta_i h', EN == (1 + 2 * th) * h ** 2 + 2 * bi * h)
    check('Lemma 2.2: -a EN == -a rho h^2 - 2 a be0 h + a th (ti^2 - tj^2)',
          (-a) * EN == -a * (1 + th) * h ** 2 - 2 * a * be0 * h + a * th * (ti ** 2 - (ti + h) ** 2))
    sN, gam = -be0 / rho, a * rho
    check('kernel completion: -a rho h^2 - 2a be0 h == a be0^2/rho - gamma (h-s)^2, s=-be0/rho',
          -a * rho * h ** 2 - 2 * a * be0 * h == a * be0 ** 2 / rho - gam * (h - sN) ** 2)
    check('normalisation: gamma s^2 - gamma (u-s)^2 == -gamma u^2 + 2 gamma s u',
          gam * s ** 2 - gam * (u - s) ** 2 == -gam * u ** 2 + 2 * gam * s * u)
    bI, bJ = th * i_ - c_, th * j_ - c_
    check('old-weights log ratio (check_gaugefree.py:40)',
          ((-a) * (Fr(1, 4) - bI ** 2) / th) - ((-a) * (Fr(1, 4) - bJ ** 2) / th) == a * (i_ - j_) * (bI + bJ))
    check('old weights = -a/(4th) + a th (i - c/th)^2 (OUT string :42)',
          (-a) * (Fr(1, 4) - bI ** 2) / th == -a / (4 * th) + a * th * (i_ - c_ / th) ** 2)


def item1_random():
    SECTION[0] = 'item1-random'
    rng = random.Random(RANDOM_SEED)

    def rq(lo, hi):
        den = rng.choice([1, 2, 3, 7, 10, 97, 1000, 65537, 10 ** 9 + 7])
        return Fr(rng.randint(int(lo * den), int(hi * den)), den)

    keys = ('general', 'correct', 'disabled_rejected', 'const_flip_rejected', 'lin_flip_rejected', 'shrunk', 'bounds',
            'lemma22', 'kernel')
    cnt = dict.fromkeys(keys, 0)
    for _ in range(NPTS):
        X, Y, D, Sv = rq(-50, 50), rq(-50, 50), rq(-Fr(1, 2), Fr(1, 2)), rq(-3, 3)
        T = rq(Fr(1, 10 ** 6), Fr(1, 2)) or Fr(1, 3)
        L = 1 / (1 + T)
        lhs = (X - L * Y + D) ** 2 - L * (X - Y - Sv) ** 2
        rhs = (1 - L) * X ** 2 - L * (1 - L) * Y ** 2 + D ** 2 - L * Sv ** 2 + 2 * (D + L * Sv) * X - 2 * L * (D + Sv) * Y
        cnt['general'] += lhs == rhs
        S1 = -D / L
        e1 = (X - L * Y + D) ** 2 - L * (X - Y - S1) ** 2
        q0 = (1 - L) * X ** 2 - L * (1 - L) * Y ** 2 + D ** 2
        corr = q0 - D ** 2 / L + 2 * D * (1 - L) * Y
        dis = q0 + D ** 2 / L - 2 * D * (1 - L) * Y          # mutation control 1: line 23 as written
        m_const = q0 + D ** 2 / L + 2 * D * (1 - L) * Y      # mutation control 2: constant sign only
        m_lin = q0 - D ** 2 / L - 2 * D * (1 - L) * Y        # mutation control 3: y-linear sign only
        cnt['correct'] += e1 == corr
        cnt['disabled_rejected'] += e1 != dis or D == 0
        cnt['const_flip_rejected'] += e1 != m_const or D == 0
        cnt['lin_flip_rejected'] += e1 != m_lin or D == 0 or Y == 0
        S2 = -D * (1 - T)

        def f(XX, YY):
            return (XX - L * YY + D) ** 2 - L * (XX - YY - S2) ** 2
        cxv, cyv = (f(1, 0) - f(-1, 0)) / 2, (f(0, 1) - f(0, -1)) / 2   # exact for quadratics
        cnt['shrunk'] += cxv == 4 * D * T / (1 + T) and cyv == -2 * D * T / (1 + T)
        ok = abs(cxv) <= 2 * T and abs(cyv) <= T and abs(S2) <= (1 - T) / 2 and 1 - 2 * abs(S2) >= T
        cnt['bounds'] += ok and (1 - L) <= T and L * (1 - L) <= T
        A, BE, TI, HH = rq(1, 60), rq(-Fr(1, 2), Fr(1, 2)), rq(-500, 500), rq(-40, 40)
        R = 1 + T
        l22 = (R * HH + BE + T * TI) ** 2 - (BE + T * (TI + HH)) ** 2
        cnt['lemma22'] += (l22 == (1 + 2 * T) * HH ** 2 + 2 * (BE + T * TI) * HH
                           and -A * l22 == -A * R * HH ** 2 - 2 * A * BE * HH + A * T * (TI ** 2 - (TI + HH) ** 2))
        sn = -BE / R
        cnt['kernel'] += (-A * R * HH ** 2 - 2 * A * BE * HH == A * BE ** 2 / R - A * R * (HH - sn) ** 2
                          and 1 - 2 * abs(sn) >= T / R >= T / 2)
    labels = {'general': 'general-s identity', 'correct': 'correct s=-dl/lam bracket',
              'disabled_rejected': 'mutation control 1 (disabled line-23 bracket) rejected',
              'const_flip_rejected': 'mutation control 2 (constant sign only) rejected',
              'lin_flip_rejected': 'mutation control 3 (y-linear sign only) rejected',
              'shrunk': 'shrunk-shift coefficients 4dl th/(1+th), -2dl th/(1+th)',
              'bounds': '|cx|<=2th, |cy|<=th, |s|<=(1-th)/2, 1-2|s|>=th, quadratic coeffs <= th',
              'lemma22': 'Lemma 2.2 identities', 'kernel': 'kernel completion and 1-2|s| >= th/rho >= th/2'}
    for k in keys:
        check('random (seed %d, %d points): %s' % (RANDOM_SEED, NPTS, labels[k]), cnt[k] == NPTS, '%d/%d' % (cnt[k], NPTS))
    T0 = Fr(1, 100)
    L0 = 1 / (1 + T0)
    check('s=-dl/lam at dl=1/2 has |s| = 1/2 + th/2 > 1/2 (why the note shrinks the shift)', abs(-Fr(1, 2) / L0) == Fr(1, 2) + T0 / 2)
    tot = 4 * Fr(1, 2) * T0 / (1 + T0) + 2 * Fr(1, 2) * T0 / (1 + T0)
    check('note line 31 "(total) <= 2 b0 th B" understates the summed range 3th/(1+th) (th=1/100)',
          tot == 3 * T0 / (1 + T0) and tot > 2 * T0, str(tot))
    check('...but each axis is <= 2 b0 th B and the Section-5 bound 4 b0 th B holds', tot <= 4 * T0
          and 4 * Fr(1, 2) * T0 / (1 + T0) <= 2 * T0)


# ================================================================ final point (same rebuild as verify.py)
_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
_UNOPS = (ast.UAdd, ast.USub)


def _parse(src):
    if not isinstance(src, str) or len(src) > 4000:
        raise ValueError('expression must be a short string')
    tree = ast.parse(src, mode='eval')
    for node in ast.walk(tree):
        if isinstance(node, (ast.Expression, ast.Load, ast.Name) + _BINOPS + _UNOPS):
            continue
        if isinstance(node, ast.BinOp) and isinstance(node.op, _BINOPS):
            continue
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, _UNOPS):
            continue
        if isinstance(node, ast.Constant) and type(node.value) is int:
            continue
        raise ValueError('%s not allowed in %r' % (type(node).__name__, src))
    return tree


def _ev(node, env, vocab):
    if isinstance(node, ast.Expression):
        return _ev(node.body, env, vocab)
    if isinstance(node, ast.Constant):
        return Fr(node.value)
    if isinstance(node, ast.Name):
        if node.id not in vocab or node.id not in env:
            raise ValueError('unknown/undefined name %s' % node.id)
        return env[node.id]
    if isinstance(node, ast.UnaryOp):
        v = _ev(node.operand, env, vocab)
        return -v if isinstance(node.op, ast.USub) else v
    l, r = _ev(node.left, env, vocab), _ev(node.right, env, vocab)
    if isinstance(node.op, ast.Add):
        return l + r
    if isinstance(node.op, ast.Sub):
        return l - r
    if isinstance(node.op, ast.Mult):
        return l * r
    if isinstance(node.op, ast.Div):
        if r == 0:
            raise ValueError('division by zero')
        return l / r
    if r.denominator != 1 or abs(r.numerator) > 100000 or (l == 0 and r < 0):
        raise ValueError('bad power')
    return l ** int(r)


def seval(src, env, vocab):
    return Fr(_ev(_parse(src), env, vocab))


def exact_literal(sv):
    body = sv[1:] if sv[:1] == '-' else sv
    num, _, den = body.partition('/')
    ip, _, fp = num.partition('.')
    if not (ip.isdigit() and (fp == '' or fp.isdigit()) and (den == '' or den.isdigit())):
        raise ValueError('bad exact literal %r' % sv[:40])
    return Fr(sv)


def build_point(pt, vocab):
    env = {}
    for name, val in pt['definitions']:
        if name not in vocab or name in env:
            raise ValueError('bad/duplicate definition %s' % name)
        if isinstance(val, str):
            env[name] = seval(val, env, vocab)
        elif isinstance(val, dict) and set(val) == {'exact'}:
            env[name] = exact_literal(val['exact'])
        elif isinstance(val, dict) and set(val) == {'floor_grid', 'grid', 'minus'}:
            g = seval(val['grid'], env, vocab)
            if g.denominator != 1 or g <= 0:
                raise ValueError('grid must be a positive integer')
            xv = seval(val['floor_grid'], env, vocab)
            env[name] = Fr((xv * g).__floor__(), g.numerator) - seval(val['minus'], env, vocab)
        else:
            raise ValueError('bad definition form for %s' % name)
    return env


def frac_sha(v):
    return hashlib.sha256(str(Fr(v)).encode()).hexdigest()


R0_EXP = 30010


def show(v):
    """Display: integer part plus an exact offset in units of 1e-30010, else 4 correctly rounded significant digits."""
    unit = Fr(1, 10 ** R0_EXP)
    n = round(v)
    off = (v - n) / unit
    if off.denominator == 1 and abs(off) < 10 ** 6:
        o = int(off)
        if n == 0:
            return '%de-%d' % (o, R0_EXP) if o else '0'
        return '%d%s' % (n, ('%+de-%d' % (o, R0_EXP)) if o else '')
    with localcontext() as cx:       # correctly rounded (half-even) to 4 significant digits from the exact value
        cx.prec = 4
        return str(+(Decimal(v.numerator) / Decimal(v.denominator)))


# Item 2 records. group: superseded | active | false-option. cond: exact condition (> 0 means it holds).
# ledger: (strict-check row, formula transcribed from outer/check_ledger.py ledger()).
# control: (control flag, control row, formula from check_ledger.py) -- must be <= 0.
HITS = [
    dict(id='U1', group='superseded', what='old union row: g-fold scan of U, g^2 per window',
         cond='1-(eps+beta+1/2-xi)-kappa', holds=False, show='-0.5937', exact='-19/32+7*r+(eps*q-kappa)',
         control=('old_g_factor_union_row', 'old_g_factor_union_row_above_kappa', '(1-eps-beta-1/2+xi)-kappa')),
    dict(id='U2', group='superseded', what='g|F| <= g^2 tag work charged to one record', cond='1-2*beta', holds=False,
         show='-1+12e-30010', exact='-1+12*r',
         control=('old_union_tag_2beta', 'old_union_tag_2beta', '1-2*beta')),
    dict(id='U3', group='active', what='tag O(g) per visit; header O(g log L)', cond='1-beta', holds=True, show='6e-30010',
         exact='6*r', ledger=[('union_tag_work_per_visit_fits_record', '1-beta'), ('union_header_fits_record', '1-beta')]),
    dict(id='U4', group='active', what='new union row', cond='xi+1/2-eps-kappa', holds=True, show='0.4063', exact='13/32+r+(eps*q-kappa)',
         ledger=[('sparse_union_movement_above_kappa', '(xi+1/2-eps)-kappa')]),
    dict(id='U5', group='active', what='membership g h^2 per record', cond='1-beta-2*(1-eps)', holds=True, show='2e-30010', exact='2*r',
         ledger=[('membership_arithmetic_fits_record', '1-beta-2*(1-eps)')]),
    dict(id='U6', group='active', what='group key g h', cond='1-(beta+1-eps)', holds=True, show='4e-30010', exact='4*r',
         ledger=[('group_key_fits_record', '1-(beta+1-eps)')]),
    dict(id='U7', group='superseded', what='full-key sort surcharge (not used)', cond='(xi+1/2-eps)-(beta+1-eps)-kappa',
         holds=False, show='-0.5937', exact='-19/32+5*r+(eps*q-kappa)',
         control=('full_key_sort', 'unnecessary_full_key_sort_above_kappa', '((xi+1/2-eps)-(beta+1-eps))-kappa')),
    dict(id='U8a', group='false-option', what='HALO option K0^2 = g^2 h^2 = O(B)', cond='1-2*(beta+1-eps)', holds=False,
         show='-1+8e-30010', exact='-1+8*r'),
    dict(id='U8b', group='active', what='halo metadata K0^2 within the p^2 face allowance', cond='2-2*(beta+1-eps)',
         holds=True, show='8e-30010', exact='8*r', ledger=[('group_below_dimension', '(eps-beta)')], ledger_scale=2),
    dict(id='U8c', group='active', what='halo metadata term (HALO-THEOREM:44 branch)',
         cond='1-kappa-((eps-beta)+(beta+halo-core)+2*(beta+1-eps)-1)', holds=True, show='79.00', exact='79+10*r-kappa'),
    dict(id='U9', group='active', what='g sequential passes on halo copies', cond='1-(eps+beta+halo-core+2)-kappa',
         holds=True, show='77.00', exact='77+8*r-kappa',
         ledger=[('microbox_face_corrections_above_kappa', '(1-(eps+beta+halo-core+2))-kappa')]),
    dict(id='U10', group='active', what='support router O(g polylog p)', cond='1-beta', holds=True, show='6e-30010', exact='6*r',
         ledger=[('support_router_span', '1-beta')]),
    dict(id='U11', group='superseded', what='g a d precision bits', cond='1-(beta+eps)', holds=False, show='-1+8e-30010', exact='-1+8*r',
         control=('full_cell_gauge', 'unrecentered_group_gauge', '1-TH-r-beta')),
    dict(id='U12', group='superseded', what='linear gauge g a B', cond='1-xi-r-beta', holds=False, show='-0.9079',
         control=('old_linear_guard', 'old_linear_guard', '1-xi-r-beta')),
    dict(id='U13', group='superseded', what='GAUGEFREE bold guard beta+2xi-eps <= 1-r-zeta',
         cond='1-(2*xi-eps)-r-zeta-beta', holds=False, show='-0.8159',
         control=('old_theta_chirp_guard', 'old_theta_chirp_guard', '1-(2*xi-eps)-r-beta')),
    dict(id='U14', group='active', what='fine chirp g a theta B^2 (ledger form)', cond='1-(2*xi-TH)-r-beta', holds=True,
         show='0.1841', ledger=[('group_gauge_power_slack', '1-(2*xi-TH)-r-beta')]),
    dict(id='U14b', group='active', what='fine chirp guard with zeta (GAUGEFREE:95 form)', cond='1-(2*xi-TH)-r-zeta-beta',
         holds=True, show='0.1841'),
    dict(id='U15', group='active', what='linear leftover dominated by chirp (xi > 0)', cond='xi-1/2', holds=True,
         show='0.4079', ledger=[('cap_above_band', 'xi-1/2')]),
]


def item2(points_path):
    SECTION[0] = 'item2-final-point'
    PTS = json.loads(Path(points_path).read_text())
    vocab = set(PTS['vocabulary'])
    fin = PTS['points']['final']
    Pt = build_point(fin, vocab)
    fps = fin['fingerprints']
    bad = [n for n, hsh in fps.items() if frac_sha(Pt[n]) != hsh]
    check('final point rebuilt from POINTS.json: %d SHA-256 fingerprints match' % len(fps), not bad and len(fps) >= 11,
          'mismatch: %s' % bad if bad else '')
    r = Fr(1, 10 ** R0_EXP)
    check('eps = 1-2e-30010, beta = 1-6e-30010, r0 = 1e-30010, zeta = 1e-30012',
          Pt['eps'] == 1 - 2 * r and Pt['beta'] == 1 - 6 * r and Pt['r'] == r and Pt['zeta'] == r / 100)
    check('xi = eps(1+q) - 3/32 + r0 (Strassen c = 3/32), theta power 2, halo 48, core 128',
          Pt['xi'] == Pt['eps'] * (1 + Pt['q']) - Fr(3, 32) + r and Pt['c'] == Fr(3, 32)
          and (Pt['TH'], Pt['halo'], Pt['core']) == (2, 48, 128))
    vals = {}
    for H in HITS:
        v = seval(H['cond'], Pt, vocab)
        vals[H['id']] = v
        check('%s %s: %s %s at the final point (= %s)' % (H['id'], H['what'], H['cond'], '> 0' if H['holds'] else '<= 0', show(v)),
              (v > 0) == H['holds'] and show(v) == H['show'], 'value %s, expected display %s' % (show(v), H['show']))
        if 'exact' in H:
            check('%s: exact closed form %s' % (H['id'], H['exact']), seval(H['exact'], Pt, vocab) == v)
        for row, form in H.get('ledger', ()):
            lv = seval(form, Pt, vocab)
            check('%s: ledger row %s (%s) agrees with the sweep condition and is > 0' % (H['id'], row, form),
                  lv * H.get('ledger_scale', 1) == v and lv > 0)
        if 'control' in H:
            flag, row, form = H['control']
            cv = seval(form, Pt, vocab)
            check('%s: rejecting control %s.%s (%s) is <= 0' % (H['id'], flag, row, form), cv <= 0, show(cv))
    groups = {g: [H['id'] for H in HITS if H['group'] == g] for g in ('superseded', 'active', 'false-option')}
    check('every active record holds and every superseded/false-option record fails',
          all(vals[i] > 0 for i in groups['active']) and all(vals[i] <= 0 for i in groups['superseded'] + groups['false-option']))
    check('every superseded record has a rejecting control', all('control' in H for H in HITS if H['group'] == 'superseded'))
    return Pt, vocab


# ================================================================ --source-root
EXTRA_PINS = {  # files not in SOURCES-T74.json; from `git show pr/2044:research/capped-fusion-t74-k554/<path>`
    'outer/run_outer.py': ('cb46c44c70d05597bda3375517ed4f5a3f93294d30aff356c5ad5fe6d03b5aeb',
                           '8a9434e5b5d877c0b26976b379180cf5d9508d7e'),
    'outer/struct_check.py': ('f13c6a166394549a25b6e727c4a43c0a34ae270c9498a9697683d63e0e5f9971',
                              'a541e93ae70acfa62998cfb833ef35d0a5900a41'),
    'verify_release.py': ('bd8e9373edfe1062e7d6e8c2dc962fd4b5a4d05272f283ed85be3401a8d9463c',
                          '65b4cdef75eb3f713e58b7081f25b630492e22f3'),
}
CG_LINES = {  # outer/check_gaugefree.py at #2044 head, exact text
    20: 'claim=-b0*((1-lam)*x**2-lam*(1-lam)*y**2+dl**2-lam*s**2+2*(dl+lam*s)*x-2*lam*(dl+s)*y)',
    21: 'assert sp.simplify(res-claim)==0',
    22: 'sub=sp.expand(claim.subs(s,-dl/lam))',
    23: 'assert sp.simplify(sub-(-b0)*((1-lam)*x**2-lam*(1-lam)*y**2+dl**2+dl**2/lam+0*x-2*dl*(1-lam)*y- 2*dl**2*0))==0 or True',
    24: 'lin_x=sp.simplify(sp.diff(sub,x).subs({x:0,y:0})); lin_y=sp.simplify(sp.diff(sub,y).subs({x:0,y:0}))',
    25: 'assert sp.simplify(lin_x)==0 and sp.simplify(lin_y-(-b0)*(-2*lam*(dl-dl/lam)))==0',
    35: 'assert sp.simplify(sp.expand(EN-EKer-EChirp))==0',
    40: 'assert sp.simplify((-a*(sp.Rational(1,4)-b_i**2)/th)-(-a*(sp.Rational(1,4)-b_j**2)/th)-a*(i_-j_)*(b_i+b_j))==0',
    44: 'shr=sp.expand(claim.subs(s,-dl*(1-th)).subs(lam,1/(1+th)))',
    45: 'cx=sp.simplify(sp.diff(shr,x).subs({x:0,y:0})/(-b0)); cy=sp.simplify(sp.diff(shr,y).subs({x:0,y:0})/(-b0))',
    46: 'assert sp.simplify(cx-2*dl*2*th/(1+th))==0 and sp.simplify(cy-(-2*dl*th/(1+th)))==0',
    53: '    B0=rnd(Fr(1,50),2); L=1/(1+rnd(Fr(1,200),Fr(1,10))); D=rnd(-Fr(1,2),Fr(1,2)); S=-D/L',
}
RUN_OUTER_19 = "subprocess.run([sys.executable, '-B', str(P / 'outer/check_gaugefree.py')], check=True, stdout=subprocess.DEVNULL)"
STRUCT_130 = ('                assert all(x == 0 for r in S[(p, q)] for x in r) or True   # far blocks are tiny/zero or '
              'ignored by the tridiagonal solve below (checked via full solve)')

VP = 'vendor/pr1673/capped-phase-fusion/'
PLA, CS, CI, OA, MLS, HT = (VP + n for n in ('PHASE-LAYOUT-AUDIT.md', 'CAPPED-SIGNOFF.md', 'CAPPED-INTERIORS.md',
                                             'OUTER-AUDIT.md', 'MATRIX-LAYOUT-SIGNOFF.md', 'HALO-THEOREM.md'))
US, GF, RB, FPC = 'outer/UNION-SCHEDULE.md', 'outer/GAUGEFREE-INTERIORS.md', 'outer/RECT-BOUNDARY.md', 'outer/FINE-PADDING-COMPOSITION.md'
FPP, CL = 'vendor/pr1786/FINE-PRIME-PADDING.md', 'outer/check_ledger.py'
# (tag, file, lines, anchor): the anchor must occur within +-2 lines of the cited line (range).
CITES = [
    ('I1', GF, '30', '600 exact rational mixed-difference checks'),
    ('I1', GF, '31', 'Choose **s = -delta (1-theta)**'),
    ('I1', GF, '31', 'logarithmic range <= 2 b0 theta B (total)'),
    ('I1', GF, '32', '(With s = -delta/lambda the linear terms vanish in x and are 2 b0 delta (1-lambda) in y'),
    ('I1', GF, '37', '**gamma = a rho, s = -beta0/rho**'),
    ('I1', GF, '84', "the linear leftover is <= 2 b0 theta B'"),
    ('I1', GF, '92', '4 b0 theta B (linear leftover)'),
    ('I1', 'outer/check_gaugefree.py', '36', 'exp(a be0^2/rho) exp(-gamma (h-s)^2)'),
    ('I1', 'outer/check_gaugefree.py', '42', 'log w_i = const + a th (i - c/th)^2'),
    ('I1', FPC, '13', 'the unproved stability claim of STRUCTURED-BOUNDARY.md is dispensable'),
    ('U1', PLA, '4', 'V g^2 W polylog(p)/d'), ('U1', PLA, '86', 'Scan U once'),
    ('U1', PLA, '103-108', 'O(V [g^2 mu + g mu polylog p])'), ('U1', PLA, '229', 'union movement:'),
    ('U1', CS, '30-31', 'per group: O(V g^2 W/B polylog p)'),
    ('U1', CI, '38', 'sparse union movement | `epsilon+beta+1/2-b`'),
    ('U1', CI, '41', 'For the sparse union, its fraction within a group'),
    ('U1', OA, '86', 'sparse union, basic movement'),
    ('U1', MLS, '19-21', 'epsilon + beta + 1/2 - xi < 1-kappa'), ('U1', MLS, '31-33', 'It scans U once per axis'),
    ('U1', US, '17-18', 'the g-fold scan of U is removed'), ('U1', US, '98', 'Old audit row: `eps + beta + 1/2 - xi`'),
    ('U1', US, '110', 'reinstating the old row `1 - eps - beta - 1/2 + xi`'),
    ('U1', US, '122', 'the old row 1-eps-beta-1/2+xi = -0.5921 fails'),
    ('U1', RB, '65', 'the old g-factor union row would be -0.341'),
    ('U1', FPC, '12', 'control `old_g_factor_union_row`'),
    ('U1', CL, '139', "margins['old_g_factor_union_row']=1-eps-beta-Q(1,2)+xi"),
    ('U2', GF, '17', 'union tag check 1-2 beta > 0'), ('U2', GF, '103-104', '`union_tag_work_fits_record` (1 - 2 beta)'),
    ('U2', GF, '110', 'o(p) because 2 beta < 1'), ('U2', US, '103', 'a record is visited at most |F| <= g times'),
    ('U2', US, '124', 'union tag work per visit 1-beta = 6e-30010'), ('U2', RB, '66', 'union tag work 1 - 2 beta = 0.158'),
    ('U2', FPC, '12', '2 beta < 1 fails (control `old_union_tag_2beta`)'),
    ('U2', FPP, '266', 'not the obsolete 2 beta<1'), ('U2', CL, '193', "checks['old_union_tag_2beta']=1-2*beta"),
    ('U2', CL, '220', "('old_union_tag_2beta',{'old_tag':True})"), ('U2', 'verify_release.py', '112', 'the old 2*beta tag test'),
    ('U3', US, '11', 'a header of O(g log L) bits'), ('U3', US, '46-47', 'tag work per visit is O(g) bit operations'),
    ('U3', US, '58', 'O(g log L) bits per comparison'), ('U3', US, '103', 'tag work is at most O(g) per visit'),
    ('U3', GF, '110', 'is per visit'), ('U3', FPP, '264-266', 'O(g log L)-bit headers are absorbed'),
    ('U3', PLA, '119-120', 'O(g log L) bits'),
    ('U4', US, '94-98', 'no factor g^2 and no per-axis scan of U'),
    ('U5', PLA, '123-130', '`O(g h^2 polylog p)` per record'),
    ('U5', PLA, '177', 'The g membership tests cost O(g h^2 polylog p)=o(p) per p-bit record.'),
    ('U5', CS, '44-47', 'is O(g h^2 polylog p), h=Theta(p/d)'),
    ('U5', CI, '64', 'per-record phase metadata exponent `beta+2(1-epsilon)`'), ('U5', MLS, '20', 'beta + 2(1-epsilon) < 1'),
    ('U6', CS, '48', 'coordinate headers use O(g log p) bits'), ('U6', OA, '62', 'group-key length `K=O(g p/d)`'),
    ('U6', OA, '76', '`h_K=beta+1-epsilon`'), ('U6', HT, '31', '`K0=O(g(h+b)+log g)=O(gh)`'),
    ('U6', HT, '150', 'These are K0=O(gh) bits.'),
    ('U7', CS, '49-50', 'sparse sort with O(gh)-bit keys remains below the target'),
    ('U7', OA, '87', 'sparse union, conservative key surcharge'),
    ('U7', CI, '43', 'full active-group key surcharge adds only `beta+1-epsilon`'),
    ('U7', CI, '64', 'optional full-key surcharge leaves it below 0.781'),
    ('U7', MLS, '34-35', 'correctly rejected in the new ledger'),
    ('U8a', HT, '31-32', 'Require `K0^2=O(B)` or retain the explicit extra metadata term below.'),
    ('U8b', HT, '44', 'O((gL/N)V K0^2/B)'), ('U8b', HT, '150-157', 'O(K0^2) safe metadata work per copy'),
    ('U8b', CI, '43', 'Sparse core-face corrections'),
    ('U9', OA, '58-62', '`O(V (g A/L) g [1+w^2/d] polylog p)` per group'), ('U9', OA, '89', '`epsilon+beta+3-8+2`'),
    ('U9', PLA, '213-219', 'g sequential such passes on this sparse volume'),
    ('U9', HT, '185-186', 'Summing over rectangles costs `O(M g polylog p)`'),
    ('U9', CS, '63-65', 'O(g p^-5), now about p^-4.9064'), ('U9', FPP, '230-233', '`epsilon+beta+48-128+2`'),
    ('U9', CL, '137', "'microbox_face_corrections':1-(eps+beta+halo_power-core_power+2)"),
    ('U10', CS, '52-57', 'router uses O(g polylog p) moved/control bits'),
    ('U10', CI, '66', 'even though gK is larger than one axis width'),
    ('U10', VP + 'SUPPLIER-SUPPORT-AUDIT.md', '121', 'gK=O(p^beta log p) bit positions'),
    ('U10', VP + 'SUPPORT-ADVERSARIAL-AUDIT.md', '189-200', 'k=O(gK)=O(p^.093 log p)'),
    ('U10', VP + 'SUPPORT-ADVERSARIAL-AUDIT.md', '227', 'gG/ell_axis=Theta(p^.091 log p)'),
    ('U10', US, '123', 'support router span 1-beta = 6e-30010 > 0'),
    ('U11', VP + 'TENSOR-COMPILER.md', '25-27', 'g a d+g polylog(p)=O(p)'),
    ('U11', VP + 'LOG-A-PHASE-SCHUR-AUDIT.md', '112', 'exp(O(g*a*d))'),
    ('U11', VP + 'SUPPLIER-SUPPORT-AUDIT.md', '109', 'O(g) extra magnitude and error allowance'),
    ('U11', VP + 'CAPPED-GAUGE-AUDIT.md', '67', '**ad cost occurs in offline coefficient accuracy**'),
    ('U11', VP + 'CAPPED-GAUGE-AUDIT.md', '107', 'no remaining full-cell term g*a*d may be charged'),
    ('U11', CL, '190', "checks['unrecentered_group_gauge']=1-THETA_POWER-r-beta"),
    ('U12', VP + 'CAPPED-GAUGE-AUDIT.md', '99-107', '`O(g a Bcap + g polylog p)`'),
    ('U12', CI, '68', '`1-b-r-beta=zeta>0`'), ('U12', GF, '17', 'ledger guard beta + xi <= 1-r-zeta'),
    ('U13', GF, '17', 'guard beta + 2 xi - eps <= 1-r-zeta'), ('U13', GF, '93-95', '**beta + 2 xi - eps <= 1 - r - zeta**'),
    ('U13', GF, '101', '**1 - (2 xi - eps) - r - beta**'),
    ('U13', FPC, '46', 'superseded by `beta + 2 xi - 2 < 1` at fine theta'),
    ('U14', GF, '1', 'the chirp range becomes O(a B^2/p^2)'), ('U14', GF, '41', 'e^{O(g (a theta B^2 + polylog))}'),
    ('U14', GF, '94', 'O(g a theta B^2)'), ('U14', FPP, '163-169', 'beta + 2 xi - 2 < 1'),
    ('U15', GF, '96', 'is dominated by the chirp (exponent beta + 2 xi - eps) since xi > 0'),
    ('U15', GF, '101', '`shift_leftover_linear_dominated_by_chirp`: xi > 0'),
    ('NX', US, '85', 'the total is O(p (log g + log L + 1) * sum_r |S_r|)'),
    ('NX', GF, '96', 'The offline accuracy term a d = o(p) is unchanged.'),
    ('NX', FPP, '159-187', 'Setup arithmetic at P_setup is separate from these records.'),
    ('NX', GF, '72', 'Identical to SHALLOW-TOEPLITZ sec. 4, 5, 6, 9'),
    ('NX', 'README.md', '16', 'SymPy 1.14.0 is only needed for the vendored PR1673 evidence checks'),
    ('NX', 'outer/check_gaugefree.py', '12', 'import sympy as sp, mpmath as mp, numpy as np'),
    ('STALE', 'outer/STRUCTURED-BOUNDARY.md', '97', 'beta = 0.99665, union tag work per visit 1 - beta = 0.00335'),
    ('STALE', CS, '75-78', 'membership descriptor power    =  .0966144543147439.'),
    ('STALE', PLA, '128-130', '`g=p^(1-epsilon-r-zeta)` and epsilon>2/3'),
    ('STALE', GF, '105', 'pkg8-era package, superseded by outer/FINE-PADDING-COMPOSITION.md'),
    ('STALE', GF, '117', '(pkg8-era, superseded by the fine-padding point beta = 1 - 6e-100)'),
]


def _to_poly(node):
    """ast of a sympy-free arithmetic expression over x,y,lam,dl,b0 (ints, + - * / **int) -> P."""
    if isinstance(node, ast.Name) and node.id in ('x', 'y', 'lam', 'dl', 'b0', 's'):
        return V[node.id]
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return P.lift(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_to_poly(node.operand)
    if isinstance(node, ast.BinOp):
        lt = _to_poly(node.left)
        if isinstance(node.op, ast.Pow):
            if not (isinstance(node.right, ast.Constant) and type(node.right.value) is int):
                raise ValueError('non-integer power')
            return lt ** node.right.value
        rt = _to_poly(node.right)
        op = type(node.op)
        if op is ast.Add:
            return lt + rt
        if op is ast.Sub:
            return lt - rt
        if op is ast.Mult:
            return lt * rt
        if op is ast.Div:
            return lt / rt
    raise ValueError('unsupported node %s' % type(node).__name__)


def _vacuous(node):
    t = node.test
    return (isinstance(t, ast.BoolOp) and isinstance(t.op, ast.Or)
            and any(isinstance(v, ast.Constant) and v.value is True for v in t.values))


def source_root(dirarg, Pt, vocab):
    SECTION[0] = 'source-root'
    d = Path(dirarg)
    root = d / PKG_REL if (d / PKG_REL / 'outer').is_dir() else d
    if not (root / 'outer' / 'check_gaugefree.py').is_file():
        check('--source-root contains %s' % PKG_REL, False, str(d))
        return
    SRC = json.loads((HERE / 'SOURCES-T74.json').read_text())
    check('SOURCES-T74.json pins PR #2044 head %s' % HEAD[:8], SRC.get('head_sha') == HEAD and SRC.get('package') == PKG_REL)
    pins = {k: (m['sha256'], m['git_blob']) for k, m in SRC['files'].items()}
    for k, v in EXTRA_PINS.items():
        pins.setdefault(k, v)
    used = sorted({c[1] for c in CITES} | {'outer/check_gaugefree.py', 'outer/run_outer.py', 'outer/struct_check.py',
                                            CL, 'outer/LEDGER.json'})
    text = {}
    nbad = []
    for rel in used:
        p = root / rel
        if rel not in pins or not p.is_file():
            nbad.append(rel + ' (unpinned or missing)')
            continue
        data = p.read_bytes()
        if (hashlib.sha256(data).hexdigest(), hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()) != pins[rel]:
            nbad.append(rel)
        if rel != 'outer/LEDGER.json':
            text[rel] = data.decode('utf-8').splitlines()
    check('%d used source files match their SHA-256 + git-blob pins (%d from SOURCES-T74.json, %d in-file)'
          % (len(used), len([r for r in used if r in SRC['files']]), len([r for r in used if r not in SRC['files']])),
          not nbad, '; '.join(nbad))
    cg = text.get('outer/check_gaugefree.py', [])
    wrong = [n for n, t in CG_LINES.items() if len(cg) < n or cg[n - 1] != t]
    check('check_gaugefree.py lines %s have the exact pinned text' % sorted(CG_LINES), not wrong, str(wrong))
    tree = ast.parse('\n'.join(cg))
    asserts = {nd.lineno: _vacuous(nd) for nd in ast.walk(tree) if isinstance(nd, ast.Assert)}
    check('check_gaugefree.py:23 is an assert whose test is `... or True` (vacuous)', asserts.get(23) is True)
    check('check_gaugefree.py:21,25,35,40,46 are live (non-vacuous) asserts', all(asserts.get(n) is False for n in (21, 25, 35, 40, 46)))
    try:
        a23 = next(nd for nd in ast.walk(tree) if isinstance(nd, ast.Assert) and nd.lineno == 23)
        call = a23.test.values[0].left                       # sp.simplify(sub - (-b0)*(BRACKET))
        br = _to_poly(call.args[0].right.right)
        claim = _to_poly(next(nd for nd in ast.walk(tree) if isinstance(nd, ast.Assign) and nd.lineno == 20).value)
        a25 = next(nd for nd in ast.walk(tree) if isinstance(nd, ast.Assert) and nd.lineno == 25)
        lin_y_expected = _to_poly(a25.test.values[1].left.args[0].right)
        ok_parse = True
    except (StopIteration, AttributeError, IndexError, ValueError) as e:
        ok_parse = False
        check('parse check_gaugefree.py lines 20/23/25 with ast', False, repr(e))
    if ok_parse:
        check('line 20 claim (parsed) == -b0 * Lemma 2.1 bracket', claim == -b0 * RHS)
        check('line 23 bracket (parsed) == DISABLED transcription and != certified bracket', br == DISABLED and not br == CORRECT)
        check('line 25 expected y-slope (parsed) == -b0 * (y-linear of certified bracket)',
              lin_y_expected == -b0 * CORRECT.coeff('x', 0).coeff('y', 1))
    vac = []
    for py in sorted((root / 'outer').glob('*.py')):
        try:
            tr = ast.parse(py.read_text(encoding='utf-8'))
        except SyntaxError:
            vac.append('outer/%s:unparsable' % py.name)
            continue
        vac += ['outer/%s:%d' % (py.name, nd.lineno) for nd in ast.walk(tr) if isinstance(nd, ast.Assert) and _vacuous(nd)]
    check('vacuous asserts in outer/*.py are exactly check_gaugefree.py:23 and struct_check.py:130',
          vac == ['outer/check_gaugefree.py:23', 'outer/struct_check.py:130'], str(vac))
    sc_l = text.get('outer/struct_check.py', [])
    check('struct_check.py:130 exact text (second vacuous `or True`)', len(sc_l) >= 130 and sc_l[129] == STRUCT_130)
    cl_tree = ast.parse('\n'.join(text.get(CL, [])))
    mods = set()
    for nd in ast.walk(cl_tree):
        if isinstance(nd, ast.Import):
            mods.update(al.name for al in nd.names)
        elif isinstance(nd, ast.ImportFrom):
            mods.add(nd.module)
    names = {nd.id for nd in ast.walk(cl_tree) if isinstance(nd, ast.Name)}
    strs = [nd.value for nd in ast.walk(cl_tree) if isinstance(nd, ast.Constant) and isinstance(nd.value, str)]
    lam_assign = [(nd.lineno, ast.dump(nd.value)) for nd in ast.walk(cl_tree) if isinstance(nd, ast.Assign)
                  and any(isinstance(tg, ast.Name) and tg.id == 'lam' for tg in nd.targets)]
    check('check_ledger.py imports only fractions/decimal/pathlib/math/hashlib/json/sys/gmpy2 (no sympy, subprocess, '
          'runpy, importlib)', mods == {'fractions', 'decimal', 'pathlib', 'math', 'hashlib', 'json', 'sys', 'gmpy2'}, str(mods))
    check('check_ledger.py never names check_gaugefree / GAUGEFREE-INTERIORS and never calls exec/eval/__import__',
          not any('check_gaugefree' in sv or 'GAUGEFREE' in sv for sv in strs)
          and not names & {'exec', 'eval', '__import__', 'compile', 'runpy', 'subprocess', 'importlib'})
    check('check_ledger.py has none of the identity symbols (dl, b0, claim, sub, sp, s=-dl/lam); its only `lam` is the '
          'supplier lambda = 1-(q_+a)/2 at line 126',
          not names & {'dl', 'b0', 'claim', 'sub', 'sp', 'sympy', 'shr', 'cx', 'cy'}
          and lam_assign == [(126, ast.dump(ast.parse('1-(q_+a)/2', mode='eval').body))], str(lam_assign))
    refs = []
    for py in sorted(root.rglob('*.py')):
        for n, line in enumerate(py.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
            if 'check_gaugefree' in line:
                refs.append('%s:%d' % (py.relative_to(root).as_posix(), n))
    check('only reference to check_gaugefree in any *.py is run_outer.py:19 (besides its own docstring)',
          refs == ['outer/check_gaugefree.py:5', 'outer/run_outer.py:19'], str(refs))
    ro = text.get('outer/run_outer.py', [])
    check('run_outer.py:19 only runs it as a pass/fail subprocess with stdout discarded',
          len(ro) >= 19 and ro[18] == RUN_OUTER_19)
    bad = []
    for tag, rel, spec, anchor in CITES:
        L = text.get(rel)
        for part in spec.split(','):
            lo, _, hi = part.partition('-')
            lo, hi = int(lo), int(hi or lo)
            if L is None or anchor not in '\n'.join(L[max(0, lo - 3):hi + 2]):
                bad.append('%s %s:%s' % (tag, rel, part))
    check('%d cited file:line anchors found within +-2 lines' % len(CITES), not bad, '; '.join(bad))
    LED = json.loads((root / 'outer' / 'LEDGER.json').read_bytes())
    row = LED['rows']['struct_boundary_radix_union']
    R = lambda nd: Fr(nd['rational'])  # noqa: E731
    stored = {'eps': row['epsilon'], 'beta': row['beta'], 'xi': row['xi'], 'r': row['r0'], 'zeta': row['zeta'],
              'kappa': row['kappa'], 'q': row['q']}
    check('LEDGER.json row struct_boundary_radix_union equals the rebuilt point (eps,beta,xi,r0,zeta,kappa,q)',
          all(R(v) == Pt[k] for k, v in stored.items()))
    sc = row['strict_checks']
    rc = LED['rejecting_controls']['struct_boundary_radix_union']
    for H in HITS:
        for name, form in H.get('ledger', ()):
            check('%s: LEDGER strict check %s == recomputed' % (H['id'], name),
                  name in sc and R(sc[name]) == seval(form, Pt, vocab))
        if 'control' in H:
            flag, name, form = H['control']
            check('%s: LEDGER rejecting control %s.%s == recomputed and <= 0' % (H['id'], flag, name),
                  name in rc.get(flag, {}) and R(rc[flag][name]) == seval(form, Pt, vocab) and R(rc[flag][name]) <= 0)
    absent = ('shift_leftover_linear_dominated_by_chirp', 'shift_gap_theta_polynomial')
    check('GAUGEFREE 6.1 row names %s are absent from LEDGER; cap_above_band, theta_positive_polynomial_power present' % (absent,),
          not any(n in sc for n in absent) and 'cap_above_band' in sc and 'theta_positive_polynomial_power' in sc)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--source-root', help='export containing %s at PR #2044 head' % PKG_REL)
    args = ap.parse_args()
    t0 = time.time()
    try:
        item1_symbolic()
        item1_random()
        Pt, vocab = item2(HERE / 'POINTS.json')
        if args.source_root:
            source_root(args.source_root, Pt, vocab)
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as e:
        check('unexpected error', False, '%s: %s' % (type(e).__name__, e))
    sections = []
    for sec, _, _, _ in RESULTS:
        if sec not in sections:
            sections.append(sec)
    for sec in sections:
        rs = [r for r in RESULTS if r[0] == sec]
        print('[%s] %d/%d checks pass' % (sec, sum(r[2] for r in rs), len(rs)))
        for _, name, ok, info in rs:
            if not ok:
                print('  FAIL: %s %s' % (name, ('(' + info + ')') if info else ''))
    fails = [r for r in RESULTS if not r[2]]
    mode = 'source-root' if args.source_root else 'default'
    groups = {g: sum(1 for H in HITS if H['group'] == g) for g in ('superseded', 'active', 'false-option')}
    if fails:
        print('FAIL_T74_REVIEW_ITEMS failed=%d checks=%d mode=%s' % (len(fails), len(RESULTS), mode))
        sys.exit(1)
    print('PASS_T74_REVIEW_ITEMS checks=%d mode=%s item1_random_points=%d seed=%d item2_records=%d '
          'active=%d superseded=%d false_option=%d cites=%s runtime=%.1fs'
          % (len(RESULTS), mode, NPTS, RANDOM_SEED, len(HITS), groups['active'], groups['superseded'],
             groups['false-option'], len(CITES) if args.source_root else 'skipped', time.time() - t0))


if __name__ == '__main__':
    main()
