#!/usr/bin/env python3
"""Exact holes-completion factorization for geometric Vandermonde matrices."""
from fractions import Fraction as F
from pathlib import Path
import json

def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def inv(a):
 n=len(a);w=[list(r)+[F(i==j) for j in range(n)] for i,r in enumerate(a)]
 for i in range(n):
  k=next(k for k in range(i,n) if w[k][i]);w[i],w[k]=w[k],w[i]
  z=w[i][i];w[i]=[x/z for x in w[i]]
  for k in range(n):
   if k!=i:
    z=w[k][i];w[k]=[x-z*y for x,y in zip(w[k],w[i])]
 return [r[n:] for r in w]
def pmul(a,b):
 c=[F(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):c[i+j]+=x*y
 return c
def peval(a,x):
 z=F(0)
 for c in reversed(a):z=z*x+c
 return z
def ceil(x):return -((-x.numerator)//x.denominator)

cases=0;hole_formula=0;max_height=0
for t in range(3,13):
 for s in range((t+1)//2,t):
  rho=F(t,s);H=t-s
  selected=[(2*t*j+s)//(2*s) for j in range(s)]
  assert len(set(selected))==s
  holes=[k for k in range(t) if k not in selected]
  assert len(holes)==H
  # Exact complementary Beatty identity, including tie cases.
  rp=F(t,H)
  formula=[ceil(rp*(F(l)+F(1,2))-F(1,2)) for l in range(H)]
  assert holes==formula,(t,s,holes,formula)
  for l,h in enumerate(holes):assert abs(F(h)-rp*(F(l)+F(1,2)))<=F(1,2)
  hole_formula+=1
  for base in (F(2),F(3,2)):
   x=[base**i for i in range(t)]
   V=[[xi**j for j in range(t)] for xi in x];Vi=inv(V)
   P=[F(1)]
   for xi in x:P=pmul(P,[-xi,F(1)])
   derivative=[F(j)*P[j] for j in range(1,len(P))]
   T=[[P[t-(i-j)] if i>=j else F(0) for j in range(H)] for i in range(H)]
   Ht=[[x[h]**j for h in holes] for j in range(H)]
   D=[[1/peval(derivative,x[holes[i]]) if i==j else F(0) for j in range(H)] for i in range(H)]
   A=[[Vi[t-1-j][h] for h in holes] for j in range(H)]
   assert mm(mm(T,Ht),D)==A
   # Complete a partial values vector to a degree<s polynomial.
   y=[[F((k*k+3*k+1)%7-3)] for k in range(t)]
   for h in holes:y[h][0]=F(0)
   c=mm(Vi,y);tail=[[-c[t-1-j][0]] for j in range(H)]
   z=mm(inv(A),tail)
   for i,h in enumerate(holes):y[h]=z[i]
   final=mm(Vi,y)
   assert all(final[j][0]==0 for j in range(s,t))
   Vs=[[x[k]**j for j in range(s)] for k in selected]
   direct=mm(inv(Vs),[[F((k*k+3*k+1)%7-3)] for k in selected])
   assert final[:s]==direct
   max_height=max(max_height,max(max(abs(v.numerator).bit_length(),v.denominator.bit_length()) for r in Vi for v in r))
   cases+=1
res=dict(status='PASS_EXACT_HOLES_FACTORIZATION',factorization_cases=cases,
         complementary_beatty_cases=hole_formula,max_inverse_coefficient_bits=max_height,
         scope='Exact finite Vandermonde/Toeplitz/complement algebra and degree-tail completion. No floating stability or O(p) global implementation established.')
Path(__file__).with_name('HOLES-CONTROLS.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
