"""Joint collapse of adjacent operation-frame components.

All incoming/outgoing chains and actual value supports bound each common
frame. Old internal rank increments are charged once per role edge. A move
must reduce the full boundary-plus-internal numerical objective. Floating
scores select a witness only; admission requires the independent exact audit.
"""
from collections import defaultdict
import random,time
from physical_opt import join,meet
from paired_cube.frames import contained

def components(o):
 n=len(o.ops);parent=list(range(n))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i in range(n):
  for j in o.prev[i]:
   if j is not None and o.frames[i]==o.frames[j]:
    a,b=root(i),root(j)
    if a!=b:parent[max(a,b)]=min(a,b)
 groups=defaultdict(list)
 for i in range(n):groups[root(i)].append(i)
 adjacent=set()
 for i in range(n):
  for j in o.prev[i]:
   if j is not None and root(i)!=root(j):adjacent.add(tuple(sorted((root(i),root(j)))))
 return groups,sorted(adjacent)

def descend(o,rounds=5,order='forward',seed=0):
 result=[];rng=random.Random(seed)
 for rnd in range(rounds):
  t=time.monotonic();groups,adjacent=components(o)
  if order=='random':rng.shuffle(adjacent)
  elif (order=='reverse')^(rnd%2==1):adjacent.reverse()
  tried=feasible=moved=changed=largest=0;gain=0.
  for a,b in adjacent:
   ids=groups[a]+groups[b];inside=set(ids);tried+=1
   # Each original component remains uniform even after overlapping moves.
   assert all(o.frames[i]==o.frames[a] for i in groups[a])
   assert all(o.frames[i]==o.frames[b] for i in groups[b])
   L=();U=o.full;previous=[];after=[];old=0.
   for i in ids:
    x,y,node=o.ops[i];F=o.frames[i];L=join(L,o.spans[node])
    for role,j in zip((x,y),o.prev[i]):
     P=o.frames[j] if j is not None else o.start[role]
     assert contained(P,F);old+=o.phi[len(F)-len(P)]
     if j not in inside:previous.append(P);L=join(L,P)
    for role,j in zip((x,y),o.next[i]):
     if j not in inside:
      N=o.frames[j] if j is not None else o.end[role]
      assert contained(F,N);after.append(N);U=meet(U,N,o.h);old+=o.phi[len(N)-len(F)]
   if not contained(L,U):continue
   feasible+=1
   def score(F):
    d=len(F);return sum(o.phi[d-len(P)] for P in previous)+sum(o.phi[len(N)-d] for N in after)
   best=min((L,U),key=lambda F:(score(F),len(F),F));delta=old-score(best)
   if delta>1e-7:
    for i in ids:o.frames[i]=best
    moved+=1;changed+=len(ids);gain+=delta;largest=max(largest,len(ids))
  row=dict(round=rnd,groups=len(groups),tried=tried,feasible=feasible,moved=moved,changed=changed,largest=largest,numerical_excess_gain=gain,seconds=time.monotonic()-t)
  print('joint',row,flush=True);result.append(row)
  if not moved:break
 for i in range(len(o.ops)):
  P,N=o.neighbors(i);assert contained(o.spans[o.ops[i][2]],o.frames[i]);assert all(contained(F,o.frames[i]) for F in P);assert all(contained(o.frames[i],F) for F in N)
 return result
