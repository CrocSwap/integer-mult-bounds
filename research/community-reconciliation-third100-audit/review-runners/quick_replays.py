import json,subprocess,tarfile,hashlib,time,gzip,os,shutil,signal
from pathlib import Path
P=Path('/tmp/reconciliation-third100-20261013');R=Path('/tmp/integer-mult-queue-20261013');rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']};PY='/tmp/integer-mult-review-venv/bin/python';out=[]
recipes=[(365,'e8-coupled-retiming','verify.py'),(367,'frame-algebra-performance','test_rows.py'),(368,'campaign-100-results','validate_archive.py')]
for n,folder,script in recipes:
 w=P/f'quick-{n}';w.mkdir();prefix='research/'+folder;proc=subprocess.Popen(['git','archive',rows[n]['headRefOid'],prefix],cwd=R,stdout=subprocess.PIPE)
 with tarfile.open(fileobj=proc.stdout,mode='r|') as t:t.extractall(w,filter='data')
 assert proc.wait()==0
 cmd=[PY,'-B',str(w/prefix/script)];log=P/f'pr{n}-fresh.txt';start=time.monotonic();print('START',n,flush=True)
 with log.open('w') as f:
  child=subprocess.Popen(cmd,cwd=w,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  try:ret=child.wait(timeout=900)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGTERM);child.wait();ret=124
 out.append(dict(number=n,head=rows[n]['headRefOid'],command=cmd,exit_code=ret,seconds=time.monotonic()-start,log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()));(P/'fresh-execution.json').write_text(json.dumps(out,indent=2)+'\n');print('END',n,ret,round(time.monotonic()-start),flush=True);shutil.rmtree(w)
