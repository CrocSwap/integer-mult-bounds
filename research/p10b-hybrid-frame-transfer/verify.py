#!/usr/bin/env python3
"""Fresh sink-aware cube-orientation source, PR327 supplier, literal p10b stages, T300 banks and exact assembly.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions required; refusing -O')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,hashlib,json,os,subprocess,time
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def integrity():
 actual={}
 for p in ROOT.rglob('*'):
  assert not p.is_symlink(),'Symlink in package'
  if p.is_file()and p!=ROOT/'MANIFEST.json':actual[p.relative_to(ROOT).as_posix()]=sha(p)
 assert actual==json.loads((ROOT/'MANIFEST.json').read_text())['files'],'Missing, changed or unpinned source'
 pins=json.loads((ROOT/'SOURCE.json').read_text())
 for key,directory in [('predecessor','predecessor'),('complex_reserve','complex-reserve')]:assert sha(ROOT/'vendor'/directory/'MANIFEST.json')==pins[key]['manifest_sha256']
 return sha(ROOT/'MANIFEST.json')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--cxx',default='c++');ap.add_argument('--boost-include',type=Path);a=ap.parse_args()
 assert sys.version_info>=(3,11)and sys.byteorder=='little'
 digest=integrity();out=a.output.resolve();assert not out.exists()and not out.is_relative_to(ROOT),'Fresh external output required';out.mkdir(parents=True)
 for d in ('logs','bin','bank','charts'):(out/d).mkdir()
 start=time.monotonic();stages=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');py=[sys.executable,'-B'];code=ROOT/'code';src=ROOT/'vendor/predecessor';reserve=ROOT/'vendor/complex-reserve'
 def run(label,args):
  print(label,flush=True);t=time.monotonic()
  with(out/'logs'/(label+'.log')).open('w')as log:subprocess.run(list(map(str,args)),check=True,stdout=log,stderr=subprocess.STDOUT,env=env,cwd=out)
  stages.append(dict(stage=label,seconds=time.monotonic()-t))
 try:
  run('regenerate-flow-source',py+[src/'bitword/producer/regenerate_structural.py',src,'--work',out/'source-regeneration','--rounds','2'])
  run('immutable-flow-source',py+[src/'verify.py','--output',out/'predecessor'])
  run('immutable-complex-reserve',py+[reserve/'verify.py','--output',out/'complex-reserve'])
  run('reconstruct-p10b-word',py+[code/'materialize.py',out])
  run('export-native',py+[code/'export_native.py','--base',out/'materialized/parity-baseline','--candidate',out/'materialized/final','--output',out/'native-export'])
  for name in ('base','candidate','EXPORT.json','ROLE-MAP.json'):(out/'native-export'/name).rename(out/name)
  (out/'native-export').rmdir()
  for name in ('legality','columns','changed-charts','banks','invoice'):
   cmd=[a.cxx,'-O2','-std=c++17','-I',ROOT/'vendor/native']
   if a.boost_include:cmd+=['-I',a.boost_include.resolve()]
   run('compile-'+name,cmd+[code/(name+'.cpp'),'-o',out/'bin'/name])
  b=out/'base';c=out/'candidate';bin=out/'bin'
  run('legality',[bin/'legality',b,c,out/'LEGALITY.json'])
  run('columns',[bin/'columns',c/'COHORT249-RECORDS.bin',out/'COLUMNS.json','960',str(json.loads((ROOT/'SOURCE.json').read_text())['expected']['R']),'20'])
  run('tiling',py+[code/'tiling.py',b,c,out/'TILING.json'])
  run('bank-frames-and-assignment',[bin/'banks',b,c/'COHORT249-INITIAL.json',c/'COHORT249-FRAMES.json',out/'bank','p10b-hybrid023transfer-pr327-t300',out/'TILING.json',c/'COHORT249-FINAL.json'])
  run('changed-charts',[bin/'changed-charts',b,c,out/'charts'])
  run('geometry-admission',py+[code/'admit_geometry.py','--base',b,'--candidate',c,'--bank',out/'bank','--charts',out/'charts','--output',out/'BANK.json'])
  run('all-frame-prime-minors',py+[code/'frame_prime_minors.py',c/'frames.json',out/'FRAME-PRIMES.json'])
  run('price',py+[code/'price.py',c,'--bank',out/'BANK.json','--complex',out/'predecessor/complex.json','--complex-reserve',reserve,'--complex-reserve-proof',out/'complex-reserve','--output',out/'PRICE.json'])
  run('finite-invoice',[bin/'invoice',c/'COHORT249-RECORDS.bin',out/'PRICE.json',out/'BANK.json',out/'COLUMNS.json',out/'INVOICE.json'])
  run('prime-threshold-bootstrap',py+[code/'threshold_bootstrap.py','--arithmetic-stage','--source',ROOT,'--replay',out,'--expected-word',json.loads((ROOT/'SOURCE.json').read_text())['final_word_sha256'],'--require-frame-primes','--output',out/'REFINEMENT.json'])
  run('producer-binding-controls',py+[code/'producer_binding_controls.py',out/'PRODUCER-BINDING-CONTROLS.json'])
  run('complete-admission',py+[code/'finish.py',out])
  assert integrity()==digest,'Source changed during replay';cert=json.loads((out/'CERTIFICATE.json').read_text())
  report=dict(status=cert['status'],kappa=cert['kappa'],word_sha256=cert['word_sha256'],manifest_sha256=digest,inputs_unchanged=True,fresh_stages=stages,seconds=time.monotonic()-start,scope=cert['scope'])
  (out/'VERIFICATION.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print('PASS conditional kappa = '+cert['kappa'],flush=True)
 except BaseException as exc:
  (out/'FAILURE.json').write_text(json.dumps(dict(status='FAIL',error=str(exc),completed=stages),indent=2)+'\n');raise
if __name__=='__main__':main()
