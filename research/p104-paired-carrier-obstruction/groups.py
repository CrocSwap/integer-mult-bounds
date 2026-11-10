from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
import gzip,json,itertools
base=HERE
w=json.load(gzip.open(base/'inputs/PR6702-WORD.json.gz'));p=w['program'];n=w['public'];N=n+w['owned_fields'];MOD=65521
scalar=lambda x:Q(x).numerator*pow(Q(x).denominator,-1,MOD)%MOD
s=(HERE/'retained/single_search.py').read_text();exec(s[s.index('writes='):s.index('# Check the actual old-input')])
rows=[{r:Q(1)}if r<n else{}for r in range(N)];at=defaultdict(list)
for c in intervals:at[c['first']].append(c)
def axpy(a,b,q):
 for k,v in b.items():
  z=a.get(k,Q(0))+q*v
  if z:a[k]=z
  else:a.pop(k,None)
for i,e in enumerate(p):
 for c in at[i]:c['v']=rows[c['role']].copy()
 op,r=e[:2]
 if op in ('INIT','CLEAR'):rows[r]={}
 elif op=='SCALE':rows[r]={k:q*Q(e[2])for k,q in rows[r].items()}
 elif op in ('ADD','COPY'):axpy(rows[r],rows[e[2]],Q(e[3]))
expected=[{r:Q(1)}if r<n else{}for r in range(N)]
for r in w['live']:expected[r+112][r]=Q(1)
if rows!=expected:raise ValueError('Exact all-input source endpoint')
for c in intervals:
 if not any(scalar(q)for q in c['v'].values()):raise ValueError('Zero modular held row')
for e in p:
 if e[0]=='SCALE'and not scalar(e[2]):raise ValueError('Nonunit source SCALE')
groups=defaultdict(list)
for c in intervals:
 v=c['v'];a=v[min(v)];key=tuple(sorted((r,q/a)for r,q in v.items()));c['norm']=a;groups[key].append(c)
st=Counter();pairs=[]
for v,cs in groups.items():
 for a,b in itertools.combinations(cs,2):
  if a['first']>b['first']:a,b=b,a
  st['pairs']+=1;st['same_role']+=a['role']==b['role'];st['adjacent_shared_move']+=a['second']==b['first'];st['disjoint_moves']+=a['second']<b['first']
  if a['role']==b['role']:
   changes=[(i,e)for i,e in writes[a['role']]if a['first']<i<b['second'] and e[0]not in ('MOVE','SCALE')]
   if not changes:st['same_role_no_writes']+=1;pairs.append((a,b))
print('GROUPS',len(groups),'SIZES',dict(Counter(len(x)for x in groups.values())),'PAIRS',dict(st),flush=True)
for a,b in pairs:print('PAIR',a['role'],a['first'],a['second'],b['first'],b['second'],[a[k]for k in ('E','F','G')],[b[k]for k in ('E','F','G')],flush=True)
