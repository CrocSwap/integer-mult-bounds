#!/usr/bin/env python3
"""Check the induction identities on arbitrary constrained child matrices.
This model constructs no recursive word or polynomial interval.
Charles Bethin, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import random

def mul(a,b):
 d=len(a);z=[[Q(0) for _ in range(d)] for _ in range(d)]
 for i in range(d):
  for k in range(d):
   if a[i][k]:
    for j in range(d):z[i][j]+=a[i][k]*b[k][j]
 return z

def add(a,b,s=1):return [[x+s*y for x,y in zip(r,t)] for r,t in zip(a,b)]
def unit(d):return [[Q(i==j) for j in range(d)] for i in range(d)]
def inverse(a):
 d=len(a);v=[r[:]+s for r,s in zip(a,unit(d))]
 for k in range(d):
  p=next(j for j in range(k,d) if v[j][k]);v[p],v[k]=v[k],v[p]
  scale=v[k][k];v[k]=[t/scale for t in v[k]]
  for j in range(d):
   if j!=k:
    scale=v[j][k];v[j]=[x-scale*y for x,y in zip(v[j],v[k])]
 return [r[d:] for r in v]

def require(a,b):
 if a!=b:raise ValueError('phase identity fails')

def main():
 rng=random.Random(64);count=0
 for scratch in (1,2,3):
  d=2*(3+scratch);I=unit(d)
  def block(dst,src,coef):
   M=[[Q(0) for _ in range(d)] for _ in range(d)]
   for i in range(2):
    for j in range(2):M[2*dst+i][2*src+j]=coef[i][j]
   return M
  def coeff():return [[Q(rng.randrange(-3,4)) for _ in range(2)] for _ in range(2)]
  def child(src,dst):
   M=I
   # Every scratch coordinate participates; the outer source stays fixed.
   for w in range(3,3+scratch):
    M=mul(add(I,block(w,src,coeff())),M)
    M=mul(add(I,block(dst,w,coeff())),M)
   return mul(add(I,block(dst,src,coeff())),M)
  for trial in range(4):
   A=coeff();B=coeff();E=block(1,2,A);H=block(2,0,B)
   U=add(I,H);V=add(I,E);Ui=add(I,H,-1);Vi=add(I,E,-1)
   G=mul(E,H);F=add(I,G)
   require(F,mul(Vi,mul(Ui,mul(V,U))))
   Pa=child(0,2);Pb=child(0,2);Qa=child(2,1);Qb=child(2,1)
   Pai=inverse(Pa);Pbi=inverse(Pb);Qai=inverse(Qa);Qbi=inverse(Qb)
   starts=[Pa,mul(Qa,U),mul(Pa,mul(Ui,mul(V,U))),mul(Qa,F)]
   ends=[Pb,mul(Qb,U),mul(Pb,mul(Ui,mul(V,U))),mul(Qb,F)]
   predictions={(0,1):mul(Qb,mul(U,Pai)),(1,2):mul(mul(Pb,Ui),mul(V,Qai)),(2,3):mul(mul(Qb,Vi),Pai),
    (0,2):add(mul(Pb,Pai),mul(E,mul(U,Pai))),
    (1,3):add(mul(Qb,Qai),mul(mul(Qb,Vi),H),-1),
    (0,3):add(mul(Qb,Pai),G)}
   for (s,t),pred in predictions.items():require(mul(ends[t],inverse(starts[s])),pred);count+=1
   backwards={(2,0):add(mul(Pa,Pbi),mul(E,mul(U,Pbi)),-1),
    (3,1):add(mul(Qa,Qbi),mul(mul(Qa,Vi),H)),
    (3,0):add(mul(Pa,Qbi),G,-1)}
   for (s,t),pred in backwards.items():require(mul(starts[t],inverse(ends[s])),pred);count+=1
 print('PASS_PHASE_ALGEBRA identities='+str(count)+' shared_scratch=1,2,3 block_size=2')
if __name__=='__main__':main()
