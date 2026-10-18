import json,gzip,subprocess,tarfile,hashlib,time
from pathlib import Path
R=Path('/tmp/integer-mult-queue-20261013');P=Path('/tmp/reconciliation-next100-20261013');r=next(r for r in json.load(gzip.open(P/'SOURCES.json.gz','rt'))['pull_requests'] if r['number']==275);w=P/'primary275';w.mkdir();h=r['head']
z=subprocess.Popen(['git','archive',h,'research/finite-assembly-pr799','research/finite-assembly-frontier'],cwd=R,stdout=subprocess.PIPE)
with tarfile.open(fileobj=z.stdout,mode='r|')as t:t.extractall(w,filter='data')
assert z.wait()==0
spec=json.load(open(w/'research/finite-assembly-pr799/UPSTREAM.json'));u=P/'upstream275';u.mkdir()
for path,f in spec['files'].items():
 raw=subprocess.check_output(['git','show',spec['commit']+':'+path],cwd=R);assert len(raw)==f['bytes']and hashlib.sha256(raw).hexdigest()==f['sha256'];dest=u/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
rs=[]
for i,cmd in enumerate([['python3.12','-B','research/finite-assembly-frontier/verify.py'],['python3.12','-E','-S','-B','research/finite-assembly-pr799/verify.py','--upstream',str(u),'--output',str(P/'pr275-application-result')]]):
 log=P/f'pr275-primary-{i}.txt';start=time.monotonic()
 with log.open('w')as f:ret=subprocess.run(cmd,cwd=w,stdout=f,stderr=subprocess.STDOUT,timeout=600).returncode
 rs.append(dict(number=275,head=h,upstream=spec['commit'],command=cmd,exit_code=ret,seconds=time.monotonic()-start,log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),scope='Two finite-assembly packages only; other PR275 packages not accepted by this receipt'))
 (P/'primary-execution.json').write_text(json.dumps(rs,indent=2)+'\n');print(i,ret,flush=True)
