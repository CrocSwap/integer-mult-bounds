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
