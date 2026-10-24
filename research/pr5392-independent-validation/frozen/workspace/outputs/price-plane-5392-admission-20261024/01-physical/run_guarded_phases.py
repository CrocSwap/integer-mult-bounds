#!/usr/bin/env python3
from pathlib import Path
import datetime,hashlib,json,os,resource,signal,subprocess,sys,time
HERE=Path(__file__).resolve().parent;SCRIPT=HERE/'check_phases.py';CAP=HERE.parent/'source-capsule'
def hashes():return {str(p.relative_to(CAP)):hashlib.sha256(p.read_bytes()).hexdigest() for p in CAP.rglob('*') if p.is_file()}
def limits():
 os.setsid();resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
pre=hashes();start=time.monotonic();stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();argv=[sys.executable,'-B',str(SCRIPT)]
with (HERE/'phase.stdout.log').open('w') as out,(HERE/'phase.stderr.log').open('w') as err:
 p=subprocess.Popen(argv,stdout=out,stderr=err,preexec_fn=limits);peak=0;stop=None
 while p.poll() is None:
  try:
   for l in Path('/proc/'+str(p.pid)+'/status').read_text().splitlines():
    if l.startswith('VmRSS:'):peak=max(peak,int(l.split()[1]))
  except FileNotFoundError:pass
  if time.monotonic()-start>120:
   stop='wall limit120seconds';os.killpg(p.pid,signal.SIGKILL);break
  time.sleep(.1)
 exitcode=p.wait()
result={'argv':argv,'code_sha256':hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),'started_utc':stamp,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':exitcode,'resource_stop':stop,'seconds':round(time.monotonic()-start,3),'peak_rss_kib':peak,'address_space_limit_bytes':512*1024**2,'wall_limit_seconds':120,'source_files':len(pre),'source_immutability':pre==hashes(),'stdout_bytes':(HERE/'phase.stdout.log').stat().st_size,'stderr_bytes':(HERE/'phase.stderr.log').stat().st_size}
(HERE/'PHASE-GUARD-RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));sys.exit(0 if exitcode==0 and not stop and result['source_immutability'] else 1)
