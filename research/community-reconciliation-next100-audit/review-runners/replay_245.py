from pathlib import Path
import subprocess,json,gzip,time,hashlib,os,shutil,tarfile
R=Path('/tmp/integer-mult-queue-20261013');P=Path('/tmp/reconciliation-next100-20261013');rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']};g=['git','-c','maintenance.auto=false','-c','gc.auto=0']
pins={'bit':('a1175449f34d39ff933d9d8ab23ced1f32b290ec','research/paired-cube-diagonal-bit-168'),'complex':('187e1010ac8b259af8e9b5166f68b64bc27b4b47','research/source-assisted-complex-flow'),'served':('8786fec0148a41409874cad133123da227d93751','research/served-diagonal-bit'),'frames':('b739fc226a54a4a507989aa1bef092d491287451','research/butterfly-coordinated-bit-211')}
roots={}
for name,(head,prefix) in pins.items():
 if subprocess.run(g+['cat-file','-e',head],cwd=R).returncode:subprocess.run(g+['fetch','--no-tags','origin',head],cwd=R,check=True)
 root=P/('parent245-'+name);subprocess.run(g+['worktree','add','--detach','--no-checkout',str(root),head],cwd=R,check=True)
 # Include all research paths on complex side: its arithmetic wrapper reads several suppliers. Sparse roots preserve exact commits.
 paths=['research'] if name=='complex' else [prefix]
 subprocess.run(g+['sparse-checkout','set','--cone',*paths],cwd=root,check=True)
 subprocess.run(g+['reset','--hard',head],cwd=root,check=True,stdout=subprocess.DEVNULL);roots[name]=root
work=P/'late245';work.mkdir();head=rows[245]['headRefOid'];prefix='research/served-frame-composition'
proc=subprocess.Popen(g+['archive',head,prefix],cwd=R,stdout=subprocess.PIPE)
with tarfile.open(fileobj=proc.stdout,mode='r|') as t:t.extractall(work,filter='data')
assert proc.wait()==0
out=P/'pr245-fresh';cmd=['python3.12','-B',str(work/prefix/'verify.py')]
for name,root in roots.items():cmd.extend(['--'+name+'-root',str(root)])
cmd+=['--output',str(out)];log=P/'pr245-fresh.txt';start=time.monotonic()
with log.open('w') as f:ret=subprocess.run(cmd,cwd=work,stdout=f,stderr=subprocess.STDOUT).returncode
receipt=dict(number=245,head=head,command=cmd,parents={name:h for name,(h,p) in pins.items()},exit_code=ret,seconds=time.monotonic()-start,log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
(P/'composition-execution.json').write_text(json.dumps([receipt],indent=2)+'\n');print(ret,receipt['seconds'],flush=True)
for name,root in roots.items():subprocess.run(g+['worktree','remove','--force',str(root)],cwd=R,check=True)
if out.exists():
 for name in ('certificate.json','execution.json'):
  f=out/name
  if f.exists():(P/('pr245-'+name+'.gz')).write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 shutil.rmtree(out)
shutil.rmtree(work)
