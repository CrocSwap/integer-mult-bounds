from pathlib import Path
import json,struct,hashlib
P=Path(__file__).resolve().parent;S=P/'signed-rerun'
events=list(struct.iter_unpack('<6i',(S/'signed-records.bin').read_bytes()))
decoder=json.loads((S/'decoder-and-dirt.json').read_text())
for t in range(120):
 row={120+t:1}
 for op,a,b,c,f,z in reversed(events):
  if op==1:
   row[b]=row.get(b,0)+c*row.get(a,0)
   if not row[b]:row.pop(b,None)
  elif op==2:
   row[a]=row.get(a,0)+row.get(b,0);row.pop(b,None)
   if not row[a]:row.pop(a,None)
  elif op==3:row.pop(b,None)
 want={120+t:1};want.update({int(k):v for k,v in decoder['M'][t].items()})
 assert row==want,t
r=dict(status='PASS_INDEPENDENT_ALL120_TARGET_ADJOINT_ROWS',checks=120,signed_sha256=hashlib.sha256((S/'signed-records.bin').read_bytes()).hexdigest())
(P/'ADJOINT.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
