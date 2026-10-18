#!/usr/bin/env python3
"""Offline historical PR588 native moment replay: two exact PR585 outputs retained, seven fresh sources checked."""
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

def verify_external(lean,mathlib,base_path,reused_path):
 reference_path=ROOT/'EXTERNAL_OBJECTS_REFERENCE.json'
 assert sha(reference_path)=='8d486d9515284f369722b702d17b0ab390d246bd49b88ddf67aa3758e746bb1f'
 ref=json.loads(reference_path.read_text())
 for p,info in [(base_path,ref['base']),(reused_path,ref['reused_extension']), (ROOT/ref['subset_file'],{'sha256':ref['subset_sha256'],'bytes':ref['subset_bytes']}),(ROOT/ref['extension_file'],{'sha256':ref['extension_sha256'],'bytes':ref['extension_bytes']})]:
  assert p.is_file() and sha(p)==info['sha256'] and p.stat().st_size==info['bytes']
 base=json.loads(base_path.read_text());reused=json.loads(reused_path.read_text());subset=json.loads((ROOT/ref['subset_file']).read_text());extension=json.loads((ROOT/ref['extension_file']).read_text())
 assert len(base['modules'])==1366 and len(reused['modules'])==1794 and len(extension['modules'])==158
 assert subset['reference_sha256']==ref['reused_extension']['sha256'] and subset['reference_modules']==1794
 assert subset['selected_module_count']==len(subset['modules'])==1736 and len(set(subset['modules']))==1736
 assert subset['excluded_module_count']==len(subset['excluded_modules'])==58 and len(set(subset['excluded_modules']))==58
 for key in ['lean_version','lean_binary_sha256','mathlib_commit','library_paths_relative_to_mathlib']:assert base[key]==reused[key]==extension[key]
 assert sha(lean)==base['lean_binary_sha256'] and base['lean_version']=='4.21.0'
 assert base['mathlib_commit']=='308445d7985027f538e281e18df29ca16ede2ba3'
 rm={r['module']:r for r in reused['modules']};assert len(rm)==1794
 assert set(subset['modules']).isdisjoint(subset['excluded_modules']) and set(subset['modules'])|set(subset['excluded_modules'])==set(rm)
 rows=base['modules']+[rm[n] for n in subset['modules']]+extension['modules'];names={r['module'] for r in rows}
 assert len(rows)==len(names)==ref['union_modules']==extension['union_module_count']==3260
 assert extension['referenced_module_count']==3102 and extension['extension_module_count']==158
 roots={'lean':lean.parent.parent,'mathlib':mathlib};paths=[mathlib/p for p in base['library_paths_relative_to_mathlib']]
 assert len(paths)==8 and all(p.is_dir() for p in paths)
 for row in rows:
  assert row['root'] in roots
  for field in ('source_path','object_path'):assert not Path(row[field]).is_absolute() and '..' not in Path(row[field]).parts
  source=roots[row['root']]/row['source_path'];obj=roots[row['root']]/row['object_path']
  assert source.is_file() and obj.is_file() and sha(source)==row['source_sha256'] and sha(obj)==row['object_sha256'],row['module']
  assert obj.stat().st_size==row['object_bytes'] and set(row['imports'])<=names,row['module']
  rel=Path(*row['module'].split('.')).with_suffix('.olean');first=next((p/rel for p in paths+[roots['lean']/'lib/lean'] if(p/rel).is_file()),None)
  assert first and first.resolve()==obj.resolve(),row['module']
 return dict(base,modules=rows),paths,names

