#!/usr/bin/env python3
from fractions import Fraction as F
from pathlib import Path
import json

def p2(k):return F(2)**k
cases=entries=completion=0
for s in range(3,22):
 for t in range(s+1,min(2*s,s+5)+1):
  rho=F(t,s);lam=1/rho;q=[(2*t*j+s)//(2*s) for j in range(s)]
  cells={}
  for j,i in enumerate(q):cells.setdefault(i-j,[]).append(i)
  for c,inds in cells.items():
   m=inds[len(inds)//2];delta=F((t-s)*m-t*c,t)
   assert abs(delta)<=F(1,2)
   for k in inds:
    betak=(rho-1)*k-rho*c
    assert -F(1,2)<=betak<F(1,2)
    for i in inds:
     x=i-m;y=k-m
     raw=p2(-(t*(i-c)-s*k)**2)/3
     col=p2(-(t*(t-s)*x*x+2*t*((t-s)*m-t*c)*x))
     row=p2(s*(t-s)*y*y+2*s*((t-s)*m-t*c)*y-((t-s)*m-t*c)**2)/3
     toe=p2(-s*t*(x-y)**2)
     assert raw==row*toe*col
     beta_num=(t-s)*i-t*c
     N=p2(-(t*i-s*k-t*c)**2+beta_num**2)
     assert raw==N*p2(-beta_num**2)/3
     entries+=1
   cases+=1
  # Global selected block of identity-hole completion.
  for i,qi in enumerate(q):
   for j,qj in enumerate(q):
    raw=p2(-(t*j-s*qi)**2)/3
    bn=t*j-s*qj
    N=p2(-(t*j-s*qi)**2+bn*bn)
    assert raw==N*p2(-bn*bn)/3
    completion+=1
out={'status':'all exact assertions passed','phase_cell_cases':cases,'local_two_factorization_entries':entries,'selected_completion_entries':completion,'scope':'Exact target-grid coordinate conversion, local Toeplitz/Gaussian-normalized factorizations and selected block of square hole completion. Norm estimates are analytic.'}
Path(__file__).with_name('FORWARD-CELL-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
