#!/usr/bin/env python3
"""Cold replay of retained parent, fresh natives, new global invoice and outer ledger."""
import argparse,concurrent.futures,hashlib,json,os,shutil,subprocess,sys,time,threading
from fractions import Fraction as Q
from pathlib import Path
import sys as _sys
_sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source-partner-lifetimes'))
from build import HERE,build,read,write,need

def full(work,fill,resume_parent=False):
 if not __debug__:raise RuntimeError('Assertions are required')
 if resume_parent:
  p=work/'build/derivative'
  need(p.is_dir() and not (work/'STAGES.json').exists(),'resume only at in-progress first parent stage')
  for tag in ['base','extra']:
   need(read(p/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz')==read(HERE/f'evidence/eight-alias-{tag}.json.gz'),'resume word '+tag)
  need(read(p/'PROFILE.json')==read(HERE/'PROFILE.json'),'unchanged build profile before candidate lift')
 else:
  work.mkdir(parents=True,exist_ok=False);p=build(work/'build')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',AUDIT_FAST_SHARDS='4')
 for k in ['PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD']:env.pop(k,None)
 stages=[];stage_lock=threading.Lock()
 def run(name,script,*args):
  cmd=[sys.executable,'-B',str(script),*map(str,args)];start=time.monotonic()
  with (work/(name+'.log')).open('w') as log:r=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
  with stage_lock:
   stages.append(dict(name=name,command=cmd,exit_code=r.returncode,seconds=time.monotonic()-start,script_sha256=hashlib.sha256(Path(script).read_bytes()).hexdigest(),log_sha256=hashlib.sha256((work/(name+'.log')).read_bytes()).hexdigest()))
   write(work/'STAGES.json',stages)
  need(r.returncode==0,'failed '+name+'; see '+str(work/(name+'.log')));print('PASS',name,flush=True)
 def parent():
  if not resume_parent:return run('retained-parent',p/'vendor/pr1297/verify.py','--work',work/'parent')
  # Continue the actual fresh child process started by the previous driver.
  # No parent check is skipped: its complete result and native input bindings
  # must arrive before this stage can pass.
  deadline=time.monotonic()+3600;receipt=work/'parent/RESULT.json'
  while not receipt.exists():
   need(time.monotonic()<deadline,'continued parent replay did not finish');time.sleep(5)
  result=read(receipt)
  need(result['status']=='PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION','continued full parent status')
  need(all(s['exit_code']==0 for s in result['stages']),'continued parent stages')
  for tag,name in [('base','gauge44-word.json.gz'),('extra','extra-word.json.gz')]:
   need(read(work/f'parent/native-{tag}/local/FULL-WORD.json.gz')==read(p/'vendor/pr1297'/name),'continued parent native input '+tag)
  with stage_lock:
   stages.append(dict(name='retained-parent',exit_code=0,execution='Continuation of the fresh child started before the driver was restarted to parallelize independent native checks',result_sha256=hashlib.sha256(receipt.read_bytes()).hexdigest(),script_sha256=hashlib.sha256((p/'vendor/pr1297/verify.py').read_bytes()).hexdigest(),log_sha256=hashlib.sha256((work/'retained-parent.log').read_bytes()).hexdigest()))
   write(work/'STAGES.json',stages)
  print('PASS retained-parent',flush=True)
 def native(tag):run('native-'+tag,p/'new/run_native_borrow.py',p/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz',work/('native-'+tag))
 # Independent checks use separate work directories; no generated files overlap.
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  futures=[pool.submit(parent)]+[pool.submit(native,tag) for tag in ['base','extra']]
  for future in futures:future.result()
 # Native inputs are fixed PR2530 words. Only whole-call hosting changes.
 print('NATIVES_COMPLETE_WAITING_FOR_LITERAL_FILL',str(fill),flush=True)
 deadline=time.monotonic()+1800
 while not fill.exists():
  need(time.monotonic()<deadline,'no candidate fill arrived within bounded search')
  time.sleep(10)
 orderfile=fill.with_name('CANDIDATE-ORDER.json')
 need(orderfile.exists(),'candidate order sidecar')
 order_hash=hashlib.sha256(orderfile.read_bytes()).hexdigest()
 shutil.copy2(orderfile,p/'new/borrow-fill/ORDER.json')
 fill_bytes=fill.read_bytes();fill_hash=hashlib.sha256(fill_bytes).hexdigest()
 shutil.copy2(fill,p/'new/borrow-fill/FILL.json.gz')
 run('candidate-owner-reconstruction',p/'reconstruct.py','--out',work/'candidate-owners')
 run('candidate-parent-lift',p/'lift_parent.py','--owners',work/'candidate-owners','--out',work/'candidate-parent')
 for n in ['PLAN.json','OWNERS.json.gz','DISPATCH.json','PROFILE.json','CONSTRUCTION.json','GLOBAL-TEMPLATE.json.gz','SPEC.json']:shutil.copy2(work/'candidate-parent'/n,p/n)
 for n in ['PLAN.json','PROFILE.json','SPEC.json']:shutil.copy2(work/'candidate-parent'/n,p/'new'/n)
 for name in ['SPEC.json','new/SPEC.json']:
  z=read(p/name);z['outer_refinement']=dict(endpoint_digits=24,grid_digits=18,margin_digits=28,bootstrap_steps=12);z['expected']['live']=66304;write(p/name,z)
 original_profile=read(HERE/'PROFILE.json');candidate_profile=read(p/'PROFILE.json')
 need(candidate_profile!=original_profile,'candidate must change paid profile')
 need(sum(int(r)*n for r,n in candidate_profile.items())==4816512,'candidate rank mass')
 run('rebind',p/'new/rebind.py',p,work/'native-base/local',work/'native-extra/local',work/'rebound')
 runtime=work/'parent/layout/source_partners';runtime.mkdir()
 for n in ['replay.py','freeze_spec.py','audit_mixed.py','independent_core.py','geometry_controls.py','audit_fast.py']:shutil.copy2(p/n,runtime/n)
 for n in ['code','construction','inputs']:shutil.copytree(p/n,runtime/n)
 shutil.copytree(work/'rebound',runtime/'candidate');shutil.copytree(work/'native-extra',runtime/'native-extra')
 data=runtime/'candidate'
 run('discover',runtime/'replay.py','--data',data,'--work',work/'discovery','--local',work/'native-base/local','--discover')
 run('strict',runtime/'replay.py','--data',data,'--work',work/'strict','--local',work/'native-base/local')
 run('geometry-controls',runtime/'geometry_controls.py','--source',work/'parent/layout/joint1148-round45/source/research/complex-k492-owner-repair/vendor/multicold','--strict',work/'strict','--out',work/'GEOMETRY-CONTROLS.json')
 result=read(work/'strict/RESULT.json');need(result['status']=='PASS_STRICT_MIXED_T74_EXACT_FILL','strict status')
 for n in ['PLAN.json','PROFILE.json','SPEC.json']:shutil.copy2(data/n,p/'new'/n)
 write(p/'CLAIM.json',dict(kappa=result['kappa'],scope='Conditional finite construction; inherited interfaces remain.'))
 spec=read(p/'new/SPEC.json');C=Q(spec['expected']['complex_lower']);DIG=spec['outer_refinement']['endpoint_digits']
 write(p/'outer/B.json',dict(b=str(C-Q(1,10**(DIG+80))),b_above_endpoint=str(C+Q(1,10**DIG)),profile=spec['expected']['global_profile'],live=spec['expected']['live']))
 for name in ['check_ledger.py','independent_check.py']:run('outer-'+name,p/'outer'/name)
 run('outer-evidence',p/'outer/run_outer.py',work/'outer-replay')
 ledger=read(p/'outer/LEDGER.json');k=Q(ledger['rows']['struct_boundary_radix_union']['kappa']['rational'])
 previous=read(work/'build/source/research/gmx-t74-borrow43-handoff/outer/OUTER-CLAIM.json');need(k>Q(previous['kappa']),'strict improvement over pinned PR2462')
 comparison=HERE/'evidence/PR2474-OUTER-CLAIM.json'
 need(hashlib.sha256(comparison.read_bytes()).hexdigest()==read(HERE/'LATEST-COMPARISON.json')['sha256'],'PR2474 comparison pin')
 need(k>Q(read(comparison)['kappa']),'strict improvement over PR2474')
 need(ledger['profile']==spec['expected']['global_profile'] and ledger['W']==66304,'outer supplier binding')
 need(C>Q(read(HERE/'CLAIM.json')['complex_lower']),'strict certified endpoint improvement over PR2530')
 need(k>Q(read(HERE/'CLAIM.json')['kappa']),'strict outer improvement over PR2530')
 need(ledger['profile']==candidate_profile,'literal candidate profile binding')
 need(hashlib.sha256(fill.read_bytes()).hexdigest()==fill_hash,'candidate fill unchanged during replay')
 need(hashlib.sha256(orderfile.read_bytes()).hexdigest()==order_hash,'candidate order unchanged during replay')
 receipt=dict(status='PASS_RESIDUAL_EXCHANGE_COMPLETE_FINITE_ADMISSION_AND_OUTER',candidate_fill_sha256=fill_hash,comparison_pr2530=read(HERE/'CLAIM.json')['kappa'],kappa=str(k),complex_lower=str(C),previous_kappa=previous['kappa'],gain=str(k-Q(previous['kappa'])),
  source_commit='ef34071fee6dfb0286e9850a5cec4e36d9eb126d',predecessor_pr2530_head='b4012098048e12500b2d33d2e84be281915a27ac',global_profile=ledger['profile'],supplier=result,
  outer_checks=len(ledger['rows']['struct_boundary_radix_union']['strict_checks']),outer_controls=len(ledger['rejecting_controls']['struct_boundary_radix_union']),stages=stages,
  scope='Conditional finite construction and exact outer arithmetic; no independent human review or complete multiplication theorem.')
 write(work/'RESULT.json',receipt);print(receipt['status'],str(k),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--fill',type=Path,required=True);ap.add_argument('--resume-in-progress-parent',action='store_true');a=ap.parse_args();full(a.work.resolve(),a.fill.resolve(),a.resume_in_progress_parent)
