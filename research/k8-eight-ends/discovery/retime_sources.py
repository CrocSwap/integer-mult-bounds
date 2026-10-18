import os
import sys,json,gzip,copy,importlib.util,math
from pathlib import Path
from collections import defaultdict,Counter
from fractions import Fraction as F
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a=mod('a',ROOT/'research/gauge44-slots/independent/audit_local.py');p=mod('p',ROOT/'research/gauge44-slots/construction/promo/build_promotion.py')
w=json.loads(gzip.decompress(Path(os.environ['K8_BASE_WORD']).read_bytes()));v=112;n=704;FULL=a.basis([1<<i for i in range(9)])
cur=[(port,) for port in w['ports']]+[()]*(n-v)
for r,fr in w['start_extra'].items():cur[int(r)]=a.basis(fr)
rows=[{i:F(1)} if i<v else {} for i in range(n)]
def key(row):
 if not row:return None,None
 s=sorted(row);q=row[s[0]];return tuple((i,row[i]/q) for i in s),q
for e in w['A']:
 a.apply(e,rows)
 for r in a.registers(e):cur[r]=a.basis(e[-1])
for e in w['cut']:a.apply(e,rows)
slots=[];aliases=defaultdict(list);reads={};barriers=defaultdict(list)
for j in range(len(w['B'])+1):
 slots.append(cur.copy())
 for s in range(v):
  k,q=key(rows[s]);aliases[k].append((j,s,q))
 if j==len(w['B']):break
 e=w['B'][j]
 if e[0]=='add' and v<=e[1]<2*v and e[2]>=2*v:reads[j]=key(rows[e[2]])
 if e[0]=='scale' and v<=e[1]<2*v:barriers[e[1]].append(j)
 if e[0]=='add' and v<=e[2]<2*v:barriers[e[2]].append(j)
 a.apply(e,rows)
 for r in a.registers(e):cur[r]=a.basis(e[-1])
ends=[FULL]*v+[a.basis([x for x in range(1,512) if (x&port).bit_count()%2==0]) for port in w['ports']]+[FULL]*(n-2*v)
for r,fr in w['helper_final'].items():ends[int(r)]=a.basis(fr)
for ci,fr in reversed(w['early_cleanup']):
 for r in a.registers(w['cleanup'][ci]):ends[r]=a.basis(fr)
nexts=[None]*(len(w['B'])+1);nxt=ends.copy();nexts[-1]=nxt.copy()
for j in range(len(w['B'])-1,-1,-1):
 for r in a.registers(w['B'][j]):nxt[r]=a.basis(w['B'][j][-1])
 nexts[j]=nxt.copy()
old=p.chain_profile(w);records=[];stats=Counter()
for i,(k,q) in reads.items():
 if k is None:continue
 e=w['B'][i];t=e[1];lo=max([-1]+[j for j in barriers[t] if j<i])+1;hi=min([len(w['B'])]+[j for j in barriers[t] if j>i]);seen=set()
 for j,s,sq in aliases.get(k,[]):
  if not lo<=j<=hi:continue
  stats['algebraic_slots']+=1;fr=a.basis(list(slots[j][s])+list(slots[j][t]));sig=(s,fr,q/sq)
  if sig in seen:continue
  if not a.contained(fr,nexts[j][s]) or not a.contained(fr,nexts[j][t]):continue
  seen.add(sig);stats['frame_feasible_distinct']+=1
  c=F(e[3],e[4])*q/sq;gate=['add',t,s,c.numerator,c.denominator,list(fr)];nw=copy.deepcopy(w);nw['B']=[x for z in range(len(w['B'])+1) for x in (([gate] if z==j else [])+([w['B'][z]] if z<len(w['B']) and z!=i else []))];np=p.chain_profile(nw);delta=Counter(np);delta.subtract(old);score=sum(d*c*math.log(d) for d,c in delta.items());rec=dict(old_B=i,insert_before_B=j,target=t,helper=e[2],source=s,coefficient=str(c),frame=list(fr),entropy_delta=score,profile_delta={str(d):c for d,c in delta.items() if c});records.append(rec)
records.sort(key=lambda r:-r['entropy_delta']);(P/'RETIME-CENSUS.json').write_text(json.dumps(dict(stats=dict(stats),candidates=records),indent=2)+'\n');print(json.dumps(dict(stats=dict(stats),top=records[:12]),indent=2),flush=True)
