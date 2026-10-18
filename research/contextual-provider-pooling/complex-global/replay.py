"""Portable mixed-provider finite-clone controller and independent physical invoice."""
from pathlib import Path
import argparse,json,shutil,subprocess,sys,time,os
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--providers',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
P=Path(__file__).resolve().parent;v=P/'vendor531';q=P/'vendor535';out=a.out.resolve();assert not out.exists();out.mkdir(parents=True)
locations=json.loads(a.providers.read_text());assert set(locations)=={'n0','n2','n6','n8'}
# Resolve input locations once; the execution template records hashes and programs, not these paths.
locations={k:str((a.providers.resolve().parent/Path(v)).resolve())for k,v in locations.items()}
providers=out/'PROVIDERS.json';providers.write_text(json.dumps(locations,indent=2)+'\n',encoding='utf8',newline='\n')
launcher=P/'run_portable.py';stages=[]
controller=out/'controller-input';shutil.copytree(v/'inputs/data-base',controller);(controller/'split-centres').mkdir(exist_ok=True)
shutil.copyfile(q/'inputs/ROUND20-PARENT-TEMPLATE.json.gz',controller/'split-centres/GLOBAL-TEMPLATE.json.gz')
shutil.copyfile(v/'evidence/local/CANONICAL-WORD.json.gz',controller/'split-centres/CANONICAL-WORD.json.gz')
for f in controller.rglob('*'):
 if f.is_file()and f.suffix in('.json','.py','.md','.txt'):f.write_bytes(f.read_bytes().replace(b'\r\n',b'\n'))
source_plan=out/'SOURCE-PLAN.json';source_plan.write_bytes((P/'inputs558/PLAN.json').read_bytes().replace(b'\r\n',b'\n'))
def run(name,script,*args):
 t=time.monotonic();log=out/(name+'.log');print('RUN',name,flush=True)
 with log.open('w',encoding='utf8',newline='\n')as f:z=subprocess.run([sys.executable,'-B',str(launcher),str(script),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1'))
 stages.append({'name':name,'seconds':time.monotonic()-t,'exit':z.returncode});(out/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n',encoding='utf8',newline='\n')
 if z.returncode:print(log.read_text(encoding='utf8'),flush=True);raise SystemExit(name+' failed')
 print('PASS',name,flush=True)
source=out/'source-base';mixed=out/'mixed72';clone=out/'clone';base=clone/'base';hosted=out/'hosted';audit=out/'audit';audit.mkdir()
run('01-bind',v/'code/prepare_supplier_base.py','--data-base',controller,'--local',locations['n0'],'--out',source)
run('02-mixed-selector',P/'build_mixed72.py','--owners',P/'inputs558/OWNERS.json.gz','--plan',source_plan,'--providers',providers,'--out',mixed)
run('03-clone',P/'build_mixed_clone.py','--base',source,'--owners',mixed/'OWNERS.json.gz','--plan',mixed/'PLAN.json','--out',clone)
run('04-source-lift',P/'audit_clone_lift.py','--source-base',source,'--clone-base',base,'--output',audit/'CLONE-LIFT.json','--mutation-controls')
run('05-emit',P/'emit_mixed.py','--base',base,'--owners',clone/'OWNERS.json.gz','--plan',clone/'PLAN.json','--providers',providers,'--out',hosted)
run('06-physical',P/'audit_mixed.py',base,hosted,audit/'ASYNC-AUDIT.json','--providers',providers,'--mutation-controls')
run('07-invoice',P/'invoice_mixed.py','--base',base,'--hosted',hosted,'--audit',audit,'--out',audit,'--providers',providers,'--retained-invoice',v/'evidence/audit/PREFIX-AND-INVOICE.json')
r=json.loads((audit/'ASYNC-AUDIT.json').read_text());z={'status':'PASS_MIXED_PROVIDER_WHOLE_OWNER_PHYSICAL_AND_FINITE_INVOICE','complex_template_sha256':r['template_sha256'],'source_base':'source-base','base':'clone/base','hosted':'hosted','audit':'audit','providers':'PROVIDERS.json','live':r['complex_live'],'profile':r['complex_profile'],'deficit':r['deficit'],'stages':stages,'scope':'Fresh source-bound local providers, deterministic per-call selector and finite clone pooling; exact all47 scalar assembly is performed by the top-level verifier.'}
(out/'RESULT.json').write_text(json.dumps(z,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(z,indent=2))
