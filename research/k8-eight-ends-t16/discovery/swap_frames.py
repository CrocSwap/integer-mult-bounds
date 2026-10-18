"""Discovery: commute adjacent B gates and exactly enumerate their frame intervals."""
import json,gzip,copy,importlib.util,math,time
from pathlib import Path
from collections import Counter
from functools import lru_cache
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=mod('M',ROOT/'research/k8-eight-ends/discovery/frame_model.py');promo=mod('p',ROOT/'research/gauge44-slots/construction/promo/build_promotion.py')
@lru_cache(None)
def join(a,b):return M.basis(a+b)
@lru_cache(None)
def meet(a,b):return M.meet(a,b)
@lru_cache(None)
def interval(lo,hi):return tuple(M.interval(lo,hi))
def union(frames):
 ans=()
 for f in frames:ans=join(ans,f)
 return ans
def intersection(frames):
 ans=M.FULL
 for f in frames:ans=meet(ans,f)
 return ans
def inside(a,b):return join(a,b)==b
def commute(a,b):
 if a[0]!='add' or b[0]!='add':return False
 return a[1]!=b[2] and b[1]!=a[2]
def score(prev,after,gates):
 cur=dict(prev);val=0
 for e in gates:
  fr=tuple(e[-1])
  for q in M.registers(e):
   if not inside(cur[q],fr):return None
   d=len(fr)-len(cur[q]);val+=d*math.log(d) if d else 0;cur[q]=fr
 for q,fr in after.items():
  if not inside(cur[q],fr):return None
  d=len(fr)-len(cur[q]);val+=d*math.log(d) if d else 0
 return val
w=json.loads(gzip.decompress((ROOT/'research/k8-eight-ends/FULL-WORD.json.gz').read_bytes()));original=copy.deepcopy(w);model=M.Model(w);ceil=model.ceil
start=[(p,) for p in w['ports']]+[()]*(704-112)
for q,fr in w['start_extra'].items():start[int(q)]=tuple(fr)
for e in w['A']:
 for q in M.registers(e):start[q]=tuple(e[-1])
ends=[M.FULL]*112+[M.basis([x for x in range(1,512) if (x&p).bit_count()%2==0]) for p in w['ports']]+[M.FULL]*480
for q,fr in w['helper_final'].items():ends[int(q)]=tuple(fr)
for ci,fr in reversed(w['early_cleanup']):
 for q in M.registers(w['cleanup'][ci]):ends[q]=tuple(fr)
trace=[];stats=Counter()
for sweep in range(12):
 nxt=ends.copy();nexts=[];last=[True]*704;lasts=[]
 for i in range(len(w['B'])-1,-1,-1):
  nexts.append(nxt.copy());lasts.append(last.copy())
  for q in M.registers(w['B'][i]):nxt[q]=tuple(w['B'][i][-1]);last[q]=False
 nexts.reverse();lasts.reverse();cur=start.copy();changed=0;i=0
 while i<len(w['B'])-1:
  a,b=w['B'][i:i+2];ra,rb=tuple(M.registers(a)),tuple(M.registers(b));qs=set(ra+rb)
  if commute(a,b) and set(ra)&set(rb):
   stats['commuting_shared_windows']+=1;prev={q:cur[q] for q in qs};after={q:nexts[i+1][q] for q in qs};bounds=dict(after)
   for q in qs:
    if lasts[i+1][q] and q in ceil:bounds[q]=meet(bounds[q],ceil[q])
   old=score(prev,after,[a,b]);assert old is not None
   lo=union(prev[q] for q in rb);hi=intersection([*(bounds[q] for q in rb),intersection(bounds[q] for q in ra)])
   if inside(lo,hi) and len(hi)-len(lo)<=3:
    best=(old,None)
    for F in interval(lo,hi):
     ccur=dict(prev)
     for q in rb:ccur[q]=F
     lo2=union(ccur[q] for q in ra);hi2=intersection(bounds[q] for q in ra)
     if not inside(lo2,hi2) or len(hi2)-len(lo2)>3:continue
     for G in interval(lo2,hi2):
      nb=b[:-1]+[list(F)];na=a[:-1]+[list(G)];value=score(prev,after,[nb,na]);stats['frame_assignments']+=1
      if value is not None and value>best[0]+1e-9:best=(value,[nb,na])
    if best[1]:
     w['B'][i:i+2]=best[1];changed+=1;r=dict(sweep=sweep,B=i,entropy_gain=best[0]-old,before=[a,b],after=best[1]);trace.append(r);print('improve',sweep,i,best[0]-old,flush=True)
     # Consume the complete window so all successor frames used here remain unchanged.
     for e in best[1]:
      for q in M.registers(e):cur[q]=tuple(e[-1])
     i+=2;continue
  for q in ra:cur[q]=tuple(a[-1])
  i+=1
 print('sweep',sweep,'changed',changed,flush=True)
 if not changed:break
lp=Counter({int(k):v for k,v in original['report']['local_profile'].items()});lp.subtract(promo.chain_profile(original));lp.update(promo.chain_profile(w));w['report']['local_profile']={str(k):v for k,v in sorted(lp.items()) if v};(P/'SWAPPED.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));(P/'SWAP-SEARCH.json').write_text(json.dumps(dict(stats=dict(stats),trace=trace,profile=w['report']['local_profile']),indent=2)+'\n');print('profile',w['report']['local_profile'],'stats',dict(stats),flush=True)
