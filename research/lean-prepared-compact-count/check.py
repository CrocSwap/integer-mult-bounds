#!/usr/bin/env python3
"""Offline eighteen-source prepared compact counting replay using sixteen pinned PR sources and an exact existing Mathlib cache."""
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

def verify_external(lean,mathlib,external_manifest):
 assert sha(external_manifest)=='2e29aae6cd405281d34d718395ab98f4adab083c64b34341fa7c8a879e6a1dd1'
 manifest=json.loads(external_manifest.read_text())
 assert sha(lean)==manifest['lean_binary_sha256']
 assert manifest['mathlib_commit']=='308445d7985027f538e281e18df29ca16ede2ba3'
 roots={'lean':lean.parent.parent,'mathlib':mathlib}
 paths=[mathlib/p for p in manifest['library_paths_relative_to_mathlib']]
 assert len(paths)==8 and len(manifest['modules'])==1366
 assert all(p.is_dir() for p in paths)
 names={r['module'] for r in manifest['modules']};assert len(names)==1366
 for row in manifest['modules']:
  source=roots[row['root']]/row['source_path'];obj=roots[row['root']]/row['object_path']
  assert source.is_file() and obj.is_file() and sha(source)==row['source_sha256'] and sha(obj)==row['object_sha256'],row['module']
  assert obj.stat().st_size==row['object_bytes'] and set(row['imports'])<=names,row['module']
  relative=Path(*row['module'].split('.')).with_suffix('.olean')
  resolved=next((p/relative for p in paths+[roots['lean']/'lib/lean'] if (p/relative).is_file()),None)
  assert resolved is not None and resolved.resolve()==obj.resolve(),row['module']
 return manifest,paths,names

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--lean',required=True);ap.add_argument('--input-foundation-root',required=True,help='Exact PR488 input-preparation package.');ap.add_argument('--dispatcher-foundation-root',required=True,help='Exact PR511 count-dispatcher package.');ap.add_argument('--automatic-width-root',required=True,help='Exact PR519 automatic-width package.');ap.add_argument('--amortization-root',required=True,help='Exact PR526 receipt-amortization package.');ap.add_argument('--prepared-input-root',required=True,help='Exact PR530 prepared-input package, including its pinned external runtime manifest.');ap.add_argument('--compact-copy-root',required=True,help='Exact published compact-copy package.');ap.add_argument('--mathlib-root',required=True,help='Existing exact Mathlib4.21 cache tree; no downloads.');ap.add_argument('--build-dir',default='.build');ap.add_argument('--slot-service',help='Optional existing FIFO slot service exposing acquire(); does not change Lean inputs.');ap.add_argument('--lean-sha256');args=ap.parse_args()
 assert Path('/proc/self/status').is_file(),'Linux /proc is required for the stated memory review'
 roots={'package':ROOT,'pr488':Path(args.input_foundation_root).resolve(),'pr511':Path(args.dispatcher_foundation_root).resolve(),'pr519':Path(args.automatic_width_root).resolve(),'pr526':Path(args.amortization_root).resolve(),'pr530':Path(args.prepared_input_root).resolve(),'pr565':Path(args.compact_copy_root).resolve()}
 assert all(p.is_dir() for p in roots.values())
 source_for=lambda row:roots[row['origin']]/row['file']
 lean=Path(args.lean).resolve();assert lean.is_file()
 if args.lean_sha256:assert sha(lean)==args.lean_sha256
 version=subprocess.check_output([str(lean),'--version'],text=True).strip();assert re.search(r'\b4\.21\.0\b',version),version
 external_reference=json.loads((ROOT/'EXTERNAL_OBJECTS_REFERENCE.json').read_text());external_manifest=roots['pr530']/'EXTERNAL_OBJECTS.json'
 assert external_reference=={'origin':'pr530','file':'EXTERNAL_OBJECTS.json','commit':'5a21a91d083fc73a1f48bf22d89da768dcf2696a','sha256':'2e29aae6cd405281d34d718395ab98f4adab083c64b34341fa7c8a879e6a1dd1','bytes':797008,'modules':1366,'meaning':'Exact unchanged source/object runtime inventory supplied by the required PR530 worktree; the checker verifies its hash and every row before compilation.'}
 assert external_manifest.stat().st_size==external_reference['bytes']
 external,external_paths,external_names=verify_external(lean,Path(args.mathlib_root).resolve(),external_manifest)
 manifest=json.loads((ROOT/'MANIFEST.json').read_text());rows=manifest['compile_order'];names={r['module']for r in rows};seen=set()
 assert not names & external_names
 assert len(rows)==18 and manifest['source_bytes']==198018
 assert sum(r['origin']=='pr488' for r in rows)==4 and sum(r['origin']=='pr511' for r in rows)==4 and sum(r['origin']=='pr519' for r in rows)==3 and sum(r['origin']=='pr526' for r in rows)==3 and sum(r['origin']=='pr530' for r in rows)==1 and sum(r['origin']=='pr565' for r in rows)==1 and sum(r['origin']=='package' for r in rows)==2
 dependencies=json.loads((ROOT/'DEPENDENCIES.json').read_text())
 expected_commits={'pr488':'edd3102b415df5b9d6f633ac0a4dedcf69c58525','pr511':'79f7c03c7f820ab89955b75ef239cbaccc627e6e','pr519':'ffd3c48a80ba8b579dc300e785e387fe8acddfef','pr526':'e7d6dc6e474f8690d72ef8b841290948028f66f3','pr530':'5a21a91d083fc73a1f48bf22d89da768dcf2696a','pr565':'b5766e15ab1c9f5c86e994aa7754a7750c6af76c'}
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
  assert imports==row['imports'];assert set(imports)<=seen|external_names;seen.add(row['module'])
 assert sum(len(r['expected_probes']) for r in rows)==133
 build=Path(args.build_dir);build=build if build.is_absolute()else ROOT/build;build.mkdir(parents=True,exist_ok=False);(build/'logs').mkdir();(build/'receipts').mkdir();(build/'sources').mkdir();(build/'objects').mkdir()
 build=build.resolve()
 for row in rows:
  target=build/'sources'/(row['module']+'.lean');shutil.copyfile(source_for(row),target);assert sha(target)==row['sha256']
 for module in names:
  assert not any((p/(module+'.olean')).exists() for p in external_paths),module
 service=None
 if args.slot_service:
  spec=importlib.util.spec_from_file_location('existing_lean_slot_service',Path(args.slot_service).resolve());service=importlib.util.module_from_spec(spec);spec.loader.exec_module(service)
 env=dict(os.environ);env['LEAN_PATH']=os.pathsep.join([str(build/'objects')]+[str(p) for p in external_paths]);env['LEAN_EXTRA_PATHS']='';env.pop('LEAN_SYSROOT',None);env['MIMALLOC_ARENA_RESERVE']='64MiB'
 outcome={'started_utc':now(),'manifest_sha256':sha(ROOT/'MANIFEST.json'),'dependencies_manifest_sha256':sha(ROOT/'DEPENDENCIES.json'),'dependency_commits':expected_commits,'lean_version':version,'lean_binary_sha256':sha(lean),'external_manifest_sha256':sha(external_manifest),'external_manifest_origin':'pr530','external_reference_sha256':sha(ROOT/'EXTERNAL_OBJECTS_REFERENCE.json'),'external_library_paths':[str(p) for p in external_paths],'source_search_path':env['LEAN_PATH'],'status':'RUNNING','receipts':[]};(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n')
 for row in rows:
  requested=time.monotonic();slot=None;handle=None;handles=[]
  if service:slot,handle,handles=service.acquire('isolated_prepared_compact_count_package:'+row['module'])
  queue=time.monotonic()-requested;started=time.monotonic();start_utc=now();source=build/'sources'/(row['module']+'.lean');output_path=build/'objects'/(row['module']+'.olean');log=build/'logs'/(row['module']+'.log');peak=0;peak_rss=0;peak_threads=0;samples=0;timed_out=False
  try:
   assert sha(source)==row['sha256'];cmd=[str(lean),'-s','65536','-j','1','-o',str(output_path),source.name]
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
   elapsed=time.monotonic()-started;log.write_bytes(data);text=data.decode(errors='replace');forbidden=('sorryAx'in text or "declaration uses 'sorry'"in text)
   probes=complete_probes(text);probe_match=probes==row['expected_probes'] and all(set(p['axioms'])<={'propext','Classical.choice','Quot.sound'} for p in probes)
   passed=proc.returncode==0 and not timed_out and not forbidden and probe_match and output_path.is_file()and sha(source)==row['sha256']and sha(source_for(row))==row['sha256'];review=passed and(elapsed>40 or peak>int(3.5*1024**3))
   rec={'module':row['module'],'source_sha256':row['sha256'],'status':'PASS'if passed else'FAIL','review_stop':review,'exit_code':proc.returncode,'timed_out':timed_out,'started_utc':start_utc,'finished_utc':now(),'compile_seconds':elapsed,'queue_seconds':queue,'peak_vm_bytes':peak,'peak_rss_bytes':peak_rss,'peak_threads':peak_threads,'samples':samples,'complete_axiom_probes':probes,'expected_probes_match':probe_match,'slot':slot,'log_sha256':sha(log),'object_sha256':sha(output_path)if passed else None,'imports':row['imports'],'axiom_output':[s for s in text.splitlines()if'depends on axioms:'in s or'does not depend on any axioms'in s]};rp=build/'receipts'/(row['module']+'.json');rp.write_text(json.dumps(rec,indent=2)+'\n');outcome['receipts'].append({'module':row['module'],'receipt_sha256':sha(rp),'status':rec['status']});outcome['status']='REVIEW_STOP'if review else('RUNNING'if passed else'FAIL');(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n');print(json.dumps(rec),flush=True)
   if not passed or review:return 2
  finally:
   if handle:fcntl.flock(handle,fcntl.LOCK_UN)
   for h in handles:h.close()
 outcome['status']='PASS';outcome['finished_utc']=now();outcome['modules']=len(outcome['receipts']);(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n');print('PASS exact isolated18-module prepared-compact-count closure',flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
