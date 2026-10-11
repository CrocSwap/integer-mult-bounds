"""Complete new partial-own local checks, then freshly admit the async composition."""
from pathlib import Path
import subprocess,json,hashlib,time,os,sys
R=Path(__file__).resolve().parent;P=R/'source507-review';S=P/'vendor/complex/e8-complex-gauge-kernel';C=P/'code';B=R/'partial-coordinated-local/gauge80-kernel42';O=R/'partial-coordinated-admission';O.mkdir(exist_ok=False);guard=O/'guarded';guard.mkdir();A=O/'audit';A.mkdir();H=O/'hosted';steps=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',LG_BASE=str(B.parent));env.pop('PYTHONOPTIMIZE',None);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.load(open(B/'RECEIPT.json'))['status']=='PASS_FRESH_PARTIAL_COORDINATED_LOCAL'
def run(name,script,*args,cwd=None):
 log=O/(name+'.log');t=time.monotonic();print('RUN',name,flush=True)
 with log.open('w')as f:q=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=cwd or O,env=env,stdout=f,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,returncode=q.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)));(O/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n');assert q.returncode==0,(name,log.read_text()[-5000:]);print('PASS',name,flush=True)
try:
 run('emit-async',R/'pr507-async-code/emit_async.py',S,B,R/'partial-coordinated-restricted-realized/OWNERS.json.gz',R/'partial-coordinated-restricted-realized/PLAN.json',H)
 run('audit-async',R/'pr507-async-code/audit_async.py',B,H,A/'ASYNC-AUDIT.json')
 run('invoice',R/'pr507-async-code/audit_async_invoice.py',A,B,H)
 run('arithmetic',R/'pr507-async-code/assemble.py',A,B,H,R/'source505-review/inputs/PR493-EXPECTED.json')
 x=json.load(open(A/'EXACT-ASSEMBLY.json'));expected=json.load(open(R/'partial-coordinated-arithmetic/EXACT-ARITHMETIC.json'));assert all(x[k]==expected[k]for k in ['kappa','complex_lower','bit_lower']);receipt=dict(status='PASS_PARTIAL_COORDINATED_ASYNC_FINITE_COMPOSITION',kappa=x['kappa'],kappa_decimal=x['kappa_decimal'],complex_lower=x['complex_lower'],complex_template_sha256=x['complex_template_sha256'],provider_mode='completed-source-pinned-provider-reuse',local_mode='completed-partial-factory-reuse; fresh coordinated-gauge scalar-phase-lemmaG-and-guarded-physics',bit_mode='PR493 unchanged operator cited; profile repriced',local_receipt_sha256=sha(B/'RECEIPT.json'),steps=steps,artifacts={p.relative_to(O).as_posix():sha(p)for p in sorted(O.rglob('*.json'))if p.name not in ['RECEIPT.json','STEPS.json']},scope='Conditional finite witness. Inherited all-size compiler, mutable-basis/common-label, Lemma A realization, restored-row, precision/tape and analytic-transfer assumptions remain.')
 (O/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],x['kappa_decimal'],flush=True)
except BaseException as e:
 (O/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise
