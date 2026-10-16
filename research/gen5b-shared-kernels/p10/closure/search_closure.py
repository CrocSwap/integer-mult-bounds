"""Bounded190-line/two-order screen, fully charging donor activations.

Integer maxflow optimizes a rounded finite-exponent moment surrogate. Exact
candidate pricing and physical admission remain separate checks.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collections import defaultdict,Counter,deque
from itertools import combinations
from fractions import Fraction as Q
import gzip,json,math,time,hashlib
from source_contract import ROOT,SOURCE,HEAD,verify_inputs

def read(name):
 raw=(SOURCE/name).read_bytes();return json.loads(gzip.decompress(raw)if name.endswith('.gz')else raw)
def annihilator(frame):
 if 'a'in frame:return frame['a']
 A=[[Q(x)for x in row]for row in frame['b']];piv=[];k=0
 for j in range(20):
  p=next((i for i in range(k,len(A))if A[i][j]),None)
  if p is None:continue
  A[k],A[p]=A[p],A[k];d=A[k][j];A[k]=[x/d for x in A[k]]
  for i in range(len(A)):
   if i!=k:
    d=A[i][j]
    if d:A[i]=[x-d*y for x,y in zip(A[i],A[k])]
  piv.append(j);k+=1
 out=[]
 for j in range(20):
  if j in piv:continue
  v=[Q(0)]*20;v[j]=1
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
 start=time.monotonic();pins=verify_inputs()
 w=read('bitword/selected/bit/word_p10.json.gz');f={int(k):v for k,v in read('bitword/selected/bit/frames_p10.json.gz')['frames'].items()}
 cache=json.loads(gzip.decompress((ROOT/'response-cache.json.gz').read_bytes()));rows={int(r):z for r,z in cache['roles'].items()}
 assert cache['source_head']==HEAD and cache['installed_response_and_cut_checks']==775
 response={r:int(z['response_hex'],16)for r,z in rows.items()};members={s for z in cache['installed_entries']for s in[z['physical_pivot']]+z['physical_donors']}
 descended={s for z in read('descent-selection.json')['entries']for s in z['scalar'][:2]};restored={z['helper']for z in read('restore-selection.json')['entries']};sink=read('sink-selection.json')['sinks'];sunk={z['role']for z in sink};sources=set(w['sources'].values())
 removed_streams={z['stream']for z in sink};pre_slots=[s for s in range(1920,10150)if s not in removed_streams]
 assert len(pre_slots)==8223
 lift=lambda s:s if s<1920 else pre_slots[s-1920]
 reorders=read('reorder-selection.json');reordered={lift(s)for z in reorders['moves']for s in z['incidence'][:2]if s>=1920}
 first={r:z['first_base_use']['frame']for r,z in rows.items()if z['first_base_use']}
 baseeligible=[r for r,z in rows.items()if not z['is_gauge']and r not in sunk|sources and z['stream']not in members|descended|restored and r in first and z['initial_read_count']>0]
 eligible=[r for r in baseeligible if rows[r]['stream']not in reordered]
 byframe=defaultdict(list)
 for r in eligible:byframe[first[r]].append(r)
 groups={pair:[]for pair in combinations(range(20),2)}
 for frame,roles in byframe.items():
  A=annihilator(f[frame]);columns=defaultdict(list)
  for j in range(20):columns[tuple(row[j]for row in A)].append(j)
  for same in columns.values():
   for pair in combinations(same,2):groups[pair]+=roles
 a=769791094751301/10**18;m=100
 # Subtracting linear rank accounts for the equal width-stock decrease.
 # The exact same per-call fallback term is included for every positive child.
 bad=32*m*m/10**16*math.exp(a*math.log(m))/a
 phi=lambda r:0 if not r else r*math.expm1(a*math.log(m/r))/a+bad
 results=[];candidates=[]
 for ordername in ('role_ascending','dimension_descending_then_role'):
  for line,rs in groups.items():
   dimensions={r:f[first[r]]['dim']for r in rs}
   rs=sorted(rs,key=(lambda r:r)if ordername=='role_ascending'else(lambda r:(-dimensions[r],r)))
   basis={};donors=[];relations=[]
   for role in rs:
    value=response[role];co=0
    while value:
     k=value.bit_length()-1
     if k not in basis:
      j=len(donors);donors.append(role);basis[k]=(value,co^(1<<j));break
     old,oldco=basis[k];value^=old;co^=oldco
    if not value:
     ds=[d for j,d in enumerate(donors)if co>>j&1]
     assert ds
     x=response[role]
     for d in ds:x^=response[d]
     assert x==0
     relations.append(dict(pivot=role,donors=ds))
   chosen,profit=closure(relations,dimensions,phi)
   variants=[]
   # Retain one explicit endpoint for each residue, rather than dropping all
   # nonzero residues. At most four deterministic marginal removals, no new bases.
   for removals in range(min(4,len(chosen))+1):
    used={d for z in chosen for d in z['donors']};active={z['pivot']for z in chosen}|used;H=Counter()
    for role in active:
     d=dimensions[role];H[d]-=1
     if d>1:H[d-1]+=1
    H[1]+=len(used);H={r:n for r,n in sorted(H.items())if n};score=sum(n*phi(r)for r,n in H.items())
    assert sum(r*n for r,n in H.items())==-len(chosen)
    row=dict(order=ordername,line=list(line),pivots=len(chosen),donors=len(used),members=len(active),mod5=len(chosen)%5,removed_for_residue=removals,local_histogram_delta=H,finite_exponent_surrogate_delta=score,setup_pairs=sum(len(z['donors'])for z in chosen),reused_donor_members=sum('reuse'in rows[r]for r in active))
    variants.append(row)
    if chosen and score<0:
     candidates.append(dict(**row,relations=chosen[:]))
    if not chosen or removals==4:break
    uses=Counter(d for z in chosen for d in z['donors'])
    def margin(z):
     benefit=phi(dimensions[z['pivot']])-phi(dimensions[z['pivot']]-1)
     released=sum(phi(1)+phi(dimensions[d]-1)-phi(dimensions[d])for d in z['donors']if uses[d]==1)
     return benefit-released
    drop=min(range(len(chosen)),key=lambda i:(margin(chosen[i]),chosen[i]['pivot']))
    chosen=chosen[:drop]+chosen[drop+1:]
   results.append(dict(order=ordername,line=list(line),helpers=len(rs),response_rank=len(donors),nullity=len(relations),rounded_closure_profit=profit,variants=variants))
 def key(z):return(z['finite_exponent_surrogate_delta'],z['line'],z['order'])
 candidates.sort(key=key)
 summary=dict(status='COMPLETE_BOUNDED_190_LINE_TWO_ORDER_SCREEN',source_head=HEAD,
  eligible_before_reorder_guard=len(baseeligible),eligible_after_reorder_guard=len(eligible),eligible_reused_physical_donors=sum('reuse'in rows[r]for r in eligible),reorder_guard_excluded=len(baseeligible)-len(eligible),
  lines=190,donor_orders=2,basis_screens=len(results),nonzero_nullity_screens=sum(r['nullity']>0 for r in results),positive_variants=len(candidates),
  positive_mod0=sum(z['mod5']==0 for z in candidates),best_by_residue={str(k):next(({a:b for a,b in z.items()if a!='relations'}for z in candidates if z['mod5']==k),None)for k in range(5)},
  cache_sha256=hashlib.sha256((ROOT/'response-cache.json.gz').read_bytes()).hexdigest(),source_inputs=pins,
  scope='Unused physical slots only, including reuse donors; all installed/descended/restored/sink/source/gauged and conservatively all moved reorder operand slots excluded.190 coordinate contrasts, two fixed basis orders and at most four marginal removals per closure. Full donor activation costs and finite-exponent fallback-call terms included. Positive rounded surrogate is not exact pricing or physical admission.')
 (ROOT/'screen-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 (ROOT/'line-receipts.json').write_text(json.dumps(results,indent=2)+'\n')
 (ROOT/'positive-candidates.json').write_text(json.dumps(candidates,indent=2)+'\n')
 print(json.dumps({k:v for k,v in summary.items()if k not in('source_inputs',)},indent=2));return summary
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 run()
