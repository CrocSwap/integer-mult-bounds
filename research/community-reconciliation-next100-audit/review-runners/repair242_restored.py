from pathlib import Path
import subprocess,json,gzip,time,hashlib,os,shutil,tarfile
P=Path('/tmp/reconciliation-next100-20261013');R=Path('/tmp/integer-mult-queue-20261013');A=R/'research/community-reconciliation-next100-audit/adapters/pr242';A.mkdir(parents=True,exist_ok=True);row=next(r for r in json.load(open(P/'snapshot.json'))['pull_requests']if r['number']==242);head=row['headRefOid'];prefix='research/source527-five-stage-crossover';work=P/'repair242';work.mkdir();proc=subprocess.Popen(['git','archive',head,prefix],cwd=R,stdout=subprocess.PIPE)
with tarfile.open(fileobj=proc.stdout,mode='r|')as t:t.extractall(work,filter='data')
assert proc.wait()==0
pkg=work/prefix;
for item in json.load(open(P/'pr242-missing.json')):
 data=subprocess.check_output(['git','cat-file','blob',item['available']['blob']],cwd=R);assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'];dest=pkg/item['path'];assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
original=(pkg/'verify.sh').read_bytes();s=original.decode().replace('\r\n','\n');line=next(l for l in s.splitlines()if l.startswith('root='));s=s.replace(line,'root=${PR242_SOURCE_ROOT:?Set PR242_SOURCE_ROOT to the original immutable package}')
(A/'verify-lf.sh').write_text(s);(A/'SOURCE.json').write_text(json.dumps(dict(head=head,original_path=prefix+'/verify.sh',original_sha256=hashlib.sha256(original).hexdigest(),adapter_sha256=hashlib.sha256(s.encode()).hexdigest(),changes=['CRLF to LF in launcher','Explicit immutable source root instead of launcher dirname']),indent=2)+'\n');(A/'README.md').write_text('''# PR242 shell-launcher portability repair

The original verify.sh contains CRLF line endings, so Bash rejects pipefail before
running a check. This separate LF launcher takes PR242_SOURCE_ROOT as its source
root. All original package bytes remain unchanged and pass FILES.json checks.
The original tree also omits28 files already pinned by FILES.json. MISSING-SOURCES.json
identifies exact matching retained Git blobs; restore_sources.py supplies those bytes.
No stage, coefficient, compiler command or assertion is removed.

Run `PR242_SOURCE_ROOT=/path/to/source527-five-stage-crossover bash verify-lf.sh`
with the original package requirements and the platform C++ include configuration.
''')
out=P/'repair242-out';out.mkdir();env={**os.environ,'PR242_SOURCE_ROOT':str(pkg),'TMPDIR':str(out),'PATH':'/tmp/integer-mult-review-venv/bin:'+os.environ['PATH'],'CXX':'clang++','CPATH':str(R/'research/e8-bit-carrier-skeleton/portable-include')+':/tmp/coordinated-crossover-v2.PSyYno/deps/include','PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'};cmd=['bash',str(A/'verify-lf.sh')];log=P/'pr242-restored.txt';start=time.monotonic()
with log.open('w')as f:ret=subprocess.run(cmd,cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT).returncode
receipt=dict(number=242,head=head,command=cmd,environment={k:env[k]for k in ['PR242_SOURCE_ROOT','TMPDIR','CXX','CPATH']},exit_code=ret,seconds=time.monotonic()-start,log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),scope='Separate LF launcher and 28 omitted manifest-pinned files restored from exact SHA-256 matching retained Git blobs; no scientific source/hash check changed');(P/'shell-repair-execution.json').write_text(json.dumps(json.load(open(P/'shell-repair-execution.json'))+[receipt],indent=2)+'\n');print(ret,receipt['seconds'],flush=True)
for f in out.rglob('*'):
 if f.is_file()and f.suffix in ('.json','.log')and f.stat().st_size<2000000 and not any(x in f.relative_to(out).parts for x in ('deps','upstream','source','build')):
  dest=P/'pr242-repair-outputs'/f.relative_to(out);dest=dest.with_name(dest.name+'.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(gzip.compress(f.read_bytes(),mtime=0))
shutil.rmtree(out);shutil.rmtree(work)
