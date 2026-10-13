"""Directed equal-frame closures refine PR501's whole-component retiming moves.
Nomination only. Scalar order, entrances, centre and target boundaries stay fixed.
"""
from pathlib import Path
from functools import lru_cache
from collections import Counter
from fractions import Fraction
import sys,json,gzip,copy,math,time,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
O=R/'complex501-directed-closures';O.mkdir(exist_ok=False)
w=json.load(gzip.open(R/'pr501-retimed-word.json.gz'));original=copy.deepcopy(w)
b=float(Fraction(json.load(open(R/'source501-delta-review/EXPECTED.json'))['complex_lower']))
n=240+w['report']['R'];labels=[];pins=[];keys={};seq=[[] for _ in range(n)]
def node(F,pin,rs,key=None):
 i=len(labels);labels.append(G.basis(F));pins.append(pin)
 for r in rs:seq[r].append(i)
 if key is not None:keys[key]=i
for r in range(n):node([w['ports'][r]] if r<120 else w.get('start_extra',{}).get(str(r),[]) if r>=240 else [],True,[r])
for part in ['A','B']:
 if part=='B':
  for r,F in zip(w['centers'],w['center_frames']):node(F,True,[r])
  for t in range(120):node(w.get('target_levels',{}).get(str(t),[]),True,[120+t])
 for j,e in enumerate(w[part]):node(e[-1],False,[e[1],e[2]] if e[0]=='add' else [e[1]],(part,j))
for r in range(n):node(G.perp(w['ports'][r-120]) if 120<=r<240 else G.FULL,True,[r])
edges=[(a,z) for ss in seq for a,z in zip(ss,ss[1:])];incoming=[[]for _ in labels];outgoing=[[]for _ in labels]
for k,(a,z) in enumerate(edges):outgoing[a].append(k);incoming[z].append(k)
@lru_cache(None)
def span(F):return frozenset(G.span(F))
def cost(rank):return rank*math.expm1(b*math.log(73/rank))/b+32*73**2/1e16*73**b/b if rank else 0
costs=[cost(r) for r in range(10)]
def total():return sum(costs[len(labels[z])-len(labels[a])] for a,z in edges)
startcost=total();history=[];ledger=[];t0=time.monotonic()
for it in range(100):
 for a,z in edges:assert span(labels[a])<=span(labels[z])
 forward=[frozenset([i]) for i in range(len(labels))];backward=forward.copy()
 for i in reversed(range(len(labels))):
  forward[i]=frozenset({i}.union(*(forward[edges[k][1]] for k in outgoing[i] if labels[i]==labels[edges[k][1]])))
 for i in range(len(labels)):
  backward[i]=frozenset({i}.union(*(backward[edges[k][0]] for k in incoming[i] if labels[i]==labels[edges[k][0]])))
 best=None;seen=set();trials=0;feasible=0;neutral=0
 for direction,groups in [('up',forward),('down',backward)]:
  for group in groups:
   sig=(direction,group)
   if sig in seen or any(pins[i] for i in group):continue
   seen.add(sig);trials+=1;cf=labels[next(iter(group))]
   ins=[k for i in group for k in incoming[i] if edges[k][0] not in group];outs=[k for i in group for k in outgoing[i] if edges[k][1] not in group]
   low=G.basis([v for k in ins for v in labels[edges[k][0]]]);high=G.basis(set.intersection(*(set(span(labels[edges[k][1]])) for k in outs)))
   nf=high if direction=='up' else low
   if cf==nf:continue
   assert span(low)<=span(nf)<=span(high);feasible+=1
   old=sum(costs[len(cf)-len(labels[edges[k][0]])] for k in ins)+sum(costs[len(labels[edges[k][1]])-len(cf)] for k in outs)
   new=sum(costs[len(nf)-len(labels[edges[k][0]])] for k in ins)+sum(costs[len(labels[edges[k][1]])-len(nf)] for k in outs);delta=new-old
   if abs(delta)<1e-9:neutral+=1
   if delta < -1e-9 and (best is None or delta<best[0]):best=(delta,group,nf,direction)
 ledger.append(dict(iteration=it,groups_tested=trials,changed_frame_candidates=feasible,neutral_candidates=neutral,best_delta=None if best is None else best[0]))
 if best is None:break
 delta,group,nf,direction=best;oldtotal=total()
 for i in group:labels[i]=nf
 assert abs(total()-oldtotal-delta)<1e-7
 for (part,j),i in keys.items():w[part][j][-1]=list(labels[i])
 p=G.profile(w);expected={int(r):v for r,v in original['report']['local_profile'].items()};actual=sum(costs[r]*(p.get(r,0)-expected.get(r,0)) for r in set(p)|set(expected));assert abs(actual-(total()-startcost))<1e-6
 history.append(dict(direction=direction,delta_float=delta,frame=list(nf),nodes=sorted(group),profile=dict(sorted(p.items()))));print('IMPROVEMENT',it,delta,'events',len(group),'profile',dict(sorted(p.items())),flush=True)
profile=G.profile(w);w['report']['local_profile']={str(r):v for r,v in sorted(profile.items())};w['cleanup']=[G.inverse(e,G.FULL) for e in reversed(w['A']+w['B']) if not 120<=e[1]<240]
assert G.widths_of(w)==G.widths_of(original)
raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode();(O/'WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0))
(O/'HISTORY.json').write_text(json.dumps(history,indent=2)+'\n');(O/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n')
result=dict(status='DIRECTED_CLOSURE_LOCAL_PROFILE_SCREEN_ONLY',baseline_pr=501,baseline_head='1dc056496fdbbc74073ed26d948a2dc235dbf356',accepted_moves=len(history),cost_before=startcost,cost_after=total(),profile=dict(sorted(profile.items())),seconds=time.monotonic()-t0,word_sha256=hashlib.sha256(raw).hexdigest(),scope='Full finite Gaussian, physical hosting and exact moment admission required for any improvement.')
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True)
