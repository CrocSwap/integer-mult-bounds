#!/usr/bin/env python3
"""Recover pinned PR2462, then construct a separate eight-alias derivative."""
import argparse,gzip,hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def write(p,x):
 b=json.dumps(x,sort_keys=True,separators=(',',':')).encode();p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def extract(archive,dst):
 with tarfile.open(archive) as t:
  need(all((m.isfile() or m.isdir()) and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in t),'archive members')
  t.extractall(dst,filter='data')
def prepare(work):
 work.mkdir(parents=True,exist_ok=False);pin=read(HERE/'SOURCE-PR.json');archive=ROOT/pin['base_archive'];overlay=HERE/'pr2462-overlay.tar.gz'
 need(sha(archive)==pin['base_archive_sha256'] and sha(overlay)==pin['overlay_sha256'],'source archive pins')
 extract(archive,work);p=work/'research/gmx-t74-borrow43-handoff'
 for name in pin['deleted']:(p/name).unlink()
 extract(overlay,p);need(sha(p/'MANIFEST.json')==pin['manifest_sha256'],'PR2462 manifest')
 manifest=read(p/'MANIFEST.json');need({f.relative_to(p).as_posix() for f in p.rglob('*') if f.is_file() and f!=p/'MANIFEST.json'}==set(manifest),'source file set')
 for name,h in manifest.items():need(sha(p/name)==h,'source '+name)
 return p

def build(work):
 source=prepare(work/'source');p=work/'derivative';shutil.copytree(source,p)
 for name,h in read(HERE/'VENDOR.json').items():need(sha(HERE/name)==h,'vendor '+name)
 for name,h in read(HERE/'OVERRIDES.json').items():
  need(sha(source/name)==h['old_sha256'],'override source '+name)
  need(sha(HERE/Path(name).name)==h['new_sha256'],'override bytes '+name)
 from generate import make
 for tag in ['base','extra']:
  w=make(source,work/'generated',tag)
  need(all(g[0]=='add' and 112<=g[1]<224 and g[2] in w['centers'] for g in w['cut']),'cut consists only of centre-to-target additions (PR2478 guard)')
  need(read(work/f'generated/eight-alias-{tag}.json.gz')==read(HERE/f'evidence/eight-alias-{tag}.json.gz'),'deterministic word '+tag)
  shutil.copy2(work/f'generated/eight-alias-{tag}.json.gz',p/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz')
 for src,dst in [('eight-fill.json.gz','new/borrow-fill/FILL.json.gz'),('eight-order.json','new/borrow-fill/ORDER.json'),('eight-providers.json','new/BORROW-PROVIDERS.json')]:shutil.copy2(HERE/'evidence'/src,p/dst)
 shutil.copy2(HERE/'rebind.py',p/'new/rebind.py')
 shutil.copy2(HERE/'independent_core.py',p/'independent_core.py')
 for script,args in [('reconstruct.py',['--out',work/'owners']),('lift_parent.py',['--owners',work/'owners','--out',work/'parent-data'])]:subprocess.run([sys.executable,'-B',str(p/script),*map(str,args)],check=True)
 for n in ['PLAN.json','OWNERS.json.gz','DISPATCH.json','PROFILE.json','CONSTRUCTION.json','GLOBAL-TEMPLATE.json.gz','SPEC.json']:shutil.copy2(work/'parent-data'/n,p/n)
 for n in ['PLAN.json','PROFILE.json','SPEC.json']:shutil.copy2(work/'parent-data'/n,p/'new'/n)
 for name in ['SPEC.json','new/SPEC.json']:
  spec=read(p/name);need(spec['geometry']['replicas']==74 and spec['geometry']['charged_prefix_bits']==2048,'geometry')
  spec['outer_refinement']=dict(endpoint_digits=24,grid_digits=18,margin_digits=28,bootstrap_steps=12);spec['expected']['live']=66304;write(p/name,spec)
 return p
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();print(build(a.work.resolve()))
