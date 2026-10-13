"""Single donor/pivot basis exchanges on the retimed baseline kernel classes.
The same entrance-count inventory is preserved; finite physical admission is separate.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from functools import lru_cache
import json,gzip,sys,copy,math,time
R=Path(__file__).resolve().parent;O=R/'async505-donor-exchanges';O.mkdir(exist_ok=False);sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
W=json.load(gzip.open(R/'pr501-retimed-bare-core.json.gz'));S=json.load(open(R/'complex496-entrance-search/BASE-SELECTION.json'));C=G.responses(W);F=G.first_frames(W);orig=G.solve_relation;G.responses=lambda _:C;G.first_frames=lambda _:F
@lru_cache(None)
def rel(ds,p):return orig(C,list(ds),p)
G.solve_relation=lambda c,ds,p:rel(tuple(ds),p)
b=float(Q(json.load(open(R/'async505-order24-realized/audit/EXACT-ASSEMBLY.json'))['complex_lower']));m=73;cost=lambda r:r*math.expm1(b*math.log(m/r))/b+32*m*m/1e16*m**b/b;score=lambda H:sum(n*cost(int(r))for r,n in H.items());base=G.build(W,S);baseval=score(base['report']['local_profile']);bestval=baseval;wc=Counter(G.widths_of(base));ledger=[];moves=[];start=time.monotonic()
for sweep in range(3):
 best=None
 for ci,c in enumerate(S['kernel']):
  for d in c['donors']:
   for p in c['pivots']:
    sel=copy.deepcopy(S);z=sel['kernel'][ci];z['donors']=sorted((set(c['donors'])-{d})|{p});z['pivots']=sorted((set(c['pivots'])-{p})|{d});row=dict(sweep=sweep,cl=ci,donor=d,pivot=p)
    try:
     w=G.build(W,sel);hh=w['report']['local_profile'];assert Counter(G.widths_of(w))==wc;value=score(hh);row.update(status='PASS_LOCAL_CONSTRUCTOR_ONLY',cost=value,gain_over_baseline=baseval-value,profile=hh)
     if value<bestval-1e-7 and (best is None or value<best[0]):best=(value,sel,w,row)
    except AssertionError as e:row.update(status='REJECTED_LOCAL_CONSTRUCTOR',error=str(e))
    ledger.append(row)
 if best is None:break
 bestval,S,w,row=best;moves.append(row);d=O/('move-'+str(len(moves)));d.mkdir();(d/'SELECTION.json').write_text(json.dumps(S,indent=2)+'\n');(d/'WORD.json.gz').write_bytes(G.dump(w));(d/'RESULT.json').write_text(json.dumps(row,indent=2)+'\n');print('MOVE',row,flush=True)
(O/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');res=dict(status='COMPLETE_BOUNDED_DONOR_PIVOT_EXCHANGES',trials=len(ledger),outcomes=dict(Counter(r['status']for r in ledger)),moves=moves,baseline_cost=baseval,best_cost=bestval,gain=baseval-bestval,seconds=time.monotonic()-start,scope='Fixed response map and kernel classes, gauge palette retained. Single-exchange neighborhood and at most three improving sweeps; floating local objective and constructor checks only. No physical, global or optimality claim.');(O/'COMPLETE.json').write_text(json.dumps(res,indent=2)+'\n');print(res,flush=True)
