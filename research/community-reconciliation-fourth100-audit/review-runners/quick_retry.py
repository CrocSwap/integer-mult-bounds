import subprocess,os,json,gzip,hashlib,time,platform,tarfile,io,sys
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');R=Path('/tmp/integer-mult-queue-20261013');PY='/tmp/integer-mult-review-venv/bin/python';rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']}
items={521:('native-unipotent-fusion',[['check.py']]),630:('exact-ade-census',[['test_census.py'],['census.py','--check','{pkg}/RESULTS.json']]),631:('e8-continuation-20261013/punctures',[['verify.py','--negative-controls','--write','{out}/results.json']]),661:('r420-phase-b-frame-bound',[['verify.py']]),663:('dirty-commutator-audit',[['verify.py','--check']]),665:('clean-residual-dilation',[['verify.py']]),666:('composite-cyclic-bezout',[['verify.py','--check','{pkg}/EXPECTED.json'],['verify_lifting.py','--check','{pkg}/LIFTING-EXPECTED.json'],['test_verify.py'],['test_lifting.py']]),667:('exact-log-horner',[['verify.py'],['test_package.py']])}
record=P/'quick-retry-execution.json';receipts=json.load(open(record))if record.exists()else[]
for n in map(int,sys.argv[1:]):
 root,commands=items[n];src=P/f'quick-retry-{n}';src.mkdir();raw=subprocess.check_output(['git','archive',rows[n]['headRefOid'],'research/'+root],cwd=R)
 with tarfile.open(fileobj=io.BytesIO(raw))as t:t.extractall(src,filter='data')
 pkg=src/'research'/root
 pin_name,key={661:('SOURCES.json','inputs'),665:('SOURCE-PINS.json','local_sha256'),666:('SOURCE.json','input_sha256')}[n]
 pins=json.load(open(pkg/pin_name))[key]
 for path,digest in pins.items():
  raw=subprocess.check_output(['git','show',rows[n]['headRefOid']+':'+path],cwd=R);assert hashlib.sha256(raw).hexdigest()==digest
  dest=src/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 out=P/f'quick-retry-{n}-out';out.mkdir();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');start=time.time();log=P/f'pr{n}-quick-retry.txt';print('START',n,flush=True);actual=[]
 with log.open('w')as f:
  for c in commands:
   cmd=[PY,'-B',str(pkg/c[0]),*[v.format(pkg=pkg,out=out)for v in c[1:]]];actual.append(cmd);z=subprocess.run(cmd,cwd=src,env=env,stdout=f,stderr=subprocess.STDOUT)
   if z.returncode:break
 receipt=dict(number=n,head=rows[n]['headRefOid'],commands=actual,cwd=str(src),exit_code=z.returncode,seconds=time.time()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest(),environment=platform.platform(),scope='Fresh unmodified scoped mathematical/tooling checker; no full multiplication theorem claim.')
 receipts.append(receipt);record.write_text(json.dumps(receipts,indent=2)+'\n');print('DONE',n,z.returncode,round(receipt['seconds']),flush=True)
