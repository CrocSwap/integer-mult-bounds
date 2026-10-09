# Copyright 2026 icekylinx. Apache-2.0.
# Prepared with OpenAI GPT-6 Astra and Codex assistance; see NOTICE.
#!/usr/bin/env python3
"""Construct a signed deferred-readout schedule from one concrete matched M.
Readout supports use an overapproximation (union through transpose M), so every
selected orthogonality/chain condition is conservative over Q. Coefficients
are the exact finite rational matrix J M, specified without dense expansion.
"""
from pathlib import Path
from collections import defaultdict,Counter
from itertools import combinations
import json,argparse
from .binary import load
from .lift import contained,perp,basis

def run(path,matchfile,annfile,liftfile):
 h,v,n,q,args,core,cover,roots,kind,active,oldrank,types=load(path)
 mt=json.loads(Path(matchfile).read_text());arcs=dict(mt['matching_arcs']);ann=json.loads(Path(annfile).read_text());lift=json.loads(Path(liftfile).read_text())
 nr=[h-len(a) if a is not None else 0 for a in ann];full=(1<<h)-1
 order=sorted((x for x in range(1,n) if active[x]),key=lambda x:(oldrank[x],x))
 uses=defaultdict(list)
 for x in order:
  if args[2*x]:
   for j in (0,1):uses[args[2*x+j]].append(2*x+j)
 for j,x in enumerate(roots):uses[x].append((1<<31)|j)
 incoming={u:d for d,u in arcs.items()};assign={};sources={};ops=[];R=0
 for x in order:
  if args[2*x]:
   aa,bb=args[2*x],args[2*x+1]
   p,o=assign[2*x],assign[2*x+1]
   if x in arcs:
    u=arcs[x];value=roots[u&0x7fffffff] if u>>31 else args[2*(u//2)+(u&1)]
    if value==aa:p,o=o,p
    else:assert value==bb
    assert u not in assign;assign[u]=o
   ops.append((p,o,x))
  else:p=R;R+=1;sources[x]=p
  free=[u for u in uses[x] if u not in incoming]
  assert free
  for j,u in enumerate(free):
   assert u not in assign
   if j==0:assign[u]=p
   else:
    s=R;R+=1;assign[u]=s;ops.append((s,p,x))
 assert R==mt['R'],(R,mt['R'])
 rootroles=[assign[(1<<31)|j] for j in range(q)]
 prev=[-1]*R;pred=[];first=[None]*R
 for i,(a,b,x) in enumerate(ops):
  pred.append((prev[a],prev[b]));prev[a]=prev[b]=i
  if first[a] is None:first[a]=x
  if first[b] is None:first[b]=x
 centerroles=[rootroles[j] for j in range(q) if kind[j]]
 stack=[prev[s] for s in centerroles if prev[s]>=0];phase=set()
 while stack:
  i=stack.pop()
  if i in phase:continue
  phase.add(i);stack.extend(p for p in pred[i] if p>=0)
 touched=set(sources.values())
 for i in phase:touched.update(ops[i][:2])
 triples=list(combinations(range(h),3));tid={sum(1<<j for j in t):i for i,t in enumerate(triples)}
 co=[0]*R
 for j,(x,s,k) in enumerate(zip(roots,rootroles,kind)):
  if k:co[s]|=(1<<v)-1
  else:co[s]|=1<<tid[core[x]|(full^cover[x])]
 for a,b,x in reversed(ops):co[b]|=co[a]
 return dict(ops=ops,sources=sources,rootroles=rootroles,phase1=sorted(phase))
