"""Monotone-frame single-gate retiming; exact local constructor checks, no full admission."""
from pathlib import Path
from collections import Counter,defaultdict
import sys,json,gzip,copy,math,time,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
O=R/'complex496-retiming-centres-fixed';O.mkdir(exist_ok=False)
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
fixed_centres={('A',max(j for j,e in enumerate(W['A']) if r in regs(e))) for r in centers if any(r in regs(e) for e in W['A'])}
history=[];tested=0;t0=time.monotonic()
for iteration in range(250):
 events,prev,nxt=context(W);best=None
 for q,(key,j,F,rs) in enumerate(events):
  if key is None or (key,j) in fixed_centres:continue
  low=set().union(*(space(prev[q][r]) for r in rs));high=set.intersection(*(set(space(nxt[q][r])) for r in rs))
  old=sum(cost(len(F)-len(prev[q][r]))+cost(len(nxt[q][r])-len(F)) for r in rs)
  for E in sorted(set(frames)|{frame(sorted(low-{0})),frame(sorted(high-{0}))},key=lambda F:(len(F),F)):
   if E==F or not low<=space(E)<=high:continue
   tested+=1;delta=sum(cost(len(E)-len(prev[q][r]))+cost(len(nxt[q][r])-len(E)) for r in rs)-old
   if delta < -1e-10 and (best is None or delta<best[0]):best=(delta,key,j,F,E)
 if best is None:break
 delta,key,j,F,E=best;W[key][j][-1]=list(E);new=G.profile(W)
 # Cleanup must remain the literal reverse of all source/helper gates.
 W['cleanup']=[G.inverse(e,G.FULL) for e in reversed(W['A']+W['B']) if not 120<=e[1]<240]
 actual=sum(cost(r)*v for r,v in new.items())-sum(cost(r)*v for r,v in hist0.items())
 history.append(dict(iteration=iteration,part=key,index=j,old_frame=list(F),new_frame=list(E),delta_float=delta,profile=dict(sorted(new.items()))));hist0=new
 if iteration%10==0:print('move',iteration,'delta',delta,'profile',dict(new),'tested',tested,flush=True)
W['report']['local_profile']={str(r):v for r,v in sorted(hist0.items())}
raw=json.dumps(W,sort_keys=True,separators=(',',':')).encode();(O/'WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0));(O/'HISTORY.json').write_text(json.dumps(history,indent=2)+'\n');result=dict(status='MONOTONE_LOCAL_PROFILE_SCREEN_ONLY',accepted_moves=len(history),tested_candidates=tested,iterations=iteration+1,limit=250,terminated_local_optimum=best is None,profile=dict(sorted(hist0.items())),word_sha256=hashlib.sha256(raw).hexdigest(),seconds=time.monotonic()-t0,scope='No independent dirty-column, Gaussian-phase, physical-controller or exact global moment admission yet. Centres frozen; existing frame set only.')
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True)
