import pathlib,json,subprocess,hashlib,time,platform,sys,os,signal
P=pathlib.Path('/tmp/pr-efficient1800');py='/tmp/pr-efficient200-venv/bin/python'
for n in ['tools-native']:
 root=P/'combined-tools';meta={'headRefOid':json.loads((P/'selection.json').read_text())['baseline']};start=time.monotonic();commands=[];status='passed';maxrss=0
 paths=[f for sub in ['scripts','tests','research/p104-native-channel'] for f in (root/sub).rglob('*.py')];before={f.relative_to(root).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in paths}
 queue=[([py,'-B','tests/test_research_bytecode_isolation.py','--p104-probe'],300,'Actual retained P104 clean, contaminated and cache-isolated native verifier: identical complete original receipt and source bytes')]
 with (P/f'check-{n}.log').open('wb') as log:
  for i,(cmd,timeout,scope) in enumerate(queue):
   log.write((json.dumps(dict(argv=cmd,timeout_seconds=timeout,checks=scope))+'\n').encode());log.flush();t=time.monotonic();p=subprocess.Popen(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);reason=None
   while p.poll() is None:
    if time.monotonic()-t>timeout:reason='timeout';break
    rows=subprocess.check_output(['ps','-axo','pid=,pgid=,rss='],text=True);rss=sum(int(z[2]) for line in rows.splitlines() if len(z:=line.split())==3 and int(z[1])==p.pid);maxrss=max(maxrss,rss)
    if rss>1024*1024:reason='memory_guard_1GiB';break
    time.sleep(.5)
   try:os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   code=p.wait();commands.append(dict(argv=cmd,timeout_seconds=timeout,exit_code=code,seconds=time.monotonic()-t,stop_reason=reason,checks=scope));log.write((json.dumps(commands[-1])+'\n').encode());log.flush()
   if reason or code:status='budget_deferred' if reason else 'failed';break
 after={f.relative_to(root).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in paths if f.exists()};d=dict(number=n,head=meta['headRefOid'],status=status,seconds=time.monotonic()-start,commands=commands,commands_expected=len(queue),input_sha256=before,changed_files_after={k:dict(before=v,after=after.get(k)) for k,v in before.items() if after.get(k)!=v},log_sha256=hashlib.sha256((P/f'check-{n}.log').read_bytes()).hexdigest(),environment=dict(python=subprocess.check_output([py,'--version'],text=True).strip(),platform=platform.platform()),maximum_sampled_process_group_rss_kib=maxrss,resource_guard='One package at a time; declared per-command timeout and sampled1GiB process-group RSS guard; group cleanup on every terminal outcome. No Lean launched.',scope='Exact-head scoped registered commands only; mechanism review and publication separate. A timeout/setup failure is not mathematical evidence.')
 (P/f'check-{n}.json').write_text(json.dumps(d,indent=2)+'\n');print(n,status,round(d['seconds'],2),'seconds','changed',len(d['changed_files_after']),flush=True)
