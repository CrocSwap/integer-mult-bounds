"""Recollect PR203 evidence from actual Git objects, separately from the verifier."""
from pathlib import Path
import hashlib,json,platform,subprocess,sys,time
P=Path('/tmp/pr-efficient1800');pkg=P/'sources/2834/research/pr203-retention-receipt'
start=time.monotonic();output=P/'collected-2834.json'
cmd=[sys.executable,'-B',str(pkg/'collect.py'),'--output',str(output)]
r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=40)
if r.returncode:raise RuntimeError(r.stdout)
a=json.loads(output.read_text());b=json.loads((pkg/'SOURCE-PROOF.json').read_text())
if a!=b:raise ValueError('Raw Git recollection differs from retained source proof')
detail=dict(paths=len(a['files']),git_objects=len(a['objects']),complete_semantic_equality=True,scope='Recollects raw Git identities; does not rerun archived C++ or solver censuses.')
log=P/'check-2834-supplement.log';log.write_text(r.stdout+json.dumps(detail)+'\n')
d=dict(number=2834,head=json.loads((P/'2834.json').read_text())['headRefOid'],status='passed',seconds=time.monotonic()-start,commands=[dict(argv=cmd,exit_code=0)],input_sha256={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),pkg/'collect.py',pkg/'verify.py',pkg/'SOURCE-PROOF.json']},log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),environment=dict(python=sys.version,platform=platform.platform()),details=detail)
(P/'check-2834-supplement.json').write_text(json.dumps(d,indent=2)+'\n');print('2834 PASS exact original Git recollection',flush=True)
