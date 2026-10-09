"""Independent85-group target chronology, exact integer transfer and dual primes.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
Actual source490 and both scalar signs are checked separately by replay.py.
"""
from pathlib import Path
from collections import defaultdict,Counter
import importlib.util,sys,json,hashlib
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent
sp=importlib.util.spec_from_file_location('target_boundary490_setup',P/'extra/setup.py');setup=importlib.util.module_from_spec(sp);sp.loader.exec_module(setup)
m=setup.m;W=m.W;C=m.C;extra=setup.extra;extraroles={r['role']for r in extra}
selection=json.loads((D/'selection.json').read_text());groups=selection['groups'];owner={};roles=defaultdict(list);gs=[]
for i,g in enumerate(groups):
 ts=g['targets'];F=W.register(g['frame_basis']);assert len(ts)in(2,4)and g['pivot']in ts and C.nondeg(F)
 for t in ts:assert t not in owner;owner[t]=i;assert all(W.module.dot(C.cov[t],b)==0 for b in C.B[F])
 for role in g['roles']:
  assert role in W.gauge and set(ts)<=set(m.adj[role])and len({m.adj[role][t]for t in ts})==1
  assert C.sub(W.gauge[role]['frame'],F);roles[role].append(i)
 gs.append(dict(targets=ts,pivot=g['pivot'],roles=g['roles'],frame=F))
assert len(gs)==85 and len(owner)==316 and not(set(owner)&{t for z in m.terminal for t in z['targets']})
compact=lambda H:{str(k):v for k,v in sorted(H.items())if v}

def trace(aggregated,include_extra):
 paths=[[]for _ in range(W.v)];active=set(range(len(gs)))if aggregated else set();seen=[set()for _ in gs];restores=[];pivotreads=0;removedreads=0;events=0
 def move(t,f):
  nonlocal events
  assert C.nondeg(f)and(not paths[t]or C.sub(paths[t][-1],f));assert all(W.module.dot(C.cov[t],b)==0 for b in C.B[f]);paths[t].append(f);events+=1
 def gauge(s):
  nonlocal pivotreads,removedreads
  if not include_extra and s in extraroles:return
  grouped=roles.get(s,[])if aggregated else []
  for i in sorted({owner[t]for t in m.adj[s]if t in owner}):
   if i not in active or i in grouped:continue
   g=gs[i];assert seen[i]==set(g['roles'])
   for t in g['targets']:move(t,g['frame'])
   assert len({paths[t][-1]for t in g['targets']})==1
   active.remove(i);restores.append(dict(group=i,before_role=s,frame=g['frame']))
  skipped=set()
  for i in grouped:
   assert i in active and s not in seen[i];g=gs[i]
   move(g['pivot'],W.gauge[s]['frame']);seen[i].add(s);pivotreads+=1;skipped.update(g['targets']);removedreads+=len(g['targets'])-1
  for t in m.adj[s]:
   if t not in skipped:move(t,W.gauge[s]['frame'])
 for j,op in enumerate(W.rest):
  for s in m.at[j]:gauge(s)
  if op in m.bywrite:move(m.bywrite[op]['pivot'],W.opframe[op])
  if op in m.afterwrite:
   for t in m.afterwrite[op]['targets']:move(t,m.afterwrite[op]['root_frame'])
 for s in m.at[len(W.rest)]:gauge(s)
 assert not active
 for j,(root,role)in enumerate(zip(W.g['roots'],W.w['rootroles'])):
  if root['kind']=='side'and j not in m.deletedroots:
   for t in root['targets']:move(t,W.w['root_frame'][j])
  for e in m.deliveries[j]:
   for t in e['receivers']:move(t,e['deliver_frame'])
 H=Counter();R=Counter()
 for t,path in enumerate(paths):
  assert path;d=0
  for f in path:
   step=C.dimf[f]-d;assert step>=0
   if step:H[step]+=1
   d=C.dimf[f]
  assert d<=W.h-1
  if d<W.h-1:H[W.h-1-d]+=1
  previous=[C.cov[t]];d=1
  for f in reversed(path):
   assert all(W.module.dot(a,b)==0 for a in previous for b in C.B[f]);step=len(C.A[f])-d;assert step>=0
   if step:R[step]+=1
   previous=C.A[f];d=len(previous)
  if W.h>d:R[W.h-d]+=1
 assert H==R and sum(k*n for k,n in H.items())==W.v*(W.h-1)
 return dict(histogram=H,reflected=R,restores=restores,pivotreads=pivotreads,removedreads=removedreads,events=events)
base=trace(False,False);unaggregated=trace(False,True);final=trace(True,True)
oldprofile=json.loads((P/'newg/profile.json').read_text())['profile'];assert compact(base['histogram'])==oldprofile['physical_target_histogram']
scalar=json.loads((D/'replay.json').read_text())
for r in[scalar['F2']]+scalar['integer']:
 assert compact(final['histogram'])==r['actual_target_histogram']==r['actual_reflected_target_histogram']
 assert final['restores']==r['aggregation_restores']and final['pivotreads']==r['aggregation_pivot_reads']
