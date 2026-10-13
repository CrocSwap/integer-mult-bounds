"""Screen complete-word substitutions on fixed async physical owners.
Offsets may be repacked within the same pending child. No owner/window changes.
This is a discovery model, not a physical or invoice admission certificate.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
import json,gzip,sys,math,time
R=Path(__file__).resolve().parent;O=R/'async505-word-choice-search';O.mkdir(exist_ok=False)
sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
cs=read(R/'complex501-heterogeneous-words/CANDIDATES.json');roles=read(R/'source505-review/inputs/ASYNC-OWNERS.json.gz');plan=read(R/'source505-review/inputs/ASYNC-3.json');old=read(R/'async505-retimed-candidate/audit/EXACT-ASSEMBLY.json');b=float(Fraction(old['complex_lower']));m=plan['M'];order=[tuple(x)for x in plan['order']];at={k:i for i,k in enumerate(order)};capacities={};used=Counter();role={}
for z in roles:
 k=(z['owner_replica'],z['child'],z['port']);role[at[z['stage'],z['replica']],z['helper']]=k;used[k]+=z['width'];capacities[k]=plan['windows'][f"{z['owner_replica']},{z['child']}"][0]
words=[]
for c in cs:
 w=read(R/Path(c['source']).parent/'WORD.json.gz');widths=G.widths_of(w);h={int(k):v for k,v in c['profile'].items()};assert Counter(widths)==Counter({int(k):v for k,v in c['widths'].items()});words.append((widths,h))
basew=words[0][0];assert all(basew[h]==z['width']for z in roles for h in [z['helper']]);left={k:capacities[k]-used[k]for k in capacities};assert min(left.values())>=0
cost=lambda r:r*math.expm1(b*math.log(m/r))/b+32*m*m/1e16*m**b/b if r else 0
localcost=[sum(n*cost(r)for r,n in H.items())for ws,H in words];choices=[0]*len(order);moves=[];ledger=[];start=time.monotonic()
for sweep in range(100):
 best=None;feasible=reject=0
 for t in range(len(order)):
  current=choices[t];cw=words[current][0]
  for j,(ww,hh)in enumerate(words):
   if j==current:continue
   deltas=Counter()
   for h,(x,y)in enumerate(zip(cw,ww)):
    if x!=y:deltas[role[t,h]]+=y-x
   excess=max([v-left[k]for k,v in deltas.items()]+[0])
   if excess>0:reject+=1;gain=None
   else:
    feasible+=1;gain=localcost[current]-localcost[j]+sum(cost(left[k])-cost(left[k]-v)for k,v in deltas.items())
    if gain>1e-8 and (best is None or gain>best[0]):best=(gain,t,j,deltas)
   if sweep==0:ledger.append(dict(call=t,stage=order[t][0],replica=order[t][1],candidate=j,feasible=excess==0,maximum_capacity_excess=excess,cost_gain=gain))
 if best is None:break
 gain,t,j,deltas=best;moves.append(dict(call=t,stage=order[t][0],replica=order[t][1],from_candidate=choices[t],to_candidate=j,label=cs[j]['label'],cost_gain=gain))
 choices[t]=j
 for k,v in deltas.items():left[k]-=v
 print('MOVE',moves[-1],flush=True)
H=Counter()
for j in choices:H.update(words[j][1])
# Include unchanged pending containers with no helper roles too.
parent=read(R/'stage4-local-verification/baseline/split-centres/GLOBAL-TEMPLATE.json.gz')
for idle in parent['idle_children']:
 for rep in range(plan['T']):
  k=(rep,idle['child'],idle['port']);r=left.get(k,idle['rank'])
  if r:H[r]+=1
assert m*plan['live']-sum(r*n for r,n in H.items())==plan['deficit']
result=dict(status='FLOAT_FIXED_OWNER_COMPLETE_WORD_SCREEN',candidates=len(cs),first_sweep_cases=len(ledger),sweeps=sweep+1,last_feasible=feasible,last_capacity_rejects=reject,moves=moves,choices=choices,profile=dict(sorted(H.items())),total_cost_gain=sum(x['cost_gain']for x in moves),seconds=time.monotonic()-start,scope='Fixed families and owner intervals. New widths repack each pending child contiguously. Local constructor results only; full mixed-word emitter, independent controller and finite invoice remain necessary.')
(O/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print('RESULT',{k:v for k,v in result.items()if k not in ['choices','profile','moves']},flush=True)
