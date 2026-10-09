# Cyclic interval strips (PR62 interval idea) in the h23 retained-total bit producer.
# Copy of scripts/partial_swap/paired.py with ONLY the strip leave-one-out replaced; loaded privately.
# Rohan Arun with Anthropic Claude assistance, Apache-2.0; original notices retained.
# Copyright 2026 icekylinx. Licensed under Apache-2.0.
# Adapted with AI assistance from the archived partial-swap research producer.
# Underlying circuit modules: jacklightChen/integer-mult-bounds, PR7
# commit 6725c6a17b17871a35353fd29157f4ed851bc114; original credits retained.
#!/usr/bin/env python3
"""Cancellation-free pair exclusion with recursively aggregated vertex weights.

At each level group vertices in pairs. Internal edges become vertex weights
in the smaller graph. Keeping those weights in the recursion avoids a separate
leave-two-out circuit for each level. All coefficients are checked exactly.
"""
from exclusion_circuit import ExclusionCircuit
from itertools import combinations
import os
LAYOUT='cyclic';ORDER='id';CARRY='last'
class PairedExclusionCircuit(ExclusionCircuit):
 base_threshold = 2
 def loo(self,values):
  """Total and leave-one-out sums; layout selected by BITX_LAYOUT (bitx research)."""
  add=self.add;k=len(values);v=[0]+list(values)  # 1-based
  if LAYOUT=='prefix':
   st,one,_=self.vector(values,False);return st,one
  if k==0:return 0,[]
  if LAYOUT=='dual':
   # s_j=(A_{j-1}+v_{j+1})+B_{j+2}, s_k=A_{k-1}
   A=[0]*(k+1)
   for t in range(1,k):A[t]=add(A[t-1],v[t])
   B=[0]*(k+3)
   for t in range(k,1,-1):B[t]=add(v[t],B[t+1])
   one=[add(add(A[t-1],v[t+1]),B[t+2]) for t in range(1,k)]+[A[k-1]]
   return add(A[k-1],v[k]),one
  if LAYOUT=='skip':
   # s_j=A_{j-2}+(v_{j-1}+B_{j+1}), s_1=B_2
   A=[0]*(k+1)
   for t in range(1,k-1):A[t]=add(A[t-1],v[t])
   B=[0]*(k+3)
   for t in range(k,1,-1):B[t]=add(v[t],B[t+1])
   one=[B[2]]+[add(A[t-2],add(v[t-1],B[t+1])) for t in range(2,k+1)]
   return add(v[1],B[2]),one
  if LAYOUT=='cyclic':
   # I(a,m)=I(a,m-1)+v_{a+m-1} (cyclic, 0-based a); s_j=I(j+1,k-1)
   vals=list(values);I={}
   for a in range(k):
    cur=0
    for m in range(1,k):
     cur=add(cur,vals[(a+m-1)%k]);I[a,m]=cur
   one=[I[(j+1)%k,k-1] if k>1 else 0 for j in range(k)]
   return add(one[0],vals[0]),one
  raise ValueError(LAYOUT)
 def pair(self,points):return self.block(points,{(a,b):self.variables[a,b] for a,b in combinations(points,2)},{a:0 for a in points})
 def grouping(self,points):return [points[i:i+2] for i in range(0,len(points),2)]
 def block(self,points,edges,weights):
  if len(points)<=self.base_threshold:
   total=lambda omit:self.total([x for p,x in edges.items() if not set(p)&set(omit)]+[x for p,x in weights.items() if p not in omit])
   return total(()),{a:total((a,)) for a in points},{(a,b):total((a,b)) for a,b in combinations(points,2)}
  groups=self.grouping(points);ng=len(groups);e=lambda a,b:edges[tuple(sorted((a,b)))]
  coarse={(i,j):self.total([e(a,b) for a in groups[i] for b in groups[j]]) for i,j in combinations(range(ng),2)}
  wt={i:self.total([weights[a] for a in g]+[e(a,b) for a,b in combinations(g,2)]) for i,g in enumerate(groups)}
  total,outside,far=self.block(list(range(ng)),coarse,wt)
  strips={};sums={}
  for i,g in enumerate(groups):
   other=[j for j in range(ng) if j!=i]
   if ORDER=='rev':other.sort(key=lambda j:-j)
   elif ORDER=='partner':other.sort(key=lambda j:((j^1)==i,-j))
   elif ORDER=='partnerfirst':other.sort(key=lambda j:((j^1)!=i,j))
   for a in g:
    carry=self.total([weights[u] for u in g if u!=a])
    vals=[self.total([e(u,v) for u in g if u!=a for v in groups[j]]) for j in other]
    if CARRY=='last':
     st,one=self.loo(vals+[carry]);one=one[:-1]
    else:
     st,one=self.loo([carry]+vals);one=one[1:]
    strips[a]={j:z for j,z in zip(other,one)};sums[a]=st
  out={};single={a:self.add(outside[i],sums[a]) for i,g in enumerate(groups) for a in g}
  for i,g in enumerate(groups):
   for a,b in combinations(g,2):out[a,b]=outside[i]
  for i,j in combinations(range(ng),2):
   for a in groups[i]:
    left=self.add(far[i,j],strips[a][j])
    for b in groups[j]:
     cross=self.total([e(u,v) for u in groups[i] if u!=a for v in groups[j] if v!=b])
     out[a,b]=self.add(left,self.add(strips[b][i],cross))
  return total,single,out
if __name__=='__main__':
 for n in (15,25,45,49):
  c=PairedExclusionCircuit(n);print(n,c.verify(),flush=True)
