"""Optional basin escape discovery, not an admitted native supplier."""
import graph as S,cut as Q,joint as J
from collections import Counter,defaultdict
from pathlib import Path
from output import OUTPUT
import json,time,sys
def basis(A):
 B=[];V={0}
 for x in sorted(A):
  if x not in V:B.append(x);V|={v^x for v in tuple(V)}
 assert V==set(A)
 return B
def extend(E,A):
 V=S.V.space(E)
 for x in sorted(A):
  if x not in V:E.append(x);V|={v^x for v in tuple(V)}
 return E
def registry(A):
 A=set(A);key=frozenset(A)
 if key not in SPACEIDS:
  SPACEIDS[key]=len(S.frames);S.frames.append(basis(A));S.spaces.append(set(A))
 return SPACEIDS[key]
SPACEIDS={frozenset(v):i for i,v in enumerate(S.spaces)}
def contracts(NF):
 out=defaultdict(dict)
 for u,v,op,_ in Q.warps:
  if op<0:u,v=v,u
  A=frozenset(S.spaces[NF[u]]);B=frozenset(S.spaces[NF[v]])
  assert len(A)==len(B)
  if len(A) not in (1,512):out[abs(op)].setdefault((A,B),[]).append((u,v))
 return out
def maps(NF):
 gs={}
 for op,cs in contracts(NF).items():
  pairs=sorted(cs,key=lambda ab:len(ab[0]));assert len(pairs)<=2
  A,B=pairs[0]
  if len(pairs)==1:E=basis(A);F=basis(B)
  else:
   U,V=pairs[1];assert len(A)==2
   a=next(iter(A-{0}));b=next(iter(B-{0}));assert (a in U)==(b in V)
   if a in U:E=extend(basis(A),U);F=extend(basis(B),V)
   else:E=extend(basis(U),A);F=extend(basis(V),B)
  E=extend(E,range(512));F=extend(F,range(512))
  gi=S.inverse(E);G=[S.image(F,x) for x in gi]
  assert len(set(S.image(G,x) for x in range(512)))==512
  assert all({S.image(G,x) for x in U}==set(V) for U,V in pairs)
  gs[op]=G
 for op in range(1,73):
  if op not in gs:gs[op]=S.Gs[op]
 gs.update({-op:S.inverse(G) for op,G in list(gs.items())})
 return gs
def state(NF):
 gs=maps(NF);paid=[];H=[];P=Counter();HH=Counter()
 for u,v,_,_ in S.paid:
  assert S.spaces[NF[u]]<=S.spaces[NF[v]]
  r=len(S.frames[NF[v]])-len(S.frames[NF[u]])
  paid.append((u,v,r))
  if r:P[r]+=1
 for r,u,v,_,_ in S.helpers:
  assert S.spaces[NF[u]]<S.spaces[NF[v]]
  g=len(S.frames[NF[v]])-len(S.frames[NF[u]]);HH[g]+=1;H.append((r,u,v,g))
 warps=[(u,v,op,tuple(S.frames[NF[u]])) for u,v,op,_ in Q.warps]
 return dict(NF=NF,paid=paid,warps=warps,helpers=H,P0=P,H0=HH,gs=gs)
def solvefn(st):
 cs=contracts(st['NF']);fullpins={z for u,v,op,B in st['warps'] if len(B)==9 for z in (u,v)}
 def native_constraints(l,active,pins,imp):
  for u,v,op,B in st['warps']:
   if active[u] and active[v]:imp.extend([(u,v),(v,u)])
   elif active[u]:pins.add(u)
   elif active[v]:pins.add(v)
  for op,ps in cs.items():
   if len(ps)<2:continue
   (A,B),(U,V)=sorted(ps,key=lambda ab:len(ab[0]));assert len(A)==2
   a=next(iter(A-{0}));b=next(iter(B-{0}));inside=a in U;assert inside==(b in V)
   if inside and bool((a&l).bit_count()%2)!=bool((b&l).bit_count()%2):
    for u,v in ps[U,V]:
     if active[u]:pins.add(u)
     if active[v]:pins.add(v)
 ns=Q.__dict__.copy();ns.update(st);ns.update(native_constraints=native_constraints,fixed=Q.fixed|fullpins)
 exec(J.src,ns)
 return ns['solve']
def apply(NF,cut):
 chosen=set(cut['chosen']);l=cut['l']
 return [registry(x for x in S.spaces[f] if (l&x).bit_count()%2==0) if i in chosen else f for i,f in enumerate(NF)]
def energy(st,t=.99697822419):
 return sum(n*r**t for r,n in st['P0'].items())-sum(n*r**t for r,n in st['H0'].items())
if __name__=='__main__':
 original=state(Q.NF[:]);base=energy(original)
 seed=json.loads((OUTPUT/'landscape-seed.json').read_text());NF=apply(Q.NF,seed);st=state(NF)
 print('SEED',seed['cap'],seed['l'],'energy',energy(st)-base,flush=True)
 history=[seed];start=time.monotonic()
 for roundno in range(5):
  f=solvefn(st);best=None
  for l in range(1,512):
   r=f(l,.99697822419)
   if r['energy'] < -1e-9 and (best is None or r['energy']<best['energy']):best=r
  if best is None:print('LOCAL_MINIMUM',roundno,'total_energy',energy(st)-base,flush=True);break
  NF=apply(NF,best);st=state(NF);history.append(best)
  print('ROUND',roundno,'direction',best['l'],'gain',best['energy'],'total',energy(st)-base,'seconds',time.monotonic()-start,flush=True)
  payload=dict(history=history,NF=NF,frames=S.frames,maps=st['gs'],paid=st['P0'],helpers=st['H0'],energy=energy(st)-base)
  (OUTPUT/'landscape-best.json').write_text(json.dumps(payload,indent=2)+'\n')
