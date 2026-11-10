#!/usr/bin/env python3
"""Exact checks of the upper suffix recurrence, tile identity, and blocked data algorithm."""
from fractions import Fraction as F
from pathlib import Path
import json
from check_lower import poly_mul, elem

def prod(xs):
 z=F(1)
 for x in xs:z*=x
 return z

def add(a,b):
 out=[F(0)]*max(len(a),len(b))
 for i,x in enumerate(a):out[i]+=x
 for i,x in enumerate(b):out[i]+=x
 return out

def prefix_sum(roots,weights):
 """sum weights[j] product_{k<j}(1+roots[k] X)."""
 if len(weights)==1:return [weights[0]]
 mid=len(weights)//2
 P=[F(1)]
 for x in roots[:mid]:P=poly_mul(P,[F(1),x])
 return add(prefix_sum(roots[:mid-1],weights[:mid]),poly_mul(P,prefix_sum(roots[mid:],weights[mid:])))

def run():
 out={'instances':0,'suffix_recurrences':0,'tile_entries':0,'signed_prefix_tree_and_hankel_outputs':0,'alpha_ratio_bounds':0}
 for s in range(3,13):
  for t in range(s+1,2*s+1):
   q=[(2*t*i+s)//(2*s) for i in range(s)]
   xs=[F(4)**k for k in q];ee=[F(3)**(-i*i) for i in range(s)]
   U=lambda i,j:(-1)**(j-i)*ee[j]/ee[i]*elem(xs[:j],j-i)
   C=lambda i,j:elem(xs[:j],j-i)/prod(xs[i:j])
   BB=[ee[j]*prod(xs[:j]) for j in range(s)]
   for i in range(s):
    for j in range(i,s-1):
     delta=C(i,j+1)-C(i,j)
     expected=elem(xs[:j],j-i+1)/prod(xs[i:j+1]) if i else F(0)
     assert delta==expected and delta>=0
     assert delta<=2*F(4)**(-(j-i+1))
     out['suffix_recurrences']+=1
   u=[F((-1)**j*(j+2),j+1) for j in range(s)]
   for m in range(1,s):
    l=max(0,m-4);r=min(s,m+5);I=list(range(l,m));J=list(range(m,r))
    aa=[elem([x/xs[m] for x in xs[:m]],h) for h in range(m+1)]
    tau=[(-1)**(j-m)*BB[j]/BB[m] for j in J]
    gamma={i:U(i,m) for i in I}
    roots=[xs[m]/xs[k] for k in range(m,r-1)]
    moments=prefix_sum(roots,[tau[k]*u[j] for k,j in enumerate(J)])
    R=len(moments)-1
    for i in I:
     d=m-i
     for j in J:
      b=[elem([xs[m]/xs[k] for k in range(m,j)],h) if h<=j-m else F(0) for h in range(R+1)]
      v=sum((aa[d+h]/aa[d]*b[h] for h in range(R+1) if d+h<=m),F(0))
      assert gamma[i]*tau[j-m]*v==U(i,j)
      out['tile_entries']+=1
    # Blocks of length two for normalized Hankel convolution.
    for d0 in range(1,m-l+1,2):
     B=min(2,m-l-d0+1)
     a=[aa[d0+k]/aa[d0] if d0+k<=m else F(0) for k in range(B+R)]
     cv=poly_mul(a,list(reversed(moments)))
     for off in range(B):
      d=d0+off;i=m-d
      got=gamma[i]*cv[off+R]/(aa[d]/aa[d0])
      expected=sum((U(i,j)*u[j] for j in J),F(0))
      assert got==expected
      out['signed_prefix_tree_and_hankel_outputs']+=1
    for d in range(1,m+1):
     for k in range(m-d+1):
      rat=aa[d+k]/aa[d]
      assert F(1,2)*F(4)**(-2*d*k-k*(k+1))<=rat<=2
      out['alpha_ratio_bounds']+=1
   out['instances']+=1
 return out
if __name__=='__main__':
 out={'status':'all exact assertions passed','arithmetic':'fractions.Fraction','checks':run(),'scope':'Algebra, signs, degree indexing, suffix-tail recurrence, and signed blocked upper data application. Cp-bit stability and asymptotic data cost are analytic, not certified by finite tests.'}
 Path(__file__).with_name('UPPER-DATA-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
