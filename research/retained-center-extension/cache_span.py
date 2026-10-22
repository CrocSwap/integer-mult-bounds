#!/usr/bin/env python3
"""Exact scalar-bundle cache experiment; Apache-2.0, OpenAI assistance."""
import json
import sys
from hashlib import sha256
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=HERE.parents[1]/'research/joint-helper-lattice/CONTROLLER.json'
pin=next(r for r in json.loads((HERE/'SOURCES.json').read_text())['files'] if r['path']=='research/joint-helper-lattice/CONTROLLER.json')
if sha256(p.read_bytes()).hexdigest()!=pin['sha256']:raise ValueError('Changed controller source')
d=json.loads(p.read_text());m=32
rows=[{(i,0,0):Q(1)} for i in range(m)];basis={};rank=0;receipts=[]
def add(a,b,c=1):
 out=dict(a)
 for k,v in b.items():
  v=out.get(k,0)+c*v
  if v:out[k]=v
  else:out.pop(k,None)
 return out
def shifted(a,q=0,mask=0):
 out={}
 for (j,e,s),v in a.items():
  if s&mask:raise ValueError('Repeated stage factor')
  out[j,e+q,s|mask]=v
 return out
def reduce(a):
 a=dict(a)
 while a:
  p=min(a)
  if p not in basis:return a
  a=add(a,basis[p],-a[p])
 return a
def keep(a):
 a=reduce(a)
 if a:
  p=min(a);basis[p]={k:v/a[p] for k,v in a.items()}
for row in rows:keep(row)
for idx,e in enumerate(d['physical_events']):
 op=e[0]
 if op in ['LOCAL','QUERY_SHEAR']:
  _,stage,pair,back=e;x,y=2*pair,2*pair+1
  if back:x,y=y,x
  query=shifted(rows[x],q=1 if back else -1)
  new=reduce(query);receipts.append({'stage':stage,'full':op=='LOCAL','backward':back,'cache_available_in_bundle_span':not new,'span_rank':len(basis),'new_terms':len(new)})
  keep(query)
  rows[y]=add(rows[y],query,-1 if back else 1)
  if op=='LOCAL':
   for r in [x,y]:rows[r]=shifted(rows[r],mask=1<<stage)
 elif op=='IDLE':
  _,pair,ss=e;mask=sum(1<<s for s in ss)
  for r in [2*pair,2*pair+1]:rows[r]=shifted(rows[r],mask=mask)
 elif op=='ADD':
  _,dst,src,*c=e;rows[dst]=add(rows[dst],rows[src],c[0] if c else 1)
 elif op in ['SWAP','SIGNED_SWAP']:
  _,a,b=e;rows[a],rows[b]=rows[b],{k:v*(-1 if op=='SIGNED_SWAP' else 1) for k,v in rows[a].items()}
 else:raise ValueError(op)
 for row in rows:keep(row)
result={'status':'FINITE_SCALAR_BUNDLE_CACHE_SCREEN_NO_REUSE_FOUND',
        'pairs':16,'query_stages':len(receipts),'full_stages':sum(r['full'] for r in receipts),
        'available_full_stages':[r['stage'] for r in receipts if r['full'] and r['cache_available_in_bundle_span']],
        'scope':'Rational scalar span of all previous query demands and external main snapshots; independent Laurent stage variables; common bundle projection. No physical or port-dependent cache impossibility claim.',
        'stages':receipts}
if result['available_full_stages']:raise ValueError('Changed cache screen result')
if sys.argv[1:]==['--write']:(HERE/'CACHE-SPAN.json').write_text(json.dumps(result,indent=2)+'\n')
else:
 if sys.argv[1:]:raise ValueError('Unknown arguments')
 if result!=json.loads((HERE/'CACHE-SPAN.json').read_text()):raise ValueError('Changed exact cache receipt')
print(json.dumps({k:v for k,v in result.items() if k!='stages'},sort_keys=True))
