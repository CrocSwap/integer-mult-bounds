"""Fixed-native common-line extension discovery; exact rank tables."""
import landscape as L,cut as Q,graph as S
from collections import Counter
import numpy as np,json,time
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow,breadth_first_order
from pathlib import Path
from output import OUTPUT
def solve(st,w,t=.99697822419):
 NF=st['NF'];active=[w not in S.spaces[f] for f in NF];pins=set(Q.fixed);imp=[];unary=[0.]*(len(NF));power=[0.]+[i**t for i in range(1,11)]
 for u,v,r in st['paid']:
  if active[v]:
   assert active[u];imp.append((u,v));d=power[r+1]-power[r];unary[u]-=d;unary[v]+=d
  elif active[u]:unary[u]+=power[r-1]-power[r]
 for u,v,g,B in st['warps']:
  if active[u] and active[v]:
   Gw=S.image(st['gs'][g],w)
   if Gw in S.spaces[NF[v]] or (Gw^w) in S.spaces[NF[v]]:imp.extend([(u,v),(v,u)])
   else:pins.update((u,v))
  elif active[u]:pins.add(u)
  elif active[v]:pins.add(v)
 for r,u,v,g in st['helpers']:
  if active[v]:
   assert active[u];imp.append((u,v));d=power[g+1]-power[g];unary[u]+=d;unary[v]-=d
  elif active[u]:unary[u]+=power[g]-power[g-1]
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
 graph=coo_matrix((np.array(caps,dtype=np.int64),(rows,cols)),shape=(n,n)).tocsr();flow=maximum_flow(graph,0,1)
 residual=graph-flow.flow;residual.data=(residual.data>0).astype(np.int8);residual.eliminate_zeros()
 reachable=set(breadth_first_order(residual,0,directed=True,return_predecessors=False));chosen={i for i,j in ren.items() if j not in reachable}
 assert not(chosen&pins);assert all(u not in chosen or v in chosen for u,v in imp)
 P=Counter();H=Counter()
 for u,v,r in st['paid']:
  rank=r-int(u in chosen)+int(v in chosen);assert rank>=0
  if rank:P[rank]+=1
 for r,u,v,g in st['helpers']:
  rank=g-int(u in chosen)+int(v in chosen);assert rank>0;H[rank]+=1
 energy=sum((P[r]-st['P0'][r])*power[r] for r in set(P)|set(st['P0']))-sum((H[r]-st['H0'][r])*power[r] for r in set(H)|set(st['H0']))
 return dict(w=w,t=t,energy=energy,paid=dict(P),helpers=dict(H),chosen=sorted(chosen))
def apply(NF,r):
 chosen=set(r['chosen']);w=r['w']
 return [L.registry(S.spaces[f]|{x^w for x in S.spaces[f]}) if i in chosen else f for i,f in enumerate(NF)]
if __name__=='__main__':
 st=L.state(Q.NF[:]);st['gs']=S.Gs
 best=0;start=time.monotonic();records=[]
 for w in range(1,512):
  r=solve(st,w);records.append({k:v for k,v in r.items() if k!='chosen'})
  if r['energy']<best-1e-9:
   best=r['energy'];(OUTPUT/'extension-best.json').write_text(json.dumps(r,indent=2)+'\n');print('BEST',records[-1],flush=True)
  if w%64==0:print('progress',w,'seconds',time.monotonic()-start,'best',best,flush=True)
 (OUTPUT/'extension-screen.json').write_text(json.dumps(records,indent=2)+'\n');print('DONE',time.monotonic()-start,'best',best,flush=True)
