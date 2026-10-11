from pathlib import Path
from collections import Counter
import json,hashlib
O=Path(__file__).resolve().parent;ROOT=O.parents[2];P=ROOT/'experiments/architecture/whole-owner-pooling-v4/bit60';B=ROOT/'experiments/architecture/pr454-signed-extra-v4/with-prefix60';N=json.load(open(P/'NOMINATION.json'));S=N['schedule'];local={e['stage']:i for i,e in enumerate(S)if e['kind']=='local'};active={e['stage']:e['pair']for e in S if e['kind']=='local'}
last={j:-1 for j in range(5)};windows={};children={}
for pos,e in enumerate(S):
 k=e['kind']
 if k=='idle':
  p=e['pair'];i=e['idx'];eligible=[s for s,t in local.items()if last[p]<t<pos and active[s]!=p];windows[i]=(p,e['rank'],eligible);children[i]=e
  last[p]=pos
 elif k=='local':last[e['pair']]=pos
 elif k=='bridge':
  last[e['src']]=last[e['dst']]=pos
windows={k:v for k,v in windows.items()if v[1] and v[2]}
assert {str(k):[p,r,s]for k,(p,r,s)in windows.items()}==N['windows']
st=json.load(open(B/'records/249-states.json'));F=json.load(open(B/'records/frames.json'))['frames'];width={h:8-F[str(st['initial'][str(240+h)])]['dim']for h in range(740)}
assert Counter(width.values())==Counter({8:645,7:87,4:8})
seen=set();occupied=set();foreign=0;ownerfamilies=set();remaining={(i,cp):r for i,(p,r,s)in windows.items()for cp in range(1920)}
for i,cp,off,w,stage,h in N['slots']:
 rep,helper=divmod(h,740);ownerrep,within=divmod(cp,240);side,port=divmod(within,120);p,r,ss=windows[i]
 assert 0<=rep<8 and 0<=ownerrep<8 and stage in ss and w==width[helper] and 0<=off<=r-w
 assert (stage,h)not in seen;seen.add((stage,h));foreign+=rep!=ownerrep
 family=ownerrep*1200+p*240+within;ownerfamilies.add(family)
 for x in range(off,off+w):
  key=(i,family,x);assert key not in occupied;occupied.add(key)
 remaining[i,cp]-=w
assert seen=={(s,h)for s in range(11)for h in range(8*740)}
assert all(r>=0 for r in remaining.values())
H=Counter({r:0 for r in []});G=json.load(open(B/'global/hosted/GLOBAL.json'))
for ori,n in [('forward',48),('reverse',40)]:
 for r,c in G['local_checks'][ori]['profile'].items():H[int(r)]+=n*c
for r in remaining.values():
 if r:H[r]+=1
assert dict(sorted(H.items()))=={int(k):v for k,v in N['profile'].items()}
assert sum(r*n for r,n in H.items())==745536 and 78*9600-sum(r*n for r,n in H.items())==3264
out={'status':'PASS_INDEPENDENT_ACTUAL60_WHOLE_POOLED_ASSIGNMENT_WINDOWS_PROFILE','slots':len(seen),'foreign_replica_assignments':foreign,'occupied_child_axes':len(occupied),'profile':dict(sorted(H.items())),'rankmass':745536,'deficit':3264,'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [P/'NOMINATION.json',B/'records/249-states.json',B/'records/frames.json',B/'global/hosted/GLOBAL.json']},'scope':'Whole VALUE helper assignment and replica/physical-family window/profile checks. Actual sigma cover-row injectivity, literal emitted program, reflected operator inverse, full arbitrary-correlated-dirt compiler endpoint, extra route-selector fee and complete moment/assembly remain separate gates. Complete stage sweeps precede next schedule event; activepair excluded on everyreplica.'}
(O/'WHOLE-POOL60-BIT-ASSIGNMENT.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],foreign)
