from pathlib import Path
import subprocess,json,gzip,time,hashlib,os,shutil,tarfile,signal
R=Path('/tmp/integer-mult-queue-20261013');P=Path('/tmp/reconciliation-next100-20261013');rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']}
recipes={281:'gen4-retiming-entrances-target',242:'source527-five-stage-crossover',271:'cleanup-sandwich-272'}
PY='/tmp/integer-mult-review-venv/bin/python';env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','CPATH':str(R/'research/e8-bit-carrier-skeleton/portable-include')+':/tmp/coordinated-crossover-v2.PSyYno/deps/include'};results=[]
# Separate output trees; enough disk remains for this native queue beside the smaller Python queue.
for n,folder in recipes.items():
 env['TMPDIR']=str(P)
 work=P/f'native-{n}';out=P/f'native-{n}-out';work.mkdir();head=rows[n]['headRefOid'];prefix='research/'+folder
 proc=subprocess.Popen(['git','archive',head,prefix],cwd=R,stdout=subprocess.PIPE)
 with tarfile.open(fileobj=proc.stdout,mode='r|') as t:t.extractall(work,filter='data')
 assert proc.wait()==0
 cmd=[PY,'-B',str(work/prefix/'verify.py'),'--output',str(out)]
 if n==242:
  out.mkdir();env['TMPDIR']=str(out);env['PATH']=str(Path(PY).parent)+':'+os.environ['PATH'];env['CXX']='clang++';cmd=['bash',str(work/prefix/'verify.sh')]
 if n==271:
  parent='4d23d0ee5682c99b792614bae4bc5330da19ff13';part='research/filtered-kernel-target120'
  proc=subprocess.Popen(['git','archive',parent,part],cwd=R,stdout=subprocess.PIPE)
  with tarfile.open(fileobj=proc.stdout,mode='r|') as t:t.extractall(work,filter='data')
  assert proc.wait()==0
  cmd += ['--base',str(work/part),'--boost-include','/tmp/coordinated-crossover-v2.PSyYno/deps/include','--cxx','clang++']
 log=P/f'pr{n}-late-native.txt';start=time.monotonic();print('START',n,flush=True)
 with log.open('w') as f:
  child=subprocess.Popen(cmd,cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  try:ret=child.wait(timeout=1800)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGTERM);child.wait();ret=124
 files=[];retained=[]
 if out.exists():
  for f in out.rglob('*'):
   if not f.is_file():continue
   path=f.relative_to(out).as_posix()
   if f.suffix in ('.json','.log','.txt') and f.stat().st_size<2_000_000 and not any(x in path.split('/') for x in ('upstream','build','source','bin','logs')):
    data=f.read_bytes();dest=f'pr{n}-late-outputs/'+path+'.gz';(P/dest).parent.mkdir(parents=True,exist_ok=True);(P/dest).write_bytes(gzip.compress(data,mtime=0));retained.append(dict(path=path,file=dest,sha256=hashlib.sha256(data).hexdigest()))
  # failures need their stage stderr, successful runs retain bounded logs too
  for f in out.rglob('*.log'):
   if f.stat().st_size<2_000_000:
    data=f.read_bytes();dest=f'pr{n}-late-outputs/'+f.relative_to(out).as_posix()+'.gz';(P/dest).parent.mkdir(parents=True,exist_ok=True);(P/dest).write_bytes(gzip.compress(data,mtime=0));retained.append(dict(path=f.relative_to(out).as_posix(),file=dest,sha256=hashlib.sha256(data).hexdigest()))
 receipt=dict(number=n,head=head,source_prefix=prefix,command=cmd,environment={'python':PY,'CPATH':env['CPATH']},exit_code=ret,seconds=time.monotonic()-start,log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),outputs=retained)
 results.append(receipt);(P/'late-native-execution.json').write_text(json.dumps(results,indent=2)+'\n');print('END',n,ret,round(receipt['seconds']),flush=True)
 shutil.rmtree(work)
 if out.exists():shutil.rmtree(out)
