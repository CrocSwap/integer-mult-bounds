#!/usr/bin/env python3
from fractions import Fraction as F
from math import prod,ceil
from pathlib import Path
import json

def p2(k):return F(2)**k
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b))] for i in range(len(a))]
def symmetric(xs,n,complete):
 p=[F(1)]+[F(0)]*n
 for x in xs:
  if complete:
   for j in range(1,n+1):p[j]+=x*p[j-1]
  else:
   for j in range(n,0,-1):p[j]+=x*p[j-1]
 return p[n]
def test(s,t,l,n):
 ids=list(range(l,l+n));q={i:(2*t*i+s)//(2*s) for i in ids}
 x={i:p2(2*s*t*q[i]) for i in ids}
 e={i:p2(-t*t*i*i+(t*i-s*q[i])**2) for i in ids}
 g=lambda i,j:p2(-(t*j-s*q[i])**2+(t*j-s*q[j])**2)
 c={i:prod(1-x[k]/x[i] for k in ids if k<i) for i in ids}
 lo=[];up=[];li=[];ui=[];checks=0
 r=p2(2*s*t);cl=1-1/(r-1);env=p2(ceil(F(s*s,4)));decay=p2(-t*(t-s))
 for i in ids:
  lr=[];ur=[];lir=[];uir=[]
  for j in ids:
   lr.append(g(i,j)*prod(1-x[k]/x[i] for k in ids if k<j)/c[j] if i>=j else F(0))
   ur.append(e[j]/e[i]*symmetric([x[k] for k in ids if k<=i],j-i,True) if j>=i else F(0))
   if i>=j:
    h=i-j
    exponent=-(t*i-s*q[i])**2+(t*j-s*q[j])**2-t*t*h+2*t*sum(t*k-s*q[k] for k in ids if j<k<=i)
    z=(-1)**h*c[i]/c[j]*p2(exponent)/prod(1-x[j]/x[k] for k in ids if j<k<=i)
    assert abs(z)<=cl**-2*env*decay**h;checks+=1
   else:z=F(0)
   lir.append(z)
   if j>=i:
    h=j-i;z=(-1)**h*e[j]/e[i]*symmetric([x[k] for k in ids if k<j],h,False)
    assert abs(z)<=cl**-1*env*decay**h;checks+=1
   else:z=F(0)
   uir.append(z)
  lo.append(lr);up.append(ur);li.append(lir);ui.append(uir)
 eye=[[F(i==j) for j in range(n)] for i in range(n)]
 diag=[[c[ids[i]] if i==j else F(0) for j in range(n)] for i in range(n)]
 assert mm(mm(lo,diag),up)==[[g(i,j) for j in ids] for i in ids]
 assert mm(lo,li)==eye and mm(li,lo)==eye
 assert mm(up,ui)==eye and mm(ui,up)==eye
 return checks,5*n*n
cases=bounds=entries=0
for s,t in ((2,3),(3,4),(4,5),(4,7)):
 for l,n in ((-2,4),(-1,5),(0,5)):
  a,b=test(s,t,l,n);cases+=1;bounds+=a;entries+=b
out={'status':'pass','arithmetic':'exact rational with a=s^2 log(2)','finite_origin_cases':cases,'exact_factorization_and_inverse_entries':entries,'uniform_inverse_entry_bounds':bounds,'scope':'Finite-origin algebra and uniform estimates; bilateral limit and periodization justified analytically in companion note.'}
Path(__file__).with_name('FIXED-A-LDU-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
