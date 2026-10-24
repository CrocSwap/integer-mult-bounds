#!/usr/bin/env python3
"""Read-only literal invoice, source/closure binding and optional exact replay."""
from pathlib import Path
from collections import Counter
import argparse,json,resource,hashlib
from exact_engine import evaluate,need
from invoice import H,W,ROOT,CAP,PKG,HEAD,read,sha,checked,transpose_records,local_paid,assemble,hist,scalar
p=argparse.ArgumentParser();p.add_argument('--static-only',action='store_true');p.add_argument('--receipt',type=Path,default=H/'FUNDING-v2.json');a=p.parse_args()
resource.setrlimit(resource.RLIMIT_AS,(500*1024*1024,500*1024*1024))
r=read(a.receipt);ip=H/'INVOICE-v1.json';need(sha(ip)==r['invoice']['sha256'],'invoice changed');inv=read(ip)
m=read(CAP/'ROOT-MANIFEST.json');need(m['head']==HEAD and sha(CAP/'ROOT-MANIFEST.json')==r['source']['root_manifest_sha256'],'source manifest changed')
for row in m['rows']:checked(row,(CAP/row['path']).read_bytes())
for name,row in r['source']['canonical_dependencies'].items():need(sha(Path(row['path']))==row['sha256'],'canonical input changed')
for key,file in [('engine_sha256','exact_engine.py'),('invoice_runner_sha256','invoice.py'),('funding_runner_sha256','funding.py')]:need(sha(H/file)==r[key],'independent code changed '+file)
if 'closure_dependencies_sha256' in r:
 for name,h in r['closure_dependencies_sha256'].items():need(sha(Path(name))==h,'gate dependency changed')
 need(sha(H/'close_funding.py')==r['closure_runner_sha256'],'closure code changed')
 cr=read(Path(r['precision_stock_gate']['path']))
 for name,h in cr['dependencies_sha256'].items():need(sha(ROOT/name)==h,'precision source dependency changed')
x=read(CAP/PKG/'WORD.json.gz');base=read(H/'frozen-canonical/research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz');c=base['canonical'];ctl=read(H/'frozen-canonical/research/joint-helper-lattice/CONTROLLER.json')
need(x['forward_body']==transpose_records(x['backward'],c),'literal transpose chronology changed')
owned=set(map(tuple,x['owned_roles']));helpers=Counter(len(c['frames'][c['final'][i]])-len(c['frames'][c['start'][i]]) for i in range(224,len(c['start'])) if ('L',i) not in owned)
loc={};sc={}
for d,k in [('forward','forward_body'),('backward','backward')]:loc[d],sc[d],_,_=local_paid(x[k],c,x['backward'] if d=='forward' else None)
P,T,*_=assemble(ctl,loc,{'forward':helpers,'backward':helpers});need({'paid':hist(P),'productive':hist(T)}==inv['histograms'],'literal invoice reconstruction differs')
sc['forward']+=2*len(c['ports'])*scalar(['scale',['L',0],-1,1]);need(max(sc.values())==inv['ordinary']['local_scalar_max'],'new scalar charge mismatch')
result={'status':'PASS_READ_ONLY_LITERAL_AND_SOURCE_GATE_REPRODUCTION','receipt_sha256':sha(a.receipt),'invoice_sha256':sha(ip),'endpoint_funded':r['endpoint_funded'],'exact_numerical_replay':False}
if not a.static_only:
 fresh=evaluate(hist(T),hist(P),r['config'])
 for k,v in fresh.items():
  if k not in ('seconds','status','external_gate_requirements'):need(r[k]==v,'exact numerical mismatch '+k)
 result.update(status='PASS_READ_ONLY_LITERAL_AND_EXACT_FUNDING_REPRODUCTION',exact_numerical_replay=True,seconds=fresh['seconds'])
print(json.dumps(result))
