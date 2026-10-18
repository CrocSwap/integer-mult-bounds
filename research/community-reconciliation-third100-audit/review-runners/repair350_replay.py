from pathlib import Path
import subprocess,json,gzip,time,hashlib,os,shutil,tarfile,signal
R=Path('/tmp/integer-mult-queue-20261013');P=Path('/tmp/reconciliation-third100-20261013');rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']}
recipes=[(350,'w3-p10b-pointwise-complex-retimed','verify.py',None)]
PY='/tmp/integer-mult-review-venv/bin/python';env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','CPATH':str(R/'research/e8-bit-carrier-skeleton/portable-include')+':/tmp/coordinated-crossover-v2.PSyYno/deps/include','PATH':'/tmp/integer-mult-review-venv/bin:'+os.environ['PATH']};results=[]
for n,folder,script,flag in recipes:
 work=P/f'repaired-{n}';out=P/f'repaired-{n}-out';work.mkdir();head=rows[n]['headRefOid'];prefix='research/'+folder
 proc=subprocess.Popen(['git','archive',head,prefix],cwd=R,stdout=subprocess.PIPE)
 with tarfile.open(fileobj=proc.stdout,mode='r|') as t:t.extractall(work,filter='data')
 assert proc.wait()==0
 subprocess.run([PY,'-B',str(R/'research/community-reconciliation-third100-audit/adapters/repair_source.py'),str(n),str(work/prefix),'--git-root',str(R)],check=True)
 cmd=[PY,'-B',str(work/prefix/script)]
 if flag=='portable':cmd += [str(work/prefix),'--work',str(out)]
 elif flag is not None:cmd += ([flag] if flag else [])+[str(out)]
 log=P/f'pr{n}-repaired.txt';start=time.monotonic();print('START',n,flush=True)
 with log.open('w') as f:
  child=subprocess.Popen(cmd,cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  try:ret=child.wait(timeout=2400)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGTERM);child.wait();ret=124
 retained=[]
 if out.exists():
  for f in out.rglob('*'):
   if not f.is_file():continue
   path=f.relative_to(out).as_posix()
   if f.suffix in ('.json','.log','.txt') and f.stat().st_size<2_000_000 and not any(x in path.split('/') for x in ('upstream','source','sources','bin','vendor')):
    data=f.read_bytes();dest=f'pr{n}-repaired-outputs/'+path+'.gz';(P/dest).parent.mkdir(parents=True,exist_ok=True);(P/dest).write_bytes(gzip.compress(data,mtime=0));retained.append(dict(path=path,file=dest,sha256=hashlib.sha256(data).hexdigest()))
 receipt=dict(number=n,head=head,source_prefix=prefix,command=cmd,environment={'python':PY,'CPATH':env['CPATH']},exit_code=ret,seconds=time.monotonic()-start,log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),outputs=retained)
 results.append(receipt);(P/'retime-repair-execution.json').write_text(json.dumps(results,indent=2)+'\n');print('END',n,ret,round(receipt['seconds']),flush=True)
 shutil.rmtree(work)
 if out.exists():shutil.rmtree(out)
