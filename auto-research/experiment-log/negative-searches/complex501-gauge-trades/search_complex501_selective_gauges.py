"""Replace only centre/target-conflicting gauges on PR501's retimed core.
This searches a new neighborhood; no global optimality or admission is claimed.
"""
from pathlib import Path
from functools import lru_cache
from collections import Counter,defaultdict
import json,gzip,sys,copy,time
R=Path(__file__).resolve().parent;O=R/'complex501-selective-gauges';O.mkdir(exist_ok=False);sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
W=json.load(gzip.open(R/'pr501-retimed-bare-core.json.gz'));S=json.load(open(R/'complex496-entrance-search/BASE-SELECTION.json'));C=G.responses(W);F=G.first_frames(W);orig=G.solve_relation;G.responses=lambda _:C;G.first_frames=lambda _:F
@lru_cache(None)
def rel(ds,p):return orig(C,list(ds),p)
G.solve_relation=lambda c,ds,p:rel(tuple(ds),p)
served=defaultdict(set);cf={r:G.span(E) for r,E in zip(W['centers'],W['center_frames'])}
for e in W['cut']:served[e[1]-120].add(e[2])
cs={h:set.union(*(served[t] for t in col)) if col else set() for h,col in enumerate(C)};targets={h:set(col) for h,col in enumerate(C)};allowed={h:G.span(E).intersection(*(cf[r] for r in cs[h])) for h,E in F.items()};used={h for c in S['kernel'] for h in c['donors']+c['pivots']};old={int(h):G.basis(e) for h,e in S['gauge'].items()};oldspan={h:G.span(e) for h,e in old.items()};ledger=[];seen={};t0=time.monotonic()
def test(label,sel,meta):
 try:
  w=G.build(W,sel);profile=w['report']['local_profile'];wc=dict(Counter(G.widths_of(w)));sig=json.dumps([profile,sorted(wc.items())],sort_keys=True);row=dict(label=label,status='PASS_LOCAL_CONSTRUCTOR_ONLY',profile=profile,width_counts=wc,rank=w['report']['entrance_rank'],**meta)
  if sig in seen:row['duplicate_profile_of']=seen[sig]
  else:
   seen[sig]=label;d=O/label;d.mkdir();(d/'SELECTION.json').write_text(json.dumps(sel,indent=2)+'\n');(d/'WORD.json.gz').write_bytes(G.dump(w));(d/'RESULT.json').write_text(json.dumps(row,indent=2)+'\n');print('NEW',row,flush=True)
 except AssertionError as e:row=dict(label=label,status='REJECTED_LOCAL_CONSTRUCTOR',error=str(e),**meta)
 ledger.append(row)
test('baseline',S,{})
for h in sorted(F):
 if h in used:continue
 candidates={G.basis(sorted(allowed[h]-{0}))}|{(v,) for v in allowed[h]-{0}}
 # Existing compatible geometry supplies larger intermediate subspaces too.
 candidates|={e for e in old.values() if G.span(e)<=allowed[h]}
 for E in sorted(candidates):
  if not E or E==old.get(h):continue
  sp=G.span(E);removed=[g for g in old if g!=h and (cs[h]&cs[g] or targets[h]&targets[g]) and not(sp<=oldspan[g] or oldspan[g]<=sp)]
  s=copy.deepcopy(S)
  for g in removed:s['gauge'].pop(str(g))
  s['gauge'][str(h)]=list(E)
  test('h'+str(h)+'-e'+'-'.join(map(str,E)),s,dict(helper=h,entrance=list(E),removed=removed,entrance_rank_delta=len(E)-len(old.get(h,()))-sum(len(old[g]) for g in removed)))
(O/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');result=dict(trials=len(ledger),profiles=len(seen),seconds=time.monotonic()-t0,outcomes=dict(Counter(x['status'] for x in ledger)));(O/'COMPLETE.json').write_text(json.dumps(result,indent=2)+'\n');print('COMPLETE',result,flush=True)
