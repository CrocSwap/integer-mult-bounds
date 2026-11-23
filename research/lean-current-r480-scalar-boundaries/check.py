#!/usr/bin/env python3
"""Offline current R480 replay: six exact PR590 outputs retained, six fresh sources checked."""
import argparse,fcntl,hashlib,importlib.util,json,os,re,resource,signal,subprocess,time,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
 resource.setrlimit(resource.RLIMIT_CPU,(60,62));os.setsid()
def complete_probes(text):
 result=[]
 pattern=r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])"
 for m in re.finditer(pattern,text,re.S):
  result.append({'declaration':m[1],'axioms':[] if m[2] is None else [a.strip() for a in m[2].split(',') if a.strip()]})
 return result

def verify_external(lean,external_manifest):
 assert sha(external_manifest)=='2c27354193fc7b11079b61116ab8e9c80485903845bda48ddf3c66057fed2cb1'
 manifest=json.loads(external_manifest.read_text());rows=manifest['ordered_modules']
 assert manifest['lean_toolchain']=='leanprover/lean4:v4.21.0' and manifest['distribution']=='lean-4.21.0-linux'
 assert manifest['root_modules']==['Init'] and manifest['module_count']==len(rows)==317
 assert manifest['edge_count']==sum(len(row['imports']) for row in rows)==1077
 assert manifest['source_bytes']==sum(row['source']['bytes'] for row in rows)==5050982
 assert manifest['object_bytes']==sum(row['object']['bytes'] for row in rows)==84918424
 root=lean.parent.parent;binary=manifest['binary']
 assert (root/binary['file']).resolve()==lean and sha(lean)==binary['sha256'] and lean.stat().st_size==binary['bytes']
 names={row['module'] for row in rows};assert len(names)==317;seen=set()
 for row in rows:
  assert row['module'] not in seen and set(row['imports'])<=seen;seen.add(row['module'])
  for kind,suffix,prefix in [('source','.lean','src/lean'),('object','.olean','lib/lean')]:
   relative=Path(prefix)/Path(*row['module'].split('.')).with_suffix(suffix)
   assert Path(row[kind]['file'])==relative
   path=root/relative;assert path.is_file() and sha(path)==row[kind]['sha256'] and path.stat().st_size==row[kind]['bytes'],row['module']
  # No external library paths are added; the official core object is the default match.
  object_path=root/row['object']['file'];resolved=root/'lib/lean'/Path(*row['module'].split('.')).with_suffix('.olean')
  assert resolved.resolve()==object_path.resolve(),row['module']
 return dict(manifest,modules=rows),[],names

def normalize_prefix_log(module, data):
 # Only the three already recorded warning source paths may differ.
 if module != 'BitXorTargetTranslation':return data
 text=data.decode('utf-8')
 for line in (96,110,127):
  pattern=rf'^(?:[^\r\n]*[/\\])?BitXorTargetTranslation\.lean:{line}:0: warning:'
  text,n=re.subn(pattern,f'BitXorTargetTranslation.lean:{line}:0: warning:',text,flags=re.M)
  assert n==1,'Expected exactly one of each recorded XOR warning location'
 return text.encode('utf-8')

