#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned local Git export, declared stages, native chains and complete release.

No network fetch is performed. Fresh retained bootstrap is the default;
--retained explicitly reuses a fully authenticated prior parent/native cache.
The preparation/release mechanisms derive from PR2894/2857/2839 with credit.
"""
import argparse,hashlib,io,json,os,shutil,subprocess,sys,tarfile,time
from pathlib import Path,PurePosixPath
from fractions import Fraction as Q
P=Path(__file__).resolve().parent
HEAD='18d03c447886895ef9abf888398178e0428533ca'
UPSTREAM_MANIFEST='3cb842b93dd3b0707ceea825bef2afeaa68f8df0d554867761b4752b69077293'
DERIVED_MANIFEST='56cf455752722051d598a7da1e5ee700637fbaef09189f534413dbe6e0525a83'
RECORDED_RETAINED='dd36443f2789ffa6deca7210c76ada781e2b9b7e622a546b366f51a475faff3e'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def tree(p):
 assert not any(f.is_symlink() for f in p.rglob('*'))
 return {f.relative_to(p).as_posix():sha(f) for f in p.rglob('*') if f.is_file() and f!=p/'MANIFEST.json'}
def export(repo,out):
 prefix=PurePosixPath('research/shared-kernel-packing')
 raw=subprocess.run(['git','-C',str(repo),'archive','--format=tar',HEAD,str(prefix)],check=True,capture_output=True).stdout
 out.mkdir()
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as ar:
  for f in ar.getmembers():
   p=PurePosixPath(f.name);assert not p.is_absolute() and '..' not in p.parts and '\\' not in f.name
   if f.isdir() and (p==prefix or p in prefix.parents):continue
   assert p.is_relative_to(prefix);rel=p.relative_to(prefix);assert f.isfile() or f.isdir()
   q=out/rel
   if f.isdir():q.mkdir(parents=True,exist_ok=True)
   else:q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(ar.extractfile(f).read())
 assert sha(out/'MANIFEST.json')==UPSTREAM_MANIFEST and tree(out)==read(out/'MANIFEST.json')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--retained',type=Path);ap.add_argument('--dry-run',action='store_true');a=ap.parse_args()
 assert __debug__;work=a.work.resolve();assert not work.exists() and not work.is_relative_to(P) and not P.is_relative_to(work)
 assert tree(P)==read(P/'MANIFEST.json'),'complete public package inventory'
 work.mkdir(parents=True);upstream=work/'pr2894';export(a.repo.resolve(),upstream);core=upstream/'vendor/pr2857';source=work/'pr2833';source4=work/'source4';pm=work/'source-pm';final=work/'source';native=work/'native';candidate=work/'candidate';bound=work/'prepare-native-bound.py'
 retained=a.retained.resolve() if a.retained else work/'retained'
 if a.retained:assert not retained.is_relative_to(work) and not work.is_relative_to(retained)
 py=[sys.executable,'-B'];recipe=[('export-pr2833',py+[upstream/'tools/materialize_source.py','--repo',a.repo.resolve(),'--out',source])]
 if not a.retained:recipe.append(('fresh-retained-bootstrap',py+[upstream/'tools/prepare_retained.py','--source',source,'--out',retained,'--jobs','1']))
 recipe += [('four-kernel-stage',py+[core/'build_overlay.py','--source',source,'--generator',core/'shared_kernel.py','--review',core/'review_four_groups.py','--candidate-dir',core/'words','--out',source4]),('preload-stage',py+[upstream/'vendor/pm/build_pm_overlay.py','--overlay',source4,'--pm-dir',upstream/'vendor/pm','--out',pm]),('two-sided-stage',py+[P/'tools/build_channel_overlay.py','--source',pm,'--local-package',P,'--out',final]),('fresh-current-native',py+[bound,'--source',final,'--retained-cache',retained/'native-cache','--retained-receipt',retained/'NATIVE-RECEIPT.json','--out',native,'--jobs','1']),('complete-admission',py+[P/'tools/admit_channel408.py','--source',final,'--fill',P/'allocation/FILL.json.gz','--order',P/'allocation/ORDER.json','--dispatch',P/'allocation/DISPATCH.json','--native-cache',native/'native-cache','--native-receipt',native/'NATIVE-RECEIPT.json','--work',candidate,'--replica-helper-dir',core/'vendor/pr2839','--reconstructor',core/'vendor/pr2839/reconstruct_replica.py','--blocknorm-checker',P/'tools/channel_blocknorm.py','--comparison-claim',upstream/'CLAIM.json','--source-profile','channel408','--comparison-profile','pr2894','--jobs','1'])]
 if a.dry_run:
  save(work/'PREFLIGHT.json',{'status':'SOURCE_EXPORT_AND_RECIPE_ONLY_NOT_A_REPLAY','commands':[[n,list(map(str,c))] for n,c in recipe]});print('PASS_PINNED_PR2894_EXPORT_RECIPE_ONLY');return
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(work/'bytecode'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONINTMAXSTRDIGITS='0')
 for n in ['PYTHONOPTIMIZE','PYTHONPATH','WITNESS_SPEC','WITNESS_RECORD','WITNESS_DISCOVER']:env.pop(n,None)
 stages=[]
 for name,cmd in recipe:
  if name=='fresh-current-native':
   assert sha(final/'MANIFEST.json')==DERIVED_MANIFEST
   text=(P/'tools/prepare_channel_native.py').read_text();old='OLD_RECEIPT_SHA='+repr(RECORDED_RETAINED);assert text.count(old)==1
   new=sha(retained/'NATIVE-RECEIPT.json');bound.write_text(text.replace(old,'OLD_RECEIPT_SHA='+repr(new)))
   save(work/'RETAINED-BINDING.json',{'recorded_receipt_sha256':RECORDED_RETAINED,'this_receipt_sha256':new,'bound_script_sha256':sha(bound),'explicit_reuse':bool(a.retained),'scope':'Only this receipt identity is rebound; complete cache, parent source/claim and 16 stages are still authenticated by the unchanged strict checks.'})
  log=work/(name+'.log');start=time.monotonic()
  with log.open('w') as f:r=subprocess.run(list(map(str,cmd)),env=env,cwd=work,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
  stages.append({'stage':name,'exit_code':r.returncode,'seconds':time.monotonic()-start,'log_sha256':sha(log)});save(work/'STAGES.json',stages)
  assert r.returncode==0,'failed '+name+'; see '+str(log);print('PASS',name,flush=True)
 result=read(candidate/'RESULT.json');receipt=read(candidate/'release/RELEASE-RECEIPT.json');claim=read(P/'CLAIM.json')
 assert result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE' and receipt['status']=='PASS_RELEASE'
 assert Q(result['kappa'])==Q(receipt['kappa_decimal'])==Q(claim['kappa'])
 assert result['release_receipt_sha256']==sha(candidate/'release/RELEASE-RECEIPT.json') and result['package_manifest_sha256']==receipt['manifest_sha256']
 assert tree(P)==read(P/'MANIFEST.json') and tree(upstream)==read(upstream/'MANIFEST.json')
 save(work/'RESULT.json',{'status':'PASS_TWO_SIDED_HELPER408_COMPLETE_REPLAY','kappa':result['kappa'],'native_receipt_sha256':sha(native/'NATIVE-RECEIPT.json'),'admission_result_sha256':sha(candidate/'RESULT.json'),'explicit_retained_reuse':bool(a.retained),'fresh_retained_bootstrap':not bool(a.retained),'stages':stages,'scope':'Conditional finite supplier/outer result; inherited all-size theorem obligations remain.'})
 print('PASS_TWO_SIDED_HELPER408_COMPLETE_REPLAY',result['kappa'],flush=True)
if __name__=='__main__':main()
