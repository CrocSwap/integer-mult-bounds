

"""Offline changed-construction replay: Python3.11+, SymPy, C++17, Boost headers.
All inherited all-size supplier/hosting/compiler interfaces remain conditional.
"""
from pathlib import Path
import os,sys,json,hashlib,subprocess,time,argparse,shutil
assert __debug__
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('output',type=Path);parser.add_argument('--complex-output',type=Path);args=parser.parse_args()
OUT=args.output.resolve();assert not OUT.exists() and not OUT.is_relative_to(ROOT)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def integrity():
 actual={p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.rglob('*')if p.is_file()and p!=ROOT/'MANIFEST.json'and '__pycache__'not in p.parts}
 assert actual==read(ROOT/'MANIFEST.json'),'Package manifest mismatch'
integrity();OUT.mkdir(parents=True);start=time.monotonic();steps=[]
env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHONPATH=os.pathsep.join(map(str,[ROOT/'vendor/runtime',ROOT/'vendor/complex',ROOT/'code'])),TMP=str(OUT),TEMP=str(OUT));env.pop('PYTHONOPTIMIZE',None)
def run(name,args):
 print('RUN',name,flush=True);t=time.monotonic();p=OUT/(name+'.log')
 with p.open('w',encoding='utf-8')as f:r=subprocess.run(list(map(str,args)),env=env,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,p.read_text(encoding='utf-8')[-5000:])
 steps.append(dict(name=name,seconds=round(time.monotonic()-t,3),log_sha256=sha(p)));print('PASS',name,flush=True)
def py(name,path,*args):run(name,[sys.executable,'-B',path,*args])
try:
 overlays=read(ROOT/'inputs/PROVIDER-OVERLAYS.json')
 for n in ['11','1']:
  source=OUT/('provider-source-'+n)
  shutil.copytree(ROOT,source)
  for rel,h in overlays[n].items():
   frozen=ROOT/'inputs/providers'/n/rel;assert sha(frozen)==h
   shutil.copyfile(frozen,source/rel)
  py('changed-provider-'+n,source/'code/verify_bit.py',OUT/('provider-'+n))
 p11=OUT/'provider-11';p1=OUT/'provider-1';mixed=OUT/'mixed'
 py('stage-inventory-emission',ROOT/'code/emit_portfolio.py',p11/'hosted',p11,ROOT/'code/PORTFOLIO-SELECTION.json',mixed,p1)
 py('independent-mixed-physical-audit',ROOT/'code/audit_portfolio.py',p11,mixed,mixed/'AUDIT.json',p1)
 if args.complex_output:
  previous=args.complex_output.resolve();pin=read(ROOT/'inputs/complex-reuse-pin.json')
  receipt=read(previous/'RECEIPT.json');assert receipt['status']==pin['status'] and sha(previous/'RECEIPT.json')==pin['receipt_sha256']
  for rel,h in pin['implementation'].items():assert sha(ROOT/rel)==h,('changed complex implementation',rel)
  for rel,h in pin['outputs'].items():assert sha(previous/rel)==h,('changed complex evidence',rel)
  cx=previous/'complex';steps.append(dict(name='completed-complex-reused',receipt_sha256=pin['receipt_sha256'],source_files=len(pin['implementation']),output_files=len(pin['outputs'])))
 else:
  co=OUT/'provider';tr=ROOT/'vendor/transport'
  py('complex-scalar-and-phase',ROOT/'code/build-local.py','--word',ROOT/'inputs/kernel79.json.gz','--vendor',tr/'upstream449','--routes',tr/'routes.json.gz','--clifford',tr/'clifford_exact.py','--out',co)
  py('complex-normalization',ROOT/'code/normalize-local.py','--canonical',co/'CANONICAL-WORD.json.gz','--programs',co/'LOCAL-PROGRAMS.json.gz','--checks',co/'LOCAL-CHECKS.json','--clifford',tr/'clifford_exact.py','--out',co)
  for ori,c in read(co/'NORMALIZED-CHECKS.json').items():assert c['sha256']==read(tr/'receipts79/NORMALIZED-CHECKS.json')[ori]['sha256']
  cx=OUT/'complex';cx.mkdir()
  py('data-phases',ROOT/'vendor/complex/complex_phases.py',co/'CANONICAL-WORD.json.gz',cx/'DATA-PHASES.json')
  selection=ROOT/'inputs/borrowed79-selection.json';base=ROOT/'inputs/complex-controller-base.json.gz';phase=cx/'DATA-PHASES.json';word=co/'CANONICAL-WORD.json.gz';local=co/'SCALAR-FRAME-AUDIT.json';wrapper=co/'CANONICAL-WRAPPERS.json';template=cx/'GLOBAL-TEMPLATE.json.gz'
  py('borrowed-emission',ROOT/'code/borrowed_emit.py',selection,base,phase,word,local,wrapper,template,co)
  py('borrowed-independent',ROOT/'code/borrowed_audit.py',template,selection,base,phase,word,local,wrapper,cx/'PHYSICAL-AUDIT.json',co)
  py('routes-independent',ROOT/'code/independent_routes.py',template,phase,cx/'INDEPENDENT-ROUTES.json')
  py('whole-controller',ROOT/'code/global_controller.py',template,cx/'PHYSICAL-AUDIT.json',co/'NORMALIZED-CHECKS.json',phase,cx/'GLOBAL.json',cx/'AUDIT.json')
 py('two-moments-and-47-constraints',ROOT/'code/assemble.py',p11,mixed,mixed/'AUDIT.json',OUT/'RESULT.json','--complex',cx,'--engines',ROOT/'engines','--inherited',ROOT/'inherited','--route-extra',6,'--label','PR483','--parent-kappa','1296606691405309/1000000000000000000','--nine','hosted','--variant-globals',str(p1/'hosted/GLOBAL.json'))
 result=read(OUT/'RESULT.json');expected=read(ROOT/'EXPECTED.json')
 for key in ['kappa','bit_lower','complex_lower','bit_profile','complex_profile']:assert result[key]==expected[key],(key,result[key],expected[key])
 integrity();receipt=dict(status='PASS_RESPONSE_PORTFOLIO_COMPLETED_COMPLEX_REUSED' if args.complex_output else 'PASS_RESPONSE_PORTFOLIO_FULL_COMPOSITION',kappa=result['kappa'],seconds=round(time.monotonic()-start,3),python=sys.version,manifest_sha256=sha(ROOT/'MANIFEST.json'),steps=steps,scope=('Fresh two-provider reconstruction/native columns, actual mixed physical audit/invoice and47constraints; unchanged completed complex receipt,implementation and output hashes explicitly checked; no fresh complex execution.' if args.complex_output else 'Fresh two-provider, mixed physical and complex supplier replay with47constraints. All-size interfaces remain conditional; no Lean certification.'))
 (OUT/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
except BaseException as e:
 (OUT/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),completed=steps),indent=2)+'\n');raise
