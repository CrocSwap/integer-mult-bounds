"""Fresh changed static44 complete-owner emission, controller audit and finite invoice."""
from pathlib import Path
import sys,json,gzip,shutil,subprocess,time,os
assert len(sys.argv)==8,'run_complex44.py V531 P535 LOCAL OWNERS PLAN PORTABLE_LAUNCHER OUT'
v,p,local,owners,plan,launcher,out=map(lambda x:Path(x).resolve(),sys.argv[1:]);assert not out.exists();out.mkdir(parents=True)
controller=out/'controller-input';shutil.copytree(v/'inputs/data-base',controller);(controller/'split-centres').mkdir(exist_ok=True)
shutil.copyfile(p/'inputs/ROUND20-PARENT-TEMPLATE.json.gz',controller/'split-centres/GLOBAL-TEMPLATE.json.gz')
shutil.copyfile(v/'evidence/local/CANONICAL-WORD.json.gz',controller/'split-centres/CANONICAL-WORD.json.gz')
# Text inputs are canonically copied, independent of Git checkout newlines.
for f in controller.rglob('*'):
 if f.is_file() and f.suffix in ('.json','.py','.md','.txt'):
  f.write_bytes(f.read_bytes().replace(b'\r\n',b'\n'))
plan_copy=out/'PLAN.json';plan_copy.write_bytes(plan.read_bytes().replace(b'\r\n',b'\n'));plan=plan_copy
bit_fixture=out/'PR510-EXPECTED.json';bit_fixture.write_bytes((p/'inputs/PR510-EXPECTED.json').read_bytes().replace(b'\r\n',b'\n'))
stages=[]
def run(name,script,*args):
 t=time.monotonic();log=out/(name+'.log');print('RUN',name,flush=True)
 with log.open('w',encoding='utf-8',newline='\n')as f:z=subprocess.run([sys.executable,'-B',str(launcher),str(script),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1'))
 stages.append(dict(name=name,seconds=time.monotonic()-t,exit=z.returncode));(out/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n',encoding='utf-8',newline='\n')
 if z.returncode:print(log.read_text(encoding='utf-8'),flush=True);raise SystemExit(name+' failed')
 print('PASS',name,round(stages[-1]['seconds'],2),flush=True)
run('01-bind',v/'code/prepare_supplier_base.py','--data-base',controller,'--local',local,'--out',out/'base')
run('02-emit',v/'code/emit_supplier_hosted.py','--base',out/'base','--owners',owners,'--plan',plan,'--out',out/'hosted')
audit=out/'audit';audit.mkdir()
run('03-physical',v/'code/audit_supplier_hosted.py',out/'base',out/'hosted',audit/'ASYNC-AUDIT.json','--mutation-controls')
run('04-invoice',v/'code/invoice_final.py','--base',out/'base','--hosted',out/'hosted','--audit',audit,'--out',audit,'--retained-invoice',v/'evidence/audit/PREFIX-AND-INVOICE.json')
run('05-moments',p/'code/assemble_combined.py',audit,out/'base',out/'hosted',bit_fixture)
z=json.loads((audit/'EXACT-ASSEMBLY.json').read_text());r=dict(status='PASS_CHANGED_COMPLEX_SUPPLIER_AND_LITERAL_WHOLE_OWNER_PACKING',complex_lower=z['complex_lower'],complex_template_sha256=z['complex_template_sha256'],stages=stages,scope='Actual changed local supplier and whole-owner controller admitted with fresh phase/frame/chart/finite invoice under retained all-size interfaces. Bit cited by this assembly is a regression; root separately assembles the new changed bit supplier.')
(out/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(r,indent=2),flush=True)
