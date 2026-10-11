#!/usr/bin/env python3
"""Offline nine-source replay using six exact PR488/PR511 dependencies."""
import argparse,fcntl,hashlib,importlib.util,json,os,re,resource,signal,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
 resource.setrlimit(resource.RLIMIT_CPU,(60,62));os.setsid()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--lean',required=True);ap.add_argument('--input-foundation-root',required=True,help='Exact PR488 input-preparation package.');ap.add_argument('--dispatcher-foundation-root',required=True,help='Exact PR511 count-dispatcher package.');ap.add_argument('--build-dir',default='.build');ap.add_argument('--slot-service',help='Optional existing FIFO slot service exposing acquire(); does not change Lean inputs.');ap.add_argument('--lean-sha256');args=ap.parse_args()
 assert Path('/proc/self/status').is_file(),'Linux /proc is required for the stated memory review'
 roots={'package':ROOT,'pr488':Path(args.input_foundation_root).resolve(),'pr511':Path(args.dispatcher_foundation_root).resolve()}
 assert all(p.is_dir() for p in roots.values())
 source_for=lambda row:roots[row['origin']]/row['file']
 lean=Path(args.lean).resolve();assert lean.is_file()
 if args.lean_sha256:assert sha(lean)==args.lean_sha256
 version=subprocess.check_output([str(lean),'--version'],text=True).strip();assert re.search(r'\b4\.21\.0\b',version),version
 manifest=json.loads((ROOT/'MANIFEST.json').read_text());rows=manifest['compile_order'];names={r['module']for r in rows};seen=set()
 assert len(rows)==9 and manifest['source_bytes']==74140
 assert sum(r['origin']=='pr488' for r in rows)==2 and sum(r['origin']=='pr511' for r in rows)==4 and sum(r['origin']=='package' for r in rows)==3
 dependencies=json.loads((ROOT/'DEPENDENCIES.json').read_text())
 expected_commits={'pr488':'edd3102b415df5b9d6f633ac0a4dedcf69c58525','pr511':'79f7c03c7f820ab89955b75ef239cbaccc627e6e'}
 assert set(dependencies)==set(expected_commits)
 for alias,dependency in dependencies.items():
  assert dependency['commit']==expected_commits[alias]
  for dep in dependency['files']:
   row=next(r for r in rows if r['module']==dep['module']);assert row['origin']==alias and row['sha256']==dep['sha256'] and row['bytes']==dep['bytes']
 for row in rows:
  p=source_for(row);assert p.is_file()and sha(p)==row['sha256']and p.stat().st_size==row['bytes'],row['module']
  imports=[]
  for line in p.read_text().splitlines():
   m=re.match(r'^import\s+(.+)$',line)
   if m:imports.extend(m[1].split('--',1)[0].split())
  assert imports==row['imports'];assert set(imports)-{'Lean'}<=seen;seen.add(row['module'])
 build=Path(args.build_dir);build=build if build.is_absolute()else ROOT/build;build.mkdir(parents=True,exist_ok=False);(build/'logs').mkdir();(build/'receipts').mkdir()
 service=None
 if args.slot_service:
  spec=importlib.util.spec_from_file_location('existing_lean_slot_service',Path(args.slot_service).resolve());service=importlib.util.module_from_spec(spec);spec.loader.exec_module(service)
 env=dict(os.environ);env['LEAN_PATH']=str(build);env['LEAN_EXTRA_PATHS']='';env.pop('LEAN_SYSROOT',None);env['MIMALLOC_ARENA_RESERVE']='64MiB'
 outcome={'started_utc':now(),'manifest_sha256':sha(ROOT/'MANIFEST.json'),'dependencies_manifest_sha256':sha(ROOT/'DEPENDENCIES.json'),'dependency_commits':expected_commits,'lean_version':version,'lean_binary_sha256':sha(lean),'external_library_paths':[],'source_search_path':str(build),'status':'RUNNING','receipts':[]};(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n')
 for row in rows:
  requested=time.monotonic();slot=None;handle=None;handles=[]
  if service:slot,handle,handles=service.acquire('isolated_automatic_width_count_package:'+row['module'])
  queue=time.monotonic()-requested;started=time.monotonic();start_utc=now();source=source_for(row);output_path=build/(row['module']+'.olean');log=build/'logs'/(row['module']+'.log');peak=0;samples=0;timed_out=False
  try:
   assert sha(source)==row['sha256'];cmd=[str(lean),'-s','65536','-j','1','-o',str(output_path),source.name]
   proc=subprocess.Popen(cmd,cwd=source.parent,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,preexec_fn=limits)
   while True:
    try:
     text=Path(f'/proc/{proc.pid}/status').read_text();m=re.search(r'^VmPeak:\s+(\d+)',text,re.M);peak=max(peak,int(m[1])*1024 if m else 0);samples+=1
    except OSError:pass
    remaining=60-(time.monotonic()-started)
    if remaining<=0:
     timed_out=True;os.killpg(proc.pid,signal.SIGKILL);data,_=proc.communicate();break
    try:data,_=proc.communicate(timeout=min(.1,remaining));break
    except subprocess.TimeoutExpired:pass
   elapsed=time.monotonic()-started;log.write_bytes(data);text=data.decode(errors='replace');forbidden=('sorryAx'in text or "declaration uses 'sorry'"in text)
   passed=proc.returncode==0 and not timed_out and not forbidden and output_path.is_file()and sha(source)==row['sha256'];review=passed and(elapsed>40 or peak>int(3.5*1024**3))
   rec={'module':row['module'],'source_sha256':row['sha256'],'status':'PASS'if passed else'FAIL','review_stop':review,'exit_code':proc.returncode,'timed_out':timed_out,'started_utc':start_utc,'finished_utc':now(),'compile_seconds':elapsed,'queue_seconds':queue,'peak_vm_bytes':peak,'samples':samples,'slot':slot,'log_sha256':sha(log),'object_sha256':sha(output_path)if passed else None,'imports':row['imports'],'axiom_output':[s for s in text.splitlines()if'depends on axioms:'in s or'does not depend on any axioms'in s]};rp=build/'receipts'/(row['module']+'.json');rp.write_text(json.dumps(rec,indent=2)+'\n');outcome['receipts'].append({'module':row['module'],'receipt_sha256':sha(rp),'status':rec['status']});outcome['status']='REVIEW_STOP'if review else('RUNNING'if passed else'FAIL');(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n');print(json.dumps(rec),flush=True)
   if not passed or review:return 2
  finally:
   if handle:fcntl.flock(handle,fcntl.LOCK_UN)
   for h in handles:h.close()
 outcome['status']='PASS';outcome['finished_utc']=now();outcome['modules']=len(outcome['receipts']);(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n');print('PASS exact isolated9-module automatic-width closure',flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
