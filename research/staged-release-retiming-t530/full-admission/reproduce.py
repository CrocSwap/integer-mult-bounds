#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Source-bound retiming derivative; substantial OpenAI Codex assistance.
"""Rebuild exact sources, or run the separate complete scientific replay.

This separate replay is not the registered bounded summary check. Pass
--materialize-only for fresh source reconstruction alone. The complete replay
retains all original scientific gates and reuses authenticated parent evidence.
"""
import argparse,gzip,hashlib,io,json,os,subprocess,sys,tarfile,time
from pathlib import Path,PurePosixPath
from fractions import Fraction as Q
H=Path(__file__).resolve().parent
MAIN='20ecf2891d80b5acf18d980b2164fb44ea7faa90'
MANIFEST='fb47533a401d1d13719be8b9aab91fe5313931ca62d40dba336eab6a96275aa0'
def need(ok,message):
 if not ok:raise ValueError(message)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def export_main(repo,out):
 pins=read(H/'MAIN-INPUTS.json');need(pins['base_commit']==MAIN,'frozen main commit')
 env=dict(os.environ,GIT_NO_REPLACE_OBJECTS='1')
 subprocess.run(['git','-C',str(repo),'cat-file','-e',MAIN+'^{commit}'],env=env,check=True,stdout=subprocess.DEVNULL)
 names=sorted(pins['sha256']);raw=subprocess.run(['git','-C',str(repo),'archive','--format=tar',MAIN,'--',*names],env=env,check=True,capture_output=True).stdout
 out.mkdir();seen=set()
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as tar:
  for m in tar:
   p=PurePosixPath(m.name)
   need(not p.is_absolute() and '..' not in p.parts and '\\' not in m.name,'unsafe Git archive path')
   if m.isdir():continue
   need(m.isfile() and m.name in pins['sha256'] and m.name not in seen,'exact regular-file export set')
   stream=tar.extractfile(m);need(stream is not None,'export bytes');body=stream.read()
   need(hashlib.sha256(body).hexdigest()==pins['sha256'][m.name],'frozen input hash '+m.name)
   q=out/m.name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(body);seen.add(m.name)
 need(seen==set(names),'complete pinned main export')
 return len(seen)
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--repo',type=Path,default=H.parents[2]);a.add_argument('--work',type=Path,required=True);a.add_argument('--allocation',type=Path);a.add_argument('--materialize-only',action='store_true');x=a.parse_args()
 need(__debug__ and not sys.flags.optimize,'assertions must be enabled for inherited scientific code')
 repo=x.repo.resolve();work=x.work.resolve();need(not work.exists() and not work.is_relative_to(H),'fresh external work directory');work.mkdir(parents=True)
 pins=read(H/'vendor/PR3626-INPUTS.json');need(pins['head']=='659fd5e7064d9466b668d7188cbb013b333a415a','PR3626 exact source head')
 original=read(H/'vendor/PR3626-FETCH-PINS.json');need(original['head']==pins['head'],'original fetch provenance')
 for path,digest in pins['sha256'].items():
  need(original['sha256'][path]==digest,'published dependency hash')
  local=H/'vendor/staged-width-t530'/Path(path).relative_to('research/staged-width-t530');need(sha(local)==digest,'PR3626 input '+path)
 frozen=work/'main-files';exported=export_main(repo,frozen)
 t530=H/'vendor/staged-width-t530';t8=frozen/'research/t8-rank7-two-swaps';stages=[]
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(work/'pycache'),PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 for key in ['PYTHONPATH','PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_RECORD','WITNESS_DISCOVER']:env.pop(key,None)
 def run(label,args,extra_env=None):
  start=time.monotonic();cmd=[sys.executable,'-B',*map(str,args)]
  with (work/(label+'.log')).open('w') as f:r=subprocess.run(cmd,env=env if extra_env is None else dict(env,**extra_env),stdout=f,stderr=subprocess.STDOUT)
  stages.append({'name':label,'command':cmd,'exit_code':r.returncode,'seconds':time.monotonic()-start,'log_sha256':sha(work/(label+'.log'))});(work/'STAGES.json').write_text(json.dumps(stages,indent=2));need(r.returncode==0,label+': inspect its work log')
  print('PASS',label,flush=True)
 prepared=work/'prepared';retimed=work/'retimed'
 run('original-materialization',[t530/'replay.py','--t8-package',t8,'--main-files',frozen,'--work',prepared,'--materialize-only'])
 run('retiming-source',[H/'scripts/integrate.py','--parent',prepared/'changed','--out',retimed])
 need(sha(retimed/'source/MANIFEST.json')==MANIFEST,'same frozen654 source')
 manifest=read(retimed/'source/MANIFEST.json');need(len(manifest)==654 and all(sha(retimed/'source'/p)==h for p,h in manifest.items()),'complete source payload hashes')
 run('preserved-staged-review',[retimed/'source/new/borrow/review_staged3605.py'])
 run('new-retiming-review',[retimed/'source/new/borrow/review_release_retime.py'])
 summary={'status':'PASS_PUBLIC_SOURCE_REBUILD_654_FILES','source_manifest_sha256':MANIFEST,'source_files':654,'main_commit':MAIN,'exported_inputs':exported,'stages':[{'name':s['name'],'exit_code':s['exit_code'],'log_sha256':s['log_sha256']} for s in stages],'scope':'Fresh exact source reconstruction and reconstruction controls only; no fresh native/controller/outer admission.'}
 (work/'SOURCE-REBUILD-RESULT.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
 if x.materialize_only:print('PASS_PUBLIC_SOURCE_REBUILD_654_FILES');return
 old=prepared/'predecessor'
 run('fresh-native',[retimed/'prepare_extension_native.py','--source',retimed/'source','--retained-cache',old/'native-cache','--retained-receipt',old/'NATIVE-RECEIPT.json','--out',retimed/'native','--jobs','1'])
 allocation=x.allocation.resolve() if x.allocation else work/'allocation'
 if x.allocation is None:run('literal-owners',[t530/'owners/portable_expand.py','--out',allocation],{'OWNER_SOURCE_REPO':str(frozen)})
 fill=read(allocation/'FILL.json.gz');need(fill['columns']==['time','helper','owner_replica','child','port','offset'] and len(fill['rows'])==1946160,'complete literal allocation')
 need(not fill.get('dispatch_overrides',[]),'no dispatch override');fill['dispatch_overrides']=[];legacy=work/'FILL-legacy.json.gz';legacy.write_bytes(gzip.compress(json.dumps(fill,separators=(',',':')).encode(),mtime=0))
 cmd=[retimed/'admit_extension.py'];vals={'source':retimed/'source','fill':legacy,'order':allocation/'ORDER.json','dispatch':allocation/'DISPATCH.json','native-cache':retimed/'native/native-cache','native-receipt':retimed/'native/NATIVE-RECEIPT.json','work':retimed/'admission','replica-helper-dir':old/'helpers','reconstructor':old/'helpers/reconstruct_replica.py','comparison-claim':old/'PR2969-CLAIM.json','blocknorm-checker':old/'adapters/extension_blocknorm.py'}
 for k,v in vals.items():cmd+=['--'+k,v]
 cmd+=['--source-profile','staged3605','--comparison-profile','pr2969','--jobs','1'];run('full-admission',cmd)
 r=read(retimed/'admission/RESULT.json');need(r['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE','complete scientific release')
 need(Q(r['kappa'])==Q('.001730394391813963415120')-Q(1,10**46)-Q(1,10**70),'exact conditional modern headline')
 need(Q(r['kappa'])>Q('.001730071864705779882540')-Q(1,10**46)-Q(1,10**70),'strict improvement over PR3626')
 (work/'RESULT.json').write_text(json.dumps({'status':'PASS_RETIMER_T530_COMPLETE_CONDITIONAL_RELEASE','kappa':r['kappa'],'source_manifest_sha256':MANIFEST,'stages':stages},indent=2));print('PASS_RETIMER_T530_COMPLETE_CONDITIONAL_RELEASE',r['kappa'])
if __name__=='__main__':main()
