#!/usr/bin/env python3
"""Independent exact audit of the endpoint certification and the
endpoint-to-kappa reduction of the selected frontier890 record
(certificates/selected-result.json -> research/community-frontier890-audit/
ASSEMBLY.json), with the surcharge-model accounting step as the adversarial
target.

Assignment seed 73, track 60-74 (adversarial mathematical audit).
Prepared with help from opencode. Apache-2.0, per CONTRIBUTING.md.

Scope (one accounting chain, three steps):

 1. Endpoint certification. The six recorded "accepted at e / rejected at
    e+1e-24" moment rows are recomputed from the recorded complex profile and
    the blob-pinned PR589 bit record, with two independent rational interval
    enclosures (Mercator log/exp bounds, and the base-two atanh/polynomial
    bounds) and a third direct 60-digit Decimal evaluation of the moment sum.
    This closes the moment-engine obligation left open by
    research/audit-kappa-floor-seed67/AUDIT.md.

 2. Endpoint-to-kappa reduction. Both reductions (accepted and conservative)
    are recomputed with exact rationals, importing none of the repository
    engines: seven-step bootstrap chain, guard margins, all 47 outer slacks
    per row, and the 1e-18 grid floor. Same method as seed 67, new record.

 3. Surcharge accounting. The asymmetry surcharge_model = {complex: False,
    bit: True} is load-bearing. Its exact price in ticks, the two recorded
    model controls, and the reduction that remains licensed if the complex
    side keeps its surcharge are recomputed and compared.

This script reruns no construction, owner census or invoice. Findings and
coverage limits are in AUDIT.md.

Reproduce:  python research/audit-frontier890-endpoint-seed73/audit_endpoint_reduction.py
Requires CPython >= 3.10, standard library only, no -O (assertions enabled).
"""
import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSEMBLY_PATH = ROOT / 'research/community-frontier890-audit/ASSEMBLY.json'
SELECTED_PATH = ROOT / 'certificates/checkpoints/frontier890.json'
CLAIM_PATH = ROOT / 'research/complex-t21-owners/data/CLAIM.json'
BIT_PATH = ROOT / 'research/e8-bit-p111-tuned/tune/EXPECTED.json'
ENGINES = ROOT / 'research/complex-k492-owner-repair/vendor/multicold/engines'

TICK = Q(1, 10**18)
ENDPOINT_STEP = Q(1, 10**24)
ETA = BETA = Q(1, 10**24)
S_FLOOR = Q(1, 10**27)
CHAIN_SEED = Q(384599, 10**10)
BRIDGE_LITERAL = Q(1)
BRIDGE_ROW_GAP = Q(10**6) - Q(51 * 20161, 25)
PREVIOUS_FRONTIER = Q('0.001661634653669567')   # PR799 ancestor exponent
BASELINE870 = Q('0.001661956299899884')          # PR870/T16 value


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def frac(text):
    return Q(text)


# ---------------------------------------------------------------------------
# Transcription A: engines/moment.py (Mercator log, 24-degree exponential,
# 224-bit outward dyadic rounding). Exact rationals only.
# ---------------------------------------------------------------------------

DYAD = 1 << 224


