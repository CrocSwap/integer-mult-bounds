"""Bind two verified providers, reconstruct physical owners, and admit the invoice.
Prepared with OpenAI Codex assistance; Apache-2.0. No optimization or discovery.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time
if not __debug__:raise RuntimeError('Assertions required')
P=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dump=lambda p,x:p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--parent',type=Path,required=True);ap.add_argument('--prefixk',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
 w=a.work.resolve();assert not w.exists();w.mkdir();(w/'logs').mkdir()
 parent=a.parent.resolve();assert read(parent/'RESULT.json')['kappa_decimal']=='0.001600770286423653'
 assert read(parent/'RECEIPT.json')['manifest_sha256']==sha(P/'vendor/pr575/MANIFEST.json')
 s=P/'vendor/pr575';code=P/'code';g=w/'global';spec=read(P/'data/WITNESS-SPEC.json')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',GAIN_PR564_SOURCE=str(s),WITNESS_SPEC=str(P/'data/WITNESS-SPEC.json'));env.pop('WITNESS_DISCOVER',None);env.pop('PYTHONOPTIMIZE',None)
 start=time.monotonic();steps=[]
 def run(name,script,*args):
  cmd=[sys.executable,'-B',str(s/'code/run_portable.py'),str(script),*map(str,args)];log=w/'logs'/(name+'.log');t=time.monotonic();print('RUN',name,flush=True)
  with log.open('w',encoding='utf-8',newline='\n')as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
  steps.append(dict(name=name,command=cmd,seconds=time.monotonic()-t,exit_code=r.returncode,script_sha256=sha(script),log_sha256=sha(log)));dump(w/'STAGES.json',steps)
  if r.returncode:raise RuntimeError(name+' failed\n'+log.read_text()[-6000:])
  print('PASS',name,flush=True)
 run('bind-proof-content',code/'bind_providers_portable.py','--baseline',parent/'baseline558','--provider','prefix_eight='+str(parent/'eightcold-local'),'--provider','prefixk_eight='+str(a.prefixk.resolve()),'--plan',P/'data/PLAN.json','--out',g)
 run('emit-literal-owners',code/'emit_allcold.py','--base',g/'base','--owners',P/'data/OWNERS.json.gz','--plan',g/'PLAN.json','--out',g/'hosted')
 (g/'audit').mkdir()
 run('independent-physical-audit',code/'audit_allcold.py',g/'base',g/'hosted',g/'audit/ASYNC-AUDIT.json','--mutation-controls')
 assert len(read(g/'audit/ASYNC-AUDIT.json')['mutations_rejected'])==spec['expected']['mutations_rejected']
 run('fresh-finite-invoice',code/'invoice_allcold.py','--base',g/'base','--hosted',g/'hosted','--audit',g/'audit','--out',g/'audit','--retained-invoice',s/'vendor/pr558/vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json')
 run('both-exact-models',code/'assemble.py',s,g,w/'ASSEMBLY.json')
 run('assembly-mutation-controls',code/'assembly_controls.py','--source-package',s,'--owner',g/'audit/OWNERS-AND-PROFILE.json','--invoice',g/'audit/PREFIX-AND-INVOICE.json','--out',w/'ASSEMBLY-CONTROLS.json')
 assert len(read(w/'ASSEMBLY-CONTROLS.json')['rejected_controls'])==106
 run('phase-timing-controls',code/'phase_timing_controls.py',s,g/'base',g/'audit',w/'PHASE-TIMING-CONTROLS.json')
 run('actual-recompression-controls',code/'generated_identity_controls.py','--base',g/'base','--audit',g/'audit','--out',w/'GENERATED-IDENTITY-CONTROLS.json')
 assert read(w/'GENERATED-IDENTITY-CONTROLS.json')['counts']==dict(recompression_accepted=2,semantic_rejected=18,reference_or_metadata_rejected=18)
 z=read(w/'ASSEMBLY.json')
 for key in ('kappa_decimal','complex_lower','conservative_complex_lower','conservative_kappa_decimal'):assert z[key]==spec['expected'][key]
 result={k:z[k]for k in('kappa','kappa_decimal','complex_lower','conservative_complex_lower','conservative_kappa_decimal','complex_profile','provider_counts')};result['status']='PASS_TWO_PROVIDER_JOINT_PREFIX_KERNEL_ADMISSION';dump(w/'RESULT.json',result)
 files=['RESULT.json','ASSEMBLY.json','ASSEMBLY-CONTROLS.json','PHASE-TIMING-CONTROLS.json','GENERATED-IDENTITY-CONTROLS.json','global/BINDING.json','global/audit/ASYNC-AUDIT.json','global/audit/OWNERS-AND-PROFILE.json','global/audit/PREFIX-AND-INVOICE.json']
 dump(w/'RECEIPT.json',dict(status=result['status'],seconds=time.monotonic()-start,steps=steps,artifacts={n:sha(w/n)for n in files},parent_receipt_sha256=sha(parent/'RECEIPT.json'),spec_sha256=sha(P/'data/WITNESS-SPEC.json')));print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
