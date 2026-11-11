#!/usr/bin/env python3
"""Exact semantic assembly with the balanced prefix, for the paired-cube network.

Prepared by eumemic with Anthropic Claude assistance. Apache-2.0. The 47 strict constraints, the seven margins and
the finite bridge are unchanged from icekylinx's scripts/structured_bulk_assembly.py (PR144, adapted from Zhihao
Chen's PR23). The prefix is the RaD project's (hipotures) balanced positional transform, reviewed in
references/semantic-bulk/rad20/reports/review-balanced-transform.md: the prefix margin becomes 1-eps instead of
1-eps(1+c), and eps(1+c)<1 remains a strict geometric condition (K_geometry) whose gap need not exceed kappa.
The parameters c=q+eta/4 and eps=(1-eta)/(1+q) are those of the reviewed balanced assembly in
research/copied-fixed/balanced_assembly.py, with its backoff h equal to eta. Nothing else differs from
structured_bulk_assembly.assembly.
"""
from fractions import Fraction as Q


def assembly(bit_saving,complex_saving,bridge,kappa,eta=Q(1,10**8),beta=Q(1,4)):
    a,b=bit_saving,complex_saving
    tau,sigma=1-a,1-b
    q=a*(1-2*eta); lp=1-q; lam=(tau+lp)/2
    c=q+eta/4; eps=(1-eta)/(1+q)
    minimum=eps*q; r=(minimum+1-eps)/2; delta=eta/8
    internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
    margins=dict(balanced_prefix=1-eps,coordinate_movement=a,
        compact_phase_layer=minimum,bulk_exposure=a,
        Gaussian_arithmetic=min(1-eps-delta,r-delta),
        scalar_work=1-eps-delta,dimension=eps)
    slacks=dict(bit_positive=a,complex_above_bit=b-a,
        complex_below_one_over32=Q(1,32)-b,beta_positive=beta,
        beta_below_one=1-beta,leaf_saving_above_bit=(1-beta)*b-a,
        q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,
        c_positive=c,c_below_one=1-c,q_below_reservations=c-q,
        lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf,compact_reservations=lp-(1-c),
        lambda_prime_below_one=q,epsilon_positive=eps,epsilon_below_one=1-eps,
        guard_width=1-eps,K_geometry=1-eps*(1+c),K_dominates_log=eps*c,
        record_suffix=1-eps,phase_local=1-eps-delta,phase_boundary=r-delta,
        gamma_sublinear=1-eps-r,cell_above_band=eps-(1-r)/2,
        prime_interval_packing=1-eps,alpha_positive=r,alpha_below_one=1-r,
        alpha_below_one_fourth=Q(1,4)-r,delta_positive=delta,
        delta_below_one_eighth=Q(1,8)-delta,short_record_fallback=eps-a,
        small_field_exposure=1-eps-minimum,
        artificial_boundary=8-eps+r-delta-minimum,
        literal_scalar_guard=Q(bridge['semantic']['strict_literal_gap']),
        row_product_gap=bridge['rows']['degree_gap'])
    slacks.update({name+'_above_kappa':val-kappa for name,val in margins.items()})
    assert len(slacks)==47 and len(margins)==7
    assert all(v>0 for v in slacks.values()),{k:str(v) for k,v in slacks.items() if v<=0}
    assert min(margins.values())==minimum
    assert margins['balanced_prefix']-minimum==eta and 1-eps-r==eta/2
    assert 1-eps*(1+c)==eta-eps*eta/4
    return dict(parameters=dict(a_bit=a,a_complex=b,tau=tau,sigma=sigma,
            eta=eta,beta=beta,q=q,c=c,epsilon=eps,lambda_=lam,
            lambda_prime=lp,alpha_squared_power=r,delta=delta,
            C0=bridge['semantic']['C0'],C1=1,kappa=kappa),
        strict_constraints=slacks,margins=margins,minimum_margin=minimum,
        absorption_gap=minimum-kappa,
        recurrence=dict(internal=internal,leaf=leaf,reservations=1-c))
