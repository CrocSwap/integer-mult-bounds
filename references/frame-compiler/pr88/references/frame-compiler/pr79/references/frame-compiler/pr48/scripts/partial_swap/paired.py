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
class PairedExclusionCircuit(ExclusionCircuit):
 base_threshold = 2
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
   for a in g:
    carry=self.total([weights[u] for u in g if u!=a])
    vals=[self.total([e(u,v) for u in g if u!=a for v in groups[j]]) for j in other]
    st,one,_=self.vector([carry]+vals,False)
    strips[a]={j:z for j,z in zip(other,one[1:])};sums[a]=st
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
