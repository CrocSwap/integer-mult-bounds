"""Trade gauge roles for existing kernel79 response relations on the retimed core."""
from pathlib import Path
from functools import lru_cache
from collections import Counter
import json,gzip,sys,copy,time,itertools
R=Path(__file__).resolve().parent;O=R/'complex501-kernel-gauge-trades';O.mkdir(exist_ok=False);sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
W=json.load(gzip.open(R/'pr501-retimed-bare-core.json.gz'));S=json.load(open(R/'complex496-entrance-search/BASE-SELECTION.json'));K=json.load(open(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/data/selections/kernel79.json'))['kernel'];C=G.responses(W);F=G.first_frames(W);orig=G.solve_relation;G.responses=lambda _:C;G.first_frames=lambda _:F
@lru_cache(None)
def rel(ds,p):return orig(C,list(ds),p)
G.solve_relation=lambda c,ds,p:rel(tuple(ds),p)
oldp={p for c in S['kernel'] for p in c['pivots']};ledger=[];seen={};t0=time.monotonic();solo=[]
for c in K:
 for p in c['pivots']:
  ds=sorted(rel(tuple(c['donors']),p));solo.append(dict(E=c['E'],donors=ds,pivots=[p]))
def test(label,new):
 s=copy.deepcopy(S);np={p for c in new for p in c['pivots']};nd={d for c in new for d in c['donors']};removed=[h for h in s['gauge'] if int(h) in np|nd]
 for h in removed:s['gauge'].pop(h)
 keep=[];removed_p=[]
 for c in s['kernel']:
  for p in c['pivots']:
   ds=sorted(rel(tuple(c['donors']),p))
   if p in np|nd or set(ds)&np:removed_p.append(p)
   else:keep.append(dict(E=c['E'],donors=ds,pivots=[p]))
 s['kernel']=keep+new
 try:
  w=G.build(W,s);profile=w['report']['local_profile'];wc=dict(Counter(G.widths_of(w)));sig=json.dumps([profile,sorted(wc.items())],sort_keys=True);row=dict(label=label,status='PASS_LOCAL_CONSTRUCTOR_ONLY',profile=profile,width_counts=wc,rank=w['report']['entrance_rank'],removed_gauges=removed,removed_pivots=removed_p,new_pivots=sorted(np))
  if sig in seen:row['duplicate_profile_of']=seen[sig]
  else:
   seen[sig]=label;d=O/label;d.mkdir();(d/'SELECTION.json').write_text(json.dumps(s,indent=2)+'\n');(d/'WORD.json.gz').write_bytes(G.dump(w));(d/'RESULT.json').write_text(json.dumps(row,indent=2)+'\n');print('NEW',row,flush=True)
 except AssertionError as e:row=dict(label=label,status='REJECTED_LOCAL_CONSTRUCTOR',error=str(e),removed_gauges=removed,removed_pivots=removed_p,new_pivots=sorted(np))
 ledger.append(row)
test('baseline',[])
for c in solo:test('pivot-'+str(c['pivots'][0]),[c])
for j,c in enumerate(K):test('class-'+str(j),[c])
for a,z in itertools.combinations(range(len(K)),2):test('classes-'+str(a)+'-'+str(z),[K[a],K[z]])
test('all-kernel79',K)
(O/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');result=dict(trials=len(ledger),profiles=len(seen),outcomes=dict(Counter(x['status'] for x in ledger)),seconds=time.monotonic()-t0);(O/'COMPLETE.json').write_text(json.dumps(result,indent=2)+'\n');print('COMPLETE',result,flush=True)
