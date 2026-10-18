#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent price check (task C) of PR #2269: global profile and an exact moment-root bracket.

Object: CrocSwap/integer-mult-bounds PR #2269 (jeremykothe2), head
b479fc5567bc09ab9185bffe89b62594f36d74e5, package research/gmx-t74-borrow43/.
The package's complex saving is b = (certified native complex endpoint) - 1e-100
= 0.0016962471390584742207696... (outer/B.json).  The claimed conditional kappa
(outer/OUTER-CLAIM.json) is derived from b by the inherited PR1673/PR1786 outer
ledger.

Credit: PR2269 (jeremykothe2) for the borrow43 package, its profile, endpoints
and ledger; PR2226 (Cinna Davis / 1337isnot1337, with OpenAI Codex) for
anticipatory dirty borrowing; PR2260 (Dugongue) for concurrent application of
PR2226; the T74 lineage PR1319/PR1297 (Rohan Arun), PR1625 (mdumitrean), the
pivot-554 kernel (PR1672 lineage); the retained PR547/PR548/PR559 moment
engines and the icekylinx and Zhihao Chen (jacklightChen) / eumemic exact-assembly and
independent-checker lineage.  This file shares no code with any of them.  It was
written from their written specification (package README, new/SPEC.json,
outer/RETUNED-SLACKS.md, outer/FINE-PADDING-COMPOSITION.md and the moment
formula as stated in code/assemble.py); no package code is imported or run.

The only imported code is our own: words_check.py (task A) and fill_check.py
(task B), loaded from this directory by explicit file path.

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.

Usage:  python3 -I -B price_check.py [--repo PATH | --blob-dir DIR] [--out [RECEIPT.json]]
--blob-dir DIR: an exported copy of the package, DIR/<package-relative path>
(for example `git archive <head> research/gmx-t74-borrow43 | tar -x`, then
DIR = <that>/research/gmx-t74-borrow43).  The receipt (default
price_check.receipt.json) must be next to this script.  The final stdout line
starts with PASS_T74_BORROW43_PRICE_INDEPENDENT or FAIL_T74_BORROW43_PRICE_INDEPENDENT.

MODEL (stated precisely; also written to the receipt field "model").
 1. Local paid profiles P_gauge44 = profile of BORROW-WORD-43base and
    P_extra = profile of BORROW-WORD-43extra, recounted by words_check.frame_check
    (nested frame climbs + COPY charges; warps checked by words_check.check_all_warps).
 2. Idle remainders: recounted by the fill_check pipeline from OWNERS.json.gz
    (rank minus occupied cells for every (owner replica, child, port) bin).
 3. Composition (new/SPEC.json expected.global_profile; code/assemble.py sums the
    dispatched providers' paid profiles over the 666 calls and adds the idle
    remainders):  H = sum over calls of P_dispatch(call) + idle
    = 249 P_gauge44 + 417 P_extra + idle, with the counts taken from DISPATCH.json.
 4. Moment (m = 73, W = 66304 live data families):
       mu(a) = sum_r n_r (r/m)^(1-a) / W = sum_r n_r r/(m W) exp(a log(m/r)).
    Native complex side (evidence/ASSEMBLY.json surcharge_model complex = false;
    code/assemble.py checks complex_lower with surcharge off): no surcharge.
    This is the side of new/SPEC.json complex_lower and of outer/B.json b.
    Conservative complex side (surcharge on): mu(a) + 32 m N m^a / (10^16 W),
    N = sum_r n_r (number of children).  It prices conservative_complex_lower.
    Every rank satisfies 0 < r < m, so each term is strictly increasing in a;
    the root rho is the unique a > 0 with mu(a) = 1 (mu(0) = mass/(mW) < 1).
    'accept a' means mu(a) < 1 is certified; 'reject a' means mu(a) > 1 is certified.
 5. Certified evaluation (exact integers on the grid 2^-PREC, PREC = 800 bits,
    every rounding directed): log x = k log 2 + 2 atanh(z) with 2^k <= x < 2^(k+1),
    z = (x - 2^k)/(x + 2^k) in [0, 1/3), log 2 = 2 atanh(1/3); atanh(z) by its
    positive series plus the remainder bound z^(2N+1)/((2N+1)(1-z^2)); exp(x) for
    0 <= x < 1 by its positive Taylor series (lower: truncated sum) plus the
    remainder bound x^N/N! (N+1)/(N+1-x) (upper).  mu(a) is then enclosed by an
    exact rational interval; comparisons with 1 are exact.  Self-tests: log 2 by a
    second formula (18 atanh(1/26) - 2 atanh(1/4801) + 8 atanh(1/8749)), log(m/r)
    against log m - log r, and exp(log 2) must enclose 2.
 6. Root bracket: bisection on the decimal grid 10^-130 starting from [0, 1/100],
    using only certified accept/reject decisions; it does not use any claimed value.
