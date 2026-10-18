#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact check of the selected suppliers' moment acceptance and
the a < D/E small-saving diagnostic.

Navinor (with help from opencode). Apache-2.0.

Code-disjoint by construction: this file imports nothing from the repository's
retained moment engines (moment.py, base_two_moment.py, the atanh prime chain of
research/pending-claims-independent-pricing, or
research/community-batch970-audit/submitted/957/.../audit_endpoint_reduction.py).
It restates the priced bill from the published ledgers and computes:

  1. ledger aggregates (rank mass, deficit) and their coverage identities,
     reconstructed from the published histograms rather than taken from the
     recorded aggregates;
  2. the moment residual f(a) - 1 at the two certified endpoints of
     research/community-frontier1094-audit/ASSEMBLY.json and at their next
     1e-24 grid points, with ln enclosed by rational square-root bisection
     (independent cross-check: bisection inverting a Taylor exp) and exp by
     Taylor partial sums with an explicit rational tail bound;
  3. the certified D/E diagnostic: for the priced bill
        f(a) = (1/(mW)) * sum_r n_r r (m/r)^a  +  c_s m^a,
     convexity gives  a* < D_eff / E_eff  strictly, where
        D_eff = mW - sum n_r r - c_s mW,   E_eff = sum n_r r ln(m/r) + c_s mW ln m.
     For c_s = 0 this is exactly the autoresearch.md section-2 diagnostic
     "a < D/E" with D = mW - sum n_r r, E = sum n_r r log(m/r).

