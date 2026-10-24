"""Global monotone hyperplane retiming of the native word; discovery only."""
import graph as S
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow,breadth_first_order
import json,time,sys
N=len(S.NF);parent=list(range(N))
def find(x):
 while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
 return x
def union(x,y):
 x,y=find(x),find(y)
 if x!=y:parent[y]=x
# Keep every chronological zero-length edge: a changed gauge may create paid work.
roots=sorted({find(i) for i in range(N)});idx={r:i for i,r in enumerate(roots)};ids=[idx[find(i)] for i in range(N)]
NF=[S.NF[r] for r in roots];fixed={ids[x] for x in S.fixed|set(S.starts[:224])|set(S.ends[:224])}
paid=[(ids[u],ids[v],r) for u,v,r,I in S.paid]
warps=[(ids[u],ids[v],g,B) for u,v,g,B in S.warp]
helpers=[(r,ids[u],ids[v],g) for r,u,v,g,I in S.helpers]
H0=Counter(g for r,u,v,g in helpers);P0=S.original.copy();SCALE=100000;INF=1000000000

def solve(l,t):
 active=[bool(S.restrict(l,S.frames[f])) for f in NF];pins=set(fixed);imp=[];unary=[0.]*(len(NF))
 power=[0.]+[i**t for i in range(1,11)]
 for u,v,r in paid:
  if active[u]:
   assert active[v]
   imp.append((v,u));d=power[r+1]-power[r];unary[u]+=d;unary[v]-=d
  elif active[v]:unary[v]+=power[r-1]-power[r]
 for u,v,g,B in warps:
  a=S.restrict(l,B);b=S.restrict(l,[S.image(S.Gs[g],x) for x in B])
  assert bool(a)==active[u] and bool(b)==active[v]
  if a and b:
   if a==b:imp.extend([(u,v),(v,u)])
   else:pins.update((u,v))
  elif a:pins.add(u)
  elif b:pins.add(v)
 for r,u,v,g in helpers:
  if active[u]:
   assert active[v];imp.append((v,u));d=power[g+1]-power[g];unary[u]-=d;unary[v]+=d
  elif active[v]:unary[v]+=power[g]-power[g-1]
 ren={i:j+2 for j,i in enumerate(i for i,a in enumerate(active) if a and i not in pins)};n=len(ren)+2
 budget=sum(max(0.,-unary[i]) for i in ren);scale=min(10**9,int((2**30)/(budget+1)));hard=sum(max(0,-round(unary[i]*scale)) for i in ren)+1
 rows=[];cols=[];caps=[]
 def arc(u,v,c):
  if c:rows.append(u);cols.append(v);caps.append(c)
 hardarcs=set()
 for u,v in imp:
  u=ren.get(u,0);v=ren.get(v,0)
  if u and v:hardarcs.add((v,u))
  elif u:hardarcs.add((0,u))
 for u,v in hardarcs:arc(u,v,hard)
 for i,j in ren.items():
  c=round(unary[i]*scale)
  if c>=0:arc(0,j,c)
  else:arc(j,1,-c)
 graph=coo_matrix((np.array(caps,dtype=np.int64),(rows,cols)),shape=(n,n)).tocsr();assert not len(graph.data) or max(graph.data)<2**31;flow=maximum_flow(graph,0,1)
 residual=graph-flow.flow;residual.data=(residual.data>0).astype(np.int8);residual.eliminate_zeros()
 reachable=set(breadth_first_order(residual,0,directed=True,return_predecessors=False));chosen={i for i,j in ren.items() if j not in reachable}
 assert not(chosen & pins)
 assert all(u not in chosen or v in chosen for u,v in imp)
 P=Counter({8:8});H=Counter()
 for u,v,r in paid:
  rank=r+int(u in chosen)-int(v in chosen)
  assert rank>=0
  if rank:P[rank]+=1
 for r,u,v,g in helpers:
  rank=g+int(u in chosen)-int(v in chosen)
  assert rank>0
  H[rank]+=1
 energy=sum((P[r]-P0[r])*power[r] for r in set(P)|set(P0))-sum((H[g]-H0[g])*power[g] for g in set(H)|set(H0))
 return {'l':l,'t':t,'energy':energy,'paid':dict(sorted(P.items())),'helpers':dict(sorted(H.items())),'chosen':sorted(chosen),'original_nodes':sorted(i for i in range(N) if ids[i] in chosen)}
if __name__=='__main__':
 t=float(sys.argv[1]) if len(sys.argv)>1 else .996;best=0;start=time.monotonic();allr=[]
 print('compressed_nodes',len(NF),'paid',len(paid),flush=True)
 for l in range(1,1<<S.n):
  r=solve(l,t);allr.append({k:v for k,v in r.items() if k not in ('chosen','original_nodes')})
  if r['energy']<best-1e-8:
   best=r['energy'];(Path(__file__).parent/f'quotient-best-{t}.json').write_text(json.dumps(r,indent=2)+'\n');print('BEST',{k:v for k,v in r.items() if k not in ('chosen','original_nodes')},flush=True)
  if l%64==0:print('progress',l,'seconds',time.monotonic()-start,'best',best,flush=True)
 (Path(__file__).parent/f'quotient-screen-{t}.json').write_text(json.dumps(allr,indent=2)+'\n');print('DONE',time.monotonic()-start,'best',best,flush=True)
