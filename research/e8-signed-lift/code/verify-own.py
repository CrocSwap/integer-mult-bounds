#!/usr/bin/env python3
"""Rebuild and audit only the new source-bound construction; never replay public suppliers."""
import argparse,gzip,hashlib,json,os,struct,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
if not __debug__:raise SystemExit('Assertions must remain enabled')
SOURCE_WORD='05df0a39669bb077a9a2fa527904023a5a9da18cf644e06429d44f2a7ea92603'
SINK_WORD='98be41f1f01876d4aeba7e0238e9d7d59141dbd6e8ea8890f94165abf534e569'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(args):
 root=args.package_root.resolve();out=args.output.resolve()
 if out.exists():raise SystemExit('Use a new output directory; results are preserved')
 if out==root or root in out.parents:raise SystemExit('Output must be outside the immutable package')
 code=root/'code';data=root/'data';pins=read(data/'FINAL-PINS.json');expected=args.expected_final_sha or pins['final_word_sha256'];assert len(expected)==64
 required=['make-sinks.py','make-warm.py','kernel-emit-final.cpp','hash.h','json.hpp','legality.cpp','banks.cpp','changed-charts.cpp','columns.cpp','signed-target.cpp','source-span.cpp','export_native.py','tiling.py','source_tiling.py','admit_geometry.py','frame_prime_minors.py','reflected_ledgers.py']
 assert all((code/f).is_file()for f in required)
 tracked=[code/f for f in required]+[data/'FINAL-PINS.json',data/'TERMINAL-SCREEN.json',data/'OWN-SELECTION-FINAL.json',data/'OWN-FRAMES-FINAL.json.gz']+[data/'native351'/(n+'.gz')for n in ['records.bin','frames.json','initial.json','final.json','meta.json','physical.json','regs.json','labels.json']]
 before={str(p.relative_to(root)):sha(p)for p in tracked};out.mkdir(parents=True);(out/'bin').mkdir();(out/'logs').mkdir();(out/'native351').mkdir();(out/'bank').mkdir();(out/'charts').mkdir();(out/'controls').mkdir();stages=[];start=time.monotonic()
 def launch(label,argv,expect_fail=False):
  begin=time.monotonic()
  with (out/'logs'/(label+'.log')).open('w',encoding='utf8')as f:r=subprocess.run(list(map(str,argv)),stdout=f,stderr=subprocess.STDOUT,cwd=out,env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1'))
  if (r.returncode==0)==expect_fail:raise RuntimeError(label+' unexpected exit '+str(r.returncode))
  stages.append(dict(stage=label,seconds=round(time.monotonic()-begin,6),exit=r.returncode,negative_control=expect_fail));print(('REJECT'if expect_fail else'PASS'),label,flush=True)
 py=[sys.executable,'-X','utf8','-B']
 try:
  for name in ['records.bin','frames.json','initial.json','final.json','meta.json','physical.json','regs.json','labels.json']:
   raw=gzip.decompress((data/'native351'/(name+'.gz')).read_bytes());(out/'native351'/name).write_bytes(raw)
   assert hashlib.sha256(raw).hexdigest()==pins['native351_expanded_sha256'][name]
  assert sha(out/'native351/records.bin')==SOURCE_WORD
  (out/'OWN-FRAMES-FINAL.json').write_bytes(gzip.decompress((data/'OWN-FRAMES-FINAL.json.gz').read_bytes()))
  assert sha(out/'OWN-FRAMES-FINAL.json')==pins['kernel_frames_expanded_sha256']
  suffix='.exe'if os.name=='nt'else''
  binaries={}
  for label,src in [('kernel','kernel-emit-final.cpp'),('legality','legality.cpp'),('banks','banks.cpp'),('changed-charts','changed-charts.cpp'),('columns','columns.cpp'),('signed-target','signed-target.cpp'),('source-span','source-span.cpp'),('even-lift-control','even-lift-control.cpp')]:
   exe=out/'bin'/(label+suffix);argv=[args.cxx,'-O3','-std=c++17','-I',code]
   if args.boost_include:argv+=['-I',args.boost_include]
   launch('compile-'+label,argv+[code/src,'-o',exe]);binaries[label]=exe
  launch('make-sinks',py+[code/'make-sinks.py','--base',out/'native351','--selection',data/'TERMINAL-SCREEN.json','--output',out/'sinks','--receipt',out/'SINKS-MATERIALIZATION.json'])
  assert sha(out/'sinks/records.bin')==SINK_WORD
  launch('make-signed-kernel',[binaries['kernel'],out/'sinks',data/'OWN-SELECTION-FINAL.json',out/'OWN-FRAMES-FINAL.json',out/'kernel'])
  if 'kernel_word_sha256'in pins:assert sha(out/'kernel/records.bin')==pins['kernel_word_sha256']
  launch('exact-even-term-omission',[binaries['even-lift-control'],out/'kernel',out/'EVEN-LIFT-CONTROL.json'])
  launch('make-corrected-warm-cache',py+[code/'make-warm.py','--base',out/'kernel','--output',out/'final','--labels',out/'native351/labels.json','--receipt',out/'WARM-CACHE-MATERIALIZATION.json'])
  assert sha(out/'final/records.bin')==expected
  m=read(out/'final/meta.json');assert m['v']==960 and m['h']==20 and m['n']==9530 and m['R']==7610
  launch('signed-all-target-columns',[binaries['signed-target'],out/'native351',out/'final',out/'SINKS-MATERIALIZATION.json',out/'SIGNED-TARGET.json'])
  launch('all-actual-integer-source-spans',[binaries['source-span'],out/'final',out/'SOURCE-SPANS.json'])
  launch('full-five-stage-arbitrary-dirt',[binaries['columns'],out/'final/records.bin',out/'COLUMNS.json',m['v'],m['R'],m['h']])
  launch('native-export',py+[code/'export_native.py','--base',out/'native351','--candidate',out/'final','--output',out/'native-export'])
  b=out/'native-export/base';c=out/'native-export/candidate'
  launch('full-word-frame-copy-legality',[binaries['legality'],b,c,out/'LEGALITY.json'])
  launch('actual-zero-padding-free-tiling',py+[code/'tiling.py',b,c,out/'TILING.json'])
  launch('actual-300-replica-bank-allocation',[binaries['banks'],b,c/'COHORT249-INITIAL.json',c/'COHORT249-FRAMES.json',out/'bank','own-source-bound-bit-construction',out/'TILING.json',c/'COHORT249-FINAL.json'])
  launch('exact-changed-projector-charts',[binaries['changed-charts'],b,c,out/'charts'])
  launch('bind-all-new-geometry',py+[code/'admit_geometry.py','--base',b,'--candidate',c,'--bank',out/'bank','--charts',out/'charts','--output',out/'BANK.json'])
  launch('only-new-prime-frame-minors',py+[code/'frame_prime_minors.py',c/'COHORT249-FRAMES.json',out/'NEW-FRAME-PRIMES.json'])
  launch('both-complete-reflected-ledgers',py+[code/'reflected_ledgers.py','--candidate',c,'--output',out/'REFLECTED-LEDGERS.json'])
  ev=list(struct.iter_unpack('<6i',(out/'final/records.bin').read_bytes()));controls=[]
  for cat,label in [(90,'sink-setup'),(91,'sink-scatter'),(92,'signed-kernel-setup'),(93,'signed-kernel-restore'),(94,'warm-setup'),(95,'warm-feed'),(96,'warm-redirect'),(97,'warm-current-source-restore'),(98,'warm-correction-restore'),(99,'warm-scatter')]:
   ix=[i for i,e in enumerate(ev)if e[0]==1 and e[5]==cat];assert ix;omit=set(ix);raw=b''.join(struct.pack('<6i',*e)for i,e in enumerate(ev)if i not in omit);p=out/'controls'/(label+'.bin');p.write_bytes(raw)
   launch('reject-omit-'+label,[binaries['columns'],p,out/'controls'/(label+'.json'),960,7610,20],True)
   log=(out/'logs'/('reject-omit-'+label+'.log')).read_text();assert 'full formal column'in log
   controls.append(dict(omission=label,category=cat,ADDs_removed=len(ix),word_sha256=sha(p),rejected_at_defining_decoder=True))
  assert before=={str(p.relative_to(root)):sha(p)for p in tracked},'Immutable packaged inputs changed during review'
  receipt=dict(status='PASS_FRESH_OWN_BIT_REBUILD_AND_CHANGED_ONLY_NATIVE_AUDIT',source_word_sha256=SOURCE_WORD,sinks_word_sha256=SINK_WORD,final_word_sha256=expected,bank=read(out/'BANK.json'),controls=controls,stages=stages,source_hashes=before,seconds=time.monotonic()-start,public_unchanged_pipeline_replayed=False,complex_supplier_replayed=False,scope='Our deterministic literal sinks/signed-kernel/corrected-cache reconstruction and all changed bit-side checks only. Parent-owned E8 pins, exact rational moments, finite invoice and47strictassemblyconstraints are additional mandatory final admission.')
  (out/'OWN-VERIFICATION.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],expected,flush=True)
 except BaseException as e:
  (out/'FAILURE.json').write_text(json.dumps(dict(status='FAIL',error=str(e),completed=stages,seconds=time.monotonic()-start),sort_keys=True,indent=2)+'\n');raise
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--package-root',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--cxx',default='g++');ap.add_argument('--boost-include',type=Path);ap.add_argument('--expected-final-sha');run(ap.parse_args())
