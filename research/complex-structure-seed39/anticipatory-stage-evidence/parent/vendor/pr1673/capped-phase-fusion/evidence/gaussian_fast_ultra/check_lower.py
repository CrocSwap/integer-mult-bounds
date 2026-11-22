#!/usr/bin/env python3
"""Exact finite controls for LOWER-FACTOR.md; no floating point."""
from fractions import Fraction as F
from math import prod
import json
from pathlib import Path

def matmul(A,B):
 return [[sum((a*b for a,b in zip(row,col)),F(0)) for col in zip(*B)] for row in A]
def eye(n): return [[F(i==j) for j in range(n)] for i in range(n)]
def inv(A):
 n=len(A); B=[list(r)+list(e) for r,e in zip(A,eye(n))]
 for k in range(n):
  v=B[k][k]; assert v; B[k]=[x/v for x in B[k]]
  for i in range(n):
   if i!=k:
    v=B[i][k]; B[i]=[x-v*y for x,y in zip(B[i],B[k])]
 return [r[n:] for r in B]
def poly_mul(a,b):
 out=[F(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b): out[i+j]+=x*y
 return out
def newton_poly(xs):
 out=[F(1)]
 for x in xs: out=poly_mul(out,[-x,F(1)])
 return out
def elem(xs,k): return (-1)**k*newton_poly(xs)[len(xs)-k]
def suffix_pull(vs,M):
 """All <prod_(k>=i)(1-v_k Z),M>, exact D&C transpose tree."""
 if not vs: return [M[0]]
 if len(vs)==1: return [M[0]-vs[0]*M[1],M[0]]
 mid=len(vs)//2; left,right=vs[:mid],vs[mid:]
 P=[F(1)]
 for v in right: P=poly_mul(P,[F(1),-v])
 LM=[sum((P[k]*M[h+k] for k in range(len(P))),F(0)) for h in range(len(left)+1)]
 return suffix_pull(left,LM)[:-1]+suffix_pull(right,M[:len(right)+1])

def run():
 count={'instances':0,'inverse_entries':0,'tile_entries':0,'suffix_outputs':0,'exponent_bounds':0,'upper_entries':0}
 for s in range(3,12):
  for t in range(s+1,2*s+1):
   rho=F(t,s); q=[(2*t*i+s)//(2*s) for i in range(s)]
   beta=[rho*i-q[i] for i in range(s)]; x=[F(2)**k for k in q]
   # Arbitrary exact rational diagonal tests all identities independent of Gaussian values.
   d=[F(3)**(-q[i]*q[i]) for i in range(s)]
   C=[prod((1-x[k]/x[i] for k in range(i)),start=F(1)) for i in range(s)]
   D=lambda i,j:prod((1-x[j]/x[k] for k in range(j+1,i+1)),start=F(1))
   A=[d[i]*x[i]**i*C[i]/prod(x[:i+1],start=F(1)) for i in range(s)]
   L=[[F(0)]*s for _ in range(s)]
   for i in range(s):
    for j in range(i+1):
     L[i][j]=d[i]/d[j]*prod((x[i]-x[k] for k in range(j)),start=F(1))/prod((x[j]-x[k] for k in range(j)),start=F(1))
   LI=inv(L)
   for i in range(s):
    for j in range(i+1):
     assert LI[i][j]==(-1)**(i-j)*A[i]/A[j]/D(i,j)
     count['inverse_entries']+=1
     h=i-j
     exponent=-beta[i]**2+beta[j]**2-rho**2*h+2*rho*sum(beta[j+1:i+1],F(0))
     assert exponent<=F(1,4)-rho*(rho-1)*h
     count['exponent_bounds']+=1
   # Newton U inverse coefficients and V=L D U, with row diagonal removed.
   V=[[x[i]**j for j in range(s)] for i in range(s)]
   T=[[L[i][j]*d[j]/d[i] for j in range(s)] for i in range(s)]
   U=matmul(inv(T),V)
   for i in range(s):
    pivot=prod((x[i]-x[k] for k in range(i)),start=F(1))
    U[i]=[v/pivot for v in U[i]]
   UI=inv(U)
   for i in range(s):
    for j in range(i,s):
     assert UI[i][j]==(-1)**(j-i)*elem(x[:j],j-i)
     count['upper_entries']+=1
   # Every adjacent-cut tile, arbitrary signed inputs, exact moment/suffix algorithm.
   u=[F((-1)**j*(2*j+1),j+1) for j in range(s)]
   for l in range(1,s):
    b=min(s-1,l+3); J=list(range(max(0,l-4),l)); I=list(range(l,b+1))
    z=[x[j]/x[l] for j in J]; v=[x[l]/x[k] for k in range(l+1,b+1)]
    w=[(-1)**j*A[l]/A[j]/D(b,j)*u[j] for j in J]
    M=[sum((wj*zj**m for wj,zj in zip(w,z)),F(0)) for m in range(len(I))]
    pulled=suffix_pull(v,M)
    for i,got in zip(I,pulled):
     got*=(-1)**i*A[i]/A[l]
     expect=sum((LI[i][j]*u[j] for j in J),F(0))
     assert got==expect
     count['suffix_outputs']+=1; count['tile_entries']+=len(J)
   count['instances']+=1
 return count
if __name__=='__main__':
 out={'status':'all exact assertions passed','arithmetic':'fractions.Fraction','checks':run(),'scope':'Nonperiodic Newton L inverse and U inverse algebra; exact signed cross-tile data application; no runtime or tensor-fusion certificate.'}
 p=Path(__file__).with_name('LOWER-CONTROLS.json');p.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
