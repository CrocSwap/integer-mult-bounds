"""Higher codimension common-kernel discovery; exact rank tables, approximate cuts."""
import cut as Q
import graph as S
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow,breadth_first_order
import json,time,sys,random
FIDS=sorted(set(Q.NF));restrict={(l,f):S.restrict(l,S.frames[f]) for l in range(1,512) for f in FIDS}
warpBs=[tuple(S.image(S.Gs[g],x) for x in B) for u,v,g,B in Q.warps]
wr={(l,j):S.restrict(l,B) for l in range(1,512) for j,B in enumerate(warpBs)}
def rb(rows):
 b={}
 for x in rows:
  for p,y in sorted(b.items(),reverse=True):
   if x>>p&1:x^=y
  if x:
   p=x.bit_length()-1
   for k,y in list(b.items()):
    if y>>p&1:b[k]=y^x
   b[p]=x
 return tuple(b[k] for k in sorted(b,reverse=True))
def solve(W,t=.996):
 rs={f:rb(restrict[l,f] for l in W) for f in FIDS};a=[len(rs[f]) for f in Q.NF];pins=set(Q.fixed);imp=[];unary=[0.]*(len(a));power=[0.]+[i**t for i in range(1,14)]
 for u,v,r in Q.paid:
  x,y=a[u],a[v];assert x<=y
  if x:
   imp.append((v,u));d=power[r+x]-power[r];unary[u]+=d;unary[v]+=power[r+x-y]-power[r+x]
  elif y:unary[v]+=power[r-y]-power[r]
 for j,(u,v,g,B) in enumerate(Q.warps):
  if a[u] and a[v]:
   if rs[Q.NF[u]]==rb(wr[l,j] for l in W):imp.extend([(u,v),(v,u)])
   else:pins.update((u,v))
  elif a[u]:pins.add(u)
  elif a[v]:pins.add(v)
 for r,u,v,g in Q.helpers:
  x,y=a[u],a[v];assert x<=y
  if x:
   imp.append((v,u));d=power[g+x]-power[g];unary[u]-=d;unary[v]-=power[g+x-y]-power[g+x]
  elif y:
   if g==y:pins.add(v)
   else:unary[v]+=power[g]-power[g-y]
 ren={i:j+2 for j,i in enumerate(i for i,x in enumerate(a) if x and i not in pins)};n=len(ren)+2;rows=[];cols=[];caps=[]
 def arc(u,v,c):
  if c:rows.append(u);cols.append(v);caps.append(c)
 for u,v in imp:
  u=ren.get(u,0);v=ren.get(v,0)
  if u and v:arc(v,u,Q.INF)
  elif u:arc(0,u,Q.INF)
 for i,j in ren.items():
  c=round(unary[i]*Q.SCALE)
  if c>=0:arc(0,j,c)
  else:arc(j,1,-c)
 graph=coo_matrix((np.array(caps,dtype=np.int64),(rows,cols)),shape=(n,n)).tocsr();flow=maximum_flow(graph,0,1);residual=graph-flow.flow;residual.data=(residual.data>0).astype(np.int8);residual.eliminate_zeros();reach=set(breadth_first_order(residual,0,directed=True,return_predecessors=False));chosen={i for i,j in ren.items() if j not in reach}
 assert not(chosen & pins);assert all(u not in chosen or v in chosen for u,v in imp)
 P=Counter();H=Counter()
 for u,v,r in Q.paid:
  rank=r+a[u]*int(u in chosen)-a[v]*int(v in chosen);assert rank>=0
  if rank:P[rank]+=1
 for r,u,v,g in Q.helpers:
  rank=g+a[u]*int(u in chosen)-a[v]*int(v in chosen);assert rank>0;H[rank]+=1
 energy=sum((P[r]-Q.P0[r])*power[r] for r in set(P)|set(Q.P0))-sum((H[g]-Q.H0[g])*power[g] for g in set(H)|set(Q.H0))
 return {'W':W,'energy':energy,'paid':dict(sorted(P.items())),'helpers':dict(sorted(H.items())),'chosen':sorted(chosen),'original_nodes':sorted(i for i in range(Q.N) if Q.ids[i] in chosen)}
