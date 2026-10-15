#!/usr/bin/env python3
"""Exact arithmetic only. This does not automatically certify proof obligations."""
from fractions import Fraction as Q
from decimal import Decimal, localcontext
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

def dec(x):
    with localcontext() as ctx:
        ctx.prec = 65
        return str(Decimal(x.numerator) / Decimal(x.denominator))

def compute(q=None, zeta=None, old_vd=False):
    b = Q('0.001675462676808103522925')
    a_bit = Q('0.001733427039589844234749')
    q = b-Q(1,10**10) if q is None else q
    r = Q(1,10**6)
    zeta = Q(1,10**8) if zeta is None else zeta
    a_eff = (q+b)/2
    t_stop = Q(1,10**9)
    tau, sigma = 1-a_eff, 1-b
    lam_prime = 1-q
    lam = 1-(q+a_eff)/2
    internal = tau + (1-t_stop)*max(sigma-tau,Q(0))
    leaf = sigma+t_stop*(1-sigma)
    eps = (1+q-q*(r+zeta))/(1+2*q)
    beta = 1-eps-r-zeta
    kappa = Q('0.001672664764353193')
    selected = Q('0.001672660197076918')
    omega_upper = Q(45,16)
    # alpha^2=O(log p), so w=O(sqrt(p) polylog(p)).
    wide = Q(1,2)
    key = beta+1-eps
    margins = dict(
        main_transform=eps*q,
        global_coordinate_router=a_eff,
        fused_gaussian=1-eps+q*beta,
        group_bit_router=1-eps+a_eff*beta,
        group_scans=1-eps+beta,
        boundary_batched_algebra=1-(omega_upper-1)*wide,
        sparse_union_movement=1-beta-wide,
        sparse_union_full_key=1-beta-wide-key,
        polynomial_products=eps,
        # gA/L copies, g sequential passes, each p^2 conservatively.
        microbox_face_corrections=1-(eps+beta+3-8+2),
    )
    if old_vd:
        margins['unreplaced_per_axis_scan'] = 1-eps
    slacks = dict(
        actual_bit_above_effective=a_bit-a_eff,
        complex_above_effective=b-a_eff,
        complex_below_one_over_32=Q(1,32)-b,
        q_positive=q,
        complex_endpoint=b-q,
        q_below_effective_bit=a_eff-q,
        stop_positive=t_stop,
        stop_below_one=1-t_stop,
        leaf_saving_above_effective_bit=(1-t_stop)*b-a_eff,
        q_below_internal=1-internal-q,
        q_below_leaf=1-leaf-q,
        lambda_above_tau=lam-tau,
        lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal,
        lambda_prime_above_lambda=lam_prime-lam,
        lambda_prime_above_leaf=lam_prime-leaf,
        lambda_prime_below_one=q,
        epsilon_positive=eps,
        epsilon_below_one=1-eps,
        group_positive=beta,
        group_below_dimension=eps-beta,
        group_controls_below_one_axis_width=1-eps-beta,
        support_router_span=1-beta,
        group_guard=1-eps-r-beta,
        alpha_logarithm_absorption=r,
        local_gauge_sublinear=1-eps-r,
        core_above_band=eps-wide,
        record_suffix=1-eps,
        prime_interval_packing=1-eps,
        semantic_dimension_guard=1-eps,
        microbox_larger_than_halo=Q(8-3)-beta,
        short_record_fallback=eps-a_eff,
        improvement=kappa-selected,
    )
    slacks.update({name+'_above_kappa':val-kappa for name,val in margins.items()})
    assert eps*q == 1-eps+q*beta
    return dict(parameters=dict(a_bit=a_bit,a_eff=a_eff,b=b,q=q,r=r,zeta=zeta,
        t_stop=t_stop,tau=tau,sigma=sigma,lambda_=lam,lambda_prime=lam_prime,
        epsilon=eps,beta_group=beta,kappa=kappa,selected=selected,
        omega_upper=omega_upper,microbox_power=Q(8),halo_power=Q(3)),
        margins=margins,slacks=slacks)

def convert(o):
    if isinstance(o,Q): return {'rational':str(o),'decimal':dec(o)}
    if isinstance(o,dict): return {k:convert(v) for k,v in o.items()}
    return o

if __name__ == '__main__':
    row=compute()
    assert 7**16 < 2**45
    assert all(x>0 for x in row['slacks'].values())
    assert min(row['margins'].values())==row['margins']['main_transform']
    controls={}
    for name,kw in [('complex_endpoint_equality',{'q':Q('0.001675462676808103522925')}),
                    ('zero_group_guard',{'zeta':Q(0)}),
                    ('old_per_axis_scan',{'old_vd':True})]:
        bad=compute(**kw)
        failed={n:v for n,v in bad['slacks'].items() if v<=0}
        assert failed, name
        controls[name]={'rejected_slacks':failed}
    result=dict(status='PASS_EXACT_ARITHMETIC_PENDING_FULL_PROOF_REVIEW',
        scope='Exact outer arithmetic; no automatic theorem promotion.',
        **row, controls=controls,
        theorem_obligations=[
            'retained finite suppliers and exact common-frame/mutable-source compiler',
            'deferred reservations and paid global synthetic layout',
            'shallow Toeplitz plus SPD extension and tensor compiler',
            'small-a forward conditioning and exact target-grid square completion',
            'grouped sparse-union route and batched boundary arithmetic',
            'dyadic core with sparse microbox-face repair and monotone q-image scans',
            'scalar product-diagonal scan and retained all-size semantic/prime/error transfer',
        ])
    path=ROOT/'OUTER-ARITHMETIC.json'
    path.write_text(json.dumps(convert(result),indent=2)+'\n')
    print(result['status'])
    print('kappa',dec(row['parameters']['kappa']))
    print('minimum margin',dec(min(row['margins'].values())))
    print('gain',dec(row['slacks']['improvement']))
    print('positive exact slacks',len(row['slacks']))
    print('negative controls',', '.join(controls))
