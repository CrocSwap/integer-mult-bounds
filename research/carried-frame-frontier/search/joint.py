import cut as Q,graph as S
from collections import defaultdict
import inspect,json,time
from pathlib import Path
from output import OUTPUT
contracts=defaultdict(dict);fullpins=set()
for u,v,op,B in Q.warps:
 if len(S.frames[Q.NF[u]])==9:fullpins.update((u,v))
 d=len(S.frames[Q.NF[u]])
 if d in (0,9):continue
 a,b=(u,v) if op>0 else (v,u)
 key=(frozenset(S.spaces[Q.NF[a]]),frozenset(S.spaces[Q.NF[b]]))
 contracts[abs(op)].setdefault(key,[]).append((a,b))
assert set(contracts)==set(range(1,73))
assert all(len(ps)<=2 for ps in contracts.values())
def native_constraints(l,active,pins,imp):
 for u,v,op,B in Q.warps:
  if active[u] and active[v]:imp.extend([(u,v),(v,u)])
  elif active[u]:pins.add(u)
  elif active[v]:pins.add(v)
 for op,ps in contracts.items():
  if len(ps)<2:continue
  (A,B),(U,V)=sorted(ps,key=lambda ab:len(ab[0]))
  assert len(A)==2
  a=next(iter(A-{0}));b=next(iter(B-{0}));inside=a in U
  assert inside==(b in V)
  if inside and bool((a&l).bit_count()%2)!=bool((b&l).bit_count()%2):
   for u,v in ps[(U,V)]:
    if active[u]:pins.add(u)
    if active[v]:pins.add(v)
ns=Q.__dict__.copy();ns.update(fixed=Q.fixed|fullpins,native_constraints=native_constraints)
src=inspect.getsource(Q.solve)
a=src.index(' for u,v,g,B in warps:');b=src.index(' for r,u,v,g in helpers:',a)
src=src[:a]+' native_constraints(l,active,pins,imp)\n'+src[b:]
exec(src,ns);solve=ns['solve']
if __name__=='__main__':
 best=0;start=time.monotonic();records=[]
 for l in range(1,512):
  r=solve(l,.99697822419);records.append({k:v for k,v in r.items() if k not in ('chosen','original_nodes')})
  if r['energy']<best-1e-9:
   best=r['energy'];(OUTPUT/'relaxed-joint-best.json').write_text(json.dumps(r,indent=2)+'\n');print('BEST',records[-1],flush=True)
  if l%64==0:print('progress',l,'seconds',time.monotonic()-start,'best',best,flush=True)
 (OUTPUT/'relaxed-joint-screen.json').write_text(json.dumps(records,indent=2)+'\n');print('DONE',time.monotonic()-start,'best',best,flush=True)
