# SPDX-License-Identifier: Apache-2.0
"""Relocate the replay tree and audit source imports and paths without full replay."""
from pathlib import Path
from hashlib import sha256
import ast,json,shutil,subprocess,sys,tempfile,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE_REQUIRED=[
 'inputs/pr7480/source.py','inputs/pr7480/construct.py','inputs/pr7480/WITNESS.json',
 'inputs/pr7480/derive_grid.py','inputs/pr7480/verify_native.py','inputs/pr7480/NATIVE-RESULT.json',
 'inputs/pr7480/RESULT.json','inputs/pr7480/WORD.json.gz','inputs/pr7480/INPUTS.json',
 'inputs/pr7480/adapt.py','inputs/pr7480/inputs/pr7334.tar.gz']
FULL_REQUIRED=['producer54/run_full.py','producer54/reroute/build.py',
 'producer54/validation_native/run.py','producer54/validation_native/owned_contract.py',
 'producer54/validation_signed/run.py']
CORE_REQUIRED=['producer54/run_core.py','producer54/reroute/independent_check.py',
 'producer54/reroute/adversarial.py','engines/retained_independent.py',
 'inputs/pr7113/ODD-TYPE-AB-CALLER.json']
GENERATED_FOR_PROBE=['producer54/reroute/WORD.json.gz','producer54/reroute/RESULT.json',
 'producer54/reroute/OLD-TO-NEW.json','producer54/validation_native/NATIVE-RESULT.json']
PAYLOAD=SOURCE_REQUIRED+FULL_REQUIRED+CORE_REQUIRED
for name in PAYLOAD+GENERATED_FOR_PROBE:assert(ROOT/name).is_file(),name
required={'frozen_source_inputs':SOURCE_REQUIRED,'full_replay_scripts':FULL_REQUIRED,
 'additional_core_replay_inputs':CORE_REQUIRED,
 'generated_inputs_carried_for_review':GENERATED_FOR_PROBE,
 'preserve_notices':['inputs/pr7480/NOTICE'],
 'notes':['The whole authenticated pr7334.tar.gz is required, including every inventoried member and nested archive.',
          'Keep the relative layout with producer54, inputs, and engines as siblings under the extracted package root.',
          'No pre-existing native or signed generated receipt is needed by run_full.py; each is recalculated before use.',
          'The candidate word, emitted splice receipt, and full receipts should nevertheless be shipped for independent review.']}
