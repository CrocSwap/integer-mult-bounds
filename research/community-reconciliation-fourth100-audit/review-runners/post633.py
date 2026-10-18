import subprocess,tarfile,io,json,hashlib,os,time,gzip
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');R=Path('/tmp/integer-mult-queue-20261013');n=633
row=next(x for x in json.load(open(P/'snapshot.json'))['pull_requests'] if x['number']==n)
src=P/'extra-633';out=P/'extra-633-out';here=src/'research/pr627-independent-audit-20261013';pkg=out/'input/complex-571-cold14-k492b';PY='/tmp/integer-mult-review-venv/bin/python'
paths=['research/complex-k492-owner-repair/data/SPEC.json','research/complex-k492-owner-repair/extras/exact_intervals.py']
raw=subprocess.check_output(['git','archive',row['headRefOid'],*paths],cwd=R)
with tarfile.open(fileobj=io.BytesIO(raw)) as t:t.extractall(src,filter='data')
assert json.load(open(out/'replay/RESULT.json'))['status']=='PASS_COLD14_NATIVE_COMPLEX_AND_CITED_BIT'
prior=next(x for x in json.load(open(P/'extra-execution.json')) if x['number']==633)
assert hashlib.sha256((P/prior['log']).read_bytes()).hexdigest()==prior['sha256']
routing=src/'research/complex-multicold/vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
word=out/'replay/jp8-step6-cold_end/FULL-WORD.json.gz'
commands=[[PY,'-B',str(here/'check_native_owners.py'),'--package',str(pkg),'--replay',str(out/'replay'),'--repository',str(src),'--out',str(out/'INDEPENDENT-OWNERS.json')]]
for script,dest in [('inputs/contributor_check_new_helpers.py','focused-controls'),('check_extra_tail_controls.py','extra-controls')]:commands.append([PY,'-B',str(here/script),'--package',str(pkg),'--word',str(word),'--routing',str(routing),'--out',str(out/dest)])
log=P/'pr633-post.txt';start=time.time();rc=0
with log.open('w') as f:
 f.write('Fresh full upstream replay completed; resuming unchanged downstream independent checks after adding two omitted exact-head repository inputs.\n'+json.dumps(dict(prior_log=prior['log'],prior_sha256=prior['sha256'],result_sha256=hashlib.sha256((out/'replay/RESULT.json').read_bytes()).hexdigest(),added_inputs={p:hashlib.sha256((src/p).read_bytes()).hexdigest() for p in paths}))+'\n');f.flush()
 for cmd in commands:
  f.write('COMMAND '+json.dumps(cmd)+'\n');f.flush();z=subprocess.run(cmd,cwd=src,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),stdout=f,stderr=subprocess.STDOUT)
  if z.returncode:rc=z.returncode;break
receipt=dict(number=n,head=row['headRefOid'],commands=commands,exit_code=rc,seconds=time.time()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest(),scope='Full fresh upstream replay plus resumed unchanged independent owner, exact moment, helper and tail controls; only omitted exact-head auxiliary inputs added. Prior full replay and output hashes identified in log.')
(P/'post-execution.json').write_text(json.dumps([receipt],indent=2)+'\n')
keep=P/'pr633-outputs'
for f in out.rglob('*'):
 if f.is_file() and (f.suffix=='.log' or f.name in ['RESULT.json','RECEIPT.json','INDEPENDENT-OWNERS.json','VERIFICATION.json']):
  dest=keep/f.relative_to(out);dest=dest.with_name(dest.name+'.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(gzip.compress(f.read_bytes(),mtime=0))
print(receipt)
