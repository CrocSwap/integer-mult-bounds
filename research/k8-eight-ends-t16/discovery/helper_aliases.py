import sys,json,gzip,copy,importlib.util,math
from pathlib import Path
from fractions import Fraction as F
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
BASE=ROOT/'research/k8-eight-ends/FULL-WORD.json.gz'
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a=mod('a',ROOT/'research/gauge44-slots/independent/audit_local.py');p=mod('p',ROOT/'research/gauge44-slots/construction/promo/build_promotion.py');w=json.loads(gzip.decompress(BASE.read_bytes()));v=112;n=704;FULL=a.basis([1<<i for i in range(9)])
ends=[FULL]*v+[a.basis([x for x in range(1,512) if (x&port).bit_count()%2==0]) for port in w['ports']]+[FULL]*480
for r,fr in w['helper_final'].items():ends[int(r)]=a.basis(fr)
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
 ss=sorted(row);q=row[ss[0]];return tuple((i,row[i]/q) for i in ss),q
result=[];stats=Counter();old=p.chain_profile(w)
for sec in ['A','B']:
 if sec=='B':
  for e in w['cut']:a.apply(e,rows)
 for i,e in enumerate(w[sec]):
  if sec=='B' and e[0]=='add' and v<=e[1]<2*v and e[2]>=2*v:
   stats['helper_target_reads']+=1;hk,hq=key(rows[e[2]])
   for s in list(range(v))+list(range(2*v,n)):
    if s==e[2]:continue
    sk,sq=key(rows[s])
    if hk is not None and sk==hk:
     stats['clean_aliases']+=1;fr=a.basis(list(cur[s])+list(cur[e[1]]));feasible=a.contained(fr,nexts[i][s]) and a.contained(fr,nexts[i][e[1]])
     if not feasible:
      result.append(dict(B=i,target=e[1],helper=e[2],source=s,coefficient=str(F(e[3],e[4])*hq/sq),frame=list(fr),frame_feasible=False));continue
     stats['frame_feasible']+=1;rec=dict(B=i,target=e[1],helper=e[2],source=s,coefficient=str(F(e[3],e[4])*hq/sq),frame=list(fr));nw=copy.deepcopy(w);q=F(rec['coefficient']);nw['B'][i]=['add',e[1],s,q.numerator,q.denominator,list(fr)];np=p.chain_profile(nw);delta=Counter(np);delta.subtract(old);rec['profile_delta']={k:c for k,c in delta.items() if c};rec['entropy_delta']=sum(k*c*math.log(k) for k,c in delta.items());result.append(rec)
  a.apply(e,rows)
  for r in a.registers(e):cur[r]=a.basis(e[-1])
result.sort(key=lambda r:-r.get('entropy_delta',-1e9));out=dict(stats=dict(stats),candidates=result);(P/'HELPER-ALIASES.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(stats=dict(stats),top=[r for r in result if r.get('profile_delta')][:20]),indent=2))
# Helpers with no non-target reads and hence candidates for complete removal.
uses=defaultdict(list);writes=defaultdict(list)
for sec in ['A','B']:
 for i,e in enumerate(w[sec]):
  writes[e[1]].append((sec,i,e))
  if e[0]=='add':uses[e[2]].append((sec,i,e))
retire=[dict(helper=h,writes=writes[h],reads=uses[h]) for h in range(224,n) if uses[h] and all(112<=e[1]<224 for sec,i,e in uses[h])]
(P/'RETIRABLE-HELPERS.json').write_text(json.dumps(retire,indent=2)+'\n');print('target-only helpers',len(retire))
