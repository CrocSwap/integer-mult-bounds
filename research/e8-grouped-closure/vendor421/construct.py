"""Prepend capacity-admitted gauges then close chronological frames exactly.
OpenAI Codex; exact scalar word unchanged apart from literal entrance shears.
"""
from pathlib import Path
import json,copy,hashlib,argparse
import common as Re
from fractions import Fraction as Q
parser=argparse.ArgumentParser();parser.add_argument('base',type=Path);parser.add_argument('selection',type=Path);parser.add_argument('output',type=Path);parser.add_argument('--source-sha256',required=True);parser.add_argument('--expected-sha256');args=parser.parse_args()
def canonical(vs):
 piv={}
 for x in sorted(vs,reverse=True):
  for k,y in sorted(piv.items(),reverse=True):
   if x>>k&1:x^=y
  if x:
   k=x.bit_length()-1
   for j,y in list(piv.items()):
    if y>>k&1:piv[j]^=x
   piv[k]=x
 return [y for k,y in sorted(piv.items(),reverse=True)]
source=args.base;assert hashlib.sha256(source.read_bytes()).hexdigest()==args.source_sha256
root=args.output;assert not root.exists();root.mkdir(parents=True)
b=json.loads(source.read_text());c=copy.deepcopy(b);plans=json.loads(args.selection.read_text());head=[]
for pl in plans:
 E=canonical(pl['basis']);f=next((i for i,e in enumerate(c['frames']) if len(e)==len(E) and Re.inside(E,e)),len(c['frames']))
 if f==len(c['frames']):c['frames'].append(E)
 for pp in pl['pivots']:
  p=pp['pivot'];assert c['start'][p]==0;c['start'][p]=f;c['ext'].append([p,f])
  for d,a in sorted(pp['coefficients'].items(),key=lambda x:int(x[0])):
   d=int(d);a=Q(a)
   for _ in range(abs(a.numerator)):head.append(['in',f,d,[[p,1 if a>0 else -1,a.denominator]]])
c['ext'].sort();c['A']=head+c['A']
cur=c['start'][:];changed=[]
for part in ['A','B']:
 if part=='B':
  for _,r,f in c['ret']:assert cur[r]==f,'fixed retained snapshot frame'
 for i,g in enumerate(c[part]):
  roles=[g[2]]+[z[0] for z in g[3]]+(g[4] if len(g)>4 else [])
  union=canonical(c['frames'][g[1]]+[u for r in roles for u in c['frames'][cur[r]]])
  if not Re.inside(union,c['frames'][g[1]]):
   old=g[1];nf=next((j for j,z in enumerate(c['frames']) if len(z)==len(union) and Re.inside(union,z)),len(c['frames']))
   if nf==len(c['frames']):c['frames'].append(union)
   g[1]=nf;changed.append(dict(part=part,index=i,old=old,new=nf,basis=union,roles=roles))
  for r in roles:cur[r]=g[1]
for r in range(len(cur)):assert Re.inside(c['frames'][cur[r]],c['frames'][c['final'][r]])
Re.rehist_and_audit(c)
for tag in ['whole','before_snapshot']:
 old=copy.deepcopy(b);new=copy.deepcopy(c)
 if tag=='before_snapshot':
  for z in [old,new]:z['B']=[];z['scat']['table']=[[] for _ in range(z['v'])]
 wanted=Re.replay(old);actual=Re.replay(new)
 for g in reversed(head):
  d=g[2];p,a,z=g[3][0];q=Q(a,z)
  for row in wanted:
   v=row.get(p,Q(0))+q*row.get(d,Q(0))
   if v:row[p]=v
   else:row.pop(p,None)
 assert actual==wanted,tag
 if tag=='whole':assert all(p not in actual[t] for p,_ in c['ext'] for t in range(c['v'],2*c['v']))
controls=[]
for change in changed:
 bad=copy.deepcopy(c);bad[change['part']][change['index']][1]=change['old'];rejected=False
 try:Re.rehist_and_audit(bad)
 except AssertionError as exc:rejected=True;reason=str(exc)
 assert rejected,'reverting required propagated frame must fail full label walk'
 controls.append(dict(name='revert_required_propagated_frame',part=change['part'],index=change['index'],rejected=True,reason=reason))
bad=copy.deepcopy(c);bad['A'].pop(0);rawbad=Re.replay(bad)
leaks=[(t,p) for p,_ in c['ext'] for t in range(c['v'],2*c['v']) if rawbad[t].get(p,Q(0))]
assert leaks,'omitting new entrance gate must leak gauged dirt'
controls.append(dict(name='omit_first_new_entrance_gate',rejected=True,raw_gauged_leak_witness=leaks[0]))
blob=json.dumps(c,sort_keys=True,separators=(',',':')).encode();(root/'candidate.json').write_bytes(blob)
if args.expected_sha256:assert hashlib.sha256(blob).hexdigest()==args.expected_sha256
a=Re.histogram(c);a.subtract(Re.histogram(b));delta={r:v for r,v in a.items() if v}
receipt=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(blob).hexdigest(),gauges=len(c['ext']),new_gates=len(head),selection=plans,adverse_controls=controls,changed_original_frames=changed,local_delta=delta,paid_profile=dict(Re.histogram(c)),all1021raw_and_snapshot_columns_right_multiplied_by_literal_prepended_word=True,all_gauged_response_columns_zero=True)
(root/'RECEIPT.json').write_text(json.dumps(receipt,indent=2));(root/'SELECTION.json').write_text(json.dumps(plans,indent=2));print(json.dumps(receipt,indent=2))
