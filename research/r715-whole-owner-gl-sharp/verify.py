"""Offline fresh finite reconstruction, operator audit, and sharp GL assembly.
Python3.11+, SymPy, C++17, Boost headers. No network or unproved float checks.
All-size weighted compiler/analytic interfaces remain explicitly inherited.
Prepared by OpenAI Codex; every upstream source notice is retained.
"""
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
assert __debug__
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);ap.add_argument('--boost-include',type=Path);ap.add_argument('--cxx',default=os.environ.get('CXX','c++'));a=ap.parse_args()
OUT=a.out.resolve();assert not OUT.exists() and not OUT.is_relative_to(ROOT),'Use a fresh output directory outside the source package'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def integrity():
 for p,z in read(ROOT/'UPSTREAM-SOURCES.json')['files'].items():
  b=(ROOT/p).read_bytes();assert hashlib.sha256(b).hexdigest()==z['sha256'],p
  if 'git_blob' in z:assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==z['git_blob'],p
 if (ROOT/'MANIFEST.json').exists():
  expected=read(ROOT/'MANIFEST.json')
  actual={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'MANIFEST.json' and '__pycache__' not in p.parts}
  assert actual==expected,'Complete source manifest mismatch'
integrity();OUT.mkdir();steps=[];start=time.monotonic();B=ROOT/'bit';C=ROOT/'complex';A=ROOT/'wrapper';bo=OUT/'bit';bo.mkdir();native=bo/'native';native.mkdir();(native/'bin').mkdir();host=bo/'hosted';host.mkdir();cx=OUT/'complex';cx.mkdir();provider=cx/'provider';ch=cx/'hosted';ch.mkdir()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHONUTF8='1',PYTHONPATH=os.pathsep.join(map(str,[B/'vendor/native',C/'vendor/transport',C/'vendor/complex',C/'code'])));env.pop('PYTHONOPTIMIZE',None)
def run(name,args):
 print('RUN',name,flush=True);t=time.monotonic();p=OUT/(name+'.log')
 with p.open('w') as f:r=subprocess.run(list(map(str,args)),env=env,stdout=f,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,returncode=r.returncode,seconds=round(time.monotonic()-t,3),log_sha256=sha(p)))
 (OUT/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
 assert r.returncode==0,(name,p.read_text()[-5000:]);print('PASS',name,flush=True)
def py(name,path,*args):run(name,[sys.executable,'-B',path,*args])
try:
 n=B/'vendor/native';word=B/'data/word.json';assert gzip.decompress((B/'data/word.json.gz').read_bytes())==word.read_bytes()
 py('bit-records',n/'export_records.py',word,native/'records')
 py('bit-labels',B/'code/labels.py',native/'records')
 py('bit-cohort',n/'stage_cohort.py',native/'records',native/'records',native/'cin',native/'cout')
 for name,src,defs in [('legality','legality_h.cpp',['-DNCOPY=9']),('legality_ncopy_h','legality_h.cpp',[]),('columns_h','columns_h.cpp',['-DNCOPY=9','-DVPORTS=120','-DRHELP=715']),('columns_k5','columns_k.cpp',['-DNCOPY=9','-DVPORTS=120','-DRHELP=715','-DKPAIRS=5'])]:
  cmd=[a.cxx,'-O2','-std=c++17','-DHDIM=8',*defs,'-I'+str(B/'vendor/portable-include'),'-I'+str(n)]
  if a.boost_include:cmd+=['-I'+str(a.boost_include)]
  run('compile-'+name,[*cmd,'-o',native/'bin'/name,n/src])
 run('bit-legality',[native/'bin/legality',native/'cin',native/'cout',native/'cout/legality.json'])
 for name,file in [('columns_h','columns.json'),('columns_k5','columns_k5.json')]:run('bit-'+name,[native/'bin'/name,native/'cout/COHORT249-RECORDS.bin',native/'cout'/file])
 py('bit-record-mutations',B/'code/mutate_records.py',native/'records',native/'cin',native/'cout',native/'bin/legality',native/'bin/columns_k5',native/'bin/legality_ncopy_h')
 py('bit-gram',n/'gram_frames.py',native/'records','--gram','e8ham','--h',8,'--positive')
 py('bit-geometry',B/'code/geometry.py','--source',B/'vendor/geometry','--out',host)
 py('bit-source-emission',B/'code/emit.py','--word',B/'data/word.json.gz','--local-check',native,'--out',host,'--isometries',B/'data/residual-isometries.json')
 py('bit-gl-cover',A/'gl_cover.py',B,bo)
 nine=bo/'nine';nine.mkdir();shutil.copy2(B/'vendor/geometry/NINE-GEOMETRY.json',nine/'GEOMETRY.json')
 py('bit-independent-hosting',B/'code/audit.py',native,nine,host)
 py('bit-local-actual-ledgers',A/'check_local_ledgers.py',B,bo)
 py('bit-actual-owner-matrices',A/'cover_owner_injection.py',B,bo)
 py('bit-finite-physical-operator',A/'finite_bit_cover.py',bo)
 tr=C/'vendor/transport'
 py('complex-source-scalar-phase',C/'code/build-local.py','--word',C/'inputs/kernel79.json.gz','--vendor',tr/'upstream449','--routes',tr/'routes.json.gz','--clifford',tr/'clifford_exact.py','--out',provider)
 py('complex-normalization',C/'code/normalize-local.py','--canonical',provider/'CANONICAL-WORD.json.gz','--programs',provider/'LOCAL-PROGRAMS.json.gz','--checks',provider/'LOCAL-CHECKS.json','--clifford',tr/'clifford_exact.py','--out',provider)
 for ori,z in read(provider/'NORMALIZED-CHECKS.json').items():assert z['sha256']==read(tr/'receipts79/NORMALIZED-CHECKS.json')[ori]['sha256']
 phase=ch/'DATA-PHASES.json'
 py('complex-data-phases',C/'vendor/complex/complex_phases.py',provider/'CANONICAL-WORD.json.gz',phase)
 assert read(phase)==read(C/'inputs/complex-data-phases.json')
 sel=C/'inputs/borrowed79-selection.json';base=C/'inputs/complex-controller-base.json.gz';cw=provider/'CANONICAL-WORD.json.gz';local=provider/'SCALAR-FRAME-AUDIT.json';wrap=provider/'CANONICAL-WRAPPERS.json';template=ch/'GLOBAL-TEMPLATE.json.gz'
 py('complex-whole-emission',C/'code/borrowed_emit.py',sel,base,phase,cw,local,wrap,template,provider)
 py('complex-independent-physical',C/'code/borrowed_audit.py',template,sel,base,phase,cw,local,wrap,ch/'PHYSICAL-AUDIT.json',provider)
 py('complex-independent-routes',C/'code/independent_routes.py',template,phase,ch/'INDEPENDENT-ROUTES.json')
 py('complex-whole-controller',C/'code/global_controller.py',template,ch/'PHYSICAL-AUDIT.json',provider/'NORMALIZED-CHECKS.json',phase,ch/'GLOBAL.json',ch/'AUDIT.json')
 py('complex-independent-local-ledgers',A/'replay_fresh_local_rows.py',provider,ch/'INDEPENDENT-LOCAL-ROWS.json')
 py('complex-owner-and-finite-operator',A/'cover_operator_bridge.py',template,phase,ch/'COVER-BRIDGE.json')
 py('sharp-two-moments-and-outer',ROOT/'invoice/assemble.py',bo,host,host/'AUDIT.json',OUT/'ASSEMBLY.json','--nine','hosted','--complex',ch,'--route-extra',6,'--parent-kappa','161953209398787/125000000000000000','--label','PR473')
 py('independent-invoice',ROOT/'invoice/independent_invoice.py',host,ch,OUT/'ASSEMBLY.json',OUT/'INDEPENDENT-INVOICE.json')
 integrity();result=read(OUT/'ASSEMBLY.json')
 receipt=dict(status='PASS_FRESH_WHOLE_OWNER_GL_SHARP_FINITE_CONSTRUCTION',kappa=result['kappa'],steps=steps,seconds=round(time.monotonic()-start,3),scope='Fresh native bit replay, both exact local frame ledgers, actual whole-owner injection, finite physical operator controls, source complex phases/normalizers, complete paid controllers, independent invoice, two moments and strict outer assembly. Retains inherited all-size/compiler/analytic conditions; no cross-family split.')
 (OUT/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='steps'},indent=2))
except BaseException as e:
 (OUT/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),completed=steps),indent=2)+'\n');raise
