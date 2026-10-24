#!/usr/bin/env python3
"""Two-sided parent stock envelope and exact fit band for the selected #4470 BIT stage.

Checks PROOF.md: source bindings, exhaustive small-rank models of the source
borrowed-digit formula, exact witnesses at the selected rank N=2^H1, and
rejection controls. Standard library only. Apache-2.0.
JoyboyBrian, with substantial assistance from Anthropic Claude (Claude Code).
"""
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DELTA = Q(1, 250)

BRIDGE = 'research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md'
PARAMS = 'research/kappa-rebuild/bit/BIT-ALLSIZE-PARAMETERS.json'
QT_RESULT = 'research/query-thinned-controllers/RESULT.json'
QT_PROOF = 'research/query-thinned-controllers/PROOF.md'
JH_PROOF = 'research/joint-helper-lattice/PROOF.md'
ROWS = 'notes/three-stage-cover-rows.tex'
SELECTED = 'certificates/selected-result.json'

STOCK = {
    'borrowed_digits': 'k <= D_N(ceil(e/w))*(N^2*(w-1)+ceil(log_q(B*|GL_N(F_q)|)))+ceil(log_q S_old)+1',
    'depth_bound': 'D_N(n)=floor(log_N n) for rank<=floor(n/N) children; any larger explicit integer bound is safe.',
    'reserve': 'S(e,w)=W(w)^D_N(ceil(e/w))*S_old(e,w)',
    'role_divisor': 'W(w)=B*|GL_N(F_q)|*q^(N^2*(w-1))',
}
PHRASES = {
    BRIDGE: ['A safe reserve is `W(w)^D * S_old`', 'For sufficiently large `e`, borrow `k<e/2` high digits'],
    QT_PROOF: ['Change the atom power to delta=0.004', 'the delayed-cover stock formulas', 'w=ceil(e^0.004)'],
    JH_PROOF: ['Retain the source BIT ordinary saving 0.0034, with atom exponent 0.004.'],
    ROWS: ['inherited old-leaf', 'logarithmic reserve', 'Small widths use the retained supplier directly.'],
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load_sources(override=None):
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    data = {}
    for item in pins['files']:
        raw = (ROOT / item['path']).read_bytes()
        if override and item['path'] in override:
            raw = override[item['path']](raw)
        need(hashlib.sha256(raw).hexdigest() == item['sha256'], 'source hash ' + item['path'])
        data[item['path']] = raw
    return data


def bind(data):
    """Return (H1, delta) read from the pinned selected-chain sources."""
    sel = json.loads(data[SELECTED])
    need(sel['kappa'] == '60403/20000000', 'selected record is #4470')
    res = json.loads(data[QT_RESULT])
    bit, strict = res['ordinary_BIT'], res['bit_strictification']
    H1 = strict['uniform_H1']
    need(strict['uniform_N'] == '2^%d' % H1, 'BIT uniform rank encoding')
    delta = Q(bit['atom'])
    need('2^26*N^5' in bit['prime_rule'], 'prime rule')
    ordinary = (1 - delta) * Q(bit['after_cover']) + delta * Q(384599, 10**10)
    need(ordinary == Q(bit['ordinary_saving']) == Q('0.0034363538396'), 'ordinary saving of the stage')
    need(delta > ordinary and delta < 1 - ordinary, 'adapter and stock exponent gaps')
    stock = json.loads(data[PARAMS])['stock']
    for key, text in STOCK.items():
        need(stock[key] == text, 'stock formula ' + key)
    for path, phrases in PHRASES.items():
        text = data[path].decode('utf-8')
        for phrase in phrases:
            need(phrase in text, 'source sentence in ' + path)
    return H1, delta


# ---------------------------------------------------------------- source formula, exact integers
def ilog(N, n):
    """floor(log_N n) for n >= 1."""
    D, p = 0, N
    while p <= n:
        D, p = D + 1, p * N
    return D


def ceil_log(q, x):
    c, p = 0, 1
    while p < x:
        c, p = c + 1, p * q
    return c


def gl_order(N, q):
    out = 1
    for i in range(N):
        out *= q**N - q**i
    return out


def det_mod(m, q):
    m = [row[:] for row in m]
    n, det = len(m), 1
    for c in range(n):
        piv = next((r for r in range(c, n) if m[r][c] % q), None)
        if piv is None:
            return 0
        if piv != c:
            m[c], m[piv], det = m[piv], m[c], -det
        det = det * m[c][c] % q
        inv = pow(m[c][c], -1, q)
        for r in range(c + 1, n):
            f = m[r][c] * inv % q
            m[r] = [(a - f * b) % q for a, b in zip(m[r], m[c])]
    return det % q


def brute_gl(N, q):
    from itertools import product
    return sum(1 for e in product(range(q), repeat=N * N)
               if det_mod([list(e[i * N:(i + 1) * N]) for i in range(N)], q))


def k_parent(N, chart_digits, e, w, lift=True):
    """Source parent stock D*(N^2(w-1)+ceil(log_q(B|GL_N(F_q)|))); chart_digits is the ceiling."""
    n = -(-e // w)
    D = ilog(N, n)
    lift_digits = N * N * (w - 1) if lift else 0
    return D * (lift_digits + chart_digits), D, n


def model_checks(lift=True, roles=None, E=2000, W=6, envelope=True, role_hypothesis=True):
    """Lemmas 1 and 2(a)-(c) on every (N,q,B,w,e) of a finite grid."""
    for N, q in ((2, 3), (2, 5), (3, 3)):
        need(brute_gl(N, q) == gl_order(N, q), 'GL order formula')
    counts = {'instances': 0, 'D0': 0, 'D1_over_chunk': 0, 'infeasible_2b': 0, 'fit_2c': 0}
    for N in (2, 3, 4):
        for q in (3, 5, 7):
            G = gl_order(N, q)
            need(q**(N * N - 1) < G < q**(N * N), 'GL order brackets')
            for B in (roles or (1, 2, 1000, q**(N * N))):
                cB, chart = ceil_log(q, B), ceil_log(q, B * G)
                for w in range(1, W + 1):
                    for e in range(1, E + 1):
                        k, D, n = k_parent(N, chart, e, w, lift)
                        counts['instances'] += 1
                        need((n - 1) * w < e <= n * w, 'atom count')
                        if envelope:
                            need(D * N * N * w <= k <= D * (N * N * w + cB), 'two-sided envelope')
                        if D == 0:
                            need(n < N and k == 0, 'D=0 has no parent stock')
                            counts['D0'] += 1
                        if D == 1:
                            need(k > e, 'every D=1 width overdraws the chunk')
                            counts['D1_over_chunk'] += 1
                        if D >= 1 and n <= 2 * D * N * N:
                            need(2 * k >= e, 'infeasible for n <= 2DN^2')
                            counts['infeasible_2b'] += 1
                        if (cB <= N * N or not role_hypothesis) and n >= 8 * D * N * N + 1:
                            need(4 * k < e, 'parent fit for n >= 8DN^2+1')
                            counts['fit_2c'] += 1
    need(all(counts.values()), 'every lemma branch is exercised')
    return counts


def high_depth_check(N=64, top=400):
    need(all(N**(D - 2) >= 8 * D + 1 for D in range(3, top)), 'Lemma 2(d)')
    return top - 3


# ---------------------------------------------------------------- selected scale
def bands(H1, delta):
    s = 1 - delta
    floor = lambda x: x.numerator // x.denominator
    ceil = lambda x: -((-x.numerator) // x.denominator)
    return {'no_parent_stock_max_log2e': floor(Q(H1 - 1) / s),
            'infeasible_min_log2e': ceil(Q(H1 + 1) / s),
            'infeasible_max_log2e': floor(Q(2 * H1 + 1) / s),
            'fit_min_log2e': ceil(Q(2 * H1 + 6) / s)}


def fit_derivation(H1, slack):
    """Theorem 3.3 step: (1-delta)t >= 2H1+slack gives n >= 2^(2H1+slack-1) >= 16N^2+1.

    In log2 units with N=2^H1 this is 2^(slack-1) >= 16 + 2^(-2H1)."""
    return Q(2)**(slack - 1) >= 16 + Q(1, 2**min(2 * H1, 4096))


def witness(H1, t, a=250):
    """Exact parent stock at e=2^t, a|t, atom 1/a: returns (D, infeasible, fits) for c_B <= N^2."""
    need(t % a == 0, 'witness exponent')
    u = t // a                         # w = 2^u, n = 2^(t-u) exactly
    D = (t - u) // H1                  # floor(log_N n)
    if D == 0:
        return 0, False, True
    x = t - 1 - 2 * H1 - u             # lower D*N^2*w >= 2^(t-1)  <=>  D >= 2^x
    infeasible = x <= 0 or (x < 64 and D >= 2**x)
    y = t - 2 - 2 * H1 - u             # upper D*N^2*(w+1) < 2^(t-2) <=> D < 2^y (u huge)
    fits = y > 0 and (y >= 64 or D < 2**y)
    need(not (infeasible and fits), 'witness consistency')
    return D, infeasible, fits


def oracle_checks():
    """Materialize e=2^t at reduced ranks N=2^H1 and atoms 1/a; compare witness() with big integers."""
    compared = 0
    for H1, a, top in ((2000, 250, 16000), (3, 2, 400), (5, 3, 600), (6, 4, 900), (7, 5, 900)):
        N = 2**H1
        b = bands(H1, Q(1, a))
        for t in range(a, top + 1, a):
            e, w = 2**t, 2**(t // a)
            n = -(-e // w)
            D = ilog(N, n)
            low, high = D * N * N * w, D * (N * N * w + N * N)
            got = witness(H1, t, a)
            need(got == (D, D >= 1 and 2 * low >= e, D == 0 or 4 * high < e), 'witness oracle at t=%d' % t)
            if b['infeasible_min_log2e'] <= t <= b['infeasible_max_log2e']:
                need(got[1], 'reduced-rank band is infeasible')
            if t >= b['fit_min_log2e'] and H1 >= 6:
                need(got[2], 'reduced-rank fit')
            compared += 1
    return compared


def selected_checks(H1, delta):
    b = bands(H1, delta)
    need(delta == Q(1, 250), 'selected atom')
    need(fit_derivation(H1, 6) and not fit_derivation(H1, 5), 'fit slack 6 is the least integer this derivation admits')
    need(2 + Q(1, 2**4096) <= 4, 'band top: n <= 2^(2H1+1)+1 <= 4N^2')
    span = lambda lo, hi: range(lo - lo % 250 + 250, hi - hi % 250 + 1, 250)
    lo, hi, fit, z = b['infeasible_min_log2e'], b['infeasible_max_log2e'], b['fit_min_log2e'], b['no_parent_stock_max_log2e']
    seen = {'D0': 0, 'infeasible': 0, 'fits': 0, 'undetermined': 0}
    for t in list(span(z - 2500, z)):
        D, bad, ok = witness(H1, t)
        need(D == 0, 'no parent stock below the band')
        seen['D0'] += 1
    edges = [*span(lo - 1, lo + 2500), *span(hi - 2500, hi), *span(H1 * 3 // 2, H1 * 3 // 2 + 2500)]
    for t in edges:
        D, bad, ok = witness(H1, t)
        need(1 <= D <= 2 and bad, 'infeasible band witness at t=%d' % t)
        seen['infeasible'] += 1
    last_bad, first_ok = None, None
    for t in span(hi - 5000, fit + 5000):
        D, bad, ok = witness(H1, t)
        if t >= fit:
            need(ok, 'fit witness at t=%d' % t)
        if bad:
            last_bad = t
        if ok and first_ok is None:
            first_ok = t
        seen['fits' if ok else 'infeasible' if bad else 'undetermined'] += 1
    need(last_bad is not None and first_ok is not None and last_bad < first_ok, 'single transition')
    need(hi < first_ok and last_bad <= hi + 250 and first_ok <= fit + 250, 'transition inside the proved window')
    for t in (3 * H1 * 250 // 249 + 250, 10**15, 10**18):
        t -= t % 250
        D, bad, ok = witness(H1, t)
        need(D >= 3 and ok, 'D>=3 witness fits')
        seen['fits'] += 1
    sigma_old_log2 = fit - 3 - (1 + fit).bit_length()
    return dict(b, witness_counts=seen, last_infeasible_witness=last_bad, first_fit_witness=first_ok,
                band_width_log2e=hi - lo + 1, window_bits=fit - hi,
                old_leaf_log_coefficient_allowance_log2_at_fit=sigma_old_log2)


def run(override=None, lift=True):
    data = load_sources(override)
    H1, delta = bind(data)
    result = {'status': 'PASS_SELECTED_BIT_STAGE_STOCK_BAND', 'H1': H1, 'delta': str(delta),
              'models': model_checks(lift=lift), 'lemma_2d_depths_checked': high_depth_check(),
              'reduced_rank_oracle_witnesses': oracle_checks()}
    result.update(selected_checks(H1, delta))
    return result


def controls():
    """Every control must be rejected."""
    rejected = {}
    def expect_fail(name, thunk):
        try:
            thunk()
        except ValueError as exc:
            rejected[name] = str(exc)
            return
        raise SystemExit('FAIL: control accepted: ' + name)
    expect_fail('tampered_bridge', lambda: load_sources({BRIDGE: lambda raw: raw.replace(b'k<e/2', b'k<e/3')}))
    expect_fail('no_high_matrix_lift', lambda: model_checks(lift=False, E=300, envelope=False))
    expect_fail('roles_above_q_to_N2', lambda: model_checks(roles=(7**80,), E=1500, envelope=False, role_hypothesis=False))
    expect_fail('stale_atom_3_over_1000', lambda: need(bands(25986965159937, Q(3, 1000)) == EXPECTED_BANDS, 'stale atom bands'))
    expect_fail('rank_off_by_one', lambda: need(selected_checks(25986965159938, DELTA)['fit_min_log2e'] == EXPECTED_BANDS['fit_min_log2e'], 'rank'))
    expect_fail('fit_one_bit_early', lambda: need(fit_derivation(25986965159937, 5), 'slack 5'))
    expect_fail('feasible_single_level', lambda: need(witness(25986965159937, 30000000000000)[2], 'D=1 fit'))
    return rejected


EXPECTED_BANDS = {'no_parent_stock_max_log2e': 26091330481863, 'infeasible_min_log2e': 26091330481866,
                  'infeasible_max_log2e': 52182660963729, 'fit_min_log2e': 52182660963735}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', type=Path, help='write a fresh receipt to a new path (never overwrites)')
    args = ap.parse_args()
    result = run()
    for key, value in EXPECTED_BANDS.items():
        need(result[key] == value, 'documented band ' + key)
    result['controls_rejected'] = sorted(controls())
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if args.write:
        need(not args.write.exists(), 'refuse to overwrite ' + str(args.write))
        args.write.write_text(text, encoding='utf-8')
    else:
        need((HERE / 'RESULT.json').read_text(encoding='utf-8') == text, 'stored receipt RESULT.json')
    print('%s H1=%d infeasible_log2e=[%d,%d] fit_from_log2e=%d window_bits=%d models=%d controls=%d' % (
        result['status'], result['H1'], result['infeasible_min_log2e'], result['infeasible_max_log2e'],
        result['fit_min_log2e'], result['window_bits'], result['models']['instances'], len(result['controls_rejected'])))


if __name__ == '__main__':
    try:
        main()
    except ValueError as exc:
        raise SystemExit('FAIL: ' + str(exc))
