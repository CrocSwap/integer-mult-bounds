#!/usr/bin/env python3
from check_lower import F, poly_mul, newton_poly, matmul, eye, inv
from pathlib import Path
import json

def local(xs,ds,l,r):
 n=r-l;A=[[F(0)]*n for _ in range(n)]
 for j in range(l,r):
  P=newton_poly(xs[l:j])
  for k,p in enumerate(P):A[k][j-l]=ds[j]*p/ds[l+k]
 return A

def main():
 count=0
 for n in range(2,13):
  xs=[F(2)**(i+i//3) for i in range(n)]
  ds=[F(3)**(-i*i) for i in range(n)]
  for l in range(n-1):
   for r in range(l+2,n+1):
    m=(l+r)//2;n1=m-l;n2=r-m
    P=newton_poly(xs[l:m]);M=eye(r-l)
    for i in range(l,r):
     for j in range(m,r):
      k=i-l-(j-m)
      M[i-l][j-l]=ds[j]/ds[i]*P[k] if 0<=k<len(P) else F(0)
    C=[[F(0)]*(r-l) for _ in range(r-l)]
    for start,stop in ((l,m),(m,r)):
     T=local(xs,ds,start,stop)
     for i in range(stop-start):
      for j in range(stop-start):C[start-l+i][start-l+j]=T[i][j]
    assert matmul(M,C)==local(xs,ds,l,r)
    B=[row[n1:] for row in M[:n1]];D=[row[n1:] for row in M[n1:]];DI=inv(D)
    K=matmul(B,DI);S=eye(r-l)
    for i in range(n1):
     for j in range(n2):S[i][n1+j]=K[i][j]
    E=eye(r-l)
    for i in range(n2):
     for j in range(n2):E[n1+i][n1+j]=D[i][j]
    assert matmul(S,E)==M
    count+=1
 out={'status':'all exact assertions passed','arithmetic':'fractions.Fraction','normalized_node_merges_and_shear_factorizations':count,'scope':'Algebra and degree indexing, not bounded FFT realization or tensor fusion.'}
 Path(__file__).with_name('UPPER-MERGE-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
