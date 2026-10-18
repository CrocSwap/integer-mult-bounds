"""Portable exact theorem tests and finite frame-graph validation; no kappa audit."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
from collections import Counter
if not __debug__:raise SystemExit('Run with assertions enabled.')
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
p=Path(__file__).resolve().parent;o=a.out.resolve()
assert o!=p and p not in o.parents,'Output must be outside this package.'
assert not o.exists(),'Use a new output directory.'
manifest=json.loads((p/'MANIFEST.json').read_text(encoding='utf-8'))
files={f.relative_to(p).as_posix():f for f in p.rglob('*')if f.is_file()and '__pycache__'not in f.parts and f.name!='MANIFEST.json'}
assert set(files)==set(manifest)
def canon(f):
 b=f.read_bytes()
 return b.replace(b'\r\n',b'\n')if f.suffix in {'.py','.cpp','.hpp','.h','.md','.json','.txt','.sha256'}else b
for k,f in files.items():assert hashlib.sha256(canon(f)).hexdigest()==manifest[k],k
rows=(p/'data/flags.txt').read_text().splitlines();nf,nn,nr=map(int,rows[0].split());assert len(rows)==1+nf+nn
frames=[];dims=[]
for line in rows[1:1+nf]:
 z=list(map(int,line.split()));F=set(z[1:]);assert z[0]==len(z)-1==len(F)and 0 in F and all(0<=x<512 for x in F)
 basis={}
 for x in F:
  while x:
   k=x.bit_length()-1
   if k not in basis:basis[k]=x;break
   x^=basis[k]
 assert len(F)==2**len(basis)
 for b in basis.values():assert all((x^b)in F for x in F)
 frames.append(F);dims.append(len(basis))
info=json.loads((p/'data/FLAG-INPUT.json').read_text());assert len(info['refs'])==nn
last=[None]*nr;hist=Counter();edges=0;fixed=0
for i,line in enumerate(rows[1+nf:]):
 z=list(map(int,line.split()));fx,fi,n=z[:3];rs=z[3:];assert fx in (0,1)and 0<=fi<nf and len(rs)==n and len(set(rs))==n
 assert bool(fx)==(info['refs'][i][0]not in ('A','B'))
 fixed+=fx
 for reg in rs:
  assert 0<=reg<nr
  if last[reg]is not None:
   prev=last[reg];assert frames[prev]<=frames[fi],(i,reg)
   d=dims[fi]-dims[prev];edges+=1
   if d:hist[d]+=1
  last[reg]=fi
assert all(x is not None for x in last)
o.mkdir(parents=True)
subprocess.run([sys.executable,'-B',str(p/'code/exact_selftest.py'),'--output',str(o/'SELFTEST.json')],check=True)
checked=json.loads((o/'SELFTEST.json').read_text());recorded=json.loads((p/'evidence/EXACT-SELFTEST.json').read_text());assert checked==recorded
res=dict(status='PASS_EXACT_TOOLKIT_CHECKS',files=len(files),frame_nodes=nn,registers=nr,distinct_frames=nf,fixed_nodes=fixed,register_edges=edges,edge_histogram=dict(sorted(hist.items())),selftest=checked,numerical_gain_claimed=False,scope='Frame dataset and exact finite tests only; no replay of the scalar suppliers, separate discovery screens, global controller or multiplication assembly.')
(o/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n',encoding='ascii');print(json.dumps(res))
