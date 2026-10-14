#!/usr/bin/env python3
"""Offline five-source selected rational replay with a pinned exact subset of the PR528 runtime cache."""
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
 reference_path=ROOT/'EXTERNAL_OBJECTS_REFERENCE.json'
 assert sha(reference_path)=='9536e566ab941c4fde47240206c4e4ee8bfaa51e04e5b08df7e4def78f4fd11d'
 reference=json.loads(reference_path.read_text())
 assert reference['origin']=='pr528' and reference['commit']=='ba5e50abb80c6b854b127ccbe37d524e11c6db72'
 assert sha(external_manifest)==reference['sha256']=='68879b4390894c6eb6a5914afce3233de935e0202871386066a935825c86c339'
 assert external_manifest.stat().st_size==reference['bytes'] and reference['modules']==2213
 manifest=json.loads(external_manifest.read_text());sp=ROOT/reference['subset_file']
 assert sha(sp)==reference['subset_sha256']=='ffeb1811cb9aa803a66febe6f5f39a125c969876a5cf98f089e47b2b91cb0066' and sp.stat().st_size==reference['subset_bytes']
 subset=json.loads(sp.read_text());selected=subset['modules'];names=set(selected)
 assert len(selected)==len(names)==subset['module_count']==reference['subset_modules']==319 and reference['extension_modules']==0
 base={r['module']:r for r in manifest['modules']};assert len(base)==len(manifest['modules'])==2213 and names<=base.keys()
 selected_rows=[base[n] for n in selected]
 assert hashlib.sha256(json.dumps(selected_rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()==subset['selected_rows_sha256']=='19a68845aba2261dc895c8af95b16f49cd03d78209df1b2b867599fb9c7132f9'
 assert sum(r['object_bytes'] for r in selected_rows)==subset['external_object_bytes']==85527032
 assert sha(lean)==manifest['lean_binary_sha256'] and manifest['mathlib_commit']=='308445d7985027f538e281e18df29ca16ede2ba3'
 roots={'lean':lean.parent.parent,'mathlib':mathlib};paths=[mathlib/p for p in manifest['library_paths_relative_to_mathlib']]
 assert len(paths)==8 and all(p.is_dir() for p in paths)
 manifest=dict(manifest);manifest['modules']=selected_rows
 for row in manifest['modules']:
  source=roots[row['root']]/row['source_path'];obj=roots[row['root']]/row['object_path']
  assert source.is_file() and obj.is_file() and sha(source)==row['source_sha256'] and sha(obj)==row['object_sha256'],row['module']
  assert obj.stat().st_size==row['object_bytes'] and set(row['imports'])<=names,row['module']
  relative=Path(*row['module'].split('.')).with_suffix('.olean');resolved=next((p/relative for p in paths+[roots['lean']/'lib/lean'] if (p/relative).is_file()),None)
  assert resolved is not None and resolved.resolve()==obj.resolve(),row['module']
 return manifest,paths,names

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--lean',required=True);ap.add_argument('--runtime-base-root',required=True,help='Exact PR528 complete-bank-endpoint runtime inventory.');ap.add_argument('--mathlib-root',required=True,help='Existing exact Mathlib4.21 cache tree; no downloads.');ap.add_argument('--build-dir',default='.build');ap.add_argument('--slot-service',help='Optional existing FIFO slot service exposing acquire(); does not change Lean inputs.');ap.add_argument('--lean-sha256');args=ap.parse_args()
 assert Path('/proc/self/status').is_file(),'Linux /proc is required for the stated memory review'
 roots={'included':ROOT}
 assert all(p.is_dir() for p in roots.values())
 source_for=lambda row:roots[row['origin']]/row['file']
 def source_data(row):
  data=source_for(row).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'] and len(data)==row['bytes'],row['module'];return data
 lean=Path(args.lean).resolve();assert lean.is_file()
 if args.lean_sha256:assert sha(lean)==args.lean_sha256
 version=subprocess.check_output([str(lean),'--version'],text=True).strip();assert re.search(r'\b4\.21\.0\b',version),version
 external_manifest=Path(args.runtime_base_root).resolve()/'EXTERNAL_OBJECTS.json'
 external,external_paths,external_names=verify_external(lean,Path(args.mathlib_root).resolve(),external_manifest)
 manifest=json.loads((ROOT/'MANIFEST.json').read_text());rows=manifest['compile_order'];names={r['module']for r in rows};seen=set()
 assert not names & external_names
 assert len(rows)==5 and manifest['source_bytes']==214798
 assert all(r['origin']=='included' for r in rows)
 assert sha(ROOT/'MANIFEST.json')=='dd3880ce395e899be44fe758d9dbd6bc989dfc0b25e07ad14a2cc9613ab8ebc3'
 dependencies=json.loads((ROOT/'DEPENDENCIES.json').read_text())
 expected_commits={'pr528':'ba5e50abb80c6b854b127ccbe37d524e11c6db72'}
 assert sha(ROOT/'DEPENDENCIES.json')=='138af9e80d9f0d8c18f331d86bec4f3b3e69af8898f51b1024f106703598ad7f'
 assert dependencies['pr528']['commit']==expected_commits['pr528']
 for row in rows:
  data=source_data(row)
  imports=[]
  for line in data.decode().splitlines():
   m=re.match(r'^import\s+(.+)$',line)
   if m:imports.extend(m[1].split('--',1)[0].split())
  assert imports==row['imports'];assert set(imports)<=seen|external_names;seen.add(row['module'])
 assert sum(len(r['expected_probes']) for r in rows)==34
 reachable=set();external_rows={r['module']:r for r in external['modules']}
 def visit(name):
  if name in reachable:return
  assert name in external_rows;reachable.add(name)
  for child in external_rows[name]['imports']:visit(child)
 for row in rows:
  for imp in row['imports']:
   if imp in external_names:visit(imp)
 assert reachable==external_names,'Exact external subset must equal the transitive import closure'
 build=Path(args.build_dir);build=build if build.is_absolute()else ROOT/build;build.mkdir(parents=True,exist_ok=False);(build/'logs').mkdir();(build/'receipts').mkdir();(build/'sources').mkdir();(build/'objects').mkdir()
 build=build.resolve()
 for row in rows:
  target=build/'sources'/(row['module']+'.lean');target.write_bytes(source_data(row));assert sha(target)==row['sha256']
 for module in names:
  assert not any((p/(module+'.olean')).exists() for p in external_paths),module
 service=None
 if args.slot_service:
  spec=importlib.util.spec_from_file_location('existing_lean_slot_service',Path(args.slot_service).resolve());service=importlib.util.module_from_spec(spec);spec.loader.exec_module(service)
 env=dict(os.environ);env['LEAN_PATH']=os.pathsep.join([str(build/'objects')]+[str(p) for p in external_paths]);env['LEAN_EXTRA_PATHS']='';env.pop('LEAN_SYSROOT',None);env['MIMALLOC_ARENA_RESERVE']='64MiB'
 outcome={'started_utc':now(),'manifest_sha256':sha(ROOT/'MANIFEST.json'),'dependencies_manifest_sha256':sha(ROOT/'DEPENDENCIES.json'),'dependency_commits':expected_commits,'lean_version':version,'lean_binary_sha256':sha(lean),'external_manifest_sha256':sha(external_manifest),'external_library_paths':[str(p) for p in external_paths],'source_search_path':env['LEAN_PATH'],'status':'RUNNING','receipts':[]};(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n')
 for row in rows:
  requested=time.monotonic();slot=None;handle=None;handles=[]
  if service:slot,handle,handles=service.acquire('isolated_complete_bank_endpoint_package:'+row['module'])
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
   passed=proc.returncode==0 and not timed_out and not forbidden and probe_match and output_path.is_file()and sha(source)==row['sha256']and hashlib.sha256(source_data(row)).hexdigest()==row['sha256'];review=passed and(elapsed>40 or peak>int(3.5*1024**3))
   rec={'module':row['module'],'source_sha256':row['sha256'],'status':'PASS'if passed else'FAIL','review_stop':review,'exit_code':proc.returncode,'timed_out':timed_out,'started_utc':start_utc,'finished_utc':now(),'compile_seconds':elapsed,'queue_seconds':queue,'peak_vm_bytes':peak,'peak_rss_bytes':peak_rss,'peak_threads':peak_threads,'samples':samples,'complete_axiom_probes':probes,'expected_probes_match':probe_match,'slot':slot,'log_sha256':sha(log),'object_sha256':sha(output_path)if passed else None,'imports':row['imports'],'axiom_output':[s for s in text.splitlines()if'depends on axioms:'in s or'does not depend on any axioms'in s]};rp=build/'receipts'/(row['module']+'.json');rp.write_text(json.dumps(rec,indent=2)+'\n');outcome['receipts'].append({'module':row['module'],'receipt_sha256':sha(rp),'status':rec['status']});outcome['status']='REVIEW_STOP'if review else('RUNNING'if passed else'FAIL');(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n');print(json.dumps(rec),flush=True)
   if not passed or review:return 2
  finally:
   if handle:fcntl.flock(handle,fcntl.LOCK_UN)
   for h in handles:h.close()
 verify_external(lean,Path(args.mathlib_root).resolve(),external_manifest)
 for row in rows:
  assert sha(build/'sources'/(row['module']+'.lean'))==row['sha256'] and hashlib.sha256(source_data(row)).hexdigest()==row['sha256']
 outcome['post_preservation_verified_utc']=now()
 outcome['status']='PASS';outcome['finished_utc']=now();outcome['modules']=len(outcome['receipts']);(build/'REPLAY_RESULT.json').write_text(json.dumps(outcome,indent=2)+'\n');print('PASS exact isolated5-module selected rational closure',flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
