"""Successor discovery on #7105: explicit boundary group, one retimed role only.
Parameterized boundary-group ranks by OpenAI Codex for dillona; retains predecessor authors below.

Optional finite discovery; the verifier does not trust this search.

Helper kernel/basis methods: Ali Romman. Paid main-path retiming extension:
Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Floating point only screens candidates; accepted constructions receive exact
whole-word, phase, invoice and complete conditional-parameter verification.
"""
import gzip,json,sys,time
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict,Counter
sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import L
add,span=L.add,L.span
from split import basis

def pure_combinations(rows, roles, group):
    """Eliminate coordinates outside the group; retain field coefficients."""
    pivots, output = {}, []
    for role in roles:
        outside = {k:v for k,v in rows[role].items() if k not in group}
        inside = {k:v for k,v in rows[role].items() if k in group}
        coefficients = {role:Q(1)}
        while outside:
            pivot = min(outside)
            if pivot not in pivots:
                scale = 1/outside[pivot]
                pivots[pivot] = [{k:v*scale for k,v in row.items()}
                                 for row in (outside, inside, coefficients)]
                break
            scale = -outside[pivot]
            for target, source in zip((outside, inside, coefficients), pivots[pivot]):
                add(target, source, scale)
        if not outside and inside:
            output.append((inside, coefficients))
    return output


def dyadic_program(program):
    for event in program:
        q = Q(event[-2])
        numerator, denominator = abs(q.numerator), q.denominator
        if denominator & (denominator-1):
            return False
        if event[0] == 'SCALE' and numerator & (numerator-1):
            return False
    return True



def encode(value):
 if isinstance(value,Q):return str(value)
 if isinstance(value,dict):return {str(k):encode(v)for k,v in value.items()}
 if isinstance(value,(tuple,list)):return [encode(x)for x in value]
 return value