# Exact local transfer over independent variables for arbitrary initial Y and
# arbitrary gauge-read values, including all recipients outside each group.
def add(a,c,b):
 ans=a.copy()
 for j,x in b.items():
  ans[j]=ans.get(j,0)+c*x
  if not ans[j]:del ans[j]
 return ans
def transfer(g,sign,mutation=None):
 ts=g['targets'];p=g['pivot'];alltargets=set(ts)|{t for s in g['roles']for t in m.adj[s]};y={t:{('Y',t):1}for t in alltargets};want={t:z.copy()for t,z in y.items()}
 for t in ts:
  if t!=p and mutation!='omit_setup':y[t]=add(y[t],-1,y[p])
 for s in g['roles']:
  z={('Z',s):1}
  for t,c in m.adj[s].items():
   want[t]=add(want[t],-sign*c,z)
   if t not in ts or t==p:y[t]=add(y[t],-sign*c,z)
  if mutation=='repeat_nonpivot':y[ts[-1]]=add(y[ts[-1]],-sign*m.adj[s][p],z)
 for t in ts:
  if t!=p and mutation!='omit_inverse':y[t]=add(y[t],1,y[p])
 assert y==want
for g in gs:
 for sign in(1,-1):transfer(g,sign)
controls=[]
for name in('omit_setup','omit_inverse','repeat_nonpivot'):
 try:transfer(gs[0],1,name)
 except AssertionError:controls.append(name)
 else:raise AssertionError('Local transfer corruption accepted: '+name)
def determinant(A):
 A=[list(r)for r in A];n=len(A)
 if not n:return 1
 den=1;sign=1
 for k in range(n-1):
  i=next((j for j in range(k,n)if A[j][k]),None)
  if i is None:return 0
  if i!=k:A[k],A[i]=A[i],A[k];sign=-sign
  pivot=A[k][k]
  for i in range(k+1,n):
   for j in range(k+1,n):
    x=A[i][j]*pivot-A[i][k]*A[k][j];assert x%den==0;A[i][j]=x//den
   A[i][k]=0
  den=pivot
 return sign*A[-1][-1]

def prime_record(B,dual=False):
 sums=list(map(sum,B));scale=9-W.h if dual else 9;sign=1 if dual else -1
 gram=[[scale*W.module.dot(x,y)+sign*sums[i]*sums[j]for j,y in enumerate(B)]for i,x in enumerate(B)]
 det=determinant(gram);assert det;rest=abs(det);powers={}
 for p in(2,3,5,7,11,13,17,19,23,29,31):
  exponent=0
  while rest%p==0:rest//=p;exponent+=1
  powers[str(p)]=exponent
 assert 0<rest<2**80
 check=rest
 for p,e in powers.items():check*=int(p)**e
 assert check==abs(det)
 return dict(dimension=len(B),cleared_determinant=det,small_prime_powers=powers,remaining_factor=rest)
primes=[dict(frame=f,basis=C.B[f],annihilator=C.A[f],primal=prime_record(C.B[f]),dual=prime_record(C.A[f],True))for f in sorted({g['frame']for g in gs})]
delta=Counter(final['histogram']);delta.subtract(base['histogram']);aggregate_delta=Counter(final['histogram']);aggregate_delta.subtract(unaggregated['histogram']);assert sum(k*n for k,n in delta.items())==0
setupcalls=sum(len(g['targets'])-1 for g in gs);assert setupcalls==231 and final['pivotreads']==98
result=dict(status='PASS_SOURCE490_85_TARGET_GROUPS_INDEPENDENT_CHRONOLOGY_BOTH_REFLECTIONS_INTEGER_TRANSFER_AND_PRIMES',groups=85,targets=316,pivot_reads=final['pivotreads'],old_complete_target_histogram=compact(base['histogram']),source490_unaggregated_target_histogram=compact(unaggregated['histogram']),new_complete_target_histogram=compact(final['histogram']),reflected_target_histogram=compact(final['reflected']),local_delta=compact(delta),aggregation_only_local_delta=compact(aggregate_delta),rank_mass_delta=0,setup_scalar_calls=setupcalls,inverse_scalar_calls=setupcalls,removed_gauge_reads=final['removedreads'],net_extra_scalar_calls=2*setupcalls-final['removedreads'],conservative_extra_fixed_calls=2*3*72*2*setupcalls,retained_fixed_call_bound=2**40,old_target_events=base['events'],new_target_events=final['events'],restores=final['restores'],prime_witnesses=primes,maximum_prime_residual=max(z[k]['remaining_factor']for z in primes for k in('primal','dual')),local_integer_both_signs=True,local_transfer_controls_rejected=controls,scope='Independent actual target chronology, equal-frame inverses before the first nonprefix read, exact all-variable local integer transfer, both complete ledgers and dual prime exclusions. Complete supplier and assembly checked separately.',input_pins={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(D/'selection.json',D/'word.py',D/'replay.py',P/'extra/setup.py',P/'extra/selection.json',Path(__file__))})
(D/'boundary.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS85 target groups,316targets, both reflected ledgers, both integer transfers and dual primes',compact(delta),flush=True)
