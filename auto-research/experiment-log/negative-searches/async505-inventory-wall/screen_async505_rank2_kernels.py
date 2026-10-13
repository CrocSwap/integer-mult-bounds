"""Exhaustive rank-two entrance screen on the retimed bare core.
Full modular column rank proves no rational dependence; deficient sets are
checked exactly before any candidate is reported. No higher-rank screen claimed.
"""
from pathlib import Path
from collections import defaultdict,Counter
from fractions import Fraction as Q
from itertools import combinations
import json,gzip,sys,time
R=Path(__file__).resolve().parent;O=R/'async505-rank2-kernel-screen';O.mkdir(exist_ok=False);sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
W=json.load(gzip.open(R/'pr501-retimed-bare-core.json.gz'));F=G.first_frames(W);C=G.responses(W);S=json.load(open(R/'complex496-entrance-search/BASE-SELECTION.json'));gauges={int(h)for h in S['gauge']};prime=1000003;planes=defaultdict(set);start=time.monotonic()
for h,E in F.items():
 vectors=sorted(G.span(E)-{0});seen=set()
 for a,b in combinations(vectors,2):
  q=tuple(sorted((a,b,a^b))[:2])
  if q not in seen:planes[q].add(h);seen.add(q)
mod=[{r:(v.numerator*pow(v.denominator,-1,prime))%prime for r,v in col.items()}for col in C]
def basis(ids,exact=False):
 piv={};donors=[];dependent=[]
 for h in ids:
  col=dict(C[h]if exact else mod[h])
  for r,p in sorted(piv.items()):
   x=col.get(r,0)
   if x:
    for t,v in p.items():
     z=col.get(t,0)-x*v
     if not exact:z%=prime
     if z:col[t]=z
     else:col.pop(t,None)
  if not col:dependent.append(h);continue
  r=min(col);x=col[r];piv[r]={t:(v/x if exact else v*pow(x,-1,prime)%prime)for t,v in col.items()};donors.append(h)
 return donors,dependent
cache={};rows=[];positives=[]
for mode in ['retain-gauges','all-helpers']:
 counts=Counter()
 for E,hh in sorted(planes.items()):
  ids=tuple(sorted(hh-gauges if mode=='retain-gauges'else hh))
  if len(ids)<2:counts['too_few_columns']+=1;continue
  if ids not in cache:
   ds,ps=basis(ids)
   if ps:ds,ps=basis(ids,True)
   cache[ids]=(ds,ps)
  ds,ps=cache[ids];counts['exact_dependent'if ps else'full_column_rank']+=1
  if ps:positives.append(dict(mode=mode,E=list(E),eligible=list(ids),donors=ds,pivots=ps,nullity=len(ps)))
 rows.append(dict(mode=mode,counts=dict(counts)));print(rows[-1],flush=True)
(O/'DEPENDENCIES.json').write_text(json.dumps(positives,indent=2)+'\n');res=dict(status='COMPLETE_RANK_TWO_ENTRANCE_DEPENDENCY_SCREEN',planes=len(planes),distinct_column_sets=len(cache),modes=rows,dependencies=len(positives),seconds=time.monotonic()-start,prime=prime,scope='All two-dimensional binary subspaces contained in retimed first frames. Modular full rank is a rational-independence witness because every response denominator is invertible modulo the recorded prime; every deficient set is reranked with exact fractions. No claim about other local words, scalar reorderings or new response maps.');(O/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(res,flush=True)
