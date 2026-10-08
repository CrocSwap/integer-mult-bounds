#!/usr/bin/env python3
"""Exact common-basis and ordered-corner controls for dimensions (33,31,34).

Dominik Scholz, with substantial OpenAI GPT-6 Astra assistance. Apache-2.0.
PR24 supplies the family; PR25 supplies the A5 Schur-block precedent.
The symbolic argument is in notes/near-balanced-bit.tex.
"""
from fractions import Fraction as Q
from random import Random

def prescribed(a,b,R,C):
 H=a*b;n=len(R)
 for beta in range(b):
  p={}
  for i,c in list(enumerate(R))+[(H-len(C)+j,c) for j,c in enumerate(C)]:
   if i%b!=beta:continue
   r=i//b
   if (r in p and p[r]!=c) or (c in p.values() and p.get(r)!=c):return False
   p[r]=c
 return H>=2*n

def connected(a,b,labels,start):
 edges=[(c,a+((start+i)%b)) for i,c in enumerate(labels)]
 seen={0}
 while 1:
  new=seen|{y for x,y in edges if x in seen}|{x for x,y in edges if y in seen}
  if new==seen:break
  seen=new
 return len(seen)==a+b

def dual_pair(x,u,seed):
 rnd=Random(seed);b=len(x)
 ys=[Q(rnd.randrange(1,997)) for _ in range(b-2)]+[Q(0),Q(0)]
 vs=[Q(rnd.randrange(1,997)) for _ in range(b-2)]+[Q(0),Q(0)]
 det=x[-2]*u[-1]-x[-1]*u[-2];assert det
 for y,targetx,targetu in [(ys,1,0),(vs,0,1)]:
  tx=targetx-sum(xx*yy for xx,yy in zip(x,y));tu=targetu-sum(uu*yy for uu,yy in zip(u,y))
  y[-2]=(tx*u[-1]-x[-1]*tu)/det;y[-1]=(x[-2]*tu-tx*u[-2])/det
 assert sum(xi*yi for xi,yi in zip(x,ys))==1
 assert sum(ui*yi for ui,yi in zip(u,ys))==0
 assert sum(xi*vi for xi,vi in zip(x,vs))==0
 assert sum(ui*vi for ui,vi in zip(u,vs))==1
 assert all(ys) and all(vs)
 return ys,vs

def elimination(M, record=False):
 M=[row[:] for row in M];n=len(M);used=set();piv=[];values=[]
 for i in range(n):
  available=[j for j in range(n) if j not in used and M[i][j]]
  assert available,('singular',i)
  j=max(available);used.add(j);piv.append(j);values.append(M[i][j])
  for ii in range(i+1,n):
   if not M[ii][j]:continue
   factor=M[ii][j]/M[i][j]
   for jj in range(n):
    if M[i][jj]:M[ii][jj]-=factor*M[i][jj]
 return (piv,values) if record else piv

def a1(a,seed):
 b=a-2;k=a+1;H=a*b;n=a+k;I=list(range(a));R=C=I+[0]+I
 assert prescribed(a,b,R,C)
 assert connected(a,b,R[:a+b-1],0)
 assert connected(a,b,C[-(a+b-1):],H-(a+b-1))
 xa=[Q(i+1) for i in range(a)];ya=[Q(1,sum(xa))]*a
 xb=[Q(i+1) for i in range(b)];ub=[Q(i+2) for i in range(b)];yb,vb=dual_pair(xb,ub,seed)
 ot=[Q(i+1) for i in range(k)];ou=[Q(1,sum(ot))]*k
 p=I+[a]+I;q=I+list(range(k))
 f=[xa[R[i]]*xb[i%b]/ub[i%b]/ot[p[i]] for i in range(n)]
 g=[ya[C[j]]*yb[(H-n+j)%b]/vb[(H-n+j)%b]/ou[q[j]] for j in range(n)]
 M=[[Q(R[i]==C[j])+Q(p[i]==q[j])*f[i]*g[j] for j in range(n)] for i in range(n)]
 # Explicit first a block is I plus a single lower subdiagonal.
 for i in range(a):
  for j in range(a):assert M[i][a+1+j]==Q(i==j)+Q(i==j+1)*f[i]*g[a+1+j]
 expected=list(range(a+1,2*a+1))+[a,a-1]+list(range(1,a-1))+[0]
 actual,values=elimination(M,record=True);assert actual==expected
 determinant=Q(1)
 for value in values:determinant*=value
 inversions=sum(actual[i]>actual[j] for i in range(n) for j in range(i+1,n))
 determinant*=(-1)**inversions
 assert determinant
 # Opposite orientation changes only a global projector sign.
 assert elimination([[-x for x in row] for row in M])==expected
 return dict(a=a,b=b,k=k,seed=seed,pivots=actual,profile=[a,1,1,a-2,1],
   exact_rational=True,biorthogonal_pairings=True,common_prescriptions=True,A5_trees=True,
   rational_witness={name:list(map(str,values)) for name,values in [("xa",xa),("ya",ya),("xb",xb),("yb",yb),("ub",ub),("vb",vb),("outer_t",ot),("outer_phi",ou),("f",f),("g",g)]},
   exact_pivot_values=list(map(str,values)),scalar_pivots={"w":str(values[a]),"next":str(values[a+1]),"last":str(values[-1])},normalized_corner_determinant=str(determinant))

def basis():
 a,b,k=33,31,34;H=a*b;I=list(range(a));R=C=I+[0]+I;n=len(R)
 assert prescribed(a,b,R,C)
 trees=[]
 for labels,start in [(R[:a+b-1],0),(C[-(a+b-1):],H-(a+b-1))]:
  assert connected(a,b,labels,start)
  edges=[(c,a+(start+i)%b) for i,c in enumerate(labels)]
  assert len(edges)==a+b-1
  remaining=set(range(a+b));leaf=[]
  while len(remaining)>1:
   degree={v:sum(v in e and all(w in remaining for w in e) for e in edges) for v in remaining}
   x=min(v for v in remaining if degree[v]==1);leaf.append(x);remaining.remove(x)
  trees.append(dict(edges=edges,leaf_order=leaf,survivor=next(iter(remaining))))
 return dict(a=a,b=b,k=k,row_labels=R,inverse_column_labels=C,trees=trees)

def a5():
 a,b=33,31;H=a*b;n=a+b-1;I=list(range(a));R=C=I+[0]+I
 R=R[:n];C=C[-n:]
 p=[Q(i+1) for i in range(a)];xi=[1/sum(p)]*a
 v=[Q(i+2) for i in range(b)];nu=[1/sum(v)]*b
 M=[]
 for i in range(n):
  row=[]
  for j in range(n):
   beta=i%b;gamma=(H-n+j)%b;r=R[i];c=C[j]
   row.append(Q(beta==gamma)*p[r]*xi[c]+Q(r==c)*v[beta]*nu[gamma]-p[r]*xi[c]*v[beta]*nu[gamma])
  M.append(row)
 pivot=M[0][-1];assert pivot
 for i in range(1,b-1):
  for j in range(i+a-1,n-1):
   reduced=M[i][j]-M[i][-1]*M[0][j]/pivot
   assert reduced==(p[i]*xi[i+2] if j==i+a-1 else 0)
 pivots=elimination(M)
 assert pivots[0]==n-1 and pivots[1:b-1]==list(range(a,a+b-2))
 assert elimination([[-x for x in row] for row in M])==pivots
 return dict(exact_rational=True,profile=[*([1]*34),29,897],pivots=pivots)