(HERE/'REQUIRED-FILES.json').write_text(json.dumps(required,indent=2)+'\n')
probe=r'''
from pathlib import Path
from hashlib import sha256
import ast,importlib.util,json,sys,time
root=Path(sys.argv[1]);out=Path(sys.argv[2]);started=time.time()
network_events=[]
def network_guard(event,args):
 if event in ('socket.connect','socket.connect_ex','socket.bind','socket.getaddrinfo','urllib.Request'):
  network_events.append(event);raise AssertionError('Unexpected network operation '+event)
sys.addaudithook(network_guard)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
native=load('relocated_native',root/'producer54/validation_native/run.py')
assert native.ROOT==root and native.SOURCE==root/'inputs/pr7480' and native.CANDIDATE==root/'producer54/reroute'
source=sys.modules['source'];files=set();data=[];engines=[]
with source.sources()as(vendor,archive,rank9,bundle,parent,old):
 assert sha256(source.canonical(native.construct(old))).hexdigest()==native.BASELINE
 for folder in(vendor,archive,rank9,bundle,parent):
  files.update(folder.rglob('*.py'))
 native_paths=[bundle/'gate.py',rank9/'candidate_gate.py',rank9/'physical_child.py',rank9/'signed_child.py',
  archive/'audit_native.py',archive/'audit_price.py',archive/'verify.py',vendor/'independent.py',
  vendor/'interval_gate.py',vendor/'frozen/clifford_exact.py',vendor/'frozen/native_verify.py',
  vendor/'frozen/verify_host3_odd.py',vendor/'frozen/physical.py',
  vendor/'retained/odd-native-common-grid/independent_bounds.py',
  vendor/'retained/query-only-precision-envelope/envelopes.py',
  vendor/'retained/query-only-precision-envelope/source_binding.py']
 for p in native_paths:
  assert p.is_file(),p
  engines.append({'name':p.name,'sha256':sha256(p.read_bytes()).hexdigest()})
 for p in(vendor/'INDEPENDENT-SOURCES.json',vendor/'data/caller.json',vendor/'data/bit-admission.json',rank9/'dyadic/CALLER.json'):
  assert p.is_file();data.append({'name':p.name,'sha256':sha256(p.read_bytes()).hexdigest()})
 with source.bundles()as(parts,unused,temp):
  assert 7113 in parts
  folder=parts[7113]/'replay/supplier7112/short-caller'
  expected=parts[7113]/'expected/ODD-TYPE-AB-CALLER.json'
  assert sha256(expected.read_bytes()).hexdigest()=='255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
  assert expected.read_bytes()==(root/'inputs/pr7113/ODD-TYPE-AB-CALLER.json').read_bytes()
  for name in('emit_odd_type_b.py','emit_odd_type_ab.py','check_odd_caller_exact_grid.py','check_odd_physical_binding.py',
   'check_odd_precision.py','check_odd_partial_admission.py','check_odd_fixed_tape_counts.py','short_native_catalogue.py','assemble_odd_application.py'):
   assert(folder/name).is_file(),name
  assert (root/'engines/retained_independent.py').read_bytes()==(folder/'independent.py').read_bytes()
  files.update((parts[7113]/'replay').rglob('*.py'))
  for module in tuple(sys.modules.values()):
   p=getattr(module,'__file__',None)
   if p and Path(p).is_file() and Path(p).suffix=='.py' and ('terminal-cut-source-'in p or str(root)in p):files.add(Path(p))
  files.update(root.rglob('*.py'))
  stems={p.stem for p in files};imports={};network=[];absolute=[]
  for p in sorted(files):
   text=p.read_text();tree=ast.parse(text,filename=str(p))
   names=set()
   for node in ast.walk(tree):
    if isinstance(node,ast.Import):names.update(a.name.split('.')[0]for a in node.names)
    elif isinstance(node,ast.ImportFrom)and node.module:names.add(node.module.split('.')[0])
    if isinstance(node,ast.Constant)and isinstance(node.value,str):
     if node.value.startswith(('/workspace/','/home/','/Users/')):absolute.append({'file':p.name,'value':node.value})
   for name in names:
    imports.setdefault(name,[]).append(p.name)
    if name in {'requests','urllib','socket','http','httpx','aiohttp','ftplib'}:network.append({'file':p.name,'module':name})
  third_party={n:sorted(set(v))for n,v in imports.items()if n not in sys.stdlib_module_names and n not in stems}
  # No source module in the native or signed closure requires a package outside
  # the standard library or the authenticated local source tree.
  assert not third_party,third_party
  assert not network,network
  assert not absolute,absolute
  report={'status':'PASS_RELOCATED_AUTHENTICATED_SOURCE_PREREQUISITES',
   'isolated_python':bool(sys.flags.isolated),'unrelated_cwd':str(Path.cwd()),
   'relocated_layout_checked':True,'authenticated_native_source_regenerated':True,
   'authenticated_fixed7113_caller_matches':True,'core_native_engine_authenticated':True,
   'python_files_inspected':len(files),'import_modules':sorted(imports),
   'external_package_imports':third_party,'network_api_imports':network,'network_events':network_events,
   'environment_specific_absolute_path_constants':absolute,'required_native_engines':engines,'required_data':data,
   'scope':'Source authentication, source reconstruction, relative paths, import dependencies, and static network audit only; full mathematical replay is not repeated.',
   'elapsed_seconds':time.time()-started}
  out.write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],report['python_files_inspected'],flush=True)
'''
with tempfile.TemporaryDirectory(prefix='producer-portable-layout-')as tmp:
 copied=Path(tmp)/'portable';copied.mkdir()
 for name in PAYLOAD+GENERATED_FOR_PROBE:
  target=copied/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 with(HERE/'PORTABILITY.log').open('w')as stream:
  subprocess.run([sys.executable,'-I','-B','-c',probe,str(copied),str(HERE/'PORTABILITY.json')],cwd=Path(tmp),stdout=stream,stderr=subprocess.STDOUT,check=True)
print((HERE/'PORTABILITY.log').read_text(),end='')
