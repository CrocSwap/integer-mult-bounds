"""Gauge entrances intersected with actual served-centre frames, then coordinated replacements."""
from pathlib import Path
from functools import lru_cache
from collections import Counter,defaultdict
import json,gzip,sys,copy,time,hashlib
R=Path(__file__).resolve().parent;O=R/'complex496-gauge-intersections';O.mkdir(exist_ok=False);sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
W=json.load(gzip.open(R/'complex496-entrance-search/BASE-WORD.json.gz'));S=json.load(open(R/'complex496-entrance-search/BASE-SELECTION.json'));C=G.responses(W);F=G.first_frames(W);orig=G.solve_relation
G.responses=lambda _:C;G.first_frames=lambda _:F
@lru_cache(None)
def rel(ds,p):return orig(C,list(ds),p)
G.solve_relation=lambda c,ds,p:rel(tuple(ds),p)
served=defaultdict(set);cf={r:G.span(E) for r,E in zip(W['centers'],W['center_frames'])}
for e in W['cut']:served[e[1]-120].add(e[2])
cs={h:set.union(*(served[t] for t in col)) if col else set() for h,col in enumerate(C)}
allowed={h:G.span(E).intersection(*(cf[r] for r in cs[h])) for h,E in F.items()}
maxE={h:list(G.basis(sorted(a-{0}))) for h,a in allowed.items()}
used={h for c in S['kernel'] for h in c['donors']+c['pivots']};ledger=[];seen={};t0=time.monotonic()
def test(label,sel,meta):
 try:
  w=G.build(W,sel);profile=w['report']['local_profile'];wc=dict(Counter(G.widths_of(w)));sig=json.dumps([profile,sorted(wc.items())],sort_keys=True)
  row=dict(label=label,status='PASS_LOCAL_CONSTRUCTOR_ONLY',profile=profile,width_counts=wc,entrance_rank=w['report']['entrance_rank'],**meta)
  if sig in seen:row['duplicate_profile_of']=seen[sig]
  else:
   seen[sig]=label;d=O/label;d.mkdir();(d/'SELECTION.json').write_text(json.dumps(sel,indent=2)+'\n');(d/'WORD.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));(d/'RESULT.json').write_text(json.dumps(row,indent=2)+'\n');print('NEW',row,flush=True)
 except AssertionError as e:row=dict(label=label,status='REJECTED_LOCAL_CONSTRUCTOR',error=str(e),**meta)
 ledger.append(row);return row
base=test('baseline',S,{})
# Intersecting centre endpoints is less permissive than raw first-frame promotion,
# but often yields a legal proper subspace where the first-frame trial was rejected.
for h,E in maxE.items():
 if h in used or not E:continue
 if E==S['gauge'].get(str(h)):continue
 s=copy.deepcopy(S);s['gauge'][str(h)]=E;test('max-'+str(h),s,dict(helper=h))
# Coherent centre-wide gauge reset to one common line. Restore all eligible helpers
# on that line, then let the full constructor reject any remaining centre/target conflicts.
lines=sorted(set(v for h,a in allowed.items() if h not in used for v in a-{0}))
for v in lines:
 eligible={h for h,a in allowed.items() if h not in used and v in a};touched=set.union(*(cs[h] for h in eligible)) if eligible else set()
 s=copy.deepcopy(S);s['gauge']={h:E for h,E in S['gauge'].items() if not(cs[int(h)]&touched)}
 for h in eligible:s['gauge'][str(h)]=[v]
 test('line-reset-'+str(v),s,dict(line=v,eligible=len(eligible),centres=len(touched)))
(O/'GEOMETRY.json').write_text(json.dumps(dict(allowed_entrances={str(h):e for h,e in maxE.items()},centre_incidence={str(h):sorted(v) for h,v in cs.items()}),indent=2)+'\n');(O/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');(O/'COMPLETE.json').write_text(json.dumps(dict(trials=len(ledger),profiles=len(seen),seconds=time.monotonic()-t0),indent=2)+'\n');print('COMPLETE',len(ledger),len(seen),flush=True)
