# Copyright 2026 icekylinx. Licensed under Apache-2.0.
# Adapted with AI assistance from the archived partial-swap research producer.
# Underlying circuit modules: jacklightChen/integer-mult-bounds, PR7
# commit 6725c6a17b17871a35353fd29157f4ed851bc114; original credits retained.
"""Backward positive labels only; the unused dense-macro candidate is omitted."""
import struct,array
from collections import deque
from .binary import read_array, write_array

def read(path):
 f=open(path,'rb');h,v,n,q=struct.unpack('<4I',f.read(16))
 def a(c,k):return read_array(f,c,k)
 args=a('I',2*n);core=a('Q',n);cover=a('Q',n);roots=a('I',q);kind=a('I',q);active=a('B',n)
 return h,v,n,q,args,core,cover,roots,kind,active

def run(path):
 h,v,n,q,args,core,cover,roots,kind,active=read(path);full=(1<<h)-1
 lookup={};group=[-1]*n;nodes=[]
 for x in range(1,n):
  if not active[x]:continue
  key=(core[x],cover[x]) if args[2*x] else ('source',x)
  if key not in lookup:lookup[key]=len(nodes);nodes.append([])
  g=lookup[key];group[x]=g;nodes[g].append(x)
 ng=len(nodes);pending=[0]*ng;forced=[0]*ng;graphs=[0]*ng;extra=[[] for _ in range(ng)]
 pairs=[];pairbit={}
 for a in range(h):
  for b in range(a+1,h):pairbit[(1<<a)|(1<<b)]=1<<len(pairs);pairs.append((a,b))
 for j,x in enumerate(roots):
  g=group[x];forced[g]|=core[x]
  if not kind[j]:bad=full^cover[x];assert bad.bit_count()==2;graphs[g]|=pairbit[bad]
 for x in range(1,n):
  if active[x] and args[2*x]:
   g=group[x]
   for y in args[2*x:2*x+2]:
    if group[y]!=g:pending[group[y]]+=1
 from pathlib import Path
 linkfile=Path(path+'.links')
 if not linkfile.exists():raise FileNotFoundError('Generate original matching dependencies first: '+str(linkfile))
 if linkfile.exists():
  raw=linkfile.read_bytes();nn,ne=struct.unpack_from('<2I',raw);assert nn==n
  for i in range(ne):
   a,b=struct.unpack_from('<2I',raw,8+8*i);ga,gb=group[a],group[b]
   if ga!=gb:pending[ga]+=1;extra[gb].append(ga)
 queue=deque(g for g in range(ng) if not pending[g]);seen=0
 while queue:
  g=queue.popleft();seen+=1;assert forced[g]
  for x in nodes[g]:
   if args[2*x]:
    for y in args[2*x:2*x+2]:
     a=group[y]
     if a!=g:
      forced[a]|=forced[g];graphs[a]|=graphs[g];pending[a]-=1
      if not pending[a]:queue.append(a)
  for a in extra[g]:
   forced[a]|=forced[g];graphs[a]|=graphs[g];pending[a]-=1
   if not pending[a]:queue.append(a)
 assert seen==ng
 cache={};newlabels={};newnodes=[];newranks=[];newgroup=[-1]*n
 def label(F,graph):
  key=(F,graph)
  if key in cache:return cache[key]
  adj=[[] for _ in range(h)];z=graph
  while z:
   low=z&-z;z-=low;a,b=pairs[low.bit_length()-1];assert not ((1<<a|1<<b)&F);adj[a].append(b);adj[b].append(a)
  color=[-1]*h;zero=0;comps=[]
  for a in range(h):
   if F>>a&1 or color[a]>=0:continue
   color[a]=0;todo=[a];parts=[0,0];bad=False
   while todo:
    b=todo.pop();parts[color[b]]|=1<<b
    for c in adj[b]:
     if color[c]<0:color[c]=color[b]^1;todo.append(c)
     elif color[c]==color[b]:bad=True
   if bad:zero|=parts[0]|parts[1]
   else:comps.append(tuple(parts))
  assert F.bit_count() in (1,2)
  out=(F,zero,tuple(comps));cache[key]=out;return out
 for old,xs in enumerate(nodes):
  if not args[2*xs[0]]:assert len(xs)==1;key=('source',xs[0]);r=1
  else:key=label(forced[old],graphs[old]);r=len(key[2]);assert r>=2
  if key not in newlabels:newlabels[key]=len(newnodes);newnodes.append([]);newranks.append(r)
  g=newlabels[key]
  for x in xs:newgroup[x]=g;newnodes[g].append(x)
 labpath=path+'.positive';fo=open(labpath,'wb');fo.write(struct.pack('<2I',h,n));rr=array.array('I',[0]*n);ff=array.array('Q',[0]*n);sy=array.array('b',[0]*(n*h));keylist=[None]*len(newlabels)
 for key,g in newlabels.items():keylist[g]=key
 for x in range(1,n):
  if not active[x]:continue
  g=newgroup[x];rr[x]=newranks[g];key=keylist[g]
  if key[0]=='source':F=core[x];comps=[]
  else:F=key[0];comps=key[2]
  ff[x]=F
  for i in range(h):
   if F>>i&1:sy[x*h+i]=1
  for j,(pos,neg) in enumerate(comps):
   for i in range(h):
    if pos>>i&1:sy[x*h+i]=j+2
    elif neg>>i&1:sy[x*h+i]=-(j+2)
 for z in (rr,ff,sy):write_array(fo,z)
 fo.close()
 return dict(h=h, nodes=n, forward_classes=ng, positive_classes=len(newnodes))