def verify_prefix(prefix, package, deps, rows, lean, observed):
 assert sha(package/'MANIFEST.json')==deps['package_manifest_sha256']
 pm=json.loads((package/'MANIFEST.json').read_text());pr={r['module']:r for r in pm['compile_order']}
 assert sha(package/'OFFICIAL_CORE_MANIFEST.json')==sha(ROOT/'OFFICIAL_CORE_MANIFEST.json')
 rp=prefix/'REPLAY_RESULT.json';result=json.loads(rp.read_text())
 assert result['status']=='PASS' and result['modules']==8 and len(result['receipts'])==8
 assert result['manifest_sha256']==deps['package_manifest_sha256']
 assert result['lean_binary_sha256']==sha(lean)
 assert result['external_manifest_sha256']==sha(ROOT/'OFFICIAL_CORE_MANIFEST.json')
 assert result['external_library_paths']==[]
 if observed:assert sha(rp)==deps['observed_prefix_result_sha256']
 receipts={r['module']:r for r in result['receipts']};assert len(receipts)==8
 by_name={r['module']:r for r in rows if r['origin']=='PR590'}
 assert len(deps['required_modules'])==len(by_name)==6
 checked=[]
 for dep in deps['required_modules']:
  module=dep['module'];row=by_name[module];prior=pr[module]
  assert prior['sha256']==row['sha256'] and prior['bytes']==row['bytes']
  assert prior['imports']==row['imports'] and prior['expected_probes']==row['expected_probes']
  assert sha(package/prior['file'])==row['sha256']
  for kind,suffix,folder in [('source','.lean','sources'),('object','.olean','objects'),('observed_receipt','.json','receipts'),('observed_log','.log','logs')]:
   assert dep[kind]['relative_path']==f'{folder}/{module}{suffix}'
  for kind in ('source','object'):
   p=prefix/dep[kind]['relative_path'];assert p.is_file() and sha(p)==dep[kind]['sha256'] and p.stat().st_size==dep[kind]['bytes']
  receipt=prefix/dep['observed_receipt']['relative_path'];log=prefix/dep['observed_log']['relative_path'];rec=json.loads(receipt.read_text());raw=log.read_bytes()
  assert receipts[module]['status']=='PASS' and receipts[module]['receipt_sha256']==sha(receipt)
  assert rec['module']==module and rec['status']=='PASS' and rec['review_stop'] is False and rec['exit_code']==0 and rec['timed_out'] is False
  assert rec['compile_seconds']<=45 and rec['peak_vm_bytes']<=int(3.5*1024**3)
  assert rec['source_sha256']==row['sha256'] and rec['object_sha256']==dep['object']['sha256'] and rec['log_sha256']==sha(log)
  assert rec['imports']==row['imports'] and rec['expected_probes_match'] is True
  assert complete_probes(raw.decode('utf-8'))==row['expected_probes']==rec['complete_axiom_probes']
  assert b'sorryAx' not in raw and b"declaration uses 'sorry'" not in raw
  assert hashlib.sha256(normalize_prefix_log(module,raw)).hexdigest()==dep['observed_log']['sha256']
  if observed:assert sha(receipt)==dep['observed_receipt']['sha256'] and sha(log)==dep['observed_log']['sha256']
  checked.append({'module':module,'source_sha256':row['sha256'],'object_sha256':dep['object']['sha256'],'receipt_sha256':sha(receipt),'log_sha256':sha(log)})
 return checked

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--lean',required=True);ap.add_argument('--build-dir',default='.build');ap.add_argument('--slot-service',help='Optional existing FIFO slot service exposing acquire(); does not change Lean inputs.');ap.add_argument('--lean-sha256');ap.add_argument('--prefix-build',required=True);ap.add_argument('--prefix-package',required=True);ap.add_argument('--require-observed-prefix',action='store_true',help='Also require the exact recorded local prefix result, receipts and raw logs.');ap.add_argument('--guard-only',action='store_true',help='Verify all inputs and absence of the new build without creating it or compiling.');args=ap.parse_args();assert __debug__,'Run Python without -O'
 assert Path('/proc/self/status').is_file(),'Linux /proc is required for the stated memory review'
 prefix=Path(args.prefix_build).resolve();package=Path(args.prefix_package).resolve();roots={'included':ROOT,'PR590':prefix/'sources'}
 assert all(p.is_dir() for p in roots.values())
 source_for=lambda row:roots[row['origin']]/row['file']
 def source_data(row):
  data=source_for(row).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'] and len(data)==row['bytes'],row['module'];return data
 lean=Path(args.lean).resolve();assert lean.is_file()
 if args.lean_sha256:assert sha(lean)==args.lean_sha256
 version=subprocess.check_output([str(lean),'--version'],text=True).strip();assert re.search(r'\b4\.21\.0\b',version),version
 external_manifest=ROOT/'OFFICIAL_CORE_MANIFEST.json'
 external,external_paths,external_names=verify_external(lean,external_manifest)
 manifest=json.loads((ROOT/'MANIFEST.json').read_text());rows=manifest['compile_order'];names={r['module']for r in rows};seen=set()
 assert not names & external_names
 assert len(rows)==len(names)==12 and manifest['source_bytes']==135091
 assert sum(r['origin']=='included' for r in rows)==6 and sum(r['origin']=='PR590' for r in rows)==6
 assert sum(r['bytes'] for r in rows)==135091 and sum(r['bytes'] for r in rows if r['origin']=='included')==37690
 assert all(re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',r['module']) and r['file']==r['module']+'.lean' for r in rows)
 assert sha(ROOT/'MANIFEST.json')=='de79146d6171093e603e313ca60248f420de743d8433bc9fc9ce296e20e72b6c'
 assert sha(ROOT/'DEPENDENCIES.json')=='104cbdf1faa5d1586e181f690f4402f1244a73cd6f33250d53ac07878024d2e3'
 deps=json.loads((ROOT/'DEPENDENCIES.json').read_text())
 prefix_checked=verify_prefix(prefix,package,deps,rows,lean,args.require_observed_prefix)
 expected_commits={}  # Sources/objects are content-bound; no Git executable or supplier execution is needed.
 for row in rows:
  data=source_data(row)
  imports=[]
  for line in data.decode().splitlines():
   m=re.match(r'^import\s+(.+)$',line)
   if m:imports.extend(m[1].split('--',1)[0].split())
  assert imports==row['imports'];assert set(imports)<=seen|external_names;seen.add(row['module'])
 assert sum(len(r['expected_probes']) for r in rows)==91
 assert sum(len(r['expected_probes']) for r in rows if r['origin']=='included')==62
 reachable=set();external_rows={r['module']:r for r in external['modules']}
 def visit(name):
  if name in reachable:return
  assert name in external_rows;reachable.add(name)
  for child in external_rows[name]['imports']:visit(child)
 for row in rows:
  for imp in row['imports']:
   if imp in external_names:visit(imp)
 assert reachable==external_names,'Exact external subset must equal the transitive import closure'
 build=Path(args.build_dir);build=(build if build.is_absolute()else ROOT/build).resolve();assert not build.exists(),'Fresh output directory required'
 # Freeze every predecessor artifact, not only the six imported ones. Hold shared locks
 # on inputs throughout the run; rehash after the FIFO and after each compiler.
 protected_paths=set(p for p in ROOT.iterdir() if p.is_file())|{package/'MANIFEST.json',package/'OFFICIAL_CORE_MANIFEST.json',prefix/'REPLAY_RESULT.json'}
 for folder in ('sources','objects','logs','receipts'):
  protected_paths.update(p for p in (prefix/folder).iterdir() if p.is_file())
 protected_paths.update(package/pr['file'] for pr in json.loads((package/'MANIFEST.json').read_text())['compile_order'])
 protected={p:sha(p) for p in protected_paths};input_locks=[]
 for p in sorted(protected,key=str):
  h=p.open('rb');fcntl.flock(h,fcntl.LOCK_SH);input_locks.append(h)
 accepted_artifacts={}
 def guard(staged=False,objects=None):
  for p,digest in accepted_artifacts.items():assert sha(p)==digest,str(p)
  for p,digest in protected.items():assert sha(p)==digest,str(p)
  verify_external(lean,external_manifest)
  assert verify_prefix(prefix,package,deps,rows,lean,args.require_observed_prefix)==prefix_checked
  for row in rows:
   source_data(row)
   if staged:assert sha(build/'sources'/row['file'])==row['sha256']
  if staged:
   objects=objects or {}
   assert {p.name for p in (build/'objects').iterdir()}=={name+'.olean' for name in objects},'Unexpected object/shadowing'
   for module,digest in objects.items():assert sha(build/'objects'/(module+'.olean'))==digest,module
 guard()
 if args.guard_only:
  print(json.dumps({'status':'GUARD_PASS','retained':6,'fresh':6,'official_core':317,'new_probes':62,'prefix_result_sha256':sha(prefix/'REPLAY_RESULT.json'),'completed_utc':now()}));return 0
 build.mkdir(parents=True,exist_ok=False);(build/'logs').mkdir();(build/'receipts').mkdir();(build/'sources').mkdir();(build/'objects').mkdir()
 build=build.resolve()
 for row in rows:
  target=build/'sources'/(row['module']+'.lean');target.write_bytes(source_data(row));assert sha(target)==row['sha256']
 for module in names:
  assert not any((p/(module+'.olean')).exists() for p in external_paths),module
 accepted_objects={}
 for dep in deps['required_modules']:
  target=build/'objects'/(dep['module']+'.olean');shutil.copyfile(prefix/dep['object']['relative_path'],target);assert sha(target)==dep['object']['sha256'];accepted_objects[dep['module']]=sha(target)
 guard(True,accepted_objects)
 service=None
 if args.slot_service:
  spec=importlib.util.spec_from_file_location('existing_lean_slot_service',Path(args.slot_service).resolve());service=importlib.util.module_from_spec(spec);spec.loader.exec_module(service)
 env=dict(os.environ);env['LEAN_PATH']=os.pathsep.join([str(build/'objects')]+[str(p) for p in external_paths]);env['LEAN_EXTRA_PATHS']='';env.pop('LEAN_SYSROOT',None);env['MIMALLOC_ARENA_RESERVE']='64MiB'
 outcome={'started_utc':now(),'manifest_sha256':sha(ROOT/'MANIFEST.json'),'dependencies_manifest_sha256':sha(external_manifest),'dependency_commits':expected_commits,'lean_version':version,'lean_binary_sha256':sha(lean),'external_manifest_sha256':sha(external_manifest),'external_library_paths':[str(p) for p in external_paths],'source_search_path':env['LEAN_PATH'],'status':'RUNNING','retained_modules':prefix_checked,'retained_count':6,'fresh_count':6,'new_axiom_probes':62,'prefix_result_sha256':sha(prefix/'REPLAY_RESULT.json'),'exact_observed_prefix':args.require_observed_prefix,'receipts':[]};(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n')
 for row in [r for r in rows if r['origin']=='included']:
  requested=time.monotonic();slot=None;handle=None;handles=[]
  if service:slot,handle,handles=service.acquire('isolated_current_r480_retained_prefix:'+row['module'])
  queue=time.monotonic()-requested;guard_started=time.monotonic();source=build/'sources'/(row['module']+'.lean');output_path=build/'objects'/(row['module']+'.olean');log=build/'logs'/(row['module']+'.log');peak=0;peak_rss=0;peak_threads=0;samples=0;timed_out=False
  try:
   guard(True,accepted_objects);guard_seconds=time.monotonic()-guard_started;started=time.monotonic();start_utc=now();assert not output_path.exists();assert sha(source)==row['sha256'];cmd=[str(lean),'-s','65536','-j','1','-o',str(output_path),source.name]
   proc=subprocess.Popen(cmd,cwd=source.parent,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,preexec_fn=limits)
   while True:
    try:
     text=Path(f'/proc/{proc.pid}/status').read_text();m=re.search(r'^VmPeak:\s+(\d+)',text,re.M);peak=max(peak,int(m[1])*1024 if m else 0);m=re.search(r'^VmHWM:\s+(\d+)',text,re.M);peak_rss=max(peak_rss,int(m[1])*1024 if m else 0);m=re.search(r'^Threads:\s+(\d+)',text,re.M);peak_threads=max(peak_threads,int(m[1]) if m else 0);samples+=1
    except OSError:pass
    remaining=60-(time.monotonic()-started)
    if remaining<=0:
     timed_out=True;os.killpg(proc.pid,signal.SIGKILL);data,_=proc.communicate();break
    try:data,_=proc.communicate(timeout=min(.1,remaining));break
    except subprocess.TimeoutExpired:pass
   elapsed=time.monotonic()-started;compiler_finished_utc=now();log.write_bytes(data);text=data.decode(errors='replace');forbidden=('sorryAx'in text or "declaration uses 'sorry'"in text)
   probes=complete_probes(text);probe_match=probes==row['expected_probes'] and all(set(p['axioms'])<={'propext','Classical.choice','Quot.sound'} for p in probes)
   passed=proc.returncode==0 and not timed_out and not forbidden and probe_match and output_path.is_file()
   post_started=time.monotonic();after_objects=dict(accepted_objects)
   if output_path.is_file():after_objects[row['module']]=sha(output_path)
   verification_error=None
   try:guard(True,after_objects)
   except Exception as exc:verification_error=repr(exc);passed=False
   post_guard_seconds=time.monotonic()-post_started;review=passed and(elapsed>45 or peak>int(3.5*1024**3))
   rec={'module':row['module'],'source_sha256':row['sha256'],'status':'PASS'if passed else'FAIL','review_stop':review,'exit_code':proc.returncode,'timed_out':timed_out,'started_utc':start_utc,'finished_utc':compiler_finished_utc,'post_guard_finished_utc':now(),'preservation_error':verification_error,'compile_seconds':elapsed,'queue_seconds':queue,'post_fifo_guard_seconds':guard_seconds,'post_compile_guard_seconds':post_guard_seconds,'command':cmd,'lean_binary_sha256':sha(lean),'peak_vm_bytes':peak,'peak_rss_bytes':peak_rss,'peak_threads':peak_threads,'samples':samples,'complete_axiom_probes':probes,'expected_probes_match':probe_match,'slot':slot,'log_sha256':sha(log),'object_sha256':sha(output_path)if passed else None,'imports':row['imports'],'axiom_output':[s for s in text.splitlines()if'depends on axioms:'in s or'does not depend on any axioms'in s]};rp=build/'receipts'/(row['module']+'.json');rp.write_text(json.dumps(rec,indent=2)+'\n');outcome['receipts'].append({'module':row['module'],'receipt_sha256':sha(rp),'status':rec['status']});outcome['status']='REVIEW_STOP'if review else('RUNNING'if passed else'FAIL');(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n');print(json.dumps(rec),flush=True)
   if not passed or review:return 2
   accepted_objects[row['module']]=sha(output_path);accepted_artifacts[log]=sha(log);accepted_artifacts[rp]=sha(rp)
  finally:
   if handle:fcntl.flock(handle,fcntl.LOCK_UN)
   for h in handles:h.close()
 guard(True,accepted_objects)
 for row in rows:
  assert sha(build/'sources'/(row['module']+'.lean'))==row['sha256'] and hashlib.sha256(source_data(row)).hexdigest()==row['sha256']
 outcome['post_preservation_verified_utc']=now()
 outcome['status']='PASS';outcome['finished_utc']=now();outcome['modules']=12;outcome['fresh_modules']=len(outcome['receipts']);(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n');print('PASS exact current R480: six retained, six fresh, 62 new probes',flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
