#!/usr/bin/env python3
"""Exploratory whole intersection-one circuit; no frame certificate.

Counts are a screening result, not a multiplication witness. Small cases check
all coefficients; every construction step checks disjoint input supports.
"""
import sys,time,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from functools import lru_cache
from itertools import combinations
from math import comb,log,log1p,log2
from exclusion_circuit import ExclusionCircuit
MODE=os.environ.get("SPLIT_MODE","half")

class Circuit:
 add=ExclusionCircuit.add
 total=ExclusionCircuit.total
 vector=ExclusionCircuit.vector
 pair=ExclusionCircuit.pair
 def __init__(self,n,k,l,r):
  self.n=n;self.k=k;self.l=l;self.r=r
  self.inputs=list(combinations(range(n),k));self.targets=list(combinations(range(n),l))
  self.variables={p:i+1 for i,p in enumerate(self.inputs)}
  self.support=[0]+[1<<i for i in range(len(self.inputs))]
  self.args=[None]*len(self.support);self.lookup={s:i for i,s in enumerate(self.support)}
 def finish(self,outs):
  self.outputs=outs;active=set();stack=list(outs)
  while stack:
   x=stack.pop()
   if not x or x in active:continue
   active.add(x)
   if self.args[x]:stack.extend(self.args[x])
  self.active=sorted(active);self.additions=sum(self.args[x] is not None for x in active)
  return self
 def apply(self,template,inputs):
  nodes=[0]*(len(template.args));nodes[1:len(inputs)+1]=inputs
  for n in template.active:
   if template.args[n]:a,b=template.args[n];nodes[n]=self.add(nodes[a],nodes[b])
  return [nodes[n] for n in template.outputs]

def feasible(n,k,l,r):return 0<=k<=n and 0<=l<=n and 0<=r<=min(k,l) and k+l-r<=n
@lru_cache(None)
def build(n,k,l,r):
 assert feasible(n,k,l,r)
 c=Circuit(n,k,l,r);p=len(c.inputs);q=len(c.targets);row=comb(l,r)*comb(n-l,k-r)
 if row==1:
  return c.finish([next(i+1 for i,s in enumerate(c.inputs) if len(set(s)&set(t))==r) for t in c.targets])
 if l==0:return c.finish([c.total(list(range(1,p+1)))])
 if n<=4:
  return c.finish([c.total([i+1 for i,s in enumerate(c.inputs) if len(set(s)&set(t))==r]) for t in c.targets])
 if k==l==1 and r==0:
  return c.finish(c.vector(list(range(1,p+1)),False)[1])
 if k==1 and l==2 and r==0:
  return c.finish([x for pair,x in sorted(c.vector(list(range(1,p+1)))[2].items())])
 if k==l==2 and r==0:
  _,_,out=c.pair(list(range(n)));return c.finish([out[t] for t in c.targets])
 nl={"half":n//2,"third":max(1,n//3),"quarter":max(1,n//4),"pair":min(2,n-1)}[MODE];nr=n-nl;pieces={t:[] for t in c.targets}
 for b in range(max(0,l-nr),min(l,nl)+1):
  TL=list(combinations(range(nl),b));TR=list(combinations(range(nr),l-b))
  for a in range(max(0,k-nr),min(k,nl)+1):
   IL=list(combinations(range(nl),a));IR=list(combinations(range(nr),k-a))
   for u in range(r+1):
    if not feasible(nl,a,b,u) or not feasible(nr,k-a,l-b,r-u):continue
    left=build(nl,a,b,u);right=build(nr,k-a,l-b,r-u)
    mat=[[c.variables[s+tuple(nl+x for x in t)] for t in IR] for s in IL]
    lc=len(IR)*left.additions+len(TL)*right.additions
    rc=len(TR)*left.additions+len(IL)*right.additions
    if lc<=rc:
     temp=list(zip(*[c.apply(left,list(col)) for col in zip(*mat)]))
     out=[c.apply(right,list(row)) for row in temp]
    else:
     temp=[c.apply(right,row) for row in mat]
     out=list(zip(*[c.apply(left,list(col)) for col in zip(*temp)]))
    for i,s in enumerate(TL):
     for j,t in enumerate(TR):pieces[s+tuple(nl+x for x in t)].append(out[i][j])
 c.finish([c.total(pieces[t]) for t in c.targets])
 return c

if __name__=='__main__':
 for n in map(int,sys.argv[1:] or ['12','24','46']):
  start=time.time();c=build(n,3,3,1)
  if n<=24:
   for t,x in zip(c.targets,c.outputs):
    assert c.support[x]==sum(1<<i for i,s in enumerate(c.inputs) if len(set(s)&set(t))==1)
  R=c.additions+len(c.outputs);v=comb(n,3);D=v**3-6*v*v*n*n
  msg={'n':n,'additions':c.additions,'roles':R,'allocated':len(c.args),'secs':time.time()-start}
  if D>0:
   W=2*v**3+2*v*v*(R+n);a=-log1p(-D/(W*n**3))/log(n**3)
   msg.update(a=a,bits=-log2(3*a*a/70))
  print(msg,flush=True)