def verify_prefix(prefix, package, deps, rows, lean, observed):
 assert sha(package/'MANIFEST.json')=='dd3880ce395e899be44fe758d9dbd6bc989dfc0b25e07ad14a2cc9613ab8ebc3'
 pm=json.loads((package/'MANIFEST.json').read_text());pr={r['module']:r for r in pm['compile_order']}
 rp=prefix/'REPLAY_RESULT.json';result=json.loads(rp.read_text())
 assert result['status']=='PASS' and result['modules']==5 and len(result['receipts'])==5
 assert result['manifest_sha256']=='dd3880ce395e899be44fe758d9dbd6bc989dfc0b25e07ad14a2cc9613ab8ebc3' and result['lean_binary_sha256']==sha(lean)
 if observed:assert sha(rp)=='f47cfea8e63f20c62d6bb84d23961d20d2279fa560dfe8a9e1b28e1abdf3ef6e'
 receipts={r['module']:r for r in result['receipts']};assert len(receipts)==5
 assert deps['pr585']['commit']=='809915a264d4fbe1f7597cc13da3610dc4d52f15'
 by_name={r['module']:r for r in rows if r['origin']=='pr585'}
 assert len(deps['pr585']['sources'])==len(by_name)==2
 checked=[]
 for dep in deps['pr585']['sources']:
  module=dep['module'];row=by_name[module];prior=pr[module]
  assert prior['sha256']==row['sha256']==dep['sha256'] and prior['bytes']==row['bytes']
  assert prior['imports']==row['imports'] and prior['expected_probes']==row['expected_probes']
  assert sha(package/prior['file'])==row['sha256']
  source=prefix/'sources'/row['file'];obj=prefix/'objects'/(module+'.olean');receipt=prefix/'receipts'/(module+'.json');log=prefix/'logs'/(module+'.log')
  assert sha(source)==row['sha256'] and source.stat().st_size==row['bytes'] and sha(obj)==dep['public_object_sha256']
  rec=json.loads(receipt.read_text());raw=log.read_bytes()
  assert receipts[module]['status']=='PASS' and receipts[module]['receipt_sha256']==sha(receipt)
  assert rec['module']==module and rec['status']=='PASS' and rec['review_stop'] is False and rec['exit_code']==0 and rec['timed_out'] is False
  assert rec['compile_seconds']<=40 and rec['peak_vm_bytes']<=int(3.5*1024**3)
  assert rec['source_sha256']==row['sha256'] and rec['object_sha256']==dep['public_object_sha256'] and rec['log_sha256']==sha(log)
  assert rec['imports']==row['imports'] and rec['expected_probes_match'] is True
  assert complete_probes(raw.decode('utf-8'))==row['expected_probes']==rec['complete_axiom_probes']
  assert b'sorryAx' not in raw and b"declaration uses 'sorry'" not in raw
  assert sha(log)==dep['public_log_sha256']
  if observed:assert sha(receipt)==dep['public_receipt_sha256']
  checked.append({'module':module,'source_sha256':row['sha256'],'object_sha256':dep['public_object_sha256'],'receipt_sha256':sha(receipt),'log_sha256':sha(log)})
 return checked

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--lean',required=True);ap.add_argument('--mathlib-root',required=True);ap.add_argument('--base-runtime-manifest',required=True);ap.add_argument('--reused-runtime-extension',required=True);ap.add_argument('--build-dir',default='.build');ap.add_argument('--slot-service',help='Optional existing FIFO slot service exposing acquire(); does not change Lean inputs.');ap.add_argument('--lean-sha256');ap.add_argument('--prefix-build',required=True);ap.add_argument('--prefix-package',required=True);ap.add_argument('--require-observed-prefix',action='store_true',help='Also require the exact recorded local prefix result, receipts and raw logs.');ap.add_argument('--guard-only',action='store_true',help='Verify all inputs and absence of the new build without creating it or compiling.');args=ap.parse_args();assert __debug__,'Run Python without -O'
 assert Path('/proc/self/status').is_file(),'Linux /proc is required for the stated memory review'
 prefix=Path(args.prefix_build).resolve();package=Path(args.prefix_package).resolve();roots={'included':ROOT,'pr585':prefix/'sources'}
 assert all(p.is_dir() for p in roots.values())
 source_for=lambda row:roots[row['origin']]/row['file']
 def source_data(row):
  data=source_for(row).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'] and len(data)==row['bytes'],row['module'];return data
 lean=Path(args.lean).resolve();assert lean.is_file()
 if args.lean_sha256:assert sha(lean)==args.lean_sha256
 version=subprocess.check_output([str(lean),'--version'],text=True).strip();assert re.search(r'\b4\.21\.0\b',version),version
 external_manifest=Path(args.base_runtime_manifest).resolve();reused_manifest=Path(args.reused_runtime_extension).resolve();mathlib=Path(args.mathlib_root).resolve()
 external,external_paths,external_names=verify_external(lean,mathlib,external_manifest,reused_manifest)
 manifest=json.loads((ROOT/'MANIFEST.json').read_text());rows=manifest['compile_order'];names={r['module']for r in rows};seen=set()
 assert not names & external_names
 assert len(rows)==len(names)==9 and manifest['source_bytes']==235135
 assert sum(r['origin']=='included' for r in rows)==7 and sum(r['origin']=='pr585' for r in rows)==2
 assert sum(r['bytes'] for r in rows)==235135 and sum(r['bytes'] for r in rows if r['origin']=='included')==125586
 assert all(re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',r['module']) and r['file']==r['module']+'.lean' for r in rows)
 assert sha(ROOT/'MANIFEST.json')=='44f1d5df2ef983d15a88b16a5ae40958e21d7c89911ae308704ec97bf3028de5'
 assert sha(ROOT/'DEPENDENCIES.json')=='3007c0e4e8add3e04f0336aeb035e552a4dc07cfd69724211bd1b830e00bfa54'
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
 assert sum(len(r['expected_probes']) for r in rows)==31
 assert sum(len(r['expected_probes']) for r in rows if r['origin']=='included')==20
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
 # Freeze every predecessor artifact, not only the two imported ones. Hold shared locks
 # on inputs throughout the run; rehash after the FIFO and after each compiler.
 protected_paths=set(p for p in ROOT.iterdir() if p.is_file())|{package/'MANIFEST.json',external_manifest,reused_manifest,prefix/'REPLAY_RESULT.json'}
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
  verify_external(lean,mathlib,external_manifest,reused_manifest)
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
  print(json.dumps({'status':'GUARD_PASS','retained':2,'fresh':7,'external_pairs':3260,'new_probes':20,'prefix_result_sha256':sha(prefix/'REPLAY_RESULT.json'),'completed_utc':now()}));return 0
 build.mkdir(parents=True,exist_ok=False);(build/'logs').mkdir();(build/'receipts').mkdir();(build/'sources').mkdir();(build/'objects').mkdir()
 build=build.resolve()
 for row in rows:
  target=build/'sources'/(row['module']+'.lean');target.write_bytes(source_data(row));assert sha(target)==row['sha256']
 for module in names:
  assert not any((p/(module+'.olean')).exists() for p in external_paths),module
 accepted_objects={}
 for dep in deps['pr585']['sources']:
  target=build/'objects'/(dep['module']+'.olean');shutil.copyfile(prefix/'objects'/(dep['module']+'.olean'),target);assert sha(target)==dep['public_object_sha256'];accepted_objects[dep['module']]=sha(target)
 guard(True,accepted_objects)
 service=None
 if args.slot_service:
  spec=importlib.util.spec_from_file_location('existing_lean_slot_service',Path(args.slot_service).resolve());service=importlib.util.module_from_spec(spec);spec.loader.exec_module(service)
 env=dict(os.environ);env['LEAN_PATH']=os.pathsep.join([str(build/'objects')]+[str(p) for p in external_paths]);env['LEAN_EXTRA_PATHS']='';env.pop('LEAN_SYSROOT',None);env['MIMALLOC_ARENA_RESERVE']='64MiB'
 outcome={'started_utc':now(),'manifest_sha256':sha(ROOT/'MANIFEST.json'),'dependencies_manifest_sha256':sha(external_manifest),'dependency_commits':expected_commits,'lean_version':version,'lean_binary_sha256':sha(lean),'external_manifest_sha256':sha(external_manifest),'external_library_paths':[str(p) for p in external_paths],'source_search_path':env['LEAN_PATH'],'status':'RUNNING','retained_modules':prefix_checked,'retained_count':2,'fresh_count':7,'new_axiom_probes':20,'prefix_result_sha256':sha(prefix/'REPLAY_RESULT.json'),'exact_observed_prefix':args.require_observed_prefix,'receipts':[]};(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n')
 for row in [r for r in rows if r['origin']=='included']:
  requested=time.monotonic();slot=None;handle=None;handles=[]
  if service:slot,handle,handles=service.acquire('isolated_historical588_native_retained_prefix:'+row['module'])
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
   post_guard_seconds=time.monotonic()-post_started;review=passed and(elapsed>40 or peak>int(3.5*1024**3))
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
 outcome['status']='PASS';outcome['finished_utc']=now();outcome['modules']=9;outcome['fresh_modules']=len(outcome['receipts']);(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n');print('PASS exact historical PR588 native moment: two retained, seven fresh, 20 new probes',flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
