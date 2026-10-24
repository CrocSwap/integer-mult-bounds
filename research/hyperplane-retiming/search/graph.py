"""Exploratory exact-graph phase-flow discovery. No admission claimed."""
import gzip,json,math,time,sys
from collections import Counter,defaultdict
from pathlib import Path
D=Path(__file__).resolve().parent.parent
w=json.loads(gzip.decompress((D/'inputs/pr4610-round3-word.json.gz').read_bytes())); c=w['canonical'];p=w['programs']['forward'];n=c['h'];frames=c['frames']
def span(B):
 s={0}
 for b in B:s|={x^b for x in tuple(s)}
 return s
spaces=list(map(span,frames));basis_cache={}
def basis(S):
 key=frozenset(S)
 if key not in basis_cache:
  B=[];s={0}
  for x in sorted(S):
   if x not in s:B.append(x);s|={y^x for y in tuple(s)}
  basis_cache[key]=tuple(B)
 return basis_cache[key]
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
for f in c['start']:current.append(node(f));starts.append(current[-1])
def bridge(r,v):
 u=current[r];a=NF[u];b=NF[v];I=basis(spaces[a]&spaces[b]);rank=len(frames[a])+len(frames[b])-2*len(I)
 paid.append((u,v,rank,I));current[r]=v
for e in p:
 if e[0]=='climb':continue
 if e[0]=='scalar':
  g=e[1];roles=g[1:3] if g[0] in ('add','copy') else g[1:2]
  v=node(e[2],any(r[0]!='L' for r in roles))
  for r in roles:
   if r[0]=='L':bridge(r[1],v)
 elif e[0]=='warp':
  r=e[1][1];u=current[r]
  if NF[u]!=e[3]:
   a=node(e[3]);bridge(r,a);u=a
  v=node(e[4]);warp.append((u,v,e[2],tuple(frames[e[3]])));current[r]=v
 elif e[0] in ('adapter','residual_adapter'):
  fixed.add(current[e[2]])
ends=[]
for r,f in enumerate(c['final']):
 v=node(f);bridge(r,v);ends.append(v)
helpers=[]
for r in range(224,632):
 a,b=c['start'][r],c['final'][r];I=basis(spaces[a]&spaces[b]);g=len(frames[a])+len(frames[b])-2*len(I);helpers.append((r,starts[r],ends[r],g,I))
original=Counter(r for u,v,r,I in paid if r);original[8]+=8
assert original==Counter({int(k):v for k,v in c['local_profile'].items()}),(original,c['local_profile'])
print(json.dumps({'nodes':len(NF),'paid_edges':len(paid),'warps':len(warp),'helpers':Counter(g for r,u,v,g,I in helpers),'paid':original}),flush=True)

def restrict(l,B):return sum(((l&x).bit_count()%2)<<i for i,x in enumerate(B))
