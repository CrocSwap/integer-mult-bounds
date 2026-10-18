import subprocess,json,time,hashlib,gzip
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');n=634;src=P/'extra-634/research/lower-bounds-coding-gap';out=P/'extra-634-out';keep=P/'pr634-outputs';keep.mkdir(exist_ok=True)
# Check contributed immutable proofs now; generated proofs are tested separately when the wrapper finishes.
cmds=[];log=P/'pr634-proof.txt';start=time.time();rc=0
with log.open('w') as f:
 f.write((P/'drat-source.json').read_text()+'\n');f.flush()
 for N in [6,8,10,12]:
  cmd=[str(P/'drat-trim'),str(src/f'proofs/patsat-{N}.cnf'),str(src/f'proofs/patsat-{N}.drat')];cmds.append(cmd)
  z=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);f.write('COMMAND '+json.dumps(cmd)+'\n'+z.stdout.decode(errors='replace')+'\n');f.flush()
  if b's VERIFIED' not in z.stdout:rc=1;break
rows=json.load(open(P/'snapshot.json'))['pull_requests'];head=next(r['headRefOid'] for r in rows if r['number']==634)
receipt=dict(number=n,head=head,commands=cmds,exit_code=rc,seconds=time.time()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest(),scope='Independent drat-trim verification of the four contributed SAT proofs. Complements the separate fresh CNF/solver/profile replay, not the optional external 33-vertex graph or written compiler theorem.')
(P/'proof-execution.json').write_text(json.dumps([receipt],indent=2)+'\n');print(receipt)
