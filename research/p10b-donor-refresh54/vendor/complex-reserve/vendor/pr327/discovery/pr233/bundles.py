"""Connected equal-frame endpoint moves, motivated by PR164/168 bundle descent.

Own explicit boundary implementation: all source spans, incoming and outgoing
role frames are recomputed before a move. No physical legality is inferred from
an optimization score; the independent physical verifier remains mandatory.
"""
from collections import defaultdict
from physical_opt import join,meet
from paired_cube.frames import contained

def descend(o,rounds=4):
 report=[]
 for rnd in range(rounds):
  n=len(o.ops);parent=list(range(n))
  def root(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  def union(i,j):
   a,b=root(i),root(j)
   if a!=b:parent[max(a,b)]=min(a,b)
  for i in range(n):
   for j in o.prev[i]:
    if j is not None and o.frames[i]==o.frames[j]:union(i,j)
  groups=defaultdict(list)
  for i in range(n):groups[root(i)].append(i)
  groups=[l for l in groups.values() if len(l)>1];groups.sort(key=lambda l:min(l),reverse=not rnd%2)
  moved=changed=0;gain=0.;big=0
  for ids in groups:
   inside=set(ids);F=o.frames[ids[0]];assert all(o.frames[i]==F for i in ids)
   L=();U=o.full;previous=[];after=[]
   for i in ids:
    a,b,x=o.ops[i];L=join(L,o.spans[x])
    for role,j in zip((a,b),o.prev[i]):
     if j not in inside:
      A=o.frames[j] if j is not None else o.start[role];previous.append(A);L=join(L,A)
    for role,j in zip((a,b),o.next[i]):
     if j not in inside:
      A=o.frames[j] if j is not None else o.end[role];after.append(A);U=meet(U,A,o.h)
   assert contained(L,F) and contained(F,U)
   def score(A):
    d=len(A);return sum(o.phi[d-len(P)] for P in previous)+sum(o.phi[len(N)-d] for N in after)
   old=score(F);candidate=min((L,U),key=score);delta=old-score(candidate)
   if delta>1e-7:
    for i in ids:o.frames[i]=candidate
    moved+=1;changed+=len(ids);gain+=delta;big=max(big,len(ids))
  rec=dict(round=rnd,components=len(groups),moved_components=moved,changed_operations=changed,numerical_excess_gain=gain,largest_moved_component=big);report.append(rec);print('bundles',rec,flush=True)
  if not moved:break
 for i in range(n):
  P,N=o.neighbors(i);assert contained(o.spans[o.ops[i][2]],o.frames[i]);assert all(contained(F,o.frames[i]) for F in P);assert all(contained(o.frames[i],F) for F in N)
 return report
