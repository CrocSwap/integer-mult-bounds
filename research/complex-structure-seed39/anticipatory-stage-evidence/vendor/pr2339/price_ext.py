#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pricing harness for an extended T74 (or T8) complex supplier under explicit idle-refill models.

Question it answers: if the two T74 pivot-566+554 borrow words of PR2269 (gauge44 and extra) are
replaced by extended words P_gauge44', P_extra' (for example with PR2226-style LOW / anticipatory
aliases added), what complex saving b does the native moment certify, given that the owner fill
(and hence the idle remainder profile) has NOT been rebuilt?  The idle profile is therefore modelled,
not constructed.  Every number printed for a model is a MODEL PRICE, not a certified supplier and
not a kappa claim.  Only the positive controls price realized (constructed) profiles.

Credit: PR2226 (Cinna Davis / 1337isnot1337, with OpenAI Codex) for anticipatory dirty borrowing and
the 80-alias (48 high + 32 low) T8 word whose profile defines the demo delta; PR2269 (Jeremy Kothe /
jeremykothe2) for the T74 borrow43 words, fill, profile and the claimed b; PR2260 (Dugongue) for the
T8 44-high selective-borrowing supplier, its fill and profile; PR2312 for the current top open claim
used as a reference value only; the T74 lineage (PR1319/PR1297 Rohan Arun, PR1625 mdumitrean,
pivot-554 kernel) and the retained PR547/PR548/PR559 moment engines.  The certified evaluator is
adapted from our own iteration-3 checker (fork commit 4a2f20ea339e30348448096ca789d0efe55df9bb,
research/t74-borrow43-independent-check/price_check.py, Apache-2.0, same authors).  No PR code is
imported or run; PR constants are written here and can be re-checked against the pinned PR blobs
with the `sources` subcommand.

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.

Usage (Python 3.10+, standard library only):
  python3 -I -B price_ext.py controls [--out]          positive/negative controls (exact reproduction)
  python3 -I -B price_ext.py price INPUT.json [--digits D] [--out]
  python3 -I -B price_ext.py demo [--digits D] [--out]  T8-transferred delta proxy on both T74 words
  python3 -I -B price_ext.py sources [--repo PATH]      re-read every hard-coded PR constant from git
  python3 -I -B price_ext.py all [--out]                sources + controls + demo

INPUT.json (see demo-t8-delta-proxy.json):
  {"family": "T74" | "T8", "label": "...",
   "providers": {"gauge44": {"profile": {"1": n1, ...}, "helpers": h, "helper_width_sum": w}, "extra": {...}}}
  or, instead of explicit profiles, "delta": {"1": d1, ...} (applied to every base word) or
  "delta": {"gauge44": {...}, "extra": {...}}; "helpers" may then be given per provider or once.
  Optional "idle": {...}: an explicitly constructed idle profile, priced as model X (no modelling).

