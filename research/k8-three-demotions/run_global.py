"""Replay a changed local word on the pinned, independently checked T16 geometry.

Only the driver is new. Every admission, invoice, arithmetic, mutation and
independent-window engine is byte-identical to the credited PR1074 source.
"""
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,time
from fractions import Fraction as Q
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];PRE=ROOT/'research/k8-eight-ends-t16'
def rd(p):
 p=Path(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')

def main():
 assert __debug__
 ap=argparse.ArgumentParser();ap.add_argument('--local',type=Path,required=True);ap.add_argument('--parent-work',type=Path,required=True);ap.add_argument('--data',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--discover',action='store_true');a=ap.parse_args()
 local,parent,data,work=[p.resolve() for p in [a.local,a.parent_work,a.data,a.work]];assert not work.exists();work.mkdir(parents=True)
 assert rd(parent/'RESULT.json')['status']=='PASS_K8_EIGHT_ENDS_T16_COMPLETE_ADMISSION'
 for rel,h in rd(P/'PARENT-PINS.json').items():assert sha(parent/rel)==h,rel
 plan=rd(data/'PLAN.json');old=rd(PRE/'PLAN.json.gz');spec=rd(data/'SPEC.json');word=rd(local/'CANONICAL-WORD.json.gz')
 for key in ('K','T','M','L','live','deficit','order','windows','sides','pairs','replica_lift'):assert plan[key]==old[key],('geometry changed',key)
 for oldcall,newcall in zip(old['provider_calls'],plan['provider_calls']):
  assert {k:v for k,v in oldcall.items() if k!='local_program_sha256'}=={k:v for k,v in newcall.items() if k!='local_program_sha256'}
 assert len(plan['provider_calls'])==len(old['provider_calls'])==144
 assert word['ports']==old['provider_registry']['gauge44']['ports'] and word['centers']==old['provider_registry']['gauge44']['centers']
 runtime=work/'runtime';shutil.copytree(PRE/'vendor/pr1074',runtime,ignore=shutil.ignore_patterns('__pycache__'))
 for name in ('PLAN.json','OWNERS.json.gz','SPEC.json'):shutil.copy2(data/name,runtime/'data'/name)
 data=runtime/'data'
 source=ROOT/'research/complex-k492-owner-repair/vendor/multicold';vendor=source/'vendor/pr558/vendor/pr552/complex-global/vendor531'
 for rel,h in rd(runtime/'data/UPSTREAM-PINS.json').items():assert sha(ROOT/rel)==h,rel
 for rel,pins in rd(PRE/'UPSTREAM.json')['files'].items():assert sha(runtime/rel)==pins['sha256']
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',MULTICOLD_SOURCE=str(source),GAIN_PR564_SOURCE=str(source))
 for k in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD','WITNESS_SPEC'):env.pop(k,None)
 env['WITNESS_SPEC']=str(data/'SPEC.json')
 if a.discover:env.update(WITNESS_DISCOVER='1',WITNESS_RECORD=str(work/'WITNESS-RECORD.jsonl'))
 stages=[]
 def run(name,script,*args,extra=None):
  t=time.monotonic();log=work/(name+'.log')
  with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(source/'code/run_portable.py'),str(script),*map(str,args)],cwd=ROOT,env=dict(env,**(extra or {})),stdout=f,stderr=subprocess.STDOUT)
  stages.append(dict(step=name,exit_code=r.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)));dump(work/'STAGES.json',stages);assert r.returncode==0,(name,log.read_text()[-6000:]);print('PASS',name,flush=True)
 code=runtime/'code';g=work/'global'
 run('bind',code/'bind_providers_portable.py','--baseline',parent/'t16/parent16','--provider','gauge44='+str(local),'--plan',data/'PLAN.json','--out',g)
 run('emit',code/'emit_allcold.py','--base',g/'base','--owners',data/'OWNERS.json.gz','--plan',g/'PLAN.json','--out',g/'hosted')
 run('audit',code/'audit_allcold.py',g/'base',g/'hosted',g/'audit/ASYNC-AUDIT.json','--mutation-controls')
 run('invoice',code/'invoice_allcold.py','--base',g/'base','--hosted',g/'hosted','--audit',g/'audit','--out',g/'audit','--retained-invoice',vendor/'evidence/audit/PREFIX-AND-INVOICE.json')
 run('assembly',code/'assemble.py',source,g,work/'ASSEMBLY.json')
 if a.discover:
  print('NOMINATED',rd(work/'ASSEMBLY.json')['kappa_decimal']);return
 for name,script,out in [('admission-controls','assembly_controls.py','ADMISSION-CONTROLS.json'),('bit-supplier-controls','bit_supplier_controls.py','BIT-SUPPLIER-CONTROLS.json')]:
  run(name,code/script,'--source-package',source,'--owner',g/'audit/OWNERS-AND-PROFILE.json','--invoice',g/'audit/PREFIX-AND-INVOICE.json','--out',work/out)
 run('independent-t16',runtime/'t16/indep16.py','--baseline-parent',parent/'t16/global8/base/split-centres/GLOBAL-TEMPLATE.json.gz','--owners',data/'OWNERS.json.gz','--word',local/'CANONICAL-WORD.json.gz','--out',work/'INDEPENDENT-T16.json',extra={'T16_EXPECTED_IDLE':json.dumps(spec['expected']['idle_remainder_profile']),'T16_EXPECTED_WIDTHS':json.dumps(spec['providers']['gauge44']['inventory'])})
 asm=rd(work/'ASSEMBLY.json');ind=rd(work/'INDEPENDENT-T16.json');inv=rd(g/'audit/PREFIX-AND-INVOICE.json');owner=rd(g/'audit/OWNERS-AND-PROFILE.json');audit=rd(g/'audit/ASYNC-AUDIT.json');ac=rd(work/'ADMISSION-CONTROLS.json');bc=rd(work/'BIT-SUPPLIER-CONTROLS.json')
 assert asm['status']=='PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY' and asm['kappa']==spec['expected']['kappa']
 assert len(ac['rejected_controls'])==69 and not ac['discovery_accepted_controls']
 assert len(bc['rejected_controls'])==12 and bc['derived_deficit']==10272
 assert len(ind['controls_rejected'])==6 and ind['status']=='PASS_INDEPENDENT_T16_LITERAL_WINDOWS_CHARTS_PREFIX_ROW'
 assert ind['profile']==asm['complex_profile']==plan['profile']
 assert ind['rank_mass']==owner['rank_mass']==1041408 and ind['deficit']==owner['deficit']==5120
 assert ind['roles']==owner['hosted_residuals']==audit['complex_hosted_residuals']==69120
 assert ind['calls']==audit['complete_invocations']==inv['complete_invocation_sweeps']==144
 assert audit['mutation_controls_run'] and len(audit['mutations_rejected'])==15
 assert ind['actual_73_axis_charts']==owner['actual_73column_sigmas']==audit['actual_orthogonal_73column_maps']
 assert ind['prefix_bits']==inv['global_prefix_bits']<inv['charged_prefix_bits']==512
 assert ind['physical_row_coefficient']==inv['finite']['physical_row_coefficient']<inv['finite']['retained_row_coefficient']==20161
 assert inv['strict_checks'] and all(inv['strict_checks'].values())
 assert len(asm['outer'])==47 and all(Q(v)>0 for v in asm['outer'].values())
 for name in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','RESIDUAL-ADAPTERS.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json'):
  assert rd(g/'base/providers/gauge44'/name)==rd(local/name),name
 assert asm['template_sha256']==owner['template_sha256']==inv['template_sha256']
 assert inv['owner_audit_sha256']==sha(g/'audit/OWNERS-AND-PROFILE.json') and inv['controller_audit_sha256']==sha(g/'audit/ASYNC-AUDIT.json')
 assert Q(asm['kappa'])>Q(rd(PRE/'CLAIM.json')['kappa'])
 result=dict(status='PASS_CHANGED_LOCAL_INTERFACES_STRICT_T16_ADMISSION',kappa=asm['kappa'],kappa_decimal=asm['kappa_decimal'],complex_lower=asm['complex_lower'],bit_lower=asm['bit_lower'],profile=asm['complex_profile'],idle=ind['idle'],controls=dict(admission=69,bit_supplier=12,independent_t16=6,controller=15),outer_strict_inequalities=47,steps=stages)
 dump(work/'REPLAY.json',result);print(result['status'],result['kappa_decimal'])

if __name__=='__main__':main()
