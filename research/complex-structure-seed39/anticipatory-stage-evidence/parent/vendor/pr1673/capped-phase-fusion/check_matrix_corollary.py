#!/usr/bin/env python3
"""Exact corollary ledger, additionally assuming the supplied 9/4 theorem."""
from fractions import Fraction as Q
from decimal import Decimal,localcontext
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent

def decimal(x):
    with localcontext() as ctx:
        ctx.prec=65
        return str(Decimal(x.numerator)/Decimal(x.denominator))

def calculate(q=None,zeta=None,union_slack=None,old_vd=False,
              full_cell_gauge=False,add_full_key_sort=False):
    bit=Q('0.001733427039589844234749')
    complex_=Q('0.001675462676808103522925')
    q=complex_-Q(1,10**10) if q is None else q
    a=(q+complex_)/2
    r=Q(1,10**6)
    zeta=Q(1,10**8) if zeta is None else zeta
    union_slack=Q(1,10**5) if union_slack is None else union_slack
    tau_matrix=Q(19,8)
    c=(3-tau_matrix)/2
    stop=Q(1,10**9)
    cap=(Q(3,2)+q-(1+q)*(r+zeta)+union_slack)/(2+q)
    eps=(1+q*(1-cap-r-zeta))/(1+q)
    beta=1-cap-r-zeta
    kappa=Q('0.001673360105405778')
    selected=Q('0.001672660197076918')
    first=Q('0.001672922349588871')
    tau_bit,sigma=1-a,1-complex_
    internal=tau_bit+(1-stop)*max(sigma-tau_bit,Q(0))
    leaf=sigma+stop*(1-sigma)
    lam=1-(q+a)/2
    key=beta+1-eps
    margins=dict(
        main_transform=eps*q,
        global_coordinate_router=a,
        fused_gaussian=1-eps+q*beta,
        group_bit_router=1-eps+a*beta,
        group_scans=1-eps+beta,
        boundary_algebraic_matrix=c+cap-eps,
        sparse_union_movement=1-eps-beta-Q(1,2)+cap,
        polynomial_products=eps,
        microbox_face_corrections=1-(eps+beta+3-8+2),
    )
    if old_vd:margins['unreplaced_per_axis_scan']=1-eps
    if add_full_key_sort:
        margins['unnecessary_union_full_key_sort']=margins['sparse_union_movement']-key
    slacks=dict(
        actual_bit_above_effective=bit-a,
        complex_above_effective=complex_-a,
        complex_below_one_over_32=Q(1,32)-complex_,
        q_positive=q,
        complex_endpoint=complex_-q,
        q_below_effective_bit=a-q,
        stop_positive=stop,
        stop_below_one=1-stop,
        leaf_saving_above_effective_bit=(1-stop)*complex_-a,
        q_below_internal=1-internal-q,
        q_below_leaf=1-leaf-q,
        lambda_above_tau=lam-tau_bit,
        lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal,
        lambda_prime_above_lambda=1-q-lam,
        lambda_prime_above_leaf=1-q-leaf,
        epsilon_positive=eps,
        epsilon_below_one=1-eps,
        capped_block_above_band=cap-Q(1,2),
        capped_block_below_cell=eps-cap,
        group_positive=beta,
        group_below_dimension=eps-beta,
        support_router_span=1-beta,
        group_gauge_power_slack=1-cap-r-beta,
        actual_logarithmic_group_guard=1-cap-beta,
        global_gamma_power_slack=1-eps-r,
        actual_logarithmic_gamma_guard=1-eps,
        alpha_logarithm_absorption=r,
        group_key_fits_record=1-key,
        membership_arithmetic_fits_record=1-beta-2*(1-eps),
        sparse_union_fraction_decays=cap-beta-Q(1,2),
        microbox_halo_volume=8-3-beta,
        union_positive_slack=union_slack,
        matrix_exponent_above_source_bound=tau_matrix-Q(9,4),
        matrix_exponent_below_five_halves=Q(5,2)-tau_matrix,
        short_record_fallback=eps-a,
        improvement_over_selected=kappa-selected,
        improvement_over_first_reviewed_transfer=kappa-first,
    )
    if full_cell_gauge:
        slacks['unrecentered_group_gauge']=1-eps-r-beta
    slacks.update({name+'_above_kappa':value-kappa for name,value in margins.items()})
    assert margins['main_transform']==margins['fused_gaussian']
    assert margins['sparse_union_movement']==margins['main_transform']+union_slack
    return dict(parameters=dict(a_bit=bit,a_eff=a,complex_saving=complex_,q=q,
        r_spare=r,zeta=zeta,sigma_union=union_slack,stop=stop,
        epsilon=eps,capped_block_power=cap,beta_group=beta,
        matrix_exponent=tau_matrix,matrix_source_bound=Q(9,4),
        c_boundary=c,kappa=kappa,selected=selected,first_reviewed_transfer=first,
        lambda_=lam,lambda_prime=1-q,tau=tau_bit,sigma=sigma,
        microbox_power=Q(8),halo_power=Q(3)),margins=margins,slacks=slacks)

def encode(o):
    if isinstance(o,Q):return dict(rational=str(o),decimal=decimal(o))
    if isinstance(o,dict):return {k:encode(v) for k,v in o.items()}
    return o

if __name__=='__main__':
    row=calculate()
    assert all(value>0 for value in row['slacks'].values())
    assert min(row['margins'].values())==row['margins']['main_transform']
    controls={}
    tests=[('endpoint_equality',dict(q=Q('0.001675462676808103522925'))),
           ('zero_group_guard',dict(zeta=Q(0))),
           ('zero_union_slack',dict(union_slack=Q(0))),
           ('old_per_axis_scan',dict(old_vd=True)),
           ('unrecentered_full_cell_gauge',dict(full_cell_gauge=True)),
           ('full_key_sort_on_union',dict(add_full_key_sort=True))]
    for name,kwargs in tests:
        bad=calculate(**kwargs)
        failed={k:v for k,v in bad['slacks'].items() if v<=0}
        assert failed,name
        controls[name]=failed
    output=dict(status='PASS_CONDITIONAL_MATRIX_PHASE_FUSION_REVIEW',
        scope='Additional matrix-conditioned corollary. Assumes supplied omega_C<=9/4 theorem and the effective algebraic stability transfer, as well as all first-transfer assumptions.',
        review=dict(integrated='Root read the matrix corollary and independent layout signoff, reproduced the exact parameters and ledger, and replayed matrix source construction controls.',
                    matrix_source='PROOF-AND-COVERAGE.md',
                    effective_stability='ALGEBRAIC-STABILITY-INDEPENDENT.md',
                    independent_layout='MATRIX-LAYOUT-SIGNOFF.md'),
        omitted_row=dict(name='optional full-coordinate-key union surcharge',
            reason='The actual U_i complete-rectangle extraction, one-field transpose, and ordered merge do not sort union records. Sparse microhalo keys remain paid in their separate cost.'),
        **row,controls=controls)
    (ROOT/'MATRIX-COROLLARY-ARITHMETIC.json').write_text(json.dumps(encode(output),indent=2)+'\n')
    print(output['status'])
    for name in ['epsilon','capped_block_power','beta_group','kappa']:
        print(name,decimal(row['parameters'][name]))
    print('minimum margin',decimal(min(row['margins'].values())))
    print('gain over selected',decimal(row['slacks']['improvement_over_selected']))
    print('gain over first transfer',decimal(row['slacks']['improvement_over_first_reviewed_transfer']))
    print('positive strict slacks',len(row['slacks']))
    print('controls',', '.join(controls))
