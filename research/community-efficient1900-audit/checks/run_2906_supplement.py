from pathlib import Path
import json,subprocess,hashlib,time,platform,os,signal
P=Path('/tmp/pr-efficient1900');D=P/'combined-2906';S=D;py='/tmp/pr-efficient200-venv/bin/python';start=time.monotonic();commands=[];status='passed';maxrss=0
paths=[f for f in D.rglob('*') if f.is_file() and '.git' not in f.relative_to(D).parts];before={f.relative_to(D).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}
q=[(D,[py,'-I','-O','-B','tests/test_isolated_historical_completion.py','-v'],120,'All seven actual historical overlay tests, including six additional routes'),
(D,[py,'-I','-O','-B','tests/test_isolated_test_cancellation.py','-v'],120,'Current cancellation regressions; native Linux tests skip explicitly'),
(D,[py,'-I','-B',str(P/'baseline_2906.py')],120,'Independent unchanged-baseline falsification: exactly four lifetime assertions must fail')]

with (P/'check-2906-supplement.log').open('wb') as log:
 for root,cmd,timeout,scope in q:
  log.write((json.dumps(dict(cwd=str(root),argv=cmd,timeout_seconds=timeout,checks=scope))+'\n').encode());log.flush();t=time.monotonic();proc=subprocess.Popen(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);reason=None
  while proc.poll() is None:
   if time.monotonic()-t>timeout:reason='timeout';break
   rows=subprocess.check_output(['ps','-axo','pid=,pgid=,rss='],text=True);rss=sum(int(z[2]) for line in rows.splitlines() if len(z:=line.split())==3 and int(z[1])==proc.pid);maxrss=max(maxrss,rss)
   if rss>1024*1024:reason='memory_guard_1GiB';break
   time.sleep(.5)
  try:os.killpg(proc.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  code=proc.wait();commands.append(dict(cwd=str(root),argv=cmd,timeout_seconds=timeout,exit_code=code,seconds=time.monotonic()-t,stop_reason=reason,checks=scope));log.write((json.dumps(commands[-1])+'\n').encode());log.flush()
  if reason or code:status='budget_deferred' if reason else 'failed';break
changed={k:dict(before=v,after=hashlib.sha256((D/k).read_bytes()).hexdigest() if (D/k).exists() else None) for k,v in before.items() if not (D/k).exists() or hashlib.sha256((D/k).read_bytes()).hexdigest()!=v}
d=dict(number=2906,head=json.loads((P/'2906.json').read_text())['headRefOid'],status=status,seconds=time.monotonic()-start,commands=commands,commands_expected=len(q),input_sha256=before,changed_files_after=changed,log_sha256=hashlib.sha256((P/'check-2906-supplement.log').read_bytes()).hexdigest(),maximum_sampled_process_group_rss_kib=maxrss,environment=dict(python=subprocess.check_output([py,'--version'],text=True).strip(),platform=platform.platform()),scope='Current composed runner lifetime repair; original six Linux tests ported only to native macOS retained process observers. No Linux replay, resource-cap or detached-session containment claim.')
(P/'check-2906-supplement.json').write_text(json.dumps(d,indent=2)+'\n');print(status,round(d['seconds'],2),'seconds',len(changed),'changed',flush=True)
