import subprocess,os,json,gzip,hashlib,time,platform,tarfile,io,shutil,sys
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');R=Path('/tmp/integer-mult-queue-20261013');PY='/tmp/integer-mult-review-venv/bin/python';rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']};pre=P/'cold-635'
items={648:'gauge44-repack',649:'gauge44-bit589',652:'gauge44-bit589b',655:'gauge44-layered',656:'gauge44-layered-b',659:'gauge44-notri-layered',664:'gauge44-promo'}
record=P/'gauge-execution.json';receipts=json.load(open(record))if record.exists()else[]
for n in map(int,sys.argv[1:]):
 root=items[n];src=P/f'gauge-{n}';src.mkdir();raw=subprocess.check_output(['git','archive',rows[n]['headRefOid'],'research/'+root],cwd=R)
 with tarfile.open(fileobj=io.BytesIO(raw))as t:t.extractall(src,filter='data')
 pkg=src/'research'/root;out=P/f'gauge-{n}-out';out.mkdir();common=['--main',str(R),'--pr635',str(pre)];commands=[[PY,'-B',str(pkg/'verify_manifest.py')],[PY,'-B',str(pkg/'construction/reproduce.py'),*common,'--out',str(out/'base'),'--until','phases'if n<655 else'word']];local=out/'base/local'
 if n in [655,656]:
  commands.append([PY,'-B',str(pkg/'construction/layers/reproduce_layers.py'),*common,'--word-dir',str(out/'base'),'--out',str(out/'layered')]);local=out/'layered/local';word=out/'layered/layers/FULL-WORD.json.gz'
 if n in [659,664]:
  commands.append([PY,'-B',str(pkg/'construction/notri/reproduce_notri.py'),*common,'--word-dir',str(out/'base'),'--out',str(out/'notri'),'--word-only'])
  commands.append([PY,'-B',str(pkg/'construction/layers_np/reproduce_np.py'),*common,'--notri-dir',str(out/'notri'),'--hamming',str(out/'base/hamming'),'--out',str(out/'np')]);local=out/'np/local';word=out/'np/layers/FULL-WORD.json.gz'
 if n==664:
  commands.append([PY,'-B',str(pkg/'construction/promo/reproduce_promo.py'),*common,'--np-dir',str(out/'np'),'--k','3','--out',str(out/'promo')]);local=out/'promo/local';word=out/'promo/promo/FULL-WORD.json.gz'
 if n>=655:commands.append([PY,'-B',str(pkg/'independent/audit_local.py'),'--word',str(word),'--main',str(R),'--output',str(out/'independent.json')])
 commands.append([PY,'-B',str(pkg/'verify_global.py'),'--main',str(R),'--local',str(local),'--work',str(out/'global')])
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PATH=str(Path(PY).parent)+':'+os.environ['PATH']);start=time.time();log=P/f'pr{n}-gauge.txt';print('START',n,flush=True);actual=[]
 with log.open('w')as f:
  for cmd in commands:
   actual.append(cmd);f.write('COMMAND '+json.dumps(cmd)+'\n');f.flush();z=subprocess.run(cmd,cwd=src,env=env,stdout=f,stderr=subprocess.STDOUT)
   if z.returncode:break
 receipt=dict(number=n,head=rows[n]['headRefOid'],commands=actual,cwd=str(src),exit_code=z.returncode,seconds=time.time()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest(),environment=platform.platform(),scope='Fresh reconstructed local phases and complete global admission under source-pinned dependencies; unchanged bit is cited and repriced.')
 keep=P/f'pr{n}-outputs';keep.mkdir(exist_ok=True)
 for f in out.rglob('*'):
  if f.is_file()and (f.suffix=='.log'or f.name in ['RESULT.json','RECEIPT.json','VERIFICATION.json','FAILURE.json','ASSEMBLY.json','INVOICE.json','independent.json']):
   dest=keep/f.relative_to(out);dest=dest.with_name(dest.name+'.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 receipts.append(receipt);record.write_text(json.dumps(receipts,indent=2)+'\n');print('DONE',n,z.returncode,round(receipt['seconds']),flush=True)
 if z.returncode==0:shutil.rmtree(out)
