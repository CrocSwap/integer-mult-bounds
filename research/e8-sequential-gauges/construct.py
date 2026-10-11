from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import copy,json,sys,hashlib,gzip
r=Path(__file__).resolve().parent;out=Path(sys.argv[2]);assert not out.exists();out.mkdir(parents=True);sys.dont_write_bytecode=True;sys.path.insert(0,str(r.parent/'e8-response-resynth-bank64/vendor402'));from cxkernel import rehist,inside,first_frames
base=json.loads((Path(sys.argv[1])).read_text());c=copy.deepcopy(base);plans=sorted(json.loads((r/'SELECTION.json').read_text()),key=lambda p:-p['gain']);ns={};exec(compile((r.parent/'e8-response-resynth-bank64/vendor402/cxop.py').read_text().split('\na, ta = op(')[0],'raw-op','exec'),ns);rows,tot=ns['op'](base);used=set();selected=[];gates=[];pivots=[];first=first_frames(base);ext=dict(base['ext'])
for plan in plans:
 roles=set(plan['donors'])|{p['pivot'] for p in plan['pivots']}
 if roles&used:continue
 assert not roles&set(ext)
 E=plan['basis'];fid=next((i for i,e in enumerate(c['frames']) if e==E),len(c['frames']))
 if fid==len(c['frames']):c['frames'].append(E)
 for s in roles:assert inside(E,base['frames'][first[s]])
 for p in plan['pivots']:
  pivot=p['pivot'];co={int(k):Q(str(v)).limit_denominator(10000) for k,v in p['coefficients'].items()}
  for t in range(base['v'],2*base['v']):assert rows[t].get(pivot,Q(0))+sum(q*rows[t].get(d,Q(0)) for d,q in co.items())==0
  c['start'][pivot]=fid;ext[pivot]=fid;pivots.append(pivot)
  for donor,q in co.items():
   assert q.denominator in (1,2)
   gates.extend([['in',fid,donor,[[pivot,1 if q>0 else -1,q.denominator]]] for _ in range(abs(q.numerator))])
 used|=roles;selected.append(plan)
c['A']=gates+c['A'];c['ext']=sorted([p,f] for p,f in ext.items());c=rehist(c)
# Check every actual transition, including source-touching empty markers.
current=c['start'][:]
for section in ('A','B'):
 for gate in c[section]:
  roles=[gate[2]]+[z[0] for z in gate[3]]+(gate[4] if gate[0]=='out' else [])
  for s in roles:assert inside(c['frames'][current[s]],c['frames'][gate[1]]),(s,current[s],gate);current[s]=gate[1]
for s in range(len(current)):assert inside(c['frames'][current[s]],c['frames'][c['final'][s]])
new,ntot=ns['op'](c);assert all(new[t].get(p,Q(0))==0 for p in ext for t in range(base['v'],2*base['v']))
# Full raw operator must equal right multiplication by each literal prepended shear.
expected=copy.deepcopy(rows)
for gate in reversed(gates):
 _,f,d,terms=gate;p,a,b=terms[0];q=Q(a,b)
 for row in expected:
  value=row.get(p,Q(0))+q*row.get(d,Q(0))
  if value:row[p]=value
  else:row.pop(p,None)
assert new==expected
expected_tot=copy.deepcopy(tot)
for gate in reversed(gates):
 _,f,d,terms=gate;p,a,b=terms[0];q=Q(a,b)
 for row in expected_tot.values():
  value=row.get(p,Q(0))+q*row.get(d,Q(0))
  if value:row[p]=value
  else:row.pop(p,None)
assert ntot==expected_tot
bad=copy.deepcopy(c);bad['A'].pop(0);wrong,_=ns['op'](bad);assert any(wrong[t].get(p,Q(0)) for p in ext for t in range(base['v'],2*base['v']))
headlen=len(base['A'])-len(json.loads((r.parent/'e8-shared-donor-chains/inputs/helper781.json').read_text())['A']);bad=copy.deepcopy(c);bad['A']=base['A'][:headlen]+gates+base['A'][headlen:];wrong,_=ns['op'](bad);assert any(wrong[t].get(p,Q(0)) for p in ext for t in range(base['v'],2*base['v']))
raw=json.dumps(c,sort_keys=True,separators=(',',':')).encode();(out/'candidate.json').write_bytes(raw);h=lambda z:Counter({int(k):sum(b.get(k,0) for b in z['blocks'].values()) for b in z['blocks'].values() for k in b});delta=h(c);delta.subtract(h(base));delta={k:v for k,v in delta.items() if v}
headall=c['A'][:len(c['A'])-len(json.loads((r.parent/'e8-shared-donor-chains/inputs/helper781.json').read_text())['A'])]
N={};written=set()
for gate in headall:
 assert gate[0]=='in'
 for source,a,b in gate[3]:
  assert source not in written
  row=N.setdefault(gate[2],{});row[source]=row.get(source,Q(0))+Q(a,b)
 written.add(gate[2])
def multiply(a,b):
 result={}
 for i,row in a.items():
  rr={}
  for k,q in row.items():
   for j,z in b.get(k,{}).items():rr[j]=rr.get(j,Q(0))+q*z
  rr={j:q for j,q in rr.items() if q}
  if rr:result[i]=rr
 return result
N2=multiply(N,N);assert N2 and not multiply(N2,N)
oldhead=base['A'][:len(base['A'])-len(json.loads((r.parent/'e8-shared-donor-chains/inputs/helper781.json').read_text())['A'])];olddonors={g[2] for g in oldhead};ans=dict(status='PASS_EXACT_SEQUENTIAL_GAUGE_RAW_OPERATOR_AND_NESTED_FRAMES',new_pivots=pivots,former_donors_promoted=sorted(set(pivots)&olddonors),gauges=len(ext),new_gates=len(gates),selected=selected,delta=delta,rank_mass_delta=sum(k*v for k,v in delta.items()),candidate_sha256=hashlib.sha256(raw).hexdigest(),N_squared_nonzero_entries=sum(len(row) for row in N2.values()),N_cubed_zero=True,ordered_prefix_sources_read_before_write=True,controls_rejected=['omit new entrance gate','reverse ordered entrance layers'])
(out/'RESULT.json').write_text(json.dumps(ans,indent=2)+'\n');print(json.dumps({k:v for k,v in ans.items() if k!='selected'},indent=2))
