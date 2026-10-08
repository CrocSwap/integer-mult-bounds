"""Dimension-parametric PR23 arithmetic, adapted from Zhihao Chen (Apache-2.0).

Assembly also retains PR25's explicit 47-constraint count. This module
checks arithmetic conditional on the cited semantic/tape interface proofs.
No producer generation or imports from another checkout are performed.
"""
from fractions import Fraction as Q

def ceil(x):return -(-x.numerator//x.denominator)

def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [js(v) for v in x]
    return x

def halving(m,r):
    k=1
    while m**k<=2*r**k:k+=1
    assert m**(k-1)<=2*r**(k-1)
    return k

def cutoffs(f,a):
    p=a['parameters'];e,c,r,beta=p['epsilon'],p['c'],p['alpha_squared_power'],p['beta']
    ka,km,kb=ceil(1/r),ceil(1/(e*c)),ceil(1/(1-e));C0=f['semantic']['C0']
    minimum=max(f['bit']['m'],f['complex']['m']);ks=ceil(1/(e*beta))
    cuts=dict(gamma=ceil(7/(1-e-r)),logarithmic_alpha=16*ka*ka+1,
        full_guard=ceil(Q((2*C0).bit_length())/(1-e)),
        phase_cell=ceil(9/(e-(1-r)/2)),compact_controls=64*km*km+1,
        K_geometry=ceil(3/(1-e*(1+c))),microbox_period=128*kb*kb+1,
        reservoirs=14,stopped_leaf=ks*(4*minimum).bit_length())
    cuts['common']=max(cuts.values());L=cuts['common']
    def power(exponent,rhs):
        assert exponent>=rhs.bit_length()
        return dict(exponent=exponent,rhs=rhs,rhs_bit_length=rhs.bit_length(),strict=True)
    checks=dict(compact=power(L//km,32*L+192),period=power(L//kb,16*L+56),
        alpha=power(L//ka,8*L+64))
    checks['row_stock']=[power((L*2**j)//kb,f['rows']['suffix_slope']*(L*2**j+8)) for j in range(6)]
    checks['stopped_leaf']=[power((L*2**j)//ks,4*minimum) for j in range(6)]
    assert L>=max(2*ka,2*km,2*kb,25)
    assert L*(1-e)>=(2*C0).bit_length() and L*(1-e-r)>=7
    assert L*(e-(1-r)/2)>=9 and L*(1-e*(1+c))>=3
    return dict(cutoff_log2_input_bits=cuts,compressed_power_checks=checks,
        additional_eventual_conditions=['BHP prime threshold and 12 d^2 < x^(19/40)',
          'Fixed rational basis, shared eligible prime and native table setup',
          'Polynomial descriptor and catalogue domination; e<=C*p,p>=C',
          'Strict logarithmic absorption and inherited exact-recovery thresholds'],
        practical_runtime_claim=False)

def assembly(f,bit_saving,kappa,old_guard=False,old_exposures=False):
    # Parameterized transcription of Zhihao Chen's PR23 assembly. Only a changes.
    a,b=bit_saving,Q(18,10**6);h=Q(1,10**8);beta=Q(1,4)
    tau,sigma=1-a,1-b;q=a*(1-2*h);lp=1-q;lam=(tau+lp)/2
    c=q*(1+h);eps=(1-h)/(1+c+q);G=eps*q
    r=(G+1-eps)/2;delta=h/8
    C1=Q(19991,10000) if old_guard else Q(1)
    margins=dict(g1=1-eps*(1+c),g2=a,g3=G,g4=a,
        g5=min(1-eps-delta,r-delta),g6=1-eps-delta,g7=eps)
    if old_exposures:margins.update(g2=eps*c*a,g4=a*(1-eps))
    internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
    slacks=dict(a_positive=a,a_below_b=b-a,b_below_one_over32=Q(1,32)-b,
        beta_positive=beta,beta_below_one=1-beta,phase_leaf_above_bit=(1-beta)*b-a,
        q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,
        c_positive=c,c_below_one=1-c,q_below_reservations=c-q,
        lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf,compact_reservations=lp-(1-c),lambda_prime_below_one=q,
        epsilon_positive=eps,epsilon_below_one=1-eps,guard_width=1-eps*C1,
        K_geometry=1-eps*(1+c),K_dominates_log=eps*c,
        record_suffix=1-eps,phase_local=1-eps-delta,phase_boundary=r-delta,
        gamma_sublinear=1-eps-r,cell_above_band=eps-(1-r)/2,
        prime_interval_packing=1-eps,alpha_positive=r,alpha_below_one=1-r,
        alpha_below_one_fourth=Q(1,4)-r,delta_positive=delta,
        delta_below_one_eighth=Q(1,8)-delta,short_record_fallback=eps-a,
        small_field_exposure=1-eps-G,artificial_boundary=8-eps+r-delta-G,
        literal_scalar_guard=Q(f['semantic']['strict_literal_gap']),
        row_product_gap=f['rows']['degree_gap'])
    slacks.update({name+'_above_kappa':value-kappa for name,value in margins.items()})
    assert len(slacks)==47 and all(x>0 for x in slacks.values()),{k:str(v) for k,v in slacks.items() if v<=0}
    assert len(margins)==7 and min(margins.values())==G and margins['g1']-G==h
    assert kappa>Q(1,2**17)
    p=dict(a_bit=a,a_complex=b,tau=tau,sigma=sigma,beta=beta,q=q,c=c,
        epsilon=eps,lambda_=lam,lambda_prime=lp,alpha_squared_power=r,
        delta=delta,C0=f['semantic']['C0'],C1=C1,kappa=kappa)
    return dict(parameters=p,constraints=slacks,margins=margins,minimum_margin=G,
        absorption_gap=G-kappa,gap_above_2_minus17=kappa-Q(1,2**17),
        ratio_to_PR23=kappa/Q(1099,10**8),
        recurrence=dict(internal=internal,leaf=leaf,reservations=1-c))
