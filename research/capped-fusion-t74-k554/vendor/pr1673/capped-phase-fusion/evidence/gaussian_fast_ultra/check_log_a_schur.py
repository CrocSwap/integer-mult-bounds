#!/usr/bin/env python3
from fractions import Fraction as F
from pathlib import Path
import json

def gap(A,i):return abs(A[i][i])-sum(abs(x) for j,x in enumerate(A[i]) if j!=i)
def norm(A):return max(sum(abs(x) for x in row) for row in A)
def run():
 counts={'nearest_exponent_checks':0,'far_exponent_checks':0,'schur_eliminations':0,'schur_entries':0}
 for s in range(2,61):
  for t in range(s+1,2*s+1):
   rho=F(t,s);th=rho-1
   q=lambda i:(2*t*i+s)//(2*s)
   beta=lambda i:rho*i-q(i)
   for i in range(s):
    b=beta(i)
    lower=(b-rho)**2-beta(i-1)**2
    upper=(b+rho)**2-beta(i+1)**2
    assert lower>=1+2*th-2*b
    assert upper>=1+2*th+2*b
    counts['nearest_exponent_checks']+=2
    for h in [-4,-3,-2,2,3,4]:
     assert (rho*h+b)**2-beta(i+h)**2>=h*h-abs(h)
     counts['far_exponent_checks']+=1
 # Both signs and asymmetric rows: no positivity hypothesis on filled off-diagonals.
 for n in range(3,15):
  for seed in range(6):
   A=[[F(1) if i==j else F(((-1)**(i+j+seed))*((7*i+3*j+seed)%11+1),40*n) for j in range(n)] for i in range(n)]
   original_gap=min(gap(A,i) for i in range(n)); original_norm=norm(A)
   while len(A)>2:
    k=(seed+len(A))%len(A);idx=[i for i in range(len(A)) if i!=k]
    B=[[A[i][j]-A[i][k]*A[k][j]/A[k][k] for j in idx] for i in idx]
    assert min(gap(B,i) for i in range(len(B)))>=original_gap
    assert norm(B)<=original_norm
    assert all(B[i][i]>0 for i in range(len(B)))
    counts['schur_eliminations']+=1;counts['schur_entries']+=len(B)**2
    A=B
 return counts
if __name__=='__main__':
 out={'status':'all exact assertions passed','arithmetic':'fractions.Fraction','checks':run(),'scope':'Nearest/far Gaussian exponent inequalities and signed/asymmetric Schur row-gap preservation; the transcendental row-sum estimate and tensor transfer are analytic.'}
 Path(__file__).with_name('LOG-A-SCHUR-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
