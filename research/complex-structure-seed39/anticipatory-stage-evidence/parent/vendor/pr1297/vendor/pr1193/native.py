import os,sys,time,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];work=Path(sys.argv[2]);work.mkdir(parents=True,exist_ok=False);raw=Path(sys.argv[1]).resolve()
src=ROOT/'research/complex-k492-owner-repair/vendor/multicold';up=ROOT/'research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code';base=src/'vendor/pr558';par=base/'vendor/pr552';local=work/'local'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',MULTICOLD_SOURCE=str(src),GAIN_PR564_SOURCE=str(src),CPLUS_INCLUDE_PATH=os.environ.get('CPLUS_INCLUDE_PATH','/opt/homebrew/include'));env.pop('PYTHONOPTIMIZE',None)
steps=[]
for label,script,args in [('native',up/'hpe_audit_and_transport.py',['--raw',raw,'--routing',par/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz','--out',local]),('ledgers',up/'hpe_emit_local.py',[local]),('local-replay',up/'hpe_audit_local.py',[local]),('wrappers',up/'hpe_adapters_local.py',[local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json']),('phases',base/'code/phases_full.py',[local,par/'complex-global/vendor531/vendor/clifford'])]:
 t=time.monotonic()
 with (work/(label+'.log')).open('w') as f:p=subprocess.run([sys.executable,'-B',str(src/'code/run_portable.py'),str(script),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT,env=env)
 steps.append(dict(step=label,exit_code=p.returncode,seconds=time.monotonic()-t));(work/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n');assert p.returncode==0,(label,(work/(label+'.log')).read_text()[-4000:]);print('PASS',label,flush=True)
