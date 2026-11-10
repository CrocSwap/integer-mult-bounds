#!/usr/bin/env python3
"""Exact tariff certificate for all copy and thin-query counts of one helper profile.

The combinatorial and Gram-complement proof is in JOINT-HELPER-COVER-PROOF.txt.
No unproved bound on the number of rank-two stages is used.
"""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
INPUTS = HERE.parent / 'helper_exchange' / 'inputs'
sys.path.insert(0, str(INPUTS))
import promotion_budget_reference as P

SOURCE = INPUTS / 'SOURCE-INVOICE.json'
SOURCE_SHA = '8356d241d6ed54608953277c3b962813e3efcc91173b08cc5faf95ec1b9e2b2e'


def add(*xs):
    return tuple(sum(x[i] for x in xs) for i in (0, 1))


def scale(c, x):
    c = Q(c)
    return (c*x[0], c*x[1]) if c >= 0 else (c*x[1], c*x[0])


def fixed(x):
    return (Q(x), Q(x))


def main():
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    source = json.loads(raw)
    paid = {int(r): count for r, count in source['local']['paid'].items()}
    helpers = {int(r): count for r, count in source['local']['helpers'].items()}
    records = []
    for k in (Q('.0042'), Q('.00424927762')):
        t = 1-k

        @lru_cache(None)
        def H(r):
            r = Q(r)
            a = P.tariff(r.numerator, k)
            b = P.tariff(r.denominator, k)
            assert b[0] > 0
            return (a[0]/b[1], a[1]/b[0])

        p, h = P.price(paid, k), P.price(helpers, k)
        L = scale(Q(1, 104), add(p, scale(-1, h)))
        N = add(scale(6, L), scale(4, H(16)), fixed(2), scale(-2, H(17)))
        rho = Q(1, 6)
        a, b = Q(97), Q(171, 11)
        B = add(scale(Q(1, 2), H(a)), scale(Q(11, 2), H(b)))
        M = add(B, scale(-1, N), fixed(-rho))
        derivative = add(scale(3*(k+t/a), H(a)),
                         scale(-3*(k+t/b), H(b)), fixed(-1))
        # A concave function lies below its tangent. These bounds also
        # cover either derivative sign and both endpoints of [0,1/3].
        tangent_at_zero = add(M, scale(-rho, derivative))
        tangent_at_third = add(M, scale(Q(1, 3)-rho, derivative))
        small_ratio_upper = max(tangent_at_zero[1], tangent_at_third[1])
        plain_zero_thin = add(scale(6, H(Q(67, 3))), scale(-1, N))
        large_ratio_upper = plain_zero_thin[1]-Q(1, 3)
        excluded = max(small_ratio_upper, large_ratio_upper) < 0
        assert excluded
        records.append({
            'kappa': str(k),
            'native_net_deficit_per_port': P.record(L),
            'cost_N_per_copy_per_port': P.record(N),
            'tangent_rho': str(rho),
            'margin_at_tangent': P.record(M),
            'derivative_at_tangent': P.record(derivative),
            'tangent_value_at_zero': P.record(tangent_at_zero),
            'tangent_value_at_one_third': P.record(tangent_at_third),
            'rho_at_most_one_third_margin_upper': str(small_ratio_upper),
            'rho_at_least_one_third_margin_upper': str(large_ratio_upper),
            'overall_margin_upper': P.record((max(small_ratio_upper, large_ratio_upper),)*2),
            'excluded_at_this_target': excluded,
        })
    result = {
        'status': 'PASS_ALL_DEFECT_JOINT_HELPER_COVER_CERTIFICATE',
        'source_invoice_sha256': SOURCE_SHA,
        'children_per_six_field_block': [1, 2, 2, 1],
        'full_stage_ranks_per_block': [2, 3, 3, 2],
        'consumed_child_targets_per_block': 2,
        'arbitrary_positive_copy_count': True,
        'arbitrary_nonnegative_root_thin_query_count': True,
        'arbitrary_repacking_of_supports': True,
        'paid_promotions_of_original_rank2_stages_to_rank3': True,
        'gram_rank': 'rank Z = delta, total rank-one factors = 6*ell+delta',
        'matching_bound': 'Disjoint full-stage supports give an identity principal minor of Z; matching number <= delta.',
        'hitting_core': 'A maximal matching has union of at most 3*delta coordinates; this union meets every full stage.',
        'core_body_mass_lower': '48*ell',
        'whole_root_body_mass': '128*ell',
        'whole_root_fields': '6*ell',
        'rho': 'delta/ell',
        'small_rho_productive_bound': '3*rho*H(1+16/rho)+(6-3*rho)*H(1+80/(6-3*rho))',
        'N': '6*L+4*H16+2-2*H17',
        'margin_bound': 'productive_bound-N-rho',
        'prices': records,
        'scope': 'Characteristic zero, unchanged complete clean source and binary children (1,2,2,1) per block, two honestly consumed whole H17 child outputs per block, baseline full projector ranks (2,3,3,2), arbitrary globally repacked simultaneous commuting stage supports and arbitrary root thin-query count. Any original rank2 full stages may be promoted to rank3 with a paid H8 idle. Such promotions can be trimmed while retaining the core hit, increasing the margin by concavity. Each mixed stage must support its separate nilpotent query and disjoint helper-reflection factor. Different child sizes/contracts, added productive helpers, ranks above3 or different stage profiles, noncommuting or operator-dependent stages and changed source interfaces remain outside.',
        'construction_supplied': False,
        'new_kappa_claim': False,
    }
    (HERE / 'JOINT-HELPER-COVER-RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'])
    for r in records:
        print(r['kappa'], 'margin_upper', r['overall_margin_upper']['upper'],
              'excluded', r['excluded_at_this_target'])


if __name__ == '__main__':
    main()
