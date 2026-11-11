"""Nominate eleven-stage hosting of exact local words; no global claim."""
from pathlib import Path
import sys,json,math
from collections import Counter
from fractions import Fraction as Q
r=Path.cwd();sys.path.insert(0,str(r/'early-reuse-publication/research/e8-r740-idle-hosting'));import hosting_core as HC
sys.path.insert(0,str(r/'source443-review/code/engines'));import moment as M
out=r/'eleven-kernel-screen';out.mkdir(exist_ok=True)
K=5;L=2*K+1;m=8+7*(L-1);T=8;c=.0012649635760773785
HC.cost=lambda rank,m:rank*math.expm1(c*math.log(m/rank))/c if rank else 0.
events=[dict(kind='local',stage=0,pair=0)];stage=1
for j in range(K):
 events.append(dict(kind='local',stage=stage,pair=j));stage+=1
 if j<K-1:events.append(dict(kind='bridge',dst=j,src=j+1))
 events.append(dict(kind='local',stage=stage,pair=j));stage+=1
 if j<K-1:events.append(dict(kind='bridge',dst=j,src=j+1))
for j in reversed(range(K-1)):events.append(dict(kind='bridge',dst=j+1,src=j))
levels=[-1]*K;indexed=[];idx=0
for e in events:
 indexed.append(e)
 if e['kind']!='local':continue
 s=e['stage'];levels[e['pair']]=s
 idles=[]
 if s in range(1,2*K-1,2):
  j=(s+1)//2;idles.append((j,7*(s+1)));levels[j]=s
 elif s in range(2,2*K,2):
  j=s//2;idles.append((j,7));levels[j]=s
 elif s==2*K:
  for j in range(K):idles.append((j,7*(2*K-levels[j])));levels[j]=2*K
 for j,rank in idles:indexed.append(dict(kind='idle',idx=idx,pair=j,rank=rank));idx+=1
win={i:w for i,w in HC.windows(indexed).items() if w[1] and w[2]}
dims=[x['dim'] for k,x in sorted(json.loads((r/'research439-screen/records/frames.json').read_text())['frames'].items(),key=lambda kv:int(kv[0]))]
for tag,path,hpath in [('rank138',r/'hosted138-screen/bit426-source-centres/bit-source-centres.json',r/'hosting443-kernel138-screen/RESULT.json'),('rank147',r/'hosting-kernel-growth/WORD.json',r/'hosting-kernel-growth/EXACT-LOCAL.json')]:
 w=json.loads(path.read_text());counts=Counter(8-dims[w['start'][h]] for h in range(240,980));H={int(k):v for k,v in json.loads(hpath.read_text())['local_profile'].items()}
 print(tag,'widths',counts,flush=True)
 y,z,val=HC.solve(win,240,{(s,width):n for s in range(L) for width,n in counts.items()},m,pad_value=1000.0)
 slots,rem=HC.expand(win,y,z,{s:list(enumerate([8-dims[w['start'][h]] for h in range(240,980)])) for s in range(L)},240)
 assert len(slots)==L*w['R'],('not all hosted',len(slots))
 paid=Counter({k:v*L*T for k,v in H.items()})
 for e in indexed:
  if e['kind']!='idle' or not e['rank']:continue
  for cp in range(240):
   q=rem[e['idx'],cp] if e['idx'] in win else e['rank']
   if q:paid[q]+=T
 assert m*(2*K*120*T)-sum(k*n for k,n in paid.items())==(2*K*120-L*72)*T
 cert=M.certify(paid,m,2*K*120*T,True)
 HC.save_selection(out/(tag+'-selection.json'),'bit',y,z,val)
 result=dict(status='EXACT_AGGREGATE_ONLY_GLOBAL_PENDING',tag=tag,profile=dict(paid),widths=dict(counts),moment=cert)
 (out/(tag+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(tag,cert,flush=True)