def d_floor(x):
    return Q(x.numerator * DYAD // x.denominator, DYAD)


def d_ceil(x):
    return -d_floor(-x)


@lru_cache(maxsize=None)
def mercator_log(x):
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    j = int(x >= Q(3, 2))
    if j:
        x /= Q(3, 2)

    def mercator(y):
        z = y - 1
        assert 0 <= z <= Q(1, 2)
        t, s = z, Q(0)
        for n in range(1, 225):
            s += (t if n & 1 else -t) / n
            t *= z
        return s, s + t / 225

    a, b = mercator(x)
    c, d = mercator(Q(3, 2))
    e, f = mercator(Q(4, 3))
    return d_floor(a + (k + j) * c + k * e), d_ceil(b + (k + j) * d + k * f)


def mercator_exp(l, u):
    assert 0 <= l <= u < Q(1, 10)

    def poly(x):
        s = t = Q(1)
        for j in range(1, 25):
            t = t * x / j
            s += t
        return s, t

    lo, _ = poly(l)
    hi, last = poly(u)
    return d_floor(lo), d_ceil(hi + last * u / 25 / (1 - u / 26))


def mercator_moment(H, m, W, a, bad):
    lo = hi = Q(0)
    for r, n in H.items():
        assert 0 < r < m and n > 0
        l, u = mercator_log(Q(m, r))
        e, f = mercator_exp(a * l, a * u)
        p = Q(r * n, m * W)
        lo += p * e
        hi += p * f
    if bad:
        l, u = mercator_log(Q(m))
        e, f = mercator_exp(a * l, a * u)
        p = Q(32 * m * sum(H.values()), 10**16 * W)
        lo += p * e
        hi += p * f
    return d_floor(lo), d_ceil(hi)


# ---------------------------------------------------------------------------
# Transcription B: engines/base_two_moment.py (atanh log, 12-degree
# exponential, 1e-30 outward rounding). Exact rationals only.
# ---------------------------------------------------------------------------

GRID = 10**30


def b_log_unit(x):
    assert 1 <= x <= 2
    z = (x - 1) / (x + 1)
    lo = 2 * sum((z**(2 * j + 1) / (2 * j + 1) for j in range(80)), Q(0))
    return lo, lo + 2 * z**161 / (161 * (1 - z * z))


def b_log(x):
    k = 0
    while x > 2:
        x /= 2
        k += 1
    lo, hi = b_log_unit(x)
    l2, u2 = b_log_unit(Q(2))
    lo, hi = lo + k * l2, hi + k * u2
    return Q((lo * GRID).__floor__(), GRID), Q((hi * GRID).__ceil__(), GRID)


def b_exp(x):
    assert 0 <= x < 1
    term = total = Q(1)
    for j in range(1, 13):
        term *= x / j
        total += term
    tail = term * x / 13 / (1 - x / 14)
    return total, total + tail


def base_two_moment(m, W, entries, a):
    lo = hi = Q(0)
    for t, count in entries:
        t, count = int(t), int(count)
        assert 0 < t < m and count > 0
        l, u = b_log(Q(m, t))
        lower = b_exp(a * l)[0]
        upper = b_exp(a * u)[1]
        lo += Q(t * count, m * W) * lower
        hi += Q(t * count, m * W) * upper
    return Q((lo * GRID).__floor__(), GRID), Q((hi * GRID).__ceil__(), GRID)


# ---------------------------------------------------------------------------
# Method C: direct 60-digit Decimal evaluation of the moment sum. No interval
# bounds, no shared rounding with A or B; used only for sign agreement.
# ---------------------------------------------------------------------------

def decimal_moment(H, m, W, a, bad):
    with localcontext() as ctx:
        ctx.prec = 60
        ad = Decimal(a.numerator) / Decimal(a.denominator)
        total = Decimal(0)
        for r, n in H.items():
            p = Decimal(r * n) / Decimal(m * W)
            total += p * (ad * (Decimal(m) / Decimal(r)).ln()).exp()
        if bad:
            p = Decimal(32 * m * sum(H.values())) / Decimal(10**16 * W)
            total += p * (ad * Decimal(m).ln()).exp()
        return total


def row_values(H, m, W, z, bad):
    """The exact recorded row payload of check_moment for one endpoint."""
    l, u = mercator_moment(H, m, W, z, bad)
    ll, uu = base_two_moment(m, W, list(H.items()), z)
    if bad:
        fl, fu = base_two_moment(m, W, [(1, 32 * m * m * sum(H.values()))], z)
        ll += fl / 10**16
        uu += fu / 10**16
    payload = dict(mercator=[str(l - 1), str(u - 1)], base_two=[str(ll - 1), str(uu - 1)])
    return payload, (l, u, ll, uu)


# ---------------------------------------------------------------------------
# Transcription D: the endpoint-to-kappa reduction (outer_witness in the
# assembly stage) and the 47 strict outer slacks (engines/outer.py).
# ---------------------------------------------------------------------------

def ceil_q(x):
    return -(-x.numerator // x.denominator)


def reduce_endpoint(bb, c, eta=ETA, beta=BETA):
    s = min(c, (1 - beta) * bb) - S_FLOOR
    assert 0 < s < c and s < (1 - beta) * bb
    chain = [CHAIN_SEED]
    cuts = []
    for _ in range(7):
        old = chain[-1]
        a = (1 - s) * s + s * old
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
        assert old < a < s < 1 - a and gap > 0
        cut = max(ceil_q(Q(36) / gap**2), ceil_q(Q(2 * (4 + 512)) / gap))
        assert cut * gap**2 >= 36 and cut * gap >= 2 * (4 + 512)
        cuts.append(dict(exponent=str(a), gap=str(gap), cutoff_log2=str(cut)))
        chain.append(a)
    q = chain[-1] * (1 - 2 * eta)
    margin = (1 - eta) * q / (1 + q)
    ticks = margin * 10**18
    k = Q((ticks.numerator - 1) // ticks.denominator, 10**18)
    return dict(kappa=k, margin=margin, s=s, chain=chain, cuts=cuts)


def outer_slacks(a, b, kappa, eta=ETA, beta=BETA):
    tau, sigma = 1 - a, 1 - b
    q = a * (1 - 2 * eta)
    lp = 1 - q
    lam = (tau + lp) / 2
    c = q + eta / 4
    eps = (1 - eta) / (1 + q)
    minimum = eps * q
    r = (minimum + 1 - eps) / 2
    delta = eta / 8
    internal = tau + (1 - beta) * max(sigma - tau, Q(0))
    leaf = sigma + beta * (1 - sigma)
    margins = dict(balanced_prefix=1 - eps, coordinate_movement=a,
                   compact_phase_layer=minimum, bulk_exposure=a,
                   Gaussian_arithmetic=min(1 - eps - delta, r - delta),
                   scalar_work=1 - eps - delta, dimension=eps)
    slacks = dict(bit_positive=a, complex_above_bit=b - a,
                  complex_below_one_over32=Q(1, 32) - b, beta_positive=beta,
                  beta_below_one=1 - beta, leaf_saving_above_bit=(1 - beta) * b - a,
                  q_positive=q, q_below_internal=1 - internal - q,
                  q_below_leaf=1 - leaf - q, c_positive=c, c_below_one=1 - c,
                  q_below_reservations=c - q, lambda_above_tau=lam - tau,
                  lambda_above_sigma=lam - sigma, lambda_above_internal=lam - internal,
                  lambda_prime_above_lambda=lp - lam, compact_leaf=lp - leaf,
                  compact_reservations=lp - (1 - c), lambda_prime_below_one=q,
                  epsilon_positive=eps, epsilon_below_one=1 - eps, guard_width=1 - eps,
                  K_geometry=1 - eps * (1 + c), K_dominates_log=eps * c,
                  record_suffix=1 - eps, phase_local=1 - eps - delta,
                  phase_boundary=r - delta, gamma_sublinear=1 - eps - r,
                  cell_above_band=eps - (1 - r) / 2, prime_interval_packing=1 - eps,
                  alpha_positive=r, alpha_below_one=1 - r,
                  alpha_below_one_fourth=Q(1, 4) - r, delta_positive=delta,
                  delta_below_one_eighth=Q(1, 8) - delta,
                  short_record_fallback=eps - a,
                  small_field_exposure=1 - eps - minimum,
                  artificial_boundary=8 - eps + r - delta - minimum,
                  literal_scalar_guard=BRIDGE_LITERAL, row_product_gap=BRIDGE_ROW_GAP)
    slacks.update({name + '_above_kappa': val - kappa for name, val in margins.items()})
    assert len(slacks) == 47 and len(margins) == 7
    assert min(margins.values()) == minimum
    return slacks, margins, minimum


def detected(name, matches):
    """Negative control: `matches` compares a tampered record to the recomputation."""
    assert matches is False, 'negative control not detected: ' + name


def main():
    if not __debug__:
        raise RuntimeError("This historical audit requires assertions enabled; do not use -O")
    selected = json.loads(SELECTED_PATH.read_text(encoding='utf-8'))
    assembly = json.loads(ASSEMBLY_PATH.read_text(encoding='utf-8'))
    claim = json.loads(CLAIM_PATH.read_text(encoding='utf-8'))
    bit_record = json.loads(BIT_PATH.read_text(encoding='utf-8'))

    # --- pins -------------------------------------------------------------
    assert sha256(ASSEMBLY_PATH) == selected['certificate_sha256'], 'certificate pin'
    for name in ('moment', 'base_two_moment', 'outer'):
        key = 'engines/%s.py' % name
        assert sha256(ENGINES / ('%s.py' % name)) == assembly['input_sha256'][key], key
    assert git_blob(BIT_PATH) == assembly['bit_supplier']['git_blob_sha1'], 'bit blob pin'
    assert Q(assembly['kappa']) == Q(claim['kappa']), 'claim kappa'
    assert Q(assembly['complex_lower']) == Q(claim['complex_lower']), 'claim endpoint'

    # --- inputs of the moment sums ---------------------------------------
    H = {int(r): n for r, n in assembly['complex_profile'].items()}
    mass = sum(r * n for r, n in H.items())
    m_c, W_c = 73, claim['live']
    deficit_c = claim['deficit']
    assert m_c * W_c - mass == deficit_c and m_c * m_c > 2 * max(H)**2, 'complex stock identity'
    bit = bit_record['nine']
    bitH = {int(r): n for r, n in bit['profile'].items()}
    word = bit_record['word']
    v, cst = word['v'], word['decoder_constant']
    L, T = 9, 32
    K = (L - 1) // 2
    m_b, W_b = 1 + 7 * L, bit['bit']['live']
    deficit_b = T * (2 * K * v - L * cst)
    assert m_b == 64 and deficit_b == assembly['bit_supplier']['derived_deficit'] == 10272
    assert m_b * W_b - sum(r * n for r, n in bitH.items()) == deficit_b
    assert m_b * m_b > 2 * max(bitH)**2, 'bit stock identity'

    b = Q(assembly['complex_lower'])
    b_c = Q(assembly['conservative_complex_lower'])
    c = Q(assembly['bit_lower'])

    # --- 1. endpoint certification ---------------------------------------
    recorded = {(row['side'], row['endpoint'], row['surcharge']): row
                for row in assembly['moments'] + assembly['conservative_moments']}
    assert len(recorded) == 6, 'six recorded moment rows'
    cases = [('bit', bitH, m_b, W_b, c, True),
             ('bit', bitH, m_b, W_b, c + ENDPOINT_STEP, True),
             ('conservative_complex', H, m_c, W_c, b_c, True),
             ('conservative_complex', H, m_c, W_c, b_c + ENDPOINT_STEP, True),
             ('complex', H, m_c, W_c, b, False),
             ('complex', H, m_c, W_c, b + ENDPOINT_STEP, False)]
    checked = 0
    for side, h, m, W, z, bad in cases:
        row = recorded[(side, str(z), bad)]
        payload, (l, u, ll, uu) = row_values(h, m, W, z, bad)
        assert payload['mercator'] == row['mercator'], 'mercator mismatch at %s %s' % (side, z)
        assert payload['base_two'] == row['base_two'], 'base_two mismatch at %s %s' % (side, z)
        accept = row['accept']
        assert (u < 1 and uu < 1) if accept else (l > 1 and ll > 1), 'sign condition'
        f = decimal_moment(h, m, W, z, bad)
        assert (f < 1) if accept else (f > 1), 'decimal sign agreement'
        with localcontext() as ctx:
            ctx.prec = 60
            tol = Decimal('1e-40')
            flo = Decimal(l.numerator) / Decimal(l.denominator)
            fhi = Decimal(u.numerator) / Decimal(u.denominator)
            assert flo - tol <= f <= fhi + tol, 'decimal inside mercator interval'
        checked += 1

    # --- 2. endpoint-to-kappa reduction ----------------------------------
    accepted = reduce_endpoint(b, c)
    conservative = reduce_endpoint(b_c, c)
    assert accepted['kappa'] == Q(assembly['kappa']), 'accepted kappa'
    assert conservative['kappa'] == Q(assembly['conservative_kappa']), 'conservative kappa'
    assert Q(Decimal(assembly['kappa_decimal'])) == accepted['kappa']
    assert Q(Decimal(assembly['conservative_kappa_decimal'])) == conservative['kappa']
    for computed, rec in ((accepted['cuts'], assembly['bootstrap']),
                          (conservative['cuts'], assembly['conservative_bootstrap'])):
        assert len(computed) == len(rec) == 7
        for got, want in zip(computed, rec):
            assert (got['exponent'], got['gap'], got['cutoff_log2']) == \
                   (want['exponent'], want['gap'], want['cutoff_log2']), 'bootstrap row'
    for red, rec in ((accepted, assembly['outer']), (conservative, assembly['conservative_outer'])):
        slacks, margins, minimum = outer_slacks(red['chain'][-1],
                                                b if red is accepted else b_c, red['kappa'])
        assert len(rec) == 47
        for name, value in rec.items():
            assert frac(value) == slacks[name], 'outer slack %s' % name
    assert all(frac(v) > 0 for v in assembly['outer'].values())
    assert all(frac(v) > 0 for v in assembly['conservative_outer'].values())

    margin_ticks = (accepted['margin'] - accepted['kappa']) / TICK
    conservative_ticks = (conservative['margin'] - conservative['kappa']) / TICK
    assert 0 < margin_ticks < 1 and 0 < conservative_ticks < 1
    assert accepted['kappa'] + TICK > accepted['margin'], 'grid floor'

    # --- 3. surcharge accounting -----------------------------------------
    delta_k = accepted['kappa'] - conservative['kappa']
    assert delta_k == Q(Decimal(assembly['native_correction_gain'])), 'native_correction_gain'
    assert delta_k == Q(2882365, 10**18)
    delta_b = b - b_c
    transfer = delta_k / delta_b
    assert delta_b == Q(2891969004600, 10**24)
    assert assembly['surcharge_model'] == {'complex': False, 'bit': True}

    # The accepted kappa under the conservative (surcharged) complex input.
    slacks_c, _, _ = outer_slacks(conservative['chain'][-1], b_c, accepted['kappa'])
    failing = sorted(n for n, v in slacks_c.items() if v <= 0)
    assert failing == ['Gaussian_arithmetic_above_kappa', 'balanced_prefix_above_kappa',
                       'compact_phase_layer_above_kappa', 'scalar_work_above_kappa'], failing
    assert conservative['kappa'] < accepted['kappa'] < b
    assert conservative['kappa'] > PREVIOUS_FRONTIER and conservative['kappa'] > BASELINE870

    # Both recorded model controls, on both engines where defined.
    l, u = mercator_moment(H, m_c, W_c, b, True)
    assert l > 1, 'model control: native endpoint rejected with old surcharge'
    l, u = mercator_moment(bitH, m_b, W_b, c + ENDPOINT_STEP, False)
    assert u < 1, 'model control: bit successor not rejected without the surcharge'
    assert assembly['model_controls'] == ['native_complex_endpoint_rejected_with_old_surcharge',
                                          'omitting_bit_surcharge_would_fail_next_endpoint_rejection']

    # --- negative controls ------------------------------------------------
    def recompute_kappa(record):
        return reduce_endpoint(Q(record['complex_lower']), Q(record['bit_lower']))['kappa']

    tampered = dict(assembly, kappa=str(accepted['kappa'] + TICK))
    detected('kappa bumped one tick', Q(tampered['kappa']) == recompute_kappa(tampered))
    detected('native_correction_gain altered', Q(Decimal('2.882366E-12')) == delta_k)
    swapped = dict(assembly, complex_lower=assembly['conservative_complex_lower'],
                   conservative_complex_lower=assembly['complex_lower'])
    detected('endpoints swapped', recompute_kappa(swapped) == Q(assembly['kappa']))
    tampered_slack = Q(1, 10**18)
    detected('outer slack replaced', tampered_slack ==
             outer_slacks(accepted['chain'][-1], b, accepted['kappa'])[0]['compact_phase_layer_above_kappa'])
    tampered_H = dict(H)
    tampered_H[48] = tampered_H[48] + 1
    detected('profile role count altered',
             row_values(tampered_H, m_c, W_c, b, False)[0]['mercator']
             == recorded[('complex', str(b), False)]['mercator'])
    detected('next grid point accepted',
             all(v > 0 for v in outer_slacks(accepted['chain'][-1], b, accepted['kappa'] + TICK)[0].values()))

    # --- summary ----------------------------------------------------------
    print('PASS frontier890 endpoint certification and reduction audit (seed 73)')
    print('  moment rows recomputed          =', checked, '(both engines + decimal signs)')
    print('  kappa                           =', accepted['kappa'])
    print('  margin - kappa                  = %.6f tick' % float(margin_ticks))
    print('  conservative margin - kappa_c   = %.6f tick' % float(conservative_ticks))
    print('  binding endpoint                = complex')
    print('  endpoint slack c-(1-beta)b      = %.6e' % float(c - (1 - BETA) * b))
    print('  accepted - conservative kappa   =', delta_k, '(=%d ticks)' % (delta_k / TICK))
    print('  endpoint gap b - b_c            = %.6e' % float(delta_b))
    print('  transfer factor                 = %.12f' % float(transfer))
    print('  guard cluster at kappa_c input  =', failing)
    print('  conservative kappa vs frontier  = above PR799 and PR870: True')
    print('  negative controls detected      = 6')


if __name__ == '__main__':
    main()
