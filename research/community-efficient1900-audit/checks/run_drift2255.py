from pathlib import Path
import json,subprocess,hashlib,time
from process_tree_watch import ProcessTreeWatch
P=Path('/tmp/pr-efficient1900');D=Path('/tmp/pr-efficient1200/sources/2255');head=json.loads((P/'2255.json').read_text())['headRefOid'];py='/tmp/pr-efficient200-venv/bin/python'
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=D)
subprocess.run(['git','checkout','--detach',head],cwd=D,check=True,stdout=subprocess.DEVNULL)
cmd=[py,'-I','-B','research/live-pin-drift-audit-seed5985/verify.py'];start=time.monotonic();peak=0;reason=None
with (P/'check-2255.log').open('wb') as log:
 proc=subprocess.Popen(cmd,cwd=D,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);watch=ProcessTreeWatch(proc.pid)
 while proc.poll() is None:
  rss,_=watch.sample();peak=max(peak,rss)
  if rss>1048576:reason='sampled_memory_guard_1GiB';watch.stop();break
  if time.monotonic()-start>600:reason='600_second_timeout';watch.stop();break
  time.sleep(.25)
 code=proc.wait()
changes=subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=D,text=True)
r=dict(number=2255,head=head,status='passed' if code==0 and reason is None and not changes else 'held',argv=cmd,exit_code=code,seconds=time.monotonic()-start,peak_sampled_descendant_rss_kib=peak,stop_reason=reason,tracked_changes_after=changes,log_sha256=hashlib.sha256((P/'check-2255.log').read_bytes()).hexdigest(),scope='Full original revised audit in the complete frozen author checkout. Historical inventory, all pins, Git history and four named failures checked; candidate drift is not a consumer failure claim. No current frontier or historical pins changed.')
(P/'check-2255.json').write_text(json.dumps(r,indent=2)+'\n');print(r,flush=True)
