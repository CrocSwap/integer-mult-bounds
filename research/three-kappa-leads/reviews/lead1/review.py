from pathlib import Path
import json,gzip,sys,subprocess,copy,itertools
from collections import Counter,defaultdict
from fractions import Fraction as Q
import mpmath as mp
R=Path('/Users/temp/.codex/worktrees/three-kappa-leads/integer-mult-bounds');P=R/'research/three-kappa-leads';O=Path('/tmp/three-kappa-astra-lead1')
sys.path.insert(0,str(P))
import chronology_check as C
j=lambda p:json.loads(p.read_text())
d=j(P/'CHRONOLOGY-CANDIDATE.json');template=json.loads(gzip.decompress((R/'research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz').read_bytes()))
def groups(order):
 clock={tuple(v):i for i,v in enumerate(order)};ans=Counter(); children={x['child']:x['rank'] for x in template['idle_children']};pairs={x['stage']:x['pair'] for x in template['recipe'] if x['kind']=='local'}
 for replica in range(45):
  touched={};t=None
  for e in template['execution_schedule']:
   k=e['kind']
   if k=='local_cover_sweep':t=clock[e['stage'],replica];touched[pairs[e['stage']]]=t
   elif k=='bridge':touched[e['src']]=t;touched[e['dst']]=t
   elif k=='idle_cover_sweep':
    for child in e['child_indices']:
     if child in children:ans[children[child],touched.get(e['pair'],-1),t]+=112
 return ans
actual=groups(d['order']);assert sorted([*k,v]for k,v in actual.items())==d['groups']
old=copy.deepcopy(d['order']);old[332],old[333]=old[333],old[332];prev=groups(old)
assert actual-prev==Counter({(16,317,333):224,(32,284,333):224,(48,232,333):224})
assert prev-actual==Counter({(16,317,332):224,(32,284,332):224,(48,232,332):224})
violations=[row for row in d['z'] if d['groups'][row[0]][2]==333 and row[1]==333 and tuple(d['groups'][row[0]][:3]) in actual-prev]
assert sum(x[3]for x in violations)>0
H=Counter({int(r):n*3240 for r,n in d['local_profile'].items()})
for g,q,n in d['x']:
 residual=d['groups'][g][0]-sum(w*v for w,v in zip(d['widths'],q))
 if residual:H[residual]+=n
assert dict(H)=={int(r):n for r,n in d['profile'].items()};assert sum(r*n for r,n in H.items())==23431680
assert 896*360+408+8+91+2==323069
mp.mp.dps=90
mom=lambda a:sum(n*mp.power(mp.mpf(r)/73,1-a)for r,n in H.items())/(896*360)-1
lo,hi=[mp.mpf(x)for x in j(P/'PRICE-EXPECTED.json')['root_interval']];assert mom(lo)<0<mom(hi)
c=j(P/'comparators/PR3633-ceiling-CEILING.json');dual=[{int(r):Q(v)for r,v in row.items()}for row in c['dual_by_constraint']]
count=zero=0;mini=mp.inf
for cap in [8,16,32,48]:
 for q in itertools.product(*(range(cap//w+1)for w in range(4,10))):
  left=cap-sum(w*n for w,n in zip(range(4,10),q))
  if left<0:continue
  count+=1;cost=defaultdict(Q)
  if left:cost[left]=1
  for a,row in zip([int(cap==v)for v in [8,16,32,48]]+list(q),dual):
   for r,v in row.items():cost[r]-=a*v
  cost={r:v for r,v in cost.items()if v}
  if not cost:zero+=1;continue
  val=sum(mp.mpf(v.numerator)/v.denominator*mp.power(r,1-hi)for r,v in cost.items());assert val>0;mini=min(mini,val)
assert (count,zero)==(2551,12)
controls=[]
for name,mutate in [('undo clock',lambda b:b['order'].__setitem__(slice(332,334),list(reversed(b['order'][332:334])))),('unpaid rank1',lambda b:b['profile'].__setitem__('1',b['profile']['1']+1)),('drop role flow',lambda b:b['z'][0].__setitem__(3,b['z'][0][3]-1)),('negative pattern',lambda b:b['x'][0][1].__setitem__(0,-1))]:
 b=copy.deepcopy(d);mutate(b)
 try:C.check(b)
 except ValueError as e:controls.append([name,str(e)])
 else:raise AssertionError(name)
result={'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'source_window_delta':[[*k,v]for k,v in (actual-prev).items()],'old_clock_invalid_roles':sum(x[3]for x in violations),'profile':dict(H),'numeric_crosscheck_only':[str(mom(lo)),str(mom(hi))],'patterns':count,'symbolic_zero':zero,'numeric_minimum_strict':str(mini),'aggregate_controls':controls}
(O/'INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
for script in ['chronology_check.py','price_check.py','ceiling_check.py','evidence_check.py','evidence_controls.py','aggregate_controls.py']:
 run=subprocess.run([sys.executable,'-B',str(P/script)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,cwd=R);(O/(script+'.log')).write_text(run.stdout);assert run.returncode==0,(script,run.stdout);print('PASS',script,flush=True)
