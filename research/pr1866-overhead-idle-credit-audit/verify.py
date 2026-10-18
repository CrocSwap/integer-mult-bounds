#!/usr/bin/env python3
"""Audit how PR1866's (3,1,1,1)->6 block screen prices its per-block overhead.

PR1866 (head 7d22d1d51eb6c0bc040f8181b6c5f83e051fb234) adds its e assumed
rank-one-equivalent overhead units per block to the *local* profile passed to
the retained ceiling engine. The engine fixes total paid mass by the coverage
identity (7232 per call), so each overhead unit is subtracted from the idle
remainder and only pays its excess over ideal rank-51 idle mass. The merged
complex-rank-one-block-budget package prices additional work on top of the
unchanged idle bill instead. This script evaluates both conventions on PR1866's
exact domain (k = 0..432 blocks, e = 0, 1, 2) with two arithmetic engines:

  A. the pinned research/complex-local-word-ceiling/ceiling.py enclosures
     (atanh logarithms, Taylor exponentials, Fraction outward rounding);
  B. a code-disjoint decimal engine: libmpdec's correctly rounded ln/exp,
     widened by WIDEN ulps, with ROUND_FLOOR/ROUND_CEILING for every other step.

Every decision must be strict and identical in both engines.

usage: verify.py [--write]
Prepared by ianlibanio with substantial Claude (Anthropic) assistance. Apache-2.0.
"""
import decimal
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/complex-local-word-ceiling'))
import ceiling as C  # noqa: E402

M, FAMILIES, STAGES, CENTRE, R = 73, 896, 9, 64, 51
W = Q(FAMILIES, STAGES)
TOTAL = 72 * W + CENTRE  # coverage identity, paid mass per call
SELECTED = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
BASE_BRACKET = (Q(1690054109088, 10 ** 15), Q(1690054109089, 10 ** 15))
TARGET = BASE_BRACKET[1] * Q(105, 100)
KMAX, TARIFFS = 432, (0, 1, 2)
PR1866_CLAIM = {0: (135, 298), 1: (284, 149), 2: None}  # (min k, count) from its CERTIFICATE.json
PREC, WIDEN = 80, 4
RANKS = (1, 2, 3, 4, 5, 6, 8, R)


def need(ok, why):
    if not ok:
        raise SystemExit('FAIL: ' + why)


# ---- engine A: pinned rational enclosures -------------------------------------------------
def costs_a(a):
    return {r: C.child_cost(r, M, a) for r in RANKS}


def moment_a(cost, local, extra_rank1=0):
    idle = TOTAL - sum(r * Q(n) for r, n in local.items())
    need(idle >= 0, 'local profile exceeds the coverage identity')
    k = idle / R
    lo = sum(Q(n) * cost[r][0] for r, n in local.items()) + k * cost[R][0] + extra_rank1 * cost[1][0]
    hi = sum(Q(n) * cost[r][1] for r, n in local.items()) + k * cost[R][1] + extra_rank1 * cost[1][1]
    return lo / W, hi / W


# ---- engine B: decimal with correctly rounded ln/exp and directed rounding ----------------
D = decimal.Decimal
FLOOR = decimal.Context(prec=PREC, rounding=decimal.ROUND_FLOOR, Emin=-999999, Emax=999999)
CEIL = decimal.Context(prec=PREC, rounding=decimal.ROUND_CEILING, Emin=-999999, Emax=999999)
EVEN = decimal.Context(prec=PREC, rounding=decimal.ROUND_HALF_EVEN, Emin=-999999, Emax=999999)


def widen(x, down):
    for _ in range(WIDEN):
        x = EVEN.next_minus(x) if down else EVEN.next_plus(x)
    return x


def dec(q, ctx):
    return ctx.divide(D(q.numerator), D(q.denominator))


def costs_b(a):
    """c(r) = exp((1-a)(ln r - ln m)); ln and exp are correctly rounded (<= 1/2 ulp), widened."""
    q_lo, q_hi = dec(1 - a, FLOOR), dec(1 - a, CEIL)
    lm = (widen(EVEN.ln(D(M)), True), widen(EVEN.ln(D(M)), False))
    out = {}
    for r in RANKS:
        lr = (widen(EVEN.ln(D(r)), True), widen(EVEN.ln(D(r)), False))
        d_lo, d_hi = FLOOR.subtract(lr[0], lm[1]), CEIL.subtract(lr[1], lm[0])  # both <= 0
        need(d_hi <= 0, 'rank above width')
        e_lo, e_hi = FLOOR.multiply(q_hi, d_lo), CEIL.multiply(q_lo, d_hi)
        out[r] = (widen(EVEN.exp(e_lo), True), widen(EVEN.exp(e_hi), False))
        need(out[r][0] > 0 and out[r][0] < out[r][1], 'decimal enclosure')
    return out


