#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certified moment-root brackets for the recounted 80-alias T74 global profile (native and conservative sides).

Object: the global rank profile of OWNERS-80.json.gz (this package) as recounted by fill_check80.py from the
literal roles and the PR #2339 80-alias words (commit bf1742ae) on PR #2269's T74 template (head b479fc55).
PROFILE-80.json and the build report are compared with the recount, never used as the priced input.

This file is an adaptation of our own iteration-3 price_check.py (research/t74-borrow43-independent-check/,
commit 4a2f20ea, Apache-2.0, same author).  The only imported code is our own fill_check80.py, loaded from this
directory by explicit file path (its sha256 is recorded).  No code of PR #2269 / #2322 / #2339 is imported or
run.  Pinned inputs are read with `git cat-file` and verified by git blob id and sha256.

Credits: PR2339 (this author); PR2269 Jeremy Kothe (b, complex_lower, conservative_complex_lower and the T74
assembly's moment / surcharge model); PR2322 Vlado Vojdanovski (native endpoint bracket and profile);
PR2312/PR2302 jeremykothe2; PR2226 Cinna Davis; PR1319/PR1297 T74 lineage (Rohan Arun et al.); the merged
complex-local-word-ceiling packing-cap model (Douglas Colkitt); the retained PR547/PR548/PR559 moment engines
and the icekylinx (Zhihao Chen) / eumemic exact-assembly lineage.
Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.

Usage:  python3 -I -B price80.py [--repo PATH] [--words-from-inputs] [--out]
The final stdout line starts with PASS_T74_80ALIAS_PRICE or FAIL_T74_80ALIAS_PRICE.

MODEL (stated precisely; also written to the receipt field "model").
 1. H = sum over the 666 dispatched calls of P_provider + idle = 249 P_gauge44 + 417 P_extra + idle, with
    P_provider recounted from the word by fill_check80 (frame-climb rule) and idle recounted by fill_check80
    from the 266,400 roles (rank minus occupied cells per (owner replica, child, port) bin).
 2. Moment (m = 73, W = 66304 live data families):
       mu(a) = sum_r n_r (r/m)^(1-a) / W = sum_r (n_r r) exp(a log(m/r)) / (m W).
    Native complex side (PR #2269 evidence/ASSEMBLY.json surcharge_model complex = false): no surcharge; this
    is the side of new/SPEC.json complex_lower and outer/B.json b, and of PR #2322's native endpoint.
    Conservative side (surcharge on, as the T74 assembly prices conservative_complex_lower):
       mu(a) + 32 m N m^a / (10^16 W),  N = sum_r n_r (number of children).
    Every rank satisfies 0 < r < m, so mu is strictly increasing in a; the root is the unique a > 0 with
    mu(a) = 1.  'accept a' = mu(a) < 1 certified; 'reject a' = mu(a) > 1 certified.
 3. Packing cap (merged complex-local-word-ceiling model, R = 48, as PR #2339 cap_ext.py): the fixed local
    profile 249 P_gauge44 + 417 P_extra plus ALL idle mass (m-1)W + 64*666 - local mass in fractional rank-48
    children; an upper bound on b for any hosting of these words on this template.
 4. Certified evaluation (exact integers on the grid 2^-800, directed rounding): log x = k log 2 + 2 atanh(z),
    atanh by its positive series plus the remainder bound z^(2N+1)/((2N+1)(1-z^2)); exp(x), 0 <= x < 1, by its
    Taylor series (lower: truncated sum; upper: + x^N/N! (N+1)/(N+1-x)).  Self-tests: log 2 by a second
    formula, log(m/r) against log m - log r, exp(log 2) encloses 2.
 5. Root brackets: bisection on the decimal grid 10^-40 from [0, 1/100] with certified decisions only
    (width 1e-40 <= 1e-30); no claimed value is used to locate a root.
"""

import sys

if sys.flags.optimize:
    sys.stdout.write('refusing to run under python -O\nFAIL_T74_80ALIAS_PRICE\n')
    sys.exit(2)

import argparse
import hashlib
import importlib.util
import json
import os
import time
from collections import Counter
from fractions import Fraction

PASS_LINE = 'PASS_T74_80ALIAS_PRICE'
FAIL_LINE = 'FAIL_T74_80ALIAS_PRICE'
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO = os.path.dirname(os.path.dirname(HERE))
RECEIPT_NAME = 'price80.receipt.json'
DIG = 40

PINS_2269_PRICE = {
    'outer/B.json': ('a66501df3178012477b4c54fb6888e986b52a25e', '631d89563be62a156c2b0119f9d4ba5a31cbf36380768bf8748825cf361bb525'),
    'new/SPEC.json': ('2431d1cebbb2e155356d2da160d60808498bc33d', 'bd091ed9e7f4939d06abb467d0d2c56ce0f34ba800d74132669f7b667e125d2d'),
    'new/PROFILE.json': ('3e103605dd46c8754028056eb9dde9a73b9bfdca', '50fcc0960a47f6d35064d3b55ea6dcb4cebbd305aec215c8034f626718595538'),
}
PINS_2322_PRICE = {
    'CLAIM.json': ('e10747182e8bdfa2fea1c8631bf738c15619eccb', '439ded151e7897b8e7d5ef9ad47f3cd8d1daf0b69219ef507a922519c7003530'),
    'evidence/EXACT-MOMENT.json': ('fdd26436f5b2a828a3e57908f886ab3bb578cfa1', 'c9a5bf7dbef056a8742200baaf329e41a98a49a7d7e32a5f1a181d6b0b31f776'),
}
# Claims under test, written here from the build report / PR texts (compared, never used as inputs).
CLAIMS = dict(
    b80_bracket=('0.0016865432362690642682667899981505185179', '0.0016865432362690642682667899981505185180'),
    b2269_prefix='0.0016962471390584742207696',
    kappa2322='0.001697060296258836',
    cap80_cap_ext='0.001747958371974',        # PR2339 README cap table (R = 48), ceiling() grid 1e-15
    cap43_cap_ext='0.001717935929',           # PR2339 cap_ext.py PASS line (PR2269 words, R = 48), 12 decimals
    local43={'gauge44': {1: 2351, 2: 501, 3: 414, 4: 129, 5: 42, 8: 8},
             'extra': {1: 2339, 2: 509, 3: 418, 4: 125, 5: 42, 8: 8}},
)


class Reject(Exception):
    def __init__(self, check, msg):
        Exception.__init__(self, '[%s] %s' % (check, msg))
        self.check = check
        self.msg = msg


def need(cond, check, msg):
    if not cond:
        raise Reject(check, msg)


def load_sibling(name):
    path = os.path.join(HERE, name + '.py')
    spec = importlib.util.spec_from_file_location('t74x80_' + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with open(path, 'rb') as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    return mod, digest


def plain(prof):
    return dict((str(r), prof[r]) for r in sorted(prof) if prof[r])


def int_profile(mapping, what):
    out = {}
    for k, v in mapping.items():
        need(type(v) is int and v > 0 and str(int(k)) == str(k), 'compose.profile', what + ': bad profile entry')
        out[int(k)] = v
    return out


def mass_of(prof):
    return sum(r * n for r, n in prof.items())


# ----------------------------------------------------------------------------
# Certified rational enclosures (verbatim from our iteration-3 price_check.py)
# ----------------------------------------------------------------------------

PREC = 800
ONE = 1 << PREC
MAX_TERMS = 4 * PREC


def cdiv(a, b):
    return -((-a) // b)


def atanh_enclosure(p, q, terms=None, tail=True):
    """Integers (lo, hi) with lo <= 2^PREC atanh(p/q) <= hi, for 0 <= p/q <= 1/3."""
    need(q > 0 and 0 <= 3 * p <= q, 'evaluator', 'atanh argument outside [0, 1/3]')
    if p == 0:
        return 0, 0
    p2, q2 = p * p, q * q
    pl, pu = (ONE * p) // q, cdiv(ONE * p, q)
    sl = su = 0
    j = 0
    while (pl > 0) if terms is None else (j < terms):
        need(j < MAX_TERMS, 'evaluator', 'atanh series did not terminate')
        sl += pl // (2 * j + 1)
        su += cdiv(pu, 2 * j + 1)
        pl = (pl * p2) // q2
        pu = cdiv(pu * p2, q2)
        j += 1
    if tail:
        su += cdiv(pu * q2, (2 * j + 1) * (q2 - p2))
    return sl, su


_LOG2 = []


def log2_enclosure():
    if not _LOG2:
        lo, hi = atanh_enclosure(1, 3)
        _LOG2.append((2 * lo, 2 * hi))
    return _LOG2[0]


def log_enclosure(p, q):
    """Integers (lo, hi) enclosing 2^PREC log(p/q) for p/q >= 1."""
    need(p >= q > 0, 'evaluator', 'log argument below 1')
    k = (p // q).bit_length() - 1
    a, b = p, q << k
    zl, zu = atanh_enclosure(a - b, a + b)
    l2l, l2u = log2_enclosure()
    return k * l2l + 2 * zl, k * l2u + 2 * zu


def exp_enclosure(xl, xu, terms=None, tail=True):
    """Integers (lo, hi) with lo <= 2^PREC exp(x) <= hi for every x in [xl, xu] / 2^PREC, 0 <= xl <= xu < 2^PREC."""
    need(0 <= xl <= xu < ONE, 'evaluator', 'exp argument outside [0, 1)')
    t = s = ONE
    j = 1
    while (t > 0) if terms is None else (j < terms):
        need(j < MAX_TERMS, 'evaluator', 'exp series did not terminate')
        t = ((t * xl) >> PREC) // j
        s += t
        j += 1
    lo = s
    t = s = ONE
    j = 1
    while True:
        need(j < MAX_TERMS, 'evaluator', 'exp series did not terminate')
        t = cdiv(cdiv(t * xu, ONE), j)
        if (t <= 1) if terms is None else (j >= terms):
            break
        s += t
        j += 1
    if tail:
        s += cdiv(t * (j + 1) * ONE, (j + 1) * ONE - xu)
    return lo, s


class Evaluator(object):
    """mu(a) enclosures from integer mass weights {rank: n_r * r} (fractional children allowed for the cap);
    `children` = N enables the conservative surcharge 32 m N m^a / (10^16 W)."""

    def __init__(self, weights, m, W, children=None):
        need(all(type(r) is int and 0 < r < m and type(x) is int and x > 0 for r, x in weights.items()),
             'moment', 'every child must have 0 < rank < m and a positive integer mass')
        self.weights = dict(weights)
        self.m, self.W, self.children = m, W, children
        self.logs = dict((r, log_enclosure(m, r)) for r in sorted(weights))
        self.logm = log_enclosure(m, 1)

    @classmethod
    def of_profile(cls, profile, m, W, surcharge=False):
        need(all(type(n) is int and n > 0 for n in profile.values()), 'moment', 'profile counts')
        return cls(dict((r, r * n) for r, n in profile.items()), m, W,
                   sum(profile.values()) if surcharge else None)

    def bounds(self, a):
        a = Fraction(a)
        need(a >= 0, 'moment', 'negative saving')
        an, ad = a.numerator, a.denominator
        slo = shi = 0
        for r in sorted(self.weights):
            ll, lu = self.logs[r]
            el, eu = exp_enclosure((an * ll) // ad, cdiv(an * lu, ad))
            slo += self.weights[r] * el
            shi += self.weights[r] * eu
        lo = Fraction(slo, self.m * self.W * ONE)
        hi = Fraction(shi, self.m * self.W * ONE)
        if self.children is not None:
            ll, lu = self.logm
            el, eu = exp_enclosure((an * ll) // ad, cdiv(an * lu, ad))
            c = 32 * self.m * self.children
            lo += Fraction(c * el, 10 ** 16 * self.W * ONE)
            hi += Fraction(c * eu, 10 ** 16 * self.W * ONE)
        need(lo <= hi, 'evaluator', 'empty enclosure')
        return lo, hi

    def side(self, a):
        lo, hi = self.bounds(a)
        if hi < 1:
            return -1
        if lo > 1:
            return 1
        return 0

    def root_bracket(self, digits=DIG):
        scale = 10 ** digits
        lo, hi = 0, scale // 100
        need(self.side(Fraction(lo, scale)) < 0, 'moment', 'mu(0) >= 1: no positive saving')
        need(self.side(Fraction(hi, scale)) > 0, 'moment', 'mu(1/100) <= 1')
        while hi - lo > 1:
            mid = (lo + hi) // 2
            s = self.side(Fraction(mid, scale))
            need(s != 0, 'moment.bracket', 'undecided grid point')
            if s < 0:
                lo = mid
            else:
                hi = mid
        return Fraction(lo, scale), Fraction(hi, scale)


def sci(x, sig=22, up=False):
    """x rounded to `sig` significant digits toward +inf (up) or -inf; display only."""
    x = Fraction(x)
    if x == 0:
        return '0'
    neg = x < 0
    ax = -x if neg else x
    e = len(str(ax.numerator)) - len(str(ax.denominator))
    while ax < Fraction(10) ** e:
        e -= 1
    while ax >= Fraction(10) ** (e + 1):
        e += 1
    y = ax * Fraction(10) ** (sig - 1 - e)
    larger = (up and not neg) or (neg and not up)
    k = cdiv(y.numerator, y.denominator) if larger else y.numerator // y.denominator
    ds = str(k)
    e += len(ds) - sig
    return '%s%s.%sE%+d' % ('-' if neg else '', ds[0], ds[1:sig], e)


def dec(x, digits=DIG):
    y = Fraction(x) * 10 ** digits
    need(y.denominator == 1, 'display', 'not on the decimal grid')
    n = y.numerator
    s = str(abs(n)).rjust(digits + 1, '0')
    return ('-' if n < 0 else '') + s[:-digits] + '.' + s[-digits:]


def interval(lo, hi, sig=22):
    return [sci(lo, sig, up=False), sci(hi, sig, up=True)]


def require_accept(ev, a, what):
    lo, hi = ev.bounds(a)
    need(hi < 1, 'moment.accept', '%s: mu - 1 in %s is not certified < 0' % (what, interval(lo - 1, hi - 1)))
    return lo, hi


def require_reject(ev, a, what):
    lo, hi = ev.bounds(a)
    need(lo > 1, 'moment.reject', '%s: mu - 1 in %s is not certified > 0' % (what, interval(lo - 1, hi - 1)))
    return lo, hi


def compose(local, counts, idle):
    H = Counter()
    for pid in sorted(counts):
        for r, n in local[pid].items():
            H[r] += counts[pid] * n
    for r, n in idle.items():
        H[r] += n
    return dict((r, H[r]) for r in sorted(H) if H[r])


def check_composition(H, sources):
    for name, prof in sources:
        need(H == prof, 'compose.profile', 'composed profile %s != %s %s' % (plain(H), name, plain(prof)))


def check_mass(H, m, W, T, calls):
    total = mass_of(H)
    need(W == 896 * T, 'compose.mass', 'W != 896 T')
    need(calls == 9 * T, 'compose.mass', 'calls != 9 T')
    need(m * W - total == 320 * T, 'compose.mass', 'deficit m W - mass != 320 T')
    need(total == (m - 1) * W + 64 * calls, 'compose.mass', 'mass != (m-1) W + 64 calls')
    need(m * m > 2 * max(H) ** 2, 'compose.mass', 'halving guard m^2 > 2 maxchild^2')
    return total


def cap_weights(local, counts, m, W, calls, R=48):
    """Packing cap weights: local mass per rank + all idle mass at rank R (fractional children)."""
    weights = Counter()
    for pid, n_calls in counts.items():
        for r, n in local[pid].items():
            weights[r] += n_calls * n * r
    idle_mass = (m - 1) * W + 64 * calls - sum(weights.values())
    need(idle_mass > 0 and 2 * R * R < m * m, 'cap', 'cap model')
    weights[R] += idle_mass
    return dict(weights), idle_mass


def expect_reject(name, target, fn, results):
    try:
        detail = fn()
    except Reject as e:
        ok = e.check == target
        results.append(dict(name=name, target=target, rejected_by=e.check, ok=ok, detail=e.msg[:240]))
        return ok
    results.append(dict(name=name, target=target, rejected_by=None, ok=False, detail=str(detail)[:240]))
    return False


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def run(args, receipt):
    F, f_sha = load_sibling('fill_check80')
    receipt['imported_own_modules'] = {'fill_check80.py': f_sha}
    try:
        R = F.recount(args.repo, args.words_from_inputs)
        b69, rec69 = F.read_pinned(args.repo, F.HEAD_2269, F.PKG_2269, PINS_2269_PRICE, 'PR2269')
        b22, rec22 = F.read_pinned(args.repo, F.HEAD_2322, F.PKG_2322, PINS_2322_PRICE, 'PR2322')
    except F.CheckFailure as e:
        raise Reject('fill', 'fill_check80 recount failed: ' + str(e))
    rec, ctx, words = R['recount'], R['ctx'], R['words']
    pins = dict(R['meta']['inputs'])
    pins.update(rec69)
    pins.update(rec22)
    receipt['pins'] = pins
    receipt['pr2339_files_read_from'] = R['meta']['pr2339_source']
    m, W, T, calls = F.M, rec['live'], ctx['T'], rec['calls']
    print('recount (fill_check80): roles=%d idle=%s' % (rec['roles'], rec['idle']), flush=True)

    # ---- 1. composition and mass identities
    local = dict((pid, dict(words[pid]['local'])) for pid in ('gauge44', 'extra'))
    counts = dict(rec['provider_counts'])
    need(counts == {'gauge44': 249, 'extra': 417}, 'dispatch', 'provider counts %r' % counts)
    idle = dict((int(r), n) for r, n in rec['idle'].items())
    H = compose(local, counts, idle)
    sources = [('fill_check80 recounted profile', int_profile(rec['profile'], 'recount')),
               ('build report (hard-coded in fill_check80)', dict(F.CLAIMS_80['profile']))]
    prof_path = os.path.join(HERE, 'PROFILE-80.json')
    if os.path.isfile(prof_path):
        with open(prof_path) as fh:
            sources.append(('PROFILE-80.json (claim)', int_profile(json.load(fh), 'PROFILE-80')))
    check_composition(H, sources)
    total = check_mass(H, m, W, T, calls)
    receipt['composition'] = dict(
        rule='H = %d P_gauge44 + %d P_extra + idle' % (counts['gauge44'], counts['extra']),
        local_profiles=dict((p, plain(local[p])) for p in sorted(local)), provider_counts=counts, idle=plain(idle),
        global_profile=plain(H), children=sum(H.values()), mass=total, equal_to=[s for s, _ in sources],
        identities=['mass = 73*66304 - 23680 = %d' % total, 'mass = 72*66304 + 64*666',
                    'halving guard 73^2 = 5329 > 2*48^2 = 4608'])
    print('composition: %s; mass %d = 72W + 64*666' % (plain(H), total), flush=True)

    # ---- 2. evaluator self-tests
    l2 = log2_enclosure()
    a1, a2, a3 = atanh_enclosure(1, 26), atanh_enclosure(1, 4801), atanh_enclosure(1, 8749)
    l2b = (18 * a1[0] - 2 * a2[1] + 8 * a3[0], 18 * a1[1] - 2 * a2[0] + 8 * a3[1])

    def log2_crosscheck(first, second):
        need(max(first[0], second[0]) <= min(first[1], second[1]), 'evaluator.log2_crosscheck',
             'two enclosures of log 2 are disjoint')
        return 'overlap'

    log2_crosscheck(l2, l2b)

    def exp_log2_check(e):
        need(e[0] <= 2 * ONE <= e[1], 'evaluator.exp_log2', 'exp(log 2) enclosure misses 2')
        return 'contains 2'

    exp_log2_check(exp_enclosure(l2[0], l2[1]))
    for r in sorted(set(H) | {47, 48}):
        direct = log_enclosure(m, r)
        lm, lr = log_enclosure(m, 1), log_enclosure(r, 1)
        need(max(direct[0], lm[0] - lr[1]) <= min(direct[1], lm[1] - lr[0]), 'evaluator.log_crosscheck',
             'log(m/%d) disagrees with log m - log %d' % (r, r))
    print('evaluator: PREC=%d bits; self-tests PASS' % PREC, flush=True)

    # ---- 3. this fill: native and conservative brackets
    native = Evaluator.of_profile(H, m, W)
    r_lo, r_hi = native.root_bracket()
    cons = Evaluator.of_profile(H, m, W, surcharge=True)
    c_lo, c_hi = cons.root_bracket()
    need(r_hi - r_lo == c_hi - c_lo == Fraction(1, 10 ** DIG) <= Fraction(1, 10 ** 30), 'moment.bracket', 'width')
    need(c_hi <= r_lo, 'moment.bracket', 'conservative root not below native root')
    b80_lo, b80_hi = (Fraction(x) for x in CLAIMS['b80_bracket'])
    require_accept(native, b80_lo, 'build-report bracket lower end')
    require_reject(native, b80_hi, 'build-report bracket upper end')
    need((r_lo, r_hi) == (b80_lo, b80_hi), 'moment.bracket', 'recounted bracket differs from the build report')
    acc = require_accept(native, r_lo, 'native lower end')
    rej = require_reject(native, r_hi, 'native upper end')
    cacc = require_accept(cons, c_lo, 'conservative lower end')
    crej = require_reject(cons, c_hi, 'conservative upper end')
    receipt['this_fill'] = dict(
        native=dict(root_bracket=[dec(r_lo), dec(r_hi)], width='1E-%d' % DIG,
                    mu_minus_one_at_lo=interval(acc[0] - 1, acc[1] - 1), mu_minus_one_at_hi=interval(rej[0] - 1, rej[1] - 1),
                    equals_build_report_bracket=True),
        conservative=dict(model='mu(a) + 32 m N m^a / (10^16 W), N = %d children' % sum(H.values()),
                          root_bracket=[dec(c_lo), dec(c_hi)], width='1E-%d' % DIG,
                          mu_minus_one_at_lo=interval(cacc[0] - 1, cacc[1] - 1),
                          mu_minus_one_at_hi=interval(crej[0] - 1, crej[1] - 1)),
        native_minus_conservative=interval(r_lo - c_hi, r_hi - c_lo))
    print('this fill native root in [%s, %s]' % (dec(r_lo), dec(r_hi)), flush=True)
    print('this fill conservative root in [%s, %s]' % (dec(c_lo), dec(c_hi)), flush=True)

    # ---- 4. PR2269: positive control (its endpoints under our evaluator) and comparison
    spec69 = json.loads(b69['new/SPEC.json'])
    B69 = json.loads(b69['outer/B.json'])
    H69 = int_profile(json.loads(b69['new/PROFILE.json']), 'PR2269 new/PROFILE.json')
    need(H69 == int_profile(B69['profile'], 'B.json') == int_profile(spec69['expected']['global_profile'], 'SPEC'),
         'claims.pr2269', 'PR2269 profiles disagree')
    check_mass(H69, m, W, T, calls)
    cl69 = Fraction(spec69['expected']['complex_lower'])
    ccl69 = Fraction(spec69['expected']['conservative_complex_lower'])
    b69v = Fraction(B69['b'])
    need(b69v == cl69 - Fraction(1, 10 ** 100) and dec(b69v, 100).startswith(CLAIMS['b2269_prefix']),
         'claims.pr2269', 'b = complex_lower - 1e-100')
    n69 = Evaluator.of_profile(H69, m, W)
    k69 = Evaluator.of_profile(H69, m, W, surcharge=True)
    require_accept(n69, cl69, 'PR2269 complex_lower')
    require_reject(n69, cl69 + Fraction(1, 10 ** 90), 'PR2269 complex_lower + 1e-90')
    require_accept(k69, ccl69, 'PR2269 conservative_complex_lower')
    require_reject(k69, ccl69 + Fraction(1, 10 ** 90), 'PR2269 conservative_complex_lower + 1e-90')
    n69_lo, n69_hi = n69.root_bracket()
    k69_lo, k69_hi = k69.root_bracket()
    ours_at_b69 = require_reject(native, b69v, 'this fill at PR2269 b')
    ours_at_k69 = require_reject(cons, ccl69, 'this fill (conservative) at PR2269 conservative_complex_lower')
    need(r_hi < b69v and c_hi < ccl69, 'compare', 'ordering')
    print('PR2269: endpoints reproduced; native root [%s, %s]; b - ours in %s' % (
        dec(n69_lo)[:24], dec(n69_hi)[:24], interval(b69v - r_hi, b69v - r_lo, 12)), flush=True)

    # ---- 5. PR2322: positive control and comparison
    C22 = json.loads(b22['CLAIM.json'])
    E22 = json.loads(b22['evidence/EXACT-MOMENT.json'])
    H22 = int_profile(C22['global_profile'], 'PR2322 CLAIM.json')
    need(H22 == int_profile(E22['profile'], 'EXACT-MOMENT') and (C22['live'], C22['m'], C22['deficit']) == (W, m, 23680),
         'claims.pr2322', 'PR2322 profile/geometry')
    check_mass(H22, m, W, T, calls)
    e22_lo, e22_hi = Fraction(C22['native_endpoint_lower']), Fraction(C22['native_endpoint_upper'])
    kap22 = Fraction(C22['kappa'])
    need(kap22 == Fraction(CLAIMS['kappa2322']) and kap22 < e22_lo, 'claims.pr2322', 'kappa')
    n22 = Evaluator.of_profile(H22, m, W)
    k22 = Evaluator.of_profile(H22, m, W, surcharge=True)
    require_accept(n22, e22_lo, 'PR2322 native_endpoint_lower')
    require_reject(n22, e22_hi, 'PR2322 native_endpoint_upper')
    n22_lo, n22_hi = n22.root_bracket()
    need((n22_lo, n22_hi) == (e22_lo, e22_hi), 'claims.pr2322', 'PR2322 bracket not reproduced')
    k22_lo, k22_hi = k22.root_bracket()
    ours_at_kap22 = require_reject(native, kap22, 'this fill at PR2322 kappa')
    require_reject(cons, k22_lo, 'this fill (conservative) at PR2322 conservative root')
    print('PR2322: native endpoint bracket reproduced; kappa - ours in %s' % interval(kap22 - r_hi, kap22 - r_lo, 12),
          flush=True)

    # ---- 6. packing cap (R = 48) for the 80-alias words, and the same engine on the 43-alias words
    w80, idle80 = cap_weights(local, counts, m, W, calls)
    cap80 = Evaluator(w80, m, W)
    p80_lo, p80_hi = cap80.root_bracket()
    ce = Fraction(CLAIMS['cap80_cap_ext'])
    need(ce <= p80_lo and p80_hi <= ce + Fraction(1, 10 ** 15), 'cap', 'cap_ext R=48 value %s not reproduced' % ce)
    w43, idle43 = cap_weights(dict((p, dict(v)) for p, v in CLAIMS['local43'].items()), counts, m, W, calls)
    p43_lo, p43_hi = Evaluator(w43, m, W).root_bracket()
    c43 = Fraction(CLAIMS['cap43_cap_ext'])
    need(abs(p43_lo - c43) <= Fraction(1, 2 * 10 ** 12) + Fraction(1, 10 ** 15), 'cap', 'cap43 not reproduced')
    need(r_hi < p80_lo and n69_hi < p43_lo, 'cap', 'a realized root above its cap')
    print('packing cap R=48: 80-alias [%s..] (PR2339 cap_ext %s reproduced); this fill = %.6f%% of it' % (
        dec(p80_lo)[:20], CLAIMS['cap80_cap_ext'], float(100 * r_hi / p80_lo)), flush=True)

    receipt['comparison'] = dict(
        pr2269=dict(b=dec(b69v, 100)[:44] + '...', complex_lower_accept_plus_1e90_reject=True,
                    conservative_complex_lower_accept_plus_1e90_reject=True,
                    native_root_bracket=[dec(n69_lo), dec(n69_hi)], conservative_root_bracket=[dec(k69_lo), dec(k69_hi)],
                    this_fill_mu_minus_one_at_b=interval(ours_at_b69[0] - 1, ours_at_b69[1] - 1),
                    this_fill_conservative_mu_minus_one_at_ccl=interval(ours_at_k69[0] - 1, ours_at_k69[1] - 1),
                    b_minus_this_native_root=interval(b69v - r_hi, b69v - r_lo),
                    relative_native=interval((r_lo - b69v) / b69v, (r_hi - b69v) / b69v, 8),
                    conservative_minus_this_conservative=interval(ccl69 - c_hi, ccl69 - c_lo)),
        pr2322=dict(kappa=CLAIMS['kappa2322'], native_endpoint_bracket=[C22['native_endpoint_lower'], C22['native_endpoint_upper']],
                    native_bracket_reproduced=True, conservative_root_bracket=[dec(k22_lo), dec(k22_hi)],
                    this_fill_mu_minus_one_at_kappa=interval(ours_at_kap22[0] - 1, ours_at_kap22[1] - 1),
                    kappa_minus_this_native_root=interval(kap22 - r_hi, kap22 - r_lo),
                    native_endpoint_minus_this=interval(e22_lo - r_hi, e22_hi - r_lo),
                    conservative_minus_this_conservative=interval(k22_lo - c_hi, k22_hi - c_lo)),
        packing_cap=dict(model='fixed local profile + all idle mass %d in fractional rank-48 children' % idle80,
                         cap80_root_bracket=[dec(p80_lo), dec(p80_hi)], cap_ext_value=CLAIMS['cap80_cap_ext'],
                         cap_ext_reproduced=True, cap43_root_bracket=[dec(p43_lo), dec(p43_hi)],
                         cap43_cap_ext=CLAIMS['cap43_cap_ext'],
                         this_fill_fraction_of_cap80=interval(r_lo / p80_hi, r_hi / p80_lo, 10),
                         pr2269_b_fraction_of_cap43=interval(b69v / p43_hi, b69v / p43_lo, 10)))

    # ---- 7. negative controls
    results = []
    ok = True
    ok &= expect_reject('this fill claimed at PR2269 b', 'moment.accept',
                        lambda: require_accept(native, b69v, 'PR2269 b'), results)
    ok &= expect_reject('this fill claimed at PR2322 kappa', 'moment.accept',
                        lambda: require_accept(native, kap22, 'PR2322 kappa'), results)
    ok &= expect_reject('native upper end + 1e-15 claimed admissible', 'moment.accept',
                        lambda: require_accept(native, r_hi + Fraction(1, 10 ** 15), 'r_hi + 1e-15'), results)
    ok &= expect_reject('native root claimed on the conservative side', 'moment.accept',
                        lambda: require_accept(cons, r_lo, 'native r_lo with surcharge'), results)
    split = dict(H)
    split[48] -= 1
    split[47] = split.get(47, 0) + 1
    split[1] += 1
    split = dict((r, split[r]) for r in sorted(split))
    need(mass_of(split) == total, 'control', 'split keeps the mass')
    ok &= expect_reject('one idle 48 replaced by 47 + 1: composition', 'compose.profile',
                        lambda: check_composition(split, sources[:1]), results)
    s_lo, s_hi = Evaluator.of_profile(split, m, W).root_bracket()
    moved = s_hi < r_lo or s_lo > r_hi
    results.append(dict(name='one idle 48 replaced by 47 + 1: root moves', target='moment.root', ok=moved,
                        rejected_by='moment.root' if moved else None,
                        detail='split root [%s, %s]' % (dec(s_lo), dec(s_hi))))
    ok &= moved
    ok &= expect_reject('provider counts swapped (417 gauge44 + 249 extra)', 'compose.profile',
                        lambda: check_composition(compose(local, {'gauge44': 417, 'extra': 249}, idle), sources[:1]),
                        results)
    ok &= expect_reject('43-alias local profiles with the 80-alias idle', 'compose.profile',
                        lambda: check_composition(compose(CLAIMS['local43'], counts, idle), sources[:1]), results)
    ok &= expect_reject('W off by one (66305)', 'compose.mass', lambda: check_mass(H, m, W + 1, T, calls), results)
    ok &= expect_reject('log 2 by 10 atanh terms without the remainder bound', 'evaluator.log2_crosscheck',
                        lambda: log2_crosscheck(tuple(2 * v for v in atanh_enclosure(1, 3, terms=10, tail=False)), l2b),
                        results)
    log2_crosscheck(tuple(2 * v for v in atanh_enclosure(1, 3, terms=10, tail=True)), l2b)
    ok &= expect_reject('exp(log 2) by 3 Taylor terms without the remainder bound', 'evaluator.exp_log2',
                        lambda: exp_log2_check(exp_enclosure(l2[0], l2[1], terms=3, tail=False)), results)
    exp_log2_check(exp_enclosure(l2[0], l2[1], terms=3, tail=True))
    bad = bytearray(b69['new/PROFILE.json'])
    bad[2] ^= 1

    def flipped():
        try:
            F.verify(bytes(bad), PINS_2269_PRICE['new/PROFILE.json'][0], PINS_2269_PRICE['new/PROFILE.json'][1],
                     'new/PROFILE.json (flipped)')
        except F.CheckFailure as e:
            raise Reject('pin', str(e))

    ok &= expect_reject('one flipped bit in PR2269 new/PROFILE.json', 'pin', flipped, results)
    receipt['negative_controls'] = results
    receipt['controls_ok'] = bool(ok)
    print('negative controls: %d/%d rejected by their targeted checks' % (sum(1 for x in results if x['ok']), len(results)),
          flush=True)
    need(ok, 'controls', 'a negative control was not rejected by its targeted check')
    receipt['summary'] = dict(
        native=[dec(r_lo), dec(r_hi)], conservative=[dec(c_lo), dec(c_hi)],
        below_pr2269_b=True, below_pr2322_kappa=True, cap80=[dec(p80_lo), dec(p80_hi)],
        gap_to_pr2269_b=sci(b69v - r_hi, 6), gap_to_pr2322_kappa=sci(kap22 - r_hi, 6),
        fraction_of_cap80=sci(r_hi / p80_lo, 8))
    receipt['not_checked'] = [
        'Outer ledger / bit endpoint / kappa: no kappa is claimed for this fill.',
        'Native lowering, invoice and precision tapes of the 80-alias words; the moment uses only the rank profile, '
        'm and W.  Under the PR2322 private-namespace rule the 44 zero buffers sit in the reserved tableau '
        '(fill_check80 R-f) and do not enter the profile.']
    return dict(r_lo=r_lo, r_hi=r_hi, c_lo=c_lo, c_hi=c_hi, controls=len(results))


def main():
    ap = argparse.ArgumentParser(description='Certified price of the 80-alias T74 owner fill')
    ap.add_argument('--repo', default=DEFAULT_REPO)
    ap.add_argument('--words-from-inputs', action='store_true')
    ap.add_argument('--out', action='store_true', help='write %s next to this script' % RECEIPT_NAME)
    args = ap.parse_args()
    receipt = dict(checker='price80.py', python=sys.version.split()[0],
                   object='global profile of OWNERS-80.json.gz recounted by fill_check80.py',
                   credits='PR2339 (this author); PR2269 Jeremy Kothe; PR2322 Vlado Vojdanovski; PR2312/PR2302 '
                           'jeremykothe2; PR2226 Cinna Davis; PR1319/PR1297 T74 lineage (Rohan Arun et al.); merged '
                           'complex-local-word-ceiling cap model (Douglas Colkitt). Adapted from our iteration-3 '
                           'price_check.py (commit 4a2f20ea). Prepared with substantial AI assistance (Claude Code, '
                           'Anthropic); Apache-2.0.')
    t0 = time.time()
    ok, info = True, None
    try:
        info = run(args, receipt)
    except Reject as e:
        ok = False
        receipt['failure'] = str(e)
        print('FAILED: %s' % e, flush=True)
    except Exception as e:
        ok = False
        receipt['failure'] = '%s: %s' % (type(e).__name__, e)
        print('FAILED: %s: %s' % (type(e).__name__, e), flush=True)
    receipt['model'] = __doc__.split('MODEL (stated precisely; also written to the receipt field "model").')[1].strip()
    receipt['result'] = PASS_LINE if ok else FAIL_LINE
    print('elapsed %.1f s' % (time.time() - t0))
    if args.out:
        with open(os.path.join(HERE, RECEIPT_NAME), 'w') as fh:
            json.dump(receipt, fh, indent=1, sort_keys=True)
            fh.write('\n')
    if ok:
        s = receipt['summary']
        print('%s native=[%s,%s] conservative=[%s,%s] below_2269=1 below_2322=1 cap_fraction=%s controls=%d' % (
            PASS_LINE, s['native'][0], s['native'][1], s['conservative'][0], s['conservative'][1],
            s['fraction_of_cap80'], info['controls']))
        return 0
    print(FAIL_LINE)
    return 1


if __name__ == '__main__':
    sys.exit(main())
