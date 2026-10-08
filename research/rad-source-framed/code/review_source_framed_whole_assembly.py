#!/usr/bin/env python3
"""Independent complete assembly for the nonzero-source-framed h53/R529181 graph.

The accepted complete algebra is inherited from a frozen independent reviewer;
new native counts, normalized characteristic and joint row product are rebuilt.
No new producer or finite graph selector is imported. Previously accepted
physical baselines are not replayed.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import resource
import time

from review_semantic_bulk_assembly import ceil_q, complex_counts, power_certificate, require
from review_source_frame_inputs import characteristic, reconstruct, logs
from review_whole_complex_assembly import bounds


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def finite_counts(raw):
    h,R=raw['h'],raw['side_roles']
    from math import comb
    v,m=comb(h,3),h**3;N=v**3;W=2*N+2*v*v*(R+h)
    difference=3*v*v*h*h-int(raw['L'])
    require(difference%(3*v*v)==0, 'Nonintegral protected-center decrement')
    protected=difference//(3*v*v)
    require(h==53 and R==529181 and protected in (0,1,2), 'Unaccepted new native variant')
    L=3*v*v*(h*h-protected)
    n=dict(v=v,m=m,N=N,W=W,L=L,D=N-2*L,s=W*m-N+2*L)
    for k,x in n.items():
        if k in raw:require(Q(raw[k])==x,'Changed native count differs '+k)
    require(Q(raw['eta'])==Q(n['D'],W*m) and 0<n['D'] and n['s']<m**5,
            'Changed native eta or coefficient budget fails')
    return n


def audit_native(p,base,root_component,budget):
    k=p['protected_centers']; require(k in (0,1,2),'Unaccepted protected variant')
    own=characteristic(base,k)
    n=finite_counts(p['counts']);a=Q(p['saving']);lm=Q(p['logarithm_intervals']['m'][1])
    require(a==Q(own['saving']), 'Independent strict two-star saving differs')
    require(a==Q(root_component['variants'][k]['saving']), 'Independent final zero/one/two-star saving differs')
    for key in ('kernel_dimensions','family_multiplicities','family_ranks','grouped_runs'):
        require(p[key]==own[key],'Actual generic family differs '+key)
    require(lm>=Q(own['log_m_upper']), 'New producer logarithm is not an upper bound')
    for family,r in own['grouped_runs'].items():
        lower,upper=logs(r);saved=p['logarithm_intervals'][str(r)]
        require(Q(saved[0])<=lower<=upper<=Q(saved[1]), 'New grouped logarithm is not enclosed')
    linear=Q(p['taylor_linear_coefficient']);quadratic=Q(p['taylor_quadratic_coefficient'])
    require(linear>=Q(own['normalized_linear_upper'])>0 and
            quadratic>=Q(own['normalized_quadratic_upper'])>0 and 0<a*lm<1,
            'Normalized new characteristic coefficients are not conservative')
    gap=n['D']-a*linear-a*a*quadratic/(1-a*lm)
    require(gap==Q(p['strict_taylor_gap'])>0 and Q(own['strict_gap'])>=gap,
            'Normalized exact generic characteristic fails')
    require(p['maximum_child_rank']==own['maximum_child'] and
            p['depth_per_ceil_log2e']==own['halving_degree']==974 and
            p['W_binary_upper_exponent']==own['wire_log2_ceiling']==50 ,
            'Changed native child width or exact halving proof differs')
    G_upper=budget['scalar_gates']+3*k*n['v']*n['v']
    E=budget['E'];charge=2*G_upper*n['W']**2+4*n['s']+4*n['W']+4
    require(E>charge, 'Conservative charge for every added grouped bit gate exceeds E')
    return dict(protected_centers=k,chosen_saving=str(a),strict_normalized_gap=str(gap),
                conservative_new_bit_G_upper=G_upper,new_bit_depth_upper=charge,
                bit_E_unchanged=E,strict_new_bit_guard_slack=E-charge,
                independent_longer_gap=own['strict_gap'],actual_counts=p['counts'],
                all_size_generic_frame_families=own['family_ranks'],halving_degree=974,
                W_binary_upper_exponent=50,joint_row_degree=own['row_degree'],
                giant_table_prime_materialized=False)


def audit_row(row, old_tight, primitive, phase):
    n=finite_counts(row['bit_counts']);nc=complex_counts(row['complex_counts'])
    bd=primitive['depth_per_ceil_log2e'];bb=n['W'].bit_length()
    degree=row['compact_row_padding']['polynomial_degree'];slope=4*degree
    coefficient=bb*bd+41*272
    require(degree==1000*ceil_q(Q(coefficient)*(2+Q(1,25))/1000), 'Changed joint degree differs')
    p={k:Q(v) for k,v in row['parameters'].items()}
    a,b,tau,sigma,c,beta,eps,lam,lp,r,delta,kappa=(p[k] for k in
        ('a_bit','a_complex','tau','sigma','c','beta','epsilon','lambda_',
         'lambda_prime','alpha_squared_power','delta','kappa'))
    log_records={}
    primitive_gaps={}
    ec = row['complex_branching_certificate']
    require(b == Q(7,5*10**6) == Q(phase['saving']) == Q(ec['chosen_saving']) and
        Q(ec['independent_coarse_gap']) == Q(phase['strict_normalized_gap']) > 0,
        'Whole phase row has no exact accepted homogeneous characteristic')
    log_m = Q(10)  # The new certificate deliberately uses this coarse upper bound.
    saved_gap = nc['D']-b*Q(ec['normalized_linear_upper'])-b*b*Q(ec['normalized_quadratic_upper'])/(1-b*log_m)
    require(saved_gap == Q(ec['strict_primitive_gap']) > 0 and
        Q(ec['independent_coarse_gap']) == Q(phase['strict_normalized_gap']),
        'Saved complete positive-exponential phase certificate differs')
    primitive_gaps['complex_primitive'] = saved_gap
    log_records['complex'] = dict(exponent_kind='Homogeneous weighted tree; paid bit overhead retained',
        chosen_saving=str(b),independent_longer_log_terms=128)
    require(a == Q(primitive['saving']), 'Explicit Taylor saving differs')
    eb = row['bit_saving_certificate']
    require(eb['certificate_kind'] == 'SOURCE-FRAME MIDDLE RELOCATION, GENERIC METRIC FLAGS, NORMALIZED POSITIVE EXPONENTIAL',
            'New primitive must not use a uniform rank-saving enclosure')
    require(Q(eb['chosen_saving']) == a and
            Q(eb['strict_primitive_gap']) == Q(primitive['strict_taylor_gap']) and
            Q(eb['taylor_linear_coefficient']) == Q(primitive['taylor_linear_coefficient']) and
            Q(eb['taylor_quadratic_coefficient']) == Q(primitive['taylor_quadratic_coefficient']),
            'Row primitive certificate differs from the reviewed Taylor input')
    primitive_gaps['bit_primitive'] = Q(primitive['strict_taylor_gap'])
    require(primitive_gaps['bit_primitive'] > 0, 'Normalized positive-exponential Taylor gap is not strict')
    require(tau==1-a and sigma==1-b and 0<a<b<Q(1,32) and (1-beta)*b>a,'New bit-limited whole-phase branch invalid')
    h=Q(1,2**(20 if row['mode']=='conservative' else 64))
    require(row['mode'] in ('conservative','tight'),'Unknown fixed parameter mode')
    require(beta==Q(1,8),'Chosen whole-complex stopping threshold differs')
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
               strict_recurrence_intermediate_gap=lp-lam,phase_leaf_above_bit=(1-beta)*b-a,
               joint_row_degree=degree-Q(coefficient)*(2+Q(1,25)))
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
    require(row['bit_counts']['W'] < 2**bb and cuts['common'] >= max(25, 2*kb),
            'New row divisor or real-log monotonicity range fails')
    row_checks = []
    for j, record in enumerate(padding['checks']):
        L = cuts['common']*2**j
        require(record['log2_b'] == L, 'Row-padding checkpoint differs')
        row_checks.append(power_certificate(record['strict_power_certificate'], L//kb, slope*(L+8)))
    require(padding['fixed_eventual_setup']=='New fixed bit table/prime/layout C; p>=max(C,2^25), no e<=2p assertion' and
        padding['bit_maximum_child']==n['m']-2*row['bit_counts']['h'] and padding['complex_maximum_child']==28**3-2*28 and
        padding['bit_depth_per_ceil_log2e']==bd and padding['complex_depth_per_ceil_log2e']==272 and
        Q(padding['row_degree_rational_slack'])==degree-Q(coefficient)*(2+Q(1,25))>0 and
        padding['inequality']==f'b^(1-epsilon)>{slope}*(log2(b)+8)' and
        padding['row_divisor']==f'Wcomplex^Dcomplex*Wbit^Dbit<p^{degree} after e<=C*p,p>=C,log2(p)>=25' and
        padding['no_suffix_to_prefix_gather'] and padding['max_only_stock_rejected'] and
        padding['prior_ground_stock_not_assumed'] and padding['polynomial_degree']==degree and padding['sufficient_suffix_slope']==slope and padding['stock_base_two_coefficient']==coefficient and padding['bit_wire_binary_upper_exponent']==bb and padding['complex_wire_binary_upper_exponent']==41 and
        padding['reservation']=='One initial complete leading prefix and padding; bit factors park/restore within each complex factor' and
        padding['preprocessing']=='O(V logp) leading selected C1 prefix paid once per outer invocation, not at descendants',
        'Changed-ground product, complete leading prefix or one-padding contract differs')
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


def check_sources(data,code,default=None):
    sources=data.get('source_sha256',{})
    if isinstance(sources,str):
        require(default is not None,'Unnamed frozen source');sources={default:sources}
    for name,expected in sources.items():require(digest(code/name)==expected,'Frozen source changed '+name)
    for name,expected in data.get('dependency_sha256',{}).items():
        require(digest(code/name)==expected,'Frozen dependency changed '+name)




def phase_review(ec,old_phase,finite):
    raw=dict(finite['counts']);raw['eta']=str(Q(raw['D'],raw['W']*raw['m']));n=complex_counts(raw)
    h,m,v,R=(n[k] for k in ('h','m','v','R'))
    copies=dict(middle=(R+h+1)*v*v,joined=(R+h+1)*v*v,data=2*n['N'])
    ranks=dict(middle=m-h*h,joined=m-2*h,data=(h*h-1)*(h-1))
    credited=sum(copies[k]*ranks[k] for k in ranks);individual=n['s']-credited
    from collections import Counter
    hist=Counter({1:individual})
    for k,r in ranks.items():hist[r]+=copies[k]
    require(ec['counts']==raw and ec['grouped_children']==ranks and ec['family_multiplicities']==copies
            and ec['child_histogram']=={str(r):c for r,c in hist.items()}
            and ec['child_histogram']==old_phase['child_histogram']
            and ec['total_grouped_rank']==credited and ec['all_other_individual_pivots']==individual>0,
            'The accepted whole-complex three-family histogram changed')
    lm=bounds(m)[1];moment=sum(copies[k]*ranks[k]*bounds(ranks[k])[0] for k in ranks)
    require(lm<10 and all(bounds(r)[0]>Q(99,10) for r in ranks.values()),
            'Independent longer logs do not support the new coarse phase bound')
    for k,r in dict(m=m,**ranks).items():
        lo,hi=bounds(r);saved=ec['logarithm_intervals'][k]
        require(Q(saved[0])<=lo<=hi<=Q(saved[1]),'Frozen accepted phase logs changed')
    b=Q(7,5*10**6);linear=10*n['s']-Q(99,10)*credited;quad=50*n['s']
    coarse=n['D']-b*linear-b*b*quad/(1-10*b)
    fine=n['D']-b*(n['s']*lm-moment)-b*b*n['s']*lm*lm/(2*(1-b*lm))
    require(0<coarse<=fine and Q(ec['chosen_saving'])==b and Q(ec['sigma'])==1-b
            and Q(ec['normalized_linear_upper'])==linear and Q(ec['normalized_quadratic_upper'])==quad
            and Q(ec['rank_log_moment_lower'])==Q(99,10)*credited
            and Q(ec['strict_primitive_gap'])==Q(ec['independent_coarse_gap'])==coarse,
            'Independent new homogeneous complex characteristic failed')
    require(m**272>2*(m-2*h)**272 and n['W']<2**41,
            'Unchanged complex variable-child depth/stock failed')
    return dict(saving=str(b),strict_normalized_gap=str(coarse),independent_longer_gap=str(fine),
                same_accepted_child_histogram=ec['child_histogram'],log_terms=128,dyadic_bits=384)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    names=('certificate','current-assembly','current-review','analytic-assembly','candidate',
           'finite-review','generic-inputs','source-frame-component','source-frame-report',
           'finite-source-control','boundary-report','transfer-review','complex-review')
    for name in (*names,'output'):ap.add_argument('--'+name,type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Choose a fresh output path');t=time.monotonic();code=Path(__file__).parent
    data=json.loads(args.certificate.read_text());old=json.loads(args.current_assembly.read_text())
    peer=json.loads(args.current_review.read_text());analytic=json.loads(args.analytic_assembly.read_text())
    candidate=json.loads(args.candidate.read_text());finite=json.loads(args.finite_review.read_text())
    component=json.loads(args.generic_inputs.read_text());source=json.loads(args.source_frame_component.read_text())
    control=json.loads(args.finite_source_control.read_text());transfer=json.loads(args.transfer_review.read_text())
    complex_finite=json.loads(args.complex_review.read_text())
    require(data['status']=='PASS STRICT NONZERO-SOURCE-FRAMED WHOLE-COMPLEX ASSEMBLY; FINAL INDEPENDENT REVIEW REQUIRED',
            'Wrong new source-frame producer')
    require(peer['status']=='PASS independent complete closing direct-first h53 zero one two protected whole-complex assembly'
            and peer['input_sha256'][str(args.current_assembly)]==digest(args.current_assembly),
            'Accepted complete predecessor is absent')
    check_sources(peer,code,'review_closing_whole_assembly.py')
    for record in (old,analytic,data):check_sources(record,code)
    check_sources(component,code,'review_source_frame_inputs.py')
    check_sources(source,code,'review_auxiliary_source_frames.py')
    check_sources(control,code,'finite_auxiliary_source_frames_v2.py')
    for record in (peer,component,source,data):
        for path,expected in record['input_sha256'].items():
            p=Path(path) if Path(path).is_absolute() else code.parent/path
            require(digest(p)==expected,'Frozen reviewed input changed '+str(p))
    require(digest(args.source_frame_report)=='512ea5f5d2b8913df4896d95cf9a75411e8e63147f4bf7197ac583b9a1a8e84c'
            and digest(args.boundary_report)=='5db6da9e4fad7fe42783a0648a42e11e3713e7db0c4e6b3fd55e502c327f35dc',
            'New all-size source-frame proof/actual-boundary acceptance changed')
    require(source['status']=='PASS INDEPENDENT NONZERO AUXILIARY SOURCE TRANSFER COMPONENT'
            and component['status']=='PASS independent source-frame generic characteristic arithmetic'
            and component['compiled_sha256']==candidate['checked']['compiled_sha256'],
            'Independent exact new primitive inputs are absent')
    require(control['status']=='PASS actual middle source-frame endpoints and native dirty gauge'
            and control==data['actual_source_frame_endpoint_audit'] and source==data['source_frame_component_audit']
            and control['actual_side_endpoints']['every_actual_physical_role_has_D0_first_and_D1_last']
            and control['actual_side_endpoints']['early_or_late_retained_gate_exclusions']==0
            and control['centers']['exclusions']==0, 'Actual source-frame endpoint contract failed')
    require(finite['status']=='PASS INDEPENDENT CLOSING DIRECT-FIRST-ALLOCATION COMPOUND'
            and finite['input_sha256'][str(args.candidate)]==digest(args.candidate)
            and finite['candidate_id']==control['candidate_id']==peer['accepted_finite_candidate'],
            'New source-frame chart uses an unpromoted scalar graph')
    base,budget=reconstruct(candidate)
    for key in ('h','v','m','N','W','L','D','s'):
        require(finite['full']['exact_counts'][key]==base[key],'Independent actual count differs '+key)
    best=max(old['witnesses'],key=lambda r:Q(r['parameters']['kappa']));previous=Q(best['parameters']['kappa'])
    require(previous==max(Q(r['kappa']) for r in peer['rows'])==Q(data['previous_accepted_kappa']),
            'Previous complete saving differs')
    regressions=[dict(native_construction_id=r['native_construction_id'],mode=r['mode'],prefix=r['prefix'],
                      kappa=r['parameters']['kappa'],unchanged=True) for r in old['witnesses']]
    require(data['accepted_closing_twelve_row_regressions']==regressions and len(regressions)==12,
            'All twelve accepted predecessor rows must be retained')
    require(data['complex_counts_unchanged']==best['complex_counts']
            and data['complex_scalar_G_unchanged']==transfer['finite_count_and_guard']['G'],
            'Accepted actual complex table/guard changed')
    native={};primitives={}
    for p in data['generic_characteristics']:
        ident=p['construction_id'];require(ident not in native,'Duplicate new native identity')
        native[ident]=audit_native(p,base,component,budget);primitives[ident]=p
    require(len(native)==3 and {x['protected_centers'] for x in native.values()}=={0,1,2},
            'All three reviewed new native variants required')
    phase=phase_review(data['witnesses'][0]['complex_branching_certificate'],
                       analytic['whole_complex_characteristic'],complex_finite['full'])
    require(Q(data['complex_new_coarse_saving'])==Q(phase['saving'])
            and Q(data['complex_new_coarse_gap'])==Q(phase['strict_normalized_gap'])
            and data['complex_accepted_child_histogram_unchanged'], 'New coarse phase identity differs')
    rows=[]
    for row in data['witnesses']:
        ident=row['native_construction_id'];p=primitives[ident];own=native[ident]
        require(row['bit_counts']==p['counts'] and row['complex_counts']==best['complex_counts'],
                'New native row uses different physical counts')
        guard=row['native_bit_primitive']['conservative_changed_center_bit_guard']
        require(guard['G_upper']==own['conservative_new_bit_G_upper'] and guard['E']==own['bit_E_unchanged']
                and guard['depth_upper']==own['new_bit_depth_upper']
                and guard['strict_slack']==own['strict_new_bit_guard_slack']>0,
                'New source-frame/added-center guard is not fully charged')
        phase_review(row['complex_branching_certificate'],analytic['whole_complex_characteristic'],complex_finite['full'])
        ec=row['complex_branching_certificate'];a=Q(p['saving']);b=Q(phase['saving'])
        require(Q(ec['new_native_bit_saving'])==a and Q(ec['phase_above_twice_bit'])==b-2*a<0
                and Q(ec['beta_half_leaf_above_bit'])==b/2-a<0
                and Q(ec['beta_eighth_leaf_above_bit'])==b*Q(7,8)-a>0,
                'Costed general stopping beta or old-half negative differs')
        contract={k:v for k,v in row['whole_complex_transfer'].items()
                  if k not in ('changed_bit_product_stock','old_combined_rows_historical_only')}
        require(contract==analytic['accepted_whole_complex_transfer']
                and row['whole_complex_transfer']['changed_bit_product_stock']==row['compact_row_padding'],
                'Mixed whole-complex/tail/semantic transfer changed')
        result=audit_row(row,best,p,phase);result['native_construction_id']=ident;rows.append(result)
    require(len(rows)==12 and {(r['native_construction_id'],r['mode'],r['prefix']) for r in rows}==
            set(product(native,('conservative','tight'),('original','balanced'))), 'Twelve complete new rows required')
    strongest=max(Q(r['kappa']) for r in rows)
    require(strongest>previous and strongest>Q(1076678,10**12),
            'New fully composed witness does not exceed the reported PR15 saving')
    files=[getattr(args,k.replace('-','_')) for k in names]
    result=dict(status='PASS independent complete source-framed h53 zero one two protected whole-complex assembly',
        campaign='20261007T222521Z',generated_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=digest(Path(__file__)),input_sha256={str(p):digest(p) for p in files},
        dependency_sha256={name:digest(code/name) for name in ('review_parameter_audit.py','review_source_frame_inputs.py',
            'review_whole_complex_assembly.py','review_semantic_bulk_assembly.py')},
        accepted_finite_candidate=finite['candidate_id'],actual_bit_budget=budget,
        independent_native_variants=native,independent_phase_recertification=phase,rows=rows,
        unchanged_twelve_predecessor_rows=regressions,previous_accepted_kappa=str(previous),
        wall_seconds=time.monotonic()-t,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        limitations=['Written conditional transfer and exact independent controls, not formal machine verification',
            'Nonzero auxiliary source mechanism is eumemic PR13; our exact DAG/metric-basis/wholeC composition is separately checked',
            'The giant native table/shared prime, setup/record/strict absorption/upstream thresholds remain separately eventual',
            'Same accepted three complex families only; PR14 data corners and PR15 all-residual classes are not imported'])
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for row in rows:print('PASS',row['native_construction_id'],row['mode'],row['prefix'],row['kappa'],flush=True)


if __name__=='__main__':main()
