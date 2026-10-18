import os
import sys,json,gzip,copy,importlib.util
from pathlib import Path
from fractions import Fraction as F
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[3]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a=module('audit',ROOT/'research/gauge44-slots/independent/audit_local.py')
p=module('promo',ROOT/'research/gauge44-slots/construction/promo/build_promotion.py')
IN=Path(os.environ['K8_BASE_WORD'])
w=json.loads(gzip.decompress(IN.read_bytes()));v=w['report']['v'];n=2*v+w['report']['R'];FULL=a.basis([1<<i for i in range(9)])
ends=[FULL]*v+[a.basis([x for x in range(1,512) if (x&port).bit_count()%2==0]) for port in w['ports']]+[FULL]*w['report']['R']
for r,frame in w['helper_final'].items():ends[int(r)]=a.basis(frame)
events=[(sec,i,e) for sec in ['A','B'] for i,e in enumerate(w[sec])]+[('T',i,w['cleanup'][ci][:-1]+[fr]) for i,(ci,fr) in enumerate(w['early_cleanup'])]
nexts={};nxt=ends.copy()
for ei in range(len(events)-1,-1,-1):
 sec,i,e=events[ei]
 if sec=='B':nexts[i]=nxt.copy()
 for r in a.registers(e):nxt[r]=a.basis(e[-1])
cur=[(port,) for port in w['ports']]+[()]*(n-v)
for r,fr in w['start_extra'].items():cur[int(r)]=a.basis(fr)
rows=[{i:F(1)} if i<v else {} for i in range(n)]
def key(row):
 if not row:return None,None
 s=sorted(row);q=row[s[0]];return tuple((i,row[i]/q) for i in s),q
result=[];stats=Counter();old=p.chain_profile(w)
for sec in ['A','B']:
 if sec=='B':
  for e in w['cut']:a.apply(e,rows)
 for i,e in enumerate(w[sec]):
  if sec=='B' and e[0]=='add' and v<=e[1]<2*v and e[2]>=2*v:
   stats['helper_target_reads']+=1;hk,hq=key(rows[e[2]])
   for s in range(v):
    sk,sq=key(rows[s])
    if hk is not None and sk==hk:
     stats['clean_source_aliases']+=1
     frame=a.basis(list(cur[s])+list(cur[e[1]]))
     feasible=a.contained(frame,nexts[i][s]) and a.contained(frame,nexts[i][e[1]])
     rec=dict(B=i,target=e[1],helper=e[2],source=s,coefficient=str(F(e[3],e[4])*hq/sq),frame=list(frame),frame_feasible=feasible)
     if feasible:
      nw=copy.deepcopy(w);q=F(rec['coefficient']);nw['B'][i]=['add',e[1],s,q.numerator,q.denominator,list(frame)]
      np=p.chain_profile(nw);delta=Counter(np);delta.subtract(old)
      rec['profile_delta']={k:c for k,c in delta.items() if c};rec['entropy_delta']=sum(k*c*__import__('math').log2(k) for k,c in delta.items());stats['frame_feasible']+=1
     result.append(rec)
  a.apply(e,rows)
  for r in a.registers(e):cur[r]=a.basis(e[-1])
result.sort(key=lambda r:(not r['frame_feasible'],-r.get('entropy_delta',0)))
out={'stats':dict(stats),'candidates':result}
(Path(__file__).resolve().parent/'SOURCE-CENSUS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
