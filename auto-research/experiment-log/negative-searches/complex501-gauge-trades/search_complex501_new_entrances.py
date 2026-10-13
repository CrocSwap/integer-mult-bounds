"""New entrance opportunities exposed by PR501's retimed bare scalar core."""
from pathlib import Path
from functools import lru_cache
from collections import Counter,defaultdict
from fractions import Fraction
import json,gzip,sys,copy,time,hashlib
R=Path(__file__).resolve().parent;O=R/'complex501-new-entrances';O.mkdir(exist_ok=False);sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
W=json.load(gzip.open(R/'pr501-retimed-bare-core.json.gz'));OLD=json.load(gzip.open(R/'complex496-entrance-search/BASE-WORD.json.gz'));S=json.load(open(R/'complex496-entrance-search/BASE-SELECTION.json'));C=G.responses(W);F=G.first_frames(W);F0=G.first_frames(OLD);SP={h:G.span(e) for h,e in F.items()};orig=G.solve_relation;G.responses=lambda _:C;G.first_frames=lambda _:F
@lru_cache(None)
def rel(ds,p):return orig(C,list(ds),p)
G.solve_relation=lambda c,ds,p:rel(tuple(ds),p)
ledger=[];seen={};t0=time.monotonic()
def trial(label,s,meta={}):
 try:
  w=G.build(W,s);profile=w['report']['local_profile'];widths=dict(Counter(G.widths_of(w)));sig=json.dumps([profile,sorted(widths.items())],sort_keys=True);row=dict(label=label,status='PASS_LOCAL_CONSTRUCTOR_ONLY',profile=profile,width_counts=widths,rank=w['report']['entrance_rank'],**meta)
  if sig in seen:row['duplicate_profile_of']=seen[sig]
  else:
   seen[sig]=label;d=O/label;d.mkdir();(d/'SELECTION.json').write_text(json.dumps(s,indent=2)+'\n');(d/'WORD.json.gz').write_bytes(G.dump(w));(d/'RESULT.json').write_text(json.dumps(row,indent=2)+'\n');print('NEW',row,flush=True)
 except AssertionError as e:row=dict(label=label,status='REJECTED_LOCAL_CONSTRUCTOR',error=str(e),**meta)
 ledger.append(row);return row
trial('baseline',S)
used={int(h) for h in S['gauge']}|{h for c in S['kernel'] for h in c['donors']+c['pivots']};pivots={h for c in S['kernel'] for h in c['pivots']};donors={h for c in S['kernel'] for h in c['donors']}
served=defaultdict(set);cf={r:G.span(E) for r,E in zip(W['centers'],W['center_frames'])}
for e in W['cut']:served[e[1]-120].add(e[2])
cs={h:set.union(*(served[t] for t in col)) if col else set() for h,col in enumerate(C)}
for h in F:
 if F[h]==F0[h] or h in pivots|donors:continue
 allowed=SP[h].intersection(*(cf[r] for r in cs[h]));E=list(G.basis(sorted(allowed-{0})))
 if not E or E==S['gauge'].get(str(h)):continue
 s=copy.deepcopy(S);s['gauge'][str(h)]=E;trial('gauge-'+str(h),s,dict(helper=h))
# Greedy exact rational response bases for lines newly exposed by retiming.
lines=sorted(set.union(*(SP[h]-G.span(F0[h]) for h in F if F[h]!=F0[h])))
def response_basis(hs):
 basis={};selected=[];dependent=[]
 for h in hs:
  col=dict(C[h])
  for t,(v,d) in sorted(basis.items()):
   if t not in col:continue
   q=col[t]
   for k,c in v.items():
    z=col.get(k,Fraction(0))-q*c
    if z:col[k]=z
    else:col.pop(k,None)
  if col:
   t=min(col);q=col[t];basis[t]=({k:c/q for k,c in col.items()},h);selected.append(h)
  else:dependent.append(h)
 return selected,dependent
for v in lines:
 eligible=[h for h in F if h not in used and v in SP[h]]
 if len(eligible)<2:continue
 for order in ['ascending','descending','low-rank-first']:
  hs=sorted(eligible,reverse=order=='descending') if order!='low-rank-first' else sorted(eligible,key=lambda h:(len(F[h]),h));ds,ps=response_basis(hs)
  if not ps:continue
  s=copy.deepcopy(S);s['kernel'].append(dict(E=[v],donors=ds,pivots=ps));trial('kernel-'+str(v)+'-'+order,s,dict(line=v,new_donors=len(ds),new_pivots=len(ps)))
(O/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');result=dict(trials=len(ledger),profiles=len(seen),lines=len(lines),outcomes=dict(Counter(x['status'] for x in ledger)),seconds=time.monotonic()-t0);(O/'COMPLETE.json').write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True)
