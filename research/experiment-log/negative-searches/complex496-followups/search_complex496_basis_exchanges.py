"""Rational pivot/donor swaps, then exact common-entrance promotion on PR484."""
from pathlib import Path
from collections import Counter
from functools import lru_cache
import json,gzip,sys,copy,time,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
O=R/'complex496-basis-search';O.mkdir(exist_ok=False)
W=json.load(gzip.open(R/'complex496-entrance-search/BASE-WORD.json.gz'));S=json.load(open(R/'complex496-entrance-search/BASE-SELECTION.json'));C=G.responses(W);F=G.first_frames(W);SP={h:G.span(E) for h,E in F.items()};orig=G.solve_relation
G.responses=lambda _:C;G.first_frames=lambda _:F
@lru_cache(None)
def relation(ds,p):return orig(C,list(ds),p)
G.solve_relation=lambda c,ds,p:relation(tuple(ds),p)
def split(sel,promote):
 s=copy.deepcopy(sel);classes=[]
 for c in s['kernel']:
  for p in c['pivots']:
   ds=sorted(relation(tuple(c['donors']),p));E=c['E']
   if promote:E=list(G.basis(sorted(set.intersection(*(SP[h] for h in ds+[p]))-{0})))
   classes.append(dict(E=E,donors=ds,pivots=[p]))
 s['kernel']=classes;return s
seen={};ledger=[];start=time.monotonic()
def attempt(label,sel,meta):
 try:
  candidate=split(sel,True);w=G.build(W,candidate);prof=w['report']['local_profile'];widths=Counter(G.widths_of(w));rank=w['report']['entrance_rank'];sig=json.dumps([prof,sorted(widths.items())],sort_keys=True)
  row=dict(label=label,status='PASS_LOCAL_CONSTRUCTOR_ONLY',profile=prof,width_counts=dict(widths),rank=rank,**meta)
  if sig in seen:row['profile_duplicate_of']=seen[sig]
  else:
   seen[sig]=label;d=O/label;d.mkdir();(d/'SELECTION.json').write_text(json.dumps(candidate,indent=2)+'\n');(d/'WORD.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));(d/'RESULT.json').write_text(json.dumps(row,indent=2)+'\n')
 except AssertionError as e:row=dict(label=label,status='REJECTED_LOCAL_CONSTRUCTOR',error=str(e),**meta)
 ledger.append(row)
 if len(ledger)%20==0:print('trials',len(ledger),'profiles',len(seen),'maxrank',max(x.get('rank',0) for x in ledger),'seconds',time.monotonic()-start,flush=True)
attempt('baseline',S,{})
for j,c in enumerate(S['kernel']):
 for p in c['pivots']:
  for d in sorted(relation(tuple(c['donors']),p)):
   sel=copy.deepcopy(S);k=sel['kernel'][j];k['donors']=sorted((set(k['donors'])-{d})|{p});k['pivots']=sorted((set(k['pivots'])-{p})|{d});attempt(f'swap-{j}-{p}-{d}',sel,dict(group=j,old_pivot=p,old_donor=d))
(O/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');(O/'COMPLETE.json').write_text(json.dumps(dict(trials=len(ledger),profiles=len(seen),maxrank=max(x.get('rank',0) for x in ledger),seconds=time.monotonic()-start),indent=2)+'\n');print('COMPLETE',len(ledger),len(seen),flush=True)
