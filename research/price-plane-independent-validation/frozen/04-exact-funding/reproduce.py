#!/usr/bin/env python3
"""Read-only exact replay of the frozen independent arithmetic receipt."""
from pathlib import Path
import argparse,json,resource,hashlib
from exact_engine import evaluate,need
from bind_and_check import authenticate_capsule,load_bound_invoice
H=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,default=H/'receipt-v1.json');a=p.parse_args()
resource.setrlimit(resource.RLIMIT_AS,(500*1024*1024,500*1024*1024))
r=json.loads(a.receipt.read_bytes());authenticate_capsule();inv,ih=load_bound_invoice(r['invoice']['sha256'])
if 'closure_dependencies_sha256' in r:
    for name,expected in r['closure_dependencies_sha256'].items():need(hashlib.sha256(Path(name).read_bytes()).hexdigest()==expected,'closure dependency changed')
for name,key in [('exact_engine.py','engine_sha256'),('bind_and_check.py','binding_runner_sha256')]:need(hashlib.sha256((H/name).read_bytes()).hexdigest()==r[key],'frozen independent engine changed')
fresh=evaluate(inv['histograms']['productive'],inv['histograms']['paid'],r['config'])
for k,v in fresh.items():
    if k not in ('seconds','status','external_gate_requirements'):need(r[k]==v,'arithmetic mismatch '+k)
print(json.dumps({'status':'PASS_READ_ONLY_REPRODUCTION','receipt_sha256':hashlib.sha256(a.receipt.read_bytes()).hexdigest(),'invoice_sha256':ih,'kappa':r['kappa'],'independent_replay_seconds':fresh['seconds'],'endpoint_funded':r['endpoint_funded']}))
