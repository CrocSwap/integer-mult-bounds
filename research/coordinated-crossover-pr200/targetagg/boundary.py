"""Independent literal target-chain, inverse-timing and exact prime audit.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
Source471 source/auxiliary words and paid banks are retained byte for byte.
"""
from pathlib import Path
from collections import defaultdict,Counter
import importlib.util,sys,json,hashlib
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent
sp=importlib.util.spec_from_file_location('boundary471',P/'newg/replay.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);W=m.W;C=m.C
selection=json.loads((D/'selection.json').read_text());groups=selection['groups'];target_group={};role_group={};gs=[]
for k,g in enumerate(groups):
 targets=g['targets'];pivot=g['pivot'];roles=g['roles'];f=W.register(g['frame_basis'])
 assert pivot in targets and len(set(targets))==4 and C.dimf[f]==21 and C.nondeg(f)
 for t in targets:assert t not in target_group;target_group[t]=k
 for s in roles:
  assert s not in role_group;role_group[s]=k
  assert set(m.adj[s])==set(targets)and len(set(m.adj[s].values()))==1
  assert C.sub(W.gauge[s]['frame'],f)
 gs.append(dict(targets=targets,pivot=pivot,roles=roles,frame=f))
terminaltargets={t for e in m.terminal for t in e['targets']};assert not(set(target_group)&terminaltargets)
assert len(role_group)==28 and len(gs)==27 and len(target_group)==108

def trace(aggregated):
 paths=[[]for _ in range(W.v)];seen=[set()for _ in gs];active=[aggregated]*len(gs);restores=[];events=0;early=0
 def move(t,f):
  nonlocal events
  if paths[t]:assert C.sub(paths[t][-1],f),('target nesting',t,C.dimf[paths[t][-1]],C.dimf[f])
  assert all(W.module.dot(C.cov[t],b)==0 for b in C.B[f]),('target cap',t,f)
  paths[t].append(f);events+=1
 def gauge(s):
  nonlocal early
  if aggregated and s in role_group:
   k=role_group[s];g=gs[k];assert active[k];move(g['pivot'],W.gauge[s]['frame']);seen[k].add(s);early+=1;return
  if aggregated:
   for k in sorted({target_group[t]for t in m.adj[s]if t in target_group}):
    if not active[k]:continue
    g=gs[k];assert seen[k]==set(g['roles'])
    # The first original gauge frame equals the joint inverse frame. Other
    # targets' next frames are checked by their actual subsequent move calls.
    assert C.sub(g['frame'],W.gauge[s]['frame'])and C.sub(W.gauge[s]['frame'],g['frame'])
    for t in g['targets']:move(t,g['frame'])
    active[k]=False;restores.append(dict(group=k,before_role=s,frame=g['frame']))
  for t in m.adj[s]:move(t,W.gauge[s]['frame'])
 for j,i in enumerate(W.rest):
  for s in m.at[j]:gauge(s)
  if i in m.bywrite:move(m.bywrite[i]['pivot'],W.opframe[i])
  if i in m.afterwrite:
   e=m.afterwrite[i]
   for t in e['targets']:move(t,e['root_frame'])
 for s in m.at[len(W.rest)]:gauge(s)
 assert not any(active)
 for j,(r,s)in enumerate(zip(W.g['roots'],W.w['rootroles'])):
  if r['kind']=='side'and j not in m.deletedroots:
   for t in r['targets']:move(t,W.w['root_frame'][j])
  for e in m.deliveries[j]:
   for t in e['receivers']:move(t,e['deliver_frame'])
 hist=Counter();reflected=Counter()
 for t,path in enumerate(paths):
  assert path;previous=0
  for f in path:
   d=C.dimf[f]-previous;assert d>=0
   if d:hist[d]+=1
   previous=C.dimf[f]
  if W.h-1>previous:hist[W.h-1-previous]+=1
  previous_basis=[C.cov[t]];dimension=1
  for f in reversed(path):
   assert all(W.module.dot(a,b)==0 for a in previous_basis for b in C.B[f])
   step=len(C.A[f])-dimension;assert step>=0
   if step:reflected[step]+=1
   previous_basis=C.A[f];dimension=len(previous_basis)
  if W.h>dimension:reflected[W.h-dimension]+=1
 assert hist==reflected and sum(d*n for d,n in hist.items())==W.v*(W.h-1)
 return hist,reflected,restores,events,early
old,_,_,old_events,_=trace(False);new,reflected,restores,new_events,pivotreads=trace(True)
delta=Counter(new);delta.subtract(old);delta={d:n for d,n in delta.items()if n}
assert delta=={int(k):n for k,n in selection['local_delta'].items()}
assert sum(d*n for d,n in delta.items())==0
scalar=json.loads((D/'replay.json').read_text())
for r in [scalar['F2']]+scalar['integer']:
 assert new=={int(k):n for k,n in r['actual_target_histogram'].items()}=={int(k):n for k,n in r['actual_reflected_target_histogram'].items()}
 assert r['aggregation_restores']==restores and r['aggregation_pivot_reads']==pivotreads==28
from prime_witnesses import det,factor_witness,validate_factor
primes=[]
for f in sorted({g['frame']for g in gs}):
 B=C.B[f];ss=list(map(sum,B));gram=[[9*sum(a*b for a,b in zip(x,y))-ss[i]*ss[j]for j,y in enumerate(B)]for i,x in enumerate(B)]
 determinant=det(gram);powers,residual=factor_witness(determinant);validate_factor(determinant,powers,residual)
 primes.append(dict(frame=f,dimension=len(B),basis=B,cleared_gram_determinant=determinant,small_prime_powers=powers,remaining_factor=residual))
compact=lambda h:{str(k):n for k,n in sorted(h.items())if n}
result=dict(status='PASS_TARGET_AGGREGATION_ACTUAL_CHAINS_REFLECTION_AND_PRIMES',scope='Independent target event order including original gauges, terminal writes/scatters, side roots and K; exact target inverses before the first original gauge, all primal/reflected inclusions, complete target histograms, exact Gram-factor exclusions. Source/auxiliary paid paths, charts and banks unchanged.',groups=27,targets=108,pivot_reads=pivotreads,old_complete_target_histogram=compact(old),new_complete_target_histogram=compact(new),reflected_target_histogram=compact(reflected),local_delta=compact(delta),rank_mass_delta=0,inverse_scalar_calls=81,setup_scalar_calls=81,removed_gauge_reads=84,net_extra_scalar_calls=78,conservative_extra_fixed_calls=2*3*72*162,retained_fixed_call_bound=2**40,old_target_events=old_events,new_target_events=new_events,restores=restores,prime_witnesses=primes,input_pins={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[D/'selection.json',D/'replay.py',D/'word.py',P/'newg/replay.py',Path(__file__)]})
(D/'boundary.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS27 target aggregation groups, actual scalar timestamps, complete reflected target paths,27 prime witnesses',flush=True)