def moment_b(cost, local, extra_rank1=0):
    idle = TOTAL - sum(r * Q(n) for r, n in local.items())
    need(idle >= 0, 'local profile exceeds the coverage identity')
    k = idle / R
    terms = [(Q(n), r) for r, n in local.items()] + [(k, R), (Q(extra_rank1), 1)]
    lo, hi = D(0), D(0)
    for n, r in terms:
        lo = FLOOR.add(lo, FLOOR.multiply(dec(n, FLOOR), cost[r][0]))
        hi = CEIL.add(hi, CEIL.multiply(dec(n, CEIL), cost[r][1]))
    return FLOOR.divide(FLOOR.multiply(lo, D(STAGES)), D(FAMILIES)), CEIL.divide(CEIL.multiply(hi, D(STAGES)), D(FAMILIES))


# ---- shared decision layer ------------------------------------------------------------------
def sign(iv):
    """-1 if certified < 1, +1 if certified > 1; ambiguity is a failure."""
    if iv[1] < 1:
        return -1
    if iv[0] > 1:
        return 1
    raise SystemExit('FAIL: enclosure does not separate the moment from 1')


def block_profile(k, credited_extra=0):
    """PR1866's profile: k blocks (3,1,1,1)->6, mass preserving; optional overhead inside it."""
    return {1: SELECTED[1] - 3 * k + credited_extra * k, 2: SELECTED[2], 3: SELECTED[3] - k,
            4: SELECTED[4], 5: SELECTED[5], 6: k, 8: SELECTED[8]}


def scan(moment, cost, e, credited):
    signs = []
    for k in range(KMAX + 1):
        if credited:
            iv = moment(cost, block_profile(k, e))
        else:
            iv = moment(cost, block_profile(k), extra_rank1=e * k)
        signs.append(sign(iv))
    passing = [k for k, s in enumerate(signs) if s < 0]
    need(passing == list(range(passing[0], KMAX + 1)) if passing else True, 'pass set is not an upper interval')
    return signs, (passing[0], len(passing)) if passing else None


def max_total_extra(moment, cost, k):
    """Largest integer J of extra rank-one calls (total, no idle credit) still passing at k blocks."""
    J = 0
    while sign(moment(cost, block_profile(k), extra_rank1=J + 1)) < 0:
        J += 1
    return J


def engine_result(name, moment, cost_fn):
    base_cost = (cost_fn(BASE_BRACKET[0]), cost_fn(BASE_BRACKET[1]))
    need(sign(moment(base_cost[0], SELECTED)) < 0 and sign(moment(base_cost[1], SELECTED)) > 0,
         name + ': selected ceiling bracket does not replay')
    cost = cost_fn(TARGET)
    need(sign(moment(cost, SELECTED)) > 0, name + ': selected word unexpectedly passes the target')
    out = {'credited': {}, 'additional': {}, 'signs': {}}
    for e in TARIFFS:
        for label, credited in (('credited', True), ('additional', False)):
            signs, summary = scan(moment, cost, e, credited)
            out[label][e] = summary
            out['signs'][(label, e)] = signs
    out['max_total_extra_rank1_at_432'] = max_total_extra(moment, cost, KMAX)
    out['max_total_extra_rank1_at_135'] = max_total_extra(moment, cost, 135)
    return out, cost


def block_tax_a(a):
    """Saving of one block, in rank-one call units: 3 + 3^q - 6^q with q = 1 - a (enclosure)."""
    c = costs_a(a)
    lo = (3 * c[1][0] + c[3][0] - c[6][1]) / c[1][1]
    hi = (3 * c[1][1] + c[3][1] - c[6][0]) / c[1][0]
    return lo, hi


def credited_unit_a(a):
    """Cost of one overhead unit when it displaces ideal rank-51 idle mass, in rank-one units."""
    c = costs_a(a)
    return (c[1][0] - c[R][1] / R) / c[1][1], (c[1][1] - c[R][0] / R) / c[1][0]


