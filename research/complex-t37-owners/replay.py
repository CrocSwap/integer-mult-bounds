"""Run discovery then a separate strictly pinned emitted T37 replay.

Consumes a prepared PR799 base; ancestry is checked separately by verify.py.
The verification driver supplies a completed source-bound cold base and freshly rebuilt U8.
The discovery stage freezes derived receipts for a separate strict run; it does not search.
"""
import hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
from common import ROOT,P,T21,read
OUT=Path(os.environ.get('T37_WORK',ROOT.parent/'t37-work')).resolve()
SOURCE=ROOT/'research/complex-k492-owner-repair/vendor/multicold'
NATIVE=Path(os.environ.get('T37_LOCAL',OUT/'native/local')).resolve()
BASELINE=Path(os.environ.get('T37_BASELINE',OUT/'baseline799')).resolve()
def main():
    mode=sys.argv[1];assert mode in ('discovery','strict')
    stageout=OUT/(sys.argv[2]if len(sys.argv)>2 else mode)
    assert 'T37_WORK' in os.environ and 'T37_BASELINE' in os.environ, 'Run verify.py'
    assert not stageout.exists() and not OUT.is_relative_to(ROOT)
    stageout.mkdir()
    runtime=OUT/'runtime';code=runtime/'code';specpath=runtime/'data/SPEC.json'
    if mode=='discovery':
        spec=read(specpath);spec['data']={key:hashlib.sha256(path.read_bytes()).hexdigest()for key,path in [('owners_sha256',P/'OWNERS.json.gz'),('plan_sha256',OUT/'lift/PLAN.json')]};specpath.write_text(json.dumps(spec,indent=2)+'\n')
        spec['expected']['gain_baseline_kappa']=read(T21/'data/SPEC.json')['expected']['gain_baseline_kappa'];specpath.write_text(json.dumps(spec,indent=2)+'\n')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',
             MULTICOLD_SOURCE=str(SOURCE),GAIN_PR564_SOURCE=str(SOURCE),WITNESS_SPEC=str(specpath))
    temp=OUT/'temp';temp.mkdir(exist_ok=True)
    env.update(TEMP=str(temp),TMP=str(temp),TMPDIR=str(temp))
    for key in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD'):env.pop(key,None)
    if mode=='discovery':env.update(WITNESS_DISCOVER='1',WITNESS_RECORD=str(stageout/'WITNESS-RECORD.jsonl'))
    stages=[]
    def run(name,script,*args):
        start=time.monotonic();log=stageout/(name+'.log')
        with log.open('w',encoding='utf-8')as f:
            proc=subprocess.run([sys.executable,'-B',str(SOURCE/'code/run_portable.py'),str(script),*map(str,args)],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
        stages.append(dict(name=name,exit_code=proc.returncode,seconds=round(time.monotonic()-start,3),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
        (stageout/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n')
        if proc.returncode:raise RuntimeError(name+'\n'+log.read_text(errors='replace')[-6000:])
        print('PASS',mode,name,stages[-1]['seconds'],flush=True)
    parent=OUT/'parent'
    if not parent.exists():
        shutil.copytree(BASELINE/'global/parent558',parent)
        shutil.copyfile(OUT/'lift/GLOBAL-TEMPLATE.json.gz',parent/'complex-global/base/split-centres/GLOBAL-TEMPLATE.json.gz')
    g=stageout/'global'
    run('bind',code/'bind_providers_portable.py','--baseline',parent,'--provider','gauge44='+str(NATIVE),'--plan',OUT/'lift/PLAN.json','--out',g)
    run('emit',code/'emit_allcold.py','--base',g/'base','--owners',P/'OWNERS.json.gz','--plan',g/'PLAN.json','--out',g/'hosted')
    run('audit',code/'audit_allcold.py',g/'base',g/'hosted',g/'audit/ASYNC-AUDIT.json','--mutation-controls')
    run('invoice',code/'invoice_allcold.py','--base',g/'base','--hosted',g/'hosted','--audit',g/'audit','--out',g/'audit','--retained-invoice',SOURCE/'vendor/pr558/vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json')
    run('assembly',code/'assemble.py',SOURCE,g,stageout/'ASSEMBLY.json')
    if mode=='discovery':
        run('freeze',code/'freeze_spec.py','--spec',specpath,'--discovery',stageout)
    else:
        for name,script,out in [('admission-controls','assembly_controls.py','ADMISSION-CONTROLS.json'),('bit-controls','bit_supplier_controls.py','BIT-CONTROLS.json')]:
            run(name,code/script,'--source-package',SOURCE,'--owner',g/'audit/OWNERS-AND-PROFILE.json','--invoice',g/'audit/PREFIX-AND-INVOICE.json','--out',stageout/out)
    print('COMPLETE',mode,read(stageout/'ASSEMBLY.json')['kappa_decimal'],flush=True)
if __name__=='__main__':main()
