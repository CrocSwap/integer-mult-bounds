"""Separate column transport and explicit GF(2) span oracle; no verifier imports."""
from fractions import Fraction
from functools import lru_cache

@lru_cache(None)
def span(b):
 out={0}
 for x in b:out|={y^x for y in tuple(out)}
 return frozenset(out)

@lru_cache(None)
def join(a,b):return frozenset(x^y for x in a for y in b)

def verify_contexts(w,contexts,enter):
 # Reconstruct entering-dirt columns from the source, without sparse row updates.
 n=224+w['report']['R'];sites={c['index']:c for c in contexts.values()}
 for helper in enter:
  v=[Fraction(int(i==helper)) for i in range(n)]
  def step(e):
   if e[0]=='add':v[e[1]]+=Fraction(e[3],e[4])*v[e[2]]
   else:v[e[1]]*=Fraction(e[2],e[3])
  for e in w['A']+w['cut']:step(e)
  for i,e in enumerate(w['B'][:max(sites)+21]):
   if i in sites:
    c=sites[i]
    if any(v[z]!=c['dirt'][j].get(helper,0) for j,z in enumerate(c['registers'])):
     raise ValueError('independent entry column')
   step(e)
 cur=[span((p,)) for p in w['ports']]+[frozenset({0}) for _ in range(n-112)]
 for r,b in w['start_extra'].items():cur[int(r)]=span(tuple(b))
 for part in ('A','B'):
  for i,e in enumerate(w[part]):
   if part=='B' and i in sites:
    c=sites[i]
    if any(cur[z]!=span(tuple(c['entry'][j])) for j,z in enumerate(c['registers'])):
     raise ValueError('independent entry frames')
   f=span(tuple(e[-1]))
   for z in e[1:3] if e[0]=='add' else e[1:2]:
    if not cur[z]<=f:raise ValueError('source frame nonmonotone')
    cur[z]=f
   if part=='B' and i-20 in sites:
    c=sites[i-20]
    if any(cur[z]!=span(tuple(c['exit'][j])) for j,z in enumerate(c['registers'])):
     raise ValueError('independent exit caps')

def check(ops,ctx,C):
 # Apply each basis input as a numeric column, unlike sparse row accumulation.
 cols=[]
 for j in range(12):
  v=[Fraction(int(i==j)) for i in range(12)]
  for _,t,s,a,b in ops:v[t]+=Fraction(a,b)*v[s]
  cols.append(v)
 if any(cols[j][i+6]!=C[i][j] for i in range(6) for j in range(6)):
  raise ValueError('column clean transfer')
 keys=set().union(*(x.keys() for x in ctx['dirt']))
 dirty=True
 for k in keys:
  for i in range(6):
   val=sum(cols[j][i+6]*ctx['dirt'][j].get(k,0) for j in range(12))
   if val!=ctx['reference_dirt'][i].get(k,0):dirty=False
 # Enumerate actual 9-bit vectors, no Gaussian elimination / rank routine.
 cur=[span(tuple(x)) for x in ctx['entry']]
 cap=[span(tuple(x)) for x in ctx['exit']]
 legal=True
 for _,t,s,_,_ in ops:
  joined=join(cur[t],cur[s])
  if not joined<=cap[t] or not joined<=cap[s]:legal=False
  cur[t]=cur[s]=joined
 return dirty,legal
