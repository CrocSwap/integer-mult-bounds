#!/usr/bin/env python3
"""Exact exponent checks for the polynomial-condition nearest-neighbor lemma."""
from fractions import Fraction as F
from pathlib import Path
import json
cases=products=0
for t in range(6,29):
 for s in range(max(5,(4*t+4)//5),t):
  rho=F(t,s);theta=rho-1
  if theta>F(1,4):continue
  q=[(2*t*j+s)//(2*s) for j in range(s)]
  beta=[rho*j-q[j] for j in range(s)]
  assert all(-F(1,2)<=v<F(1,2) for v in beta)
  def qext(i):
   z,j=divmod(i,s);return q[j]+z*t
  le=[];ue=[]
  for i in range(s):
   gap=qext(i)-qext(i-1)
   assert gap in (1,2)
   l=(beta[i]-rho)**2-beta[(i-1)%s]**2
   uprev=(beta[(i-1)%s]+rho)**2-beta[i]**2
   assert l+uprev==2*rho*gap
   le.append(l)
   ue.append((beta[i]+rho)**2-beta[(i+1)%s]**2)
  for i in range(s):
   lsum=usum=F(0)
   for h in range(1,2*s+1):
    lsum+=le[(i-h+1)%s];usum+=ue[(i+h-1)%s]
    low=(beta[i]**2-beta[(i-h)%s]**2
         -2*rho*sum(beta[(i-j)%s] for j in range(h))+h*rho*rho)
    upp=(beta[i]**2-beta[(i+h)%s]**2
         +2*rho*sum(beta[(i+j)%s] for j in range(h))+h*rho*rho)
    assert lsum==low and usum==upp
    assert lsum>=h*rho*theta-F(1,4)
    assert usum>=h*rho*theta-F(1,4)
    products+=2
  cases+=1
# With a >=4 log(16/theta), the proposed perturbation ratio is <=20 theta^4/16^6.
assert F(20,16**6)*F(1,4)**4 < F(1,2)
res=dict(status='PASS_EXACT_NEAREST_NEIGHBOR_EXPONENTS',parameter_pairs=cases,
         cyclic_product_bounds=products,cycle_lengths_up_to=28,
         controls=['all skip gaps checked','two full cyclic wraps checked'],
         scope='Exact exponent identities and inequalities; real exponential conclusions follow from monotonicity and geometric sums.')
Path(__file__).with_name('NEAREST-NEIGHBOR-CONTROLS.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
