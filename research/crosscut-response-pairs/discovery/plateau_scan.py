#!/usr/bin/env python3
"""Discover simultaneous legal retimings of equal-frame connected gate plateaus."""
import argparse, json, math, time
import numpy as np
from sympy import Matrix
from pathlib import Path
from array import array
from collections import defaultdict, Counter
ap=argparse.ArgumentParser(); ap.add_argument('export',type=Path); ap.add_argument('lead',type=Path);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--extremal',action='store_true');args=ap.parse_args()
t0=time.time(); X,L=args.export,args.lead
frames=json.loads((X/'frames.json').read_text())['frames'];frames={int(k):v for k,v in frames.items()}
if (L/'COHORT249-FRAMES.json').exists():frames.update({int(k):v for k,v in json.loads((L/'COHORT249-FRAMES.json').read_text()).items()})
st=json.loads((X/'249-states.json').read_text());n,v=st['n'],st['v']
initial={int(k):f for k,f in json.loads((L/'COHORT249-INITIAL.json').read_text()).items()}
raw=array('i');raw.frombytes((L/'COHORT249-RECORDS.bin').read_bytes())
events=[tuple(raw[k:k+6]) for k in range(0,len(raw),6) if raw[k]]
N=len(events); parent=list(range(N)); size=[1]*N
def root(x):
 while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
 return x
def union(a,b):
 a,b=root(a),root(b)
 if a==b:return
 if size[a]<size[b]:a,b=b,a
 parent[b]=a;size[a]+=size[b]
uses=defaultdict(list);gf={};fixed=set()
for i,(op,a,b,c,f,z) in enumerate(events):
 if op==1:
  gf[i]=f
  for s in (a,b):uses[s].append((i,f))
  if a==n or b==n:fixed.add(i)
 else:
  fixed.add(i); uses[a].append((i,c));uses[b].append((i,f))
for s,chain in uses.items():
 for (a,af),(b,bf) in zip(chain,chain[1:]):
  if a not in fixed and b not in fixed and af==bf:union(a,b)
components=defaultdict(list)
for i in gf:
 if i not in fixed:components[root(i)].append(i)
boundaries=defaultdict(list)
for s,chain in uses.items():
 if s==n:continue
 for j,(i,f) in enumerate(chain):
  if i in fixed:continue
  r=root(i)
  if j==0 or root(chain[j-1][0])!=r or chain[j-1][0] in fixed:
   pf=chain[j-1][1] if j else initial[s]
   boundaries[r].append((s,-1,pf))
  if j+1==len(chain) or root(chain[j+1][0])!=r or chain[j+1][0] in fixed:
   nf=chain[j+1][1] if j+1<len(chain) else st['final'][str(s)]
   boundaries[r].append((s,1,nf))
d={f:rec['dim'] for f,rec in frames.items()}; cache={}
def sub(a,b):
 if a==b:return True
 key=(a,b)
 if key not in cache:
  cache[key]=d[a]<=d[b] and all(sum(x*y for x,y in zip(row,col))==0 for row in frames[a]['B'] for col in frames[b]['A'])
 return cache[key]
def price(k):return k*math.log(120/k) if k else 0
def hist(edges,f):
 h=Counter()
 for s,side,g in edges:
  k=(d[f]-d[g]) if side==-1 else (d[g]-d[f]);assert k>=0
  if k:h[k]+=1
 return h
candidates=[]; dimension_open=0
newframes={}; extcache={}; rankcache={}; nextframe=max(frames)+10000; degenerate=Counter()
def modular_rank(rows,stop):
 basis={}
 for row in rows:
  a=np.array(row,dtype=np.int64)%101
  for pivot in sorted(basis):
   if a[pivot]:a=(a-a[pivot]*basis[pivot])%101
  nz=np.flatnonzero(a)
  if len(nz):
   p=int(nz[0]);a=(a*pow(int(a[p]),-1,101))%101;basis[p]=a
   if len(basis)>=stop:return len(basis)
 return len(basis)
