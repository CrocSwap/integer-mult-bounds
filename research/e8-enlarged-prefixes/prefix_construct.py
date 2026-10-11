"""OpenAI Codex 2026-10-11: bounded donor-prefix rewrite on PR404 +206gauges + PR402 composition.
Reuses Chafik Boukhalfa PR402 prefix-window search idea and block accounting;
actual recipes and dirty response are independently replayed here. Apache-2.0.
No gx E5 assertion: quarter/eighth coefficients require the explicit native lowerer.
"""
import argparse,copy,hashlib,json
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
SOURCE_SHA256='76e3feb95b537bc50d50342361f8c9f36248ba716cde8ce8aed97d9d4634065d'
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);parser.add_argument('output',type=Path);a=parser.parse_args()
assert not a.output.exists();blob=a.source.read_bytes();assert hashlib.sha256(blob).hexdigest()==SOURCE_SHA256;c=json.loads(blob);d=copy.deepcopy(c)
# Position is immediately after the preceding original A+B gate; prefixes end
# before the first positive-frame target-source read. All zero-frame source reads
# precede these deliveries. Empty source touches preserve inherited helper walks.
plans=[dict(target=144,cut=1238,deliveries=[(2018,311,255,-1,4),(3125,935,777,-3,8),(3126,935,808,-1,4)]),dict(target=124,cut=1171,deliveries=[(2024,336,563,1,2)])]
at={};cuts={};nA=len(c['A'])
for p in plans:
 r=p['target'];cuts[r]=p['cut']
 assert c['B'][p['cut']][1]>0
 assert any(src==r for src,aa,bb in c['B'][p['cut']][3])
 for pos,f,s,aa,bb in p['deliveries']:
  assert not c['v']<=s<2*c['v']
  at.setdefault(pos,[]).append(['in',f,r,[[s,aa,bb]]])
B=[]
for bi,g in enumerate(c['B']):
 if g[0]=='in' and g[2] in cuts and bi<cuts[g[2]]:
  B.extend(['out',g[1],src,[],[]] for src,aa,bb in g[3])
 else:B.append(copy.deepcopy(g))
 B.extend(sorted(at.get(nA+bi+1,[]),key=lambda g:len(c['frames'][g[1]])))
d['B']=B
# Exact block histogram; native admission independently replays both frame ledgers.
v,R=d['v'],d['R'];n=2*v+R;dim=[len(f) for f in d['frames']];cur=list(d['start']);H={k:Counter() for k in ['x','y','s','c']}
def climb(r,f):
 if cur[r]!=f:
  rank=dim[f]-dim[cur[r]];assert rank>=0;H['x' if r<v else 'y' if r<2*v else 's'][rank]+=1;cur[r]=f
for ph in ['A','B']:
 if ph=='B':
  for k,src,f in d['ret']:H['c'][dim[f]]+=1
 for g in d[ph]:
  for r in [g[2]]+[t for t,aa,bb in g[3]]+(list(g[4]) if g[0]=='out' else []):climb(r,g[1])
for r in range(n):climb(r,d['final'][r])
d['blocks']={k:{str(r):x for r,x in sorted(w.items())} for k,w in H.items()};d['N']=sum(r*x for w in H.values() for r,x in w.items())
def operator(z):
 rows=[{i:Q(1)} for i in range(n)];tot=None
 def ax(t,src,q):
  for k,aa in list(src.items()):
   x=rows[t].get(k,Q(0))+q*aa
   if x:rows[t][k]=x
   else:rows[t].pop(k,None)
 for ph in ['A','B']:
  if ph=='B':
   tot={k:dict(rows[src]) for k,src,f in z['ret']}
   for t,es in enumerate(z['scat']['table']):
    for k,aa,bb in es:ax(v+t,tot[k],Q(aa,bb))
  for g in z[ph]:
   if g[0]=='out':
    src=dict(rows[g[2]])
    for t,aa,bb in g[3]:ax(t,src,Q(aa,bb))
   else:
    for src,aa,bb in g[3]:ax(g[2],dict(rows[src]),Q(aa,bb))
 return rows,tot
old,oldtot=operator(c);new,newtot=operator(d);ext=dict(d['ext'])
protected=lambda row:{k:q for k,q in row.items() if k<2*v or k in ext}
assert oldtot==newtot and all(protected(x)==protected(y) for x,y in zip(old,new))
assert all(old[r]==new[r] for r in list(range(v))+list(range(2*v,n)))
assert all(new[v+t].get(r,Q(0))==0 for t in range(v) for r in ext)
assert all({k:q for k,q in new[v+t].items() if v<=k<2*v}=={v+t:Q(1)} for t in range(v))
changes=[]
for t in range(v,2*v):
 for r in sorted(set(old[t])|set(new[t])):
  x=new[t].get(r,Q(0))-old[t].get(r,Q(0))
  if x:assert r>=2*v and r not in ext;changes.append([t,r,x.numerator,x.denominator])
delta=Counter()
for w in d['blocks'].values():delta.update({int(r):n for r,n in w.items()})
for w in c['blocks'].values():delta.subtract({int(r):n for r,n in w.items()})
assert {r:n for r,n in delta.items() if n}=={1:-1,3:-1,4:1}
a.output.mkdir(parents=True);blob=json.dumps(d,sort_keys=True,separators=(',',':')).encode();(a.output/'candidate.json').write_bytes(blob)
receipt=dict(status='PASS_PROTECTED_PREFIX_REWRITE_WITH_EXPLICIT_REOPENED_DIRTY_RESPONSE',source_sha256=SOURCE_SHA256,candidate_sha256=hashlib.sha256(blob).hexdigest(),plans=plans,all_columns=1021,raw_operator_equals_source=False,raw_protected_X_Y_gauged_helper_columns_equal=True,helper_cleanup_operator_equal=True,nongauged_dirty_changes=changes,local_histogram_delta={r:n for r,n in delta.items() if n},gx_sixths_admission_claim=False,requires='Native recomputed K, explicit coefficient words, symbolic dirty restoration, both reflected frame ledgers, phase, complete paid banks/outer assembly')
(a.output/'RECEIPT.json').write_text(json.dumps(receipt,indent=2));print(receipt['status'],receipt['candidate_sha256'])
