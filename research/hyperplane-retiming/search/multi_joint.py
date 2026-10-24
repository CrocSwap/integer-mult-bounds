"""Two/three-dimensional coordinated deletions with shared-map reconstruction constraints."""
import multi_cut as M
import joint_cut as J
import quotient_cut as Q
import center_model as C
import graph as S
from pathlib import Path
from types import SimpleNamespace
import inspect,json,time,random

def constraints(W,a,pins,imp):
 for u,v,op,B in Q.warps:
  x,y=a[u],a[v]
  if x and y and x==y:imp.extend([(u,v),(v,u)])
  else:
   if x:pins.add(u)
   if y:pins.add(v)
 for op,ps in J.contracts.items():
  if len(ps)<2:continue
  (A,B),(U,V)=sorted(ps,key=lambda ab:len(ab[0]));x=next(iter(A-{0}));y=next(iter(B-{0}));inside=x in U;assert inside==(y in V)
  ax=any((x&l).bit_count()%2 for l in W);ay=any((y&l).bit_count()%2 for l in W)
  if inside and ax!=ay:
   for u,v in ps[U,V]:
    if a[u]:pins.add(u)
    if a[v]:pins.add(v)

def engine():
 ns=M.__dict__.copy();ns['Q']=SimpleNamespace(**dict(Q.__dict__,fixed=(Q.fixed-C.owned)|J.fullpins,paid=[*Q.paid,*C.centeredges]));ns['EXTRA']=C.EXTRA;ns['native_constraints']=constraints
 src=inspect.getsource(M.solve).replace('imp=[];unary=','imp=list(EXTRA);unary=').replace('P=Counter({8:8});H=Counter()','P=Counter();H=Counter()')
 a=src.index(' for j,(u,v,g,B) in enumerate(Q.warps):');b=src.index(' for r,u,v,g in Q.helpers:',a);src=src[:a]+' native_constraints(W,a,pins,imp)\n'+src[b:];exec(src,ns);return ns['solve']
if __name__=='__main__':
 rng=random.Random(20261023);cases={M.rb(B) for B in S.frames if len(B)==2}
 planes=[(a,b) for a in range(1,512) for b in range(a+1,512) if b<(a^b)];rng.shuffle(planes);cases.update(M.rb(W) for W in planes[:2048]);cases=list(sorted(cases))
 extra=set()
 while len(extra)<512:
  W=M.rb(rng.sample(range(1,512),3))
  if len(W)==3:extra.add(W)
 cases+=sorted(extra);f=engine();best=0;start=time.monotonic();records=[]
 for i,W in enumerate(cases):
  r=f(W,.9969782);chosen=set(r['chosen']);r['centers']=[8-len(M.rb(S.restrict(l,S.frames[Q.NF[g['high'][-1]]]) for l in W))*int(g['high'][-1] in chosen) for g in C.groups];records.append({k:v for k,v in r.items() if k not in ('chosen','original_nodes')})
  if r['energy']<best-1e-8:
   best=r['energy'];(Path(__file__).parent/'multi-joint-best.json').write_text(json.dumps(r,indent=2)+'\n');print('BEST',i,{k:v for k,v in r.items() if k not in ('chosen','original_nodes')},flush=True)
  if i%128==0:print('PROGRESS',i,len(cases),'seconds',time.monotonic()-start,'best',best,flush=True)
 (Path(__file__).parent/'multi-joint-screen.json').write_text(json.dumps(records,indent=2)+'\n');print('DONE',len(cases),time.monotonic()-start,'best',best,flush=True)
