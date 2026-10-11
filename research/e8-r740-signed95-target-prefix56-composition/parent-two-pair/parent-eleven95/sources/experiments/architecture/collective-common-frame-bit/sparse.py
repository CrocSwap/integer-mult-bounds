"""Exact collective common-frame low-paid-cost integer relations."""
import runpy,json,itertools
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;q=runpy.run_path(str(R/'experiments/architecture/odd-coefficient-kernel/solve.py'));K=q['K'];co=json.load(open(O/'COHORTS.json'))['cohorts'];out=[]
for e in co:
 pool=e['pool'];entries=[]
 for d in pool:
  for c in(-2,-1,1,2):entries.append((tuple(c*x for x in K[d]),d,c))
 index={}
 for v,d,c in entries:index.setdefault(v,[]).append((d,c))
 for p in e['pivots']:
  target=tuple(K[p]);found=[]
  if not any(target):found.append([])
  for d,c in index.get(target,[]):
   if d!=p:found.append([(d,c)])
  for v,d,c in entries:
   if d==p:continue
   rest=tuple(x-y for x,y in zip(target,v))
   for a,b in index.get(rest,[]):
    if a not in(d,p):found.append([(d,c),(a,b)])
  # Collective three-donor unit rows, not restricted to native support.
  for d,a in itertools.combinations([x for x in pool if x!=p],2):
   for c,b in itertools.product((-1,1),repeat=2):
    rest=tuple(K[p][i]-c*K[d][i]-b*K[a][i]for i in range(120))
    for f,g in index.get(rest,[]):
     if f not in(p,d,a):found.append([(d,c),(a,b),(f,g)])
  if found:
   cs=min(found,key=lambda z:(sum(abs(c)for d,c in z),len(z),sorted(z)));assert all(sum(c*K[d][i]for d,c in cs)==K[p][i]for i in range(120))
   out.append({'frame':e['frame'],'rank':e['rank'],'pivot':p,'coefficients':cs,'unit_additions':sum(abs(c)for d,c in cs),'scope':'Actualcommonfirstframe; full81word/dirt/profile gate pending, newnativeparitykernelnotcatalogrestricted.'})
 print(e['frame'],len([x for x in out if x['frame']==e['frame']]),flush=True)
(O/'SPARSE.json').write_text(json.dumps({'status':'EXACT_COMMON_FRAME_COLLECTIVE_INTEGER_NOMINATIONS','rows':out},indent=2)+'\n');print(out)
