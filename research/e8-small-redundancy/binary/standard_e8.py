from itertools import combinations,product
from fractions import Fraction
import json
from pathlib import Path

roots=[]
for i,j in combinations(range(8),2):
 for s in [-1,1]:
  x=[0]*8;x[i]=2;x[j]=2*s;roots.append(tuple(x))
for signs in product([-1,1], repeat=7):
 if sum(x<0 for x in signs)%2==0: roots.append((1,)+signs)
assert len(roots)==120

def dot(x,y):return sum(a*b for a,b in zip(x,y))
def binary_basis(xs):
 out={}
 for x in xs:
  while x:
   k=x.bit_length()-1
   if k in out:x^=out[k]
   else:out[k]=x;break
 return list(out.values())
def rank_mod(xs,p=101):
 bas={}
 for row in xs:
  row=[x%p for x in row]
  for i in range(8):
   if row[i]:
    if i in bas:
     v=row[i];row=[(x-v*y)%p for x,y in zip(row,bas[i])]
    else:
     inv=pow(row[i],-1,p);bas[i]=[x*inv%p for x in row];break
 return len(bas)
K=[sum((1^(dot(x,y)//4&1))<<j for j,y in enumerate(roots)) for x in roots]
B=binary_basis(K);assert len(B)==9
C=[0]
for b in B:C += [x^b for x in C]
a=[(1,-1,-1,-1,-1,-1,-1,1),(2,2,0,0,0,0,0,0),(-2,2,0,0,0,0,0,0),(0,-2,2,0,0,0,0,0),(0,0,-2,2,0,0,0,0),(0,0,0,-2,2,0,0,0),(0,0,0,0,-2,2,0,0),(0,0,0,0,0,-2,2,0)]

def nullvec(rows):
 rows=[[Fraction(x) for x in r] for r in rows]; piv=[];k=0
 for j in range(8):
  p=next((p for p in range(k,len(rows)) if rows[p][j]),None)
  if p is None:continue
  rows[k],rows[p]=rows[p],rows[k];t=rows[k][j];rows[k]=[x/t for x in rows[k]]
  for p in range(len(rows)):
   if p!=k:
    t=rows[p][j];rows[p]=[x-t*y for x,y in zip(rows[p],rows[k])]
  piv.append(j);k+=1
 f=next(i for i in range(8) if i not in piv);v=[Fraction(0)]*8;v[f]=1
 for j,r in zip(piv,rows):v[j]=-r[f]
 return v
