#!/usr/bin/env python3
"""Fresh offline source-bound w3 construction admission; no saved PASS is trusted."""
import sys
if not __debug__:raise SystemExit('Assertions required; refusing -O')
sys.dont_write_bytecode=True
import argparse,concurrent.futures,hashlib,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
 files={}
 for p in ROOT.rglob('*'):
  assert not p.is_symlink(),'Symlink in package'
  if p.is_file() and p!=ROOT/'MANIFEST.json':files[p.relative_to(ROOT).as_posix()]=sha(p)
 assert files==json.loads((ROOT/'MANIFEST.json').read_text())['files'],'Changed, missing or unpinned source'
 assert sha(ROOT/'vendor/pr249/MANIFEST.json')=='86e8bc5182079c00877077c8e4c7b2690ba2486bec385c0857f1794cd2e6bedb'
 return sha(ROOT/'MANIFEST.json')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--cxx',default='c++');ap.add_argument('--boost-include',type=Path);a=ap.parse_args()
 assert sys.version_info>=(3,11) and sys.byteorder=='little'
 digest=integrity();out=a.output.resolve();assert not out.exists() and not out.is_relative_to(ROOT),'Use a fresh external output'
 out.mkdir(parents=True)
 for part in ['logs','bin','bank','charts','temp']:(out/part).mkdir()
 start=time.monotonic();stages=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');py=[sys.executable,'-B'];code=ROOT/'code';up=ROOT/'vendor/pr249'
 def run(label,args,stdout=None):
  print(label,flush=True);t=time.monotonic()
  with (out/'logs'/(label+'.log')).open('w') as log:
   if stdout:
    with Path(stdout).open('w') as result:subprocess.run(list(map(str,args)),check=True,stdout=result,stderr=log,env=env,cwd=out)
   else:subprocess.run(list(map(str,args)),check=True,stdout=log,stderr=subprocess.STDOUT,env=env,cwd=out)
  stages.append({'stage':label,'seconds':time.monotonic()-t})
 try:
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
   baseline=pool.submit(run,'baseline-source',py+[up/'verify.py','--output',out/'baseline'])
   complex_source=pool.submit(run,'complex-source',py+[ROOT/'vendor/pr256/verify.py','--temp-root',out/'temp'])
   run('export-source',py+[code/'export249.py',up,out/'export'])
   run('bind-and-delete-inert-roles',py+[code/'prepare_candidate.py','--export',out/'export','--output',out/'candidate'])
   run('target-prefix',py+[code/'target_prefix.py',out/'candidate',out/'candidate',ROOT/'inputs/target-selection.json'])
   run('recompact-after-target-prefix',py+[code/'recompact.py',out/'candidate'])
   sources={'legality':ROOT/'supplied/checkers/official/cohort-legality-independent.cpp','columns':ROOT/'supplied/checkers/official/cohort-five-stage-columns.cpp','compact':code/'compact-columns.cpp','banks':code/'cohort-bank-review.cpp','charts':code/'changed-charts.cpp','invoice':code/'cohort-finite-invoice.cpp'}
   for name,path in sources.items():
    cmd=[a.cxx,'-O2','-std=c++17','-I',ROOT/'vendor']
    if a.boost_include:cmd+=['-I',a.boost_include.resolve()]
    run('compile-'+name,cmd+[path,'-o',out/'bin'/name])
   c=out/'candidate';b=out/'bin'
   run('legality',[b/'legality',out/'export',c,out/'LEGALITY.json'])
   run('columns',[b/'columns',c/'COHORT249-RECORDS.bin',out/'COLUMNS.json'])
   run('compact-columns',[b/'compact',c/'COMPACT-RECORDS.bin',out/'COMPACT-COLUMNS.json','1760','15132'])
   run('bank-frames-and-assignment',[b/'banks',out/'export',c/'COHORT249-INITIAL.json',c/'COHORT249-FRAMES.json',out/'bank','w3'])
   run('changed-charts',[b/'charts',out/'export',c,out/'charts'])
   run('geometry-admission',py+[code/'admit_geometry.py','--base',out/'export','--candidate',c,'--bank',out/'bank','--charts',out/'charts','--output',out/'BANK.json'])
   run('price',py+[code/'price.py',c,'--bank',out/'BANK.json','--output',out/'PRICE.json'])
   run('finite-invoice',[b/'invoice',c/'COHORT249-RECORDS.bin',out/'PRICE.json',out/'BANK.json',out/'COLUMNS.json',out/'INVOICE.json'])
   run('complex-guard',py+[code/'complex_guard.py'],stdout=out/'COMPLEX-GUARD.json')
   baseline.result();complex_source.result()
  run('complete-admission',py+[code/'finish.py',out])
  assert integrity()==digest,'Source mutated during replay'
  cert=json.loads((out/'CERTIFICATE.json').read_text());result={'status':cert['status'],'kappa':cert['kappa'],'word_sha256':cert['word_sha256'],'manifest_sha256':digest,'inputs_unchanged':True,'fresh_stages':stages,'seconds':time.monotonic()-start,'scope':cert['scope']}
  (out/'VERIFICATION.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS conditional kappa = '+cert['kappa'],flush=True)
 except BaseException as e:
  (out/'FAILURE.json').write_text(json.dumps({'status':'FAIL','error':str(e),'completed':stages},indent=2)+'\n');raise
if __name__=='__main__':main()
