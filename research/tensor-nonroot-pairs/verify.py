"""Offline paired rational whole-owner construction; conditional GL-cover assembly.
Run: python verify.py NEW_OUTPUT [--complex-output EXACT_COMPLETED_OUTPUT]
"""
from pathlib import Path
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,time
assert __debug__
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--complex-output',type=Path);ap.add_argument('--cxx');ap.add_argument('--boost-include');args=ap.parse_args()
OUT=args.output.resolve();assert not OUT.exists() and not OUT.is_relative_to(ROOT)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def integrity():
 actual={p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.rglob('*')if p.is_file()and p!=ROOT/'MANIFEST.json'and '__pycache__'not in p.parts}
 assert actual==read(ROOT/'MANIFEST.json'),'Package manifest mismatch'
integrity();OUT.mkdir(parents=True);start=time.monotonic();steps=[]
env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHONPATH=os.pathsep.join(map(str,[ROOT/'vendor/runtime',ROOT/'vendor/complex',ROOT/'code'])),TMP=str(OUT),TEMP=str(OUT));env.pop('PYTHONOPTIMIZE',None)
def run(name,cmd):
 print('RUN',name,flush=True);t=time.monotonic();p=OUT/(name+'.log')
 with p.open('w',encoding='utf-8')as f:z=subprocess.run(list(map(str,cmd)),env=env,stdout=f,stderr=subprocess.STDOUT)
 assert z.returncode==0,(name,p.read_text(encoding='utf-8')[-5000:])
 steps.append(dict(name=name,seconds=round(time.monotonic()-t,3),log_sha256=sha(p)));print('PASS',name,flush=True)
