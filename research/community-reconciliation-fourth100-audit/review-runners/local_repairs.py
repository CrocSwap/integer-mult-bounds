import subprocess,os,json,gzip,hashlib,time,platform,tarfile,io,shutil,sys
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');R=Path('/tmp/integer-mult-queue-20261013');PY='/tmp/integer-mult-review-venv/bin/python';rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']}
items={437:('early-reset-source-banks',['--output']),455:('e8-whole-pool-portfolio',[]),471:('e8-tensor-normalization',[]),476:('tensor-schur-r715',[]),478:('tensor-r715-next',[]),483:('tensor-response-r715',[]),492:('tensor-syndrome-portfolio',[]),498:('tensor-nonroot-pairs',[])}
record=P/'local-repair-execution.json';receipts=json.load(open(record))if record.exists()else[]
for n in map(int,sys.argv[1:]):
 root,flags=items[n];src=P/f'repaired-{n}';src.mkdir();raw=subprocess.check_output(['git','archive',rows[n]['headRefOid'],'research/'+root],cwd=R)
 with tarfile.open(fileobj=io.BytesIO(raw))as t:t.extractall(src,filter='data')
 pkg=src/'research'/root;manifest=pkg/'MANIFEST.json';original=manifest.read_bytes();m=json.loads(original)
 assert '.gitattributes' in m and not(pkg/'.gitattributes').exists()
 for name,digest in m.items():
  if name!='.gitattributes':assert hashlib.sha256((pkg/name).read_bytes()).hexdigest()==digest,name
 missing=m.pop('.gitattributes');manifest.write_text(json.dumps(m,indent=2)+'\n')
 (P/f'repair-{n}.json').write_text(json.dumps(dict(number=n,head=rows[n]['headRefOid'],manifest_path='research/'+root+'/MANIFEST.json',original_sha256=hashlib.sha256(original).hexdigest(),missing_metadata_hash=missing,repaired_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),repair='Remove only absent .gitattributes checkout metadata; all present source/data pins exact'),indent=2)+'\n')
 out=P/f'repaired-{n}-out';cmd=[PY,'-B',str(src/'research'/root/'verify.py'),*flags,str(out)];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PATH=str(Path(PY).parent)+':'+os.environ['PATH'],CPATH=str(R/'research/e8-bit-carrier-skeleton/portable-include')+':/tmp/coordinated-crossover-v2.PSyYno/deps/include');start=time.time();log=P/f'pr{n}-repaired.txt';print('START',n,flush=True)
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
