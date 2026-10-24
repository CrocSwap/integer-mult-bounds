"""Joint shared-native-map and common-hyperplane cut, including center gauges."""
import quotient_cut as Q
import center_model as C
import graph as S
import inspect,json,time,sys
from collections import defaultdict
from pathlib import Path
contracts=defaultdict(dict)
fullpins=set()
for u,v,op,B in Q.warps:
 if len(S.frames[Q.NF[u]])==9:fullpins.update((u,v))
 d=len(S.frames[Q.NF[u]])
 if d in (0,9):continue
 a,b=(u,v) if op>0 else (v,u)
 key=(frozenset(S.spaces[Q.NF[a]]),frozenset(S.spaces[Q.NF[b]]))
 contracts[abs(op)].setdefault(key,[]).append((a,b))
assert set(contracts)==set(range(1,73))
for op,ps in contracts.items():
 assert len(ps)<=2,(op,len(ps))
 if len(ps)==2:assert min(len(A) for A,B in ps)==2

def native_constraints(l,active,pins,imp):
 for u,v,op,B in Q.warps:
  if active[u] and active[v]:imp.extend([(u,v),(v,u)])
  elif active[u]:pins.add(u)
  elif active[v]:pins.add(v)
 for op,ps in contracts.items():
  if len(ps)<2:continue
  pairs=sorted(ps,key=lambda ab:len(ab[0]));(A,B),(U,V)=pairs
  a=next(iter(A-{0}));b=next(iter(B-{0}));inside=a in U;assert inside==(b in V)
  if inside and bool((a&l).bit_count()%2)!=bool((b&l).bit_count()%2):
   for u,v in ps[(U,V)]:
    if active[u]:pins.add(u)
    if active[v]:pins.add(v)

def engine():
 ns=Q.__dict__.copy();ns.update(fixed=(Q.fixed-C.owned)|fullpins,paid=[*Q.paid,*C.centeredges],EXTRA=C.EXTRA,native_constraints=native_constraints)
 src=inspect.getsource(Q.solve).replace('imp=[];unary=','imp=list(EXTRA);unary=').replace('P=Counter({8:8});H=Counter()','P=Counter();H=Counter()')
 a=src.index(' for u,v,g,B in warps:');b=src.index(' for r,u,v,g in helpers:',a);src=src[:a]+' native_constraints(l,active,pins,imp)\n'+src[b:]
 exec(src,ns);return ns['solve']
if __name__=='__main__':
 f=engine();best=0;start=time.monotonic();records=[]
 for l in range(1,512):
  r=f(l,.9969782);chosen=set(r['chosen']);r['centers']=[8-int(g['high'][-1] in chosen) for g in C.groups];records.append({k:v for k,v in r.items() if k not in ('chosen','original_nodes')})
  if r['energy']<best-1e-8:
   best=r['energy'];(Path(__file__).parent/'joint-best.json').write_text(json.dumps(r,indent=2)+'\n');print('BEST',{k:v for k,v in r.items() if k not in ('chosen','original_nodes')},flush=True)
  if l%64==0:print('PROGRESS',l,'seconds',time.monotonic()-start,'best',best,flush=True)
 (Path(__file__).parent/'joint-screen.json').write_text(json.dumps(records,indent=2)+'\n');print('DONE',time.monotonic()-start,'best',best,flush=True)
