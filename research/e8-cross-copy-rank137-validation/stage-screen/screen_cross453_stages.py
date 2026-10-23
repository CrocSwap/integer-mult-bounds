"""Explore stage counts under cross-copy hosting of fixed rank137 mixed word; no new construction claim."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import json,sys
r=Path.cwd();o=r/'cross453-stage-screen';o.mkdir(exist_ok=True)
sys.path[:0]=[str(r/'source450-review/code'),str(r/'source448-review'),str(r/'complex447-search'),str(r/'source443-review/code/engines')]
import hosting_k as HK,tape_core as TC,moment as M
w=json.loads((r/'cross450-kernel-search/WORD-MIXED.json').read_text());fs=json.loads((r/'research439-screen/records/frames.json').read_text())['frames'];widths=[8-fs[str(f)]['dim'] for f in w['start'][240:]];counts=Counter(widths);H={int(k):n for k,n in json.loads((r/'cross450-kernel-search/MIX-CHECK.json').read_text())['profile'].items()}
for K in range(6,10):
 L=2*K+1;m=1+7*L;events=[dict(kind='local',stage=0,pair=0)];stage=1
 for j in range(K):
  events.append(dict(kind='local',stage=stage,pair=j));stage+=1
  if j<K-1:events.append(dict(kind='bridge',dst=j,src=j+1))
  events.append(dict(kind='local',stage=stage,pair=j));stage+=1
  if j<K-1:events.append(dict(kind='bridge',dst=j,src=j+1))
 levels=[-1]*K;schedule=[];idx=0
 for e in events:
  schedule.append(e)
  if e['kind']!='local':continue
  s=e['stage'];levels[e['pair']]=s;idle=[]
  if s in range(1,2*K-1,2):j=(s+1)//2;idle.append((j,7*(s+1)));levels[j]=s
  elif s in range(2,2*K,2):j=s//2;idle.append((j,7));levels[j]=s
  elif s==2*K:
   for j in range(K):idle.append((j,7*(2*K-levels[j])));levels[j]=2*K
  for j,rank in idle:schedule.append(dict(kind='idle',idx=idx,pair=j,rank=rank));idx+=1
 win={i:z for i,z in TC.windows(schedule).items() if z[1]>0 and z[2]}
 try:
  selected,val=HK.solve_tape(win,240,{(s,z):n for s in range(L) for z,n in counts.items()},m,host_all=True,time_limit=45)
  pieces,rem=TC.expand(win,selected,{s:list(enumerate(widths)) for s in range(L)},240);assert len(pieces)==L*w['R']
  paid=Counter({k:n*L*8 for k,n in H.items()})
  for e in schedule:
   if e['kind']=='idle' and e['rank']:
    for cp in range(240):
     z=rem[e['idx'],cp] if e['idx'] in win else e['rank']
     if z:paid[z]+=8
  W=2*K*120*8;D=m*W-sum(k*n for k,n in paid.items());assert D==(2*K*120-72*L)*8
  cert=M.certify(paid,m,W,True);res=dict(status='AGGREGATE_ONLY',K=K,stages=L,m=m,live=W,deficit=D,bit_lower=cert['lower'],maxchild=max(paid),profile=dict(paid));TC.save(o/f'selection-{L}.json','bit',selected,val)
 except Exception as e:res=dict(status='SCREEN_FAILED',K=K,error=repr(e))
 (o/f'result-{L}.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res),flush=True)