def controls(cost_a):
    rows = []
    # 1. a rank-52 idle cap violates the halving guard 73^2 > 2 r^2.
    try:
        C.model(SELECTED, M, FAMILIES, STAGES, CENTRE, R=52)
        rows.append(('idle rank 52 rejected', False))
    except ValueError:
        rows.append(('idle rank 52 rejected', True))
    # 2. both conventions coincide with zero overhead (k = 135 boundary).
    a = moment_a(cost_a, block_profile(135, 0))
    b = moment_a(cost_a, block_profile(135), extra_rank1=0)
    rows.append(('conventions agree at e = 0', a == b))
    # 3. the boundary is sharp in both directions for the zero-overhead screen.
    rows.append(('k = 134, e = 0 rejected', sign(moment_a(cost_a, block_profile(134))) > 0))
    # 4. a profile that overspends the coverage identity is rejected by the engine.
    try:
        moment_a(cost_a, {1: 7233})
        rows.append(('coverage overspend rejected', False))
    except SystemExit:
        rows.append(('coverage overspend rejected', True))
    # 5. the credited convention passes exactly where the additional one rejects (k = 284, e = 1).
    cr = sign(moment_a(cost_a, block_profile(284, 1)))
    ad = sign(moment_a(cost_a, block_profile(284), extra_rank1=284))
    rows.append(('k = 284, e = 1: credited pass, additional reject', cr < 0 and ad > 0))
    return rows


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    need(TARGET == Q(35491136290869, 20000000000000000), 'target differs from PR1866 / PR1605 target')
    need(2 * R * R < M * M <= 2 * (R + 1) ** 2, 'idle rank cap')
    need(TOTAL == 7232, 'coverage identity')
    res_a, cost_a = engine_result('engine A', moment_a, costs_a)
    res_b, _ = engine_result('engine B', moment_b, costs_b)
    for key in ('credited', 'additional', 'signs', 'max_total_extra_rank1_at_432', 'max_total_extra_rank1_at_135'):
        need(res_a[key] == res_b[key], 'engines disagree on ' + key)
    for e, claim in PR1866_CLAIM.items():
        need(res_a['credited'][e] == claim, f'PR1866 credited threshold for e = {e} does not reproduce')
    need(res_a['additional'] == {0: (135, 298), 1: None, 2: None}, 'additional-overhead thresholds changed')

    tax_lo, tax_hi = block_tax_a(TARGET)
    need(0 < tax_lo and tax_hi < Q(1, 50), 'block saving is not in (0, 1/50) rank-one units at the target')
    tax0 = block_tax_a(Q(0))
    need(tax0[0] <= 0 <= tax0[1] and tax0[1] - tax0[0] < Q(1, 10 ** 60), 'block saving at a = 0 is not 0')
    unit_lo, unit_hi = credited_unit_a(TARGET)
    need(0 < unit_lo and unit_hi < tax_lo, 'credited overhead unit is not cheaper than the block saving')

    ctrl = controls(cost_a)
    need(all(ok for _, ok in ctrl), 'control failed: ' + ', '.join(n for n, ok in ctrl if not ok))

    fmt = lambda s: None if s is None else {'min_k': s[0], 'passing_count': s[1]}  # noqa: E731
    result = {
        'marker': 'PASS_PR1866_OVERHEAD_IDLE_CREDIT_AUDIT',
        'audited_pr': {'number': 1866, 'head': '7d22d1d51eb6c0bc040f8181b6c5f83e051fb234',
                       'package': 'research/complex-mixed-rank6-block-seedc8d6'},
        'model': {'width': M, 'families_per_replica': FAMILIES, 'stages': STAGES, 'centre_per_call': CENTRE,
                  'idle_rank_cap': R, 'paid_mass_per_call': str(TOTAL), 'selected_profile': SELECTED,
                  'target_a': str(TARGET), 'target_definition': '21/20 x selected ceiling upper bracket 1690054109089/10^15',
                  'domain': {'blocks_per_call': f'0..{KMAX}', 'overhead_rank1_units_per_block': list(TARIFFS)}},
        'thresholds_pr1866_convention_overhead_credited_against_idle': {str(e): fmt(res_a['credited'][e]) for e in TARIFFS},
        'thresholds_additional_overhead_no_idle_credit': {str(e): fmt(res_a['additional'][e]) for e in TARIFFS},
        'max_total_extra_rank1_calls_no_idle_credit': {'k=432': res_a['max_total_extra_rank1_at_432'],
                                                       'k=135': res_a['max_total_extra_rank1_at_135']},
        'block_saving_rank1_units_at_target': [str(C.down(tax_lo)), str(C.up(tax_hi))],
        'block_saving_closed_form': '3 + 3^q - 6^q, q = 1 - a; increasing in a, zero at a = 0',
        'credited_overhead_unit_rank1_units_at_target': [str(C.down(unit_lo)), str(C.up(unit_hi))],
        'engines': {'A': 'pinned ceiling.py child_cost enclosures, Fraction arithmetic',
                    'B': f'decimal prec={PREC}, correctly rounded ln/exp widened {WIDEN} ulps, directed rounding elsewhere',
                    'agreement': f'all {2 * len(TARIFFS) * (KMAX + 1)} scan decisions, baseline bracket and both J counts'},
        'controls': {name: ok for name, ok in ctrl},
        'source_sha256': {p: sha(p) for p in ('research/complex-local-word-ceiling/ceiling.py',
                                              'research/complex-local-word-ceiling/RESULT.json')},
        'python': sys.version.split()[0],
    }
    path = HERE / 'RESULT.json'
    body = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if '--write' in sys.argv:
        path.write_text(body)
    else:
        stored = json.loads(path.read_text())
        stored.pop('python', None)
        fresh = json.loads(body)
        fresh.pop('python', None)
        need(stored == fresh, 'RESULT.json differs from the recomputation (run with --write)')
    print('PASS_PR1866_OVERHEAD_IDLE_CREDIT_AUDIT',
          'credited', {e: res_a['credited'][e] for e in TARIFFS},
          'additional', {e: res_a['additional'][e] for e in TARIFFS},
          'J432', res_a['max_total_extra_rank1_at_432'],
          'block_saving', float(tax_lo))


if __name__ == '__main__':
    main()
