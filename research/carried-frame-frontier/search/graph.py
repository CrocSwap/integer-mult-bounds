import sys,importlib.util,json
from collections import Counter
from pathlib import Path
RELAXED=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
path=ROOT/'research/native-frame-carrying-swaps/verify.py'
spec=importlib.util.spec_from_file_location('source_swaps',path)
V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
c=V.c;n=c['h'];frames=c['frames'];spaces=V.spaces
p,_,_=V.construct(V.a['programs']['forward'])
def image(G,x):
 out=0
 for i,g in enumerate(G):
  if x>>i&1:out^=g
 return out
def inverse(G):
 im={image(G,x):x for x in range(1<<n)}
 return [im[1<<i] for i in range(n)]
Gs={v['op']:v['G_columns'] for v in c['warps']}
Gs.update({-k:inverse(G) for k,G in list(Gs.items())})
NF=[];fixed=set();paid=[];warp=[];current=[];starts=[]
def node(f,pin=False):
 i=len(NF);NF.append(f)
 if pin:fixed.add(i)
 return i
def bridge(r,v):
 u=current[r];a=NF[u];b=NF[v]
 assert spaces[a]<=spaces[b],(r,a,b)
 rank=len(frames[b])-len(frames[a]);paid.append((u,v,rank,()));current[r]=v
for f in c['start']:
 current.append(node(f));starts.append(current[-1])
current.append(None)
for e in p:
 if e[0]=='climb':continue
 if e[0]=='weighted_swap':
  _,d,s,*_=e;current[d],current[s]=current[s],current[d]
 elif e[0]=='scalar':
  g=e[1]
  if g[0]=='scale':continue
  roles=g[1:3] if g[0] in ('add','copy') else g[1:2]
  v=node(e[2])
  if g[0]=='clear':current[632]=v;continue
  for typ,r in roles:
   r=r+(632 if typ=='C' else 0)
   if g[0]=='copy' and typ=='C':current[r]=v
   else:bridge(r,v)
 elif e[0]=='center':
  _,r,a,b,rank=e;r+=632;u=current[r]
  assert NF[u]==a
  v=node(b)
  if spaces[a]<=spaces[b]:paid.append((u,v,rank,()))
  else:
   assert spaces[b]<=spaces[a];paid.append((v,u,rank,()))
  current[r]=v
 elif e[0]=='warp':
  r=e[1][1];u=current[r]
  if NF[u]!=e[3]:
   a=node(e[3]);bridge(r,a);u=a
  v=node(e[4]);warp.append((u,v,e[2],tuple(frames[e[3]])));current[r]=v
 elif e[0] in ('adapter','residual_adapter'):pass
ends=[]
for r,f in enumerate(c['final']):
 v=node(f);bridge(r,v);ends.append(v)
helpers=[]
for r in range(224,632):
 a,b=c['start'][r],c['final'][r];g=len(frames[b])-len(frames[a]);helpers.append((r,starts[r],ends[r],g,()))
original=Counter(r for u,v,r,I in paid if r)
assert original==Counter({int(k):v for k,v in c['local_profile'].items()}),(original,c['local_profile'])
def restrict(l,B):return sum(((l&x).bit_count()%2)<<i for i,x in enumerate(B))
print(json.dumps({'nodes':len(NF),'paid_edges':len(paid),'warps':len(warp),'helpers':Counter(g for r,u,v,g,I in helpers),'paid':original}),flush=True)
