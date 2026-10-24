#!/usr/bin/env python3
"""Read-only repeat of independent #5387 arithmetic and closure bindings."""
from pathlib import Path
import argparse,json,resource,hashlib
from exact_engine import evaluate,need
from bind_5387 import CAP,MANIFEST_SHA,HEAD,BASE
from bind_and_check import checked_bytes
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,default=H/'5387-receipt-v2.json');a=p.parse_args()
resource.setrlimit(resource.RLIMIT_AS,(500*1024*1024,500*1024*1024))
r=json.loads(a.receipt.read_bytes());need(sha(CAP/'IMMUTABLE-MANIFEST.json')==MANIFEST_SHA,'source manifest changed');m=json.loads((CAP/'IMMUTABLE-MANIFEST.json').read_bytes())
for row in m['rows']:checked_bytes(row,(CAP/row['capsule_path']).read_bytes())
for name,expected in [('EXACT-COMMIT.raw',HEAD),('CANONICAL-COMMIT.raw',BASE)]:
 b=(CAP/name).read_bytes();need(hashlib.sha1(b'commit '+str(len(b)).encode()+b'\0'+b).hexdigest()==expected,'raw commit changed')
for key,name in [('engine_sha256','exact_engine.py'),('binding_runner_sha256','bind_5387.py')]:need(sha(H/name)==r[key],'frozen independent executable changed')
if 'closure_dependencies_sha256' in r:
 for name,expected in r['closure_dependencies_sha256'].items():need(sha(Path(name))==expected,'closure dependency changed')
 cr=json.loads(Path(r['precision_stock_gate']['path']).read_bytes())
 for name,expected in cr['dependencies_sha256'].items():need(sha(ROOT/name)==expected,'expanded template dependency changed')
 need(sha(H/'close_5387.py')==r['closure_runner_sha256'],'closure executable changed')
ip=Path(r['invoice']['path']);need(sha(ip)==r['invoice']['sha256'],'invoice changed');inv=json.loads(ip.read_bytes())
fresh=evaluate(inv['histograms']['productive'],inv['histograms']['paid'],r['config'])
for k,v in fresh.items():
 if k not in ('seconds','status','external_gate_requirements'):need(r[k]==v,'independent arithmetic changed '+k)
print(json.dumps({'status':'PASS_READ_ONLY_REPRODUCTION','receipt_sha256':sha(a.receipt),'invoice_sha256':sha(ip),'kappa':r['kappa'],'endpoint_funded':r['endpoint_funded'],'independent_replay_seconds':fresh['seconds']}))
