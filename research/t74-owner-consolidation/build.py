#!/usr/bin/env python3
"""Build the source-bound four owner relocations on PR2435."""
import argparse,gzip,hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
SOURCE='research/gmx-t74-borrow43-handoff'
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def write(p,x):
 b=json.dumps(x,sort_keys=True,separators=(',',':')).encode();p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def need(ok,msg):
 if not ok:raise ValueError(msg)
def relocate(source):
 from collections import defaultdict
 fill=read(source/'new/borrow-fill/FILL.json.gz');plan=read(source/'PLAN.json')
 dispatch={(s,r):pid for s,r,pid in read(source/'DISPATCH.json')}
 providers=read(source/'new/BORROW-PROVIDERS.json');moves=read(HERE/'MOVES.json')
 need(len(moves)==4,'four explicit moves');byrole={(m['time'],m['helper']):m for m in moves}
 bins=defaultdict(list);seen=set()
 for t,h,r,c,port,off in fill['rows']:
  width=providers[dispatch[tuple(plan['order'][t])]]['widths'][h]
  key=(r,c,port)
  if (t,h) in byrole:
   move=byrole[t,h];need(list(key)==move['src'] and width==move['width'],'source role and width')
   key=tuple(move['dst']);seen.add((t,h))
  bins[key].append((t,h,width,off))
 need(seen==set(byrole),'complete four-move identity')
 rows=[]
 for (r,c,port),values in sorted(bins.items()):
  offset=0
  for t,h,width,_ in sorted(values,key=lambda v:(v[3],v[0],v[1])):
   rows.append([t,h,r,c,port,offset]);offset+=width
 return dict(columns=fill['columns'],dispatch_overrides=[],rows=sorted(rows))

def build(work):
 work.mkdir(parents=True,exist_ok=False)
 need(hashlib.sha256((HERE/'source-pr2435.tar.gz').read_bytes()).hexdigest()==read(HERE/'SOURCE-PR.json')['archive_sha256'],'immutable source archive hash')
 with tarfile.open(HERE/'source-pr2435.tar.gz') as t:
  need(all((m.isfile() or m.isdir()) and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in t),'archive members')
  t.extractall(work,filter='data')
 p=work/SOURCE
 need(hashlib.sha256((p/'MANIFEST.json').read_bytes()).hexdigest()=='03dfba2bd0c537df784d87ab8fd0f9aca07c1542d1640739eab25e00996c9c67','PR2435 manifest pin')
 manifest=read(p/'MANIFEST.json')
 need({x.relative_to(p).as_posix() for x in p.rglob('*') if x.is_file() and x!=p/'MANIFEST.json'}==set(manifest),'source file set')
 for name,h in manifest.items():need(hashlib.sha256((p/name).read_bytes()).hexdigest()==h,'source '+name)
 # Frozen source stays separately available; only this generated derivative changes.
 original=work/'source';shutil.copytree(p,original)
 for name,h in read(HERE/'OVERRIDES.json').items():
  target=p/name;data=target.read_bytes() if target.exists() else None
  need((hashlib.sha256(data).hexdigest() if data else None)==h['old_sha256'],'override source '+name)
  data=(HERE/'overrides'/name).read_bytes();need(hashlib.sha256(data).hexdigest()==h['new_sha256'],'override bytes '+name)
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 write(p/'new/borrow-fill/FILL.json.gz',relocate(original))
 for script,args in [('reconstruct.py',['--out',str(work/'owners')]),('lift_parent.py',['--owners',str(work/'owners'),'--out',str(work/'parent-data')])]:
  subprocess.run([sys.executable,'-B',str(p/script),*args],check=True)
 for name in ['PLAN.json','OWNERS.json.gz','DISPATCH.json','PROFILE.json','CONSTRUCTION.json','GLOBAL-TEMPLATE.json.gz','SPEC.json']:shutil.copy2(work/'parent-data'/name,p/name)
 for name in ['PLAN.json','PROFILE.json','SPEC.json']:shutil.copy2(work/'parent-data'/name,p/'new'/name)
 for name in ['SPEC.json','new/SPEC.json']:
  spec=read(p/name);need(spec['geometry']['replicas']==74 and spec['geometry']['charged_prefix_bits']==2048,'unchanged geometry')
  spec['outer_refinement']=dict(endpoint_digits=24,grid_digits=18,margin_digits=28,bootstrap_steps=12)
  spec['expected']['live']=66304;write(p/name,spec)
 return p
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();print(build(a.work.resolve()))
