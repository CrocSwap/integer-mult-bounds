#!/usr/bin/env python3
"""Close the six-bit fit window of the selected BIT stage's borrowed-digit prescription.

Checks PROOF.md: pinned-source bindings, an exact criterion for the depth-two borrowed
digits on small parameters, the exact-integer translation lemma on small atoms and ranks,
exact exponent arithmetic at the selected rank N = 2^H1, and rejection controls.
Standard library only. Produced by Nick Petalas. Apache-2.0.
"""
import argparse
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RECEIPT = HERE / 'RESULT.json'
SCHEMA = 'bit-stock-band-threshold/1'

A_SEL = 250                 # atom exponent 1/250: w = ceil(e^(1/250))
TAU_BITS = 2 * 10**11       # window width 2^(-TAU_BITS) in log2 e
LIMIT = 10**6               # loop bound for every integer search

QT_RESULT = 'research/query-thinned-controllers/RESULT.json'
PARAMS = 'research/kappa-rebuild/bit/BIT-ALLSIZE-PARAMETERS.json'
BRIDGE = 'research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md'
BAND_PROOF = 'research/selected-bit-stage-stock-band/PROOF.md'
BAND_README = 'research/selected-bit-stage-stock-band/README.md'
OLD_LEAF = 'research/selected-old-leaf-reserve/README.md'

STOCK = {
    'borrowed_digits': 'k <= D_N(ceil(e/w))*(N^2*(w-1)+ceil(log_q(B*|GL_N(F_q)|)))+ceil(log_q S_old)+1',
    'depth_bound': 'D_N(n)=floor(log_N n) for rank<=floor(n/N) children; any larger explicit integer bound is safe.',
    'reserve': 'S(e,w)=W(w)^D_N(ceil(e/w))*S_old(e,w)',
    'role_divisor': 'W(w)=B*|GL_N(F_q)|*q^(N^2*(w-1))',
}
PHRASES = {
    BRIDGE: ['A safe reserve is `W(w)^D * S_old`', 'For sufficiently large `e`, borrow `k<e/2` high digits'],
    BAND_PROOF: ['the undetermined window is `4N^2 < n <= 16N^2`', '`t = 52182660963735`',
                 'between `t = 52182660963729` and `t = 52182660963735`', 'k_par < e/4'],
    BAND_README: ['3. **Close the six-bit window.**', 'depends on', '`c_B` and the precise `S_old`',
                  '`c_B <= N^2`'],
    OLD_LEAF: ['`S_old = 1`', 'old-leaf term contributes exactly one digit and `k = k_par + 1`',
               'this gives `k_old ≤ 103` digits',
               'The six-bit window of #4954 remains.'],
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


# ----------------------------------------------------------------------- source binding
def load_sources(tamper=None):
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    data, digests = {}, {}
    for item in pins['files']:
        if item['usage'] != 'input':
            continue
        raw = (ROOT / item['path']).read_bytes()
        if tamper and item['path'] == tamper[0]:
            raw = tamper[1](raw)
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == item['sha256'], 'source hash ' + item['path'])
        data[item['path']], digests[item['path']] = raw, digest
    need(set(data) == {QT_RESULT, PARAMS, BRIDGE, BAND_PROOF, BAND_README, OLD_LEAF}, 'pinned input set')
    return data, digests


def bind(data):
    """Return H1 read from the pinned selected-stage sources; check the stock formula."""
    res = json.loads(data[QT_RESULT])
    bit, strict = res['ordinary_BIT'], res['bit_strictification']
    H1 = strict['uniform_H1']
    need(isinstance(H1, int) and strict['uniform_N'] == '2^%d' % H1, 'BIT uniform rank encoding')
    need(Q(bit['atom']) == Q(1, A_SEL), 'atom exponent 1/250')
    need('2^26*N^5' in bit['prime_rule'], 'prime rule')
    stock = json.loads(data[PARAMS])['stock']
    for key, text in STOCK.items():
        need(stock[key] == text, 'stock formula ' + key)
    for path, phrases in PHRASES.items():
        text = data[path].decode('utf-8')
        for phrase in phrases:
            need(phrase in text, 'source sentence in %s: %s' % (path, phrase))
    return H1


# ------------------------------------------------------- the source formula, exact integers
def ilog(N, n):
    """floor(log_N n) for n >= 1."""
    need(N >= 2 and n >= 1, 'ilog domain')
    d, p = 0, N
    for _ in range(LIMIT):
        if p > n:
            return d
        d, p = d + 1, p * N
    raise ValueError('ilog limit')


