#!/usr/bin/env python3
"""Cold replay of retained parent, fresh natives, new global invoice and outer ledger."""
import argparse,concurrent.futures,hashlib,json,os,shutil,subprocess,sys,time
from fractions import Fraction as Q
from pathlib import Path
from build import HERE,build,read,write,need

def full(work):
 work.mkdir(parents=True,exist_ok=False);p=build(work/'build')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',AUDIT_FAST_SHARDS='4')
 for k in ['PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD']:env.pop(k,None)
 stages=[]
 def run(name,script,*args):
  cmd=[sys.executable,'-B',str(script),*map(str,args)];start=time.monotonic()
  with (work/(name+'.log')).open('w') as log:r=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
  stages.append(dict(name=name,command=cmd,exit_code=r.returncode,seconds=time.monotonic()-start,script_sha256=hashlib.sha256(Path(script).read_bytes()).hexdigest()))
  write(work/'STAGES.json',stages);need(r.returncode==0,'failed '+name+'; see '+str(work/(name+'.log')));print('PASS',name,flush=True)
 run('retained-parent',p/'vendor/pr1297/verify.py','--work',work/'parent')
 def native(tag):run('native-'+tag,p/'new/run_native_borrow.py',p/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz',work/('native-'+tag))
 for tag in ['base','extra']:native(tag)
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
 need(C==Q(read(HERE/'CLAIM.json')['complex_lower']),'source-bound certified endpoint')
 receipt=dict(status='PASS_SOURCE_PARTNERS_COMPLETE_FINITE_ADMISSION_AND_OUTER',kappa=str(k),complex_lower=str(C),previous_kappa=previous['kappa'],gain=str(k-Q(previous['kappa'])),
  source_commit='ef34071fee6dfb0286e9850a5cec4e36d9eb126d',global_profile=ledger['profile'],supplier=result,
  outer_checks=len(ledger['rows']['struct_boundary_radix_union']['strict_checks']),outer_controls=len(ledger['rejecting_controls']['struct_boundary_radix_union']),stages=stages,
  scope='Conditional finite construction and exact outer arithmetic; no independent human review or complete multiplication theorem.')
 write(work/'RESULT.json',receipt);print(receipt['status'],str(k),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();full(a.work.resolve())