MODEL (stated precisely; also written to receipts).
 1. Composition (as in PR2269 code/assemble.py and PR2260 arithmetic/verify.py):
       H = sum_p calls_p * P_p + idle,   T74: 249 P_gauge44 + 417 P_extra + idle,  T8: 72 P + idle.
 2. Mass identity: mass(H) = m W - D is invariant (T74: 73*66304 - 23680 = 4816512; T8: 73*7168 - 2560
    = 520704).  Hence idle mass' = (m W - D) - sum_p calls_p mass(P_p'), and the extra freed mass relative
    to the realized base is E = idle mass' - idle mass(base).  If helper_width_sum is given, the local
    identity mass(P) = 1856 + sum of helper widths is checked (it holds for PR2269, PR2260, PR2226 and
    the R492 parent).
 3. Idle-refill models (base = the realized idle of the record being extended; for T74 that is
    PR2269's {1:23976, 3:8673, 5:813, 7:150, 48:24479}).  For E >= 0:
      F  favorable:   base + floor(E/48) children of rank 48 + one child of rank E mod 48 (if nonzero).
      C  calibrated:  shares s_r derived exactly from a realized (pre, post) idle pair:
                      delta_r = r (post_r - pre_r), E_ref = sum_r delta_r,  s_48 = delta_48 / E_ref,
                      small ranks r < 48 with delta_r > 0 share 1 - s_48 in proportion to delta_r.
                      (For T74, pre = {48:22748} = PR2269's pre-borrow idle, every delta_r >= 0 and
                      s_r = delta_r / E_ref exactly: s_48 = 83088/138198, s_1 = 23976/138198,
                      s_3 = 26019/138198, s_5 = 4065/138198, s_7 = 1050/138198.)
                      Allocation: n_r += floor(E s_r / r); the leftover mass (< 64) becomes rank-1
                      children (conservative rounding).  With E = E_ref on the pre base this reproduces
                      the post profile exactly (control).
      C8 sensitivity: same rule calibrated on the T8 transition R492 hosted parent -> PR2260
                      (net top-rank share 9792/19080; the parent's small residues were repacked).
      P  pessimistic: base + E children of rank 1.
    For E < 0 (supplier heavier than the base): F removes mass from the smallest idle children first,
    P from the rank-48 children first (shrinking the last touched child), C/C8 remove ceil(|E| s_r / r)
    children per rank where present, take any shortfall from the largest children and return any
    over-removed mass as rank-1 children.
    Not modelled: changes of the window/owner geometry, the 76 private cleanup zero buffers per call
    (outside the moment under PR2269's dedicated-family charge), any re-optimised fill.
 4. Moment (native complex side, no surcharge; the side of PR2269 outer/B.json b and PR2260 b):
       mu(a) = sum_r n_r (r/m)^(1-a) / W;   root rho: the unique a > 0 with mu(a) = 1.
    Optional conservative side (--conservative): mu(a) + 32 m N m^a / (10^16 W), N = number of children.
    b_D(H) := floor of rho on the decimal grid 10^-D, certified by mu(b_D) < 1 < mu(b_D + 10^-D).
    PR2269 packages b = b_90 - 10^-100; PR2260 packages b = 8417/5000000 (accepted on both sides).
 5. Certified evaluation (exact integers on the grid 2^-PREC, directed rounding; iteration-3 evaluator):
    log via atanh series with the remainder bound z^(2N+1)/((2N+1)(1-z^2)); exp by its Taylor series with
    the remainder bound x^N/N! (N+1)/(N+1-x); comparisons with 1 are exact rational comparisons.
 6. Gains are b_D(model) - reference, an exact rational known to lie within 10^-D below the model's root
    gain.  References: PR2269 claimed b (= complex_lower - 1e-100; its outer-ledger kappa differs from b
    by about 2e-100) and the PR2312 claimed kappa 0.001696891067241618 (reference value only, not
    re-derived).  The bit endpoint 0.001733427039589844234749 (PR2269 ledger) caps any kappa: a model
    b above it would be bit-bound (flagged, never the case in the demo).
"""

import sys

if sys.flags.optimize:
    sys.stdout.write('refusing to run under python -O\n')
    sys.exit(2)

import argparse
import gzip
import hashlib
import json
import os
import subprocess
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO = os.path.dirname(os.path.dirname(HERE))
PASS_LINE = 'PASS_T74_EXT_PRICE_HARNESS'
FAIL_LINE = 'FAIL_T74_EXT_PRICE_HARNESS'
CREDITS = ('PR2226 Cinna Davis / 1337isnot1337 (anticipatory dirty borrowing, 80-alias T8 word); PR2269 '
           'Jeremy Kothe / jeremykothe2 (T74 borrow43 words, fill, b); PR2260 Dugongue (T8 44-high supplier, fill); '
           'PR2312 (reference claim only); T74 lineage PR1319/PR1297 (Rohan Arun), PR1625 (mdumitrean), pivot-554 '
           'kernel; PR547/548/559 moment engines. Evaluator adapted from our own iteration-3 price_check.py '
           '(fork commit 4a2f20ea). Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.')


class HarnessError(Exception):
    def __init__(self, check, msg):
        Exception.__init__(self, '[%s] %s' % (check, msg))
        self.check = check
        self.msg = msg


def need(cond, check, msg):
    if not cond:
        raise HarnessError(check, msg)


# ----------------------------------------------------------------------------
# PR constants (written from the PR packages; `sources` re-reads every one of them from git)
# ----------------------------------------------------------------------------

PR2269_COMMIT = 'b479fc5567bc09ab9185bffe89b62594f36d74e5'
PR2269_PKG = 'research/gmx-t74-borrow43/'
PR2260_COMMIT = 'fde6b107e26a14da5bac5b66913c914708ea6901'
PR2260_PKG = 'research/selective-borrowing-kappa/'
PR2226_COMMIT = 'dacaf3d81f1936bb55b8454b1244e5d014272754'
PR2226_PKG = 'research/anticipatory-dirty-borrowing/'

B_2269 = Fraction('16962471390584742207696225394800943861284603706821716607210815258272261945561178592716719999999999/'
                  '1' + '0' * 100)
COMPLEX_LOWER_2269 = Fraction('212030892382309277596202817435011798266057546335271457590135190728403274319514732408959/'
                              '125' + '0' * 87)
KAPPA_2312 = Fraction('0.001696891067241618')
BIT_LOWER = Fraction('1733427039589844234749/1' + '0' * 24)

FAMILIES = {
    'T74': dict(
        name='T74', source='PR2269 head %s, %s' % (PR2269_COMMIT[:8], PR2269_PKG),
        m=73, W=66304, deficit=23680, calls={'gauge44': 249, 'extra': 417}, fixed_per_call=1856, top=48,
        base=dict(label='PR2269 realized (43 high aliases, 437 helpers, window-exact owner fill)',
                  local={'gauge44': {1: 2351, 2: 501, 3: 414, 4: 129, 5: 42, 8: 8},
                         'extra': {1: 2339, 2: 509, 3: 418, 4: 125, 5: 42, 8: 8}},
                  helpers={'gauge44': 437, 'extra': 437}, width_sum={'gauge44': 3529, 'extra': 3529},
                  idle={1: 23976, 3: 8673, 5: 813, 7: 150, 48: 24479}),
        pre=dict(label='PR2269 pre-borrow (top-level SPEC.json, 480 helpers; stale assembly, 1e-24 endpoint)',
                 local={'gauge44': {1: 2346, 2: 504, 3: 414, 4: 130, 5: 82, 8: 8},
                        'extra': {1: 2338, 2: 512, 3: 418, 4: 126, 5: 82, 8: 8}},
                 helpers={'gauge44': 480, 'extra': 480}, width_sum={'gauge44': 3734, 'extra': 3738},
                 idle={48: 22748},
                 complex_lower=Fraction('839835897752368810771/5' + '0' * 23), grid=24),
        claim=dict(b=B_2269, complex_lower=COMPLEX_LOWER_2269, grid=90,
                   global_profile={1: 1584738, 2: 337002, 3: 286065, 4: 84246, 5: 28785, 7: 150, 8: 5328,
                                   48: 24479})),
    'T8': dict(
        name='T8', source='PR2260 head %s, %s' % (PR2260_COMMIT[:8], PR2260_PKG),
        m=73, W=7168, deficit=2560, calls={'gauge44': 72}, fixed_per_call=1856, top=48,
        base=dict(label='PR2260 realized (44 high aliases, 436 helpers, multi-bin repacking)',
                  local={'gauge44': {1: 2424, 2: 418, 3: 429, 4: 141, 5: 42, 8: 8}},
                  helpers={'gauge44': 436}, width_sum={'gauge44': 3529},
                  idle={1: 1724, 3: 20, 5: 1469, 6: 18, 7: 494, 32: 11, 39: 7, 48: 2493}),
        pre=dict(label='PR2260 actual hosted parent R492 (owners/inputs/HOSTED-PARENT.json.gz)',
                 local={'gauge44': {1: 2514, 2: 404, 3: 448, 4: 160, 5: 56, 8: 8}},
                 helpers={'gauge44': 492}, width_sum={'gauge44': 3794},
                 idle={1: 85, 2: 76, 3: 173, 7: 7, 8: 6, 12: 13, 16: 33, 19: 1, 20: 2, 28: 4, 32: 62, 36: 1,
                       40: 1, 44: 6, 48: 2289}),
        claim=dict(b=Fraction(8417, 5000000), grid=7,
                   global_profile={1: 176252, 2: 30096, 3: 30908, 4: 10152, 5: 4493, 6: 18, 7: 494, 8: 576,
                                   32: 11, 39: 7, 48: 2493})),
}

# PR2226 (T8, 80 aliases = 48 high + 32 low, 400 helpers): RESULT.json replay.local_profile
PR2226_LOCAL = {1: 2382, 2: 445, 3: 406, 4: 128, 5: 42, 8: 8}
PR2226_HELPERS = 400
# T8 transfer delta = PR2226 - PR2260 local profile (both on the selected T8 word)
T8_DELTA = {1: -42, 2: 27, 3: -23, 4: -13}

CALIBRATIONS = {'C': 'T74', 'C8': 'T8'}   # model name -> family whose (pre -> base) idle transition calibrates it
MODEL_ORDER = ['F', 'C', 'C8', 'P']
MODEL_TEXT = {
    'F': 'favorable: base idle + all extra mass in rank-48 children (+ one remainder child)',
    'C': 'calibrated on T74 (PR2269 pre-borrow {48:22748} -> PR2269 realized idle split by rank)',
    'C8': 'sensitivity: calibrated on T8 (R492 hosted parent -> PR2260 realized idle, net top-rank share)',
    'P': 'pessimistic: base idle + all extra mass in rank-1 children',
    'X': 'explicit idle profile supplied by the input (constructed fill, no modelling)',
}


# ----------------------------------------------------------------------------
# Profiles
# ----------------------------------------------------------------------------

def clean(prof):
    return dict((r, prof[r]) for r in sorted(prof) if prof[r])


def plain(prof):
    return dict((str(r), prof[r]) for r in sorted(prof) if prof[r])


def mass_of(prof):
    return sum(r * n for r, n in prof.items())


def int_profile(mapping, what, allow_negative=False):
    out = {}
    need(isinstance(mapping, dict), 'input', what + ': profile must be a JSON object')
    for k, v in mapping.items():
        need(str(int(k)) == str(k).strip() and int(k) > 0, 'input', '%s: bad rank %r' % (what, k))
        need(type(v) is int and (allow_negative or v >= 0), 'input', '%s: bad count %r for rank %s' % (what, v, k))
        out[int(k)] = out.get(int(k), 0) + v
    return out


def add_profiles(*terms):
    out = {}
    for coef, prof in terms:
        for r, n in prof.items():
            out[r] = out.get(r, 0) + coef * n
    return clean(out)


def compose(fam, local, idle):
    terms = [(fam['calls'][p], local[p]) for p in sorted(fam['calls'])]
    return add_profiles(*(terms + [(1, idle)]))


def total_mass(fam):
    return fam['m'] * fam['W'] - fam['deficit']


def check_global(fam, H, what):
    m = fam['m']
    need(all(type(r) is int and 0 < r < m and type(n) is int and n > 0 for r, n in H.items()), 'compose',
         what + ': every child must have 0 < rank < m and positive count')
    need(mass_of(H) == total_mass(fam), 'compose.mass', '%s: mass %d != m W - D = %d' % (
        what, mass_of(H), total_mass(fam)))
    need(m * m > 2 * max(H) ** 2, 'compose.halving', what + ': halving guard m^2 > 2 maxchild^2 fails')


# ----------------------------------------------------------------------------
# Idle-refill models
# ----------------------------------------------------------------------------

def calibration_shares(pre, post, top):
    """Exact rank shares of the freed mass realized between two idle profiles (rule in MODEL 3)."""
    ranks = sorted(set(pre) | set(post))
    delta = dict((r, r * (post.get(r, 0) - pre.get(r, 0))) for r in ranks)
    e_ref = sum(delta.values())
    need(e_ref > 0, 'calibration', 'calibration pair frees no mass')
    need(all(delta[r] == 0 for r in ranks if r > top), 'calibration', 'idle child above the top rank')
    s_top = Fraction(delta.get(top, 0), e_ref)
    pos = dict((r, delta[r]) for r in ranks if r < top and delta[r] > 0)
    tot = sum(pos.values())
    shares = {top: s_top}
    for r, d in pos.items():
        shares[r] = (1 - s_top) * Fraction(d, tot)
    need(sum(shares.values()) == 1 and all(s >= 0 for s in shares.values()), 'calibration', 'shares do not sum to 1')
    exact = all(delta[r] >= 0 for r in ranks)
    return dict(shares=clean(shares), E_ref=e_ref, delta_mass=clean(delta), all_increments_nonnegative=exact,
                top_share=s_top)


def remove_mass(idle, amount, ascending):
    """Remove `amount` mass from idle children, smallest (ascending) or largest ranks first."""
    out = dict(idle)
    left = amount
    for r in sorted(out, reverse=not ascending):
        while left > 0 and out.get(r, 0) > 0:
            out[r] -= 1
            if r <= left:
                left -= r
            else:
                out[r - left] = out.get(r - left, 0) + 1
                left = 0
        if left == 0:
            break
    need(left == 0, 'model', 'not enough idle mass to absorb a heavier supplier')
    return clean(out)


def model_idle(name, base_idle, E, top, shares=None):
    idle = dict(base_idle)
    if name == 'F':
        if E >= 0:
            q, rem = divmod(E, top)
            idle[top] = idle.get(top, 0) + q
            if rem:
                idle[rem] = idle.get(rem, 0) + 1
            return clean(idle)
        return remove_mass(idle, -E, ascending=True)
    if name == 'P':
        if E >= 0:
            idle[1] = idle.get(1, 0) + E
            return clean(idle)
        return remove_mass(idle, -E, ascending=False)
    if name in ('C', 'C8'):
        need(shares is not None, 'model', 'calibrated model without shares')
        if E >= 0:
            placed = 0
            for r, s in shares.items():
                t = E * s / r
                k = t.numerator // t.denominator          # place at most E s_r in rank r
                idle[r] = idle.get(r, 0) + k
                placed += r * k
            leftover = E - placed
            need(0 <= leftover, 'model', 'calibrated allocation overshoots')
            idle[1] = idle.get(1, 0) + leftover            # rounding remainder -> rank 1 (conservative)
            return clean(idle)
        removed = 0
        for r, s in shares.items():                        # remove at least |E| s_r per rank where present
            t = -E * s / r
            k = min(-(-t.numerator // t.denominator), idle.get(r, 0))
            idle[r] = idle.get(r, 0) - k
            removed += r * k
        if removed < -E:                                   # shortfall (rank absent in the base): top ranks first
            return remove_mass(clean(idle), -E - removed, ascending=False)
        idle[1] = idle.get(1, 0) + (removed + E)           # over-removed mass returned as rank-1 children
        return clean(idle)
    raise HarnessError('model', 'unknown model ' + name)


# ----------------------------------------------------------------------------
# Certified rational enclosures (adapted from our iteration-3 price_check.py)
# ----------------------------------------------------------------------------

PREC = 800
ONE = 1 << PREC
MAX_TERMS = 4 * PREC


def cdiv(a, b):
    return -((-a) // b)


def atanh_enclosure(p, q, terms=None, tail=True):
    """Integers (lo, hi) with lo <= 2^PREC atanh(p/q) <= hi, for 0 <= p/q <= 1/3 (positive series + remainder)."""
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
    """Integers (lo, hi) with lo <= 2^PREC exp(x) <= hi on [xl, xu] / 2^PREC, 0 <= xl <= xu < 2^PREC."""
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


_LOGS = {}


def log_m_over_r(m, r):
    key = (m, r)
    if key not in _LOGS:
        _LOGS[key] = log_enclosure(m, r)
    return _LOGS[key]


class Moment(object):
    """Certified enclosures of mu(a) for one global profile."""

    def __init__(self, H, m, W, surcharge=False):
        need(all(type(r) is int and 0 < r < m and type(n) is int and n > 0 for r, n in H.items()), 'moment',
             'every child must have 0 < rank < m')
        self.H, self.m, self.W, self.surcharge = dict(H), m, W, surcharge
        self.N = sum(H.values())

    def bounds(self, a):
        a = Fraction(a)
        need(a >= 0, 'moment', 'negative saving')
        an, ad = a.numerator, a.denominator
        slo = shi = 0
        for r in sorted(self.H):
            ll, lu = log_m_over_r(self.m, r)
            el, eu = exp_enclosure((an * ll) // ad, cdiv(an * lu, ad))
            slo += self.H[r] * r * el
            shi += self.H[r] * r * eu
        lo = Fraction(slo, self.m * self.W * ONE)
        hi = Fraction(shi, self.m * self.W * ONE)
        if self.surcharge:
            ll, lu = log_m_over_r(self.m, 1)
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

    def floor_root(self, digits, hint=None):
        """(b_D, steps): b_D on the grid 10^-digits with mu(b_D) < 1 < mu(b_D + 10^-digits), both certified.
        A hint (any rational) only narrows the starting bracket after it is itself certified."""
        scale = 10 ** digits
        lo, hi = 0, scale // 100
        need(self.side(Fraction(lo, scale)) < 0, 'moment', 'mu(0) >= 1: no positive saving')
        need(self.side(Fraction(hi, scale)) > 0, 'moment', 'mu(1/100) <= 1')
        steps = 0
        if hint is not None:
            for w in (10 ** max(0, digits - 12), 10 ** max(0, digits - 6)):
                c = int(Fraction(hint) * scale)
                a, b = max(lo, c - w), min(hi, c + w)
                if a < b and self.side(Fraction(a, scale)) < 0 and self.side(Fraction(b, scale)) > 0:
                    lo, hi = a, b
                    steps += 2
                    break
        while hi - lo > 1:
            mid = (lo + hi) // 2
            s = self.side(Fraction(mid, scale))
            steps += 1
            need(s != 0, 'moment.bracket', 'undecided at 10^-%d grid point (raise PREC)' % digits)
            if s < 0:
                lo = mid
            else:
                hi = mid
        return Fraction(lo, scale), steps


def require_side(ev, a, want, what):
    lo, hi = ev.bounds(a)
    if want < 0:
        need(hi < 1, 'moment.accept', '%s: mu(a) < 1 not certified' % what)
    else:
        need(lo > 1, 'moment.reject', '%s: mu(a) > 1 not certified' % what)
    return lo, hi


# ----------------------------------------------------------------------------
# Display (display only)
# ----------------------------------------------------------------------------

def sci(x, sig=20):
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
    k = y.numerator // y.denominator
    ds = str(k)
    e += len(ds) - sig
    return '%s%s.%sE%+d' % ('-' if neg else '', ds[0], ds[1:sig], e)


def dec(x, digits):
    y = Fraction(x) * 10 ** digits
    need(y.denominator == 1, 'display', 'not on the decimal grid')
    n = y.numerator
    s = str(abs(n)).rjust(digits + 1, '0')
    return ('-' if n < 0 else '') + s[:-digits] + '.' + s[-digits:]


def pct(x, ref):
    return '%+.4f%%' % float(100 * Fraction(x) / ref)


# ----------------------------------------------------------------------------
# Pricing
# ----------------------------------------------------------------------------

def base_check(fam):
    for state in ('base', 'pre'):
        st = fam[state]
        H = compose(fam, st['local'], st['idle'])
        check_global(fam, H, '%s %s' % (fam['name'], state))
        for p in fam['calls']:
            need(mass_of(st['local'][p]) == fam['fixed_per_call'] + st['width_sum'][p], 'local.identity',
                 '%s %s %s: local mass != 1856 + helper widths' % (fam['name'], state, p))
    need(compose(fam, fam['base']['local'], fam['base']['idle']) == fam['claim']['global_profile'], 'compose',
         fam['name'] + ': base composition differs from the claimed global profile')


def all_shares():
    out = {}
    for model, fname in CALIBRATIONS.items():
        f = FAMILIES[fname]
        out[model] = calibration_shares(f['pre']['idle'], f['base']['idle'], f['top'])
    return out


def resolve_input(spec):
    """Normalise an input spec to (family, local profiles, helpers, width sums, explicit idle, label)."""
    fname = spec.get('family', 'T74')
    need(fname in FAMILIES, 'input', 'family must be T74 or T8')
    fam = FAMILIES[fname]
    base = fam['base']
    local, helpers, widths = {}, {}, {}
    if 'delta' in spec:
        d = spec['delta']
        per = dict((p, int_profile(d[p], 'delta ' + p, True)) for p in fam['calls']) if all(
            p in d for p in fam['calls']) else dict((p, int_profile(d, 'delta', True)) for p in fam['calls'])
        for p in fam['calls']:
            local[p] = add_profiles((1, base['local'][p]), (1, per[p]))
            need(all(n >= 0 for n in local[p].values()), 'input', 'delta makes a count negative for ' + p)
        hp = spec.get('helpers')
        for p in fam['calls']:
            helpers[p] = hp.get(p) if isinstance(hp, dict) else hp
    else:
        prov = spec.get('providers', {})
        need(set(prov) == set(fam['calls']), 'input', 'providers must be exactly %s' % sorted(fam['calls']))
        for p in fam['calls']:
            local[p] = clean(int_profile(prov[p]['profile'], 'profile ' + p))
            helpers[p] = prov[p].get('helpers')
            if 'helper_width_sum' in prov[p]:
                widths[p] = prov[p]['helper_width_sum']
    for p in fam['calls']:
        need(all(0 < r < fam['m'] for r in local[p]), 'input', 'local rank outside (0, m) for ' + p)
        if p in widths:
            need(mass_of(local[p]) == fam['fixed_per_call'] + widths[p], 'local.identity',
                 '%s: local mass %d != %d + helper widths %d' % (p, mass_of(local[p]), fam['fixed_per_call'], widths[p]))
    idle = clean(int_profile(spec['idle'], 'idle')) if 'idle' in spec else None
    return fam, local, helpers, widths, idle, spec.get('label', '(unlabelled)')


def price_profiles(fam, local, digits, models=None, base=None, explicit_idle=None, conservative=False,
                   shares=None, hint=None):
    """Price new local profiles on `base` (default: the family's realized base) under each model."""
    base = fam['base'] if base is None else base
    models = MODEL_ORDER if models is None else models
    shares = all_shares() if shares is None else shares
    local_mass = sum(fam['calls'][p] * mass_of(local[p]) for p in fam['calls'])
    idle_mass = total_mass(fam) - local_mass
    need(idle_mass >= 0, 'compose.mass', 'local words pay more than m W - D')
    E = idle_mass - mass_of(base['idle'])
    rows = []
    todo = [(mn, None) for mn in models]
    if explicit_idle is not None:
        need(mass_of(explicit_idle) == idle_mass, 'compose.mass', 'explicit idle mass %d != required %d' % (
            mass_of(explicit_idle), idle_mass))
        todo.append(('X', explicit_idle))
    for mn, given in todo:
        idle = given if given is not None else model_idle(mn, base['idle'], E, fam['top'],
                                                         shares[mn]['shares'] if mn in shares else None)
        H = compose(fam, local, idle)
        check_global(fam, H, '%s model %s' % (fam['name'], mn))
        ev = Moment(H, fam['m'], fam['W'])
        b, steps = ev.floor_root(digits, hint)
        row = dict(model=mn, text=MODEL_TEXT[mn], idle=plain(idle), idle_children=sum(idle.values()),
                   global_children=sum(H.values()), max_child=max(H), b=dec(b, digits), b_rational=b,
                   bisection_steps=steps, bit_bound=b >= BIT_LOWER)
        if conservative:
            cb, _ = Moment(H, fam['m'], fam['W'], surcharge=True).floor_root(digits, hint)
            row['b_conservative'] = dec(cb, digits)
        rows.append(row)
    return dict(local_mass_total=local_mass, idle_mass=idle_mass, extra_freed_mass=E, rows=rows,
                base_label=base['label'])


def gain_lines(rows, digits):
    out = []
    for row in rows:
        b = row['b_rational']
        g69, g12 = b - B_2269, b - KAPPA_2312
        row['gain_vs_pr2269'] = sci(g69)
        row['gain_vs_pr2269_pct'] = pct(g69, B_2269)
        row['gain_vs_pr2312'] = sci(g12)
        row['gain_vs_pr2312_pct'] = pct(g12, KAPPA_2312)
        out.append('  %-2s b_%d = %s  gain vs #2269 %s (%s)  vs #2312 %s (%s)%s' % (
            row['model'], digits, row['b'][:2 + min(digits, 24)] + ('...' if digits > 24 else ''),
            sci(g69, 8), row['gain_vs_pr2269_pct'], sci(g12, 8),
            row['gain_vs_pr2312_pct'], '  [BIT-BOUND]' if row['bit_bound'] else ''))
    return out


def strip(rows):
    return [dict((k, v) for k, v in r.items() if k != 'b_rational') for r in rows]


# ----------------------------------------------------------------------------
# Subcommands
# ----------------------------------------------------------------------------

def git_blob(repo, commit, path):
    got = subprocess.run(['git', '-C', repo, 'show', '%s:%s' % (commit, path)], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    need(got.returncode == 0, 'sources', 'cannot read %s:%s in %s' % (commit[:8], path, repo))
    data = got.stdout
    h = hashlib.sha1(b'blob %d\0' % len(data))
    h.update(data)
    return data, h.hexdigest()


def run_sources(repo, receipt):
    """Re-read every hard-coded PR constant from the pinned PR commits."""
    rec = {}

    def load(commit, pkg, rel, gz=False):
        data, blob = git_blob(repo, commit, pkg + rel)
        rec['%s:%s%s' % (commit[:8], pkg, rel)] = dict(git_blob=blob, sha256=hashlib.sha256(data).hexdigest())
        return json.loads(gzip.decompress(data) if gz else data)

    def ip(x):
        return clean(dict((int(k), v) for k, v in x.items()))

    T74, T8 = FAMILIES['T74'], FAMILIES['T8']
    spec = load(PR2269_COMMIT, PR2269_PKG, 'new/SPEC.json')
    Bj = load(PR2269_COMMIT, PR2269_PKG, 'outer/B.json')
    top = load(PR2269_COMMIT, PR2269_PKG, 'SPEC.json')
    X = spec['expected']
    need(Fraction(Bj['b']) == B_2269 and Fraction(X['complex_lower']) == COMPLEX_LOWER_2269, 'sources', 'PR2269 b')
    need(ip(Bj['profile']) == T74['claim']['global_profile'] == ip(X['global_profile']), 'sources', 'PR2269 profile')
    need(ip(X['idle_remainder_profile']) == T74['base']['idle'], 'sources', 'PR2269 idle')
    need(X['provider_counts'] == T74['calls'] and X['rank_mass'] == total_mass(T74) and X['live'] == T74['W'] ==
         Bj['live'] and spec['geometry']['dimension'] == T74['m'], 'sources', 'PR2269 geometry')
    for p in T74['calls']:
        cc = spec['providers'][p]['complete_contract']
        need(ip(spec['providers'][p]['expected_profile']) == T74['base']['local'][p] == ip(cc['paid_profile']),
             'sources', 'PR2269 local ' + p)
        need(cc['helpers'] == T74['base']['helpers'][p] and sum(cc['widths']) == T74['base']['width_sum'][p],
             'sources', 'PR2269 helpers ' + p)
    TX = top['expected']
    need(ip(TX['idle_remainder_profile']) == T74['pre']['idle'] and Fraction(TX['complex_lower']) ==
         T74['pre']['complex_lower'], 'sources', 'PR2269 pre-borrow idle / endpoint')
    for p in T74['calls']:
        need(ip(top['providers'][p]['expected_profile']) == T74['pre']['local'][p] and
             top['providers'][p]['complete_contract']['helpers'] == 480 and
             sum(top['providers'][p]['complete_contract']['widths']) == T74['pre']['width_sum'][p], 'sources',
             'PR2269 pre-borrow local ' + p)
    ar = load(PR2260_COMMIT, PR2260_PKG, 'arithmetic/EXPECTED.json')
    ow = load(PR2260_COMMIT, PR2260_PKG, 'owners/EXPECTED.json')
    fw = load(PR2260_COMMIT, PR2260_PKG, 'local/data/forward.json')
    hp = load(PR2260_COMMIT, PR2260_PKG, 'owners/inputs/HOSTED-PARENT.json.gz', gz=True)
    need(Fraction(ar['certified_complex_saving']) == T8['claim']['b'], 'sources', 'PR2260 b')
    need(ip(ar['profile']) == T8['claim']['global_profile'] == ip(ow['profile']), 'sources', 'PR2260 profile')
    need(ip(ow['idle']) == T8['base']['idle'], 'sources', 'PR2260 idle')
    need(ar['calls'] == T8['calls']['gauge44'] and ar['live'] == T8['W'] and ar['rank_mass'] == total_mass(T8) and
         ar['deficit'] == T8['deficit'] and ar['helpers_per_call'] == T8['base']['helpers']['gauge44'],
         'sources', 'PR2260 geometry')
    need(ip(fw['local_profile']) == T8['base']['local']['gauge44'] and len(fw['helper_widths']) == 436 and
         sum(fw['helper_widths'].values()) == T8['base']['width_sum']['gauge44'], 'sources', 'PR2260 local')
    g = hp['local_providers']['gauge44']
    pidle = {}
    for c in hp['idle_children']:
        pidle[c['rank']] = pidle.get(c['rank'], 0) + c.get('replicas', 1)
    need(clean(pidle) == T8['pre']['idle'], 'sources', 'R492 parent idle')
    for o in ('forward', 'backward'):
        need(ip(g['local_program_checks'][o]['paid_profile']) == T8['pre']['local']['gauge44'], 'sources',
             'R492 parent local ' + o)
    need(int(g['R']) == len(g['widths']) == 492 and sum(g['widths']) == T8['pre']['width_sum']['gauge44'] and
         hp['live'] == T8['W'] and hp['m'] == T8['m'], 'sources', 'R492 parent helpers')
    res = load(PR2226_COMMIT, PR2226_PKG, 'RESULT.json')
    need(ip(res['replay']['local_profile']) == PR2226_LOCAL and res['replay']['local_mass'] == mass_of(PR2226_LOCAL)
         and res['audit']['aliases'] == 80 and res['audit']['low_aliases'] == 32, 'sources', 'PR2226 local')
    need(add_profiles((1, PR2226_LOCAL), (-1, T8['base']['local']['gauge44'])) == T8_DELTA, 'sources', 'T8 delta')
    receipt['sources'] = dict(repo='<repository root>', blobs=rec, result='every hard-coded constant equals the pinned PR blobs')
    print('sources: %d PR blobs read at pinned commits; all hard-coded constants agree' % len(rec), flush=True)


def run_controls(receipt, digits_model=40):
    t0 = time.time()
    res = {}
    # evaluator self-tests (from iteration 3)
    l2 = log2_enclosure()
    a1, a2, a3 = atanh_enclosure(1, 26), atanh_enclosure(1, 4801), atanh_enclosure(1, 8749)
    l2b = (18 * a1[0] - 2 * a2[1] + 8 * a3[0], 18 * a1[1] - 2 * a2[0] + 8 * a3[1])
    need(max(l2[0], l2b[0]) <= min(l2[1], l2b[1]), 'evaluator', 'two log 2 enclosures are disjoint')
    e2 = exp_enclosure(l2[0], l2[1])
    need(e2[0] <= 2 * ONE <= e2[1], 'evaluator', 'exp(log 2) misses 2')
    bad = tuple(2 * v for v in atanh_enclosure(1, 3, terms=10, tail=False))
    need(not max(bad[0], l2b[0]) <= min(bad[1], l2b[1]), 'evaluator', 'truncated log 2 without remainder not caught')
    res['evaluator'] = 'log2 two formulas overlap; exp(log 2) encloses 2; truncation without remainder is caught'
    for fname in ('T74', 'T8'):
        base_check(FAMILIES[fname])
    res['compositions'] = ('T74: 249 P_g + 417 P_e + idle = PR2269 B.json profile; T8: 72 P + idle = PR2260 '
                           'EXPECTED profile; pre states (PR2269 pre-borrow, R492 parent) have mass m W - D; '
                           'local mass = 1856 + helper widths in all four states')
    print('controls: evaluator self-tests and exact compositions PASS', flush=True)

    # (1) PR2269 claimed b reproduced exactly: b = floor_90(root) - 1e-100
    T74 = FAMILIES['T74']
    H = compose(T74, T74['base']['local'], T74['base']['idle'])
    ev = Moment(H, T74['m'], T74['W'])
    b90, steps = ev.floor_root(90)
    need(b90 == COMPLEX_LOWER_2269, 'control.pr2269', 'floor_90(root) %s != PR2269 complex_lower' % dec(b90, 90))
    need(b90 - Fraction(1, 10 ** 100) == B_2269, 'control.pr2269', 'derived b != PR2269 b')
    require_side(ev, B_2269, -1, 'PR2269 b')
    require_side(ev, B_2269 + Fraction(1, 10 ** 15), 1, 'PR2269 b + 1e-15')
    res['pr2269'] = dict(floor_90_root=dec(b90, 90), derived_b='floor_90(root) - 1e-100 = PR2269 outer/B.json b '
                         'exactly', bisection_steps=steps)
    print('control PR2269: floor_1e-90(root) = complex_lower, so b = %s... reproduced exactly (%d steps)' % (
        dec(B_2269, 100)[:40], steps), flush=True)
    # every model with the base profiles has E = 0 and returns the realized idle
    for mn in MODEL_ORDER:
        idle = model_idle(mn, T74['base']['idle'], 0, 48, all_shares()[mn]['shares'] if mn in CALIBRATIONS else None)
        need(idle == T74['base']['idle'], 'control.models', 'model %s changes the idle at E = 0' % mn)
    pr = price_profiles(T74, T74['base']['local'], 30)
    need(all(r['b_rational'] == Fraction((COMPLEX_LOWER_2269 * 10 ** 30).__floor__(), 10 ** 30) for r in pr['rows']),
         'control.models', 'models with PR2269 own profiles do not reproduce its b')
    res['pr2269_models_E0'] = 'F, C, C8, P with PR2269 own profiles: E = 0, idle unchanged, b_30 = floor_30(b) for all'
    print('control PR2269 via the CLI path: E = 0 for F/C/C8/P and b_30 = %s for all' % pr['rows'][0]['b'], flush=True)

    # (2) PR2269 pre-borrow stale assembly endpoint (1e-24 grid)
    Hpre = compose(T74, T74['pre']['local'], T74['pre']['idle'])
    bpre, _ = Moment(Hpre, T74['m'], T74['W']).floor_root(24)
    need(bpre == T74['pre']['complex_lower'], 'control.preborrow', 'pre-borrow 1e-24 endpoint not reproduced')
    res['pr2269_preborrow'] = dict(floor_24_root=dec(bpre, 24), equals='PR2269 SPEC.json / evidence/ASSEMBLY.json '
                                   'complex_lower (stale pre-borrow assembly)')
    print('control PR2269 pre-borrow: floor_1e-24(root) = %s = stale ASSEMBLY complex_lower' % dec(bpre, 24), flush=True)

    # (3) PR2260 b = 0.0016834 = floor_7(root), native and conservative
    T8 = FAMILIES['T8']
    H8 = compose(T8, T8['base']['local'], T8['base']['idle'])
    ev8 = Moment(H8, T8['m'], T8['W'])
    ev8c = Moment(H8, T8['m'], T8['W'], surcharge=True)
    b7, _ = ev8.floor_root(7)
    b7c, _ = ev8c.floor_root(7)
    need(b7 == T8['claim']['b'] == b7c, 'control.pr2260', 'floor_7(root) %s / conservative %s != 0.0016834' % (
        dec(b7, 7), dec(b7c, 7)))
    r8, _ = ev8.floor_root(40)
    res['pr2260'] = dict(floor_7_root_native=dec(b7, 7), floor_7_root_conservative=dec(b7c, 7),
                         b_40=dec(r8, 40), equals='PR2260 arithmetic/EXPECTED.json certified_complex_saving 8417/5000000')
    print('control PR2260: floor_1e-7(root) = %s (native and conservative) = claimed b; b_40 = %s' % (
        dec(b7, 7), dec(r8, 40)), flush=True)

    # (4) calibrated model in-sample identity: PR2269 pre-borrow base + PR2269 local -> PR2269 idle exactly
    sh = all_shares()
    need(sh['C']['all_increments_nonnegative'], 'control.calibration', 'T74 split has a negative increment')
    E_t74 = total_mass(T74) - sum(T74['calls'][p] * mass_of(T74['base']['local'][p]) for p in T74['calls']) - \
        mass_of(T74['pre']['idle'])
    need(E_t74 == sh['C']['E_ref'] == 138198, 'control.calibration', 'E_ref')
    idle_c = model_idle('C', T74['pre']['idle'], E_t74, 48, sh['C']['shares'])
    need(idle_c == T74['base']['idle'], 'control.calibration', 'C does not reproduce PR2269 idle in-sample')
    res['calibration'] = dict(
        C=dict(E_ref=sh['C']['E_ref'], shares=dict((str(r), str(s)) for r, s in sh['C']['shares'].items()),
               top_share=float(sh['C']['top_share']),
               in_sample='PR2269 pre-borrow idle {48:22748} + E_ref under C = PR2269 realized idle exactly'),
        C8=dict(E_ref=sh['C8']['E_ref'], shares=dict((str(r), str(s)) for r, s in sh['C8']['shares'].items()),
                top_share=float(sh['C8']['top_share']), delta_mass=plain(sh['C8']['delta_mass']),
                note='R492 parent residues (ranks 2..44) were repacked away; net top-rank share kept'))
    print('control calibration: T74 shares s48=%s (%.4f), C reproduces PR2269 idle in-sample exactly; T8 top share '
          '%s (%.4f)' % (sh['C']['top_share'], float(sh['C']['top_share']), sh['C8']['top_share'],
                         float(sh['C8']['top_share'])), flush=True)

    # (5) out-of-sample model check: predict each realized record from its own predecessor
    oos = {}
    for fname in ('T74', 'T8'):
        fam = FAMILIES[fname]
        pr = price_profiles(fam, fam['base']['local'], digits_model, base=fam['pre'])
        Hr = compose(fam, fam['base']['local'], fam['base']['idle'])
        rb, _ = Moment(Hr, fam['m'], fam['W']).floor_root(digits_model)
        rows = {}
        for row in pr['rows']:
            rows[row['model']] = dict(b=row['b'], minus_realized=str(row['b_rational'] - rb),
                                      fraction_of_realized_gain_over_pre=None)
        pre_b, _ = Moment(compose(fam, fam['pre']['local'], fam['pre']['idle']), fam['m'], fam['W']).floor_root(
            digits_model)
        for row in pr['rows']:
            rows[row['model']]['fraction_of_realized_gain_over_pre'] = '%.4f' % float(
                (row['b_rational'] - pre_b) / (rb - pre_b))
        oos[fname] = dict(start=fam['pre']['label'], target=fam['base']['label'], E=pr['extra_freed_mass'],
                          realized_b=dec(rb, digits_model), predecessor_b=dec(pre_b, digits_model), models=rows)
        print('out-of-sample %s (%s -> realized, E=%d): realized b %s' % (
            fname, fam['pre']['label'].split(' (')[0], pr['extra_freed_mass'], dec(rb, digits_model)[:24]), flush=True)
        for mn in MODEL_ORDER:
            print('   %-2s model b %s  (model - realized %s; share of realized gain %s)' % (
                mn, rows[mn]['b'][:24], sci(Fraction(rows[mn]['minus_realized']), 6), rows[mn]['fraction_of_realized_gain_over_pre']),
                flush=True)
    res['out_of_sample'] = oos

    # (6) negative controls
    neg = []

    def expect(name, target, fn):
        try:
            fn()
        except HarnessError as e:
            neg.append(dict(name=name, rejected_by=e.check, ok=e.check == target))
            return
        neg.append(dict(name=name, rejected_by=None, ok=False))

    split = dict(H)
    split[48] -= 1
    split[47] = 1
    split[1] += 1
    expect('one idle 48 -> 47 + 1: PR2269 b no longer admissible', 'moment.accept',
           lambda: require_side(Moment(clean(split), 73, 66304), B_2269, -1, 'split'))
    expect('PR2269 complex_lower + 1e-90 claimed admissible', 'moment.accept',
           lambda: require_side(ev, COMPLEX_LOWER_2269 + Fraction(1, 10 ** 90), -1, 'endpoint + 1e-90'))
    bad_idle = dict(T74['base']['idle'])
    bad_idle[48] += 1
    expect('idle with one extra rank-48 child (mass identity)', 'compose.mass',
           lambda: check_global(T74, compose(T74, T74['base']['local'], bad_idle), 'tampered'))
    expect('W off by one', 'compose.mass', lambda: check_global(dict(T74, W=66305), H, 'W+1'))
    expect('local mass != 1856 + widths', 'local.identity',
           lambda: resolve_input({'family': 'T74', 'providers': {
               'gauge44': {'profile': plain(T74['base']['local']['gauge44']), 'helper_width_sum': 3528},
               'extra': {'profile': plain(T74['base']['local']['extra'])}}}))
    expect('48 rank-52 children replace 52 rank-48 children (halving guard 2*52^2 > 73^2)', 'compose.halving',
           lambda: check_global(T74, add_profiles((1, H), (1, {52: 48}), (-1, {48: 52})), 'rank52'))
    expect('explicit idle with the wrong mass', 'compose.mass',
           lambda: price_profiles(T74, T74['base']['local'], 8, models=[], explicit_idle={48: 1}))
    ok = all(x['ok'] for x in neg)
    res['negative_controls'] = neg
    print('negative controls: %d/%d rejected by their targeted checks' % (sum(x['ok'] for x in neg), len(neg)),
          flush=True)
    need(ok, 'controls', 'a negative control was not rejected by its target: %r' % neg)
    res['elapsed_s'] = round(time.time() - t0, 1)
    receipt['controls'] = res


def report_price(spec, digits, conservative, receipt, key):
    fam, local, helpers, widths, idle, label = resolve_input(spec)
    pr = price_profiles(fam, local, digits, explicit_idle=idle, conservative=conservative)
    print('%s [%s]: %s' % (key, fam['name'], label), flush=True)
    for p in sorted(fam['calls']):
        print('  %s x%d: profile %s mass %d helpers %s' % (p, fam['calls'][p], plain(local[p]), mass_of(local[p]),
                                                         helpers.get(p)), flush=True)
    print('  idle mass %d, extra freed mass vs %s: E = %d' % (pr['idle_mass'], pr['base_label'].split(' (')[0],
                                                               pr['extra_freed_mass']), flush=True)
    lines = gain_lines(pr['rows'], digits)
    for ln in lines:
        print(ln, flush=True)
    if fam['name'] == 'T8':
        print('  (T8 gains are printed against the T74 references only for orientation; compare with the T8 base '
              'b instead)', flush=True)
    receipt[key] = dict(family=fam['name'], label=label, local_profiles=dict((p, plain(local[p])) for p in local),
                        local_mass=dict((p, mass_of(local[p])) for p in local), helpers=helpers,
                        idle_mass=pr['idle_mass'], extra_freed_mass=pr['extra_freed_mass'], digits=digits,
                        base=pr['base_label'], models=strip(pr['rows']))
    return pr


def demo_spec():
    return {'family': 'T74', 'label': 'PROXY: T8 transfer delta (PR2226 80-alias word minus PR2260 44-high word) '
            'applied to both PR2269 T74 words; not a constructed word',
            'delta': plain(T8_DELTA), 'helpers': {'gauge44': 401, 'extra': 401}}


def run_demo(digits, conservative, receipt):
    spec = demo_spec()
    with open(os.path.join(HERE, 'demo-t8-delta-proxy.json'), 'w') as fh:
        json.dump(spec, fh, indent=1, sort_keys=True)
        fh.write('\n')
    report_price(spec, digits, conservative, receipt, 'demo_t74_proxy')
    # T8 analogue: PR2226's actual word on PR2260's realized fill (same models; still a model price)
    t8 = {'family': 'T8', 'label': 'PR2226 actual 80-alias T8 word priced on PR2260 realized fill (model)',
          'providers': {'gauge44': {'profile': plain(PR2226_LOCAL), 'helpers': PR2226_HELPERS,
                                    'helper_width_sum': mass_of(PR2226_LOCAL) - 1856}}}
    pr = report_price(t8, digits, conservative, receipt, 'demo_t8_pr2226')
    T8 = FAMILIES['T8']
    b8, _ = Moment(compose(T8, T8['base']['local'], T8['base']['idle']), 73, 7168).floor_root(digits)
    for row in pr['rows']:
        row_t8 = '%s (%s)' % (sci(row['b_rational'] - b8, 8), pct(row['b_rational'] - b8, b8))
        print('  %-2s T8 gain over PR2260 realized b: %s' % (row['model'], row_t8), flush=True)
    receipt['demo_t8_pr2226']['gain_vs_pr2260_realized'] = dict(
        (row['model'], sci(row['b_rational'] - b8)) for row in pr['rows'])


def main():
    ap = argparse.ArgumentParser(description='Extended T74/T8 supplier pricing under explicit idle-refill models')
    ap.add_argument('cmd', choices=['controls', 'price', 'demo', 'sources', 'all'])
    ap.add_argument('input', nargs='?', help='profiles JSON for `price`')
    ap.add_argument('--digits', type=int, default=40, help='decimal grid 10^-D for model prices (default 40)')
    ap.add_argument('--conservative', action='store_true', help='also price the surcharge (conservative) side')
    ap.add_argument('--repo', default=DEFAULT_REPO, help='git checkout holding the pinned PR commits (sources)')
    ap.add_argument('--out', nargs='?', const='', default=None,
                    help='write a JSON receipt next to this script (default price_ext.<cmd>.receipt.json)')
    args = ap.parse_args()
    need(8 <= args.digits <= 200, 'input', '--digits must be in [8, 200]')
    receipt = dict(tool='price_ext.py', python=sys.version.split()[0], prec_bits=PREC, credits=CREDITS,
                   model=__doc__.split('MODEL (stated precisely; also written to receipts).')[1].strip(),
                   references=dict(pr2269_b=dec(B_2269, 100), pr2312_kappa=str(KAPPA_2312), bit_lower=str(BIT_LOWER)))
    t0 = time.time()
    ok = True
    try:
        if args.cmd in ('sources', 'all'):
            run_sources(args.repo, receipt)
        if args.cmd in ('controls', 'all'):
            run_controls(receipt)
        if args.cmd in ('demo', 'all'):
            run_demo(args.digits, args.conservative, receipt)
        if args.cmd == 'price':
            need(args.input is not None, 'input', 'price needs an INPUT.json')
            with open(args.input) as fh:
                spec = json.load(fh)
            report_price(spec, args.digits, args.conservative, receipt, 'price')
    except HarnessError as e:
        ok = False
        receipt['failure'] = str(e)
        print('FAILED: %s' % e, flush=True)
    receipt['result'] = PASS_LINE if ok else FAIL_LINE
    receipt['elapsed_s'] = round(time.time() - t0, 1)
    if args.out is not None:
        path = args.out or os.path.join(HERE, 'price_ext.%s.receipt.json' % args.cmd)
        with open(path, 'w') as fh:
            json.dump(receipt, fh, indent=1, sort_keys=True, default=str)
            fh.write('\n')
        print('receipt written: %s' % path)
    print('elapsed %.1f s' % (time.time() - t0))
    print(PASS_LINE if ok else FAIL_LINE)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
