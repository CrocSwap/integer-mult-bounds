#!/usr/bin/env python3
from fractions import Fraction as F
from pathlib import Path
import json
from check_lower import matmul, inv, elem

def pp2(n):return F(2)**n
def prod(v):
 z=F(1)
 for x in v:z*=x
 return z
def complete(xs,n):
 c=[F(1)]+[F(0)]*n
 for x in xs:
  for k in range(1,n+1):c[k]+=x*c[k-1]
 return c[n]
def case(s,t,l,n):
 q=lambda i:(2*t*i+s)//(2*s)
 x=lambda i:pp2(2*s*t*q(i))
 e=lambda i:pp2(-t*t*i*i+(t*i-s*q(i))**2)
 G=lambda i,j:pp2(-(t*j-s*q(i))**2+(t*j-s*q(j))**2)
 C=lambda i,o:prod(1-x(k)/x(i) for k in range(o,i))
 L=lambda i,j,o:G(i,j)*prod(1-x(k)/x(i) for k in range(o,j))/C(j,o) if i>=j else F(0)
 U=lambda i,j,o:e(j)/e(i)*complete([x(k) for k in range(o,i+1)],j-i) if j>=i else F(0)
 ids=list(range(l,l+n)); LL=[[L(i,j,l) for j in ids] for i in ids];UU=[[U(i,j,l) for j in ids] for i in ids]
 CC=[[C(i,l) if i==j else F(0) for j in ids] for i in ids]
 assert matmul(matmul(LL,CC),UU)==[[G(i,j) for j in ids] for i in ids]
 UI=inv(UU)
 for ii,i in enumerate(ids):
  for jj,j in enumerate(ids):
   assert L(i+s,j+s,l+s)==L(i,j,l)
   assert U(i+s,j+s,l+s)==U(i,j,l)
   assert G(i+s,j+s)==G(i,j)
   if j>=i:
    assert UI[ii][jj]==(-1)**(j-i)*e(j)/e(i)*elem([x(k) for k in range(l,j)],j-i)
 return n*n

def main():
 instances=entries=0
 for s,t in [(2,3),(3,4),(3,5),(4,5),(4,7)]:
  for l in [-5,-2,0]:
   for n in [3,4,5]:entries+=case(s,t,l,n);instances+=1
 out={'status':'all exact assertions passed','arithmetic':'fractions.Fraction','negative_and_zero_origin_instances':instances,'finite_LDU_and_shift_entries':entries,'scope':'Finite-origin algebra, exact origin-shift correction, upper inverse formula and simultaneous periodic shifts; bilateral limiting argument is analytic.'}
 Path(__file__).with_name('BILATERAL-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