def clear_row(row):
 from functools import reduce
 from math import lcm,gcd
 den=reduce(lcm,(int(x.q) for x in row),1);v=[int(x*den) for x in row];g=reduce(gcd,(abs(x) for x in v),0)
 if g:v=[x//g for x in v]
 first=next((x for x in v if x),0)
 return [-x for x in v] if first<0 else v
def extremal(fs,upper,current):
 global nextframe
 key=(upper,tuple(sorted(fs)),current)
 if key in extcache:return extcache[key]
 typ='A' if upper else 'B';stop=24-d[current] if upper else d[current]
 rows=[row for g in fs for row in frames[g][typ]]
 if modular_rank(rows,stop)>=stop:extcache[key]=None;return None
 if not rows:b=[]
 else:b=[list(r) for r in Matrix(rows).rowspace()]
 if len(b)>=stop:extcache[key]=None;return None
 ann=[list(r) for r in Matrix(b if b else [[0]*24]).nullspace()]
 B,A=(ann,b) if upper else (b,ann)
 B=[clear_row(r) for r in B];A=[clear_row(r) for r in A];q=len(B)
 # Exact nondegeneracy in the fixed rational quadratic form 9I-J.
 G=Matrix([[9*sum(x*y for x,y in zip(r,s))-sum(r)*sum(s) for s in B] for r in B])
 if q and G.det()==0:
  degenerate[(upper,d[current],q)]+=1
  form=9*Matrix.eye(24)-Matrix.ones(24,24)
  F=Matrix(frames[current]['B']); U=Matrix(B)
  if upper:
   # Orthogonally split off the already legal frame and retain a maximal
   # nondegenerate complement of the remaining symmetric bilinear form.
   R=U-U*form*F.T*(F*form*F.T).inv()*F if len(F.tolist()) else U
   rr=R.rowspace();R=Matrix.vstack(*rr) if rr else Matrix.zeros(0,24)
   S=R*form*R.T;chosen=[];remaining=list(range(S.rows))
   while remaining:
    pivot=next((i for i in remaining if S[i,i]),None)
    if pivot is not None:ii=[pivot]
    else:
     pp=next(((i,j) for i in remaining for j in remaining if i<j and S[i,j]),None)
     if pp is None:break
     ii=list(pp)
    chosen+=ii;remaining=[i for i in remaining if i not in ii]
    if remaining:
     Sch=S.extract(remaining,remaining)-S.extract(remaining,ii)*S.extract(ii,ii).inv()*S.extract(ii,remaining)
     for a,i in enumerate(remaining):
      for b,j in enumerate(remaining):S[i,j]=Sch[a,b]
   B=F.tolist()+[R.row(i).tolist()[0] for i in chosen]
  else:
   while True:
    U=Matrix(B);G=U*form*U.T;rad=G.nullspace()
    if not rad:break
    rv=rad[0].T*U
    add=next((r for r in F.tolist() if (rv*form*Matrix(r))[0]),None)
    assert add is not None,'current frame must repair radical'
    B.append(add)
  B=[clear_row(r) for r in B];q=len(B)
  if q==d[current]:extcache[key]=None;return None
  A=[clear_row(list(r)) for r in Matrix(B).nullspace()]
  assert (Matrix(B)*form*Matrix(B).T).det()!=0
 f=nextframe;nextframe+=1;frames[f]=dict(B=B,A=A,dim=q);d[f]=q;newframes[f]=frames[f];extcache[key]=f
 return f
for r,gg in components.items():
 f=gf[gg[0]];edges=boundaries[r];prev={g for s,side,g in edges if side==-1};nxt={g for s,side,g in edges if side==1}
 low=max(d[g] for g in prev);high=min(d[g] for g in nxt)
 if low==high:continue
 dimension_open+=1
 oldH=hist(edges,f);oldcost=sum(c*price(k) for k,c in oldH.items())
 # Existing adjacent boundary frames produce portable witnesses with no new bases.
 possible=prev|nxt
 if args.extremal:
  for upper,fs in [(False,prev),(True,nxt)]:
   g=extremal(fs,upper,f)
   if g is not None:possible=possible|{g}
 for g in possible:
  if d[g]==d[f] or not low<=d[g]<=high:continue
  if not all(sub(p,g) for p in prev) or not all(sub(g,q) for q in nxt):continue
  hh=hist(edges,g);cost=sum(c*price(k) for k,c in hh.items());gain=oldcost-cost
  if gain<=1e-10:continue
  delta=Counter(hh);delta.subtract(oldH);delta={k:c for k,c in delta.items() if c}
  candidates.append(dict(component=r,gates=gg,old_frame=f,new_frame=g,old_dim=d[f],new_dim=d[g],entropy_gain=gain,delta=delta,roles=sorted({s for s,side,g in edges}),boundaries=edges))
candidates.sort(key=lambda r:-r['entropy_gain']);out=dict(status='DISCOVERY_ONLY_EXISTING_FRAME_PLATEAU_CANDIDATES',components=len(components),dimension_open=dimension_open,candidates=candidates,newframes=newframes,degenerate={str(k):v for k,v in degenerate.items()},seconds=time.time()-t0)
args.output.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('candidates','newframes')}),flush=True)
print('candidates',len(candidates),'top',[(len(q['gates']),q['old_dim'],q['new_dim'],q['entropy_gain'],q['delta']) for q in candidates[:20]],flush=True)
