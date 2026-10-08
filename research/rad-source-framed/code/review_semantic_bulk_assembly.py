#!/usr/bin/env python3
"""Independent exact arithmetic for the reviewed semantic/bulk interfaces.

Only existing independent reviewer functions are imported. No producer
is imported, no finite graph is reconstructed and no huge power is expanded.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path
import resource
import subprocess
import time

from review_asymmetric_motif import independent_saving
from review_compact_generic import audit_row as audit_old_row, promoted_metadata
from review_packed_unrolling import finite_counts


def require(c,m):
    if not c:raise AssertionError(m)


def ceil_q(x):
    return -(-x.numerator//x.denominator)


def power_certificate(raw, exponent, right):
    require(raw['exponent']==exponent and raw['right']==right and
            raw['right_bit_length']==right.bit_length() and raw['strict'],
            'Compressed power certificate fields differ')
    require(exponent >= right.bit_length(), 'Power exponent does not prove strict comparison')
    # Exactly 2^exponent >= 2^bit_length(right) > right; no exponential allocation.
    return dict(exponent=exponent,right=right,right_bit_length=right.bit_length(),strict=True)


def complex_counts(raw):
    h,R=int(raw['h']),int(raw['R'])
    require(h>=8 and h%2==0 and R>0,'Unsupported complex finite input')
    v,m=comb(h,3),h**3
    N=v**3;W=2*N+2*v*v*(R+h+1);L=3*v*v*h*(h+1);D=2*N-2*L;s=W*m-D
    result=dict(h=h,R=R,v=v,m=m,N=N,W=W,L=L,D=D,s=s,eta=Q(D,W*m))
    require(all(Q(raw[k])==v for k,v in result.items()),'Independent complex counts differ')
    require(0<D and 2<=s<m**5,'Complex rank deficit/count scope fails')
    require(3*v*v*(4*R+4)<6*W,'Accepted grouped scalar gate count fails')
    return result


def audit_row(row, old_tight):
    n=finite_counts(row['bit_counts']);nc=complex_counts(row['complex_counts'])
    p={k:Q(v) for k,v in row['parameters'].items()}
    a,b,tau,sigma,c,beta,eps,lam,lp,r,delta,kappa=(p[k] for k in
        ('a_bit','a_complex','tau','sigma','c','beta','epsilon','lambda_',
         'lambda_prime','alpha_squared_power','delta','kappa'))
    log_records={}
    primitive_gaps={}
    for name,counts,chosen in (('bit',n,a),('complex',nc,b)):
        lower,upper=independent_saving(counts['eta'],counts['m'])
        enc=row[name+'_saving_enclosure']
        require(Q(enc['saving_lower'])<lower<upper<Q(enc['saving_upper']),
                'Longer independent logarithm not inside saved enclosure')
        require(0<chosen<lower and chosen==Q(enc['chosen_saving']),
                'Primitive chosen saving exceeds independent bound')
        primitive_gaps[name+'_primitive']=(Q(enc['negative_log_deficit_lower'])-
                                           chosen*Q(enc['log_m_upper']))
        require(primitive_gaps[name+'_primitive']==Q(enc['strict_primitive_gap'])>0,
                'Saved logarithmic primitive strict slack differs')
        log_records[name]=dict(lower=str(lower),upper=str(upper),chosen_strict=True,
                                deficit_log_terms=20,radix_log_terms=48)
    require(tau==1-a and sigma==1-b and 0<a<b/2<Q(1,64),'Primitive order/half leaf branch invalid')
    require(beta==Q(1,2),'Semantic row must retain its half stopping threshold')
    h=Q(1,2**(20 if row['mode']=='conservative' else 64))
    require(row['mode'] in ('conservative','tight'),'Unknown fixed parameter mode')
    q=1-lp
    require(q==a*(1-2*h) and lam==(tau+lp)/2,'Strict layer/intermediate exponent differs')
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
    require(12*nc['W']**3+4*nc['s']+4*nc['W']+4<E and C0>2*B+18,
            'Exact scalar charge or complete linear guard constant invalid')
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
    slacks=dict(**primitive_gaps,primitive_order=b-a,half_leaf_saving=b/2-q,
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
               strict_recurrence_intermediate_gap=lp-lam)
    require(all(v>0 for v in extra.values()),'Additional router/Gaussian interface range failed')

    ka,km,kb=ceil_q(1/r),ceil_q(1/(eps*c)),ceil_q(1/(1-eps))
    cuts=dict(gamma=ceil_q(7/(1-eps-r)),logarithmic_alpha=16*ka*ka+1,
        full_guard=ceil_q(Q((2*C0).bit_length())/(1-eps)),
        phase_cell=ceil_q(9/(eps-(1-r)/2)),compact_controls=64*km*km+1,
        K_geometry=ceil_q(3/geometry),microbox_period=128*kb*kb+1,routing_reservoirs=14)
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
    # Scope ceiling follows the reviewed cost/geometry interfaces. Its
    # lower/upper enclosure is recomputed with the longer independent log.
    al,au=map(Q,(log_records['bit']['lower'],log_records['bit']['upper']))
    factor=1 if prefix=='balanced' else 2
    ceiling_low,ceiling_high=al/(1+factor*al),au/(1+factor*au)
    saved_upper=Q(row['bit_saving_enclosure']['saving_upper'])
    require(Q(row['scoped_hypothesis_upper'])==saved_upper/(1+factor*saved_upper),
            'Saved scoped upper branch differs')
    require(kappa<ceiling_low<ceiling_high<Q(row['scoped_hypothesis_upper']),
            'Independent scoped ceiling ordering or strict attainment fails')
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
        independent_scoped_ceiling_interval=[str(ceiling_low),str(ceiling_high)],
        ratio_to_83_over_10_to_12=str(kappa/Q(83,10**12)),
        old_unproved_estimates_reject_this_witness=True,
        enormous_power_allocation_performed=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('certificate','generic-compact','reference','bit-review','complex-review',
                 'complex-candidate','calibration','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();require(not args.output.exists(),'Use a fresh output path')
    start=time.monotonic()
    data=json.loads(args.certificate.read_text());old=json.loads(args.generic_compact.read_text())
    require(subprocess.run(['git','-C',str(args.reference),'rev-parse','HEAD'],capture_output=True,
                          text=True,check=True).stdout.strip()=='6e564879f51ae16f23d392e9e196c605f36d90df',
            'Compact reference revision differs')
    require(any(x['sha256']==sha256(args.generic_compact.read_bytes()).hexdigest()
                for x in data['input_files'].values()),'Semantic input generic identity differs')
    require(data['promoted_bit_audit']==old['promoted_bit_audit'] and
            data['promoted_complex_audit']==old['promoted_complex_audit'],
            'Promoted finite metadata changed in semantic composition')
    promotion=promoted_metadata(old,args)
    full=json.loads(args.bit_review.read_text())
    require(data['promoted_bit_audit']['dirty_invocation_basis_checks']==sum(
        r['input_basis_vectors'] for s in full['small_controls']
        for r in s['complete_invocation_dirty_basis_including_centers']),
        'Dirty invocation basis metadata differs')
    for name,digest in data['source_sha256'].items():
        require(sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==digest,
                'Executed producer dependency version changed '+name)
    old_rows=[audit_old_row(r) for r in old['witnesses']]
    old_tight=next(r for r in old['witnesses'] if r['mode']=='tight')
    rows=[audit_row(row,old_tight) for row in data['witnesses']]
    require({(r['mode'],r['prefix']) for r in rows}==set(product(
        ('conservative','tight'),('original','balanced'))),'Complete four-row matrix missing')
    result=dict(status='PASS independent complete semantic/bulk exact assembly audit',
        generated_at=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        reviewer_dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ('review_asymmetric_motif.py','review_parameter_audit.py',
                         'review_compact_generic.py','review_packed_unrolling.py')},
        input_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in
            (args.certificate,args.generic_compact,args.bit_review,args.complex_review,args.complex_candidate,args.calibration)},
        promotion=promotion,old_generic_independent_regressions=old_rows,rows=rows,
        elapsed_seconds=time.monotonic()-start,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        limitations=['Conditional reviewed analytic/tape/primitive interfaces; not a formal exact multiplication machine',
            'Numeric log2(b) cutoff plus separately retained eventual prime/setup/absorption thresholds',
            'No finite circuit, frame or bank control is rerun by this thin arithmetic audit'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for row in rows:print('PASS',row['mode'],row['prefix'],row['kappa'],
                         row['complete_declared_strict_conditions'],'strict conditions',flush=True)


if __name__=='__main__':
    main()
