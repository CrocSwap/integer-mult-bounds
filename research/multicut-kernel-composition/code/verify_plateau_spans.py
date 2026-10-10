#!/usr/bin/env python3
"""Exact defining-integer source span audit for the frozen changed ADDs."""
import argparse,json,time,hashlib,sys
from pathlib import Path
from array import array
if not __debug__:raise SystemExit('assertions are required')
assert sys.byteorder=='little' and array('i').itemsize==4
ap=argparse.ArgumentParser();ap.add_argument('export',type=Path);ap.add_argument('lead',type=Path);ap.add_argument('receipt',type=Path);args=ap.parse_args()
t=time.time();X,L=args.export,args.lead
frames={int(k):r for k,r in json.loads((X/'frames.json').read_text())['frames'].items()};frames.update({int(k):r for k,r in json.loads((L/'COHORT249-FRAMES.json').read_text()).items()})
st=json.loads((X/'249-states.json').read_text());n,v=st['n'],st['v'];initial={int(k):f for k,f in json.loads((L/'COHORT249-INITIAL.json').read_text()).items()};chi={s:frames[initial[s]]['B'][0] for s in range(v)}
assert all(frames[initial[s]]['dim']==1 for s in range(v))
receipt=json.loads(args.receipt.read_text());pairs=[(g,c['new_frame']) for c in receipt['selected'] for g in c['gates']];chosen=dict(pairs)
assert len(pairs)==len(chosen),'duplicate selected gates'
columns=[{i:1} if i<v else {} for i in range(n)];center=None;raw=array('i');raw.frombytes((L/'COHORT249-RECORDS.bin').read_bytes());ordinal=0;checked=0;sourcecache={};spans={}
assert hashlib.sha256(raw.tobytes()).hexdigest()==receipt['output_sha256'],'word/receipt mismatch'
assert len(raw)%6==0
for k in range(0,len(raw),6):
 op,a,b,c,f,z=raw[k:k+6]
 if not op:continue
 i=ordinal;ordinal+=1
 if i in chosen:assert op==1,'selected gate must be ADD'
 if op==2:assert center is None;center=a;continue
 if op==3:assert center==a;center=None;continue
 src=center if b==n else b;ca=columns[a]
 for s,x in columns[src].items():
  y=ca.get(s,0)+c*x
  if y:ca[s]=y
  else:ca.pop(s,None)
 if i in chosen:
  assert chosen[i]==f
  need=set()
  if not v<=a<2*v:need.update(ca)
  if not v<=b<2*v and b!=n:need.update(columns[b])
  for s in need:
   key=(f,s)
   if key not in sourcecache:sourcecache[key]=all(sum(x*y for x,y in zip(row,chi[s]))==0 for row in frames[f]['A'])
   assert sourcecache[key],(i,a,b,f,s)
  spans[i]=len(need);checked+=len(need)
assert center is None and len(spans)==len(chosen)
out=dict(status='PASS_EXACT_INTEGER_SOURCE_SPANS_FOR_CHANGED_PLATEAU_GATES',changed_gates=len(chosen),checked_operand_source_inclusions=checked,distinct_inclusions=len(sourcecache),spans=spans,seconds=time.time()-t)
(L/'PLATEAU-SOURCE-SPANS.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(chosen),checked,'seconds',time.time()-t,flush=True)
