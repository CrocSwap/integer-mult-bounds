import json,subprocess,time,hashlib
from pathlib import Path
P=Path('/tmp/reconciliation92-20261013');ROOT=Path('/tmp/integer-mult-queue-20261013')
rows={r['number']:r for r in json.loads((P/'snapshot.json').read_text())['pull_requests']}
recipes={22:[['scripts/refine_translated_partial.py']],27:[['scripts/endpoint_semantic_composition.py']],34:[['research/reversed-two-stage/reproduce.py']],35:[['research/fixed-basis-two-stage/verify.py']],41:[['research/rad-left-producer/code/exact_composition.py','--axes',f'research/rad-left-producer/fixtures/axes-{x}23-{x}25.json','--phase','research/rad-left-producer/fixtures/phase-pr36.json','--assembly','research/rad-left-producer/code/adopted_pr37_balanced_assembly.py','--output',str(P/f'pr41-{x}-output.json')] for x in ['alternating','association']]}
results=[]
for n,commands in recipes.items():
 work=P/f'final{n}';head=rows[n]['headRefOid'];subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0','worktree','add','--detach',str(work),head],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 for i,args in enumerate(commands):
  cmd=['python3.12','-B']+args;log=P/f'pr{n}-final-{i}.txt';start=time.monotonic();print('START',n,i,flush=True)
  with log.open('w') as out:code=subprocess.run(cmd,cwd=work,stdout=out,stderr=subprocess.STDOUT).returncode
  results.append(dict(number=n,head=head,command=cmd,exit_code=code,seconds=time.monotonic()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
  (P/'final-execution.json').write_text(json.dumps(results,indent=2)+'\n');print('END',n,i,code,flush=True)
 drift=subprocess.check_output(['git','diff','--binary'],cwd=work)
 if drift:(P/f'pr{n}-final-drift.patch').write_bytes(drift)
 subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0','worktree','remove','--force',str(work)],cwd=ROOT,check=True)
