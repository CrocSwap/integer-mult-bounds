import subprocess,os,json,gzip,hashlib,time,platform,tarfile,io,shutil,sys,concurrent.futures,threading
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');R=Path('/tmp/integer-mult-queue-20261013');PY='/tmp/integer-mult-review-venv/bin/python';rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']}
items={627:'complex-571-cold14-k492b',629:'complex-571-cold14-h4a',635:'complex-571-cold14-st2',637:'complex-571-cold14-st2u4',641:'complex-571-cold14-st2s4',643:'complex-571-cold14-twin',646:'signed-root-k480',636:'combined-cold-ends-20261013/witness635',638:'pr637-improvement-20261013/witness637',639:'pr638-improvement-20261013/witness638',640:'ck-u4-improvement-20261013/witness',642:'selective249-improvement-20261013/witness',644:'pr643-improvement-20261013/witness'}
record=P/'cold-parallel-execution.json';receipts=json.load(open(record))if record.exists()else[];lock=threading.Lock()
def work(n):
 root=items[n];src=P/f'cold-parallel-{n}';src.mkdir();raw=subprocess.check_output(['git','archive',rows[n]['headRefOid'],'research/'+root.split('/')[0]],cwd=R)
 with tarfile.open(fileobj=io.BytesIO(raw))as t:t.extractall(src,filter='data')
 pkg=src/'research'/root;out=P/f'cold-parallel-{n}-out';cmd=[PY,'-B',str(pkg/'verify.py'),'--work',str(out),'--jobs','2']
 spec=json.load(open(pkg/'data/SPEC.json'))
 deps=[]
 for name,d in spec['build']['sources'].items():
  source=P/'cold-deps'/name/'research'/d['dir'];assert source.exists(),source;cmd+=['--source',name+'='+str(source)];deps.append(dict(name=name,path=str(source),expected_manifest=d['manifest_sha256'],actual_manifest=hashlib.sha256((source/'MANIFEST.json').read_bytes()).hexdigest()))
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PATH=str(Path(PY).parent)+':'+os.environ['PATH']);start=time.time();log=P/f'pr{n}-cold-parallel.txt';print('START',n,flush=True)
 with log.open('w')as f:z=subprocess.run(cmd,cwd=src,env=env,stdout=f,stderr=subprocess.STDOUT)
 receipt=dict(number=n,head=rows[n]['headRefOid'],command=cmd,dependencies=deps,cwd=str(src),exit_code=z.returncode,seconds=time.time()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest(),environment=platform.platform(),scope='Fresh full spec-driven replay with exact pinned source dependencies; cited bit primitive remains as stated.')
 keep=P/f'pr{n}-outputs';keep.mkdir(exist_ok=True)
 for f in out.rglob('*'):
  if f.is_file() and (f.suffix=='.log' or f.name in ['RESULT.json','RECEIPT.json','VERIFICATION.json','FAILURE.json']):
   dest=keep/f.relative_to(out);dest=dest.with_name(dest.name+'.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 with lock:receipts.append(receipt);record.write_text(json.dumps(receipts,indent=2)+'\n');print('DONE',n,z.returncode,round(receipt['seconds']),flush=True)
 if z.returncode==0:shutil.rmtree(out)
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as ex:
 for f in ex.map(work,map(int,sys.argv[1:])):pass
