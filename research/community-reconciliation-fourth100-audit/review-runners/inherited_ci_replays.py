import subprocess,os,json,gzip,hashlib,time,platform,tarfile,io,shutil,sys
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');R=Path('/tmp/integer-mult-queue-20261013');PY='/tmp/integer-mult-review-venv/bin/python';rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']}
items={435:('split-centres-kernel',[]),438:('split-centres-kernel-r747',[]),457:('r740-hosted-rank151',[]),459:('r740-hosted-rank151-mixed',[])}
record=P/'inherited-ci-execution.json';receipts=json.load(open(record))if record.exists()else[]
for n in map(int,sys.argv[1:]):
 root,flags=items[n];src=P/f'local-{n}';src.mkdir();paths=subprocess.check_output(['git','ls-tree','--name-only',rows[n]['headRefOid']+':research'],cwd=R).decode().splitlines();wanted=[x for x in paths if x.startswith(('split-centres','e8-early-reset','e8-r740','idle-axis','r740-'))];raw=subprocess.check_output(['git','archive',rows[n]['headRefOid'],*['research/'+x for x in wanted]],cwd=R)
 with tarfile.open(fileobj=io.BytesIO(raw))as t:t.extractall(src,filter='data')
 out=P/f'local-{n}-out';cmd=[PY,'-B',str(src/'research'/root/'verify.py'),*flags,str(out)];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PATH=str(Path(PY).parent)+':'+os.environ['PATH'],CPATH=str(R/'research/e8-bit-carrier-skeleton/portable-include')+':/tmp/coordinated-crossover-v2.PSyYno/deps/include');start=time.time();log=P/f'pr{n}-local.txt';print('START',n,flush=True)
 with log.open('w')as f:z=subprocess.run(cmd,cwd=src,env=env,stdout=f,stderr=subprocess.STDOUT)
 receipt=dict(number=n,head=rows[n]['headRefOid'],command=cmd,cwd=str(src),exit_code=z.returncode,seconds=time.time()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest(),environment=platform.platform(),scope='Fresh unmodified contributed package wrapper; inherited cited suppliers and assumptions retain its explicit scope.')
 keep=P/f'pr{n}-outputs';keep.mkdir(exist_ok=True)
 for f in out.rglob('*'):
  if f.is_file() and (f.suffix=='.log' or f.name in ['RESULT.json','RECEIPT.json','VERIFICATION.json','FAILURE.json']):
   dest=keep/f.relative_to(out);dest=dest.with_name(dest.name+'.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 receipts.append(receipt);record.write_text(json.dumps(receipts,indent=2)+'\n');print('DONE',n,z.returncode,round(receipt['seconds']),flush=True)
 if z.returncode==0:
  # Only fresh task-owned reconstruction trees; evidence/logs retained separately.
  shutil.rmtree(out);shutil.rmtree(src)
