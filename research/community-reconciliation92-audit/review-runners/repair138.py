import json,subprocess,hashlib,time,shutil,os
from pathlib import Path
P=Path('/tmp/reconciliation92-20261013');R=Path('/tmp/integer-mult-queue-20261013');row=next(x for x in json.loads((P/'snapshot.json').read_text())['pull_requests'] if x['number']==138);w=P/'repair138'
git=['git','-c','maintenance.auto=false','-c','gc.auto=0'];subprocess.run(git+['worktree','add','--detach',str(w),row['headRefOid']],cwd=R,check=True,stdout=subprocess.DEVNULL)
pack=w/'research/tightened-slack';pins=json.loads((pack/'SOURCE.json').read_text())['files'];provenance=[]
for name,digest in pins.items():assert hashlib.sha256((w/name).read_bytes()).hexdigest()==digest
# Correct only the documented invocation's search/data paths, without editing frozen source.
for name in pins:
 if Path(name).name not in ('SOURCE.json','certificate.py','verify.py'):
  (pack/Path(name).name).write_bytes((w/name).read_bytes())
env=os.environ.copy();env['PYTHONPATH']=str(w/'research/cover-local-reuse');cmd=['python3.12','-B','research/tightened-slack/certificate-tight.py','--write'];log=P/'pr138-repaired-layout-complete.txt';start=time.monotonic()
with log.open('w') as out:code=subprocess.run(cmd,cwd=w,env=env,stdout=out,stderr=subprocess.STDOUT).returncode
if code==0:shutil.copyfile(pack/'certificate.json',P/'pr138-reproduced-certificate.json')
r=dict(number=138,head=row['headRefOid'],command=cmd,exit_code=code,seconds=time.monotonic()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest(),adaptation='PYTHONPATH=research/cover-local-reuse; copied byte-identical pinned geometry/checker/bit supplier inputs into tightened-slack; all SOURCE.json pins checked; no scientific source edits.',input_pins=pins)
receipt=P/'repair138-execution.json';previous=json.loads(receipt.read_text()) if receipt.exists() else [];previous.append(r);receipt.write_text(json.dumps(previous,indent=2)+'\n');print(code)
subprocess.run(git+['worktree','remove','--force',str(w)],cwd=R,check=True)
