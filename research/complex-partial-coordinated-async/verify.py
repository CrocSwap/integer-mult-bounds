"""Offline source-bound reconstruction, local physics and async finite admission."""
from pathlib import Path
import argparse,json,gzip,hashlib,subprocess,os,sys,time
assert __debug__
P=Path(__file__).resolve().parent;S=P.parent/'complex-partial-own-async';ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);ap.add_argument('--boost-include',type=Path);ap.add_argument('--cxx',default='c++');ap.add_argument('--reuse-factory',type=Path);ap.add_argument('--reuse-factory-admission',type=Path);ap.add_argument('--reuse-local',type=Path);a=ap.parse_args();O=a.out.resolve();assert not O.exists()and not O.is_relative_to(P);assert bool(a.reuse_factory)==bool(a.reuse_factory_admission)
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for root in [P,S]:
 actual={f.relative_to(root).as_posix():sha(f)for f in root.rglob('*')if f.is_file()and f!=root/'MANIFEST.json'and '__pycache__'not in f.parts};assert actual==read(root/'MANIFEST.json'),root
O.mkdir();A=O/'audit';A.mkdir();H=O/'hosted';steps=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
def run(name,script,*argv):
 log=O/(name+'.log');t=time.monotonic()
 with log.open('w')as f:q=subprocess.run([sys.executable,'-B',str(script),*map(str,argv)],stdout=f,stderr=subprocess.STDOUT,env=env)
 steps.append(dict(name=name,returncode=q.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)));(O/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n');assert q.returncode==0,(name,log.read_text()[-5000:]);print('PASS',name,flush=True)
def pins(root,file):
 for n,h in read(P/file).items():assert sha(root/n)==h,n
try:
 if a.reuse_factory:
  F=a.reuse_factory.resolve();V=a.reuse_factory_admission.resolve();pins(F,'REUSE-FACTORY-INPUTS.json');pins(V,'REUSE-FACTORY-ADMISSION-INPUTS.json')
  assert read(F/'RECEIPT.json')['status']=='PASS_FRESH_PARTIAL_OWN_KERNEL_RETIMED_COMPLEX_WORD'
  assert read(V/'RECEIPT.json')['status']=='PASS_PARTIAL_OWN_ASYNC_FINITE_COMPOSITION'
  assert read(V/'RECEIPT.json')['local_receipt_sha256']==sha(F/'RECEIPT.json');factory_mode='byte-pinned-completed-factory-and-admission-reuse'
 else:
  assert a.boost_include is not None,'Supply Boost headers for cold source verification or both explicit factory reuse paths.'
  run('fresh-source507',S/'vendor/partial-own/verify.py',O/'provider','--boost-include',a.boost_include.resolve(),'--cxx',a.cxx);F=O/'provider/retimed/gauge80-kernel42';factory_mode='fresh-source507-cold-verification'
 G=S/'vendor/partial-own/vendor/complex/e8-complex-gauge-kernel'
 run('construct-coordinated',P/'code/construct.py',G,F,P/'data/SELECTION.json',P/'data/LOCAL-WORD.json.gz',O/'CONSTRUCTED-WORD.json.gz')
 if a.reuse_local:
  B=a.reuse_local.resolve();pins(B,'REUSE-LOCAL-INPUTS.json');assert read(B/'RECEIPT.json')['status']=='PASS_FRESH_PARTIAL_COORDINATED_LOCAL';local_mode='byte-pinned-completed-changed-gauge-local-physics-reuse'
 else:
  run('fresh-coordinated-local',P/'code/verify_local.py',G,F,O/'CONSTRUCTED-WORD.json.gz',O/'local');B=O/'local/gauge80-kernel42';local_mode='fresh-changed-gauge-scalar-gaussian-guarded-physics'
 assert read(B/'split-centres/FULL-WORD.json.gz')==read(P/'data/LOCAL-WORD.json.gz')
 assert read(B/'split-centres/LOCAL-CHECKS.json')==read(P/'data/LOCAL-CHECKS.json')
 run('async-emission',P/'code/emit_async.py',G,B,P/'data/OWNERS.json.gz',P/'data/PLAN.json',H)
 run('async-independent-audit',P/'code/audit_async.py',B,H,A/'ASYNC-AUDIT.json')
 run('async-finite-invoice',P/'code/audit_async_invoice.py',A,B,H)
 run('exact-assembly',P/'code/assemble.py',A,B,H,P/'data/PR493-EXPECTED.json')
 x=read(A/'EXACT-ASSEMBLY.json');expected=read(P/'EXPECTED.json')
 for k,v in expected.items():assert x[k]==v,k
 r=dict(status='PASS_PACKAGED_PARTIAL_COORDINATED_ASYNC_FINITE_COMPOSITION',**expected,factory_mode=factory_mode,local_mode=local_mode,bit_mode='PR493 unchanged operator cited and profile repriced; cold source507 path also checks its operator',steps=steps,artifacts={f.relative_to(O).as_posix():sha(f)for f in sorted(A.glob('*.json'))},scope='Conditional finite witness; all-size compiler, mutable-basis/common-label, Lemma A realization, restored-row, precision/tape and analytic-transfer assumptions remain.')
 (O/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['kappa_decimal'],flush=True)
except BaseException as e:
 (O/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise
