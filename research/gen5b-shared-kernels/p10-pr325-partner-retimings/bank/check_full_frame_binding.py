from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_source()
"""Independent binding of fresh emitted frame records to the bank census.
This is an artifact/count/endpoint interface review, not a replacement for
its separate full rational frame validator or generic compiler theorem.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,gzip,hashlib
if not __debug__:raise RuntimeError('Assertions required')
P=contract.BANK;L=contract.FRAME;A=contract.SOURCE
def read(p):
 b=Path(p).read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
R=read(L/'RESULT.json');contract.verify_frame()
assert R['status']=='PASS_FRESH_PR325_480_RETIMINGS_FULL_LOCAL_FRAME_WORD'
for name,h in R['artifacts'].items():assert sha(L/name)==h
B=read(P/'BANK-RESULT.json');C=read(P/'endpoint-charts.json.gz');E=read(L/'local-endpoints.json');M=read(L/'role-map.json');F=read(L/'local-frames.json.gz');fm=read(L/'source-frame-map.json');rec=read(L/'local-records.json.gz');events=read(A/'scalar-events.json.gz');rank=lambda f:F[str(f)]['rank']
assert B['source_admission_sha256']==R['source_result_sha256']==sha(A/'RESULT.json');assert E['n']==R['columns']==10020 and E['removed_sink_columns']==[]
assert list(sorted(M['representative_by_physical'].values()))==C['roles'] and M['physical_helpers']==8100 and M['virtual_roles']==9060
charts={z['frame']:z for z in C['charts']};checked=set()
for p in range(1920,10020):
 role=M['representative_by_physical'][str(p)];f=E['initial'][str(p)];end=E['final'][str(p)];assert rank(end)==20
 old=C['gauge_frames'].get(str(role));assert f==fm[str(old if old is not None else -1)]
 if old is None:assert rank(f)==0;continue
 assert rank(f)==16
 if old in checked:continue
 checked.add(old);chart=charts[old];frame=F[str(f)];cols=chart['basis_columns'];basis=[[Q(x) for x in row] for row in frame['basis']];ann=[[Q(x) for x in row] for row in frame['annihilator']]
 assert len(basis)==16 and len(ann)==4
 assert all(sum(x*y for x,y in zip(a,v))==0 for a in ann for v in cols[4:])
 assert all(9*sum(x*y for x,y in zip(a,v))-sum(a)*sum(v)==0 for a in basis for v in cols[:4])
assert len(checked)==120
current={int(k):v for k,v in E['initial'].items()};H=Counter();ei=0;copy_active=False
for row in rec:
 op,a,b,c,f,z=row
 if op==0:
  assert current[a]==b and f==rank(c)-rank(b)>=0;current[a]=c
  if f:H[f]+=1
 else:
  e=events[ei];ei+=1;assert [op,a,b]==[e[k] for k in ['op','a','b']]
  if op in [2,3]:
   assert e['c']==0 and c==fm[str(e['frame'])] and f==0 and z==rank(c) and current[a]==c
   if op==2:assert not copy_active;copy_active=True;H[z]+=1
   else:assert copy_active;copy_active=False
  else:
   assert op==1 and c==e['c'] and f==fm[str(e['frame'])] and E['categories'][z]==e['semantic'][0]
assert ei==len(events)==350680 and not copy_active and current=={int(k):v for k,v in E['final'].items()}
assert H=={int(r):n for r,n in R['one_stage_paid_histogram'].items()}=={int(r):n for r,n in B['helper_histogram'].items() if n}
assert sum(H.values())==46844 and sum(r*n for r,n in H.items())==179640
literal=Counter({r:300*n for r,n in H.items()});literal.update({r:115200 for r in [4,19,38,42]});assert literal=={int(r):n for r,n in B['literal_histogram'].items()}
for key in ['forward_norm','inverse_norm','literal_unit_additions']:assert R[key]==read(A/'RESULT.json')[key]
assert R['payload_bound']==B['payload_prefix_bound']
out={'status':'PASS_FRESH_FULL_FRAME_TO_BANK_INTERFACE_BINDING','full_frame_result_sha256':sha(L/'RESULT.json'),'bank_result_sha256':sha(P/'BANK-RESULT.json'),'physical_helper_endpoints_checked':8100,'distinct_chart_frame_pairs':120,'actual_local_records':len(rec),'source_scalar_COPY_records_bound':ei,'one_stage_children':sum(H.values()),'one_stage_rank_mass':sum(r*n for r,n in H.items()),'literal_histogram':literal,'literal_children':sum(literal.values()),'checker_sha256':sha(Path(__file__)),'scope':'Fresh full local frame stream and all endpoint/chart/role/operand/count interfaces bind to the bank certificate. Its separate exact all-frame validator and independent global lowering remain external gates. No prior selections or frames transplanted.'}
(P/'FRAME-BINDING.json').write_text(json.dumps(contract.portable(out),indent=2)+'\n');print(out['status'],len(rec),ei)
