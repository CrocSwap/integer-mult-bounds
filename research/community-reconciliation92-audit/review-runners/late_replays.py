from pathlib import Path
import subprocess,json,time,hashlib
ROOT=Path('/tmp/integer-mult-queue-20261013'); TMP=Path('/tmp/reconciliation92-20261013')
rows={r['number']:r for r in json.loads((TMP/'snapshot.json').read_text())['pull_requests']}
recipes={162:('extended-links',[]),178:('paired-cube-frame-refinement',[]),182:('paired-cube-local-bit-168',[]),185:('bit-leaf-bootstrap182',[]),187:('source-assisted-bit-bootstrap',['--full']),188:('paired-cube-terminal-reuse',[]),189:('paired-cube-twin-local-168',[])}
results=[]
for n,(folder,args) in recipes.items():
 work=TMP/f'pr{n}';head=rows[n]['headRefOid'];started=time.monotonic()
 subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0','worktree','add','--detach',str(work),head],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 command=['python3.12','-B',f'research/{folder}/verify.py',*args]
 log=TMP/f'pr{n}-full.txt'
 print('START',n,flush=True)
 with log.open('w') as out:r=subprocess.run(command,cwd=work,stdout=out,stderr=subprocess.STDOUT)
 drift=subprocess.check_output(['git','diff','--stat'],cwd=work,text=True)
 delta=subprocess.check_output(['git','diff','--binary'],cwd=work)
 if delta:(TMP/f'pr{n}-drift.patch').write_bytes(delta)
 receipt=dict(number=n,head=head,command=command,exit_code=r.returncode,seconds=time.monotonic()-started,tracked_drift=drift,log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
 results.append(receipt);(TMP/'late-execution.json').write_text(json.dumps(results,indent=2)+'\n')
 print('END',n,r.returncode,'drift',bool(drift),'seconds',round(receipt['seconds']),flush=True)
 subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0','worktree','remove','--force',str(work)],cwd=ROOT,check=True)
