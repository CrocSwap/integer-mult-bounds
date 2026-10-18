from pathlib import Path
import json,subprocess,hashlib,time,platform,os,signal
P=Path('/tmp/pr-efficient1900');py='/tmp/pr-efficient200-venv/bin/python'
for n in [2903]:
 if json.loads((P/f'provenance-{n}-metadata.json').read_text())['status']!='PASS':continue
 D=P/'sources'/str(n);pkg=next(q for q in (D/'research').iterdir() if (q/'VERIFY.json').exists());manifest=json.loads((pkg/'VERIFY.json').read_text());paths=[f for f in D.rglob('*') if f.is_file() and '.git' not in f.relative_to(D).parts];before={f.relative_to(D).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in paths};commands=[];start=time.monotonic();status='passed';maxrss=0
 with (P/f'check-{n}.log').open('wb') as log:
  for row in manifest['commands']:
   cmd=[a.replace('{python}',py).replace('{package}',str(pkg)) for a in row['argv']];timeout=row['timeout_seconds'];log.write((json.dumps(dict(cwd=str(D),argv=cmd,timeout_seconds=timeout,checks=row['checks']))+'\n').encode());log.flush();t=time.monotonic();proc=subprocess.Popen(cmd,cwd=D,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);reason=None
   while proc.poll() is None:
    if time.monotonic()-t>timeout:reason='timeout';break
    raw=subprocess.check_output(['ps','-axo','pid=,pgid=,rss='],text=True);rss=sum(int(z[2]) for line in raw.splitlines() if len(z:=line.split())==3 and int(z[1])==proc.pid);maxrss=max(maxrss,rss)
    if rss>1024*1024:reason='memory_guard_1GiB';break
    time.sleep(.5)
   try:os.killpg(proc.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   code=proc.wait();result=dict(argv=cmd,timeout_seconds=timeout,exit_code=code,seconds=time.monotonic()-t,stop_reason=reason,checks=row['checks']);commands.append(result);log.write((json.dumps(result)+'\n').encode());log.flush()
   if reason or code:status='budget_deferred' if reason else 'failed';break
 changed={k:dict(before=v,after=hashlib.sha256((D/k).read_bytes()).hexdigest() if (D/k).exists() else None) for k,v in before.items() if not (D/k).exists() or hashlib.sha256((D/k).read_bytes()).hexdigest()!=v}
 if changed:status='failed'
 receipt=dict(number=n,head=json.loads((P/f'{n}.json').read_text())['headRefOid'],status=status,seconds=time.monotonic()-start,commands=commands,commands_expected=len(manifest['commands']),input_sha256=before,changed_files_after=changed,log_sha256=hashlib.sha256((P/f'check-{n}.log').read_bytes()).hexdigest(),maximum_sampled_process_group_rss_kib=maxrss,environment=dict(python=subprocess.check_output([py,'--version'],text=True).strip(),platform=platform.platform()),scope='Declared complete finite replay and defect controls. Written source/lifetime proof is reviewed separately. No full selected GL64 execution, physical allocator, supplier admission or new kappa.')
 (P/f'check-{n}.json').write_text(json.dumps(receipt,indent=2)+'\n');print(n,status,round(receipt['seconds'],2),'seconds',maxrss,'KiB',flush=True)
