"""Standard-library replay of mixed transport and exact favorable budget obstructions.

CubeJerry with substantial OpenAI GPT-6 Astra Pro assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import (C, HERE, SHAPE, capacities, complete_bounds, cr, decimal, dot,
                   explicit_jobs, moment_bounds, need, power_bounds, rank,
                   root_model, source_profile, verify_jobs, verify_stage_contract)


def pins():
    manifest = json.loads((HERE/'retained/SOURCE-PINS.json').read_text())
    for item in manifest['files']:
        data = (HERE/item['retained_path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == item['sha256'], 'Retained SHA256 source pin')
        git = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        need(git == item['git_blob'], 'Retained Git blob source pin')
    return manifest['source_head']


def dual_bound(case, inspect_only=False):
    intervals, caps, demands, targets = capacities(case['p'], case['q'])
    scale = case['scale']
    need(isinstance(scale, int) and scale > 0, 'Positive dual denominator')
    alpha = [Q(case['alpha'].get(str(i), 0), scale) for i in range(len(intervals))]
    beta = [Q(v, scale) for v in case['beta']]
    need(len(beta) == 18 and all(v <= 0 for v in alpha), 'LP dual signs/dimension')
    slack = None
    for c, d in intervals:
        lhs = sum(alpha[i] for i, (a, b) in enumerate(intervals) if c <= a and b <= d)
        lhs += sum(beta[c:d+1])
        lower_cost = power_bounds(8*(d-c+1))[0]
        gap = lower_cost-lhs
        need(gap >= 0, 'Every dual column is below its rational lower cost bound')
        slack = gap if slack is None else min(slack, gap)
    lower_paid = dot(alpha, caps)+dot(beta, demands)
    h, p = source_profile()
    native = Counter({r: 18*n for r, n in h.items()})
    for r, n in p.items():
        native[r] -= 18*n
    bound = moment_bounds(native)[1]+104*(moment_bounds(targets)[1]-3-lower_paid)
    if not inspect_only:
        need(bound < 0, 'Even the complete favorable invoice loses')
    return {'p': case['p'], 'q': case['q'], 'exact_interval_constraints': len(intervals),
            'exact_dual_columns': len(intervals), 'minimum_dual_slack': decimal(slack),
            'idle_cost_lower_bound': decimal(lower_paid), 'complete_gain_upper_bound': decimal(bound),
            'targets': dict(sorted(targets.items())), 'idle_demands': demands}


def expect_failure(callback, label):
    try:
        callback()
    except (ValueError, ZeroDivisionError):
        return label
    raise ValueError('Negative control was accepted: '+label)


def verify():
    head = pins()
    certificate = json.loads((HERE/'certificate.json').read_text())
    need(Q(certificate['C']) == C, 'Exponent pin')
    need([(v['p'], v['q']) for v in certificate['cases']] == [(4, 4), (1, 2)], 'Only declared finite targets')
    roots = {str(pair): verify_stage_contract(*pair) for pair in [(0, 0), (4, 4), (1, 2)]}
    jobs = explicit_jobs()
    paid, construction = verify_jobs(jobs)
    _, _, _, targets = capacities(1, 2)
    original_targets, original_paid = cr.outer_formula(*SHAPE)
    expected_target_delta = Counter({129: 2, 137: 1, 73: -2, 65: -1})
    target_delta = Counter(targets)
    target_delta.subtract(original_targets)
    need(dict(+target_delta) == dict(+expected_target_delta) and
         dict(-target_delta) == dict(-expected_target_delta), 'Complete target debit/credit delta')
    paid_delta = Counter(paid)
    paid_delta.subtract(original_paid)
    need(dict(+paid_delta) == {120: 2, 8: 1} and dict(-paid_delta) == {64: 1}, 'Complete idle bill delta')
    positive = sorted([129, 129, 137, 64, 0, 0], reverse=True)
    negative = sorted([73, 73, 65, 120, 120, 8], reverse=True)
    partial_positive = [sum(positive[:k]) for k in range(1, len(positive)+1)]
    partial_negative = [sum(negative[:k]) for k in range(1, len(negative)+1)]
    need(sum(positive) == sum(negative), 'Exact equal-mass comparison')
    need(all(a >= b for a, b in zip(partial_positive, partial_negative)) and positive != negative,
         'Strict concave-moment loss by majorization')
    original_interval = complete_bounds(original_targets, original_paid)
    actual_interval = complete_bounds(targets, paid)
    need(original_interval[1] < 0 and original_interval[0] > Q('-0.00000001'), 'Source root endpoint calibration')
    need(actual_interval[1] < -45, 'Realized crossing loses complete budget')
    baseline_intervals, baseline_caps, _, _ = capacities(0, 0)
    need(all(cap == 0 for (a, b), cap in zip(baseline_intervals, baseline_caps) if a <= 8 < b),
         'No cross-side carrier under original masks, regardless of source idle basis')
    min_intervals, min_caps, _, _ = capacities(1, 2)
    need(min_caps[min_intervals.index((1, 15))] == 2, 'Mixed crossing has exactly two common carrier dimensions')
    large_intervals, large_caps, _, _ = capacities(4, 4)
    need(large_caps[large_intervals.index((4, 13))] == 6, 'Larger crossing common carrier rank')
    lp = [dual_bound(case) for case in certificate['cases']]
    controls = []
    bad = deepcopy(jobs)
    row = list(bad[1][2]);row[0] = 0
    bad[1] = (bad[1][0], bad[1][1], row, bad[1][3], bad[1][4])
    controls.append(expect_failure(lambda: verify_jobs(bad), 'Deleted cross-carrier A dual coefficient'))
    bad_dual = deepcopy(certificate['cases'][0])
    bad_dual['beta'][0] += 1000*bad_dual['scale']
    controls.append(expect_failure(lambda: dual_bound(bad_dual), 'Inflated dual paid-cost lower bound'))
    # Null primal and dual spaces alone do not establish a usable idle projector.
    need(2-rank([[1, 0]])-rank([[0], [1]])+rank([[0]]) == 0,
         'Degenerate pairing control has zero capacity')
    controls.append('Nonzero primal/dual nullspaces with zero pairing rank')
    sites, F, _, _ = root_model(0, 0)
    left_source = cr.lines(*SHAPE)[0]
    first_right = next(s for s in sites if s[3] == 'R')
    need(dot(left_source[1], first_right[0]) == 2, 'Source idle line cannot cross unchanged')
    controls.append('Literal source left idle fails right native query')
    report = {'schema': 'mixed-mask-cross-side-report/1', 'status': 'scoped_negative_result',
        'source_head': head, 'C': str(C), 'no_new_kappa': True,
        'arbitrary_input_stage_contracts': roots, 'realized_crossing': construction,
        'realized_outer_targets': dict(sorted(targets.items())),
        'realized_outer_paid': dict(sorted(paid.items())),
        'source_complete_gain_interval': list(map(decimal, original_interval)),
        'realized_complete_gain_interval': list(map(decimal, actual_interval)),
        'concave_order': {'positive': positive, 'negative': negative,
            'positive_prefix_sums': partial_positive, 'negative_prefix_sums': partial_negative,
            'conclusion': 'Realized caller is strictly worse for every power tariff 0<t<1.'},
        'favorable_interval_capacity_certificates': lp, 'negative_controls': controls,
        'coverage': 'Exact normalized caller algebra, source native census, all 171 interval capacities and rational dual inequalities per case. No native/compiler/outer theorem rerun; no additional masks or non-shortest roots claimed.'}
    return report

if __name__ == '__main__':
    report = verify()
    if '--write-report' in sys.argv:
        (HERE/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
