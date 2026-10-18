#!/usr/bin/env python3
"""Exact failure control for independent coefficient rounding before erasure division."""
from fractions import Fraction as F
from pathlib import Path
import json

def pmul(a,b):
 c=[0]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):c[i+j]+=x*y
 return c
s,t=29,32;H=t-s;rho=F(t,s)
q=[(2*t*i+s)//(2*s) for i in range(s)]
holes=[i for i in range(t) if i not in q]
assert holes==[5,16,27]
# exp(2*a*rho)=2^(2s); then natural source coefficient scale is 2^(-t*j*j).
base=2**(2*s);E=[1]
for h in holes:E=pmul(E,[-base**h,1])
E0=abs(E[0]);P=1000;j=20
# Relative 2^-P perturbation of Q_0. Exactly compute the formal quotient error.
delta=F(E0,2**P)
c=[F(0)]*(j+1)
for k in range(j+1):
 rhs=delta if k==0 else F(0)
 c[k]=(rhs-sum(E[h]*c[k-h] for h in range(1,min(H,k)+1)))/E[0]
error=abs(c[j])*(2**(t*j*j))
min_error=F(2)**(t*j*j-2*s*holes[0]*j-P)
assert error>=min_error and min_error==2**6000
assert delta/E0==F(1,2**P)
res=dict(status='PASS_ERASURE_ROUNDING_FAILURE_CONTROL',s=s,t=t,holes=holes,
         relative_input_error='2^-1000',coefficient_index=j,
         normalized_output_error_lower='2^6000',
         exact_error_numerator_bits=error.numerator.bit_length(),
         scope='Independent coefficient perturbation destroys divisibility by E. Not an impossibility result for correlated or exact-root-preserving algorithms.')
Path(__file__).with_name('ERASURE-ROUNDING-CONTROL.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
