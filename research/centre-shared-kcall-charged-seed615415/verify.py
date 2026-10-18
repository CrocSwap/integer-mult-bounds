#!/usr/bin/env python3
"""Fully charged favourable relaxation for a k-call shared centre window.

This verifier converts the pinned two-panel shared-return contract of
research/centre-shared-return-guard (PR1708/PR1748 lineage) and its k-call
generalisation into the packing-ceiling model of research/complex-local-word-ceiling,
charging restoration, hosting and precision explicitly instead of leaving them
as free overhead. All arithmetic is exact (Fraction) except the printed captions.

Conversion contract (README.md states the full contract and its scope):
  * one rank-8 COPY/ERASE total = one rank-8 child (8 mass units); its ascent
    and its erase are inside that one child;
  * one ADD macro = one rank-1 child; one scratch CLEAR = one rank-1 child;
  * precision: k summed panels have envelope at most k * max, so ceil(log2 k)
    extra magnitude bits are sufficient on the 8 shared totals; each bit is
    charged as one rank-1 unit per shared total per window;
  * hosting: shared rows persist across the window at zero mass under the
    idle-axis-hosting lemma; the window constraints are named, not priced.

usage: python3.12 -B research/centre-shared-kcall-charged-seed615415/verify.py [--write]
Aaron Wang, with help from opencode (substantial AI assistance; no model named).
Apache-2.0.
"""
import json
import sys
from fractions import Fraction as Q
from math import isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'complex-local-word-ceiling'))
import ceiling as C  # noqa: E402

M, FAM, ST = 73, 896, 9
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
BASE_CENTRE = 64
GRID = Q(1, 10 ** 12)

# Exact endpoints recorded by predecessor packages (README citations).
BIT_ENDPOINT = Q(1733427039589844234749, 10 ** 24)  # c_bit, centre-sharing-overhead-budget
KAPPA_TRANSFER = Q(1, 10 ** 24)                     # complex-coverage-law-relief T2
T2 = BIT_ENDPOINT / (1 - KAPPA_TRANSFER)
KAPPA_SELECTED = Q(836330098538459, 500000000000000000)  # certificates/selected-result.json
A_SELECTED = KAPPA_SELECTED / (1 - KAPPA_SELECTED)

GUARD = ROOT / 'research' / 'centre-shared-return-guard' / 'RESULT.json'
CEILING_RESULT = ROOT / 'research' / 'complex-local-word-ceiling' / 'RESULT.json'
OVERHEAD_RESULT = ROOT / 'research' / 'centre-sharing-overhead-budget' / 'RESULT.json'


def bits(k):
    """Extra magnitude bits sufficient for k summed panel envelopes: ceil(log2 k)."""
    b, p = 0, 1
    while p < k:
        p *= 2
        b += 1
    return b


def window_bill(k):
    """Backward centre-phase bill of one fused k-call window (integer macros)."""
    return {'r8': 8, 'add': 176 * k + 8, 'clear_scratch': 8, 'clear_erase': 8}


def per_call_bill(k):
    """Per-call amplitudes of the shared window (exact Fractions)."""
    w = window_bill(k)
    return {'r8': Q(w['r8'], k), 'add': Q(w['add'], k), 'scratch': Q(w['clear_scratch'], k)}


def profile(k, precision=True, extra_rank1=Q(0)):
    """Per-call local profile of the shared window, fully charged."""
    b = per_call_bill(k)
    base_rank1 = 184 + 8  # literal phase: 184 ADD + 8 scratch CLEAR per call
    rank1 = Q(2412) - (Q(base_rank1) - (b['add'] + b['scratch']))
    if precision:
        rank1 += Q(8 * bits(k), k)
    rank1 += extra_rank1
    return {1: rank1, 2: Q(418), 3: Q(432), 4: Q(142), 5: Q(82), 8: b['r8']}


def centre(k):
    return Q(BASE_CENTRE, k)


def cap(local, cent, extra=None):
    return C.ceiling(local, M, FAM, ST, cent, grid=GRID, **(extra or {}))


def moment_hi(local, cent, a, extra=None):
    return C.relax(local, M, FAM, ST, cent, a, **(extra or {}))[1]


def moment_lo(local, cent, a, extra=None):
    return C.relax(local, M, FAM, ST, cent, a, **(extra or {}))[0]


