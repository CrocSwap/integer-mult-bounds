"""Monotone-frame single-gate retiming; exact local constructor checks, no full admission."""
from pathlib import Path
from collections import Counter,defaultdict
import sys,json,gzip,copy,math,time,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
O=R/'complex496-retiming-groups';O.mkdir(exist_ok=False)
W=json.load(gzip.open(R/'complex496-entrance-search/baseline/WORD.json.gz'));(O/'BASE-WORD.json.gz').write_bytes(gzip.compress(json.dumps(W,sort_keys=True).encode(),mtime=0))
n=240+W['report']['R'];centers=set(W['centers']);b=float(__import__('fractions').Fraction(json.load(open(R/'source496-review/EXPECTED.json'))['complex_lower']))
def frame(F):return tuple(G.basis(F))
full=frame(G.FULL);spaces={}
def space(F):
 if F not in spaces:spaces[F]=frozenset(G.span(F))
 return spaces[F]
frames={frame(e[-1]) for seq in ['A','B'] for e in W[seq]}|{(),full}|{frame([q]) for q in W['ports']};frames=sorted(frames,key=lambda F:(len(F),F));hist0=G.profile(W)
def regs(e):return [e[1],e[2]] if e[0]=='add' else [e[1]]
def context(w):
 events=[]
 for key in ['A','B']:
  if key=='B':
   for r,F in zip(w['centers'],w['center_frames']):events.append((None,r,frame(F),[r]))
   for t in range(120):events.append((None,120+t,frame(w.get('target_levels',{}).get(str(t),[])),[120+t]))
  for j,e in enumerate(w[key]):events.append((key,j,frame(e[-1]),regs(e)))
 start={r:frame([w['ports'][r]]) if r<120 else frame(w.get('start_extra',{}).get(str(r),[])) for r in range(n)}
 end={r:full if r<120 or r>=240 else frame(G.perp(w['ports'][r-120])) for r in range(n)}
 prev=[];cur=dict(start)
 for key,j,F,rs in events:
  prev.append({r:cur[r] for r in rs})
  for r in rs:cur[r]=F
 nxt=[None]*len(events);cur=dict(end)
 for q in reversed(range(len(events))):
  key,j,F,rs=events[q];nxt[q]={r:cur[r] for r in rs}
  for r in rs:cur[r]=F
 return events,prev,nxt
# Full moment dependence on local paid counts, with unchanged pending widths/packing.
def cost(rank):return rank*math.expm1(b*math.log(73/rank))/b+(32*73**2/1e16)*73**b/b if rank else 0
history=[];tested=0;t0=time.monotonic();candidate_counts=[]
for iteration in range(80):
 events,prev,nxt=context(W);byreg=defaultdict(list);valid=set()
 for q,(key,j,F,rs) in enumerate(events):
  for r in rs:byreg[r].append(q)
  if key is not None and not any(r in centers for r in rs):valid.add(q)
 adj={q:set() for q in valid}
 for r,qs in byreg.items():
  for a,c in zip(qs,qs[1:]):
   if a in valid and c in valid and events[a][2]==events[c][2]:adj[a].add(c);adj[c].add(a)
 groups={frozenset([a,c]) for a in adj for c in adj[a]};seen=set()
 for q in valid:
  if q in seen:continue
  component={q};todo=[q];seen.add(q)
  while todo:
   a=todo.pop()
   for c in adj[a]-seen:seen.add(c);component.add(c);todo.append(c)
  if len(component)>1:groups.add(frozenset(component))
 # Connected triples and quadruples are a different neighborhood from single-gate moves.
 frontier={g for g in groups if len(g)==2}
 for size in [3,4]:
  extra=set()
  for g in frontier:
   for c in set.union(*(adj[q] for q in g))-set(g):extra.add(g|{c})
  groups|=extra;frontier=extra
 candidate_counts.append(len(groups));best=None
 for group in groups:
  F=events[next(iter(group))][2];rr=set.union(*(set(events[q][3]) for q in group));bounds={};ok=True
  for r in rr:
   touched=[q for q in byreg[r] if q in group];a,c=min(touched),max(touched)
   if any(a<q<c and q not in group for q in byreg[r]):ok=False;break
   bounds[r]=(prev[a][r],nxt[c][r])
  if not ok:continue
  low=set().union(*(space(a) for a,c in bounds.values()));high=set.intersection(*(set(space(c)) for a,c in bounds.values()))
  old=sum(cost(len(F)-len(a))+cost(len(c)-len(F)) for a,c in bounds.values())
  for E in {frame(sorted(low-{0})),frame(sorted(high-{0}))}:
   if E==F or not low<=space(E)<=high:continue
   tested+=1;delta=sum(cost(len(E)-len(a))+cost(len(c)-len(E)) for a,c in bounds.values())-old
   if delta < -1e-10 and (best is None or delta<best[0]):best=(delta,group,F,E)
 if best is None:break
 delta,group,F,E=best;edits=[]
 for q in sorted(group):
  key,j,_,rs=events[q];W[key][j][-1]=list(E);edits.append([key,j])
 new=G.profile(W);actual=sum(cost(r)*v for r,v in new.items())-sum(cost(r)*v for r,v in hist0.items());assert abs(actual-delta)<1e-7,(actual,delta)
 W['cleanup']=[G.inverse(e,G.FULL) for e in reversed(W['A']+W['B']) if not 120<=e[1]<240]
 history.append(dict(iteration=iteration,edits=edits,old_frame=list(F),new_frame=list(E),delta_float=delta,profile=dict(sorted(new.items()))));hist0=new
 print('move',iteration,'gates',len(group),'delta',delta,'profile',dict(new),'tested',tested,flush=True)
W['report']['local_profile']={str(r):v for r,v in sorted(hist0.items())};raw=json.dumps(W,sort_keys=True,separators=(',',':')).encode();(O/'WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0));(O/'HISTORY.json').write_text(json.dumps(history,indent=2)+'\n');result=dict(status='MONOTONE_LOCAL_PROFILE_SCREEN_ONLY',accepted_moves=len(history),tested_candidates=tested,candidate_group_counts=candidate_counts,profile=dict(sorted(hist0.items())),word_sha256=hashlib.sha256(raw).hexdigest(),seconds=time.monotonic()-t0,scope='Groups of size2..4 plus full same-frame components; centres frozen. Independent dirty-column, Gaussian-phase, physical and exact assembly checks pending.')
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True)
