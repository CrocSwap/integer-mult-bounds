"""Actual cubic-width executions with each common-operator premise checked."""
from fractions import Fraction as F
from math import gcd
import json
from common import P,need,predecessor as source,original as st
from early import solve as truncated
from cubic import plan


def main():
    checker=source.pinned_vendor()
    fixtures=json.loads((P/'vendor/pr846/vendor/FACTORS.json').read_text())
    rows=[]
    for fixture in fixtures:
        r=fixture['radix']
        if r not in (3,4,5,7):
            continue
        phi=sum(gcd(r,j)==1 for j in range(1,r))
        budget=plan(r,phi,128,4)
        prepared=json.loads(json.dumps(fixture))
        prepared['factor_bits']=min(fixture['factor_bits'],budget['factor_bits'])
        prepared['working_bits']=budget['W']
        prepared['roots']=[[str(v) for v in st.rounded(tuple(F(z) for z in pair),prepared['factor_bits'])]
                           for pair in fixture['roots']]
        state=checker.certify(prepared)
        need(prepared['factor_bits']<=budget['factor_bits'],'bounded input root preparation')
        beta=F(1,1<<budget['g'])
        H=F(state['certificate']['inverse_norm_bound'])
        mass=sum(abs(v[0])+abs(v[1]) for v in state['q'])
        partial=max(F(1),(1<<(r-1))*mass*H)
        need(state['beta']>=beta and mass<=1<<r and H<=1<<(budget['a0']+1),
             'prepared polynomial and margin hypotheses')
        need(partial<=1<<budget['h'],'certified complementary-factor norm')
        bits=budget['W']
        u=F(1,1<<bits)
        bound=budget['execution_bound']
        for tau_name,tau in [('1',st.ONE),('3/5+4i/5',(F(3,5),F(4,5)))]:
            need(st.norm2(tau)==1,'unit phase')
            for length in [1,2,5]:
                for stride in range(length):
                    x=[(a+u,b-u) for a,b in source.inputs(length,stride+length)]
                    snapshot=tuple(x)
                    need(all((v/u).denominator==1 and (v/u).numerator%2 for z in x for v in z),
                         'arbitrary lowest working bits')
                    original_tape=st.Tape()
                    full=source.apply_kernel(checker,state,x,stride,tau,bits,original_tape)
                    saved=st.solve
                    try:
                        st.solve=truncated
                        early_tape=st.Tape()
                        early=source.apply_kernel(checker,state,x,stride,tau,bits,early_tape)
                    finally:
                        st.solve=saved
                    need(full==early and tuple(x)==snapshot,'exact equivalence and unchanged source')
                    D=max(abs(z[0])+abs(z[1]) for z in x)
                    need(D<=16,'declared source bound')
                    perturbation=F(state['certificate']['factorization_inverse_error_bound'])*D
                    need(perturbation<=F(1,1<<130) and bound+perturbation<=F(1,1<<128),
                         'root preparation and cubic execution meet target')
                    q=checker.phased_polynomial(state['q'],tau)
                    residual=F(0)
                    for i in range(length):
                        value=st.ZERO
                        for j,coefficient in enumerate(q):
                            value=st.add(value,st.mul(coefficient,full[(i-stride*j)%length]))
                        residual=max(residual,st.norm2(st.sub(value,x[i])))
                    need(residual<=(mass*bound)**2,'expanded original polynomial residual')
                    dense_error=None
                    if length<=2 and r<=5:
                        exact=checker.matrix_solve(x,q,stride)
                        dense_error=max(st.norm2(st.sub(a,b)) for a,b in zip(full,exact))
                        need(dense_error<=bound*bound,'independent dense cubic execution')
                    rows.append(dict(radix=r,length=length,stride=stride,gauge=tau_name,
                                     working_bits=bits,prepared_root_bits=prepared['factor_bits'],
                                     root_preparation_cap=budget['factor_bits'],depth_cap=budget['effective_depth'],
                                     common_partial_bound=partial,common_partial_cap=1<<budget['h'],
                                     execution_bound=bound,factorization_bound=perturbation,
                                     total_bound=bound+perturbation,residual_squared=residual,
                                     dense_error_squared=dense_error,exact_output_equal=True,
                                     source_unchanged=True,original_records=original_tape.records,
                                     truncated_records=early_tape.records))
        print('PASS actual cubic stride radix',r,'cumulative cases',len(rows),flush=True)
    return dict(cases=rows,scope='Actual uniform-width execution at radices 3,4,5,7; '
                'the all-size claim is the written common-operator argument.')