def ceil_log(q, x):
    """Least c with q^c >= x, for x >= 1."""
    need(q >= 2 and x >= 1, 'ceil_log domain')
    c, p = 0, 1
    for _ in range(LIMIT):
        if p >= x:
            return c
        c, p = c + 1, p * q
    raise ValueError('ceil_log limit')


def gl_order(N, q):
    out = 1
    for i in range(N):
        out *= q**N - q**i
    return out


def iroot(x, k):
    """floor(x^(1/k)) by bisection."""
    lo, hi = 0, 1 << (x.bit_length() // k + 1)
    for _ in range(hi.bit_length() + 2):
        mid = (lo + hi + 1) // 2
        lo, hi = (mid, hi) if mid**k <= x else (lo, mid - 1)
    need(lo**k <= x < (lo + 1)**k, 'iroot')
    return lo


def ceil_root(e, A):
    """Least w with w^A >= e, i.e. w = ceil(e^(1/A))."""
    r = iroot(e, A)
    return r if r**A == e else r + 1


def stock(N, cG, e, w, k_old):
    """Borrowed digits k = D(N^2(w-1)+cG)+k_old with D = floor(log_N ceil(e/w))."""
    n = -(-e // w)
    D = ilog(N, n)
    return D * (N * N * (w - 1) + cG) + k_old, D, n


# ------------------------------------------------------------------ Lemma 1 and Lemma 2
def role_grid(N, q):
    """Role counts B with c_B = 0..N^2+1: B = q^j and q^j + 1."""
    return sorted({q**j + s for j in range(N * N + 2) for s in (0, 1)})


def check_envelope(cases=((2, 3), (2, 5), (3, 3), (3, 5), (4, 3), (2, 7), (5, 3))):
    count = 0
    for N, q in cases:
        G = gl_order(N, q)
        need(q**(N * N - 1) < G < q**(N * N), 'GL order bounds %d %d' % (N, q))
        for B in role_grid(N, q):
            cG, cB = ceil_log(q, B * G), ceil_log(q, B)
            need(N * N <= cG <= N * N + cB, 'envelope %d %d %d' % (N, q, B))
            count += 1
    return count


def d2_threshold(N, w, delta, k_old, mutate=None):
    """Claimed exact depth-two criterion: fits iff e > 4(N^2 w + delta) + 2 k_old."""
    base = 4 * (N * N * w + delta) + 2 * k_old
    if mutate == 'off_by_one':
        return base - 1
    if mutate == 'ignore_chart':
        return 4 * N * N * w + 2 * k_old
    if mutate == 'factor_two':
        return 2 * (N * N * w + delta) + 2 * k_old
    return base


def check_d2_criterion(mutate=None):
    """For every depth-two width, the source formula agrees with the claimed criterion."""
    count = 0
    for N, qs, wmax in ((2, (3, 5, 7), 6), (3, (3, 5, 7), 6), (4, (3, 5), 5), (5, (3,), 3)):
        for q in qs:
            G = gl_order(N, q)
            for B in role_grid(N, q):
                cG = ceil_log(q, B * G)
                delta = cG - N * N
                need(0 <= delta <= ceil_log(q, B), 'chart excess within c_B')
                for w in range(1, wmax + 1):
                    for k_old in (1, 2, 5):
                        thr = d2_threshold(N, w, delta, k_old, mutate)
                        for e in range((N * N - 1) * w + 1, (N**3 - 1) * w + 1):
                            k, D, _ = stock(N, cG, e, w, k_old)
                            need(D == 2, 'depth two range')
                            need((2 * k < e) == (e > thr), 'criterion N=%d q=%d B=%d w=%d e=%d' % (N, q, B, w, e))
                            count += 1
    return count


# --------------------------------------------------- exact-integer translation lemma (small)
def pred_inf(e, N, A, s=2):
    """e^(A-1) <= (2^s N^2)^A, i.e. e^((A-1)/A) <= 2^s N^2."""
    return e**(A - 1) <= ((1 << s) * N * N)**A


def pred_fit(e, N, A, M=4, c=10):
    """e > c N^2 and (e - c N^2)^A >= (M N^2)^A e: forces e >= M N^2 e^(1/A) + c N^2."""
    return e > c * N * N and (e - c * N * N)**A >= (M * N * N)**A * e


def edge_widths(N, A):
    """Largest e with pred_inf, least e from which pred_fit holds (pred_fit is monotone)."""
    e_inf = iroot(((4 * N * N)**A), A - 1)
    lo, hi = 10 * N * N + 1, 2 * e_inf + 10 * N * N + 2
    need(pred_fit(hi, N, A), 'fit predicate at the upper end')
    for _ in range(hi.bit_length() + 2):
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if pred_fit(mid, N, A) else (mid + 1, hi)
    return e_inf, lo


def scan_translation(A, N, lo, hi, s_inf=2, M=4, c=10):
    """Check T1 and T2 on every e in [lo, hi] with the source formula's extreme readings."""
    w = ceil_root(lo, A)
    n_inf = n_fit = n_gap = 0
    for e in range(lo, hi + 1):
        for _ in range(LIMIT):
            if w**A >= e:
                break
            w += 1
        n = -(-e // w)
        D = ilog(N, n)
        if D >= 1 and pred_inf(e, N, A, s_inf):          # best reading: chart excess 0, k_old = 1
            need(2 * (D * N * N * w + 1) >= e, 'T1 violated A=%d N=%d e=%d' % (A, N, e))
            n_inf += 1
        elif D == 2 and pred_fit(e, N, A, M, c):         # worst reading: excess N^2, k_old = N^2
            need(2 * (2 * (N * N * (w - 1) + 2 * N * N) + N * N) < e, 'T2 violated A=%d N=%d e=%d' % (A, N, e))
            n_fit += 1
        elif D >= 2:
            n_gap += 1
    return n_inf, n_fit, n_gap


def check_translation(s_inf=2, M=4, c=10):
    rows = []
    for N, atoms, full in ((8, (2, 3, 4, 5), True), (16, (2, 3, 4, 5), True), (32, (2, 3, 4, 5), True)):
        for A in atoms:
            e_inf, e_fit = edge_widths(N, A)
            need(e_inf < e_fit, 'infeasible edge below fit edge')
            lo, hi = max(1, e_inf - 300), e_fit + 300
            if full and hi <= 150000:
                lo = 1
            n_inf, n_fit, n_gap = scan_translation(A, N, lo, hi, s_inf, M, c)
            rows.append([N, A, lo, hi, e_inf, e_fit, n_inf, n_fit, n_gap])
    return rows


def check_deeper_depths(N=64, top=400):
    """Lemma 2(d): N^(D-2) >= 8D+1 for every D >= 3 up to a bound, at N = 64."""
    for D in range(3, top):
        need(N**(D - 2) >= 8 * D + 1, 'depth three and beyond D=%d' % D)
    return top - 3


# ------------------------------------------------ exact transition at large rank (big integers)
def exact_transition(N, A, delta, k_old, w_lo, w_hi):
    """Least e0 such that every width in [e0, w_hi^A] fits at depth two, by blocks of w.

    Block w is ((w-1)^A, w^A]; there the prescription fits iff e > 4*(N^2*w + delta) + 2*k_old.
    """
    def thr(w):
        return 4 * (N * N * w + delta) + 2 * k_old
    need(w_lo < w_hi and w_hi - w_lo <= 64, 'block range')
    need((w_hi - 1)**A > thr(w_hi), 'top block fits entirely')
    for w in range(w_hi - 1, w_lo, -1):
        if (w - 1)**A > thr(w):                       # block w fits entirely: keep descending
            continue
        return thr(w) + 1 if thr(w) < w**A else w**A + 1
    raise ValueError('no transition inside the block range')


def check_large_rank(s_inf=2, ranks=((40, 2), (41, 3), (51, 5), (59, 11), (100, 2), (101, 3))):
    """Exact transition widths at N = 2^h: best and worst readings against both edges."""
    rows = []
    for h, A in ranks:
        N = 1 << h
        e_inf = iroot(((1 << s_inf) * N * N)**A, A - 1)
        _, e_fit = edge_widths(N, A)
        w_lo, w_hi = ceil_root(e_inf, A) - 2, ceil_root(e_fit, A) + 3
        best = exact_transition(N, A, 0, 1, w_lo, w_hi)
        worst = exact_transition(N, A, N * N, N * N, w_lo, w_hi)
        need(e_inf < best <= worst <= e_fit, 'transition inside the bracket h=%d A=%d' % (h, A))
        need(N * N <= ceil_root(e_inf, A)**(A - 1) and ilog(N, -(-e_inf // ceil_root(e_inf, A))) == 2, 'depth two')
        rows.append([h, A, (best - e_inf) * 1000 // (N * N), (worst - e_inf) * 1000 // (N * N),
                     (e_fit - e_inf) * 1000 // (N * N)])
    return rows


# ----------------------------------------------------- exact exponent arithmetic at rank N
def t_star(H1, A, mlog):
    """Real t with (A-1)/A * t = 2 H1 + mlog, i.e. e^((A-1)/A) = 2^mlog N^2."""
    return Q(A * (2 * H1 + mlog), A - 1)


def inf_by_exponent(H1, t, A, mlog):
    return (A - 1) * t <= A * (2 * H1 + mlog)


def fit_by_exponent(H1, t, A, mlog, c):
    """e = 2^t satisfies (e - c N^2)^A >= (2^mlog N^2)^A e, hence e >= 2^mlog N^2 e^(1/A) + c N^2."""
    margin = (A - 1) * t - A * (2 * H1 + mlog)         # exponent of 2 in the leading ratio
    x_small = t - 2 * H1 >= (1000 * c).bit_length()    # c N^2 / e <= 1/1000
    base = Q(1000, 999)**A < 2                        # (1 - x)^(-A) < 2 for x <= 1/1000
    return margin >= 1 and x_small and base


def depth_at_pow2(H1, t, A):
    """floor(log_N ceil(e/w)) at e = 2^t from the sign of (A-1) t - A k H1 (never zero here)."""
    D = 0
    for k in range(1, 8):
        gap = (A - 1) * t - A * k * H1
        need(gap != 0, 'depth boundary hit exactly')
        if gap > 0:
            D = k
    return D


def classify(H1, t, A=A_SEL):
    """('k<e/2' status, 'k_par<e/4' status) of the prescription at e = 2^t, S_old = 1."""
    D = depth_at_pow2(H1, t, A)
    if D == 0:
        return D, 'no-cover', 'no-cover'
    if D == 1:
        return D, 'infeasible', 'fails'
    half = ('infeasible' if inf_by_exponent(H1, t, A, 2) else
            'fits' if fit_by_exponent(H1, t, A, 2, 10) else 'undecided')
    guard = ('fails' if inf_by_exponent(H1, t, A, 3) else
             'holds' if fit_by_exponent(H1, t, A, 3, 16) else 'undecided')
    return D, half, guard


def selected_table(H1, A=A_SEL):
    t0 = int(t_star(H1, A, 2))
    rows = []
    for t in range(t0 - 6, t0 + 9):
        D, half, guard = classify(H1, t, A)
        rows.append({'t': t, 'depth': D, 'k_lt_e_over_2': half, 'k_par_lt_e_over_4': guard})
    return rows


def decimal(frac, digits=30):
    whole = frac.numerator // frac.denominator
    rest = frac - whole
    return '%d.%s' % (whole, str(rest.numerator * 10**digits // rest.denominator).zfill(digits))


def check_selected(H1, A=A_SEL):
    """Exact facts used by T1-T3 at the selected rank, as integer comparisons."""
    ts, tg = t_star(H1, A, 2), t_star(H1, A, 3)
    need(ts == Q(500 * (H1 + 1), 249) and tg - ts == Q(250, 249), 'threshold values')
    need(ts / A >= TAU_BITS + 3, 'rho = 2^(-t/250) <= 2^(-(TAU_BITS+3))')
    need(H1 >= 64 and ts > 2 * H1 + 1, 'selected rank domain')
    t0 = int(ts)
    need(t0 == 52182660963730 and decimal(ts).startswith('52182660963730.9236947791'), 'threshold decimal')
    need(not inf_by_exponent(H1, t0 + 1, A, 2) and inf_by_exponent(H1, t0, A, 2), 'integer split of k<e/2')
    need(fit_by_exponent(H1, t0 + 1, A, 2, 10) and not fit_by_exponent(H1, t0, A, 2, 10), 'integer fit of k<e/2')
    tg0 = int(tg)
    need(inf_by_exponent(H1, tg0, A, 3) and not inf_by_exponent(H1, tg0 + 1, A, 3), 'integer split of guard')
    need(fit_by_exponent(H1, tg0 + 1, A, 3, 16), 'integer fit of guard')
    t1 = int(Q(A * H1, A - 1)) + 1                      # first integer t with depth >= 1
    need(depth_at_pow2(H1, t1 - 1, A) == 0 and depth_at_pow2(H1, t1, A) == 1, 'depth-one onset')
    need(t1 == 26091330481865 and depth_at_pow2(H1, t0 - 1, A) == 2, 'onset and depth two before t*')
    return t0, tg0, decimal(ts), decimal(tg), t1


# ----------------------------------------------------------------------------- controls
def control_tamper():
    def flip(raw):
        return raw.replace(b'25986965159937', b'25986965159938', 1)
    try:
        load_sources((QT_RESULT, flip))
    except ValueError:
        return True
    return False


def control_raises(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def controls(H1, table):
    out = {
        'tampered_selected_rank_rejected': control_tamper(),
        'off_by_one_criterion_rejected': control_raises(lambda: check_d2_criterion('off_by_one')),
        'ignored_chart_excess_rejected': control_raises(lambda: check_d2_criterion('ignore_chart')),
        'factor_two_criterion_rejected': control_raises(lambda: check_d2_criterion('factor_two')),
        'inflated_infeasible_edge_rejected': control_raises(lambda: scan_translation(2, 8, 1, 70000, s_inf=3)),
        'deflated_fit_edge_rejected': control_raises(lambda: scan_translation(2, 8, 1, 70000, M=2)),
        'inflated_large_rank_edge_rejected': control_raises(lambda: check_large_rank(s_inf=3)),
        'shifted_rank_changes_table': selected_table(H1 + 1) != table,
        'fit_below_threshold_rejected': not fit_by_exponent(H1, int(t_star(H1, A_SEL, 2)), A_SEL, 2, 10),
        'infeasible_above_threshold_rejected': not inf_by_exponent(H1, int(t_star(H1, A_SEL, 2)) + 1, A_SEL, 2),
    }
    need(all(out.values()), 'rejection controls: %s' % [k for k, v in out.items() if not v])
    return out


# ------------------------------------------------------------------------------ receipt
def build_receipt():
    data, digests = load_sources()
    H1 = bind(data)
    t0, tg0, ts_dec, tg_dec, t1 = check_selected(H1)
    table = selected_table(H1)
    rows = check_translation()
    deeper = check_deeper_depths()
    need(table[0]['t'] == t0 - 6 and any(r['t'] == t0 and r['k_lt_e_over_2'] == 'infeasible' for r in table),
         'table rows')
    return {
        'schema': SCHEMA, 'sources': digests, 'H1': H1, 'atom_denominator': A_SEL,
        'tau_log2_exponent': -TAU_BITS, 'depth_one_onset_t': t1,
        't_star_k_lt_e_over_2': {'fraction': '500*(H1+1)/249', 'floor': t0, 'decimal': ts_dec},
        't_star_k_par_lt_e_over_4': {'fraction': '250*(2*H1+3)/249', 'floor': tg0, 'decimal': tg_dec},
        'selected_table': table,
        'envelope_cases': check_envelope(),
        'depth_two_instances': check_d2_criterion(),
        'translation_scans': {'columns': ['N', 'A', 'e_lo', 'e_hi', 'e_inf_edge', 'e_fit_edge',
                                          'n_inf', 'n_fit', 'n_gap'], 'rows': rows},
        'deeper_depth_checks': deeper,
        'large_rank_transitions': {'columns': ['h', 'A', 'best_minus_edge_milli_N2', 'worst_minus_edge_milli_N2',
                                               'fit_edge_minus_edge_milli_N2'], 'rows': check_large_rank()},
        'controls': controls(H1, table),
    }


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', metavar='PATH', help='write a fresh receipt (never overwrites)')
    args = ap.parse_args(argv)
    receipt = build_receipt()
    text = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    if args.write:
        out = Path(args.write)
        need(not out.exists(), 'receipt path exists: ' + str(out))
        out.write_text(text, encoding='utf-8')
        print('wrote', out)
        return 0
    need(RECEIPT.read_text(encoding='utf-8') == text, 'stored RESULT.json differs from the recomputed receipt')
    print('PASS_BIT_STOCK_BAND_THRESHOLD t*=%s guard_t*=%s depth2_instances=%d scans=%d large_rank=%d controls=%d' % (
        receipt['t_star_k_lt_e_over_2']['decimal'], receipt['t_star_k_par_lt_e_over_4']['decimal'],
        receipt['depth_two_instances'], len(receipt['translation_scans']['rows']),
        len(receipt['large_rank_transitions']['rows']), len(receipt['controls'])))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
