import json,subprocess,time,hashlib,tarfile,io
from pathlib import Path
P=Path('/tmp/reconciliation92-20261013');ROOT=Path('/tmp/integer-mult-queue-20261013');D={r['number']:r for r in json.loads((P/'snapshot.json').read_text())['pull_requests']}
recipes={5:[['python3.12','-B','-m','unittest','discover','-s','tests','-p','test_fast_gaussian.py','-v']],77:[['make','-C','research/balanced-split-reclamation','verify']],81:[['python3.12','-B','research/round9-balanced-columns/dense_audit.py'],['python3.12','-B','research/round9-balanced-columns/validate_selected.py','--bundle','research/round9-balanced-columns/selected-both','--output','build/balanced-columns-validation.json']],102:[['python3.12','-B','research/round7-moment-followup/verify.py']],110:[['python3.12','-B','research/deferred-stopped/complex_deferred.py'],['python3.12','-B','research/deferred-stopped/bit_round7.py'],['python3.12','-B','research/deferred-stopped/certificate.py']],128:[['python3.12','-B','research/completed-core-sharing/verify.py']],138:[['python3.12','-B','research/tightened-slack/certificate-tight.py','--write']],146:[['python3.12','-B','scripts/paired_cube_producer.py','--output','build/replay.json','--work-dir','build/replay']]}
results=[]
for n,commands in recipes.items():
 work=P/f'special{n}';head=D[n]['headRefOid'];subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0','worktree','add','--detach',str(work),head],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 if n==81:
  target=work/'research/round6-pr71/baseline';target.mkdir(parents=True)
  data=subprocess.check_output(['git','archive','1bef94fd40a746452548c84a4a8f8834670a3113'],cwd=ROOT)
  with tarfile.open(fileobj=io.BytesIO(data)) as t:t.extractall(target,filter='data')
  (work/'build').mkdir(exist_ok=True)
 for i,cmd in enumerate(commands):
  start=time.monotonic();log=P/f'pr{n}-special-{i}.txt';print('START',n,i,flush=True)
  with log.open('w') as out:r=subprocess.run(cmd,cwd=work,stdout=out,stderr=subprocess.STDOUT)
  results.append(dict(number=n,head=head,command=cmd,exit_code=r.returncode,seconds=time.monotonic()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest()));(P/'special-execution.json').write_text(json.dumps(results,indent=2)+'\n');print('END',n,i,r.returncode,flush=True)
 drift=subprocess.check_output(['git','diff','--binary'],cwd=work)
 if drift:(P/f'pr{n}-special-drift.patch').write_bytes(drift)
 subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0','worktree','remove','--force',str(work)],cwd=ROOT,check=True)
