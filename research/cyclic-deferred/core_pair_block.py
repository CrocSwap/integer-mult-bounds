"""Core-aware pair assembly within PairedTriple's contracted pair subproblems.

Adapted from Avi Eisenberg's PR62 interval-strip/core-aware pair producer
(Apache-2.0, Anthropic Claude assistance), on the inherited icekylinx paired
exclusion recursion. This adaptation uses a two-point base case, the caller's
cyclic-strip vector routine, and column-pair coarse sums at every level.
Prepared with OpenAI Codex assistance. All operations remain disjoint sums;
the enclosing producer checks exact supports and binary frame inclusions.
"""
from itertools import combinations

def block(self,points,edges,weights):
 if len(points)<=2:
  total=lambda omit:self.total([x for p,x in edges.items()if not set(p)&set(omit)]+[x for p,x in weights.items()if p not in omit])
  return total(()),{a:total((a,))for a in points},{(a,b):total((a,b))for a,b in combinations(points,2)}
 groups=self.grouping(points);ng=len(groups);e=lambda a,b:edges[tuple(sorted((a,b)))]
 coarse={(i,j):self.total([self.total([e(a,b)for a in groups[i]])for b in groups[j]])for i,j in combinations(range(ng),2)}
 wt={i:self.total([weights[a]for a in g]+[e(a,b)for a,b in combinations(g,2)])for i,g in enumerate(groups)}
 total,outside,far=self.block(list(range(ng)),coarse,wt)
 strips={};sums={}
 for i,g in enumerate(groups):
  other=[j for j in range(ng)if j!=i]
  for a in g:
   carry=self.total([weights[u]for u in g if u!=a])
   vals=[self.total([e(u,v)for u in g if u!=a for v in groups[j]])for j in other]
   st,one,_=self.vector([carry]+vals,False)
   strips[a]={j:z for j,z in zip(other,one[1:])};sums[a]=st
 out={};single={a:self.add(outside[i],sums[a])for i,g in enumerate(groups)for a in g}
 for i,g in enumerate(groups):
  for a,b in combinations(g,2):out[a,b]=outside[i]
 for i,j in combinations(range(ng),2):
  if len(groups[i])==2 and len(groups[j])==2:
   (a,a2),(b,b2)=groups[i],groups[j];F=far[i,j]
   Sa,Sa2,Sb,Sb2=strips[a][j],strips[a2][j],strips[b][i],strips[b2][i]
   FSa,FSa2=self.add(F,Sa),self.add(F,Sa2)
   FSb,FSb2=self.add(F,Sb),self.add(F,Sb2)
   Y1=self.add(FSb,Sa);Y2=self.add(FSa,Sb2)
   Y3=self.add(FSa2,e(a,b2));Y4=self.add(FSb2,e(a,b))
   out[a,b]=self.add(e(a2,b2),Y1);out[a,b2]=self.add(e(a2,b),Y2)
   out[a2,b]=self.add(Y3,Sb);out[a2,b2]=self.add(Y4,Sa2)
  else:
   for a in groups[i]:
    left=self.add(far[i,j],strips[a][j])
    for b in groups[j]:
     cross=self.total([e(u,v)for u in groups[i]if u!=a for v in groups[j]if v!=b])
     out[a,b]=self.add(left,self.add(strips[b][i],cross))
 return total,single,out