"""

import sys

if sys.flags.optimize:
    sys.stdout.write('refusing to run under python -O\nFAIL_T74_BORROW43_PRICE_INDEPENDENT\n')
    sys.exit(2)

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import time
from collections import Counter
from fractions import Fraction

PASS_LINE = 'PASS_T74_BORROW43_PRICE_INDEPENDENT'
FAIL_LINE = 'FAIL_T74_BORROW43_PRICE_INDEPENDENT'
COMMIT = 'b479fc5567bc09ab9185bffe89b62594f36d74e5'
PKG = 'research/gmx-t74-borrow43/'
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO = os.path.dirname(os.path.dirname(HERE))
RECEIPT_NAME = 'price_check.receipt.json'

# package-relative path -> (git blob id, sha256 of the blob bytes); asserted at run time
PINS = {
    'PROFILE.json': ('48249b94604daccf0552c0c3b2489716344f7ff2',
                     '7012a58b4078d41e3b4412204d7dfdf9eb401bfe7da5429002150bdfc3558865'),
    'new/PROFILE.json': ('3e103605dd46c8754028056eb9dde9a73b9bfdca',
                         '50fcc0960a47f6d35064d3b55ea6dcb4cebbd305aec215c8034f626718595538'),
    'new/SPEC.json': ('2431d1cebbb2e155356d2da160d60808498bc33d',
                      'bd091ed9e7f4939d06abb467d0d2c56ce0f34ba800d74132669f7b667e125d2d'),
    'outer/B.json': ('a66501df3178012477b4c54fb6888e986b52a25e',
                     '631d89563be62a156c2b0119f9d4ba5a31cbf36380768bf8748825cf361bb525'),
    'outer/OUTER-CLAIM.json': ('f1feaefc27028e590fa7992d273c137897b379eb',
                               'ffa05de3c8d7cb7de0114d25df7250909581f4a2c0ce68c8d20eb821bf67f0e5'),
    'outer/LEDGER.json': ('3644673ab40b7b3595e94bbb7e118924a1cc48a1',
                          'eab3f0cbd5b5c45c76cee3e2daefd73c994bf7cfa80be118c67e6fab6106a05b'),
    'README.md': ('b555bc54dc661658e4d5fcbc5e3bd6503d7af4bd',
                  '2bf8d14e32ea03c614107eccfcce2422287a3a0552ab90f926b464d55767afcf'),
    'CLAIM.json': ('214e02514d2aba5c3977dae6285bf925c685db3e',
                   'bbcb4b72c86e4ca668256f8bfa6e35c1830a6e0edd77b7ab6230d8a3a7d7d31e'),
    'evidence/ASSEMBLY.json': ('6e9debfd552d18846fe55e4cbe6c59a37447b035',
                               '5d9eb1ce551386024b5b6894836f81ed03a83d2e0c0bd0e02e3f6410a596bb2c'),
    'PRICE.json': ('c41b950145014912b2b2d176cb4972408c95e23e',
                   'c5ec535fd9edbdec7b64edd5a8b862edb1a7f173d411dacb279172659573e16a'),
}

# Claims under test, written here from the README / scout notes (not read from the files).
CLAIMS = dict(
    local={'gauge44': {1: 2351, 2: 501, 3: 414, 4: 129, 5: 42, 8: 8},
           'extra': {1: 2339, 2: 509, 3: 418, 4: 125, 5: 42, 8: 8}},
    local_mass=5385,
    counts={'gauge44': 249, 'extra': 417},
    idle={1: 23976, 3: 8673, 5: 813, 7: 150, 48: 24479},
    mass=4816512, m=73, W=66304, T=74, calls=666, max_child=48,
    b_decimal_prefix='0.0016962471390584742207696',
)
WORD_OF = {'gauge44': 'base', 'extra': 'extra'}   # provider id -> BORROW-WORD-43<tag>

ONE_Q = Fraction(1)


class Reject(Exception):
    def __init__(self, check, msg):
        Exception.__init__(self, '[%s] %s' % (check, msg))
        self.check = check
        self.msg = msg


def need(cond, check, msg):
    if not cond:
        raise Reject(check, msg)


# ----------------------------------------------------------------------------
# Inputs
# ----------------------------------------------------------------------------

def git_blob_id(data):
    h = hashlib.sha1()
    h.update(b'blob %d\0' % len(data))
    h.update(data)
    return h.hexdigest()


def verify_pin(rel, data):
    blob, sha = PINS[rel]
    need(git_blob_id(data) == blob, 'pin', 'git blob id mismatch for ' + rel)
    need(hashlib.sha256(data).hexdigest() == sha, 'pin', 'sha256 mismatch for ' + rel)


def read_inputs(repo, blob_dir):
    raw, record = {}, {}
    for rel in sorted(PINS):
        blob, sha = PINS[rel]
        if blob_dir is None:
            got = subprocess.run(['git', '-C', repo, 'rev-parse', '--verify', COMMIT + ':' + PKG + rel],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            need(got.returncode == 0, 'pin', 'cannot resolve %s at %s in %s' % (PKG + rel, COMMIT, repo))
            need(got.stdout.decode().strip() == blob, 'pin', PKG + rel + ' does not resolve to the pinned blob')
            got = subprocess.run(['git', '-C', repo, 'cat-file', 'blob', blob],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            need(got.returncode == 0, 'pin', 'cannot read blob ' + blob)
            data = got.stdout
        else:
            src = os.path.join(blob_dir, rel)
            need(os.path.isfile(src), 'pin', 'exported blob missing: ' + src)
            with open(src, 'rb') as fh:
                data = fh.read()
        verify_pin(rel, data)
        raw[rel] = data
        record[PKG + rel] = dict(git_blob=blob, sha256=sha, bytes=len(data))
    return raw, record


def as_json(raw, rel):
    return json.loads(raw[rel].decode('utf-8'))


def load_sibling(name):
    """Load our own task A/B module from this directory by explicit path (python -I drops the script dir)."""
    path = os.path.join(HERE, name + '.py')
    spec = importlib.util.spec_from_file_location('t74b43_' + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with open(path, 'rb') as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    return mod, digest


def int_profile(mapping, check, what):
    out = {}
    for k, v in mapping.items():
        need(type(v) is int and v > 0 and str(int(k)) == str(k), check, what + ': bad profile entry')
        out[int(k)] = v
    return out


def plain(prof):
    return dict((str(r), prof[r]) for r in sorted(prof) if prof[r])


def mass_of(prof):
    return sum(r * n for r, n in prof.items())


# ----------------------------------------------------------------------------
# Certified rational enclosures (integers on the grid 2^-PREC, directed rounding)
# ----------------------------------------------------------------------------

PREC = 800
ONE = 1 << PREC
MAX_TERMS = 4 * PREC


def cdiv(a, b):
    """ceil(a / b) for integers, b > 0."""
    return -((-a) // b)


def atanh_enclosure(p, q, terms=None, tail=True):
    """Integers (lo, hi) with lo <= 2^PREC atanh(p/q) <= hi, for 0 <= p/q <= 1/3.
    atanh(z) = sum_j z^(2j+1)/(2j+1) (positive terms).  Lower: floored partial sum.
    Upper: ceiled partial sum of N terms + z^(2N+1)/((2N+1)(1-z^2)) >= the remainder.
    terms/tail exist only for the negative controls (fixed truncation, remainder dropped)."""
    need(q > 0 and 0 <= 3 * p <= q, 'evaluator', 'atanh argument outside [0, 1/3]')
    if p == 0:
        return 0, 0
    p2, q2 = p * p, q * q
    pl, pu = (ONE * p) // q, cdiv(ONE * p, q)   # bounds of 2^PREC z^(2j+1), j = 0
    sl = su = 0
    j = 0
    while (pl > 0) if terms is None else (j < terms):
        need(j < MAX_TERMS, 'evaluator', 'atanh series did not terminate')
        sl += pl // (2 * j + 1)
        su += cdiv(pu, 2 * j + 1)
        pl = (pl * p2) // q2
        pu = cdiv(pu * p2, q2)
        j += 1
    if tail:   # pu >= 2^PREC z^(2j+1): remainder <= pu / ((2j+1)(1 - z^2)) = pu q^2 / ((2j+1)(q^2 - p^2))
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
    k = (p // q).bit_length() - 1          # 2^k <= p/q < 2^(k+1)
    a, b = p, q << k                       # y = a/b in [1, 2)
    zl, zu = atanh_enclosure(a - b, a + b)
    l2l, l2u = log2_enclosure()
    return k * l2l + 2 * zl, k * l2u + 2 * zu


def exp_enclosure(xl, xu, terms=None, tail=True):
    """Integers (lo, hi) with lo <= 2^PREC exp(x) <= hi for every x in [xl, xu] / 2^PREC, 0 <= xl <= xu < 2^PREC.
    Lower: floored Taylor partial sum at xl (positive terms).  Upper: ceiled partial sum at xu of N terms plus
    t_N (N+1)/(N+1-x) with t_N >= 2^PREC x^N/N!, which bounds sum_{i>=N} x^i/i! for 0 <= x < N+1.
    terms/tail exist only for the negative controls (fixed truncation of both sums, remainder dropped)."""
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
        t = cdiv(cdiv(t * xu, ONE), j)     # >= 2^PREC x^j / j!
        if (t <= 1) if terms is None else (j >= terms):
            break
        s += t
        j += 1
    if tail:
        s += cdiv(t * (j + 1) * ONE, (j + 1) * ONE - xu)
    return lo, s


class Evaluator(object):
    """mu(a) enclosures for one profile; logs are computed once per rank."""

    def __init__(self, profile, m, W, surcharge=False):
        need(all(type(r) is int and 0 < r < m and type(n) is int and n > 0 for r, n in profile.items()),
             'moment', 'every child must have 0 < rank < m')
        self.profile = dict(profile)
        self.m, self.W, self.surcharge = m, W, surcharge
        self.N = sum(profile.values())
        self.logs = dict((r, log_enclosure(m, r)) for r in sorted(profile))
        self.logm = log_enclosure(m, 1)

    def bounds(self, a):
        """Exact rationals lo <= mu(a) <= hi (plus the surcharge if enabled)."""
        a = Fraction(a)
        need(a >= 0, 'moment', 'negative saving')
        an, ad = a.numerator, a.denominator
        slo = shi = 0
        for r in sorted(self.profile):
            ll, lu = self.logs[r]
            el, eu = exp_enclosure((an * ll) // ad, cdiv(an * lu, ad))
            n = self.profile[r]
            slo += n * r * el
            shi += n * r * eu
        lo = Fraction(slo, self.m * self.W * ONE)
        hi = Fraction(shi, self.m * self.W * ONE)
        if self.surcharge:
            ll, lu = self.logm
            el, eu = exp_enclosure((an * ll) // ad, cdiv(an * lu, ad))
            c = 32 * self.m * self.N
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

    def root_bracket(self, digits):
        """Bisection on the 10^-digits grid from [0, 1/100] with certified decisions only."""
        scale = 10 ** digits
        lo, hi = 0, scale // 100
        need(self.side(Fraction(lo, scale)) < 0, 'moment', 'mu(0) >= 1: no positive saving')
        need(self.side(Fraction(hi, scale)) > 0, 'moment', 'mu(1/100) <= 1')
        steps, undecided = 0, None
        while hi - lo > 1:
            mid = (lo + hi) // 2
            s = self.side(Fraction(mid, scale))
            steps += 1
            if s < 0:
                lo = mid
            elif s > 0:
                hi = mid
            else:
                undecided = mid
                break
        return Fraction(lo, scale), Fraction(hi, scale), steps, undecided


# ----------------------------------------------------------------------------
# Display helpers (display only; never used for a decision)
# ----------------------------------------------------------------------------

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
    toward_larger_magnitude = (up and not neg) or (neg and not up)
    k = cdiv(y.numerator, y.denominator) if toward_larger_magnitude else y.numerator // y.denominator
    ds = str(k)
    e += len(ds) - sig
    return '%s%s.%sE%+d' % ('-' if neg else '', ds[0], ds[1:sig], e)


def dec(x, digits):
    """Exact decimal string of a rational with denominator dividing 10^digits."""
    x = Fraction(x)
    y = x * 10 ** digits
    need(y.denominator == 1, 'display', 'not on the decimal grid')
    n = y.numerator
    s = str(abs(n)).rjust(digits + 1, '0')
    return ('-' if n < 0 else '') + s[:-digits] + '.' + s[-digits:]


def interval(lo, hi):
    return [sci(lo, up=False), sci(hi, up=True)]


# ----------------------------------------------------------------------------
# Composition
# ----------------------------------------------------------------------------

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


def check_mass(H, m, W, T, calls, deficit_claim):
    mass = mass_of(H)
    need(W == 896 * T, 'compose.mass', 'W != 896 T (live data families)')
    need(calls == 9 * T, 'compose.mass', 'calls != 9 T')
    need(m * W - mass == deficit_claim == 320 * T, 'compose.mass', 'deficit m W - mass != 320 T')
    need(mass == (m - 1) * W + 64 * calls, 'compose.mass', 'mass != (m-1) W + 64 calls')
    need(m * m > 2 * max(H) ** 2, 'compose.mass', 'halving guard m^2 > 2 maxchild^2')
    return mass


# ----------------------------------------------------------------------------
# Negative-control harness
# ----------------------------------------------------------------------------

def expect_reject(name, target, fn, results):
    try:
        detail = fn()
    except Reject as e:
        ok = e.check == target
        results.append(dict(name=name, target=target, rejected_by=e.check, ok=ok, detail=e.msg[:300]))
        return ok
    results.append(dict(name=name, target=target, rejected_by=None, ok=False, detail=str(detail)[:300]))
    return False


def require_accept(ev, a, what):
    lo, hi = ev.bounds(a)
    need(hi < 1, 'moment.accept', '%s: mu - 1 in %s is not certified < 0' % (what, interval(lo - 1, hi - 1)))
    return lo, hi


def require_reject(ev, a, what):
    lo, hi = ev.bounds(a)
    need(lo > 1, 'moment.reject', '%s: mu - 1 in %s is not certified > 0' % (what, interval(lo - 1, hi - 1)))
    return lo, hi


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def run(args, receipt):
    t0 = time.time()
    raw, record = read_inputs(args.repo, args.blob_dir)
    receipt['pins'] = record
    print('pins: %d package blobs verified (sha256 + git blob id)' % len(record), flush=True)
    W_mod, w_sha = load_sibling('words_check')
    F_mod, f_sha = load_sibling('fill_check')
    receipt['imported_own_modules'] = {'words_check.py': w_sha, 'fill_check.py': f_sha}

    # ---- 1. local profiles recounted by task A code
    js, wpins, _ = W_mod.load_inputs(args.repo, args.blob_dir)
    local, local_mass, canon, word_widths = {}, {}, {}, {}
    for pid in ('gauge44', 'extra'):
        tag = WORD_OF[pid]
        P = W_mod.parse_borrow(js['word_' + tag])
        W_mod.check_all_warps(P)
        fr = W_mod.frame_check(P)
        local[pid] = dict((r, n) for r, n in sorted(fr['paid'].items()) if n)
        need(dict((r, n) for r, n in fr['copies'].items() if n) == {8: 8} and not fr['climbs'].get(8), 'local',
             pid + ': the rank-8 entries must be exactly the 8 COPY children')
        local_mass[pid] = fr['mass']
        word_widths[pid] = list(fr['widths'])
        C = W_mod.parse_canonical(js['canon_' + tag])
        frC = W_mod.frame_check(C)
        canon[pid] = dict((r, n) for r, n in sorted(frC['paid'].items()) if n)
        need(local[pid] == CLAIMS['local'][pid], 'local', '%s recount %s != claimed %s' % (
            pid, plain(local[pid]), plain(CLAIMS['local'][pid])))
        need(local_mass[pid] == mass_of(local[pid]) == CLAIMS['local_mass'], 'local', pid + ' local mass')
    print('local profiles (words_check recount): gauge44 %s extra %s, mass %d each' % (
        plain(local['gauge44']), plain(local['extra']), CLAIMS['local_mass']), flush=True)

    # ---- 2. idle remainders recounted by task B code
    try:
        fblobs, frecord = F_mod.load_blobs(args.repo, args.blob_dir)
        ctx, rows, helpers_info, extra = F_mod.borrow_case(fblobs)
        sched = F_mod.derive_schedule(ctx)
        fres = F_mod.run_pipeline(ctx, sched, rows)
    except F_mod.CheckFailure as e:
        raise Reject('fill', 'fill_check pipeline failed: ' + str(e))
    idle = dict((int(r), n) for r, n in fres['idle'].items())
    counts = dict(Counter(ctx['dispatch'].values()))
    T, W, calls = ctx['T'], fres['live'], fres['calls']
    need(idle == CLAIMS['idle'], 'idle', 'recounted idle %s != claimed %s' % (plain(idle), plain(CLAIMS['idle'])))
    need(counts == CLAIMS['counts'] and sum(counts.values()) == calls == CLAIMS['calls'], 'dispatch',
         'provider call counts %r' % counts)
    need((T, W) == (CLAIMS['T'], CLAIMS['W']), 'geometry', 'T/W')
    for pid in word_widths:   # cross-module consistency: both recounts see the same 437 helper widths
        need(word_widths[pid] == list(ctx['widths'][pid]), 'cross', pid + ' helper widths differ between A and B')
    print('idle remainders (fill_check recount): %s; dispatch %s' % (plain(idle), counts), flush=True)

    # ---- 3. composition and mass identities
    spec = as_json(raw, 'new/SPEC.json')
    Bj = as_json(raw, 'outer/B.json')
    ledger = as_json(raw, 'outer/LEDGER.json')
    m = spec['geometry']['dimension']
    need(m == CLAIMS['m'] == ledger['m'], 'geometry', 'm')
    need(spec['expected']['live'] == W == Bj['live'] == ledger['W'], 'geometry', 'W')
    H = compose(local, counts, idle)
    sources = [('PROFILE.json', int_profile(as_json(raw, 'PROFILE.json'), 'compose.profile', 'PROFILE.json')),
               ('new/PROFILE.json', int_profile(as_json(raw, 'new/PROFILE.json'), 'compose.profile', 'new/PROFILE')),
               ('new/SPEC.json expected.global_profile',
                int_profile(spec['expected']['global_profile'], 'compose.profile', 'SPEC')),
               ('outer/B.json profile', int_profile(Bj['profile'], 'compose.profile', 'B.json')),
               ('outer/LEDGER.json profile', int_profile(ledger['profile'], 'compose.profile', 'LEDGER'))]
    check_composition(H, sources)
    deficit = 320 * T
    mass = check_mass(H, m, W, T, calls, m * W - spec['expected']['rank_mass'])
    need(mass == CLAIMS['mass'] == spec['expected']['rank_mass'], 'compose.mass', 'rank mass')
    need(max(H) == CLAIMS['max_child'], 'compose.mass', 'max child')
    need(H.get(8, 0) == 8 * calls and 8 not in idle and all(local[p].get(8) == 8 for p in local), 'compose.mass',
         'rank-8 children are exactly the 8 COPY children of each call')
    receipt['composition'] = dict(
        rule='H = sum over the %d dispatched calls of P_provider + idle = %d P_gauge44 + %d P_extra + idle' % (
            calls, counts['gauge44'], counts['extra']),
        local_profiles=dict((p, plain(local[p])) for p in sorted(local)), local_mass=CLAIMS['local_mass'],
        provider_counts=counts, idle=plain(idle), global_profile=plain(H), children=sum(H.values()),
        equal_to=[s for s, _ in sources], mass=mass, live_W=W, m=m, T=T, calls=calls, deficit=deficit,
        identities=['mass = m W - D = 73*66304 - 23680 = %d, D = 320 T' % mass,
                    'mass = (m-1) W + 64 calls = 72*66304 + 64*666 = %d; the second term 42624 = W - D = 576 T '
                    'equals the mass of the 5328 = 8*666 rank-8 children, which are exactly the 8 COPY children '
                    '(rank 8) of each call: mass - (COPY mass) = (m-1) W' % mass,
                    'local: 666*5385 = %d; idle mass = %d' % (calls * CLAIMS['local_mass'], mass_of(idle)),
                    'halving guard 73^2 = 5329 > 2*48^2 = 4608'])
    print('composition: %s = PROFILE.json = new/PROFILE.json = SPEC = B.json = LEDGER; mass %d = 72W + 64*666' % (
        plain(H), mass), flush=True)

    # ---- 4. evaluator self-tests
    l2 = log2_enclosure()
    a1, a2, a3 = atanh_enclosure(1, 26), atanh_enclosure(1, 4801), atanh_enclosure(1, 8749)
    l2b = (18 * a1[0] - 2 * a2[1] + 8 * a3[0], 18 * a1[1] - 2 * a2[0] + 8 * a3[1])

    def log2_crosscheck(first, second):
        need(max(first[0], second[0]) <= min(first[1], second[1]), 'evaluator.log2_crosscheck',
             'two enclosures of log 2 are disjoint')
        return 'overlap'

    log2_crosscheck(l2, l2b)
    need(l2[1] - l2[0] < 2 ** 12 and l2b[1] - l2b[0] < 2 ** 12, 'evaluator', 'log 2 enclosure too wide')

    def exp_log2_check(e):
        need(e[0] <= 2 * ONE <= e[1], 'evaluator.exp_log2', 'exp(log 2) enclosure %s misses 2' % (
            interval(Fraction(e[0], ONE), Fraction(e[1], ONE)),))
        return 'contains 2'

    exp_log2_check(exp_enclosure(l2[0], l2[1]))
    ranks = sorted(set(H) | {47})
    for r in ranks:
        direct = log_enclosure(m, r)
        lm, lr = log_enclosure(m, 1), log_enclosure(r, 1)
        diff = (lm[0] - lr[1], lm[1] - lr[0])
        need(max(direct[0], diff[0]) <= min(direct[1], diff[1]), 'evaluator.log_crosscheck',
             'log(m/%d) disagrees with log m - log %d' % (r, r))
        need(direct[1] - direct[0] < 2 ** 16, 'evaluator', 'log enclosure too wide')
    receipt['evaluator'] = dict(
        grid_bits=PREC, log2=interval(Fraction(l2[0], ONE), Fraction(l2[1], ONE)),
        log2_width_ulps=l2[1] - l2[0],
        self_tests=['log 2 = 2 atanh(1/3) overlaps 18 atanh(1/26) - 2 atanh(1/4801) + 8 atanh(1/8749)',
                    'exp(log 2) encloses 2',
                    'log(73/r) overlaps log 73 - log r for r in %s' % ranks])
    print('evaluator: PREC=%d bits; self-tests PASS' % PREC, flush=True)

    # ---- 5. native moment: root bracket and the package endpoints
    native = Evaluator(H, m, W, surcharge=False)
    DIG = 130
    r_lo, r_hi, steps, undecided = native.root_bracket(DIG)
    need(undecided is None and r_hi - r_lo == Fraction(1, 10 ** DIG), 'moment.bracket', 'bisection stalled')
    X = spec['expected']
    complex_lower = Fraction(X['complex_lower'])
    b = Fraction(Bj['b'])
    b_above = Fraction(Bj['b_above_endpoint'])

    def b_identity(bb, bab):
        need(bb == complex_lower - Fraction(1, 10 ** 100), 'claims.b_identity', 'b != complex_lower - 1e-100')
        need(bab == complex_lower + Fraction(1, 10 ** 90), 'claims.b_identity', 'b_above != complex_lower + 1e-90')
        return 'identity holds'

    b_identity(b, b_above)
    need(Fraction(ledger['complex_lower_pinned']['rational']) == complex_lower and
         Fraction(ledger['complex_lower_short']['rational']) == b, 'claims.b_identity', 'LEDGER endpoints')
    need(dec(b, 100).startswith(CLAIMS['b_decimal_prefix']), 'claims.b_identity', 'b decimal prefix')
    cl_acc = require_accept(native, complex_lower, 'complex_lower')
    cl_rej = require_reject(native, complex_lower + Fraction(1, 10 ** 90), 'complex_lower + 1e-90')
    b_acc = require_accept(native, b, 'b')
    ba_rej = require_reject(native, b_above, 'b_above_endpoint')
    coarse = Fraction((complex_lower * 10 ** 24).__floor__(), 10 ** 24)
    co_acc = require_accept(native, coarse, 'coarse 1e-24 endpoint')
    co_rej = require_reject(native, coarse + Fraction(1, 10 ** 24), 'coarse 1e-24 endpoint + 1e-24')
    # task bracket: decimal 1e-21 cell containing b
    b_lo = Fraction((b * 10 ** 21).__floor__(), 10 ** 21)
    b_hi = b_lo + Fraction(1, 10 ** 21)
    need(b_lo <= b <= b_hi and b_hi - b_lo <= Fraction(1, 10 ** 20), 'moment.bracket', 'task bracket shape')
    tb_lo = require_accept(native, b_lo, 'b_lo')
    tb_hi = require_reject(native, b_hi, 'b_hi')
    # consistency of the independent root bracket with the claims (monotone mu)
    need(complex_lower <= r_lo and r_hi <= complex_lower + Fraction(1, 10 ** 90), 'moment.bracket',
         'root bracket not inside (complex_lower, complex_lower + 1e-90)')
    need(b_lo <= r_lo and r_hi <= b_hi, 'moment.bracket', 'root bracket not inside the task bracket')
    # the package's own enclosure of mu(b) (outer/LEDGER.json native_moment) must overlap ours
    led = [Fraction(v['rational']) for v in ledger['native_moment']]
    need(max(led[0], b_acc[0]) <= min(led[1], b_acc[1]), 'moment.ledger', 'LEDGER native_moment(b) disjoint from ours')
    gap_lo, gap_hi = r_lo - b, r_hi - b
    receipt['native'] = dict(
        model='mu(a) = sum_r n_r (r/73)^(1-a) / 66304, no surcharge (native complex side)',
        root_bracket=[dec(r_lo, DIG), dec(r_hi, DIG)], root_bracket_width='1E-%d' % DIG, bisection_steps=steps,
        complex_lower=dict(value=X['complex_lower'], accept=True, mu_minus_one=interval(cl_acc[0] - 1, cl_acc[1] - 1),
                           plus_1e90_reject=True, mu_minus_one_plus_1e90=interval(cl_rej[0] - 1, cl_rej[1] - 1)),
        b=dict(value=Bj['b'], decimal=dec(b, 100), equals='complex_lower - 1e-100', accept=True,
               mu_minus_one=interval(b_acc[0] - 1, b_acc[1] - 1),
               ledger_native_moment_overlaps=True,
               root_minus_b=interval(gap_lo, gap_hi)),
        b_above_endpoint=dict(value=Bj['b_above_endpoint'], reject=True,
                              mu_minus_one=interval(ba_rej[0] - 1, ba_rej[1] - 1)),
        coarse_1e24=dict(endpoint=dec(coarse, 24), accept=True, plus_1e24_reject=True),
        task_bracket=dict(b_lo=dec(b_lo, 21), b_hi=dec(b_hi, 21), width='1E-21', b_lo_le_b_le_b_hi=True,
                          mu_minus_one_at_b_lo=interval(tb_lo[0] - 1, tb_lo[1] - 1),
                          mu_minus_one_at_b_hi=interval(tb_hi[0] - 1, tb_hi[1] - 1)))
    print('native root in [%s, %s]' % (dec(r_lo, DIG)[:60] + '...', dec(r_hi, DIG)[:60] + '...'), flush=True)
    print('  complex_lower accepted, complex_lower+1e-90 rejected; b accepted (root - b in %s); task bracket '
          '[%s, %s] PASS' % (interval(gap_lo, gap_hi), dec(b_lo, 21), dec(b_hi, 21)), flush=True)

    # ---- 6. conservative side (surcharge) and the model control of code/assemble.py
    cons = Evaluator(H, m, W, surcharge=True)
    c_lo, c_hi, c_steps, c_und = cons.root_bracket(DIG)
    need(c_und is None, 'moment.bracket', 'conservative bisection stalled')
    ccl = Fraction(X['conservative_complex_lower'])
    cc_acc = require_accept(cons, ccl, 'conservative_complex_lower')
    cc_rej = require_reject(cons, ccl + Fraction(1, 10 ** 90), 'conservative_complex_lower + 1e-90')
    need(ccl <= c_lo and c_hi <= ccl + Fraction(1, 10 ** 90), 'moment.bracket', 'conservative bracket')
    sur_b = require_reject(cons, b, 'native b under the conservative surcharge')
    receipt['conservative'] = dict(
        model='mu(a) + 32 m N m^a / (10^16 W), N = %d children' % sum(H.values()),
        root_bracket=[dec(c_lo, DIG), dec(c_hi, DIG)],
        conservative_complex_lower=dict(value=X['conservative_complex_lower'], accept=True,
                                        mu_minus_one=interval(cc_acc[0] - 1, cc_acc[1] - 1), plus_1e90_reject=True),
        native_b_rejected_with_surcharge=dict(reject=True, mu_minus_one=interval(sur_b[0] - 1, sur_b[1] - 1)),
        native_minus_conservative_root=interval(r_lo - c_hi, r_hi - c_lo))
    print('conservative root in [%s...]; SPEC conservative_complex_lower accepted, +1e-90 rejected; native b '
          'rejected under the surcharge (model control)' % dec(c_lo, DIG)[:40], flush=True)

    # ---- 7. claimed kappa as an arithmetic function of b (outer lemmas NOT checked)
    oc = as_json(raw, 'outer/OUTER-CLAIM.json')
    kappa = Fraction(oc['kappa_rational'])
    need(Fraction(oc['kappa']) == kappa, 'claims.kappa', 'OUTER-CLAIM decimal != rational')

    def kappa_identity(kap, bb):
        q = bb - Fraction(1, 10 ** 100)
        eq = (1 - Fraction(2, 10 ** 100)) * q
        floor136 = Fraction((eq * 10 ** 136).__floor__(), 10 ** 136)
        need(kap == floor136 - Fraction(1, 10 ** 112), 'claims.kappa',
             'kappa != floor_1e-136((1-2e-100)(b-1e-100)) - 1e-112')
        return 'identity holds'

    kappa_identity(kappa, b)
    need(Fraction(ledger['rows']['struct_boundary_radix_union']['kappa']['rational']) == kappa, 'claims.kappa',
         'LEDGER kappa')
    readme = raw['README.md'].decode('utf-8')
    need(('**' + oc['kappa'] + '**') in readme, 'claims.kappa', 'README kappa string')
    strict = Fraction(as_json(raw, 'CLAIM.json')['kappa'])
    need(strict == Fraction(X['kappa']) == Fraction(ledger['online_final_kappa']['rational']), 'claims.kappa',
         'strict-assembly kappa')
    need(0 < strict < kappa < b < r_lo, 'claims.kappa', 'ordering strict kappa < kappa < b < root')
    claim = as_json(raw, 'CLAIM.json')
    baseline = Fraction(claim['baseline_kappa'])
    stated_gain = Fraction(claim['gain_over_claimed_leader'])
    half_unit = Fraction(5, 10 ** 11)   # half a unit of the 6th significant digit of 1.28346E-5
    need(abs(kappa - baseline - stated_gain) <= half_unit < abs(strict - baseline - stated_gain), 'claims.kappa',
         'CLAIM.json gain field')
    doc_notes = [
        'CLAIM.json kappa (%s...) is the strict-assembly kappa, while its gain_over_claimed_leader %s is the gain of '
        'the outer-ledger kappa over baseline_kappa (outer: %s; strict: %s).' % (
            claim['kappa_decimal'][:22], claim['gain_over_claimed_leader'], sci(kappa - baseline, 12),
            sci(strict - baseline, 12))]
    receipt['kappa'] = dict(
        claimed=oc['kappa'], identity='kappa = floor_1e-136((1 - 2e-100)(b - 1e-100)) - 1e-112 (exact)',
        b_minus_kappa=interval(b - kappa, b - kappa), root_minus_kappa=interval(r_lo - kappa, r_hi - kappa),
        strict_assembly_kappa=claim['kappa_decimal'], documentation_notes=doc_notes,
        scope='arithmetic link only; the PR1673/PR1786/PR1758 outer lemmas, the bit endpoint and the 47/62 outer '
              'inequalities are not checked here')
    print('kappa: OUTER-CLAIM kappa = floor_136((1-2e-100)(b-1e-100)) - 1e-112 exactly; strict < kappa < b < root',
          flush=True)

    # ---- 8. positive control: the pre-borrow assembly (evidence/ASSEMBLY.json = PRICE.json) endpoints
    asm = as_json(raw, 'evidence/ASSEMBLY.json')
    price = as_json(raw, 'PRICE.json')
    old = int_profile(asm['complex_profile'], 'control', 'ASSEMBLY profile')
    need(asm['surcharge_model'] == {'complex': False, 'bit': True}, 'control', 'surcharge model')
    need(mass_of(old) == mass, 'control', 'old profile mass')
    old_native, old_cons = Evaluator(old, m, W), Evaluator(old, m, W, surcharge=True)
    oc_l = Fraction(asm['complex_lower'])
    occ_l = Fraction(asm['conservative_complex_lower'])
    need(Fraction(price['prices']['native']['root']['lower']) == oc_l and
         Fraction(price['prices']['conservative']['root']['lower']) == occ_l, 'control',
         'PRICE.json and evidence/ASSEMBLY.json endpoints differ')
    require_accept(old_native, oc_l, 'old complex_lower')
    require_reject(old_native, oc_l + Fraction(1, 10 ** 24), 'old complex_lower + 1e-24')
    require_accept(old_cons, occ_l, 'old conservative_complex_lower')
    require_reject(old_cons, occ_l + Fraction(1, 10 ** 24), 'old conservative_complex_lower + 1e-24')
    o_lo, o_hi, _, _ = old_native.root_bracket(40)
    receipt['positive_control'] = dict(
        what='stale evidence/ASSEMBLY.json profile (an older pre-borrow T74 profile, H5 = 54612 = 82*666; the '
             'top-level PRICE.json carries the same endpoints): its certified 1e-24 native and conservative '
             'endpoints are reproduced (accept at the endpoint, reject at +1e-24)',
        profile=plain(old), native_endpoint=asm['complex_decimal'], conservative_endpoint=asm['conservative_complex_decimal'],
        old_root_bracket=[dec(o_lo, 40), dec(o_hi, 40)],
        root_minus_stale_assembly_root=interval(r_lo - o_hi, r_hi - o_lo))
    print('positive control: stale-assembly (older pre-borrow) endpoints %s / %s reproduced' % (asm['complex_decimal'],
                                                                         asm['conservative_complex_decimal']), flush=True)

    # ---- 9. negative controls
    results = []
    ok = True
    ok &= expect_reject('mu at claimed b + 1e-15 must exceed 1', 'moment.accept',
                        lambda: require_accept(native, b + Fraction(1, 10 ** 15), 'b + 1e-15'), results)
    lo15, hi15 = native.bounds(b + Fraction(1, 10 ** 15))
    need(lo15 > 1, 'moment.reject', 'mu(b + 1e-15) not certified > 1')
    split = dict(H)
    split[48] -= 1
    split[47] = split.get(47, 0) + 1
    split[1] += 1
    split = dict((r, split[r]) for r in sorted(split))
    need(mass_of(split) == mass, 'control', 'split keeps the mass')
    ok &= expect_reject('one idle 48 replaced by 47 + 1: composition', 'compose.profile',
                        lambda: check_composition(split, sources[:1]), results)
    ev_split = Evaluator(split, m, W)
    ok &= expect_reject('one idle 48 replaced by 47 + 1: claimed b no longer admissible', 'moment.accept',
                        lambda: require_accept(ev_split, b, 'b under the split profile'), results)
    s_lo, s_hi, _, s_und = ev_split.root_bracket(40)
    need(s_und is None, 'moment.bracket', 'split bisection stalled')
    moved = s_hi < r_lo or s_lo > r_hi
    results.append(dict(name='one idle 48 replaced by 47 + 1: root moves', target='moment.root', ok=moved,
                        rejected_by='moment.root' if moved else None,
                        detail='split root in [%s, %s]; original root - split root in %s' % (
                            dec(s_lo, 40), dec(s_hi, 40), interval(r_lo - s_hi, r_hi - s_lo))))
    ok &= moved
    ok &= expect_reject('provider counts swapped (417 gauge44 + 249 extra)', 'compose.profile',
                        lambda: check_composition(compose(local, {'gauge44': counts['extra'], 'extra': counts['gauge44']},
                                                          idle), sources[:1]), results)
    ok &= expect_reject('pre-borrow (canonical) local profiles with the same idle', 'compose.profile',
                        lambda: check_composition(compose(canon, counts, idle), sources[:1]), results)
    ok &= expect_reject('idle remainders omitted', 'compose.profile',
                        lambda: check_composition(compose(local, counts, {}), sources[:1]), results)
    ok &= expect_reject('W off by one (66305)', 'compose.mass',
                        lambda: check_mass(H, m, W + 1, T, calls, m * (W + 1) - mass), results)
    ok &= expect_reject('b tampered by +1e-80 (B.json identity)', 'claims.b_identity',
                        lambda: b_identity(b + Fraction(1, 10 ** 80), b_above), results)
    ok &= expect_reject('kappa tampered by +1e-130', 'claims.kappa',
                        lambda: kappa_identity(kappa + Fraction(1, 10 ** 130), b), results)
    ok &= expect_reject('surcharge charged on native b (model control of code/assemble.py)', 'moment.accept',
                        lambda: require_accept(cons, b, 'b with surcharge'), results)
    ok &= expect_reject('complex_lower + 1e-90 claimed admissible', 'moment.accept',
                        lambda: require_accept(native, complex_lower + Fraction(1, 10 ** 90), 'endpoint + 1e-90'),
                        results)
    ok &= expect_reject('log 2 by 10 atanh terms without the remainder bound', 'evaluator.log2_crosscheck',
                        lambda: log2_crosscheck(tuple(2 * v for v in atanh_enclosure(1, 3, terms=10, tail=False)), l2b),
                        results)
    # same truncation with the remainder bound is accepted (the remainder is what makes it sound)
    log2_crosscheck(tuple(2 * v for v in atanh_enclosure(1, 3, terms=10, tail=True)), l2b)
    ok &= expect_reject('exp(log 2) by 3 Taylor terms without the remainder bound', 'evaluator.exp_log2',
                        lambda: exp_log2_check(exp_enclosure(l2[0], l2[1], terms=3, tail=False)), results)
    exp_log2_check(exp_enclosure(l2[0], l2[1], terms=3, tail=True))
    bad = bytearray(raw['PROFILE.json'])
    bad[2] ^= 1
    ok &= expect_reject('one flipped bit in PROFILE.json', 'pin', lambda: verify_pin('PROFILE.json', bytes(bad)),
                        results)
    receipt['negative_controls'] = results
    receipt['positive_mutations_accepted'] = [
        'log 2 by the same 10 atanh terms WITH the remainder bound overlaps the reference enclosure',
        'exp(log 2) by the same 3 Taylor terms WITH the remainder bound encloses 2']
    receipt['controls_ok'] = bool(ok)
    print('negative controls: %d/%d rejected by their targeted checks' % (
        sum(1 for x in results if x['ok']), len(results)), flush=True)
    for x in results:
        print('  %s %s -> %s' % ('OK  ' if x['ok'] else 'BAD ', x['name'], x['rejected_by']), flush=True)
    need(ok, 'controls', 'a negative control was not rejected by its targeted check')

    receipt['findings'] = [
        'Global profile recomposed from the task-A recounted local profiles and the task-B recounted idle '
        'remainders: 249 P_gauge44 + 417 P_extra + idle = %s; equal to PROFILE.json, new/PROFILE.json, '
        'new/SPEC.json, outer/B.json and outer/LEDGER.json. Mass %d = 72*66304 + 64*666; the second term is the '
        'mass of the 8 rank-8 COPY children per call (W - D = 576 T).' % (plain(H), mass),
        'Native moment root (no surcharge, as the T74 assembly prices the complex endpoint) lies in [%s, %s] '
        '(width 1e-%d), inside (complex_lower, complex_lower + 1e-90): the package endpoint certificate is '
        'reproduced. b = complex_lower - 1e-100 is admissible (mu(b) < 1, root - b in %s) and agrees with the '
        'package enclosure of mu(b) in outer/LEDGER.json.' % (dec(r_lo, DIG), dec(r_hi, DIG), DIG,
                                                              interval(gap_lo, gap_hi)),
        'Task bracket: mu(%s) < 1 < mu(%s), width 1e-21, contains b.' % (dec(b_lo, 21), dec(b_hi, 21)),
        'Conservative side (surcharge 32 m N m^a / (10^16 W)): root in [%s...], SPEC conservative_complex_lower '
        'accepted and +1e-90 rejected; native b is rejected under the surcharge.' % dec(c_lo, DIG)[:45],
        'Claimed kappa = floor_1e-136((1 - 2e-100)(b - 1e-100)) - 1e-112 exactly (arithmetic only).',
        'Top-level PRICE.json and evidence/ASSEMBLY.json carry an older pre-borrow price (native endpoint %s); they '
        'do not price the borrowed profile (their endpoints are reproduced here as a positive control).' % (
            asm['complex_decimal'],),
    ]
    receipt['not_checked'] = [
        'The outer lemmas (PR1673 capped phase-cell fusion, PR1786 fine primes, PR1758 interiors, union schedule), '
        'the bit endpoint and its PR589 supplier, and the bootstrap: only the arithmetic link kappa(b) is checked.',
        'Where the 76 private zero buffers per call live. The moment uses only the rank profile, m and W; under '
        'task B\'s dedicated-family charge for the buffers none of these changes. If the buffers instead had to be '
        'hosted inside idle children, the idle remainders and hence the root would change; that model is not '
        'evaluated here.',
        'Native lowering / invoice / precision-tape obligations; the all-size assumptions of the package.',
    ]
    receipt['summary'] = dict(root_lo=dec(r_lo, DIG), root_hi=dec(r_hi, DIG), b=dec(b, 100),
                              b_lo=dec(b_lo, 21), b_hi=dec(b_hi, 21))
    return dict(r_lo=r_lo, r_hi=r_hi, b=b, controls=len(results), t=time.time() - t0)


def main():
    ap = argparse.ArgumentParser(description='Independent price check of PR2269 (global profile + moment root)')
    ap.add_argument('--repo', default=DEFAULT_REPO, help='git checkout containing commit %s' % COMMIT)
    ap.add_argument('--blob-dir', default=None, help='exported package copy, DIR/<package-relative path>')
    ap.add_argument('--out', nargs='?', const=os.path.join(HERE, RECEIPT_NAME), default=None,
                    help='write the JSON receipt (default %s next to this script)' % RECEIPT_NAME)
    args = ap.parse_args()
    if args.out is not None and os.path.dirname(os.path.abspath(args.out)) != HERE:
        print('--out must name a file next to this script (%s)' % HERE)
        print(FAIL_LINE)
        return 2
    receipt = dict(checker='price_check.py', object=dict(pr=2269, commit=COMMIT, package=PKG),
                   python=sys.version.split()[0],
                   scope='task C: global profile composition and exact moment-root bracket of the native complex '
                         'saving b',
                   credits='PR2269 jeremykothe2; PR2226 Cinna Davis / 1337isnot1337; PR2260 Dugongue; T74 lineage '
                           'PR1319/PR1297 (Rohan Arun), PR1625 (mdumitrean), pivot-554 kernel; PR547/548/559 moment '
                           'engines; icekylinx and Zhihao Chen (jacklightChen) / eumemic checker lineage. Prepared with substantial AI '
                           'assistance (Claude Code, Anthropic); Apache-2.0.')
    ok = True
    info = None
    t0 = time.time()
    try:
        info = run(args, receipt)
    except Reject as e:
        ok = False
        receipt['failure'] = str(e)
        print('FAILED: %s' % e, flush=True)
    except Exception as e:   # task A/B failures and malformed input: report, never pass
        ok = False
        receipt['failure'] = '%s: %s' % (type(e).__name__, e)
        print('FAILED: %s: %s' % (type(e).__name__, e), flush=True)
    receipt['model'] = __doc__.split('MODEL (stated precisely; also written to the receipt field "model").')[1].strip()
    receipt['result'] = PASS_LINE if ok else FAIL_LINE
    print('elapsed %.1f s' % (time.time() - t0))
    if args.out is not None:
        with open(args.out, 'w') as fh:
            json.dump(receipt, fh, indent=1, sort_keys=True)
            fh.write('\n')
        print('receipt written: %s' % args.out)
    if ok:
        print('%s root=[%s..., %s...] b_admissible=1 task_bracket=[%s,%s] controls=%d' % (
            PASS_LINE, receipt['summary']['root_lo'][:34], receipt['summary']['root_hi'][:34],
            receipt['summary']['b_lo'], receipt['summary']['b_hi'], info['controls']))
        return 0
    print(FAIL_LINE)
    return 1


if __name__ == '__main__':
    sys.exit(main())
