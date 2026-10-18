from pathlib import Path
import subprocess,json,os,hashlib,time,signal,shutil,platform
P=Path('/tmp/pr-efficient1900');D=P/'sources/2830';pkg=D/'research/a2-family-b-locus';py='/tmp/pr-efficient1800/floor-venv/bin/python';out=P/'blocus-output';shim=P/'serial-bin';shim.mkdir(exist_ok=True)
xargs=shutil.which('xargs');s=shim/'xargs';s.write_text('#!/usr/bin/env python3\nimport os,sys\na=sys.argv[1:]\nfor i in range(len(a)-1):\n if a[i]=="-P":a[i+1]="1"\nos.execv('+repr(xargs)+', ['+repr(xargs)+']+a)\n');s.chmod(0o755)
files={p.relative_to(D).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in D.rglob('*') if p.is_file()}
cmd=['bash',str(pkg/'verify.sh'),str(out)];env=os.environ.copy();env.update(PYTHON=py,PATH=str(shim)+os.pathsep+env['PATH']);start=time.monotonic();limit=1800;peak=0;reason=None
with (P/'check-2830.log').open('wb') as log:
 p=subprocess.Popen(cmd,cwd=D,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 while p.poll() is None:
  rss=sum(int(z[2]) for line in subprocess.check_output(['ps','-axo','pid=,pgid=,rss='],text=True).splitlines() if len(z:=line.split())==3 and int(z[1])==p.pid);peak=max(peak,rss)
  if rss>1048576:reason='memory_guard_1GiB';break
  if time.monotonic()-start>limit:reason='timeout';break
  time.sleep(.5)
 try:os.killpg(p.pid,signal.SIGKILL)
 except ProcessLookupError:pass
 code=p.wait()
changed=[k for k,v in files.items() if not (D/k).exists() or hashlib.sha256((D/k).read_bytes()).hexdigest()!=v]
r=dict(number=2830,head=json.loads((P/'2830.json').read_text())['headRefOid'],status='passed' if code==0 and not reason and not changed else 'deferred' if reason else 'failed',exit_code=code,stop_reason=reason,seconds=time.monotonic()-start,timeout_seconds=limit,maximum_sampled_process_group_rss_kib=peak,argv=cmd,python=py,serial_xargs_wrapper=s.read_text(),source_sha256=files,changed_files_after=changed,log_sha256=hashlib.sha256((P/'check-2830.log').read_bytes()).hexdigest(),scope='Original complete verify.sh with xargs concurrency lowered to one. Output logs compared byte-for-byte by upstream script. Written proof and parent hypotheses reviewed separately.')
(P/'check-2830.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],round(r['seconds'],2),peak,flush=True)
