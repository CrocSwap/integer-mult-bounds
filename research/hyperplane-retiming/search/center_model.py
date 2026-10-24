"""Explore center gauges jointly with persistent scalar contacts."""
import quotient_cut as Q
import graph as S
from pathlib import Path
import inspect,json,time,sys
owned=set();groups=[];pending=[];current=list(range(632));cursor=632
for e in S.p:
 if e[0]=='climb':continue
 if e[0]=='scalar':
  g=e[1];roles=g[1:3] if g[0] in ('add','copy') else g[1:2];v=cursor;cursor+=1
  if any(r[0]=='C' for r in roles):
   owned.add(v)
   if e[2]!=0:pending.append(v)
   else:groups[-1]['low'].append(v)
  for r in roles:
   if r[0]=='L':current[r[1]]=v
 elif e[0]=='warp':
  r=e[1][1];u=current[r]
  if S.NF[u]!=e[3]:u=cursor;cursor+=1
  current[r]=cursor;cursor+=1
 elif e[0]=='center':
  assert len(pending)==2
  groups.append({'high':pending,'low':[]});pending=[]
assert len(groups)==8 and all(len(g['low'])>=2 for g in groups)
EXTRA=[]
for g in groups:
 for side in ('high','low'):
  for v in g[side][1:]:EXTRA.extend([(g[side][0],v),(v,g[side][0])])
centeredges=[(g['low'][0],g['high'][-1],8) for g in groups]
