"""Depth-k merges of adjacent equal-frame components (generalizes joint.py to connected groups of up to k components).
Numerical witnesses only; the independent exact verifier remains mandatory."""
from collections import defaultdict
import random,time
from physical_opt import join,meet
from paired_cube.frames import contained
from joint import components

def evaluate(o,ids):
 inside=set(ids);L=();U=o.full;previous=[];after=[];old=0.
 for i in ids:
  x,y,node=o.ops[i];F=o.frames[i];L=join(L,o.spans[node])
  for role,j in zip((x,y),o.prev[i]):
   P=o.frames[j] if j is not None else o.start[role];old+=o.phi[len(F)-len(P)]
   if j not in inside:previous.append(P);L=join(L,P)
  for role,j in zip((x,y),o.next[i]):
   if j not in inside:
    N=o.frames[j] if j is not None else o.end[role];after.append(N);U=meet(U,N,o.h);old+=o.phi[len(N)-len(F)]
 if not contained(L,U):return None
 def score(F):
  d=len(F);return sum(o.phi[d-len(P)] for P in previous)+sum(o.phi[len(N)-d] for N in after)
 best=min((L,U),key=lambda F:(score(F),len(F),F));return old-score(best),best

def descend(o,depth=3,rounds=3,seed=0,limit=None):
 rng=random.Random(seed);report=[]
 for rnd in range(rounds):
  t=time.monotonic();groups,adjacent=components(o)
  nbr=defaultdict(set)
  for a,b in adjacent:nbr[a].add(b);nbr[b].add(a)
  keys=list(groups);rng.shuffle(keys);moved=changed=tried=0;gain=0.
  for a in keys[:limit]:
   # grow connected sets around a up to `depth` components, trying each as a merged move
   frontier=[(a,)];seen={(a,)}
   while frontier:
    grp=frontier.pop()
    if len(grp)>=2:
     ids=[i for c in grp for i in groups[c]];tried+=1
     r=evaluate(o,ids)
     if r and r[0]>1e-7:
      for i in ids:o.frames[i]=r[1]
      moved+=1;changed+=len(ids);gain+=r[0];break
    if len(grp)<depth:
     for c in grp:
      for d in nbr[c]:
       if d not in grp:
        new=tuple(sorted(grp+(d,)))
        if new not in seen:seen.add(new);frontier.append(new)
  rec=dict(round=rnd,depth=depth,groups=len(groups),tried=tried,moved=moved,changed=changed,numerical_excess_gain=gain,seconds=time.monotonic()-t);report.append(rec);print('deep',rec,flush=True)
  if not moved:break
 for i in range(len(o.ops)):
  P,N=o.neighbors(i);assert contained(o.spans[o.ops[i][2]],o.frames[i]);assert all(contained(F,o.frames[i]) for F in P);assert all(contained(o.frames[i],F) for F in N)
 return report
