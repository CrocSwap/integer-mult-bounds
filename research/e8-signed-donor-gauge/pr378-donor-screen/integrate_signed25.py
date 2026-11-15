from pathlib import Path
from collections import Counter
import json,gzip,hashlib,copy,math
P=Path('pr378-donor-screen');sha=lambda x:hashlib.sha256(x).hexdigest()
read=lambda f:json.loads((P/f).read_text())
priorraw=gzip.decompress((P/'prefix-gauge-bound-template.json.gz').read_bytes());prior=json.loads(priorraw);oldraw=gzip.decompress((P/'signed25-gauge-template.json.gz').read_bytes());new=json.loads(oldraw)
assert sha(priorraw)==read('ambient-phase-audit.json')['template_sha256']==read('bound-schedule-audit.json')['template_sha256']
assert sha(oldraw)==read('signed25-gauge-readback.json')['template_sha256']==read('signed25-gauge-emission.json')['template_sha256']
c=json.load(gzip.open(P/'signed25-donor-candidate.json.gz'));old=json.load(gzip.open(P/'prefix-donor-candidate.json.gz'))
for k in ['h','v','R','ext','ports','start','final','ret','scat']:assert c[k]==old[k]
# Unchanged window/bank action and operator bases bind the completed
# ambient proof and schedule; changed local edges checked separately.
for r,f in c['ext']:assert c['frames'][f]==old['frames'][dict(old['ext'])[r]]
for k in ['m','live','physical','recipe','idle_children','bank_padding','cover_final_correction','bank_geometry_sha256']:assert new[k]==prior[k]
for a,b in zip(new['calls'],prior['calls']):assert {k:v for k,v in a.items() if k!='local_program_sha256'}=={k:v for k,v in b.items() if k!='local_program_sha256'}
assert len(new['calls'])==len(prior['calls'])
t=copy.deepcopy(prior)
for k in ['candidate_sha256','local_programs','calls']:t[k]=new[k]
for a in t['calls']:a['local_program_sha256']=sha(json.dumps(t['local_programs'][a['orientation']],sort_keys=True,separators=(',',':')).encode())
t['version']='signed25-donor-bound-schedule-v1';t['scope']='New25-pair signed prefix plus nine exterior donor gauges. Exact prior schedule/owner/ambient identities reused only through explicit structural and basis equality. Changed local words/Clifford edges and finite invoice separately checked. Standalone replay and outer assembly remain pending.'
# Independently count actual paid children from local emitted operations,
# schedule-bound idle calls and padding, not the discovery histogram.
H=Counter()
for a in t['calls']:
 for e in t['local_programs'][a['orientation']]:
  if e[0]=='climb':H[e[5]]+=1
  elif e[0]=='center':H[e[4]]+=1
for a in t['idle_children']:H[a['rank']]+=a['replicas']
for a in t['bank_padding']:H[a['rank']]+=1
price=read('signed25-donor-screen.json');report=read('signed25-gauge-emission.json');bill=read('signed25-gauge-lift-audit.json')['bills']
assert H==Counter({int(k):v for k,v in price['profile'].items()})==Counter({int(k):v for k,v in report['paid_profile'].items()})
m=t['m'];v=c['v'];R=c['R'];h=c['h'];live=t['live'];physical=t['physical'];mass=sum(k*n for k,n in H.items());assert m*live-mass==2496
# Recompute adapter/group overcharges from emitted local records and bills.
compiler=64*(m+1)**3;macros=max(bill[o]['totals']['scalar_macros'] for o in bill);lc=sum(e[0] in ['climb','center'] for e in t['local_programs']['forward']);adapters=16*(macros+lc+2*v+R+h)+64*m+4*len(c['ext'])
prim=sum(bill[a['orientation']]['totals']['real_component_primitive_steps'] for a in t['calls']);T=1+max(a['replica'] for a in t['calls']);L=len({a['stage'] for a in t['calls']});K=len({a['pair'] for a in t['calls']});bridge=2*v*T*sum(e['kind']=='bridge' for e in t['recipe']);shifts=K*v*T;moves=2*K*v*T
items=6*v*T*L+2*L*T*R+len(t['idle_children'])*T+len(t['bank_padding'])+bridge+shifts+moves+live+physical+2*len(t['calls'])*len(c['ext']);outside=8*items+64*m
pv=prim+bridge+shifts+moves+live+(len(t['calls'])*adapters+outside)*compiler+64*physical
r=m//2;group=2**(r*r)*math.prod(2**(2*i)-1 for i in range(1,r+1));stock=group*physical;smass=group*mass;logical=group*pv+64;router=compiler*(logical+1)*(stock+1)**2;literal=2*(1<<30000)*stock**2+8*smass+4*stock+4+32*m
row=2*stock.bit_length()+9909+252;assert router<1<<30000 and literal<1<<100000 and row<20161 and m*m>2*max(H)**2
assert 32*m*(smass+(1<<100000))**2<1<<210000
invoice=dict(real_primitives_all_calls=prim,adapter_groups=adapters,outside_groups=outside,pervertex=pv,physical=physical,group_bits=group.bit_length(),physical_stock_bits=stock.bit_length(),logical_bits=logical.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),row=row)
for k,v in invoice.items():assert report['invoice'][k]==v
blob=json.dumps(t,sort_keys=True,separators=(',',':')).encode();(P/'signed25-bound-template.json.gz').write_bytes(gzip.compress(blob,mtime=0))
inputs=['signed25-donor-candidate.json.gz','signed25-gauge-lift-audit.json','signed25-gauge-readback.json','signed25-gauge-emission.json','prefix-gauge-bound-template.json.gz','bound-schedule-audit.json','ambient-phase-audit.json','prefix-gauge-routes.json.gz']
out=dict(status='PASS_CHANGED_WORD_INTEGRATION_BINDING_AND_INDEPENDENT_FINITE_RECOUNT',template_sha256=sha(blob),inherited_schedule_template_sha256=sha(priorraw),candidate_sha256=sha((P/'signed25-donor-candidate.json.gz').read_bytes()),input_pins={f:sha((P/f).read_bytes()) for f in inputs},paid_profile=dict(sorted(H.items())),rankmass=mass,deficit=m*live-mass,invoice=invoice,scope=t['scope'])
(P/'signed25-integration.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
