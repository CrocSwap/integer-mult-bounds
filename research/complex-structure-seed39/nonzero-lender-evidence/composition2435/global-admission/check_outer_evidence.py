#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Independently recount the nine outer costs and audit retained evidence pins.

Imports no outer checker. This is an exact arithmetic/evidence audit of the
stated conditional transfer; it is not a proof of its inherited all-size lemmas.
"""
import argparse
import copy
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CASE = HERE.parent
ORIGINAL = CASE.parent/'global-admission'
PARENT = CASE.parent.parent/'anticipatory-stage-evidence/parent'
ROW = 'struct_boundary_radix_union'
CONTROLS = ['endpoint_equality','zero_layout_slack','old_per_axis_scan','full_cell_gauge',
            'full_key_sort','old_g_factor_union_row','old_theta_chirp_guard','old_linear_guard',
            'old_union_tag_2beta','matrix_below_strassen','halo_too_short','core_too_small',
            'group_equals_dimension','epsilon_equals_one','epsilon_not_above_r0_slack',
            'beta_below_gaussian_window','beta_above_membership_window']


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def value(record):
    return Q(record['rational'])


def arithmetic(spec, ledger, receipt):
    digits = spec['outer_refinement']['endpoint_digits']
    need(digits == 24, 'certified endpoint grid')
    C = Q(spec['expected']['complex_lower'])
    need(C == Q('0.001699160892139825160028'), 'independently certified composition endpoint')
    r = Q(1, 10**(digits+80))
    b, q = C-r, C-2*r
    a = (b+q)/2
    delta = Q(1025,1024)*r
    eps, beta = 1-delta, 1-3*delta
    xi = eps*(1+q)-Q(3,32)+r
    floor = 10**(digits+46)
    backoff = Q(1, 10**(digits+22))
    saving = eps*q
    K = Q((saving*floor).numerator//(saving*floor).denominator, floor)-backoff
    need((C*floor).denominator == 1 and 0<C-saving<Q(1,floor), 'grid floor derivation')
    need(K == C-Q(1,floor)-backoff == Q(receipt['kappa']) == Q(receipt['kappa_decimal']), 'exact outer kappa')
    row = ledger['rows'][ROW]
    expected = dict(kappa=K,epsilon=eps,xi=xi,beta=beta,q=q,a=a,r0=r,zeta=r/100,slack=r)
    for key,x in expected.items():
        need(value(row[key]) == x, 'derived outer parameter: '+key)
    # Independent algebraic forms, without calling the producer's ledger().
    costs = {
        'main_transform':eps*q,
        'global_coordinate_router':a,
        'fused_gaussian':delta+q*beta,
        'group_bit_router':delta+a*beta,
        'group_scans':delta+beta,
        'boundary_algebraic_matrix':Q(3,32)+xi-eps,
        'sparse_union_movement':xi+Q(1,2)-eps,
        'polynomial_products':eps,
        'microbox_face_corrections':79-eps-beta,
    }
    need(set(row['margins']) == set(costs), 'nine outer cost coverage')
    for name,x in costs.items():
        need(value(row['margins'][name]) == x and x>K, 'outer cost formula: '+name)
        need(value(row['strict_checks'][name+'_above_kappa']) == x-K, 'outer cost gap: '+name)
    need(min(costs.values()) == saving, 'main transform remains binding')
    checks = row['strict_checks']
    need(len(checks) == 63 and all(value(x)>0 for x in checks.values()), '63 positive retained inequalities')
    failures = ledger['rejecting_controls'][ROW]
    need(list(failures) == CONTROLS and all(v and all(value(x)<=0 for x in v.values()) for v in failures.values()), '17 named outer rejecting controls')
    need(value(ledger['complex_lower_pinned']) == C and value(ledger['complex_lower_short']) == b, 'supplier endpoint binding')
    need(ledger['profile'] == spec['expected']['global_profile'] and (ledger['m'],ledger['W']) == (73,66304), 'supplier profile binding')
    need(value(ledger['native_moment'][0]) <= value(ledger['native_moment'][1]) < 1, 'retained endpoint enclosure')
    return K, C


def main():
    sys.set_int_max_str_digits(0)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--outer',type=Path,default=HERE/'outer-result')
    ap.add_argument('--strict',type=Path,required=True)
    ap.add_argument('--out',type=Path)
    args = ap.parse_args()
    outer, strict = args.outer.resolve(), args.strict.resolve()
    receipt, ledger, spec = (read(outer/p) for p in ('OUTER-ADMISSION.json','outer/LEDGER.json','new/SPEC.json'))
    need(receipt['status'] == 'PASS_STRICT_CANDIDATE_FINITE_AND_OUTER_ARITHMETIC_CONDITIONAL_BOUND', 'conditional outer status')
    need(ledger['status'] == 'PASS_FINE_PRIME_PADDING_EXACT_ARITHMETIC', 'outer ledger status')
    need(sha(CASE/'budget/RESTRICTED-PROFILE.json') == '4988c001824ce2228e1048263390d8be7d26bd4a565cd8cfd6c4dc34cdb75dd8' and
         spec['expected']['global_profile'] == read(CASE/'budget/RESTRICTED-PROFILE.json'), 'exact generated composition profile')
    K,C = arithmetic(spec,ledger,receipt)
    need(sha(outer/'new/SPEC.json') == sha(strict/'runtime/data/SPEC.json') == sha(HERE/'owners/SPEC.json'), 'strict SPEC binding')
    for name,h in ledger['source_sha256'].items():
        need(sha(outer/name) == h, 'outer ledger input: '+name)
    independent = read(outer/'outer/INDEPENDENT.json')
    need(independent['status'] == 'PASS_INDEPENDENT_BALANCE_DERIVATION' and
         independent['source_sha256'] == sha(outer/'new/SPEC.json') and
         Q(independent['rows'][ROW]['kappa']) == K, 'independent balance binding')
    claim = read(outer/'outer/OUTER-CLAIM.json')
    need(claim['admission_receipt_sha256'] == sha(outer/'OUTER-ADMISSION.json') and
         Q(claim['kappa_rational']) == Q(claim['kappa']) == K, 'outer claim binding')
    comparison = CASE/'vendor/outer/OUTER-CLAIM.json'
    need(sha(comparison) == '42947f62e7caf297f3712a42299dcf13ad68169eddb10ccad95b54c30853c8bb', 'pinned PR2435 comparison claim')
    need(receipt['comparison_head'] == '324d7d3590dc21003940a44cb0cbdc32b3620f25' and
         receipt['outer_source_commit'] == '5449da65da12bdfd94675dccc38731eaa91e93b6', 'separate comparison and algorithm provenance')
    old = Q(read(comparison)['kappa'])
    need(K>old and Q(receipt['gain_over_pinned_pr2435']) == K-old, 'positive PR2435 comparison')
    stages = read(outer/'STAGES.json')
    need(stages == receipt['stages'] and [s['name'] for s in stages] ==
         ['ledger','independent-balance','outer-fresh-regeneration-and-evidence'], 'three outer stage coverage')
    for s in stages:
        need(type(s['exit_code']) is int and s['exit_code'] == 0 and
             sha(outer/(s['name']+'.log')) == s['log_sha256'], 'outer stage log: '+s['name'])
    log = (outer/'outer-fresh-regeneration-and-evidence.log').read_text().splitlines()
    need(all(marker in log for marker in ('PASS_UNION_SCHEDULE','PASS_EXACT_REPLAY 19','PASS_OUTER')), 'fresh outer replay completion')
    bindings = {}
    for original,h in receipt['input_sha256'].items():
        source = Path(original)
        if source.is_relative_to(receipt['strict_supplier']):
            local = strict/source.relative_to(receipt['strict_supplier'])
        elif source.is_relative_to(receipt['original_parent_admission']):
            local = ORIGINAL/'retained-pr1297'/source.relative_to(receipt['original_parent_admission'])
        else:
            need(source.name == 'MANIFEST.json' and source.parent.name == 'pr1297', 'known outer input mapping')
            local = PARENT/'vendor/pr1297/MANIFEST.json'
        need(sha(local) == h, 'outer input receipt binding: '+original)
        bindings[original] = h
    source_files = {'check_ledger.py':CASE.parent/'PR2374-check_ledger.py',
                    **{name:ORIGINAL/'outer-screen'/('PR2374-'+name) for name in
                       ('independent_check.py','check_gaugefree.py','struct_check.py')}}
    need(set(source_files) == set(receipt['outer_source_sha256']), 'four replaced source files')
    for name,path in source_files.items():
        need(sha(path) == receipt['outer_source_sha256'][name], 'pinned outer source: '+name)
    controls=[]
    for name,mutate in (
        ('kappa substituted',lambda r,l:r.__setitem__('kappa','0.01')),
        ('main cost overstated',lambda r,l:l['rows'][ROW]['margins']['main_transform'].__setitem__('rational','1')),
        ('outer rejection omitted',lambda r,l:l['rejecting_controls'][ROW].pop('endpoint_equality'))):
        badr,badl=copy.deepcopy(receipt),copy.deepcopy(ledger);mutate(badr,badl)
        try:
            arithmetic(spec,badl,badr)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('accepted outer evidence mutation: '+name)
    with localcontext() as ctx:
        ctx.prec=30
        gain = Decimal((K-old).numerator)/Decimal((K-old).denominator)
    result = dict(status='PASS_INDEPENDENT_OUTER_COST_ARITHMETIC_AND_EVIDENCE_BINDINGS',
                  kappa=str(K),kappa_decimal=receipt['kappa_decimal'],complex_endpoint=str(C),
                  gain_over_pr2435_approx=str(gain),cost_powers_rederived=9,retained_positive_inequalities=63,
                  named_rejections_checked=17,evidence_mutations_rejected=controls,
                  checked_sha256={name:sha(outer/name) for name in
                    ('OUTER-ADMISSION.json','STAGES.json','outer/LEDGER.json','outer/INDEPENDENT.json','outer/OUTER-CLAIM.json','new/SPEC.json','CLAIM.json')},
                  input_bindings=bindings,source_sha256=receipt['outer_source_sha256'],
                  scope='Independently rederives the nine finite cost powers and exact floor/backoff kappa without importing an outer checker; verifies retained inequality/control records and receipt/source/log bindings. Does not independently rederive all 63 inequalities, transcendental enclosures, supplier compilation or all-size transfer lemmas. The separate strict global and modern outer runs supply those retained evidence checks; all written conditional assumptions remain.')
    if args.out:
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])
    print(result['kappa_decimal'])


if __name__ == '__main__':
    main()
