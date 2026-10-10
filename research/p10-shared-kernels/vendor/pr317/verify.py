#!/usr/bin/env python3
"""Fresh offline p10 source-bound kernel/target/plateau/restoration/reorder admission.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions required; refusing -O')
sys.dont_write_bytecode=True
import argparse,concurrent.futures,hashlib,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def integrity():
 actual={}
 for p in ROOT.rglob('*'):
  assert not p.is_symlink(),'symlink in package'
  if p.is_file() and p!=ROOT/'MANIFEST.json':actual[p.relative_to(ROOT).as_posix()]=sha(p)
 assert actual==json.loads((ROOT/'MANIFEST.json').read_text())['files'],'Changed, missing or unpinned source'
 assert sha(ROOT/'vendor/pr315/MANIFEST.json')==json.loads((ROOT/'SOURCE.json').read_text())['pr315']['manifest_sha256']
 return sha(ROOT/'MANIFEST.json')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--cxx',default='c++');ap.add_argument('--boost-include',type=Path);a=ap.parse_args()
 assert sys.version_info>=(3,11) and sys.byteorder=='little'
 digest=integrity();out=a.output.resolve();assert not out.exists() and not out.is_relative_to(ROOT),'Use a fresh external output';out.mkdir(parents=True)
 for d in ['logs','bin','bank','charts']:(out/d).mkdir()
 start=time.monotonic();stages=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');py=[sys.executable,'-B'];code=ROOT/'code';src=ROOT/'vendor/pr315';sel=ROOT/'stages'
 def run(label,args):
  print(label,flush=True);t=time.monotonic()
  with (out/'logs'/(label+'.log')).open('w') as log:subprocess.run(list(map(str,args)),check=True,stdout=log,stderr=subprocess.STDOUT,env=env,cwd=out)
  stages.append(dict(stage=label,seconds=time.monotonic()-t))
 try:
  with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
   baseline=pool.submit(run,'immutable-pr315-source',py+[src/'verify.py','--output',out/'baseline'])
   run('export-source',py+[code/'export_source.py',src,out/'export'])
   run('kernel-stage',py+[code/'kernel_stage.py',src,sel/'kernel-selection.json',out/'candidate-kernel'])
   run('target-prefix-stage',py+[code/'f2_target_stage.py',out/'candidate-kernel',sel/'target-selection.json',out/'candidate-target'])
   run('plateau-ascent-stage',py+[code/'plateau_stage.py',out/'candidate-target',sel/'plateau-selection.json',out/'candidate-plateau'])
   run('early-restoration-stage',py+[code/'restoration/restore_stage.py','--input',out/'candidate-plateau','--selection',sel/'restoration-selection.json','--output',out/'candidate-restored'])
   run('reorder-stage',py+[code/'reorder_stage.py','--input',out/'candidate-restored','--selection',sel/'reorder-selection.json','--output',out/'candidate'])
   for name in ['legality','columns','banks','changed-charts','invoice']:
    cmd=[a.cxx,'-O2','-std=c++17','-I',ROOT/'vendor']
    if a.boost_include:cmd+=['-I',a.boost_include.resolve()]
    run('compile-'+name,cmd+[code/(name+'.cpp'),'-o',out/'bin'/name])
   c=out/'candidate';b=out/'bin'
   run('legality',[b/'legality',out/'export',c,out/'LEGALITY.json'])
   run('columns',[b/'columns',c/'COHORT249-RECORDS.bin',out/'COLUMNS.json','960','8230','20'])
   run('tiling',py+[code/'tiling.py',out/'export',c,out/'TILING.json'])
   run('bank-frames-and-assignment',[b/'banks',out/'export',c/'COHORT249-INITIAL.json',c/'COHORT249-FRAMES.json',out/'bank','p10-composition',out/'TILING.json',c/'COHORT249-FINAL.json'])
   run('changed-charts',[b/'changed-charts',out/'export',c,out/'charts'])
   run('geometry-admission',py+[code/'admit_geometry.py','--base',out/'export','--candidate',c,'--bank',out/'bank','--charts',out/'charts','--output',out/'BANK.json'])
   baseline.result()
  run('price',py+[code/'price.py',c,'--bank',out/'BANK.json','--complex',out/'baseline/complex.json','--output',out/'PRICE.json'])
  run('finite-invoice',[b/'invoice',c/'COHORT249-RECORDS.bin',out/'PRICE.json',out/'BANK.json',out/'COLUMNS.json',out/'INVOICE.json'])
  run('complete-admission',py+[code/'finish.py',out])
  assert integrity()==digest,'Source mutated during replay';cert=json.loads((out/'CERTIFICATE.json').read_text())
  result=dict(status=cert['status'],kappa=cert['kappa'],word_sha256=cert['word_sha256'],manifest_sha256=digest,inputs_unchanged=True,fresh_stages=stages,seconds=time.monotonic()-start,scope=cert['scope'])
  (out/'VERIFICATION.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS conditional kappa = '+cert['kappa'],flush=True)
 except BaseException as e:
  (out/'FAILURE.json').write_text(json.dumps(dict(status='FAIL',error=str(e),completed=stages),indent=2)+'\n');raise
if __name__=='__main__':main()
