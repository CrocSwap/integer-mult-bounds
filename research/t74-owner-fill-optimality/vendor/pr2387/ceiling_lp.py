#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Width-aware packing ceiling for whole-helper owner fills on the T74 template (certified LP dual).

Statement (for a fixed local word pair and the PR #2269 T74 template).  Let n_w be the number of live helpers
of width w per call, N_R the number of idle bins of rank R (T*112*#children of rank R: N_8 = 49728,
N_16 = N_32 = N_48 = 33152), and P_g, P_e the local paid profiles.  ANY legal whole-helper owner fill puts
each of the 666*400 roles whole into one bin; so for each bin the multiset of hosted widths is a pattern p
with sum(p) <= R, and the bin's idle remainder R - sum(p) is a child of the global profile (if nonzero).
For fixed a the moment mu(a) = sum_r n_r (r/73)^(1-a) / 66304 is linear in the counts, hence

    66304 * mu(a) >= sum_r (249 P_g + 417 P_e)_r h_a(r) + LP(a),
    LP(a) = min sum_p x_p h_a(R_p - sum p)  s.t.  sum_{p of rank R} x_p = N_R,  sum_p x_p cnt_w(p) = 666 n_w,
    x >= 0,    h_a(r) = (r/73)^(1-a), h_a(0) = 0,

the LP relaxation of the pattern counts of the fill (time windows, families and ports are dropped).  By weak
duality LP(a) >= sum_R N_R y_R + sum_w 666 n_w z_w for every (y, z) with y_R + sum_w cnt_w(p) z_w <= h_a(rem p)
for all patterns p.  A float simplex supplies (y, z); they are converted to exact rationals and repaired to
exact feasibility against certified LOWER bounds of h_a (800-bit directed rounding, vendored iteration-3
price_check.py).  If the resulting exact lower bound of 66304*mu(a0) exceeds 66304, then mu(a0) > 1 for every
legal fill, so every fill has b < a0 (mu is increasing in a).  This is a ceiling, not a construction.

Cases: ext80 = PR2339 80-alias words (widths re-derived by check_fill.py); high43 = PR2269 words (positive
control: PR2269's realized b must lie below its ceiling); high48 / low75 = the PR2339 README variants
"+5 high only" / "+32 low only" (profiles as reported in PR2339's README table; width inventories follow from
the alias definitions: a high alias removes a width-5 helper, a low alias removes a width-8 helper and turns a
width-4 lender into width 9).  Negative control: the ext80 certificate must FAIL at a0 below the b of our own
legal fill (OWNERS-80), otherwise the machinery would be unsound.

Prior and concurrent work.  The pattern-LP relaxation is not new: PR1129 (Ali Romman) and the R480 pattern-dual audit
use it on an older inventory, and PR2360 (Jeremy Diviney, head 16d4ea6c, opened while this package was in progress)
certifies b < 0.0016870 for the same PR2339 words with the same 1163 patterns (all-extra envelope).  This file was
written independently; it gives the tighter b < 0.0016867 (actual 249/417 dispatch), the variant and control cases,
and re-checks PR2360's DUAL.json (inputs/PR2360-DUAL.json, byte copy, blob/sha256 pinned) against its own pattern
enumeration and enclosures, with a tampered-dual negative control.

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.  Credits as in build_fill.py.
Usage: python3 -I -B ceiling_lp.py [--out]
"""

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from fractions import Fraction

if not __debug__:
    sys.exit('refusing to run under python -O')

HERE = os.path.dirname(os.path.abspath(__file__))
M, W_LIVE, CALLS = 73, 66304, 666
NB = {8: 49728, 16: 33152, 32: 33152, 48: 33152}
WID = (4, 5, 7, 8, 9)
CASES = {
    'ext80': dict(inv={4: 4, 5: 4, 7: 36, 8: 84, 9: 272},
                  pg={1: 2303, 2: 527, 3: 386, 4: 125, 5: 37, 8: 8}, pe={1: 2287, 2: 535, 3: 386, 4: 125, 5: 37, 8: 8}),
    'high43': dict(inv={4: 36, 5: 9, 7: 36, 8: 116, 9: 240},
                   pg={1: 2351, 2: 501, 3: 414, 4: 129, 5: 42, 8: 8}, pe={1: 2339, 2: 509, 3: 418, 4: 125, 5: 42, 8: 8}),
    'high48_5high_only': dict(inv={4: 36, 5: 4, 7: 36, 8: 116, 9: 240},
                              pg={1: 2351, 2: 501, 3: 414, 4: 129, 5: 37, 8: 8},
                              pe={1: 2339, 2: 509, 3: 418, 4: 125, 5: 37, 8: 8}),
    # positive control from PR2322's README (head 002304ef): widths {4:33,5:9,7:38,8:114,9:240}, 434 helpers,
    # profile {1:2335,2:512,3:426,4:120,5:38,8:8} in both providers (its own fill is on the same template ranks).
    'pr2322_control': dict(inv={4: 33, 5: 9, 7: 38, 8: 114, 9: 240},
                           pg={1: 2335, 2: 512, 3: 426, 4: 120, 5: 38, 8: 8},
                           pe={1: 2335, 2: 512, 3: 426, 4: 120, 5: 38, 8: 8}),
    'low75_32low_only': dict(inv={4: 4, 5: 9, 7: 36, 8: 84, 9: 272},
                             pg={1: 2303, 2: 527, 3: 386, 4: 125, 5: 42, 8: 8},
                             pe={1: 2287, 2: 535, 3: 386, 4: 125, 5: 42, 8: 8}),
}
CLAIM_2269 = Fraction('0.0016962471390584742207696225394800943861')
CLAIM_2322 = Fraction('0.001697060296258836')
VENDOR_PRICE = ('708753e7703077a8ce4311293f02e42afb801934',
                '19fcfb9f4d766959c599223090142edb03998229459cff1266960ca6b7ed1e0f')


def load_price():
    path = os.path.join(HERE, 'vendor', 'iter3', 'price_check.py')
    data = open(path, 'rb').read()
    assert hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == VENDOR_PRICE[0]
    assert hashlib.sha256(data).hexdigest() == VENDOR_PRICE[1]
    spec = importlib.util.spec_from_file_location('iter3_price_check', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P = load_price()


def patterns():
    out = []
    for R in NB:
        def rec(i, rem, cur):
            if i == len(WID):
                out.append((R, tuple(cur)))
                return
            for k in range(rem // WID[i] + 1):
                rec(i + 1, rem - k * WID[i], cur + [WID[i]] * k)
        rec(0, R, [])
    return out


COLS = patterns()


def h_float(r, a):
    return 0.0 if r == 0 else (r / M) ** (1.0 - a)


def h_lower(r, a):
    """Certified lower bound of (r/73)^(1-a) = (r/73) exp(a log(73/r)) (exact rational)."""
    if r == 0:
        return Fraction(0)
    a = Fraction(a)
    ll, lu = P.log_enclosure(M, r)
    el, eu = P.exp_enclosure((a.numerator * ll) // a.denominator, P.cdiv(a.numerator * lu, a.denominator))
    return Fraction(r * el, M * P.ONE)


def simplex(cost, rhs):
    """Dense two-phase simplex (floats).  Returns objective, primal {col: x} and duals (one per row)."""
    m, n = len(rhs), len(COLS)
    A = [[1.0 if R == RR else 0.0 for RR in NB] + [float(p.count(w)) for w in WID] for R, p in COLS]
    T = [[A[j][i] for j in range(n)] + [1.0 if k == i else 0.0 for k in range(m)] + [float(rhs[i])] for i in range(m)]
    basis = [n + i for i in range(m)]

    def pivot(r, c):
        pv = T[r][c]
        T[r] = [x / pv for x in T[r]]
        for i in range(m):
            if i != r and T[i][c] != 0.0:
                f = T[i][c]
                T[i] = [x - f * y for x, y in zip(T[i], T[r])]
        basis[r] = c

    def run(cv, allowed):
        for _ in range(10000):
            cb = [cv[basis[i]] for i in range(m)]
            best = None
            for j in allowed:
                rc = cv[j] - sum(cb[i] * T[i][j] for i in range(m))
                if rc < -1e-12 * (1 + abs(cv[j])) and (best is None or rc < best[0]):
                    best = (rc, j)
            if best is None:
                return
            j = best[1]
            rat = None
            for i in range(m):
                if T[i][j] > 1e-12:
                    q = T[i][-1] / T[i][j]
                    if rat is None or q < rat[0] - 1e-12:
                        rat = (q, i)
            assert rat is not None, 'unbounded'
            pivot(rat[1], j)
        raise RuntimeError('simplex iteration limit')

    run([0.0] * n + [1.0] * m, range(n + m))
    assert all(basis[i] < n or abs(T[i][-1]) < 1e-6 for i in range(m)), 'infeasible LP'
    cv = list(cost) + [1e12] * m
    run(cv, range(n))
    sol = {basis[i]: T[i][-1] for i in range(m) if basis[i] < n}
    duals = [sum(cv[basis[k]] * T[k][n + i] for k in range(m)) for i in range(m)]
    return sum(cost[j] * x for j, x in sol.items()), sol, duals


def rhs_of(case):
    inv = CASES[case]['inv']
    return [NB[R] for R in NB] + [CALLS * inv[w] for w in WID]


def local_counts(case):
    c = CASES[case]
    out = {}
    for r in set(c['pg']) | set(c['pe']):
        out[r] = 249 * c['pg'].get(r, 0) + 417 * c['pe'].get(r, 0)
    return out


def lp_mu_float(case, a):
    v, sol, duals = simplex([h_float(R - sum(p), a) for R, p in COLS], rhs_of(case))
    loc = sum(n * h_float(r, a) for r, n in local_counts(case).items())
    return (loc + v) / W_LIVE, sol, duals


def lp_root_float(case):
    lo, hi = 0.0015, 0.0018
    for _ in range(45):
        mid = (lo + hi) / 2
        if lp_mu_float(case, mid)[0] < 1:
            lo = mid
        else:
            hi = mid
    return lo, hi


def certify(case, a0):
    """Exact lower bound of 66304*mu(a0) valid for every legal fill; True if it exceeds 66304."""
    a0 = Fraction(a0)
    _mu, sol, duals = lp_mu_float(case, float(a0))
    y = {R: Fraction(duals[i]) for i, R in enumerate(NB)}
    z = {w: Fraction(duals[len(NB) + i]) for i, w in enumerate(WID)}
    L = {r: h_lower(r, a0) for r in range(0, 49)}
    worst = {R: Fraction(0) for R in NB}
    for R, p in COLS:
        slack = L[R - sum(p)] - y[R] - sum(z[w] for w in p)
        if slack < worst[R]:
            worst[R] = slack
    y = {R: y[R] + worst[R] for R in NB}            # exact dual feasibility
    for R, p in COLS:
        assert y[R] + sum(z[w] for w in p) <= L[R - sum(p)]
    rhs = rhs_of(case)
    dual_bound = sum(NB[R] * y[R] for R in NB) + sum(rhs[len(NB) + i] * z[w] for i, w in enumerate(WID))
    local_lower = sum(n * h_lower(r, a0) for r, n in local_counts(case).items())
    total = local_lower + dual_bound
    return total > W_LIVE, dict(a0=str(a0), dual_repair={str(R): float(worst[R]) for R in NB},
                                lower_bound_of_W_mu=float(total), W=W_LIVE, margin=float(total - W_LIVE),
                                certified_b_below_a0=total > W_LIVE)


PR2360_DUAL = ('inputs/PR2360-DUAL.json', '78c68d193cb0fe9d6ff6183596f34893602422f3',
               'b7fa099301a15fc063bab2250c6df6fc7d013cfabefabd47d3952544738559b5')


def check_pr2360_dual(tamper=None):
    """Independent re-check of PR2360's nine dual coefficients (head 16d4ea6c, Jeremy Diviney) with this file's
    pattern enumeration and 800-bit h enclosures.  PR2360 states z_R + sum_s n_s y_s <= f_b(r), f_b(r) =
    (73 h_b(r) - r)/b; in this file's normalisation that is the dual Y_R = (b z_R + R)/73, Z_s = (b y_s - s)/73.
    Returns the exact lower bound of 66304*mu(b) for (i) the actual 249 gauge44 / 417 extra dispatch and (ii)
    PR2360's all-extra envelope; raises AssertionError if any of the 1163 pattern inequalities fails."""
    path = os.path.join(HERE, PR2360_DUAL[0])
    data = open(path, 'rb').read()
    assert hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == PR2360_DUAL[1]
    assert hashlib.sha256(data).hexdigest() == PR2360_DUAL[2]
    d = json.loads(data)
    assert tuple(d['widths']) == WID and tuple(d['bin_ranks']) == tuple(NB)
    b = Fraction(d['threshold'])
    y = {s: Fraction(v) for s, v in zip(d['widths'], d['width_dual'])}
    z = {R: Fraction(v) for R, v in zip(d['bin_ranks'], d['bin_dual'])}
    if tamper:
        z[tamper[0]] += Fraction(tamper[1])
    Y = {R: (b * z[R] + R) / M for R in NB}
    Z = {s: (b * y[s] - s) / M for s in WID}
    L = {r: h_lower(r, b) for r in range(0, 49)}
    slack = {R: None for R in NB}
    for R, p in COLS:
        s_ = L[R - sum(p)] - Y[R] - sum(Z[s] for s in p)
        assert s_ >= 0, ('PR2360 dual infeasible', R, p)
        slack[R] = s_ if slack[R] is None else min(slack[R], s_)
    inv = CASES['ext80']['inv']
    dual_bound = sum(NB[R] * Y[R] for R in NB) + sum(CALLS * inv[s] * Z[s] for s in WID)
    actual = sum(n * h_lower(r, b) for r, n in local_counts('ext80').items()) + dual_bound
    envelope = CALLS * sum(n * h_lower(r, b) for r, n in CASES['ext80']['pe'].items()) + dual_bound
    assert envelope <= actual
    return dict(threshold=str(b), pins=dict(path=PR2360_DUAL[0], git_blob=PR2360_DUAL[1], sha256=PR2360_DUAL[2],
                                            pr2360_head='16d4ea6c26cd45ebb9301ab90f33a73615627f8d'),
                patterns_checked=len(COLS), lower_bound_of_W_mu_actual_dispatch=float(actual),
                lower_bound_of_W_mu_all_extra_envelope=float(envelope),
                certified_b_below_threshold=envelope > W_LIVE,
                min_slack_in_pr2360_units={str(R): float(M * slack[R] / b) for R in NB},
                _tamper_to_violate_48=M * slack[48] / b + Fraction(1, 10**12))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    for case, c in CASES.items():
        assert sum(r * n for r, n in c['pg'].items()) == sum(r * n for r, n in c['pe'].items()) == \
            1856 + sum(w * n for w, n in c['inv'].items()), case
    out = dict(model=__doc__.split('\n\n')[1], patterns=len(COLS), bins=NB, cases={})
    certs = {'ext80': '0.0016867', 'high43': '0.0016965', 'high48_5high_only': '0.0016965',
             'low75_32low_only': '0.0016867', 'pr2322_control': '0.0016973'}
    for case in CASES:
        lo, hi = lp_root_float(case)
        mu, sol, _d = lp_mu_float(case, lo)
        basis = sorted(([R, list(p), R - sum(p), round(x, 4)] for j, x in sol.items()
                        for (R, p) in [COLS[j]] if x > 1e-9), key=lambda z: (z[0], z[1]))
        ok, cert = certify(case, certs[case])
        assert ok, ('certificate failed', case, cert)
        out['cases'][case] = dict(inventory={str(k): v for k, v in CASES[case]['inv'].items()},
                                  lp_root_float=[lo, hi], lp_optimal_patterns=basis, certificate=cert)
        print('%-18s LP ceiling (float) b_LP = %.13f   certified: every legal fill has b < %s (margin %.3g)'
              % (case, lo, certs[case], cert['margin']))
    # controls
    hi43 = Fraction(certs['high43'])
    assert CLAIM_2269 < hi43, 'positive control: PR2269 realized b lies below its own certified ceiling'
    ok, cert = certify('high43', CLAIM_2269)
    assert not ok, 'control: PR2269 has a legal fill at its claimed b, the certificate must not reject it'
    out['controls'] = dict(pr2269_claim_below_high43_ceiling=True, high43_not_rejected_at_pr2269_claim=cert)
    assert CLAIM_2322 < Fraction(certs['pr2322_control']), 'positive control: PR2322 claim below its own ceiling'
    ok, cert = certify('pr2322_control', CLAIM_2322)
    assert not ok, 'control: PR2322 reports a legal fill at its claimed kappa; the certificate must not reject it'
    out['controls']['pr2322_not_rejected_at_its_claim'] = cert
    out['controls']['pr2322_fraction_of_its_ceiling'] = float(CLAIM_2322 / Fraction(out['cases']['pr2322_control']['lp_root_float'][1]))
    x2360 = check_pr2360_dual()
    assert x2360['certified_b_below_threshold'], ('PR2360 dual does not certify', x2360)
    dz = x2360.pop('_tamper_to_violate_48')
    try:
        check_pr2360_dual(tamper=(48, dz))
        raise RuntimeError('negative control: a tampered PR2360 dual (z_48 + min slack + 1e-12) was accepted')
    except AssertionError:
        pass
    x2360['tampered_z48_by_min_slack_plus_1e-12_rejected'] = True
    out['controls']['pr2360_dual_independent_recheck'] = x2360
    print('PR2360 DUAL.json (b < %s) re-checked independently: 1163/1163 pattern inequalities hold; '
          'lower bound of 66304*mu = %.6f (all-extra envelope) / %.6f (actual dispatch) > 66304'
          % (x2360['threshold'], x2360['lower_bound_of_W_mu_all_extra_envelope'],
             x2360['lower_bound_of_W_mu_actual_dispatch']))
    fill_b = None
    rec = os.path.join(HERE, 'check_fill.receipt.json')
    if os.path.exists(rec):
        fill_b = Fraction(json.load(open(rec))['price']['root_bracket'][0])
        ok, cert = certify('ext80', fill_b)
        assert not ok, 'negative control: OWNERS-80 is a legal fill with this b; certificate must fail here'
        out['controls']['ext80_not_rejected_at_owners80_b'] = cert
        out['owners80_b_floor'] = str(fill_b)
        out['owners80_fraction_of_ext80_ceiling'] = float(fill_b / Fraction(out['cases']['ext80']['lp_root_float'][1]))
    ext = Fraction(certs['ext80'])
    assert ext < CLAIM_2269 < CLAIM_2322
    out['conclusion'] = ('Every legal whole-helper owner fill of the PR2339 80-alias words on the PR2269 T74 template '
                         'has b < %s < PR2269 claim %s < PR2322 claim %s.' % (certs['ext80'], P.dec(CLAIM_2269, 40),
                                                                              P.dec(CLAIM_2322, 18)))
    out['credits'] = ('PR2339 (this author); PR2360 Jeremy Diviney (concurrent, independent certificate b < 0.0016870 for '
                      'the same words with the same 1163-pattern relaxation; its DUAL.json re-checked here); PR1129 Ali '
                      'Romman (R480 pattern-dual relaxation, the method); PR2269 Jeremy Kothe; PR2322 Vlado Vojdanovski; '
                      'PR2312/PR2302 jeremykothe2; PR2226 Cinna Davis; PR1319/PR1297 T74 lineage. Prepared with '
                      'substantial AI assistance (Claude Code, Anthropic); Apache-2.0.')
    if args.out:
        with open(os.path.join(HERE, 'ceiling_lp.receipt.json'), 'w') as h:
            h.write(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print(out['conclusion'])
    if fill_b is not None:
        print('OWNERS-80 realizes %.6f of the ext80 LP ceiling' % out['owners80_fraction_of_ext80_ceiling'])
    print('runtime %.1fs' % (time.time() - t0))
    print('PASS_T74_WIDTH_AWARE_CEILING')
    return 0


if __name__ == '__main__':
    sys.exit(main())