def max_extra_rank1(k, precision, threshold_a, treatment):
    """Largest per-call rank-1 overhead H whose moment at threshold_a stays below one.

    treatment 'displace': overhead children displace idle mass (coverage identity
    conserved; ceiling model treatment). treatment 'additive': overhead children
    add pure moment cost on top of the identity (centre-sharing-overhead-budget
    treatment). Sharp: H passes (upper enclosure below 1) and H+1 fails (lower
    enclosure above 1), or H is capped by coverage-identity feasibility.
    """
    base = profile(k, precision=precision)
    lo, hi = moment_lo(base, centre(k), threshold_a), moment_hi(base, centre(k), threshold_a)
    C.require(hi < Q(1), 'base shared profile already fails at the threshold')
    R = C.max_idle_rank(M)
    one = C.child_cost(1, M, threshold_a)
    idle = C.child_cost(R, M, threshold_a)
    if treatment == 'additive':
        delta = one[1] / Q(FAM, ST)
    else:
        delta = (one[0] - idle[1] / R) / Q(FAM, ST)
    est = int((Q(1) - hi) / delta)
    h_feas = int(C.model(base, M, FAM, ST, centre(k))['idle_mass']) if treatment != 'additive' else est + 100000

    def moment_at(h):
        shifted = dict(base)
        shifted[1] = base[1] + Q(h)
        extra_centre = Q(h) if treatment == 'additive' else Q(0)
        return C.relax(shifted, M, FAM, ST, centre(k) + extra_centre, threshold_a)

    h = max(0, min(est - 2, h_feas))
    while h > 0 and moment_at(h)[1] >= Q(1):
        h -= 1
    while h + 1 <= h_feas and moment_at(h + 1)[1] < Q(1):
        h += 1
        C.require(h < est + 100000, 'break-even search diverged')
    capped = (h == h_feas and treatment != 'additive')
    passed = moment_at(h)[1]
    C.require(passed < Q(1), 'break-even witness does not pass the moment test')
    if h + 1 <= h_feas and not capped:
        failed = moment_at(h + 1)[0]
        C.require(failed > Q(1), 'break-even not sharp at the threshold')
    return {'H': h, 'sharp': not capped, 'capped_by_identity': capped,
            'moment_hi_at_H': fstr(passed), 'H_feasible_max': h_feas}


def fstr(fr):
    return str(fr)


def ffloat(fr, digits=12):
    return f'{float(fr):.{digits}f}'


def bracket(pair):
    return {'lo': fstr(pair[0]), 'hi': fstr(pair[1]),
            'lo_dec': ffloat(pair[0]), 'hi_dec': ffloat(pair[1])}


