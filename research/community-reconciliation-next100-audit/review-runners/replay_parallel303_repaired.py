from pathlib import Path
import subprocess,json,gzip,time,hashlib,os,shutil,tarfile,signal,difflib
R=Path('/tmp/integer-mult-queue-20261013');P=Path('/tmp/reconciliation-next100-20261013');rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']}
recipes={303:'five-stage-gen5b-full-fixed-prime'}
PY='/tmp/integer-mult-review-venv/bin/python';env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','CPATH':str(R/'research/e8-bit-carrier-skeleton/portable-include')+':/tmp/coordinated-crossover-v2.PSyYno/deps/include'};results=json.load(open(P/'parallel-execution.json'))
for n,folder in recipes.items():
 work=P/f'parallel-{n}';out=P/f'parallel-{n}-out';work.mkdir();head=rows[n]['headRefOid'];prefix='research/'+folder
 proc=subprocess.Popen(['git','archive',head,prefix],cwd=R,stdout=subprocess.PIPE)
 with tarfile.open(fileobj=proc.stdout,mode='r|') as t:t.extractall(work,filter='data')
 assert proc.wait()==0
 manifest=work/prefix/'MANIFEST.json';original=manifest.read_bytes();data=json.loads(original);key='validation/supplier-verify.log'
 assert not (work/prefix/key).exists() and data['files'][key]=='647f16533f9f6b22132da2a6c19f5f5f2c364dcdd1ebf40db7a9b6a6f7ae6ede'
 # This missing historical stdout log is referenced only by the integrity manifest, never by any scientific code.
 assert all(key not in f.read_text() for f in (work/prefix).rglob('*.py'))
 del data['files'][key];new=(json.dumps(data,indent=2)+'\n').encode();manifest.write_bytes(new)
 adapter=R/'research/community-reconciliation-next100-audit/adapters/pr303';adapter.mkdir(parents=True,exist_ok=True)
 (adapter/'manifest.patch').write_text(''.join(difflib.unified_diff(original.decode().splitlines(keepends=True),new.decode().splitlines(keepends=True),fromfile='original/MANIFEST.json',tofile='repaired/MANIFEST.json')))
 (adapter/'REPAIR.json').write_text(json.dumps(dict(head=head,original_manifest_sha256=hashlib.sha256(original).hexdigest(),repaired_manifest_sha256=hashlib.sha256(new).hexdigest(),removed_missing_log=key,missing_log_original_sha256='647f16533f9f6b22132da2a6c19f5f5f2c364dcdd1ebf40db7a9b6a6f7ae6ede',scope='Remove only an absent historical stdout-log entry; every scientific source/input/output comparison and complete parent replay remains unchanged'),indent=2)+'\n')
 cmd=[PY,'-B',str(work/prefix/'verify.py'),'--output',str(out)];log=P/f'pr{n}-manifest-repaired.txt';start=time.monotonic();print('START',n,flush=True)
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
    data=f.read_bytes();dest=f'pr{n}-parallel-outputs/'+path+'.gz';(P/dest).parent.mkdir(parents=True,exist_ok=True);(P/dest).write_bytes(gzip.compress(data,mtime=0));retained.append(dict(path=path,file=dest,sha256=hashlib.sha256(data).hexdigest()))
  # failures need their stage stderr, successful runs retain bounded logs too
  for f in out.rglob('*.log'):
   if f.stat().st_size<2_000_000:
    data=f.read_bytes();dest=f'pr{n}-parallel-outputs/'+f.relative_to(out).as_posix()+'.gz';(P/dest).parent.mkdir(parents=True,exist_ok=True);(P/dest).write_bytes(gzip.compress(data,mtime=0));retained.append(dict(path=f.relative_to(out).as_posix(),file=dest,sha256=hashlib.sha256(data).hexdigest()))
 receipt=dict(number=n,head=head,source_prefix=prefix,command=cmd,environment={'python':PY,'CPATH':env['CPATH']},exit_code=ret,seconds=time.monotonic()-start,log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),outputs=retained)
 results.append(receipt);(P/'parallel-execution.json').write_text(json.dumps(results,indent=2)+'\n');print('END',n,ret,round(receipt['seconds']),flush=True)
 shutil.rmtree(work)
 if out.exists():shutil.rmtree(out)
