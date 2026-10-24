#!/usr/bin/env python3
"""Root-granted single serial registered normal/O replay; no candidate changes."""
from pathlib import Path
import datetime,hashlib,json,os,signal,subprocess,sys,time
HERE=Path(__file__).resolve().parent
CAPSULE=HERE/'capsule-5392-v2'
REPO=CAPSULE/'snapshot'
PACKAGE='research/native-transpose-owned'
LIMIT_KIB=1024*1024

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes():return {str(p.relative_to(CAPSULE)):sha(p) for p in sorted(CAPSULE.rglob('*')) if p.is_file()}
def descendants(pid):
 found=set();todo=[pid]
 while todo:
  current=todo.pop()
  if current in found:continue
  found.add(current)
  try:todo.extend(map(int,Path('/proc',str(current),'task',str(current),'children').read_text().split()))
  except (FileNotFoundError,ProcessLookupError):pass
 return found

def rss(pid):
 try:return next((int(x.split()[1]) for x in Path('/proc',str(pid),'status').read_text().splitlines() if x.startswith('VmRSS:')),0)
 except (FileNotFoundError,ProcessLookupError):return 0

def kill_owned(members):
 groups=set()
 for pid in members:
  try:groups.add(os.getpgid(pid))
  except ProcessLookupError:pass
 for pgid in groups:
  if pgid!=os.getpgrp():
   try:os.killpg(pgid,signal.SIGKILL)
   except ProcessLookupError:pass
 for pid in members:
  try:os.kill(pid,signal.SIGKILL)
  except ProcessLookupError:pass

def main():
 global CAPSULE,REPO,PACKAGE
 grant=json.loads((HERE/'ROOT-HEAVY-GRANT.json').read_text())
 if grant.get('authorized') is not True or grant.get('scope')!='one_registered_normal_then_optimized_pair':raise RuntimeError('Explicit root heavy-token grant required')
 version=grant.get('capsule_version','capsule-5392-v2')
 if version != 'capsule-5392-v2':raise RuntimeError('Unsupported frozen capsule version')
 CAPSULE=HERE/version;REPO=CAPSULE/'snapshot'
 identity=json.loads((CAPSULE/'IMMUTABLE-MANIFEST.json').read_text());PACKAGE=identity['package']
 if grant.get('candidate_head',identity['candidate_head'])!=identity['candidate_head']:raise RuntimeError('Granted candidate head mismatch')
 expected_pass=json.loads((REPO/PACKAGE/'RESULT.json').read_text())['status']
 digest=sha(CAPSULE/'IMMUTABLE-MANIFEST.json')
 if grant.get('capsule_manifest_sha256')!=digest:raise RuntimeError('Grant capsule mismatch')
 for row in grant['substantive_gate_receipts']:
  p=HERE.parents[2]/row['path']
  if sha(p)!=row['sha256']:raise RuntimeError('Gate receipt changed: '+str(p))
 if not 4<=len(grant['substantive_gate_receipts'])<=16:raise RuntimeError('Physical/phase, independent invoice, closure and funding receipts required')
 for row in grant.get('provenance_receipts',[]):
  if sha(HERE.parents[2]/row['path'])!=row['sha256']:raise RuntimeError('Provenance receipt changed')
 for row in grant['substantive_gate_receipts']:
  gate=json.loads((HERE.parents[2]/row['path']).read_text())
  for dep,digest in gate.get('closure_dependencies_sha256',{}).items():
   if sha(Path(dep))!=digest:raise RuntimeError('Funding dependency changed: '+dep)
 receipt=HERE/'BOUNDED-REGISTERED-RUN.json'
 if receipt.exists() or (HERE/'LIVE-HANDLE.json').exists():raise RuntimeError('Single-execution guard: prior handle/receipt exists')
 manifest=json.loads((REPO/PACKAGE/'VERIFY.json').read_text())
 if len(manifest['commands'])!=2 or any(c['timeout_seconds']!=550 for c in manifest['commands']):raise RuntimeError('Registered budget changed; request new grant')
 limit_seconds=sum(c['timeout_seconds'] for c in manifest['commands'])+60
 before=hashes();(HERE/'PRE-RUN-HASHES.json').write_text(json.dumps(before,indent=2)+'\n')
 env={k:v for k,v in os.environ.items() if not k.startswith('GIT_') and k not in ('PYTHONPATH','PYTHONOPTIMIZE','PYTHONINSPECT','PYTHONPYCACHEPREFIX','LEAN_AUDIT_BIN')}
 env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',GIT_NO_REPLACE_OBJECTS='1',GIT_NO_LAZY_FETCH='1',GIT_GRAFT_FILE=os.devnull,GIT_TERMINAL_PROMPT='0')
 scratch=HERE/'scratch';scratch.mkdir(exist_ok=False);env['TMPDIR']=str(scratch)
 command=[sys.executable,'-B','scripts/research_package.py','--package',PACKAGE]
 started=time.monotonic();peak=0;stop=None;samples=[];known=set()
 with (HERE/'REGISTERED-COLD.stdout.log').open('wb') as out,(HERE/'REGISTERED-COLD.stderr.log').open('wb') as err:
  process=subprocess.Popen(command,cwd=REPO,env=env,stdout=out,stderr=err,start_new_session=True)
  (HERE/'LIVE-HANDLE.json').write_text(json.dumps({'pid':process.pid,'argv':command,'cwd':str(REPO),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
  while process.poll() is None:
   seconds=time.monotonic()-started;members=descendants(process.pid);known|=members;total=sum(rss(p) for p in members);peak=max(peak,total)
   samples.append({'seconds':seconds,'rss_kib':total,'pids':sorted(members)})
   if seconds>limit_seconds:stop='total_timeout'
   if total>LIMIT_KIB:stop='aggregate_descendant_rss'
   if stop:kill_owned(members);break
   time.sleep(.1)
  code=process.wait()
 after=hashes();(HERE/'POST-RUN-HASHES.json').write_text(json.dumps(after,indent=2)+'\n')
 changed=sorted(k for k in before.keys()|after.keys() if before.get(k)!=after.get(k))
 logs=(HERE/'REGISTERED-COLD.stdout.log').read_text()
 status='PASS_COMPLETE_REGISTERED_NORMAL_AND_OPTIMIZED' if code==0 and stop is None and not changed and logs.count(expected_pass)==2 and 'PASS_REGISTERED_RESEARCH_PACKAGE' in logs else 'FAIL_OR_INCOMPLETE'
 result={'status':status,'candidate_head':identity['candidate_head'],'package':PACKAGE,'capsule_manifest_sha256':digest,'root_grant_sha256':sha(HERE/'ROOT-HEAVY-GRANT.json'),'argv':command,'cwd':str(REPO),'exit':code,'resource_stop':stop,'seconds':time.monotonic()-started,'peak_sampled_descendant_rss_kib':peak,'total_timeout_seconds':limit_seconds,'rss_limit_kib':LIMIT_KIB,'per_registered_command_timeout_seconds':550,'scientific_or_git_bytes_changed':changed,'hash_inventory_files':len(before),'python':sys.version,'stdout_sha256':sha(HERE/'REGISTERED-COLD.stdout.log'),'stderr_sha256':sha(HERE/'REGISTERED-COLD.stderr.log'),'samples':samples,'scope':'Exactly one own registered isolated -I/-Werror normal then optimized execution; source code unchanged. No Lean, Docker, discovery, native build, historical mathematical suite or independent reviewer engine rerun.'}
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='samples'}),flush=True)
 return 0 if status.startswith('PASS_') else 1
if __name__=='__main__':raise SystemExit(main())