HERE=Path(__file__).parent
w=json.loads(gzip.decompress((Path(sys.argv[1])).read_bytes()))
n=w['public'];N=n+w['owned_fields'];main=set(w['live'])|{r+112 for r in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
U,V=map(int,sys.argv[3:5]);group={r for r in range(n)if r not in main and(w['initial'][r],w['final'][r])==(U,V)}
spans=[span(b)for b in w['frames']];dims=list(map(len,w['frames']))
contacts=defaultdict(list);moves=defaultdict(list)
for i,e in enumerate(w['program']):
 if e[0]=='MOVE':moves[e[1]].append(i)
 else:
  contacts[e[1]].append(i)
  if e[0]in('ADD','COPY'):contacts[e[2]].append(i)
t=1-.00363216151
windows=[];starts=defaultdict(list);ends=defaultdict(list)
for r in range(N):
 touches=[-1]+contacts[r]+[len(w['program'])]
 for lo,hi in zip(touches,touches[1:]):
  mi=[i for i in moves[r]if lo<i<hi]
  if not mi:continue
  a,b=w['program'][mi[0]][2],w['program'][mi[-1]][3]
  paid=[abs(dims[w['program'][i][3]]-dims[w['program'][i][2]])for i in mi]
  for f,F in enumerate(spans):
   if not(spans[U]<F<spans[V]) or not(spans[a]<=F<=spans[b]or spans[b]<=F<=spans[a]):continue
   d1,d2=abs(dims[f]-dims[a]),abs(dims[b]-dims[f]);cost=d1**t+d2**t-sum(d**t for d in paid)
   maxgain=(dims[f]-dims[U])**t+(dims[V]-dims[f])**t-(dims[V]-dims[U])**t
   if cost>=maxgain-1e-12:continue
   h=dict(role=r,lo=lo+1,hi=hi,frame=f,old=a,new=b,moves=mi,old_paid=paid,new_paid=[d1,d2],cost=cost,private=r>=n)
   idx=len(windows);windows.append(h);starts[lo+1].append(idx);ends[hi+1].append(idx)
print('windows',len(windows),flush=True)
rows=[{r:Q(1)}if r<n else{}for r in range(N)];at=defaultdict(set)
for r,f in enumerate(w['initial']):at[f].add(r)
active=defaultdict(dict);snapshots=defaultdict(list);systems=0;start=time.time()
for cut in range(len(w['program'])+1):
 changed=set()
 for idx in ends.get(cut,[]):
  h=windows[idx];active[h['frame']].pop(h['role']);changed.add(h['frame'])
 for idx in starts.get(cut,[]):
  h=windows[idx];active[h['frame']][h['role']]=idx;changed.add(h['frame'])
 if cut:
  e=w['program'][cut-1];op,r=e[:2]
  if op=='MOVE':old,new=e[2:4];at[old].remove(r);at[new].add(r);changed|={old,new}
  elif op=='INIT':rows[r]={};at[e[2]].add(r);changed.add(e[2])
  elif op=='CLEAR':rows[r]={};at[e[2]].remove(r);changed.add(e[2])
  elif op=='SCALE':rows[r]={k:v*Q(e[2])for k,v in rows[r].items()};changed.add(e[-1])
  elif op in('ADD','COPY'):
   if op=='COPY':rows[r]={}
   add(rows[r],rows[e[2]],Q(e[3]));changed.add(e[-1])
 for f in sorted(changed):
  if f in(U,V)or not active[f]:continue
  pool=at[f]|set(active[f])
  pivots=pool&group
  if not pivots:continue
  roles=sorted(pool,key=lambda r:(r not in at[f],active[f].get(r,0),r));systems+=1
  prefix=pure_combinations(rows,roles,group)
  if prefix:snapshots[cut].append((f,roles,prefix,{r:idx for r,idx in active[f].items() if r not in at[f]},sorted(pivots)))
 if cut%5000==0:print('forward',cut,'systems',systems,'saved',sum(map(len,snapshots.values())),'sec',round(time.time()-start,2),flush=True)
print('prefix done',systems,'saved',sum(map(len,snapshots.values())),'sec',time.time()-start,flush=True)
cols=[{r:Q(1)}if r<n else{}for r in range(N)];hits=[];seen=set();pairs=0
for cut in range(len(w['program']),-1,-1):
 for f,roles,prefix,changes,pivots in snapshots.get(cut,[]):
  suffix=pure_combinations(cols,roles,group)
  gain=(dims[f]-dims[U])**t+(dims[V]-dims[f])**t-(dims[V]-dims[U])**t
  for c,a in prefix:
   for rd,rb in suffix:
    pair=sum(v*rd.get(k,0)for k,v in c.items())
    if not pair:continue
    b={k:v/pair for k,v in rb.items()};d={k:v/pair for k,v in rd.items()}
    if sum(v*b.get(k,0)for k,v in a.items())!=1:continue
    pairs+=1
    support=set(a)|set(b);p=min(pivots,key=lambda r:windows[changes[r]]['cost']if r in changes and r not in support else 0)
    used=[changes[r]for r in support|{p}if r in changes]
    cost=sum(windows[idx]['cost']for idx in used)
    if cost>=gain-1e-12 or len(used)!=1:continue
    if not dyadic_program(basis(c,d,p,U)+basis(a,b,p,f)):continue
    key=(f,p,tuple(sorted(c.items())),tuple(sorted(d.items())),tuple(sorted(a.items())),tuple(sorted(b.items())))
    if key in seen:continue
    seen.add(key);hits.append(dict(frame=f,pivot=p,cut=cut,ranks=[dims[f]-dims[U],dims[V]-dims[f]],gain=gain-cost,paths=[windows[idx]for idx in used],a=a,b=b,c=c,d=d))
 if cut:
  e=w['program'][cut-1];op,r=e[:2]
  if op in('INIT','CLEAR'):cols[r]={}
  elif op=='SCALE':cols[r]={k:v*Q(e[2])for k,v in cols[r].items()}
  elif op in('ADD','COPY'):
   add(cols[e[2]],cols[r],Q(e[3]))
   if op=='COPY':cols[r]={}
 if cut%5000==0:print('reverse',cut,'pairs',pairs,'hits',len(hits),'sec',round(time.time()-start,2),flush=True)
hits.sort(key=lambda h:-h['gain'])
(Path(sys.argv[2])).write_text(json.dumps(encode(hits),indent=2)+'\n')
print('paired',pairs,'hits',len(hits),'seconds',time.time()-start,flush=True)
for h in hits[:10]:print({k:v for k,v in encode(h).items()if k not in('a','b','c','d')},flush=True)
