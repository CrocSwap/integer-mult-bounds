import json,subprocess,tarfile,io,os,time,hashlib,gzip,shutil,sys
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');R=Path('/tmp/integer-mult-queue-20261013');PY='/tmp/integer-mult-review-venv/bin/python';rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']}
roots={515:'e8-r685-inline-deletions',633:'pr627-independent-audit-20261013',634:'lower-bounds-coding-gap',651:'complex-delivery-rigidity',658:'layered-joint-owners'}
record=P/'extra-execution.json';receipts=json.load(open(record))if record.exists()else[]
def extract(n,paths,src):
 raw=subprocess.check_output(['git','archive',rows[n]['headRefOid'],*paths],cwd=R)
 with tarfile.open(fileobj=io.BytesIO(raw))as t:t.extractall(src,filter='data')
for n in map(int,sys.argv[1:]):
 src=P/f'extra-{n}';root=roots[n];pkg=src/'research'/root;out=P/f'extra-{n}-out'
 if n==633:
  for key,dest in [('multicold','complex-multicold'),('structural_gain','structural-gain'),('larger_gain','complex-k492-owner-repair/vendor/larger_gain'),('joint_prefix','complex-joint-prefix'),('frame_coalescing','kernel-frame-coalescing'),('direct_delivery','direct-delivery504-global')]:
   origin=next((P/'cold-deps'/key/'research').iterdir());shutil.copytree(origin,src/'research'/dest,dirs_exist_ok=True)
  extract(n,['research/complex-571-cold14-k492b','research/five-stage-gen4-banks'],src)
  cmd=['sh',str(pkg/'run_replay.sh'),str(out)]
 elif n==651:
  extract(n,['research/complex-571-cold14-k492','research/direct-delivery504-global/inputs/hamming'],src);cmd=['sh',str(pkg/'reproduce.sh'),str(out)]
 elif n==634:
  extract(n,['research/complex-571-hpeq5/data/EXPECTED.json','research/e8-bit-p111-tuned/tune/EXPECTED.json'],src);cmd=['bash',str(pkg/'verify.sh'),str(out)]
 elif n==658:
  # PR656 original parent retained separately, never substitute current-main versions.
  parent=P/'extra658-parent';parent.mkdir(exist_ok=True);raw=subprocess.check_output(['git','archive',rows[656]['headRefOid'],'research/gauge44-layered-b'],cwd=R)
  with tarfile.open(fileobj=io.BytesIO(raw))as t:t.extractall(parent,filter='data')
  cmd=[PY,'-B',str(pkg/'verify.py'),'--main',str(R),'--parent',str(parent/'research/gauge44-layered-b'),'--pr635',str(P/'cold-635'),'--out',str(out)]
 else:cmd=[PY,'-B',str(pkg/'verify.py'),str(out)]
 env=dict(os.environ,PYTHON=PY,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PATH=str(Path(PY).parent)+':'+os.environ['PATH'],CPATH=str(R/'research/e8-bit-carrier-skeleton/portable-include')+':/tmp/coordinated-crossover-v2.PSyYno/deps/include');start=time.time();log=P/f'pr{n}-extra.txt';print('START',n,flush=True)
 with log.open('w')as f:z=subprocess.run(cmd,cwd=src,env=env,stdout=f,stderr=subprocess.STDOUT)
 receipt=dict(number=n,head=rows[n]['headRefOid'],command=cmd,cwd=str(src),exit_code=z.returncode,seconds=time.time()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest(),scope='Fresh contributed wrapper; optional steps and inherited cited suppliers are identified in the original log.')
 keep=P/f'pr{n}-outputs';keep.mkdir(exist_ok=True)
 for f in out.rglob('*'):
  if f.is_file()and(f.suffix=='.log'or f.name in ['RESULT.json','RECEIPT.json','VERIFICATION.json','INDEPENDENT-OWNERS.json','FAILURE.json']):
   dest=keep/f.relative_to(out);dest=dest.with_name(dest.name+'.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 receipts.append(receipt);record.write_text(json.dumps(receipts,indent=2)+'\n');print('DONE',n,z.returncode,round(receipt['seconds']),flush=True)
 if z.returncode==0:shutil.rmtree(out)
