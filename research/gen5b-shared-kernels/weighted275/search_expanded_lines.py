"""Bounded 276-line shared-donor screen on the exact weighted word.

Only unused physical roles are considered; reused donor slots are permitted.
The rounded closure objective is a screen, not the certified exponent or finite
payload admission. Candidate relations still require full aliased path checks.
"""
from pathlib import Path
from collections import defaultdict,Counter,deque
from itertools import combinations
from fractions import Fraction as Q
import json,gzip,math,time
from source_data import ROOT,SOURCE,OUTPUT
def read(name):
    raw=(SOURCE/name).read_bytes()
    return json.loads(gzip.decompress(raw)if name.endswith('.gz')else raw)
def annihilator(frame):
 if 'a'in frame:return frame['a']
 A=[[Q(x)for x in row]for row in frame['b']];piv=[];k=0
 for j in range(24):
  p=next((i for i in range(k,len(A))if A[i][j]),None)
  if p is None:continue
  A[k],A[p]=A[p],A[k];d=A[k][j];A[k]=[x/d for x in A[k]]
  for i in range(len(A)):
   if i!=k:
    d=A[i][j]
    if d:A[i]=[x-d*y for x,y in zip(A[i],A[k])]
  piv.append(j);k+=1
 out=[]
 for j in range(24):
  if j in piv:continue
  v=[Q(0)]*24;v[j]=1
  for i,p in enumerate(piv):v[p]=-A[i][j]
  out.append(v)
 assert len(piv)==frame['dim']
 return out
def closure(pivots,dimension,phi,entrance=1):
 """Exact max flow for the declared 10^9-rounded integer surrogate weights."""
 ds=sorted({d for z in pivots for d in z['donors']});di={d:i for i,d in enumerate(ds)}
 np=len(pivots);nd=len(ds);source=np+nd;sink=source+1;N=sink+1;G=[[]for _ in range(N)]
 benefit=[round((phi(dimension[z['pivot']])-phi(dimension[z['pivot']]-entrance))*10**9)for z in pivots]
 cost=[round((phi(entrance)+phi(dimension[d]-entrance)-phi(dimension[d]))*10**9)for d in ds]
 assert min(benefit,default=0)>=0 and min(cost,default=0)>=0
 infinity=sum(benefit)+sum(cost)+1
 def edge(a,b,c):G[a].append([b,c,len(G[b])]);G[b].append([a,0,len(G[a])-1])
 for i,b in enumerate(benefit):
  edge(source,i,b)
  for d in pivots[i]['donors']:edge(i,np+di[d],infinity)
 for i,c in enumerate(cost):edge(np+i,sink,c)
 flow=0
 while True:
  levels=[-1]*N;levels[source]=0;q=deque([source])
  while q:
   a=q.popleft()
   for b,c,rev in G[a]:
    if c and levels[b]<0:levels[b]=levels[a]+1;q.append(b)
  if levels[sink]<0:break
  at=[0]*N
  def dfs(a,push):
   if a==sink:return push
   while at[a]<len(G[a]):
    e=G[a][at[a]];b,c,rev=e
    if c and levels[b]==levels[a]+1:
     z=dfs(b,min(push,c))
     if z:e[1]-=z;G[b][rev][1]+=z;return z
    at[a]+=1
   return 0
  while True:
   z=dfs(source,infinity)
   if not z:break
   flow+=z
 seen={source};q=deque([source])
 while q:
  a=q.popleft()
  for b,c,rev in G[a]:
   if c and b not in seen:seen.add(b);q.append(b)
 chosen=[z for i,z in enumerate(pivots)if i in seen]
 return chosen,sum(benefit)-flow
