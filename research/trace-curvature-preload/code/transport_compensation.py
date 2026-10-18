"""Exact untouched-version compensation transport. CLI WORD NEW_DIR."""
import sys,json,gzip,copy,hashlib
from pathlib import Path
from collections import defaultdict
src,out=map(Path,sys.argv[1:]);assert not out.exists();w=json.loads(gzip.decompress(src.read_bytes()));z=copy.deepcopy(w);v=w['v'];n=2*v+w['R'];pending=defaultdict(list)
for f,t,ss in w['D']:
 assert not w['frames'][f]and v<=t<2*v
 for s in ss:assert s>=2*v;pending[s].append([f,t,[s]])
assert all(not v<=r<2*v for f,t,ss in w['A']for r in [t]+ss)
a=[];delayed=0
for e in w['A']:
 for r in [e[1]]+e[2]:
  if r in pending:a.extend(pending.pop(r));delayed+=1
 a.append(e)
assert not pending;z['D']=[];z['A']=a

def chain(q):
 hist=[[q['start'][r]]for r in range(n)]
 for sec in ('D','A','B','C'):
  for f,t,ss in q[sec]:
   for r in [t]+ss:
    if hist[r][-1]!=f:hist[r].append(f)
 for r in range(n):
  if hist[r][-1]!=q['final'][r]:hist[r].append(q['final'][r])
 return hist
assert chain(z)==chain(w)
def replay(q):
 row=[1<<i for i in range(n)]
 for sec in ('D','A','scatter','B','C'):
  if sec=='scatter':
   saved=[row[h]for h in q['ret']]
   for t,S in enumerate(q['scatter']):
    for h in S:row[v+t]^=saved[h]
  else:
   for f,t,ss in q[sec]:
    assert t not in ss and len(ss)==len(set(ss))
    for s in ss:row[t]^=row[s]
 return row
expected=[1<<i for i in range(n)]
for t in range(v):expected[v+t]^=1<<t
assert replay(w)==replay(z)==expected
out.mkdir();data=gzip.compress(json.dumps(z,sort_keys=True,separators=(',',':')).encode(),compresslevel=9,mtime=0);data=data[:9]+b'\xff'+data[10:];(out/'WORD.json.gz').write_bytes(data)
r=dict(status='PASS_EXACT_UNTOUCHED_VERSION_COMPENSATION_TRANSPORT',source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(data).hexdigest(),columns=n,dirty_helpers=w['R'],shifted_helper_reads=delayed,all_register_frame_chains_identical=True,complete_scalar_map_identical=True,scope='Concrete neutral application of exact version transport; no exponent or paid-moment improvement claimed. No phase or global native program replay claimed for this appendix word.')
(out/'TRANSPORT.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
