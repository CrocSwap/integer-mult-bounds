from pathlib import Path
import json,subprocess,hashlib,time,os
from process_tree_watch import ProcessTreeWatch
P=Path('/tmp/pr-efficient1900');D=P/'sources/2244';pkg=D/'research/line-system-saturation';before={f.relative_to(D).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in D.rglob('*') if f.is_file()};out=P/'line-system-output';assert not out.exists();cmd=['bash',str(pkg/'verify.sh'),str(out)];env=dict(os.environ,PYTHON='/tmp/pr-efficient200-venv/bin/python');env.pop('GAP',None);start=time.monotonic();peak=0;reason=None
with (P/'check-2244.log').open('wb') as log:
 proc=subprocess.Popen(cmd,cwd=D,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);watch=ProcessTreeWatch(proc.pid)
 while proc.poll() is None:
  rss,_=watch.sample();peak=max(peak,rss)
  if rss>1024*1024:reason='memory_guard_1GiB';break
  if time.monotonic()-start>600:reason='timeout_600s';break
  time.sleep(.5)
 if reason:watch.stop()
 code=proc.wait()
changed={k:v for k,v in before.items() if not (D/k).exists() or hashlib.sha256((D/k).read_bytes()).hexdigest()!=v};status='budget_deferred' if reason else 'passed' if code==0 and not changed else 'failed';d=dict(number=2244,head=json.loads((P/'2244.json').read_text())['headRefOid'],status=status,argv=cmd,timeout_seconds=600,exit_code=code,stop_reason=reason,seconds=time.monotonic()-start,maximum_sampled_descendant_rss_kib=peak,input_sha256=before,changed_files_after=changed,log_sha256=hashlib.sha256((P/'check-2244.log').read_bytes()).hexdigest(),scope='Seven complete standard-library stages and source manifest checks. Optional GAP character-table stage not rerun; archived author evidence and external multiplier citation remain distinct. Written theorem review pending. No new supplier or kappa.');(P/'check-2244.json').write_text(json.dumps(d,indent=2)+'\n');print(status,round(d['seconds'],2),peak,flush=True)
