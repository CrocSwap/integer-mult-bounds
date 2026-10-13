import argparse,json,hashlib,os,shutil,subprocess,sys,time,collections
from pathlib import Path
P=Path(__file__).resolve().parent;F=P.parent;R=F/'owner37-round44';S=R/'source/research/r480-owner-optimum';N=F/'joint1148-round45';B=F/'demotions1148-round43/baseline-replay';ROOT=N/'source'
def rd(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--discover',action='store_true');ap.add_argument('--local',type=Path);a=ap.parse_args();data=a.data.resolve();work=a.work.resolve();assert not work.exists();work.mkdir();local=a.local.resolve() if a.local else B/'native/local';code=S/'code';upstream=ROOT/'research/complex-k492-owner-repair/vendor/multicold'
for rel,h in rd(S/'vendor/pr1074/UPSTREAM-PINS.json').items():assert sha(ROOT/rel)==h,rel
assert rd(B/'RESULT.json')['status']=='PASS_THREE_DEMOTIONS_COMPLETE_ADMISSION'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',MULTICOLD_SOURCE=str(upstream),GAIN_PR564_SOURCE=str(upstream))
for k in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD','WITNESS_SPEC'):env.pop(k,None)
runtime=work/'runtime';(runtime/'data').mkdir(parents=True);shutil.copytree(S/'vendor/pr1074/construction',runtime/'construction');shutil.copy2(data/'SPEC.json',runtime/'data/SPEC.json');spec=runtime/'data/SPEC.json';env['WITNESS_SPEC']=str(spec)
if a.discover:env.update(WITNESS_DISCOVER='1',WITNESS_RECORD=str(work/'WITNESS-RECORD.jsonl'))
parent=work/'parent';shutil.copytree(B/'parent/t16/parent558',parent);shutil.copy2(data/'GLOBAL-TEMPLATE.json.gz',parent/'complex-global/base/split-centres/GLOBAL-TEMPLATE.json.gz');stages=[]
def run(name,script,*args):
 t=time.monotonic();log=work/(name+'.log')
 with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(upstream/'code/run_portable.py'),str(script),*map(str,args)],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
 stages.append(dict(name=name,seconds=time.monotonic()-t,exit_code=r.returncode,log_sha256=sha(log)));(work/'STAGES.json').write_text(json.dumps(stages,indent=2));assert r.returncode==0,(name,log.read_text()[-5000:]);print('PASS',name,flush=True)
g=work/'global'
shutil.copy2(P/'assemble_candidate.py',code/'assemble.py');shutil.copy2(P/'audit_allcold_idle_overlay.py',code/'audit_allcold_idle_overlay.py')
run('bind',code/'bind_providers_portable.py','--baseline',parent,'--provider','gauge44='+str(local),'--provider','extra='+str(P/'native-extra/local'),'--plan',data/'PLAN.json','--out',g)
run('emit',code/'emit_allcold.py','--base',g/'base','--owners',data/'OWNERS.json.gz','--plan',g/'PLAN.json','--out',g/'hosted')
shutil.move(g/'hosted',g/'hosted-baseline')
run('idle-overlay',P/'idle_overlay.py','--hosted',g/'hosted-baseline','--base',g/'base','--owners',data/'OWNERS.json.gz','--moves',P/'SWAP-MOVES.json.gz','--out',g/'hosted')
env.update(AUDIT_SHARDS='4',AUDIT_FAST_PATH=str(P/'audit_fast.py'),T16_SOURCE_CODE=str(code),T16_BASE_HOSTED=str(g/'hosted-baseline'))
run('overlay-verify',P/'verify_idle_overlay.py','--hosted-baseline',g/'hosted-baseline','--hosted',g/'hosted','--base',g/'base','--owners',data/'OWNERS.json.gz','--out',work/'IDLE-OVERLAY-VERIFY.json')
run('swap-controls',P/'swap_controls.py','--hosted-baseline',g/'hosted-baseline','--hosted',g/'hosted','--base',g/'base','--out',work/'SWAP-CONTROLS.json')
run('overlay-operator',P/'check_emitted_operator.py','--hosted-baseline',g/'hosted-baseline','--hosted',g/'hosted','--base',g/'base','--out',work/'IDLE-OPERATOR-CHECK.json')
run('audit',P/'audit_fast.py',code/'audit_allcold_idle_overlay.py',g/'base',g/'hosted',g/'audit/ASYNC-AUDIT.json','--mutation-controls')
run('invoice',code/'invoice_allcold.py','--base',g/'base','--hosted',g/'hosted','--audit',g/'audit','--out',g/'audit','--retained-invoice',upstream/'vendor/pr558/vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json')
run('assembly',code/'assemble.py',upstream,g,work/'ASSEMBLY.json')
if a.discover:
 run('freeze',P/'freeze_spec.py','--spec',spec,'--discovery',work);shutil.copy2(spec,data/'SPEC.json')
else:
 for name,script,filename in [('admission','assembly_controls.py','ADMISSION-CONTROLS.json'),('bit','bit_supplier_controls.py','BIT-CONTROLS.json')]:run(name,code/script,'--source-package',upstream,'--owner',g/'audit/OWNERS-AND-PROFILE.json','--invoice',g/'audit/PREFIX-AND-INVOICE.json','--out',work/filename)
plan=rd(data/'PLAN.json')
run('independent',P/'audit_mixed.py','--parent',B/'parent/t16/global8/base/split-centres/GLOBAL-TEMPLATE.json.gz','--data',data,'--provider','gauge44='+str(local),'--provider','extra='+str(P/'native-extra/local'),'--out',work/'INDEPENDENT.json')
asm=rd(work/'ASSEMBLY.json');ind=rd(work/'INDEPENDENT.json');inv=rd(g/'audit/PREFIX-AND-INVOICE.json');ov=rd(g/'hosted/IDLE-PAIR-OVERLAY.json');exp=dict(rd(g/'hosted-baseline/HOSTED.json')['global_profile']);assert ind['profile']==plan['profile']==exp and {str(k):v for k,v in asm['complex_profile'].items()}==ov['profile'];assert ind['prefix_bits']==inv['global_prefix_bits']<1024;assert ind['physical_row_coefficient']==inv['finite']['physical_row_coefficient']<20161;assert len(ind['controls_rejected'])==8
if not a.discover:assert len(rd(work/'ADMISSION-CONTROLS.json')['rejected_controls'])==114 and len(rd(work/'BIT-CONTROLS.json')['rejected_controls'])==12
receipt=dict(status='DISCOVERY' if a.discover else 'PASS_STRICT_MIXED_T37_ENTRANCES',kappa=asm['kappa'],kappa_decimal=asm['kappa_decimal'],steps=stages,independent=ind,scope='Conditional finite construction only; two freshly replayed source-holder fusion providers; all inherited theorem obligations retained.');(work/'RESULT.json').write_text(json.dumps(receipt,indent=2));print(receipt['status'],receipt['kappa_decimal'],flush=True)
