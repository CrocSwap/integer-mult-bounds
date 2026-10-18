"""Native chain for a BORROW-WORD (anticipatory dirty borrowing, PR2226): transport -> emit -> independent replay -> wrappers -> phases (+ independent warp-recipe recheck).
Same step layout and STEPS.json as the lineage replay_native.py; usage: run_native_borrow.py BORROW-WORD.json[.gz] WORK_DIR  (WORK_DIR must not exist)."""
import json,os,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent/'code/borrow'
word=Path(sys.argv[1]).resolve();work=Path(sys.argv[2]).resolve();work.mkdir(parents=True,exist_ok=False);local=work/'local'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
flags=(0x00000040|0x08000000) if os.name=='nt' and os.environ.get('BW_IDLE','1')=='1' else 0   # windowless, IDLE priority
steps=[]
for label,script,args in [('native',HERE/'bw_transport.py',[word,local]),('ledgers',HERE/'bw_emit.py',[local]),
        ('local-replay',HERE/'bw_audit_local.py',[local]),
        ('wrappers',HERE/'bw_adapters.py',[local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json']),
        ('phases',[HERE/'bw_phases.py',HERE/'bw_check_recipes.py'],[local])]:   # phases = exact lowering, then the independent warp-recipe recheck
    t=time.monotonic();log=b''
    for script in (script if isinstance(script,list) else [script]):
        p=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=HERE,env=env,creationflags=flags)
        log+=p.stdout
        if p.returncode:break
    (work/(label+'.log')).write_bytes(log)
    steps.append(dict(step=label,exit_code=p.returncode,seconds=time.monotonic()-t));(work/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
    assert p.returncode==0,(label,log.decode(errors='replace')[-4000:])
    print('PASS',label,round(steps[-1]['seconds'],1),flush=True)
