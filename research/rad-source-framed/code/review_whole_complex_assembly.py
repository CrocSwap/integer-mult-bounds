#!/usr/bin/env python3
"""Independent complete whole-rank complex and generic-bit assembly.

The retained algebra comes from an independent assembly reviewer. The
changed native moments are independently reconstructed with128-term exact
logs and outward384-bit dyadic bounds. No new producer is imported.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path
import resource
import time

from review_asymmetric_motif import independent_saving
from review_parameter_audit import log_integer
from review_packed_unrolling import finite_counts
from review_semantic_bulk_assembly import ceil_q, complex_counts, power_certificate, require


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


@cache
def bounds(n):
    lo, hi = log_integer(n, 128)
    scale = 2**384
    lower = Q(lo.numerator*scale//lo.denominator, scale)
    upper = Q(-((-hi.numerator*scale)//hi.denominator), scale)
    require(lower <= lo <= hi <= upper, 'Independent dyadic rounding failed')
    return lower, upper


def audit_primitive(p, root):
    n=finite_counts(p['counts']);h,roles=p['h'],p['roles'];v,m=n['v'],n['m']
    require((h,roles)==(51,485680),'Unexpected promoted generic graph')
    deficits=dict(middle=h*h,joined=2*h,data=h*h+h-1)
    multiplicities=dict(middle=(roles+h)*v*v,joined=(roles+h)*v*v,data=2*n['N'])
    runs={k:m-2*d for k,d in deficits.items()}
    ranks={k:multiplicities[k]*(m-d) for k,d in deficits.items()}
    require(p['kernel_dimensions']==deficits and p['family_multiplicities']==multiplicities and
        p['grouped_runs']==runs and p['family_ranks']==ranks and sum(ranks.values())<n['s'],
        'Independent disjoint generic boundary counts differ')
    moments={k:multiplicities[k]*r*bounds(r)[0] for k,r in runs.items()}
    hist=Counter()
    for k,r in runs.items():hist[r]+=multiplicities[k]
    long_rank=sum(r*c for r,c in hist.items())
    require({str(k):v for k,v in sorted(hist.items())}==p['long_run_histogram'] and
        p['long_grouped_rank']==long_rank and p['individual_pivot_count']==n['s']-long_rank>0,
        'Generic characteristic used stale or overlapping pivot mass')
    lm=bounds(m)[1];linear=n['W']*m*lm-sum(moments.values());quadratic=Q(n['s'],2)*lm*lm
    saved_linear,saved_quadratic=(Q(p[k]) for k in ('taylor_linear_coefficient','taylor_quadratic_coefficient'))
    a=Q(p['saving']);require(a==Q(143492085004836477,10**24),'Unknown strict generic saving')
    require(saved_linear>=linear>0 and saved_quadratic>=quadratic>0,
        'Independent moments do not support producer Taylor coefficients')
    gap=n['D']-a*saved_linear-a*a*saved_quadratic
    require(gap==Q(p['strict_taylor_gap'])>0 and
        n['D']-a*linear-a*a*quadratic>=gap,'Strict generic negative-exponential characteristic failed')
    r=root['independent_characteristic']
    require(r['kernels']==deficits and r['run_lengths']==runs and r['family_ranks']==ranks and
        r['roles']==roles and Q(r['chosen_saving'])>=a and Q(r['strict_characteristic_gap'])>0 and
        r['row_degree']==66000 and r['reservoir_slope']==264000,
        'Independent constructive all-size theorem and positive-exponential audit differ')
    require(p['maximum_child_rank']==m-4*h and Q(p['child_ratio'])==Q(m-4*h,m) and
        m**651>2*(m-4*h)**651 and n['W']<2**49 and
        Q(49*651)*(2+Q(1,25))<66000,
        'New maximum child/deeper row proof failed')
    return dict(chosen_saving=str(a),strict_taylor_gap=str(gap),
        independently_rebuilt_runs=runs,family_ranks=ranks,individual_pivots=n['s']-long_rank,
        maximum_child=m-4*h,row_degree=66000,logarithm_terms=128,outward_dyadic_bits=384,
        full_h51_basis_table_prime_materialized=False,constructive_theorem_separately_reviewed=True)


def audit_phase(phase, finite, bit, ec):
    raw = dict(finite['counts'])
    raw['eta'] = str(Q(raw['D'], raw['W']*raw['m']))
    nc = complex_counts(raw)
    h, m, v, roles = nc['h'], nc['m'], nc['v'], nc['R']
    require((h, roles) == (28, 88377), 'Unexpected promoted whole-phase finite input')
    copies = dict(middle=(roles+h+1)*v*v, joined=(roles+h+1)*v*v, data=2*nc['N'])
    ranks = dict(middle=m-h*h, joined=m-2*h, data=(h*h-1)*(h-1))
    credited = sum(copies[k]*ranks[k] for k in ranks)
    individual = nc['s']-credited
    hist = Counter({1: individual})
    for k in ranks:
        hist[ranks[k]] += copies[k]
    require(individual > 0 and sum(r*n for r,n in hist.items()) == nc['s']
            and max(hist) == m-2*h < m, 'Actual disjoint whole-phase rank sum differs')
    require(phase['counts'] == finite['counts'] and phase['grouped_ranks'] == ranks
            and phase['family_multiplicities'] == copies and phase['total_grouped_rank'] == credited
            and phase['all_other_individual_pivots'] == individual
            and phase['child_histogram'] == {str(r): n for r,n in hist.items()},
            'Accepted characteristic used different physical boundaries')
    lm = bounds(m)[1]
    require(lm < 10 and all(bounds(r)[0] > Q(99,10) for r in ranks.values()),
            'Longer independent logarithm invalidates coarse phase enclosure')
    moment = sum(copies[k]*ranks[k]*bounds(ranks[k])[0] for k in ranks)
    linear = nc['s']*lm-moment
    b = Q(1,10**6)
    require(0 < b*lm < 1, 'Taylor range fails')
    gap = nc['D']-b*linear-b*b*nc['s']*lm*lm/(2*(1-b*lm))
    coarse = nc['D']-b*(10*nc['s']-Q(99,10)*credited)-b*b*50*nc['s']/(1-10*b)
    require(gap >= coarse == Q(phase['strict_normalized_gap'])
            == Q(111225521101498713,21171875) > 0
            and gap >= Q(phase['fine_positive_gap'])
            and Q(phase['saving']) == b and Q(phase['sigma']) == 1-b
            and b > 2*Q(bit['saving']), 'Whole phase strict positive-exponential characteristic fails')
    require(ec['counts'] == raw and ec['grouped_children'] == ranks and
        ec['family_multiplicities'] == copies and ec['child_histogram'] == phase['child_histogram'] and
        ec['all_other_individual_pivots'] == individual and ec['total_grouped_rank'] == credited,
        'Producer phase certificate uses different physical rank families')
    for key, rank in {'m':m, **ranks}.items():
        lower, upper = bounds(rank)
        saved = ec['logarithm_intervals'][key]
        require(Q(saved[0]) <= lower <= upper <= Q(saved[1]),
                'Longer independent phase logarithm escapes saved enclosure')
    require(Q(ec['rank_log_moment_lower']) <= moment and
        Q(ec['normalized_linear_upper']) >= linear and
        Q(ec['normalized_quadratic_upper']) >= nc['s']*lm*lm/2 and
        gap >= Q(ec['strict_primitive_gap']) > 0,
        'Independent phase characteristic does not support producer Taylor bounds')
    require(m**272 > 2*(m-2*h)**272 and nc['W'] < 2**41,
            'Variable-width complex depth and role stock fail')
    return dict(saving=str(b),sigma=str(1-b),independent_strict_gap=str(gap),
        accepted_coarse_strict_gap=str(coarse),ranks=ranks,copies=copies,
        individual_children=individual,weighted_total_rank=nc['s'],
        child_histogram={str(r): n for r,n in sorted(hist.items())},
        log_terms=128,dyadic_bits=384,maximum_child=m-2*h,depth_per_ceil_log2e=272,
        standalone_runtime_exponent_below_bit_overhead_claimed=False)


def prefix_controls():
    rows = boundaries = layouts = 0
    for dc, db in product(range(1,5), range(1,4)):
        wc, wb = 3, 5
        stock = wc**dc*wb**db
        q0 = (stock-1).bit_length()
        original = 2**q0
        padded = stock*((original+stock-1)//stock)
        require(stock <= original <= padded < 2*original, 'One initial product padding fails')
        for depth in range(dc+1):
            factor = wc**depth
            require(padded % (factor*wb**db) == 0, 'Nested role split is not exact')
            for root_row in range(padded):
                local = root_row
                complex_digits = []
                for _ in range(depth):
                    local, role = divmod(local, wc)
                    complex_digits.append(role)
                bit_digits = []
                for _ in range(db):
                    local, role = divmod(local, wb)
                    bit_digits.append(role)
                for role in reversed(bit_digits):
                    local = wb*local+role
                for role in reversed(complex_digits):
                    local = wc*local+role
                require(local == root_row and (local < original) == (root_row < original),
                        'Nested selectors changed original padding activation identity')
                rows += 1
            boundaries += 1
    for K in range(1,8):
        for rho in range(K):
            for e in range(3,13):
                m, r = 3, 2
                f, t = divmod(e,m)
                main = [rho+j*K for j in range(m*f)]
                first_active_banks = [bank*f*K+rho+j*K for bank in range(r) for j in range(f)]
                child = [rho+j*K for j in range(r*f)]
                tail = [m*f*K+rho+j*K for j in range(t)]
                require(first_active_banks == child and main+tail == [rho+j*K for j in range(e)]
                        and all(i < r*f*K for i in child)
                        and all(i >= m*f*K for i in tail), 'Complete grouped selected layout differs')
                layouts += 1
    wc, wb, dc, db = 3, 5, 4, 3
    max_only = max(wc**dc, wb**db)
    bad_original = 2**((max_only-1).bit_length())
    product_stock = wc**dc*wb**db
    require(bad_original >= max_only and product_stock > 2*bad_original,
            'Max-only nested-stock negative control does not discriminate')
    return dict(labelled_original_rows_restored=rows,depth_boundaries=boundaries,
        complete_selected_offset_layouts=layouts,activation_uses_original_global_row=True,
        max_only_stock_negative=dict(original=bad_original,individual_max=max_only,product=product_stock),
        original_padding_bitmap_restored=True)


def audit_row(row, old_tight, primitive, phase):
    n=finite_counts(row['bit_counts']);nc=complex_counts(row['complex_counts'])
    p={k:Q(v) for k,v in row['parameters'].items()}
    a,b,tau,sigma,c,beta,eps,lam,lp,r,delta,kappa=(p[k] for k in
        ('a_bit','a_complex','tau','sigma','c','beta','epsilon','lambda_',
         'lambda_prime','alpha_squared_power','delta','kappa'))
    log_records={}
    primitive_gaps={}
    ec = row['complex_branching_certificate']
    require(b == Q(1,10**6) == Q(phase['saving']) == Q(ec['chosen_saving']) and
        Q(ec['independent_coarse_gap']) == Q(phase['strict_normalized_gap']) > 0,
        'Whole phase row has no exact accepted homogeneous characteristic')
    log_m = Q(ec['logarithm_intervals']['m'][1])
    saved_gap = nc['D']-b*Q(ec['normalized_linear_upper'])-b*b*Q(ec['normalized_quadratic_upper'])/(1-b*log_m)
    require(saved_gap == Q(ec['strict_primitive_gap']) > 0 and
        Q(ec['independent_coarse_gap']) == Q(phase['strict_normalized_gap']),
        'Saved complete positive-exponential phase certificate differs')
    primitive_gaps['complex_primitive'] = saved_gap
    log_records['complex'] = dict(exponent_kind='Homogeneous weighted tree; paid bit overhead retained',
        chosen_saving=str(b),independent_longer_log_terms=128)
    require(a == Q(primitive['saving']), 'Explicit Taylor saving differs')
    eb = row['bit_saving_certificate']
    require(eb['certificate_kind'] == 'GENERIC METRIC FLAGS, DIRECT NEGATIVE-EXPONENTIAL TAYLOR',
            'New primitive must not use a uniform rank-saving enclosure')
    require(Q(eb['chosen_saving']) == a and
            Q(eb['strict_primitive_gap']) == Q(primitive['strict_taylor_gap']) and
            Q(eb['taylor_linear_coefficient']) == Q(primitive['taylor_linear_coefficient']) and
            Q(eb['taylor_quadratic_coefficient']) == Q(primitive['taylor_quadratic_coefficient']),
            'Row primitive certificate differs from the reviewed Taylor input')
    primitive_gaps['bit_primitive'] = Q(primitive['strict_taylor_gap'])
    require(primitive_gaps['bit_primitive'] > 0, 'Explicit Taylor gap is not strict')
    require(tau==1-a and sigma==1-b and 0<2*a<b<Q(1,32),'New bit-limited whole-phase branch invalid')
    h=Q(1,2**(20 if row['mode']=='conservative' else 64))
    require(row['mode'] in ('conservative','tight'),'Unknown fixed parameter mode')
    require(beta==Q(1,2),'Chosen whole-complex stopping threshold differs')
    internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
    internal_saving,leaf_saving=1-internal,1-leaf
    q=1-lp
    require(q==min(internal_saving,leaf_saving)*(1-2*h) and
        lam==(max(tau,sigma,internal)+lp)/2,
        'All three original intermediate exponent bounds were not retained')
    require(row['exponent_order']=='sigma<=tau: root dominated' and
        all(Q(row['recurrence_savings'][k])==v for k,v in
            dict(internal=internal_saving,leaf=leaf_saving,reservations=c,q=q).items()),
        'General stopped savings differ')
    prefix=row['prefix']
    if prefix=='original':
        require(c==q*(1+h) and eps==(1-h)/(1+c+q),'Original prefix strict parameters differ')
        g1=1-eps*(1+c)
    else:
        require(prefix=='balanced','Unknown reviewed prefix interface')
        require(c==q+h/4 and eps==(1-h)/(1+q),'Balanced strict parameters differ')
        g1=1-eps
    G=eps*q
    require(r==(G+1-eps)/2 and delta==h/8,'Gaussian power/precision strict parameters differ')
    internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
    reserve=max(1-c,Q(0))
    recurrence=dict(internal=internal,leaf=leaf,reservations=reserve)
    require(all(Q(row['recurrence'][k])==v for k,v in recurrence.items()),'Compact recurrence differs')
    E=64*(nc['W']+nc['m']+1)**3;B=nc['s']+E;C0=32*nc['m']*B*B
    require(p['C0']==C0 and p['C1']==1,'Linear semantic guard differs')
    semantic=row['semantic_guard'];Gscalar=semantic['scalar_gates']
    literal_depth=2*Gscalar*nc['W']**2+8*nc['s']+4*nc['W']+4+32*nc['m']
    require(Gscalar>0 and E>literal_depth and C0>2*B+18,
        'Exact actual scalar charge or complete linear guard constant invalid')
    require(semantic['literal_depth']==literal_depth and
        semantic['literal_guard_slack']==E-literal_depth and semantic['old_six_W_shortcut_not_used'] and
        semantic['stopping_beta_independent'] and
        semantic['internal']=='A(e)<=A(rmax floor(e/m))+s floor(e/m)+E' and
        semantic['complete']=='A_layer<=(2B+18)d<C0d' and
        semantic['representation']=='Same fine-grid integers; no child truncation',
        'Semantic general-beta/completed-child interface differs')
    semantic=row['semantic_guard']
    require(all(Q(semantic[k])==v for k,v in dict(E=E,B=B,C0=C0,C1=1).items()),
            'Semantic proof input constants differ')
    require(Q(row['linear_guard_constant_slack'])==C0-(2*B+18), 'Saved linear constant slack differs')
    margins=dict(g1=g1,g2=a,g3=G,g4=a,g5=min(1-eps-delta,r-delta),
                 g6=1-eps-delta,g7=eps)
    require(all(Q(row['margins'][k])==v for k,v in margins.items()),'Complete seven-margin model differs')
    require(min(margins.values())==G==Q(row['minimum_margin']),'Layer is not the unique strict minimum')
    require(kappa==Q((G.numerator*10**40-1)//G.denominator,10**40),
            'Compact decimal witness is not the strict lower grid point')
    previous=Q(old_tight['parameters']['kappa'])
    require(Q(row['previous_accepted_kappa'])==previous,'Accepted generic previous witness differs')
    geometry=1-eps*(1+c)
    slacks=dict(**primitive_gaps,complex_literal_gate_guard=E-literal_depth,
        q_below_internal_saving=internal_saving-q,q_below_leaf_saving=leaf_saving-q,
        q_below_reservation_c=c-q,
        c_positive=c,c_below_one=1-c,beta_positive=beta,beta_below_one=1-beta,
        epsilon_positive=eps,epsilon_below_one=1-eps,lambda_above_tau=lam-tau,
        lambda_above_sigma=lam-sigma,compact_internal=lam-internal,
        lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,compact_reservations=lp-reserve,
        linear_scalar_guard=1-eps,K_smaller_than_ell=geometry,K_dominates_log_p=eps*c,
        record_suffix_superpolynomial=1-eps,phase_local_cost=1-eps-delta,
        phase_boundary_cost=r-delta,gamma_sublinear=1-eps-r,
        cell_larger_than_band=eps-(1-r)/2,prime_interval_packing=1-eps,
        alpha_power=r,delta_positive=delta,delta_below_one_eighth=Q(1,8)-delta,
        prefix_vs_layer=g1-G,movement_vs_layer=a-G,exposure_vs_layer=a-G,
        gaussian_vs_layer=margins['g5']-G,scalar_vs_layer=margins['g6']-G,
        dimension_vs_layer=eps-G,absorption=G-kappa,improvement_over_accepted=kappa-previous,
        old_nonadjacent_synthetic_margin_fails=kappa-eps*a*c,
        old_separate_resampling_exposure_fails=kappa-a*(1-eps),
        small_field_exposure_vs_layer=1-eps-G,
        microbox_artificial_boundary_vs_layer=8-eps+r-delta-G)
    if prefix=='balanced':
        require(1-eps-G==h and 1-eps-r==h/2,'Balanced exact small scale gaps differ')
        if row['mode']=='tight':slacks['old_prefix_estimate_fails']=kappa-geometry
    else:require(g1-G==h,'Original exact prefix gap differs')
    require(set(slacks)==set(row['constraint_slacks']),'Declared complete constraint set differs')
    require(all(Q(row['constraint_slacks'][k])==v>0 for k,v in slacks.items()),
            'A complete strict assembly slack differs or is nonpositive')
    extra=dict(short_record_elementary_fallback=eps-a,
               gamma_constant_power_range=Q(1,4)-r,
               alpha_below_sqrt_p=1-r,lambda_prime_below_one=q,
               strict_recurrence_intermediate_gap=lp-lam,phase_leaf_above_bit=b/2-a,
               joint_row_degree=89000-Q(49*651+41*272)*(2+Q(1,25)))
    require(all(v>0 for v in extra.values()),'Additional router/Gaussian interface range failed')

    ka,km,kb=ceil_q(1/r),ceil_q(1/(eps*c)),ceil_q(1/(1-eps))
    cuts=dict(gamma=ceil_q(7/(1-eps-r)),logarithmic_alpha=16*ka*ka+1,
        full_guard=ceil_q(Q((2*C0).bit_length())/(1-eps)),
        phase_cell=ceil_q(9/(eps-(1-r)/2)),compact_controls=64*km*km+1,
        K_geometry=ceil_q(3/geometry),microbox_period=128*kb*kb+1,routing_reservoirs=14)
    kstop=ceil_q(1/(eps*beta));minimum=max(n['m'],nc['m'])
    cuts['stopped_leaf']=kstop*(4*minimum).bit_length()
    cuts['common']=max(cuts.values())
    require(row['cutoff_log2_b']==cuts,'Independent exact numeric cutoffs differ')
    require(cuts['gamma']*(1-eps-r)>=7 and
            cuts['full_guard']*(1-eps)>=(2*C0).bit_length() and
            cuts['phase_cell']*(eps-(1-r)/2)>=9 and cuts['K_geometry']*geometry>=3,
            'Guard/gamma/cell/geometry cutoff inequalities fail')
    compact=row['strengthened_real_log_compact_cutoff']
    require(compact['k']==km and compact['L0']==cuts['compact_controls'] and
            compact['denominator_slope']==32 and compact['denominator_constant']==192,
            'Real-log compact-field proof parameters differ')
    require(cuts['compact_controls']>=2*km and cuts['microbox_period']>=2*kb,
            'Monotonic real-log derivative range not established')
    compact_proof=power_certificate(compact['strict_power_certificate'],
        cuts['compact_controls']//km,32*cuts['compact_controls']+192)
    period_proof=power_certificate(row['microbox_period_power_certificate'],
        cuts['microbox_period']//kb,16*cuts['microbox_period']+56)
    # An independent, stronger alpha certificate: p^r >8log2(b)+64.
    alpha_exp=cuts['logarithmic_alpha']//ka
    require(alpha_exp >= (8*cuts['logarithmic_alpha']+64).bit_length() and
            cuts['logarithmic_alpha']>=2*ka,'Linear-log alpha domination cutoff fails')
    # This ceiling applies only to the declared certified exponent a.
    # It is not an exclusion of stronger future finite/recurrence primitives.
    factor = 1 if prefix == 'balanced' else 2
    upper = min(a,b)/(1+factor*min(a,b))
    beta_cap=min(internal_saving,leaf_saving)
    fixed_beta_upper=beta_cap/(1+factor*beta_cap)
    require(Q(row['fixed_beta_parameter_upper'])==fixed_beta_upper and
        kappa<fixed_beta_upper<=upper,'General stopping fixed-beta cap differs')
    require(Q(row['declared_exponent_parameter_upper']) == upper and kappa < upper,
            'Declared-exponent parameter cap differs')
    require(Q(row['achieved_fraction_of_parameter_upper']) == kappa/upper,
            'Declared cap attainment differs')
    padding = row['compact_row_padding']
    require(padding['status'].startswith('PASS') and padding['reciprocal_exponent_ceiling'] == kb and
            padding['real_log_lower'] == cuts['common'] and len(padding['checks']) == 6,
            'New recursive row-padding input differs')
    require(row['bit_counts']['W'] < 2**49 and cuts['common'] >= max(25, 2*kb),
            'New row divisor or real-log monotonicity range fails')
    row_checks = []
    for j, record in enumerate(padding['checks']):
        L = cuts['common']*2**j
        require(record['log2_b'] == L, 'Row-padding checkpoint differs')
        row_checks.append(power_certificate(record['strict_power_certificate'], L//kb, 356000*(L+8)))
    require(padding['fixed_eventual_setup']=='Common bit/complex alphabet/table/layout C; p>=max(C,2^25), no e<=2p assertion' and
        padding['bit_maximum_child']==51**3-4*51 and padding['complex_maximum_child']==28**3-2*28 and
        padding['bit_depth_per_ceil_log2e']==651 and padding['complex_depth_per_ceil_log2e']==272 and
        Q(padding['row_degree_rational_slack'])==89000-Q(49*651+41*272)*(2+Q(1,25))>0 and
        padding['inequality']=='b^(1-epsilon)>356000*(log2(b)+8)' and
        padding['row_divisor']=='Wcomplex^Dcomplex*Wbit^Dbit<p^89000 after e<=C*p,p>=C,log2(p)>=25' and
        padding['no_suffix_to_prefix_gather'] and padding['max_only_stock_rejected'] and
        padding['old_p66000_not_reused_as_complete_bound'] and
        padding['reservation']=='One initial complete leading prefix and padding; bit factors park/restore within each complex factor' and
        padding['preprocessing']=='O(V logp) leading selected C1 prefix paid once per outer invocation, not at descendants',
        'Nested89000-degree product, complete leading prefix or one-padding contract differs')
    stopping=row['stopped_leaf_certificate']
    require(stopping['status'].startswith('PASS') and stopping['minimum']==minimum and
        stopping['reciprocal_exponent_ceiling']==kstop and len(stopping['checks'])==6 and
        stopping['sufficient']=='b^(epsilon*beta)>4max(m_bit,m_complex)' and
        stopping['implication']=='d=floor(b^epsilon)>=b^epsilon/2 and beta<1 imply d^beta>2max(m_bit,m_complex)' and
        stopping['integer_stopping_test']=='e^v<d^u for fixed beta=u/v; fixed rational exponents need no real-power comparison',
        'Exact fixed-rational stopping comparison or floor qualification differs')
    stop_checks=[]
    for j,record in enumerate(stopping['checks']):
        L=cuts['common']*2**j
        require(record['log2_b']==L,'Stopped leaf checkpoint differs')
        stop_checks.append(power_certificate(record['strict_power_certificate'],L//kstop,4*minimum))
    require(cuts['stopped_leaf']*eps*beta>=(4*minimum).bit_length(),
        'Stopping exponent cutoff failed')
    require(Q(row['strict_gain'])==kappa-previous and
            Q(row['improvement_ratio'])==kappa/previous and
            Q(row['compact_upstream_ratio'])==kappa/Q(83,10**12),
            'Improvement/count comparison differs')
    return dict(mode=row['mode'],prefix=prefix,kappa=str(kappa),minimum_margin=str(G),
        complete_declared_strict_conditions=len(slacks),additional_interface_conditions=len(extra),
        bit_roles=row['bit_counts']['side_roles'],complex_ground=nc['h'],complex_roles=nc['R'],
        independent_log_enclosures=log_records,cutoffs=cuts,
        compact_power=compact_proof,microbox_period_power=period_proof,
        logarithmic_alpha_power=dict(exponent=alpha_exp,
            right_bit_length=(8*cuts['logarithmic_alpha']+64).bit_length(),strict=True),
        declared_exponent_parameter_upper=str(upper),
        row_padding_compressed_checks=row_checks,stopped_leaf_compressed_checks=stop_checks,
        scalar_gate_count=Gscalar,literal_scalar_depth=literal_depth,
        ratio_to_83_over_10_to_12=str(kappa/Q(83,10**12)),
        old_unproved_estimates_reject_this_witness=True,
        enormous_power_allocation_performed=False)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    names=('certificate','previous','previous-review','generic-inputs','complex-review',
           'phase-review','controls-review','transfer-review','transfer-report','output')
    for name in names:
        ap.add_argument('--'+name,type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh result path')
    start=time.monotonic();code=Path(__file__).parent;topic=code.parent
    files=[getattr(args,name.replace('-','_')) for name in names if name!='output']
    hashes={str(p):digest(p) for p in files}
    data=json.loads(args.certificate.read_text());old=json.loads(args.previous.read_text())
    prior=json.loads(args.previous_review.read_text());generic=json.loads(args.generic_inputs.read_text())
    changed=json.loads(args.complex_review.read_text());phase=json.loads(args.phase_review.read_text())
    controls=json.loads(args.controls_review.read_text());transfer=json.loads(args.transfer_review.read_text())
    require(prior['status']=='PASS independent complete delayed-complex generic-basis general-beta assembly'
        and prior['input_sha256'][str(args.previous)]==digest(args.previous),
        'Accepted uniform complete predecessor is not pinned')
    for name,expected in prior['reviewer_source_sha256'].items():
        require(digest(code/name)==expected,'Accepted complete reviewer source changed '+name)
    require(changed['status']=='PASS independent binary delayed-clone theorem and complete changed h28 witness'
        and phase['status']=='PASS independent exact b_phase=10^-6 on accepted changed h28'
        and controls['status']=='PASS independent mixed whole-rank complex interface controls'
        and transfer['status']=='PASS independent complete whole-rank complex transfer qualifications',
        'New whole-phase finite, algebra, characteristic and transfer acceptances required')
    for review in (changed,phase,controls,transfer):
        sources=review['source_sha256']
        if isinstance(sources,str):
            name={phase['status']:'review_whole_complex_characteristic.py',
                  controls['status']:'review_whole_complex.py',
                  transfer['status']:'review_whole_complex_transfer.py'}[review['status']]
            require(digest(code/name)==sources,'Independent whole-phase source changed '+name)
        else:
            for name,expected in sources.items():
                require(digest(code/name)==expected,'Independent changed finite source changed '+name)
        for name,expected in review.get('dependency_sha256',{}).items():
            require(digest(code/name)==expected,'Independent transfer dependency changed '+name)
    require(digest(args.transfer_report)=='0a12490909187459e87d1ac20e781d5758d3512ea0202a9795ba5f35ea976506'
        ==data['whole_transfer_report_sha256'], 'Full independently reviewed written transfer changed')
    report_inputs={
        topic/'reports/whole-complex-concatenation.md':'5781af807210dc3ac740e876cdb8073683ea3658f4b8aa067605608919a8f520',
        topic/'reports/whole-complex-prefix-and-wrapper-qualification.md':'84ebd3bb5327ccd04134db36d0b109b377c6d6cf2c0c82923d1c35b596dc43b2'}
    for path,expected in report_inputs.items():
        require(digest(path)==expected and transfer['inputs'][str(path)]==expected,
                'Frozen leading prefix, mixed phase or tape construction is not pinned')
    for path in (args.complex_review,args.phase_review,args.controls_review):
        require(transfer['inputs'][str(path)]==digest(path),'Final full transfer has different reviewed input')
    require(data['unchanged_generic_root_inputs_sha256']==digest(args.generic_inputs)
        and generic['status']=='PASS root independent generic-basis inputs and written theorem review'
        and data['generic_characteristic_certificate']==old['generic_characteristic_certificate']
        and data['odd_bit_finite_audit']==old['odd_bit_finite_audit']==prior['unchanged_finite_identity']
        and data['changed_complex_finite_audit']==old['changed_complex_finite_audit']==prior['changed_complex_finite_audit'],
        'Accepted finite graphs or constructive generic basis changed')
    for name,expected in data['source_sha256'].items():
        require(digest(code/name)==expected,'Executed producer source changed '+name)
    for name,record in data['input_files'].items():
        path=Path(name)
        if not path.is_absolute():path=topic/path
        require(digest(path)==record['sha256'] and path.stat().st_size==record['bytes'],
                'Frozen whole-complex input bytes changed '+str(path))
    require(any(r['sha256']==digest(args.previous_review) for r in data['input_files'].values()),
            'Whole composition does not pin its complete preceding review')
    primitive=data['generic_characteristic_certificate']['witness']
    native=audit_primitive(primitive,generic)
    rebuilt_phase=audit_phase(phase,changed['full'],primitive,data['whole_complex_characteristic'])
    counts=complex_counts(data['changed_complex_finite_audit']['counts'])
    c=changed['full']['complete_changed_logical']['additions']
    Gscalar=3*counts['v']**2*(4*(c+counts['v'])+4*counts['v']+4)
    E=64*(counts['W']+counts['m']+1)**3
    charged=2*Gscalar*counts['W']**2+8*counts['s']+4*counts['W']+4+32*counts['m']
    guard=transfer['finite_count_and_guard']
    require(Gscalar==13074237304128==guard['G'] and guard['W']==counts['W']
        and guard['s']==counts['s'] and guard['E']==E and charged==guard['stronger_wrapper_tail_depth']
        and E-charged==guard['strict_E_slack']>0 and guard['C1']==1,
        'Actual wrappers, tails or new literal coefficient guard are unpaid')
    contract=data['accepted_whole_complex_transfer']
    require(contract['status']=='INDEPENDENT COMPLETE WHOLE-RANK TRANSFER ACCEPTED'
        and contract['literal_enhanced_guard']==guard
        and contract['product_row_stock']==transfer['combined_rows']
        and contract['product_row_stock']['exact_product']=='W_complex^D_complex*W_bit^D_bit'
        and contract['product_row_stock']['polynomial_degree']==89000
        and contract['product_row_stock']['sufficient_suffix_slope']==356000
        and contract['product_row_stock']['one_initial_leading_prefix']
        and contract['reviewed_controls']['weighted_frontier'],
        'Complete field/volume, prefix or variable-tree interface missing')
    require(changed['small']['complete_dirty_basis']['complete_basis_dimension']==939
        and changed['small']['complete_dirty_basis']['forward_identity_shear_and_inverse_exact']
        and changed['small']['complete_shared_exchange']['all_dirty_banks_restored_exactly'],
        'Actual changed finite input has no complete dirty boundary acceptance')
    old_best=max(old['witnesses'],key=lambda row:Q(row['parameters']['kappa']))
    require(Q(data['previous_accepted_kappa'])==Q(old_best['parameters']['kappa'])
        ==max(Q(r['kappa']) for r in prior['rows']), 'Previously accepted exact comparison differs')
    regression=[dict(mode=r['mode'],prefix=r['prefix'],kappa=r['parameters']['kappa'],unchanged=True)
        for r in old['witnesses']]
    require(data['accepted_uniform_regressions']==regression,'Accepted four uniform rows were not retained exactly')
    rows=[]
    for row in data['witnesses']:
        require(row['bit_counts']==primitive['counts'] and row['complex_counts']==data['changed_complex_finite_audit']['counts']
            and row['complex_branching_certificate']==data['whole_complex_characteristic']
            and row['whole_complex_transfer']==contract and row['semantic_guard']['scalar_gates']==Gscalar,
            'A new complete row uses different actual primitive inputs')
        rows.append(audit_row(row,old_best,primitive,phase))
    require({(r['mode'],r['prefix']) for r in rows}==
        set(product(('conservative','tight'),('original','balanced'))), 'Four independent complete rows required')
    result=dict(status='PASS independent complete whole-complex generic-bit conditional assembly',
        generated_utc=datetime.now(timezone.utc).isoformat(),campaign='20261007T222521Z',input_sha256=hashes,
        root_written_inputs={str(p):h for p,h in report_inputs.items()},
        source_sha256=digest(Path(__file__)),
        dependency_sha256={name:digest(code/name) for name in
            ('review_parameter_audit.py','review_packed_unrolling.py','review_semantic_bulk_assembly.py')},
        exact_native_bit=native,independent_whole_phase=rebuilt_phase,rows=rows,
        new_nested_prefix_controls=prefix_controls(),actual_enhanced_scalar_guard=guard,
        all_size_written_transfer_independently_reviewed=True,
        unchanged_finite_bit=data['odd_bit_finite_audit'],unchanged_finite_complex=data['changed_complex_finite_audit'],
        wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        limitations=['Conditional written interfaces; full giant bit basis/table/prime not instantiated',
            'Homogeneous sigma pays native bit overhead tau; no standalone runtime below tau is claimed',
            'Numeric cutoff excludes separate new setup/layout/record/strict absorption/full-machine thresholds',
            'No unconditional theorem, optimizer optimality or established novelty claim'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for row in rows:print('PASS',row['mode'],row['prefix'],row['kappa'],flush=True)


if __name__=='__main__':main()
