from pathlib import Path
from fractions import Fraction
import json,gzip,hashlib
P=Path(__file__).resolve().parent;S=P/'source-closure';t=json.loads(gzip.decompress((S/'GLOBAL-TEMPLATE.json.gz').read_bytes()));e=json.loads((S/'candidate/PAIR-SELECTION.json').read_text())['pairs'];op=json.loads((S/'candidate/OPERATOR.json').read_text());c=json.loads((S/'CANDIDATE.json').read_text())
assert len(t['calls'])==88 and len(e)==60
n=0
for call in t['calls']:
 for z in e:
  u,v=z['receiver'],z['donor'];a,b=call['owners'][u],call['owners'][v]
  assert a[0]!=b[0]and a[1]==['data',call['stage'],u-120]and b[1]==['data',call['stage'],v-120]
  assert a[0]<9600 and b[0]<9600;n+=2
assert n==10560
assert op['actual_global_owner_gate_instances']==n and op['gate_instances']==1320
assert op['extra_route_selector_bound']==c['extra_target_selector_calls']==2*11*8*120*78*154==253693440
assert op['source_template_sha256']==hashlib.sha256(gzip.decompress((S/'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest()
assert c['local_units']==16466 and c['source_prefix_forward']==1124 and c['source_prefix_inverse']==27414
k=Fraction(c['kappa']);old=Fraction('0.00125940678851843');assert k>old
r={'status':'PASS_INDEPENDENT_SIGNED60_88_ACTUAL_OWNER_CALL_BINDING_AND_SOURCE_FEE','candidate_sha256':hashlib.sha256((S/'CANDIDATE.json').read_bytes()).hexdigest(),'kappa':str(k),'target_owner_gates':n,'stage_relative_chart_gates':1320,'additional_selector_fee':253693440,'scope':'Actual660 independentcharttheorem expandedover88sourceboundcalls andtwoZERO/GtargetADDs. AllVALUErow owners distinctpergate, ordinarydatafamilies only, sourceinvoice targetrelative route154factor bound explicitlycharged. Producercomplete8+47 arithmetic sourcepins verified; independentcompleteglobalinvoice/47 analysis belongs releasegate, not inferred from this finiteowner check.'}
(P/'OWNERS.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
