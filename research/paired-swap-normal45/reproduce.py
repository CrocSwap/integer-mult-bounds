#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact upstream exports, fresh changed native chains and complete supplier/outer release.
--retained explicitly reuses a hash-authenticated old bootstrap; the two changed
native words and complete admission still run freshly. No Lean formalization.
"""
from pathlib import Path,PurePosixPath
from fractions import Fraction as Q
import argparse,gzip,hashlib,io,json,os,subprocess,sys,tarfile,time
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
UPSTREAM=[('pr2942','a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf','research/paired-extension-normal45','23bd270f440c4c7ad0d106990ae391e1af799a61ef3601d00e27f1824ae8ba69'),('pr2957','b74b25f3ccc84c16e1a801d73b2f47e5ea764c78','research/paired-extension-cap-fill-swaps','9cd226a2bf7391e7fbf4a23741bb1934afafbd596aef06f2999a935cd6e44e28')]
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b)
def write(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
def tree(p):
 need(not any(f.is_symlink()for f in p.rglob('*')),'no source symlinks')
 return {f.relative_to(p).as_posix():sha(f)for f in p.rglob('*')if f.is_file()and f!=p/'MANIFEST.json'}
def export(repo,head,prefix,pin,out,env):
 raw=subprocess.run(['git','-C',str(repo),'archive','--format=tar',head,prefix],env=env,check=True,capture_output=True).stdout
 root=PurePosixPath(prefix);out.mkdir()
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:')as tar:
  for m in tar.getmembers():
   path=PurePosixPath(m.name);need(not path.is_absolute()and '..'not in path.parts and '\\'not in m.name,'safe exact Git archive')
   if m.isdir()and(path==root or path in root.parents):continue
   need(path.is_relative_to(root)and(m.isfile()or m.isdir()),'regular exact Git entry')
   dest=out/str(path.relative_to(root))
   if m.isdir():dest.mkdir(parents=True,exist_ok=True)
   else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(tar.extractfile(m).read())
 need(sha(out/'MANIFEST.json')==pin and tree(out)==read(out/'MANIFEST.json'),'complete exact exported source '+prefix)
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for x in ['repo','work']:ap.add_argument('--'+x,type=Path,required=True)
 ap.add_argument('--retained',type=Path);ap.add_argument('--jobs',type=int,choices=[1,2],default=1);ap.add_argument('--dry-run',action='store_true');a=ap.parse_args()
 need(not sys.flags.optimize,'assertions enabled');pins=read(P/'MANIFEST.json');need(tree(P)==pins,'complete public package inventory')
 repo=a.repo.resolve();work=a.work.resolve();need(not work.exists()and not work.is_relative_to(P)and not P.is_relative_to(work),'fresh external work only');work.mkdir(parents=True)
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 for k in ['PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD']:env.pop(k,None)
 stages=[]
 def run(name,command):
  log=work/(name+'.log');begin=time.monotonic()
  with log.open('w',encoding='utf-8')as f:r=subprocess.run(list(map(str,command)),cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
  stages.append({'stage':name,'command':list(map(str,command)),'exit_code':r.returncode,'seconds':time.monotonic()-begin,'log_sha256':sha(log)});write(work/'STAGES.json',stages)
  need(r.returncode==0,'failed '+name+'; see '+str(log));print('PASS',name,flush=True)
 for tag,head,prefix,pin in UPSTREAM:export(repo,head,prefix,pin,work/tag,env)
 py=[sys.executable,'-B'];normal=work/'pr2942';rewrites=work/'pr2957';recipe=work/'source-recipe'
 # Use the unchanged predecessor's exact dry-run recipe; execute only source
 # preparation, not a redundant baseline native/admission campaign.
 dry=py+[normal/'reproduce.py','--repo',repo,'--work',recipe,'--dry-run']
 retained=a.retained.resolve()if a.retained else recipe/'retained'
 if a.retained:dry+=['--retained',retained]
 run('exact-predecessor-source-recipe',dry)
 prefix=[]
 for name,command in read(recipe/'PREFLIGHT.json')['commands']:
  prefix.append((name,command))
  if name=='normal45-overlay-stage':break
 need(prefix[-1][0]=='normal45-overlay-stage','exact source-stage boundary')
 source=recipe/'source-normal45';composed=work/'composed';lifted=work/'lifted';derived=work/'source';adapters=work/'adapters';native=work/'native';candidate=work/'candidate'
 commands=prefix+[
 ('compose-declared-mechanisms',py+[P/'construction/compose.py','--normal45',normal,'--rewrites-package',rewrites,'--out',composed,'--ablations']),
 ('independent-full-operator-review',py+[P/'tools/source_review.py','--source',rewrites,'--normal-dir',normal/'data','--combined-dir',composed,'--preload-helper',normal/'vendor/preload_move.py','--operator-helper',normal/'vendor/audit_local.py','--out',work/'independent-source-review.json']),
 ('semantic-corruption-controls',py+[P/'tools/semantic_controls.py','--candidates',composed,'--source',normal,'--out',work/'semantic-controls']),
 ('construct-literal-t370',py+[P/'construction/lift_allocation.py','--source',normal,'--out',lifted]),
 ('append-authenticated-source-stage',py+[P/'tools/append_overlay.py','--source',source,'--source-manifest','79956f19c5c3d4d1ad3578e4b3d6844bc54c1f3680825fc87c80cc04f069dae8','--words',P/'data','--out',derived,'--stage','normal45-fourteen-rewrite-composition','--deleted-b-indices',P/'construction/B-DELETIONS.json']),
 ('derive-source-bound-adapters',py+[P/'tools/derive_adapters.py','--parent-package',recipe/'pr2908','--source',derived,'--retained-receipt',retained/'NATIVE-RECEIPT.json','--out',adapters,'--buffers','86','--source-commit','normal45-fourteen-rewrite-composition','--source-profile','normal45-fourteen-rewrites','--upstream-head',UPSTREAM[1][1],'--comparison','pr2942='+str(normal/'CLAIM.json'),'--comparison','pr2957='+str(rewrites/'CLAIM.json')]),
 ('two-fresh-changed-native-chains',py+[adapters/'prepare_extension_native.py','--source',derived,'--retained-cache',retained/'native-cache','--retained-receipt',retained/'NATIVE-RECEIPT.json','--out',native,'--jobs',str(a.jobs)]),
 ('complete-admission-and-outer-release',py+[adapters/'admit_extension.py','--source',derived,'--fill',P/'allocation/FILL.json.gz','--order',P/'allocation/ORDER.json','--dispatch',P/'allocation/DISPATCH.json','--native-cache',native/'native-cache','--native-receipt',native/'NATIVE-RECEIPT.json','--work',candidate,'--replica-helper-dir',recipe/'parent-export/pr2894/vendor/pr2857/vendor/pr2839','--reconstructor',recipe/'parent-export/pr2894/vendor/pr2857/vendor/pr2839/reconstruct_replica.py','--blocknorm-checker',adapters/'extension_blocknorm.py','--comparison-claim',rewrites/'CLAIM.json','--source-profile','normal45-fourteen-rewrites','--comparison-profile','pr2957','--jobs','1'])]
 write(work/'PLAN.json',{'status':'EXACT_EXPORTS_AND_PLAN_ONLY'if a.dry_run else'FULL_REPLAY_RUNNING','commands':[(n,list(map(str,c)))for n,c in commands],'explicit_retained_reuse':bool(a.retained),'jobs':a.jobs})
 if a.dry_run:print('PASS_EXACT_EXPORTS_AND_PLAN_ONLY_NOT_NATIVE_OR_RELEASE');return
 for name,command in commands:
  run(name,command)
  if name=='compose-declared-mechanisms':
   for v in ['base','extra']:need(read(composed/f'WORD-{v}.json.gz')==read(P/f'data/WORD-{v}.json.gz'),'entire regenerated word, independent of gzip container')
  if name=='construct-literal-t370':
   for n in ['FILL.json.gz','ORDER.json','DISPATCH.json']:need(read(lifted/n)==read(P/'allocation'/n),'entire regenerated literal allocation '+n)
  if name=='append-authenticated-source-stage':need(sha(derived/'MANIFEST.json')=='1e25927e0f1b4a088819e42d59fcf7909298a3e9bb7d52f3e435f11401a84003','complete composed source identity')
 result=read(candidate/'RESULT.json');release=read(candidate/'release/RELEASE-RECEIPT.json');claim=read(P/'CLAIM.json')
 need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'and release['status']=='PASS_RELEASE','complete fresh admission and release')
 need(Q(result['kappa'])==Q(release['kappa_decimal'])==Q(claim['kappa']),'exact headline')
 need(result['source_manifest_sha256']==claim['source_manifest_sha256']and result['fill_sha256']==sha(P/'allocation/FILL.json.gz'),'actual source/fill bindings')
 need(tree(P)==pins,'package remains immutable')
 write(work/'RESULT.json',{'status':'PASS_COMPOSED_NORMAL45_FOURTEEN_REWRITES_COMPLETE_REPLAY','kappa':claim['kappa'],'fresh_changed_native_providers':2,'explicit_retained_reuse':bool(a.retained),'fresh_retained_bootstrap':not bool(a.retained),'source_manifest_sha256':claim['source_manifest_sha256'],'native_receipt_sha256':sha(native/'NATIVE-RECEIPT.json'),'admission_result_sha256':sha(candidate/'RESULT.json'),'release_receipt_sha256':sha(candidate/'release/RELEASE-RECEIPT.json'),'stages':stages,'scope':'Conditional finite supplier and modern outer certificate. The inherited all-size/compiler and analytic hypotheses remain.'})
 print('PASS_COMPOSED_NORMAL45_FOURTEEN_REWRITES_COMPLETE_REPLAY',claim['kappa'],flush=True)
if __name__=='__main__':main()