Acceptance is the exact moment sign; D/E is a diagnostic upper bound only.
No kappa change is claimed or possible here.
"""
import hashlib
import json
import sys
from fractions import Fraction as Q
from math import isqrt
from pathlib import Path

try:
    sys.set_int_max_str_digits(1000000)
except AttributeError:      # Python 3.10 has no digit cap
    pass

ROOT = Path(__file__).resolve().parents[2]
ASSEMBLY = ROOT / 'research/community-frontier1094-audit/ASSEMBLY.json'
INDEPENDENT = ROOT / 'research/community-frontier1094-audit/INDEPENDENT1094.json'
BIT_EXPECTED = ROOT / 'research/e8-bit-p111-tuned/tune/EXPECTED.json'

ASSEMBLY_SHA256 = '1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045'
EXPECTED_GIT_BLOB = 'e293ddc557742637f9f679f083a1a282d87b1b13'
GRID = Q(1, 10 ** 24)

SQRT_STEPS = 112        # x^(1/2^k) reduction depth for the sqrt-bisection ln
SQRT_BITS = 320         # dyadic scale of each sqrt enclosure
EXP_ORDER = 48          # Taylor order for the small exponentials of the bill
CROSS_ORDER = 48        # Taylor order for the exp-inversion ln cross-check
CROSS_BITS = 72         # bisection depth for the exp-inversion ln cross-check


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def decimal(frac, digits=30):
    """Truncated decimal string of a rational (sign-aware)."""
    sign = '-' if frac < 0 else ''
    v = abs(Q(frac))
    scaled = (v.numerator * 10 ** digits) // v.denominator
    s = str(scaled).zfill(digits + 1)
    return sign + s[:-digits] + '.' + s[-digits:]


# ---------------------------------------------------------------------------
# Enclosure 1: ln by rational square-root bisection (no series).
#   x^(1/2^k) is bracketed by repeated integer square roots on a 2^-320 grid;
#   with u = s - 1 in [0, 1],   u - u^2/2 <= ln(1+u) <= u.
# ---------------------------------------------------------------------------

def sqrt_bracket(frac):
    """Return (lo, hi) dyadic rationals with lo <= sqrt(frac) <= hi."""
    require(frac > 0, 'sqrt domain')
    scale = 1 << (2 * SQRT_BITS)
    n = (frac.numerator * scale) // frac.denominator     # floor(frac * 2^2P)
    s = isqrt(n)
    lo = Q(s, 1 << SQRT_BITS)
    hi = Q(s + 1, 1 << SQRT_BITS)
    require(lo * lo <= frac and hi * hi >= frac, 'sqrt bracket')
    return lo, hi


def ln_sqrt(frac):
    """Enclose ln(frac), frac >= 1, by square-root reduction; exact rationals."""
    require(frac >= 1, 'ln_sqrt domain')
    if frac == 1:
        return Q(0), Q(0)
    lo, hi = frac, frac
    for _ in range(SQRT_STEPS):
        lo, _ = sqrt_bracket(lo)
        _, hi = sqrt_bracket(hi)
        require(0 < lo <= hi, 'sqrt reduction order')
    u_lo, u_hi = lo - 1, hi - 1
    require(0 <= u_lo <= u_hi < Q(1, 2), 'reduction range')
    k = Q(1 << SQRT_STEPS, 1)
    return k * (u_lo - u_lo * u_lo / 2), k * u_hi


# ---------------------------------------------------------------------------
# Enclosure 2 (cross-check): ln by bisection inverting a certified Taylor exp.
# ---------------------------------------------------------------------------

def exp_taylor(point, order):
    """Enclose exp(y) for a rational 0 <= y < 9; exact rationals."""
    require(0 <= point < 9, 'exp range')
    term = total = Q(1)
    for j in range(1, order + 1):
        term = term * point / j
        total += term
    tail = term * point / (order + 1)
    require(point < order + 1, 'exp tail ratio')
    tail = tail / (1 - point / (order + 2))
    return total, total + tail


def ln_exp_bisection(frac):
    """Enclose ln(frac), frac >= 1, by bisecting exp(t) = frac; exact rationals."""
    require(frac >= 1, 'ln_exp_bisection domain')
    if frac == 1:
        return Q(0), Q(0)
    lo, hi = Q(0), Q(1)
    while exp_taylor(hi, CROSS_ORDER)[0] < frac:
        hi *= 2
        require(hi < 1024, 'exp bisection bracket')
    for _ in range(CROSS_BITS):
        mid = (lo + hi) / 2
        mid_lo, mid_hi = exp_taylor(mid, CROSS_ORDER)
        if mid_hi < frac:
            lo = mid
        elif mid_lo > frac:
            hi = mid
        else:
            lo = hi = mid
            break
    return lo, hi


# ---------------------------------------------------------------------------
# The priced bill and the D/E diagnostic.
# ---------------------------------------------------------------------------

class Bill:
    """f(a) = (1/(mW)) sum_r n_r r (m/r)^a + c_s m^a, with certified enclosures.

    ln enclosures are intervals [l_lo, l_hi]; the exponential of a positive
    interval is bounded by monotonicity using the Taylor enclosure above.
    """

    def __init__(self, hist, m, W, surcharge_coeff=Q(0)):
        self.hist = {int(r): int(n) for r, n in hist.items()}
        self.m, self.W = int(m), int(W)
        self.c_s = Q(surcharge_coeff)
        require(self.m > 1 and self.W > 0, 'width/stock range')
        require(all(0 < r < self.m and n > 0 for r, n in self.hist.items()),
                'child rank range')
        self.mass = sum(r * n for r, n in self.hist.items())
        self.count = sum(self.hist.values())
        self.deficit = self.m * self.W - self.mass
        require(self.deficit > 0, 'deficit must be positive')
        self.ln = {r: ln_sqrt(Q(self.m, r)) for r in self.hist}
        self.ln_cross = {r: ln_exp_bisection(Q(self.m, r)) for r in self.hist}

    def residual(self, a, surcharge_coeff=None):
        """Certified interval of f(a) - 1 at a rational a >= 0."""
        c_s = self.c_s if surcharge_coeff is None else Q(surcharge_coeff)
        require(a >= 0, 'saving range')
        total_lo = total_hi = Q(0)
        for r, n in self.hist.items():
            l_lo, l_hi = self.ln[r]
            e_lo, _ = exp_taylor(a * l_lo, EXP_ORDER)
            _, e_hi = exp_taylor(a * l_hi, EXP_ORDER)
            p = Q(r * n, self.m * self.W)
            total_lo += p * e_lo
            total_hi += p * e_hi
        if c_s:
            l_lo, l_hi = ln_sqrt(Q(self.m))
            e_lo, _ = exp_taylor(a * l_lo, EXP_ORDER)
            _, e_hi = exp_taylor(a * l_hi, EXP_ORDER)
            total_lo += c_s * e_lo
            total_hi += c_s * e_hi
        return total_lo - 1, total_hi - 1

    def de_bound(self, surcharge_coeff=None):
        """Certified interval of the diagnostic ceiling D_eff / E_eff."""
        c_s = self.c_s if surcharge_coeff is None else Q(surcharge_coeff)
        require(c_s >= 0, 'surcharge range')
        d_eff = Q(self.deficit) - c_s * self.m * self.W
        require(d_eff > 0, 'effective deficit must be positive')
        e_lo = e_hi = Q(0)
        for r, n in self.hist.items():
            l_lo, l_hi = self.ln[r]
            e_lo += r * n * l_lo
            e_hi += r * n * l_hi
        if c_s:
            l_lo, l_hi = ln_sqrt(Q(self.m))
            e_lo += c_s * self.m * self.W * l_lo
            e_hi += c_s * self.m * self.W * l_hi
        require(e_lo > 0, 'E must be positive')
        return d_eff / e_hi, d_eff / e_lo

    def de_screening_extremum(self):
        """Screening-only D/E ceiling over histograms with the same m, W and
        rank mass, fractional counts allowed, ranks capped by the halving
        guard m^2 > 2 r^2. E is smallest when all rank mass sits at the cap,
        so this maximizes D/E. Not a realizability claim."""
        r_cap = 1
        while 2 * (r_cap + 1) ** 2 < self.m ** 2:
            r_cap += 1
        l_lo, l_hi = ln_sqrt(Q(self.m, r_cap))
        e_hi = self.mass * l_hi
        return self.deficit / e_hi, r_cap


# ---------------------------------------------------------------------------
# Ledgers of the selected record.
# ---------------------------------------------------------------------------

def complex_ledger(assembly, independent):
    hist = {int(r): int(n) for r, n in assembly['complex_profile'].items()}
    calls = assembly['provider_counts']['gauge44']
    mass = sum(r * n for r, n in hist.items())
    # Coverage identities D = 73W - mass and D = W - 64N determine
    # W = (mass - 64N) / 72; the audited value is pinned in INDEPENDENT1094.
    require((mass - 64 * calls) % 72 == 0, 'complex coverage identity')
    W = (mass - 64 * calls) // 72
    require(W == independent['price']['live'] == 14336, 'complex live stock')
    require(calls == independent['price']['calls'] == 144, 'complex call count')
    bill = Bill(hist, m=73, W=W)
    require(bill.deficit == W - 64 * calls == independent['price']['deficit'],
            'complex deficit identity')
    return bill, dict(m=73, W=W, N=calls, deficit=bill.deficit)


def bit_ledger(assembly, expected):
    block = assembly['bit_supplier']
    word = block['word']
    nine = expected['nine']
    hist = nine['profile']
    W = nine['bit']['live']
    require(block['path'] == 'research/e8-bit-p111-tuned/tune/EXPECTED.json',
            'bit supplier path')
    require(git_blob(BIT_EXPECTED) == block['git_blob_sha1'] == EXPECTED_GIT_BLOB,
            'bit supplier git blob')
    require(word['v'] == expected['word']['v'] == 111, 'bit word parameter v')
    require(word['decoder_constant'] == expected['word']['decoder_constant'] == 63,
            'bit decoder constant')
    L = len(word['copy_ranks'])
    require(L == expected['word']['retained_totals'] == 9, 'bit copy-rank count')
    require(set(word['copy_ranks']) == {7}, 'bit copy ranks')
    # Coverage identity D = 64W - mass = T(2Kv - L*cst), T=32 K=4 M=64.
    T, K, M = 32, 4, 64
    derived = T * (2 * K * word['v'] - L * word['decoder_constant'])
    bill = Bill(hist, m=M, W=W, surcharge_coeff=Q(32 * M * sum(hist.values()), 10 ** 16 * W))
    require(bill.deficit == derived == block['derived_deficit'],
            'bit deficit identity')
    require(block['deficit_formula'] == 'T(2Kv-L*cst), L=9 T=32 K=4 M=64',
            'bit deficit formula label')
    return bill, dict(m=M, W=W, T=T, K=K, L=L, deficit=bill.deficit)


def check_endpoint(bill, label, endpoint, nxt, recorded, controls):
    """Positive fixture for one certified endpoint, plus sign controls."""
    require(nxt == endpoint + GRID, label + ' next-grid point')
    lo, hi = bill.residual(endpoint)
    nlo, nhi = bill.residual(nxt)
    require(hi < 0, label + ' moment must accept at the endpoint')
    require(nlo > 0, label + ' moment must reject at the next grid point')
    # Agreement with the two retained engines' recorded residual intervals.
    for engine in ('mercator', 'base_two'):
        rec = recorded[engine]
        r_lo, r_hi = Q(rec[0]), Q(rec[1])
        require(lo <= r_hi and hi >= r_lo, label + ' residual agrees with ' + engine)
    # Smallest falsifying instance for the acceptance claim: one more grid
    # step from the endpoint must already flip the sign.
    flo, fhi = bill.residual(endpoint + 2 * GRID)
    require(flo > 0, label + ' two grid steps must reject')
    controls.append((label + ':endpoint+2grid-rejects', True))
    return dict(endpoint=str(endpoint), residual=[str(lo), str(hi)],
                residual_decimal=[decimal(lo), decimal(hi)],
                next_grid_residual=[str(nlo), str(nhi)],
                next_grid_decimal=[decimal(nlo), decimal(nhi)],
                accept=True, sharp_next_grid=True)


def check_de(bill, label, a_rec, controls):
    """The certified a < D/E diagnostic for one ledger."""
    b_lo, b_hi = bill.de_bound()
    require(b_lo > 0 and b_lo <= b_hi, label + ' D/E interval order')
    require(a_rec < b_lo, label + ' recorded endpoint below the D/E ceiling')
    require(b_lo - a_rec > 0, label + ' strictness')
    tight = Q(b_lo) / Q(a_rec)
    screen, r_cap = bill.de_screening_extremum()
    require(screen > b_hi, label + ' screening extremum above the ledger ceiling')
    return dict(de_bound=[str(b_lo), str(b_hi)],
                de_decimal=[decimal(b_lo), decimal(b_hi)],
                endpoint=str(a_rec),
                bound_over_endpoint=decimal(tight),
                endpoint_strictly_below=True,
                screening_extremum_decimal=decimal(screen),
                screening_rank_cap=r_cap,
                screening_note='D/E ceiling over rank-mass-preserving repackings '
                               'with fractional counts at ranks up to the halving '
                               'guard; screening only, not a realizability bound')


def single_rank_falsification(controls):
    """Exactly solvable smallest instance: H={1:1}, m=2, W=1.
    f(a) = 2^(a-1), so a* = 1 exactly, and D/E = 1/ln 2 > 1."""
    bill = Bill({1: 1}, m=2, W=1)
    lo, hi = bill.residual(Q(1))
    require(lo <= 0 <= hi, 'single-rank root must be a = 1')
    below, _ = bill.residual(Q(999, 1000))
    _, above = bill.residual(Q(1001, 1000))
    require(below < 0 < above, 'single-rank sign change around a = 1')
    b_lo, b_hi = bill.de_bound()
    require(b_lo > 1, 'single-rank D/E strictly above the root a* = 1')
    l_lo, l_hi = bill.ln[1]
    c_lo, c_hi = bill.ln_cross[1]
    require(l_lo <= c_hi and c_lo <= l_hi, 'ln(2) enclosures agree')
    controls.append(('single-rank-root-exact', True))
    return dict(root='1', de_bound=[str(b_lo), str(b_hi)],
                ln2=[decimal(l_lo), decimal(l_hi)])


def failure_controls(assembly, independent, expected, controls):
    """Semantic failure controls: every mutation must be rejected."""
    def rejected(name, fn):
        try:
            fn()
        except ValueError:
            controls.append((name, True))
            return
        raise ValueError('failure control not rejected: ' + name)

    rejected('tampered-assembly-pin',
             lambda: require(sha256(ASSEMBLY) == 'deadbeef', 'pin'))
    rejected('bit-wrong-width',
             lambda: require(
                 Bill(expected['nine']['profile'], m=73, W=expected['nine']['bit']['live'])
                 .deficit == assembly['bit_supplier']['derived_deficit'], 'deficit'))
    bad_hist = dict(assembly['complex_profile'])
    bad_hist['1'] = bad_hist['1'] + 1
    bad_hist['48'] = bad_hist['48'] - 1

    def bad_complex():
        mass = sum(int(r) * n for r, n in bad_hist.items())
        calls = assembly['provider_counts']['gauge44']
        require((mass - 64 * calls) % 72 == 0 and
                (mass - 64 * calls) // 72 == independent['price']['live'], 'coverage')
    rejected('complex-mutated-histogram', bad_complex)
    rejected('child-rank-out-of-range', lambda: Bill({73: 1}, m=73, W=1))
    rejected('zero-deficit', lambda: Bill({1: 10}, m=2, W=5))
    c_bill = Bill(assembly['complex_profile'], m=73, W=independent['price']['live'])
    a_c = Q(assembly['moments'][2]['endpoint'])
    # Claiming a shifted endpoint as accepting must fail the acceptance test.
    rejected('complex-endpoint-shifted-two-grids',
             lambda: require(c_bill.residual(a_c + 2 * GRID)[1] < 0, 'accept'))
    b_bill = Bill(expected['nine']['profile'], m=64, W=expected['nine']['bit']['live'],
                  surcharge_coeff=Q(32 * 64 * sum(int(n) for n in expected['nine']['profile'].values()),
                                     10 ** 16 * expected['nine']['bit']['live']))
    a_b = Q(assembly['moments'][0]['endpoint'])

    def doubled_surcharge():
        lo, hi = b_bill.residual(a_b, surcharge_coeff=2 * b_bill.c_s)
        require(hi < 0, 'accept with doubled surcharge')
    rejected('bit-doubled-surcharge-breaks-acceptance', doubled_surcharge)

    def negative_surcharge():
        b_bill.de_bound(surcharge_coeff=Q(-1))
    rejected('negative-surcharge-rejected', negative_surcharge)


def main():
    require(sha256(ASSEMBLY) == ASSEMBLY_SHA256, 'selected assembly pin')
    assembly, independent, expected = read(ASSEMBLY), read(INDEPENDENT), read(BIT_EXPECTED)
    controls = []

    single = single_rank_falsification(controls)
    c_bill, c_ledger = complex_ledger(assembly, independent)
    b_bill, b_ledger = bit_ledger(assembly, expected)

    moments = assembly['moments']
    bit_row = moments[0]
    cplx_row = moments[2]
    require(bit_row['surcharge'] is True and cplx_row['surcharge'] is False,
            'recorded surcharge model')

    c_endpoint = check_endpoint(c_bill, 'complex', Q(cplx_row['endpoint']),
                                Q(moments[3]['endpoint']), cplx_row, controls)
    b_endpoint = check_endpoint(b_bill, 'bit', Q(bit_row['endpoint']),
                                Q(moments[1]['endpoint']), bit_row, controls)
    c_de = check_de(c_bill, 'complex', Q(cplx_row['endpoint']), controls)
    b_de = check_de(b_bill, 'bit', Q(bit_row['endpoint']), controls)

    # ln-method agreement on every used log, for both ledgers.
    for bill, label in ((c_bill, 'complex'), (b_bill, 'bit')):
        for r, (l_lo, l_hi) in bill.ln.items():
            c_lo, c_hi = bill.ln_cross[r]
            require(l_lo <= c_hi and c_lo <= l_hi and
                    l_hi - l_lo < Q(1, 10 ** 20),
                    '%s ln(%d/%d) methods agree' % (label, bill.m, r))
    controls.append(('ln-methods-agree-all-ranks', True))

    failure_controls(assembly, independent, expected, controls)

    out = dict(
        status='PASS_INDEPENDENT_DE_DIAGNOSTIC',
        method=dict(
            ln='rational square-root bisection (x^(1/2^k), k=%d, 2^-%d grid), '
               'ln(1+u) bracketed by u-u^2/2 <= ln(1+u) <= u' % (SQRT_STEPS, SQRT_BITS),
            ln_cross='bisection inverting a Taylor exponential (order %d)' % CROSS_ORDER,
            exp='Taylor partial sums, order %d, rational geometric tail bound' % EXP_ORDER,
            arithmetic='exact fractions throughout; enclosures from explicit '
                       'inequalities only; no floating point',
            imports='no repository engine imported'),
        ledger=dict(complex=c_ledger, bit=b_ledger),
        moment=dict(complex=c_endpoint, bit=b_endpoint),
        de=dict(complex=c_de, bit=b_de),
        single_rank_falsification=single,
        lemma='For f(a) = (1/(mW)) sum_r n_r r (m/r)^a + c_s m^a with 0 < r < m, '
              'W >= 1 and c_s >= 0, f is convex and f(0) = 1 - D_eff/(mW) with '
              'D_eff > 0. The tangent at a = 0 meets 1 at D_eff/E_eff, so the '
              'exact root satisfies a* < D_eff/E_eff strictly. For c_s = 0 this '
              'is the autoresearch.md section-2 diagnostic a < D/E.',
        controls=[name for name, _ in controls],
        scope='Independent verification and diagnostic only. The moment sign is '
              'the acceptance test; D/E is a diagnostic upper bound on the root '
              'of one fixed ledger histogram and is not a realizability or '
              'repacking bound. No kappa change; the selected record is unchanged.',
        limitations=[
            'The paid profiles are taken from the published ledgers '
            '(ASSEMBLY.json complex_profile; EXPECTED.json nine.profile); this '
            'package does not rebuild either word from its original operations.',
            'The conservative (surcharge-on-complex) endpoints of ASSEMBLY.json '
            'are not rechecked here.',
            'D/E is a per-histogram ceiling; an upper bound over all repackings '
            'needs the coverage-law argument, see '
            'https://github.com/CrocSwap/integer-mult-bounds/pull/1240 for the '
            'complex local word.'],
    )
    out_path = Path(__file__).with_name('RESULT.json')
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(out['status'])
    for side in ('complex', 'bit'):
        m, d = out['moment'][side], out['de'][side]
        print('%-8s moment residual at endpoint %s  next grid %s' %
              (side, m['residual_decimal'][1], m['next_grid_decimal'][0]))
        print('%-8s D/E ceiling %s  (bound/endpoint %s)' %
              (side, d['de_decimal'][0], d['bound_over_endpoint']))
    print('controls', len(controls), 'all rejected/passed')


if __name__ == '__main__':
    try:
        main()
    except ValueError as exc:
        print('FAIL:', exc)
        sys.exit(1)
