"""Fresh PR496 pooled complex component audit after completed unchanged PR484 replay."""
from pathlib import Path
import json,subprocess,sys,time,hashlib,os
R=Path(__file__).resolve().parent;S=R/'source496-review';BASE=R/'pr496-complex-full314/gauge80-kernel42';O=R/'pr496-pooled-complex-replay';O.mkdir(exist_ok=False);A=O/'audit';A.mkdir();start=time.monotonic();steps=[]
assert json.load(open(R/'pr496-complex-full314/RECEIPT.json'))['status']=='PASS_FULL_COMPLEX_GAUGE_KERNEL_COMPOSITION'
commands=[('emitter',[S/'code/emit_pooled.py',S/'vendor/complex/e8-complex-gauge-kernel',BASE,S/'data/COLORED-OWNERS.json.gz',O/'hosted']),('controller',[S/'code/audit_pooled.py',BASE,O/'hosted',O/'HOSTING-AUDIT.json']),('serial-pool',[S/'code/finite_serial_pool.py',O/'FINITE-SERIAL-POOL.json']),('owners',[S/'code/audit484/audit_pooled_owners.py',A,BASE,O/'hosted',BASE/'work/complex-nine-native/DATA-PHASES.json']),('scalar-invoice',[S/'code/audit484/audit_scalar_invoice.py',A,BASE,O/'hosted']),('global-prefix',[S/'code/audit484/audit_pooled_prefix.py',A,BASE,O/'hosted',O/'HOSTING-AUDIT.json'])]
for name,args in commands:
 with (O/(name+'.log')).open('w') as f:q=subprocess.run([sys.executable,'-B',*map(str,args)],stdout=f,stderr=subprocess.STDOUT)
 steps.append(dict(stage=name,exit=q.returncode));(O/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n');q.check_returncode();print('PASS',name,flush=True)
receipt=dict(status='PASS_POOLED_COMPLEX_COMPONENT_CHECKS_NO_BIT_OR_OUTER_REPLAY',steps=steps,seconds=time.monotonic()-start,source_manifest_sha256=hashlib.sha256((S/'MANIFEST.json').read_bytes()).hexdigest(),provider_receipt_sha256=hashlib.sha256((R/'pr496-complex-full314/RECEIPT.json').read_bytes()).hexdigest(),scope='Fresh unchanged complex provider and changed pooled emitter, controller, serial operator, owners, scalar invoice and global prefix. Not a full PR496 two-supplier or outer composition replay.')
(O/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt,flush=True)
