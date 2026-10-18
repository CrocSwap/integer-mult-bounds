import json,gzip,subprocess,hashlib,time
from pathlib import Path
P=Path('/tmp/reconciliation92-20261013');ROOT=Path('/tmp/integer-mult-queue-20261013');A=ROOT/'research/community-reconciliation92-audit'
rows=json.loads(gzip.decompress((A/'SOURCES.json.gz').read_bytes()))['pull_requests'];r=next(x for x in rows if x['number']==110);w=P/'repair110'
subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0','worktree','add','--detach',str(w),r['head']],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
pins={'witness_23.json.gz':'b2486aa2bb222bacea6e52162a3920780e45dd8edc5d7cb03eabea336a1c6588','deferred_23.json.gz':'8c38e947ff9e021e308000dd82bb5e2194eb265d8b75194e22ce783d3e75317c'};inputs=w/'review-inputs';inputs.mkdir();provenance=[]
for name,digest in pins.items():
 owner,f=next((r,f) for r in rows for f in r['files'] if f['sha256']==digest)
 raw=subprocess.check_output(['git','cat-file','blob',f['blob']],cwd=ROOT);assert hashlib.sha256(raw).hexdigest()==digest;(inputs/name).write_bytes(raw);provenance.append(dict(name=name,sha256=digest,pr=owner['number'],head=owner['head'],path=f['path'],blob=f['blob']))
cmd=['python3.12','-B','research/deferred-stopped/bit_round7.py','review-inputs'];log=P/'pr110-repaired-inputs.txt';start=time.monotonic()
with log.open('w') as out:code=subprocess.run(cmd,cwd=w,stdout=out,stderr=subprocess.STDOUT).returncode
result=[dict(number=110,head=r['head'],command=cmd,exit_code=code,seconds=time.monotonic()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest(),external_inputs=provenance)]
(P/'repaired-execution.json').write_text(json.dumps(result,indent=2)+'\n');print(code)
subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0','worktree','remove','--force',str(w)],cwd=ROOT,check=True)
