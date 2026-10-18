from pathlib import Path
import json,subprocess,hashlib,time,platform
from process_tree_watch import ProcessTreeWatch
P=Path('/tmp/pr-efficient1900');D=P/'sources/1830';py='/tmp/pr-efficient200-venv/bin/python'; before={f.relative_to(D).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in D.rglob('*') if f.is_file() and '.git' not in f.relative_to(D).parts};commands=[];started=time.monotonic();peak=0;status='passed'
with (P/'check-1830.log').open('wb') as log:
 for script,args,limit in [('test_ci.py',['-I','-B'],60),('ci.py',['-I','-O','-B'],600)]:
  cmd=[py,*args,'research/h6-compensation-network/'+script];log.write((json.dumps(dict(argv=cmd,timeout_seconds=limit))+'\n').encode());log.flush();t=time.monotonic();proc=subprocess.Popen(cmd,cwd=D,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);watch=ProcessTreeWatch(proc.pid);reason=None
  while proc.poll() is None:
   rss,_=watch.sample();peak=max(peak,rss)
   if rss>1024*1024:reason='memory_guard_1GiB';break
   if time.monotonic()-t>limit:reason='timeout';break
   time.sleep(.5)
  if reason:watch.stop()
  code=proc.wait();commands.append(dict(argv=cmd,timeout_seconds=limit,exit_code=code,stop_reason=reason,seconds=time.monotonic()-t));log.write((json.dumps(commands[-1])+'\n').encode());log.flush()
  if reason or code:status='budget_deferred' if reason else 'failed';break
changed={k:dict(before=v,after=hashlib.sha256((D/k).read_bytes()).hexdigest() if (D/k).exists() else None) for k,v in before.items() if not (D/k).exists() or hashlib.sha256((D/k).read_bytes()).hexdigest()!=v}
if changed:status='failed'
receipt=dict(number=1830,head=json.loads((P/'1830.json').read_text())['headRefOid'],status=status,seconds=time.monotonic()-started,commands=commands,input_sha256=before,changed_files_after=changed,maximum_sampled_descendant_rss_kib=peak,log_sha256=hashlib.sha256((P/'check-1830.log').read_bytes()).hexdigest(),environment=dict(python=subprocess.check_output([py,'--version'],text=True).strip(),platform=platform.platform()),scope='Complete successor fresh-export gate, optimized semantic controls and CI boundary regressions. Prior billion-entry census retained, not rerun. No full physical program, precision propagation, all-size supplier or new kappa.')
(P/'check-1830.json').write_text(json.dumps(receipt,indent=2)+'\n');print(status,round(receipt['seconds'],2),peak,flush=True)
