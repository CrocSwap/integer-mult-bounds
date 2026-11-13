"""Materialize an exact local multi-peer bypass nomination."""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
from collections import Counter
import json,gzip,sys
from hashlib import sha256
SOURCE='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
HERE=Path(__file__).resolve().parent

def construct(old,h=None):
 if h is None:h=json.loads((HERE/"WITNESS.json").read_text())
 assert sha256(json.dumps(old,sort_keys=True,separators=(",",":")).encode()).hexdigest()==SOURCE
 p=old['program'];n=old['public'];r=h['role'];a,f,b=h['low'],h['middle'],h['high'];clock=h['clock'];block=h['block'];touched=set(h['touched']);skip=set(block)
 v={int(q):Q(x)for q,x in h['ingress'].items()};d={int(q):Q(x)for q,x in h['delta'].items()};inv={int(q):Q(x)for q,x in h['inverse'].items()}
 out=deepcopy(old);active=old['initial']+[None]*old['owned_fields'];tape=[]
 def span(b):
  s={0}
  for x in b:s|={x^y for y in tuple(s)}
  return s
 spaces=list(map(span,old['frames']))
 def append(e):
  op,q=e[:2]
  if op=='MOVE':
   x,y,o=e[2:];assert active[q]==x and o==(q>=n)and(spaces[x]<spaces[y]or o and spaces[y]<spaces[x]);active[q]=y
  elif op=='INIT':assert q>=n and active[q] is None;active[q]=e[2]
  elif op=='CLEAR':assert q>=n and active[q]==e[2];active[q]=None
  else:
   for u in e[1:3]if op in('ADD','COPY')else[e[1]]:
    if u in touched and active[u]!=e[-1]:append(['MOVE',u,active[u],e[-1],False])
    assert active[u]==e[-1]
  tape.append(e)
 for t,e in enumerate(p):
  if t==clock:
   aux=next(q for q in range(n,len(active))if active[q]is None)
   for q,x in v.items():append(['ADD',q,r,str(x),a])
   append(['INIT',aux,f])
   for j in block:
    event=p[j].copy()
    for k in(1,2)if event[0]=='ADD'else(1,):
     if event[k]==r:event[k]=aux
    append(event)
   append(['CLEAR',aux,f])
   # Correct non-bypassed outputs before using the inverse readout.
   for q,x in d.items():
    if q!=r:append(['ADD',q,r,str(-x),b])
   if inv[r]!=1:append(['SCALE',r,str(1/inv[r]),b])
   for q,x in inv.items():
    if q!=r:append(['ADD',r,q,str(-x/inv[r]),b])
  if t in skip or e[0]=='MOVE'and e[1]in touched:continue
  append(e)
 for q in touched:
  if active[q]!=old['final'][q]:append(['MOVE',q,active[q],old['final'][q],False])
 assert active==old['final']+[None]*old['owned_fields'];out['program']=tape;return out
