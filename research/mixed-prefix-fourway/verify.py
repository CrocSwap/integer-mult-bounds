#!/usr/bin/env python3
"""Cold replay of four verified local suppliers and their new whole-owner allocation.
Prepared with OpenAI Codex assistance; Apache-2.0. Standard library only.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,time
if not __debug__:raise RuntimeError('Assertions required; optimized verification is disabled')
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw)if p.suffix=='.gz'else raw)
def dump(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();w=a.work.resolve()
 assert not w.exists()and not w.is_relative_to(P),'Use a new external output directory'
 manifest=read(P/'MANIFEST.json');actual={p.relative_to(P).as_posix():sha(p)for p in P.rglob('*')if p.is_file()and p!=P/'MANIFEST.json'and '__pycache__'not in p.parts};assert actual==manifest
 for vendor,record in read(P/'SOURCE-PINS.json').items():
  for name,pin in record['files'].items():
   raw=(P/'vendor'/vendor/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==pin['sha256'];assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob']
 expected=read(P/'EXPECTED.json');parent=P/'vendor/pr572';u=parent/'vendor/pr568';b=u/'vendor/pr558';f=b/'vendor/pr552';v=f/'complex-global/vendor531';gk=f/'complex-local/static44/gk';code=P/'code';p569=P/'vendor/pr569/providers';p571=P/'vendor/pr571/frontier-composition'
 assert sha(parent/'MANIFEST.json')==expected['parent_manifest_sha256'] and sha(P/'CONTRACTS.json')==expected['contracts_sha256']
 w.mkdir();(w/'logs').mkdir();start=time.monotonic();steps=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
 def execute(name,script,*args,portable=True,optimized=False):
  cmd=[sys.executable,'-B']
  if optimized:assert not portable;cmd+=['-O']
  if portable:cmd+=[str(u/'code/run_portable.py')]
  cmd+=[str(script),*map(str,args)];log=w/'logs'/(name+'.log');began=time.monotonic();print('RUN',name,flush=True)
  with log.open('w',encoding='utf-8',newline='\n')as output:r=subprocess.run(cmd,stdout=output,stderr=subprocess.STDOUT,env=env)
  row=dict(name=name,command=cmd,script_sha256=sha(script),exit_code=r.returncode,seconds=time.monotonic()-began,log_sha256=sha(log))
  if r.returncode:raise RuntimeError(name+' failed\n'+log.read_text()[-6000:])
  print('PASS',name,flush=True);return row
 def run(*args,**kwargs):
  row=execute(*args,**kwargs);steps.append(row);dump(w/'STAGES.json',steps)
 parent_out=w/'parent572';run('full-pinned572-cold-replay',parent/'verify.py','--work',parent_out,portable=False)
 assert read(parent_out/'RESULT.json')['kappa_decimal']=='0.001600535778621932'
 baseline=parent_out/'baseline568';original=baseline/'eight-cold-word/FULL-WORD.json.gz';four=w/'four-word';local4=w/'four-local';prefix=w/'prefix-word';localp=w/'prefix-local';selection=baseline/'baseline558/reconstruction/static44/SELECTION.json'
 recipes=[p569/'fourcold-eight/recipes'/('candidate-%03d.json'%i)for i in range(3)];recipe_args=[x for p in recipes for x in ('--recipe',p)]
 run('construct-four-cold',p569/'build_suffix_kernels.py','--word',original,'--gk-dir',gk,*recipe_args,'--out',four)
 run('independent-four-cold-composition',p569/'audit_suffix_composition.py','--source',original,'--word',four/'FULL-WORD.json.gz',*recipe_args,'--out',four/'INDEPENDENT-COMPOSITION.json',portable=False,optimized=True)
 assert len(read(four/'INDEPENDENT-COMPOSITION.json')['negative_controls_rejected'])==3
 shutil.copyfile(baseline/'eight-multicold-word/PROMOTION.json',four/'PROMOTION.json')
 for pivot in ['extra-506','extra-518','extra-530','inherited-494']:
  out=four/(pivot+'-omissions.json');run('four-'+pivot+'-omissions',u/'code/audit_kernel_controls.py','--word',four/'FULL-WORD.json.gz','--recipe',p569/'fourcold-eight/controls'/(pivot+'-recipe.json'),'--out',out);assert len(read(out)['controls'])==6
 run('four-static44-omissions',f/'complex-local/static44/audit_scalar.py',four/'FULL-WORD.json.gz',selection,four/'STATIC44-SCALAR-AUDIT.json');assert len(read(four/'STATIC44-SCALAR-AUDIT.json')['controls'])==44
 run('four-rank5-omissions',b/'code/audit_promoted_scalar.py',four/'FULL-WORD.json.gz',selection,four/'PROMOTED-SCALAR-AUDIT.json');assert len(read(four/'PROMOTED-SCALAR-AUDIT.json')['controls'])==8
 run('compose-joint-prefix',p571/'compose_prefix.py','--base',p569/'width7/eight/FULL-WORD.json.gz','--prefix',p571/'prefix-input/FULL-WORD.json.gz','--combined',parent_out/'width7-word/FULL-WORD.json.gz','--gk-dir',gk,'--out',prefix)
 run('prefix-all-kernel-omissions',u/'code/audit_multicold_controls.py','--word',prefix/'FULL-WORD.json.gz','--recipe',p571/'combined-prefix-word/ALL-KERNEL-OMISSIONS.json','--out',prefix/'ALL-KERNEL-CONTROLS.json');assert len(read(prefix/'ALL-KERNEL-CONTROLS.json')['controls'])==135
 shutil.copyfile(baseline/'eight-multicold-word/PROMOTION.json',prefix/'PROMOTION.json')
 run('prefix-rank5-omissions',b/'code/audit_promoted_scalar.py',prefix/'FULL-WORD.json.gz',selection,prefix/'PROMOTED-SCALAR-AUDIT.json');assert len(read(prefix/'PROMOTED-SCALAR-AUDIT.json')['controls'])==8
 locals=[('four',four,local4,2929),('prefix',prefix,localp,3004)]
 for name,word,local,edges in locals:
  run(name+'-all-columns-native',v/'code/audit_and_transport.py','--raw',word/'FULL-WORD.json.gz','--routing',f/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz','--out',local)
  run(name+'-reflected-ledgers',v/'code/emit_local.py',local)
  run(name+'-independent-local',v/'code/audit_local.py',local);assert len(read(local/'INDEPENDENT-LOCAL-REPLAY.json')['negative_controls_rejected'])==11
  run(name+'-normalized-wrappers',v/'code/adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
 # Independent expensive phase checks write disjoint files. Parent records each completed result.
 with ThreadPoolExecutor(max_workers=2)as pool:
  jobs=[pool.submit(execute,name+'-all-phase-edges',b/'code/phases_full.py',local,v/'vendor/clifford')for name,_,local,_ in locals]
  for job in jobs:steps.append(job.result());dump(w/'STAGES.json',steps)
 for _,_,local,edges in locals:
  phase=read(local/'CLIFFORD-REVIEW.json');assert phase['directed_edges']==edges and phase['endpoint_adapters']==224 and phase['all_child_equalities_include_global_phase']is True
 glob=w/'global'
 run('bind-four-fresh-providers',code/'bind_providers.py','--parent',parent_out,'--four',local4,'--prefix',localp,'--out',glob)
 run('emit-literal-owners',code/'emit_allcold.py','--base',glob/'base','--owners',P/'data/OWNERS.json.gz','--plan',glob/'PLAN.json','--out',glob/'hosted')
 run('independent-owners-and-controls',code/'audit_allcold.py',glob/'base',glob/'hosted',glob/'audit/ASYNC-AUDIT.json','--mutation-controls');assert len(read(glob/'audit/ASYNC-AUDIT.json')['mutations_rejected'])==16
 run('fresh-four-provider-invoice',code/'invoice_allcold.py','--base',glob/'base','--hosted',glob/'hosted','--audit',glob/'audit','--out',glob/'audit','--retained-invoice',v/'evidence/audit/PREFIX-AND-INVOICE.json')
 run('both-exact-assembly-models',code/'assemble.py',u,glob,glob/'ASSEMBLY.json')
 run('full-assembly-controls',code/'assembly_controls.py','--source-package',u,'--owner',glob/'audit/OWNERS-AND-PROFILE.json','--invoice',glob/'audit/PREFIX-AND-INVOICE.json','--out',glob/'ASSEMBLY-CONTROLS.json');assert len(read(glob/'ASSEMBLY-CONTROLS.json')['rejected_controls'])==109
 run('phase-timing-controls',code/'phase_timing_controls.py',u,glob/'base',glob/'audit',glob/'PHASE-TIMING-CONTROLS.json')
 run('actual-file-recompression-controls',code/'generated_identity_controls.py','--base',glob/'base','--audit',glob/'audit','--out',glob/'GENERATED-IDENTITY-CONTROLS.json');assert read(glob/'GENERATED-IDENTITY-CONTROLS.json')['counts']==dict(recompression_accepted=4,semantic_rejected=36,reference_or_metadata_rejected=36)
 result=read(glob/'ASSEMBLY.json');keys=['kappa','kappa_decimal','complex_lower','bit_lower','complex_profile','provider_counts','conservative_kappa','conservative_complex_lower'];assert all(result[k]==expected[k]for k in keys)
 stable=dict(status='PASS_FOUR_PROVIDER_MIXED_PREFIX_FULL_COLD_ADMISSION',**{k:result[k]for k in keys},controller_controls=16,assembly_controls=109,recompression_controls=4,generated_semantic_controls=36,generated_reference_controls=36,scope=result['scope']);dump(w/'RESULT.json',stable)
 files=['RESULT.json','global/ASSEMBLY.json','global/BINDING.json','global/ASSEMBLY-CONTROLS.json','global/PHASE-TIMING-CONTROLS.json','global/GENERATED-IDENTITY-CONTROLS.json','global/audit/ASYNC-AUDIT.json','global/audit/OWNERS-AND-PROFILE.json','global/audit/PREFIX-AND-INVOICE.json','four-local/INDEPENDENT-LOCAL-REPLAY.json','four-local/CLIFFORD-REVIEW.json','prefix-local/INDEPENDENT-LOCAL-REPLAY.json','prefix-local/CLIFFORD-REVIEW.json']
 dump(w/'RECEIPT.json',dict(status=stable['status'],source_manifest_sha256=sha(P/'MANIFEST.json'),parent_receipt_sha256=sha(parent_out/'RECEIPT.json'),steps=steps,artifacts={n:sha(w/n)for n in files},seconds=time.monotonic()-start));print(json.dumps(stable,indent=2),flush=True)
if __name__=='__main__':main()