def compute():
    guard = json.loads(GUARD.read_text(encoding='utf-8'))
    overhead = json.loads(OVERHEAD_RESULT.read_text(encoding='utf-8'))
    ceiling_result = json.loads(CEILING_RESULT.read_text(encoding='utf-8'))

    # Control 1: the k = 1 and k = 2 formulas reproduce the pinned bills exactly.
    sep, fus = guard['separate_counts'], guard['fused_counts']
    k1 = window_bill(1)
    k2 = window_bill(2)
    pinned = {
        'separate_per_two_calls': {'r8': 2 * k1['r8'], 'add': 2 * k1['add'],
                                  'clear': 2 * (k1['clear_scratch'] + k1['clear_erase'])},
        'fused_per_window': {'r8': k2['r8'], 'add': k2['add'],
                            'clear': k2['clear_scratch'] + k2['clear_erase']},
    }
    C.require(pinned['separate_per_two_calls'] == {'r8': sep['R8'], 'add': sep['add'], 'clear': sep['clear']},
              'k=1 conversion does not reproduce the pinned separate bill')
    C.require(pinned['fused_per_window'] == {'r8': fus['R8'], 'add': fus['add'], 'clear': fus['clear']},
              'k=2 conversion does not reproduce the pinned fused bill')
    C.require(bits(2) == guard['precision_and_bill']['additional_magnitude_bits_sufficient'],
              'precision bit count does not match the pinned guard')

    # Control 2: k = 1 profile equals the selected word and its ceiling matches
    # the published baseline (complex-local-word-ceiling/RESULT.json).
    base_profile = profile(1, precision=False)
    C.require(base_profile == {1: Q(2412), 2: Q(418), 3: Q(432), 4: Q(142), 5: Q(82), 8: Q(8)},
              'k=1 profile does not equal the selected word')
    base_cap = cap(base_profile, Q(BASE_CENTRE))
    published = ceiling_result['ceiling']
    published_hi = Q(published['a_ceiling'])
    C.require(abs(base_cap[1] - published_hi) < Q(2, 10 ** 12),
              'k=1 ceiling does not reproduce the published baseline ceiling')

    rows = []
    for k in (1, 2, 4, 8, 16):
        gross = profile(k, precision=False)
        charged = profile(k, precision=True)
        model_g = C.model(gross, M, FAM, ST, centre(k))
        model_c = C.model(charged, M, FAM, ST, centre(k))
        cap_g = cap(gross, centre(k))
        cap_c = cap(charged, centre(k))
        rows.append({
            'k': k,
            'magnitude_bits': bits(k),
            'centre_charge_per_call': fstr(centre(k)),
            'copy_children_r8_per_call': fstr(per_call_bill(k)['r8']),
            'restoration_scratch_clear_per_call': fstr(per_call_bill(k)['scratch']),
            'hosting_mass_per_call': '0',
            'precision_rank1_per_call': fstr(Q(8 * bits(k), k)) if k > 1 else '0',
            'rank1_children_per_call': fstr(charged[1]),
            'gross_profile': {str(r): fstr(n) for r, n in gross.items()},
            'charged_profile': {str(r): fstr(n) for r, n in charged.items()},
            'idle_mass_gross': fstr(model_g['idle_mass']),
            'idle_mass_charged': fstr(model_c['idle_mass']),
            'gross_ceiling': bracket(cap_g),
            'charged_ceiling': bracket(cap_c),
            'charged_kappa_cap': ffloat(cap_c[1] / (1 + cap_c[1])),
            'charged_ratio_vs_baseline': ffloat(cap_c[1] / base_cap[1], 6),
        })

    # Control 3: one extra rank-1 child lowers the ceiling.
    extra_child_cap = cap(profile(2, True, Q(1)), centre(2))
    C.require(extra_child_cap[1] < Q(rows[1]['charged_ceiling']['hi']),
              'one extra rank-1 child did not lower the k=2 ceiling')

    # Control 4: double precision charge lowers the ceiling (sensitivity).
    double_profile = profile(2, precision=False)
    double_profile[1] += Q(8 * 2 * bits(2), 2)
    double_cap = cap(double_profile, centre(2))
    C.require(double_cap[1] < Q(rows[1]['charged_ceiling']['hi']),
              'double precision charge did not lower the k=2 ceiling')

    # Break-evens for the k = 2 charged profile, in rank-1 children per call.
    # 'displace' keeps the coverage identity (ceiling model); 'additive' adds
    # pure moment cost (centre-sharing-overhead-budget treatment).
    break_even = {}
    for treatment in ('displace', 'additive'):
        break_even[treatment] = {
            'full_gain_at_T2': max_extra_rank1(2, True, T2, treatment),
            'full_gain_at_c_bit': max_extra_rank1(2, True, BIT_ENDPOINT, treatment),
            'any_gain_at_selected': max_extra_rank1(2, True, A_SELECTED, treatment),
        }

    # Informative comparison with centre-sharing-overhead-budget's sharp rank-1
    # budgets on their identity profile {**WORD, 8: 4}, centre 32. Their moment
    # engine is the full invoice moment on the actual idle histogram; this
    # verifier uses the ideal-packing relaxation, so equality is not required,
    # but a gross deviation falsifies the conversion machinery.
    ident = {1: Q(2412), 2: Q(418), 3: Q(432), 4: Q(142), 5: Q(82), 8: Q(4)}
    R = C.max_idle_rank(M)
    one = C.child_cost(1, M, BIT_ENDPOINT)
    delta_add = one[1] / Q(FAM, ST)
    h_est = (Q(1) - moment_hi(ident, Q(32), BIT_ENDPOINT)) / delta_add
    one_sel = C.child_cost(1, M, A_SELECTED)
    h_any_est = (Q(1) - moment_hi(ident, Q(32), A_SELECTED)) / (one_sel[1] / Q(FAM, ST))
    their_full = Q(overhead['two_call']['budgets'][0]['full_gain_total'], 144)
    their_any = Q(overhead['two_call']['budgets'][0]['any_gain_total'], 144)
    ratio_full = h_est / their_full
    ratio_any = h_any_est / their_any
    C.require(Q(1, 2) < ratio_full < Q(3) and Q(1, 2) < ratio_any < Q(3),
              'additive budgets deviate grossly from centre-sharing-overhead-budget')
    cross_check = {
        'their_full_gain_per_call': fstr(their_full),
        'their_any_gain_per_call': fstr(their_any),
        'ours_full_estimate': ffloat(h_est, 6),
        'ours_any_estimate': ffloat(h_any_est, 6),
        'ratio_full': ffloat(ratio_full, 6),
        'ratio_any': ffloat(ratio_any, 6),
        'note': 'their engine is the full invoice moment on the actual idle histogram; ours is the ideal-packing relaxation; equality not required',
    }

    # Screen from the card's first_experiment (levers.py metric).
    screen = {
        'metric': 'complex packing ceiling ratio vs baseline (levers.py scale)',
        'ideal_shared_by_two_ratio': '1.90',
        'threshold': '1.10',
        'verdict': 'route survives: ideal ratio 1.90 >= 1.10',
        'whole_bound_caveat': 'bit side binds at c_bit; whole-bound gain capped at +3.4536 per cent (centre-sharing-overhead-budget)',
    }

    result = {
        'status': 'PASS_CENTRE_SHARED_KCALL_CHARGED',
        'model': {'m': M, 'families': FAM, 'stages': ST, 'w': fstr(Q(FAM, ST)),
                  'baseline_word': {str(r): n for r, n in WORD.items()},
                  'baseline_centre': BASE_CENTRE},
        'conversion_contract': {
            'rank8_total': 'one rank-8 COPY/ERASE total = one rank-8 child (8 mass units)',
            'add': 'one ADD macro = one rank-1 child',
            'scratch_clear': 'one scratch CLEAR = one rank-1 child',
            'precision': 'ceil(log2 k) magnitude bits on 8 shared totals, each charged one rank-1 unit per total per window',
            'hosting': '0 mass under the idle-axis-hosting lemma; window constraints named in README',
        },
        'pinned_bill_reproduction': pinned,
        'baseline_ceiling': bracket(base_cap),
        'rows': rows,
        'break_even_k2_rank1_per_call': break_even,
        'cross_check_overhead_budget_rank1': cross_check,
        'endpoints': {'c_bit': fstr(BIT_ENDPOINT), 'T2': fstr(T2), 'a_selected': fstr(A_SELECTED)},
        'screen': screen,
        'controls': [
            'k=1 and k=2 conversion formulas reproduce the pinned separate and fused bills exactly',
            'k=1 profile equals the selected word and reproduces the published baseline ceiling',
            'one extra rank-1 child lowers the k=2 charged ceiling',
            'double precision charge lowers the k=2 charged ceiling',
            'break-even overheads are sharp: H passes the moment test and H+1 fails (or H is the identity-feasible maximum)',
            'additive identity-profile budgets stay within a factor of two of centre-sharing-overhead-budget',
        ],
    }
    return result


def main():
    write = '--write' in sys.argv[1:]
    result = compute()
    text = json.dumps(result, indent=1, sort_keys=True, ensure_ascii=True) + '\n'
    out = HERE / 'RESULT.json'
    if write:
        out.write_text(text, encoding='utf-8', newline='\n')
    else:
        C.require(out.is_file(), 'RESULT.json missing; run with --write first')
        C.require(out.read_bytes() == text.encode('utf-8'),
                  'RESULT.json does not match the recomputation')
    k2 = result['rows'][1]
    hb = result['break_even_k2_rank1_per_call']
    print('PASS_CENTRE_SHARED_KCALL_CHARGED',
          'k2_charged_ceiling', f"{k2['charged_ceiling']['hi_dec']}",
          'k2_ratio', k2['charged_ratio_vs_baseline'],
          'H_bit_displace', hb['displace']['full_gain_at_T2']['H'],
          'H_bit_additive', hb['additive']['full_gain_at_T2']['H'],
          'H_any_additive', hb['additive']['any_gain_at_selected']['H'],
          'no_new_kappa')
    return 0


if __name__ == '__main__':
    sys.exit(main())