def run():
 start=time.monotonic();w=read('gen5bit/selected/bit/word_p12.json.gz');f={int(k):v for k,v in read('gen5bit/selected/bit/frames_p12.json.gz')['frames'].items()}
 cache=json.loads(gzip.decompress((OUTPUT/'response-cache.json.gz').read_bytes()));rows={int(r):z for r,z in cache['roles'].items()}
 resp={r:int(z['response_hex'],16)for r,z in rows.items()};stream={r:z['stream']for r,z in rows.items()}
 members={s for z in cache['installed_entries']for s in[z['physical_pivot']]+z['physical_donors']};changed=set()
 for name in('descent-selection.json','descent2-selection.json'):
  for z in read(name)['entries']:changed.update(z['scalar'][:2])
 restored={z['helper']for z in read('restore-selection.json')['entries']};sunk={z['role']for z in read('sink-selection.json')['sinks']};sources=set(w['sources'].values())
 first={r:z['first_base_use']['frame']for r,z in rows.items()if z['first_base_use']}
 eligible=[r for r,z in rows.items()if not z['is_gauge']and r not in sunk|sources and z['stream']not in members|changed|restored and r in first and z['initial_read_count']>0]
 assert len(eligible)==8085 and sum('reuse'in rows[r]for r in eligible)==1591
 byframe=defaultdict(list)
 for r in eligible:byframe[first[r]].append(r)
 groups={pair:[]for pair in combinations(range(24),2)}
 for frame,roles in byframe.items():
  A=annihilator(f[frame]);columns=defaultdict(list)
  for j in range(24):columns[tuple(row[j]for row in A)].append(j)
  for same in columns.values():
   for pair in combinations(same,2):groups[pair]+=roles
 phi=lambda r:0 if not r else r*math.log(120/r)
 results=[]
 for line,rs in groups.items():
  rs=sorted(rs);basis={};donors=[];pivots=[]
  for role in rs:
   value=resp[role];co=0
   while value:
    k=value.bit_length()-1
    if k not in basis:
     j=len(donors);donors.append(role);basis[k]=(value,co^(1<<j));break
    old,oldco=basis[k];value^=old;co^=oldco
   if not value:
    ds=[d for j,d in enumerate(donors)if co>>j&1]
    x=resp[role]
    for d in ds:x^=resp[d]
    assert not x
    pivots.append(dict(pivot=role,donors=ds))
  # Globally select dependent pivots while charging each basis donor once.
  dimensions={r:f[first[r]]['dim']for r in rs}
  pivots,integer_profit=closure(pivots,dimensions,phi)
  # Only actually used basis donors pay a new entrance split.
  used={d for z in pivots for d in z['donors']}
  # Require an even rank drop for integral full-bank retiling.
  if len(pivots)%2:
   counts=Counter(d for z in pivots for d in z['donors'])
   def gain(z):
    benefit=phi(dimensions[z['pivot']])-phi(dimensions[z['pivot']]-1)
    released=sum(phi(1)+phi(dimensions[d]-1)-phi(dimensions[d])for d in z['donors']if counts[d]==1)
    return benefit-released
   omitted=min(range(len(pivots)),key=lambda i:gain(pivots[i]))
   pivots=pivots[:omitted]+pivots[omitted+1:];used={d for z in pivots for d in z['donors']}
  active=[z['pivot']for z in pivots]+sorted(used);H=Counter()
  for r in active:
   dim=f[first[r]]['dim'];H[dim]-=1
   if dim>1:H[dim-1]+=1
  H[1]+=len(used);H={r:n for r,n in H.items()if n}
  score=sum(n*phi(r)for r,n in H.items())
  assert sum(r*n for r,n in H.items())==-len(pivots)
  results.append(dict(line=line,helpers=len(rs),response_rank=len(donors),nullity=len(rs)-len(donors),
    selected_pivots=len(pivots),used_donors=len(used),local_histogram_delta=H,phi_delta=score,rounded_closure_profit=integer_profit,
    relations=pivots if score<0 else [],setup_restore_pairs=sum(len(z['donors'])for z in pivots),reused_donor_slot_members=[r for r in active if'reuse'in rows[r]]))
 positive=[z for z in results if z['selected_pivots']and z['phi_delta']<0]
 return dict(status='COMPLETE_276_LINE_WEIGHTED_UNUSED_ROLE_SCREEN',source_head='10b40041d4ab8a6610083e95bc571aee3468bca2',
  eligible_unused_helpers=len(eligible),eligible_reused_donors=1591,lines_tested=len(results),lines_with_nonzero_nullity=sum(z['nullity']>0 for z in results),
  phi_improving_groups=len(positive),best_candidates=sorted(positive,key=lambda z:z['phi_delta'])[:10],
  all_line_receipts=[{k:v for k,v in z.items()if k!='relations'}for z in results],seconds=time.monotonic()-start,
  scope='Exact F2 rank and first-entrance histogram screen on276 contrast lines for8085 unused physical roles, including1591 reused donor slots. Both descents, old kernel members, early restored endpoints, sources and sinks are excluded. Rounded maxflow optimizes a floating entropy surrogate, not final exponent. Every selected alias requires chronological/frame/scalar/packing/chart/finite-payload admission; cap must not be inferred from entropy score.')
if __name__=='__main__':
 r=run();(OUTPUT/'expanded-line-screen.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps({k:v for k,v in r.items()if k not in('best_candidates','all_line_receipts')},indent=2))
 print(json.dumps([{k:v for k,v in x.items()if k!='relations'}for x in r['best_candidates'][:5]],indent=2))
