"""Source authentication and exact arithmetic for the written all-character proof.
This script is a proof audit aid; it does not turn arithmetic into formal proof.
"""
from pathlib import Path
import hashlib, itertools, json, platform, subprocess, sys, time
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');pkg=P/'sources/2870/research/f7-17point-fourier-obstruction-seedb5e318fe'
def need(x,msg):
    if not x:raise ValueError(msg)
start=time.monotonic();source=json.loads((pkg/'SOURCES.json').read_text());bindings=[]
for ref in source['references']:
    if not ref.get('local_path'):continue
    raw=subprocess.check_output(['git','show',ref['head']+':'+ref['source_path']],cwd=R)
    need(raw==(pkg/ref['local_path']).read_bytes(),'original vendor bytes')
    need(hashlib.sha256(raw).hexdigest()==ref['sha256'],'vendor hash')
    bindings.append(dict(pr=ref['pr'],path=ref['source_path'],sha256=ref['sha256']))
# All nonzero linear functionals have 64 points in each coset, and their
# coset-indicator transform is supported precisely at 0 and u.
def character(u,x):return 1-2*((u&x).bit_count()%2)
checked=0
for u in range(1,128):
    odd=[x for x in range(128) if character(u,x)==-1]
    need(len(odd)==64,'hyperplane cardinality')
    for v in range(128):
        actual=sum(character(v,x) for x in odd)
        need(actual==(64 if v==0 else -64 if v==u else 0),'coset transform')
        checked+=1
# Counting-feasible splits, local obstruction, then the global Parseval bill.
splits=[s for s in range(18) if s*(17-s)>=64]
need(splits==[6,7,8,9,10,11],'split count')
local_remaining=128*6-2*6**2;local_allowed=126*2**2
need(local_remaining==696 and local_allowed==504 and local_remaining>local_allowed,'local gap')
surviving=[s for s in splits if s not in [6,11]]
coefficients=sorted(2*s-17 for s in surviving)
need(coefficients==[-3,-1,1,3],'allowed coefficients')
remaining=128*17-17**2;allowed=127*max(x*x for x in coefficients)
need(remaining==1887 and allowed==1143 and remaining>allowed,'global gap')
# Positive control: a real cover is not eliminated by the two-stage argument.
cover=[0,1,2,3,4,5,6,8,16,31];need(len({a^b for a in cover for b in cover})==32,'cover')
actual_coeff=[sum(character(u,x) for x in cover) for u in range(1,32)]
need(sum(x*x for x in actual_coeff)==32*10-100,'positive Parseval')
# Check the new author progress export structurally and validate every example;
# counts remain recorded author evidence, not freshly enumerated here.
progress=json.loads((pkg/'ANCHOR-PROGRESS.json').read_text())['modes']
expected_keys={f'v0={x}' for x in range(128) if x.bit_count()%2==0 and x not in (0,3)}
examples=0
for mode,k,budget,total_expected in [('k10b3',10,3,149990400),('k11b4',11,4,0)]:
    rec=progress[mode];need(rec['complete'] is True,'author completion flag')
    need(set(rec['shards'])==expected_keys,'author shard inventory')
    hist={}
    for key,shard in rec['shards'].items():
        v0=int(key.split('=')[1])
        for e,c in shard['hist'].items():
            need(type(c) is int and c>=0 and 0<=int(e)<=budget,'author histogram type')
            hist[e]=hist.get(e,0)+c
        for e,pts in shard['examples'].items():
            need(len(pts)==len(set(pts))==k and set((0,3,v0))<=set(pts),'example shape')
            need(all(x in range(128) and x.bit_count()%2==0 for x in pts),'example ambient group')
            need(all(x>v0 for x in pts if x not in (0,3,v0)),'example shard')
            sums={a^b for i,a in enumerate(pts) for b in pts[:i]}
            need(k*(k-1)//2-len(sums)==int(e),'example excess')
            need(shard['hist'].get(e,0)>0,'example histogram binding');examples+=1
    need(hist==rec['total_hist'] and sum(hist.values())==total_expected,'author total consistency')
detail=dict(author_progress_examples=examples,author_progress_shards=124,original_vendor_bindings=bindings,coset_transform_identities=checked,local_parseval=[local_remaining,local_allowed],global_parseval=[remaining,allowed],allowed_coefficients=coefficients,positive_cover_points=len(cover),scope='Checks arithmetic and finite character identities supporting the written corollary. Does not replay predecessor long censuses or certify optional resume files.')
log=P/'check-2870-supplement.log';log.write_text(json.dumps(dict(status='PASS',**detail),sort_keys=True)+'\n')
receipt=dict(number=2870,head=json.loads((P/'2870.json').read_text())['headRefOid'],status='passed',seconds=time.monotonic()-start,commands=[dict(argv=[sys.executable,str(Path(__file__).resolve())],exit_code=0)],input_sha256={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),pkg/'README.md',pkg/'MAINTAINER-COROLLARY.md',pkg/'SOURCES.json',pkg/'fourier17.py',pkg/'ANCHOR-PROGRESS.json',pkg/'CERTIFICATE.json']},log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),environment=dict(python=sys.version,platform=platform.platform()),details=detail)
(P/'check-2870-supplement.json').write_text(json.dumps(receipt,indent=2)+'\n');print('2870 PASS all-character arithmetic and exact vendor source binding',flush=True)
