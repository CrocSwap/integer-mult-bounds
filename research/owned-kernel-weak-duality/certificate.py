"""Exact full-source signed-cut certificate support. Apache-2.0.
JoyboyBrian, with substantial OpenAI Codex assistance.
Retains Cinna Davis / 1337isnot1337's source model, without modifying it.
"""
from pathlib import Path
from collections import defaultdict, deque
from fractions import Fraction as F
from functools import lru_cache
import hashlib, json, sys
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
Z = (0,) * 10
D = 10 ** 60
C = F(302177585, 100000000000)
def need(ok, message):
    if not ok: raise ValueError(message)
def pins():
    manifest = json.loads((P / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], 'source byte mismatch: ' + row['path'])
def source():
    pins()
    sys.path.insert(0, str(ROOT / 'research/owned-kernel-shared-map'))
    import shared_maps as S
    model = S.build(S.payload(), [1])
    frozen = set(model['fixed'])
    variables = {n: i for i, n in enumerate(n for n in range(2, len(model['nodes'])) if n not in frozen and model['old_spaces'][model['nodes'][n]] != model['new_spaces'][model['nodes'][n]])}
    unary=defaultdict(lambda:[0]*10);pairs=defaultdict(lambda:[0]*10)
    def add(dst,terms,sign):
     for rank,c in terms:dst[rank]+=sign*c
    def table(a,b,rs,sign):
     if a==b:
      if a in variables:add(unary[variables[a]],[(rs[3],1),(rs[0],-1)],sign)
      return
     x,y=variables.get(a),variables.get(b)
     if x is not None:add(unary[x],[(rs[1],1),(rs[0],-1)],sign)
     if y is not None:add(unary[y],[(rs[2],1),(rs[0],-1)],sign)
     if x is not None and y is not None:add(pairs[min(x,y),max(x,y)],[(rs[3],1),(rs[1],-1),(rs[2],-1),(rs[0],1)],sign)
    for _,a,b,r in model['edges']:table(a,b,r,1)
    for _,a,b,r in model['helpers']:table(a,b,r,-1)
    return S, model, variables, dict(unary), {k: tuple(v) for k,v in pairs.items() if any(v[1:])}
def expminus(a):
 term=F(1);s=term
 for k in range(1,32):
  term=term*(-a)/k;s+=term
  if k==30:upper=s
 return s,upper
bounds=[(0,0),(D,D)]
for r in range(2,10):
 z=F(r-1,r+1);t=z;s=F(0)
 for j in range(400):s+=t/(2*j+1);t*=z*z
 lo=2*s;hi=lo+2*t/(801*(1-z*z))
 low=expminus(C*hi)[0]*r;up=expminus(C*lo)[1]*r
 bounds.append((low.numerator*D//low.denominator,-((-up.numerator*D)//up.denominator)))
Z=(0,)*10
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def neg(a):return tuple(-x for x in a)
@lru_cache(None)
def sign(a):
 if not any(a[1:]):return 0
 lo=sum(v*bounds[i][0 if v>=0 else 1] for i,v in enumerate(a));hi=sum(v*bounds[i][1 if v>=0 else 0] for i,v in enumerate(a))
 if lo>0:return 1
 if hi<0:return -1
 raise ValueError(('undecided',a,lo,hi))

def network(n, unary, pairs):
    src=2*n;sink=src+1;graph=[[] for _ in range(sink+1)];original=[]
    def edge(a,b,c):
     if sign(c)<0:raise ValueError('negative capacity')
     original.append((a,len(graph[a]),b,c))
     graph[a].append([b,len(graph[b]),c]);graph[b].append([a,len(graph[a])-1,Z])
    def und(a,b,c):edge(a,b,c);edge(b,a,c)
    u=[tuple(2*v for v in unary.get(i,Z)) for i in range(n)]
    for (a,b),cs0 in pairs.items():
     cs=tuple(cs0);sg=sign(cs)
     if not sg:continue
     u[a]=add(u[a],cs);u[b]=add(u[b],cs)
     if sg<0:und(a,b,neg(cs));und(a+n,b+n,neg(cs))
     else:und(a,b+n,cs);und(a+n,b,cs)
    for i,v in enumerate(u):
     for j,c in ((i,v),(i+n,neg(v))):
      sg=sign(c)
      if sg>0:edge(j,sink,c)
      elif sg<0:edge(src,j,neg(c))
    return graph, original, src, sink

def generate(graph, src, sink):
    sys.setrecursionlimit(100000)
    flow=Z;rounds=0;augments=0
    while True:
     level=[-1]*len(graph);level[src]=0;q=deque([src])
     while q:
      a=q.popleft()
      for b,rev,c in graph[a]:
       if sign(c)>0 and level[b]<0:level[b]=level[a]+1;q.append(b)
     if level[sink]<0:break
     it=[0]*len(graph)
     def dfs(a,f):
      if a==sink:return f
      while it[a]<len(graph[a]):
       e=graph[a][it[a]];b,rev,c=e
       if sign(c)>0 and level[b]==level[a]+1:
        lim=c if f is None or sign(sub(c,f))<0 else f
        z=dfs(b,lim)
        if sign(z)>0:e[2]=sub(c,z);graph[b][rev][2]=add(graph[b][rev][2],z);return z
       it[a]+=1
      return Z
     while True:
      f=dfs(src,None)
      if sign(f)<=0:break
      flow=add(flow,f);augments+=1
     rounds+=1
    return flow, rounds, augments

def checked_flow(arcs, flows, n):
    need(len(arcs) == len(flows), 'all directed arcs required')
    balance = [Z for _ in range(2*n+2)]
    for (a, _, b, cap), raw in zip(arcs, flows):
        need(type(raw) is list and len(raw)==10 and all(type(v) is int for v in raw), 'typed integer flow vector')
        f=tuple(raw)
        need(sign(f)>=0 and sign(sub(cap,f))>=0, 'flow capacity violation')
        balance[a]=sub(balance[a],f);balance[b]=add(balance[b],f)
    def zero(v): return not any(v[1:]) # 0^p is exactly zero
    need(all(zero(v) for v in balance[:2*n]), 'flow conservation')
    need(zero(add(balance[-2],balance[-1])), 'terminal flow conservation')
    # Baseline literal lift z_i=0, z_(n+i)=1, source=1, sink=0.
    side=lambda i: n<=i<=2*n
    cut=Z
    for a,_,b,cap in arcs:
        if side(a) and not side(b): cut=add(cut,cap)
    need(zero(sub(balance[-1],cut)), 'flow does not saturate baseline cut')
    return list(cut)
