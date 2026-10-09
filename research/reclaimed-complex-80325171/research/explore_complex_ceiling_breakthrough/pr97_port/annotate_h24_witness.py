import sys,os
if sys.flags.optimize or os.environ.get("PYTHONOPTIMIZE"):
 raise RuntimeError("Optimized Python is not permitted for scientific checks")
"""Add replay hints from existing literal promise/reuse records; no scientific resynthesis."""
from pathlib import Path
from collections import Counter
import gzip,json,hashlib,time,resource
root=Path(__file__).resolve().parent;src=root/'H24_EVENTS.jsonl.gz';dst=root/'H24_EVENTS_CLAIMED.jsonl.gz'
start=time.monotonic();last={};claim={};counts=Counter();complete=False
for i,line in enumerate(gzip.open(src,'rt')):
 r=json.loads(line);kind=r[0];counts[kind]+=1
 if kind=='add':last[r[1]]=i
 elif kind=='reuse':
  k=last[r[1]];assert k not in claim;claim[k]=0
 elif kind=='promise':
  _,uid,slot,node,*_=r
  if slot in last:
   k=last[slot]
   if k in claim:assert claim[k]==node
   else:claim[k]=node
 elif kind=='block':
  for slot in r[1]:
   if slot in last:assert last[slot] in claim;del last[slot]
 elif kind=='activate':
  assert r[1] not in last
 elif kind=='footer':complete=True
assert complete and len(claim)==counts['add']
with gzip.open(dst,'wt',compresslevel=1,newline='\n') as f:
 for i,line in enumerate(gzip.open(src,'rt')):
  r=json.loads(line)
  if r[0]=='header':
   r[1]['annotation_source_sha256']=hashlib.sha256(src.read_bytes()).hexdigest();r[1]['annotation_program_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();r[1]['signal_claims']='Every add appends expected canonical graph-node ID,0 for zero, derived from literal subsequent promise/reuse. Blocks carry labels; inject is source ID+1. Hints must be independently checked.';r[1]['reverse_recipe']='Original inverse echo at complementary middle frames; see H24_FRAME_CONTRACT.md. No transpose construction used.'
  elif r[0]=='add':r.append(claim[i])
  elif r[0]=='inject':r.append(r[2]+1)
  f.write(json.dumps(r,separators=(',',':'))+'\n')
result=dict(status='Complete gzip readback and deterministic signal-hint annotation; not independent physical replay',events=dict(counts),annotated_additions=len(claim),input_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),output_bytes=dst.stat().st_size,seconds=time.monotonic()-start,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(root/'H24_ANNOTATION_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