def py(name,path,*a):run(name,[sys.executable,'-B',path,*a])
try:
 py('rank139-source',ROOT/'code/basis_constructor.py',OUT/'base')
 py('response-retiming',ROOT/'code/retime_constructor.py',OUT/'base/word.json',ROOT/'code/RETIME-SELECTION.json',OUT/'retimed')
 assert sha(OUT/'retimed/word.json')==sha(ROOT/'bit470/data/word.json')
 cxx=args.cxx or os.environ.get('CXX')or shutil.which('g++')or shutil.which('clang++')
 if not cxx and Path('C:/mingw64/bin/g++.exe').exists():cxx='C:/mingw64/bin/g++.exe'
 assert cxx,'Set CXX or --cxx to a C++17 compiler'
 extra=['--cxx',cxx];boost=args.boost_include or os.environ.get('BOOST_INCLUDE')
 if boost:extra+=['--boost-include',boost]
 local=OUT/'local'
 py('nonroot-native-provider',ROOT/'code/audit_nonroot.py',ROOT,OUT/'retimed/word.json',ROOT/'inputs/NONROOT-SELECTION.json',local,*extra)
 parent=OUT/'parent';parent.mkdir()
 for name in ['GLOBAL.json','GLOBAL-TEMPLATE.json.gz','GEOMETRY.json']:
  frozen=ROOT/'inputs'/('PAIRED-PARENT-'+name+(''if name.endswith('.gz')else'.gz'));b=frozen.read_bytes();(parent/name).write_bytes(b if name.endswith('.gz')else gzip.decompress(b))
 allocation=OUT/'allocation';owners=allocation/'PAIRED-OWNERS.json'
 py('paired-owner-construction',ROOT/'code/paired_owner_witness.py',local/'word.json',ROOT/'inputs/PAIRED-FLOW.json',local/'NONROOT-AUDIT.json',allocation)
 py('rational-route-controls',ROOT/'code/audit_route_registry.py',owners,OUT/'ROUTE-CONTROLS.json')
 bit=OUT/'bit';bit.mkdir();host=bit/'hosted'
 py('complete-physical-emission',ROOT/'code/emit_paired.py',parent,local,local/'word.json',owners,host)
 py('actual-full-matrix-owners',ROOT/'code/audit_actual_pairs.py',owners,local/'word.json',host,host/'COVER-OWNER-INJECTION.json')
 py('literal-route-factor-invoice',ROOT/'code/route_factor_invoice.py',host/'GEOMETRY.json',owners,host/'ROUTE-FACTORS.json')
 py('independent-physical-invoice',ROOT/'code/independent_paired_invoice.py',host,local,owners,host/'AUDIT.json')
 if args.complex_output:
  previous=args.complex_output.resolve();pin=read(ROOT/'inputs/complex-reuse-pin.json');receipt=read(previous/'RECEIPT.json')
  assert receipt['status']==pin['status'] and sha(previous/'RECEIPT.json')==pin['receipt_sha256']
  for rel,h in pin['implementation'].items():assert sha(ROOT/rel)==h,('changed complex implementation',rel)
  for rel,h in pin['outputs'].items():assert sha(previous/rel)==h,('changed complex evidence',rel)
  cx=previous/'complex';steps.append(dict(name='completed-complex-reused',receipt_sha256=pin['receipt_sha256'],source_files=len(pin['implementation']),output_files=len(pin['outputs'])))
 else:
  co=OUT/'complex-provider';tr=ROOT/'vendor/transport'
  py('complex-scalar-and-phase',ROOT/'code/build-local.py','--word',ROOT/'inputs/kernel79.json.gz','--vendor',tr/'upstream449','--routes',tr/'routes.json.gz','--clifford',tr/'clifford_exact.py','--out',co)
  py('complex-normalization',ROOT/'code/normalize-local.py','--canonical',co/'CANONICAL-WORD.json.gz','--programs',co/'LOCAL-PROGRAMS.json.gz','--checks',co/'LOCAL-CHECKS.json','--clifford',tr/'clifford_exact.py','--out',co)
  for ori,z in read(co/'NORMALIZED-CHECKS.json').items():assert z['sha256']==read(tr/'receipts79/NORMALIZED-CHECKS.json')[ori]['sha256']
  cx=OUT/'complex';cx.mkdir();phase=cx/'DATA-PHASES.json'
  py('data-phases',ROOT/'vendor/complex/complex_phases.py',co/'CANONICAL-WORD.json.gz',phase)
  selection=ROOT/'inputs/borrowed79-selection.json';base=ROOT/'inputs/complex-controller-base.json.gz';word=co/'CANONICAL-WORD.json.gz';localcx=co/'SCALAR-FRAME-AUDIT.json';wrap=co/'CANONICAL-WRAPPERS.json';template=cx/'GLOBAL-TEMPLATE.json.gz'
  py('complex-borrowed-emission',ROOT/'code/borrowed_emit.py',selection,base,phase,word,localcx,wrap,template,co)
  py('complex-borrowed-independent',ROOT/'code/borrowed_audit.py',template,selection,base,phase,word,localcx,wrap,cx/'PHYSICAL-AUDIT.json',co)
  py('complex-routes-independent',ROOT/'code/independent_routes.py',template,phase,cx/'INDEPENDENT-ROUTES.json')
  py('complex-whole-controller',ROOT/'code/global_controller.py',template,cx/'PHYSICAL-AUDIT.json',co/'NORMALIZED-CHECKS.json',phase,cx/'GLOBAL.json',cx/'AUDIT.json')
 py('two-moments-GL-invoice-and-47-constraints',ROOT/'code/assemble_gl.py',bit,host,host/'AUDIT.json',OUT/'RESULT.json','--nine','hosted','--complex',cx,'--engines',ROOT/'engines','--inherited',ROOT/'inherited','--residual-isometry',512,'--route-extra',5,'--label','PR473-rank139','--parent-kappa','51899464455217/40000000000000000')
 result=read(OUT/'RESULT.json');expected=read(ROOT/'EXPECTED.json')
 for k in ['kappa','bit_lower','complex_lower','bit_profile','complex_profile','bit_template_sha256','emitted_program_sha256']:assert result[k]==expected[k],(k,result[k],expected[k])
 integrity();receipt=dict(status='PASS_NONROOT_PAIRED_GL_COMPLETED_COMPLEX_REUSED'if args.complex_output else'PASS_NONROOT_PAIRED_GL_FULL_COMPOSITION',kappa=result['kappa'],seconds=round(time.monotonic()-start,3),python=sys.version,manifest_sha256=sha(ROOT/'MANIFEST.json'),steps=steps,scope='Fresh source reconstruction, native provider, full rational owner maps, literal complete program, independent invoice, two moments and47constraints. '+('Unchanged completed complex implementation and output hashes checked; no fresh complex execution. 'if args.complex_output else'Complex supplier freshly executed. ')+'Retains explicit all-size fixed-GL-routing and analytic contracts. No cross-family split; no Lean claim.')
 (OUT/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
except BaseException as e:
 (OUT/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),completed=steps),indent=2)+'\n');raise
