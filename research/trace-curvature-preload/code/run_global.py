"""Changed-word nine-stage global emission and physical checks. No optimizer or public local revalidation."""
import sys,json,subprocess,os,shutil,time
from pathlib import Path
P=Path(sys.argv[1]).resolve();LOCAL=Path(sys.argv[2]).resolve();WORD=Path(sys.argv[3]).resolve();OUT=Path(sys.argv[4]).resolve();GEO=Path(sys.argv[5]).resolve()
VK=P/'vendor/e8-r715-eleven-stage-whole/code';SK=P.parent/'e8-bit-carrier-skeleton';PY=sys.executable
OUT.mkdir(parents=True,exist_ok=False);(OUT/'nine').mkdir();(OUT/'records').mkdir()
for f in ['249-records.bin','249-states.json','frames.json']:shutil.copyfile(LOCAL/'records'/f,OUT/'records'/f)
shutil.copyfile(GEO,OUT/'nine/GEOMETRY.json')
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0')
stages=[]
def run(name,args):
 print(name,flush=True);t=time.time();p=subprocess.run([PY,'-B',*map(str,args)],capture_output=True,text=True,env=env)
 (OUT/(name+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8',newline='\n')
 assert p.returncode==0,(name,p.stdout[-1000:],p.stderr[-2000:]);stages.append(dict(name=name,seconds=time.time()-t));print(p.stdout[-1200:],flush=True)
run('01-global',[VK/'global_k.py','--word',WORD,'--local-check',LOCAL,'--out',OUT/'nine','--isometries',SK/'data/eleven/residual-isometries.json'])
run('02-adapt',[P/'code/adapt.py',VK,OUT/'adapted'])
run('03-parent-audit',[OUT/'adapted/audit_parent_k.py','--local-check',LOCAL,'--out',OUT/'nine','--word',WORD])
run('04-host',[VK/'emit_k.py',OUT/'nine',LOCAL,OUT/'hosted','--selection',P/'data/selection9-r480.json','--key','bit','--host-all'])
run('05-host-audit',[VK/'audit_hosted_k.py',OUT,OUT/'hosted',OUT/'hosted/AUDIT.json'])
run('06-invoice',[P/'code/assemble9.py',OUT,OUT/'hosted',OUT/'hosted/AUDIT.json',SK,OUT/'INVOICE.json','pr484'])
a=json.loads((OUT/'hosted/AUDIT.json').read_text());g=json.loads((OUT/'hosted/GLOBAL.json').read_text());local=json.loads((LOCAL/'cout/columns.json').read_text());h={int(r):n for r,n in a['profile'].items()}
expected={1:362880,2:395520,3:17280,4:67200,6:49920,7:23040,8:2592};assert h==expected and a['hosted_residuals']==138240 and a['bank_assignments']==0
r=dict(status='PASS_CHANGED_BIT60_NINE_STAGE_PHYSICAL_CONTROLLER',stages=stages,profile=a['profile'],live=a['live'],deficit=a['deficit'],template_sha256=a['template_sha256'],emitted_program_sha256=a['emitted_program_sha256'],emitted_events=a['emitted_events'],parent_controls=len(json.loads((OUT/'nine/AUDIT.json').read_text())['mutations_rejected']),hosting_controls=len(a['mutations_rejected']),global_prefix_bits=g['global_prefix_bits'],bit_invoice=json.loads((OUT/'INVOICE.json').read_text())['bit'],bit_lower=json.loads((OUT/'INVOICE.json').read_text())['bit_lower'],scope='Changed nine-stage word, literal whole residual routing and parent/hosted audits. Strict scalar invoice and both moment engines passed; its old cited complex supplier is only a regression. Final outer assembly with the selected new complex supplier remains separate.')
(OUT/'RESOURCE-RESULT.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(r,indent=2))
