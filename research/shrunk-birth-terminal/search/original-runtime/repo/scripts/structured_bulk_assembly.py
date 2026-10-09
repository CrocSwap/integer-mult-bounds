#!/usr/bin/env python3
"""Copyright 2026 icekylinx. Apache-2.0.
Substantial OpenAI GPT-6 Astra and Codex assistance.

Exact finite bridge and assembly for the round-three networks.

Adapted parameter calculation and semantic/product-row proof from PR23,
Zhihao Chen (jacklightChen), which attributes routing, phase-cell inverse
and bulk resampling to the RaD project (hipotures), commit
45d9b60355872041f9275f77c057514def0d45bc. This file does not regenerate,
audit, or substitute for the finite-network or analytic source proofs.
"""
from fractions import Fraction as Q

def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [js(v) for v in x]
    return x

def halving(m,r):
    assert 0<r<m
    n=1
    while m**n<=2*r**n:n+=1
    return n

def finite_bridge(bit_m,bit_W,bit_maxchild,complex_data):
    c=complex_data; m,W,s,N=c['m'],c['W'],c['total_rank'],c['N']
    G=0; scalar_terms=[]
    for row in c['scalar_circuits']:
        h,v,additions,outputs=row['h'],row['v'],row['c'],row['q']
        # Four complete mixer sweeps, two source copies, two side
        # injections (four side sums per target), four fully expanded
        # center gather/scatter maps, and an h by h center decoder.
        # Inputs are counted as mixer groups even when they do no work.
        local=4*(additions+v)+10*v+4*h*v+4*h*h+8*h+8
        copies=N//v
        assert copies*v==N
        G+=copies*local
        scalar_terms.append(dict(h=h,v=v,c=additions,q=outputs,
            invocations=copies,local_group_upper=local))
    # G is an actual gate-count upper bound, never replaced by W.
    E=64*(W+m+G+1)**3
    charge=2*G*W*W+8*s+4*W+4+32*m
    assert charge<E
    B=s+E; C0=32*m*B*B; r=max(map(int,c['child_multiplicities']))
    assert 2*B*(m-r)>=s+E and 2*B+18<C0
    db,dc=halving(bit_m,bit_maxchild),halving(m,r)
    wb,wc=bit_W.bit_length(),W.bit_length()
    coeff=wb*db+wc*dc
    degree=1000*((coeff*51)//25000+1)
    assert Q(degree)>Q(coeff*51,25)
    return dict(bit=dict(m=bit_m,W=bit_W,maxchild=bit_maxchild,
                    halving_degree=db,wire_bits=wb),
        complex=dict(m=m,W=W,s=s,maxchild=r,halving_degree=dc,
                    wire_bits=wc,scalar_terms=scalar_terms,scalar_group_upper=G),
        semantic=dict(E=E,literal_charge=charge,strict_literal_gap=E-charge,
                    B=B,C0=C0,C1=1,induction_gap=2*B*(m-r)-s-E),
        rows=dict(coefficient=coeff,degree=degree,suffix_slope=4*degree,
                    degree_gap=Q(degree)-Q(coeff*51,25),
                    contract='W_complex^D_complex * W_bit^D_bit; preceding row prefix, single complete-row padding, nested bit stock restored'))

def assembly(bit_saving,complex_saving,bridge,kappa,eta=Q(1,10**8),beta=Q(1,4)):
    a,b=bit_saving,complex_saving
    tau,sigma=1-a,1-b
    q=a*(1-2*eta); lp=1-q; lam=(tau+lp)/2
    c=q*(1+eta); eps=(1-eta)/(1+c+q)
    minimum=eps*q; r=(minimum+1-eps)/2; delta=eta/8
    internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
    margins=dict(original_prefix=1-eps*(1+c),coordinate_movement=a,
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
    assert all(v>0 for v in slacks.values()),{k:str(v) for k,v in slacks.items() if v<=0}
    assert min(margins.values())==minimum
    assert margins['original_prefix']-minimum==eta
    return dict(parameters=dict(a_bit=a,a_complex=b,tau=tau,sigma=sigma,
            eta=eta,beta=beta,q=q,c=c,epsilon=eps,lambda_=lam,
            lambda_prime=lp,alpha_squared_power=r,delta=delta,
            C0=bridge['semantic']['C0'],C1=1,kappa=kappa),
        strict_constraints=slacks,margins=margins,minimum_margin=minimum,
        absorption_gap=minimum-kappa,
        recurrence=dict(internal=internal,leaf=leaf,reservations=1-c))
