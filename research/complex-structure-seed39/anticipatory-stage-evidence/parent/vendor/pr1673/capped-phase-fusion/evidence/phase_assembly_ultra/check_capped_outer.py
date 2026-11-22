#!/usr/bin/env python3
"""Independent rational ledger for capped phase interiors; proof review separate."""
from fractions import Fraction as Q
from decimal import Decimal, localcontext
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent

def decimal(x):
    with localcontext() as ctx:
        ctx.prec=65
        return str(Decimal(x.numerator)/Decimal(x.denominator))

def calculate(q=None,zeta=None,sigma_boundary=None,old_vd=False,full_cell_gauge=False):
    bit=Q('0.001733427039589844234749')
    complex_=Q('0.001675462676808103522925')
    q=complex_-Q(1,10**10) if q is None else q
    a=(q+complex_)/2
    r=Q(1,10**6)
    zeta=Q(1,10**8) if zeta is None else zeta
    sigma_boundary=Q(1,10**5) if sigma_boundary is None else sigma_boundary
    c=Q(3,32)
    stop=Q(1,10**9)
    eps=(1+q+q*(c-sigma_boundary-r-zeta))/(1+q)**2
    b=eps*(1+q)-c+sigma_boundary
    beta=1-b-r-zeta
    kappa=Q('0.001672922349588871')
    selected=Q('0.001672660197076918')
    tau,s=1-a,1-complex_
    internal=tau+(1-stop)*max(s-tau,Q(0))
    leaf=s+stop*(1-s)
    lam=1-(q+a)/2
    key=beta+1-eps
    margins=dict(
        main_transform=eps*q,
        global_coordinate_router=a,
        fused_gaussian=1-eps+q*beta,
        group_bit_router=1-eps+a*beta,
        group_scans=1-eps+beta,
        boundary_batched_algebra=c+b-eps,
        sparse_union_movement=1-eps-beta-Q(1,2)+b,
        sparse_union_full_key=1-eps-beta-Q(1,2)+b-key,
        polynomial_products=eps,
        microbox_face_corrections=1-(eps+beta+3-8+2),
    )
    if old_vd: margins['unreplaced_per_axis_scan']=1-eps
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
        lambda_above_tau=lam-tau,
        lambda_above_sigma=lam-s,
        lambda_above_internal=lam-internal,
        lambda_prime_above_lambda=1-q-lam,
        lambda_prime_above_leaf=1-q-leaf,
        epsilon_positive=eps,
        epsilon_below_one=1-eps,
        capped_block_above_band=b-Q(1,2),
        capped_block_below_cell=eps-b,
        group_positive=beta,
        group_below_dimension=eps-beta,
        support_router_span=1-beta,
        group_gauge_power_slack=1-b-r-beta,
        actual_logarithmic_group_guard=1-b-beta,
        global_gamma_power_slack=1-eps-r,
        actual_logarithmic_gamma_guard=1-eps,
        alpha_logarithm_absorption=r,
        group_key_fits_record=1-key,
        membership_arithmetic_fits_record=1-beta-2*(1-eps),
        microbox_halo_volume=8-3-beta,
        boundary_positive_slack=sigma_boundary,
        short_record_fallback=eps-a,
        improvement=kappa-selected,
    )
    if full_cell_gauge:
        slacks['unrecentered_group_gauge']=1-eps-r-beta
    slacks.update({name+'_above_kappa':value-kappa for name,value in margins.items()})
    assert margins['main_transform']==margins['fused_gaussian']
    assert margins['boundary_batched_algebra']==margins['main_transform']+sigma_boundary
    return dict(parameters=dict(a_bit=bit,a_eff=a,complex_saving=complex_,q=q,
        r_spare=r,zeta=zeta,sigma_boundary=sigma_boundary,stop=stop,
        epsilon=eps,capped_block_power=b,beta_group=beta,
        omega_upper=Q(45,16),c_boundary=c,kappa=kappa,selected=selected,
        lambda_=lam,lambda_prime=1-q,tau=tau,sigma=s,
        microbox_power=Q(8),halo_power=Q(3)),margins=margins,slacks=slacks)

def encode(o):
    if isinstance(o,Q):return dict(rational=str(o),decimal=decimal(o))
    if isinstance(o,dict):return {k:encode(v) for k,v in o.items()}
    return o

if __name__=='__main__':
    row=calculate()
    assert 7**16<2**45
    assert all(value>0 for value in row['slacks'].values())
    assert min(row['margins'].values())==row['margins']['main_transform']
    controls={}
    tests=[('endpoint_equality',dict(q=Q('0.001675462676808103522925'))),
           ('zero_group_guard',dict(zeta=Q(0))),
           ('zero_boundary_slack',dict(sigma_boundary=Q(0))),
           ('old_per_axis_scan',dict(old_vd=True)),
           ('unrecentered_full_cell_gauge',dict(full_cell_gauge=True))]
    for name,kwargs in tests:
        bad=calculate(**kwargs)
        failed={k:v for k,v in bad['slacks'].items() if v<=0}
        assert failed,name
        controls[name]=failed
    output=dict(status='PASS_CONDITIONAL_PHASE_FUSION_REVIEW',
        scope='Local conditional transfer and exact arithmetic; inherited supplier and all-size interfaces remain assumptions. No upstream selected certificate is changed.',
        review=dict(integrated_review='Root reviewed the complete standalone note, integrated proof chain, exact ledger, and independent cap/supplier/layout audits.',
                    independent_cap_gauge='CAPPED-GAUGE-AUDIT.md',
                    independent_cap_layout='CAPPED-SIGNOFF.md',
                    supplier_support='SUPPLIER-SUPPORT-AUDIT.md'),
        **row,controls=controls)
    (ROOT/'CAPPED-OUTER-ARITHMETIC.json').write_text(json.dumps(encode(output),indent=2)+'\n')
    print(output['status'])
    for name in ['epsilon','capped_block_power','beta_group','kappa']:
        print(name,decimal(row['parameters'][name]))
    print('minimum margin',decimal(min(row['margins'].values())))
    print('gain over selected',decimal(row['slacks']['improvement']))
    print('positive strict slacks',len(row['slacks']))
    print('controls',', '.join(controls))
