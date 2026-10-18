"""Bounded monotone lift search on R480; exact rational catalogue, floating discovery fee.
No physical or theorem claim until independent emitted operator admission.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,gzip,sys,math,time,copy,random
R=Path(__file__).resolve().parent;O=R/'bit510-sliced-minimal-frames';O.mkdir(exist_ok=False);t0=time.monotonic()
w=json.load(gzip.open(R/'bit510-observable-slice/WORD.json.gz'));lines=w['lines']
def rref(vs):
 b={}
 for row in vs:
  x=list(map(Q,row))
  for p,y in sorted(b.items()):
   if x[p]:a=x[p];x=[s-a*t for s,t in zip(x,y)]
  if any(x):
   p=next(j for j,a in enumerate(x)if a);a=x[p];x=[v/a for v in x]
   for q,y in list(b.items()):
    if y[p]:a=y[p];b[q]=[s-a*t for s,t in zip(y,x)]
   b[p]=x
 return b
def contains(b,row):
 x=list(map(Q,row))
 for p,y in sorted(b.items()):
  if x[p]:a=x[p];x=[s-a*t for s,t in zip(x,y)]
 return not any(x)
bs=[rref([lines[i]for i in f])for f in w['frames']];dim=[len(b)for b in bs];masks=[]
for f,b in zip(w['frames'],bs):
 closed={i for i,x in enumerate(lines)if contains(b,x)};assert set(f)==closed,'catalogue is not root-closed';masks.append(sum(1<<i for i in closed))
le=lambda a,b: masks[a]&masks[b]==masks[a]
N=2*w['v']+w['R'];nodes=[];chains=[[]for _ in range(N)];mutable=[]
def node(regs,frame,sec=None,idx=None):
 k=len(nodes);nodes.append(dict(regs=regs,F=frame,lo=frame,sec=sec,idx=idx))
 for r in regs:chains[r].append(k)
 if sec in ('A','B'):mutable.append(k)
 return k
for r,f in enumerate(w['start']):node([r],f)
for sec in ['D','A','B','C']:
 if sec=='B':
  for r in w['ret']:node([r],nodes[chains[r][-1]]['F'])
  for r in range(w['v'],2*w['v']):node([r],0)
 for i,(f,d,ss)in enumerate(w[sec]):node([d]+ss,f,sec,i)
for r,f in enumerate(w['final']):node([r],f)
prev={};nxt={}
for r,ch in enumerate(chains):
 for a,b in zip(ch,ch[1:]):prev[b,r]=a;nxt[a,r]=b
b=.001587447106092548;fee=lambda k:k*math.expm1(b*math.log(64/k)) if k else 0
def profile():
 h=Counter()
 for r,ch in enumerate(chains):
  for a,z in zip(ch,ch[1:]):
   fa,fz=nodes[a]['F'],nodes[z]['F'];assert le(fa,fz)
   if dim[fz]>dim[fa]:h[dim[fz]-dim[fa]]+=1
 return h
H0=profile();print('CATALOGUE',len(bs),'profile',dict(H0),'seconds',time.monotonic()-t0,flush=True)

from functools import lru_cache
original_count=len(masks);idx={m:f for f,m in enumerate(masks)}
@lru_cache(None)
def join(mask):
 basis=rref([lines[i]for i in range(len(lines))if mask>>i&1]);closed=sum(1<<i for i,x in enumerate(lines)if contains(basis,x))
 if closed not in idx:
  idx[closed]=len(masks);masks.append(closed);dim.append(len(basis));bs.append(basis)
 return idx[closed]
cur={};moves=[]
for k,z in enumerate(nodes):
 old=z['F']
 if z['sec']in ('A','B'):
  mask=0
  for r in z['regs']:mask|=masks[cur[r]]
  f=join(mask);assert le(f,old)
  if f!=old:moves.append(dict(section=z['sec'],index=z['idx'],old=old,new=f,old_rank=dim[old],new_rank=dim[f]));z['F']=f
 else:f=old
 for r in z['regs']:
  if r in cur:assert le(cur[r],f)
  cur[r]=f
H=profile();out=copy.deepcopy(w);out['frames']=[[i for i in range(len(lines))if m>>i&1]for m in masks]
for k in mutable:
 z=nodes[k];out[z['sec']][z['idx']][0]=z['F']
(O/'WORD.json.gz').write_bytes(gzip.compress(json.dumps(out,sort_keys=True,separators=(',',':')).encode(),mtime=0))
res=dict(status='COMPLETE_EXACT_CAUSAL_MINIMUM_FRAME_ASSIGNMENT',moves=moves,new_frames=len(masks)-original_count,baseline_chain_profile=dict(H0),new_chain_profile=dict(H),fee_delta=sum(fee(r)*n for r,n in H.items())-sum(fee(r)*n for r,n in H0.items()),seconds=time.monotonic()-t0,scope='Least rational span of every preceding operand frame at each A/B gate, with source starts, center cut and cleanup/final frames fixed. All newly needed root closures generated exactly. This is the least feasible frame assignment in subspace inclusion for this fixed chronological word, not a moment optimum. No new physical admission or kappa claimed.')
(O/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(res,flush=True)
