"""Finite supplier registry; signatures are derived from actual source artifacts.
New heterogeneous composition code. Underlying suppliers credited in SOURCES.json.
"""
from pathlib import Path
import json,gzip,hashlib
def read(p):
 p=Path(p);return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def content_sha(p):
 p=Path(p);return hashlib.sha256(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes()).hexdigest()
def load(index):
 index=Path(index).resolve();spec=read(index);out={};root=index.parent
 for name,rel in spec['variants'].items():
  d=(root/rel).resolve();assert root in d.parents
  c=read(d/'CANONICAL-WORD.json.gz');p=read(d/'LOCAL-PROGRAMS.json.gz');k=read(d/'LOCAL-CHECKS.json');r=read(d/'INDEPENDENT-LOCAL-REPLAY.json');a=read(d/'RESIDUAL-ADAPTERS.json');phase=read(d/'CLIFFORD-REVIEW.json')
  assert (c['v'],c['h'],c['R'])==(112,9,504)
  assert r['canonical_word_sha256']==sha(d/'CANONICAL-WORD.json.gz') and r['local_programs_sha256']==sha(d/'LOCAL-PROGRAMS.json.gz')
  assert r['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
  assert phase['canonical_word_sha256']==sha(d/'CANONICAL-WORD.json.gz') and phase['recipe_sha256']==sha(d/'CLIFFORD-RECIPES.json') and phase['all_child_equalities_include_global_phase']
  assert set(p)==set(k)=={'forward','backward'}
  for o,events in p.items():
   assert hashlib.sha256(json.dumps(events,sort_keys=True,separators=(',',':')).encode()).hexdigest()==k[o]['sha256']
   assert r['local'][o]['all_exact_columns']==728 and r['local'][o]['private_work_erased']
   assert k[o]['paid_profile']==r['paid_profiles'][o]
  widths=[9-len(c['frames'][f])for f in c['start'][224:]];assert len(widths)==504
  starts=set(c['start'][224:])-{0};assert set(map(int,a['recipes']))==starts
  for f in starts:
   rec=a['recipes'][str(f)];assert rec['vectors']==c['frames'][f] and rec['rank']==9-len(c['frames'][f]) and rec['entrance_rank']==len(c['frames'][f])
  out[name]=dict(directory=d,canon=c,programs=p,checks=k,replay=r,widths=widths,phase=phase,adapters=a)
 assert out and len(spec['selection'])==72 and set(spec['selection'])<=set(out)
 common=next(iter(out.values()))['canon']
 for z in out.values():assert z['canon']['ports']==common['ports'] and z['canon']['centers']==common['centers']
 return spec,out
def bindings(index,registry):
 root=Path(index).resolve().parent;files={}
 for name,z in registry.items():
  for f in ['CANONICAL-WORD.json.gz','FULL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','RESIDUAL-ADAPTERS.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json']:
   p=z['directory']/f
   if f=='CLIFFORD-REVIEW.json':
    receipt=read(p);receipt.pop('seconds',None)
    digest=hashlib.sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest()
   else:digest=sha(p)
   files[p.relative_to(root).as_posix()]=digest
 return files
