"""Independent literal event geometry and complete profile for ordered source493.
OpenAI Codex assistance; Apache-2.0. Does not mutate scalar witnesses.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,ast,gzip
D=Path(__file__).resolve().parent;P=D.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());compact=lambda H:{str(k):v for k,v in sorted(H.items())if v};counter=lambda H:Counter({int(k):v for k,v in H.items()})
import importlib.util
sp=importlib.util.spec_from_file_location('independent_complete_setup',D/'setup.py');setup=importlib.util.module_from_spec(sp);sp.loader.exec_module(setup)
m=setup.m;W=m.W;C=m.C;extra=setup.extra;gs=m.agg;roles=m.role_groups;owner=m.target_group;rf=m.read_frames;extraroles={r['role']for r in extra};scalar=read(D/'replay.json');rankgroups=m.rankgroups;rankowner=m.rankowner;echelon=m.echelon
inputs=[D/'replay.py',D/'word.py',D/'setup.py',D/'selection.json',D/'replay.json',P/'extra/setup.py',P/'extra/selection.json',P/'rank/selection.json',P/'echelon/selection.json',P/'newg/profile.json',Path(__file__)];pins={str(p):sha(p)for p in inputs}
assert len(extra)==22 and len(gs)==82 and len(owner)==316 and len(m.borrow)==493
assert scalar['source_selection']==extra and scalar['status']=='PASS_SOURCE493_82_EQUAL7_RANK4_ECHELON_PR230'
assert len(scalar['integer'])==2 and {x['direction']for x in scalar['integer']}=={-1,1}
for x in[scalar['F2']]+scalar['integer']:assert x['formal_columns']==20141 and x['dirty']==16621 and x['all_targets']and x['all_source_and_dirty_restored']and x['all_forward_centers_at_D0']and x['all_reflected_centers_at_D1']
assert len(scalar['controls'])==17 and all(x['status']=='REJECTED'for x in scalar['controls'].values())
for path,pin in scalar['input_pins'].items():assert sha(Path(path))==pin

def hist(chain,start=0):
 h=Counter();d=start;previous=None
 for f in chain:
  assert C.nondeg(f)and(previous is None or C.sub(previous,f));n=C.dimf[f];assert n>=d
  if n>d:h[n-d]+=1
  d=n;previous=f
 return h

def reflected_source(chain):
 h=Counter()
 for a,b in zip(reversed(chain),list(reversed(chain))[1:]):
  assert all(W.module.dot(x,y)==0 for x in C.A[a]for y in C.B[b]);d=len(C.A[b])-len(C.A[a]);assert d>=0
  if d:h[d]+=1
 return h

def trace(aggregated,include_extra,ranked=False,echeloned=False):
 paths=[[]for _ in range(W.v)];source_paths={r['role']:[W.w['source_frame'][r['source']],r['mix_frame']]for r in extra} if include_extra else {};source_events={r:[]for r in source_paths}
 active=set(range(len(gs)))if aggregated else set();seen=[set()for _ in gs];restores=[];pivotreads=0;removedreads=0;events=0
 rankactive=set(range(len(rankgroups)))if ranked else set();rankseen=[set()for _ in rankgroups];rankrestores=[];rankremoved=0
 echactive=set(range(len(echelon)))if echeloned else set();echseen=[set()for _ in echelon];echrestores=[];echreads=0
 def smove(s,f,event):
  role=W.phys[s]
  if role not in source_paths:return
  assert C.nondeg(f)and C.sub(source_paths[role][-1],f),('independent source event',role,event,source_paths[role][-1],f)
  source_paths[role].append(f);source_events[role].append(dict(virtual=s,frame=f,event=event))
 def move(t,f):
  nonlocal events
  assert C.nondeg(f)and(not paths[t]or C.sub(paths[t][-1],f));assert all(W.module.dot(C.cov[t],b)==0 for b in C.B[f]);paths[t].append(f);events+=1
 def gauge(s):
  nonlocal pivotreads,removedreads,rankremoved,echreads
  if not include_extra and s in extraroles:return
  echskip=set()
  for k,g in enumerate(echelon):
   if k not in echactive:continue
   if s not in g['roles']:
    if set(m.adj[s])&set(g['targets']):
     assert echseen[k]==g['roles']
     for t in g['targets']:move(t,g['frame'])
     echactive.remove(k);echrestores.append(dict(group=k,before_role=s,frame=g['frame']))
    continue
   echseen[k].add(s);echskip.update(g['targets'])
   for t,a in g['response'].items():
    if a.get(s,0):smove(s,W.gauge[s]['frame'],['echelon_read',t]);move(t,W.gauge[s]['frame']);echreads+=1
  for k in sorted({rankowner[t]for t in m.adj[s]if t in rankowner}):
   if k not in rankactive:continue
   g=rankgroups[k]
   if s in g['roles']:rankseen[k].add(s)
   else:
    assert rankseen[k]==g['roles']
    for t in g['targets']:move(t,g['frame'])
    rankactive.remove(k);rankrestores.append(dict(group=k,before_role=s,frame=g['frame']))
  grouped=roles.get(s,[])if aggregated else []
  for i in sorted({owner[t]for t in m.adj[s]if t in owner}):
   if i not in active or i in grouped:continue
   g=gs[i];assert seen[i]==set(g['roles'])
   for t in g['targets']:move(t,g['frame'])
   assert len({paths[t][-1]for t in g['targets']})==1
   active.remove(i);restores.append(dict(group=i,before_role=s,frame=g['frame']))
  skipped=set()
  for i in grouped:
   assert i in active and s not in seen[i];g=gs[i];f=rf[s,i]
   smove(s,f,['group_read',i]);move(g['pivot'],f);seen[i].add(s);pivotreads+=1;skipped.update(g['targets']);removedreads+=len(g['targets'])-1
  for t in m.adj[s]:
   rk=rankowner.get(t)
   if rk in rankactive and t in rankgroups[rk]['dependent']:rankremoved+=1;continue
   if t not in skipped and t not in echskip:smove(s,W.gauge[s]['frame'],['gauge_read',t]);move(t,W.gauge[s]['frame'])
 # All22 new source roles are physically untouched in the retimed center prefix.
 assert not(extraroles&{W.phys[s]for i in W.phase1 if i not in m.omitted for s in W.ops[i][:2]})
 for j,op in enumerate(W.rest):
  for s in m.at[j]:gauge(s)
  if op in m.bywrite:
   smove(W.ops[op][1],W.opframe[op],['terminal_write',op]);move(m.bywrite[op]['pivot'],W.opframe[op])
  elif op not in m.omitted:
   for s in W.ops[op][:2]:smove(s,W.opframe[op],['operation',op])
  if op in m.afterwrite:
   for t in m.afterwrite[op]['targets']:move(t,m.afterwrite[op]['root_frame'])
 for s in m.at[len(W.rest)]:gauge(s)
 assert not active and not rankactive and not echactive
 for j,(root,role)in enumerate(zip(W.g['roots'],W.w['rootroles'])):
  if root['kind']=='side'and j not in m.deletedroots:
   smove(role,W.w['root_frame'][j],['side_root',j])
   for t in root['targets']:move(t,W.w['root_frame'][j])
  for e in m.deliveries[j]:
   for t in e['receivers']:move(t,e['deliver_frame'])
 for role in source_paths:smove(role,W.w['full_frame'],['finish'])
 H=Counter();R=Counter()
 for t,path in enumerate(paths):
  assert path;H.update(hist(path));d=C.dimf[path[-1]];assert d<=W.h-1
  if d<W.h-1:H[W.h-1-d]+=1
  previous=[C.cov[t]];d=1
  for f in reversed(path):
   assert all(W.module.dot(a,b)==0 for a in previous for b in C.B[f]);step=len(C.A[f])-d;assert step>=0
   if step:R[step]+=1
   previous=C.A[f];d=len(previous)
  if W.h>d:R[W.h-d]+=1
 assert H==R and sum(k*n for k,n in H.items())==W.v*(W.h-1)
 return dict(histogram=H,reflected=R,restores=restores,pivotreads=pivotreads,removedreads=removedreads,events=events,source_paths=source_paths,source_events=source_events,rank_restores=rankrestores,rank_removed=rankremoved,echelon_restores=echrestores,echelon_reads=echreads)
base=trace(False,False);equal=trace(True,True);ranked=trace(True,True,True);final=trace(True,True,True,True);rankdelta=Counter(ranked['histogram']);rankdelta.subtract(equal['histogram']);assert compact(rankdelta)==read(P/'rank/selection.json')['local_delta'];baseline=read(P/'newg/profile.json')['profile'];assert compact(base['histogram'])==baseline['physical_target_histogram']
for x in[scalar['F2']]+scalar['integer']:
 assert compact(final['histogram'])==x['actual_target_histogram']==x['actual_reflected_target_histogram']
 assert final['restores']==x['aggregation_restores']and final['pivotreads']==x['aggregation_pivot_reads']==92
 assert {str(k):v for k,v in final['source_paths'].items()}==x['actual_extra_source_paths'];assert final['rank_restores']==x['rank_restores']and final['rank_removed']==x['rank_removed_reads']==108
 assert final['echelon_restores']==x['echelon_restores']and final['echelon_reads']==x['echelon_reads']==48
# Each removed ordinary physical register includes its complete later alias.
recipient={d:b for b,d in W.pairs};roots=defaultdict(list)
for j,r in enumerate(W.w['rootroles']):roots[r].append(W.w['root_frame'][j])
positions={i:j for j,i in enumerate(W.phase1+W.rest)}
rows=[];source_delta=Counter();local=counter(baseline['physical_internal_histogram']);sources=counter(baseline['physical_source_histogram'])
for r in extra:
 role,s=r['role'],r['source'];ops=W.role_ops[role];aux=[W.opframe[i]for i in ops]+roots[role]
 if role in recipient:
  rec=recipient[role];assert positions[ops[-1]]<positions[W.role_ops[rec][0]]
  aux += [W.gauge[rec]['frame']]+[W.opframe[i]for i in W.role_ops[rec]]+roots[rec]
 aux.append(W.w['full_frame']);oldaux=hist(aux);oldsource=hist(m.kpair[s]['passive_chain'][1:],1);chain=final['source_paths'][role]
 newsource=hist(chain[1:],1);assert newsource==reflected_source(chain)
 d=Counter(newsource);d.subtract(oldaux);d.subtract(oldsource);assert sum(k*v for k,v in d.items())==-24
 source_delta.update(d);local.subtract(oldaux);sources.subtract(oldsource);sources.update(newsource)
 rows.append(dict(role=role,source=s,partner=r['partner'],source_path=chain,old_aux_histogram=compact(oldaux),old_source_histogram=compact(oldsource),complete_source_histogram=compact(newsource),source_delta=compact(d),reflected_equal=True))
assert all(n>=0 for h in(local,sources)for n in h.values());assert sum(k*n for k,n in source_delta.items())==-528
child=counter(baseline['child_histogram']);target_delta=Counter(final['histogram']);target_delta.subtract(base['histogram']);totaldelta=Counter(source_delta);totaldelta.update(target_delta)
for k,n in totaldelta.items():child[k]+=3*n
assert all(n>=0 for n in child.values());mass=sum(k*n for k,n in child.items());stock=baseline['W_per_vertex']-22;R=baseline['R']-22
assert stock==20141 and R==16621 and mass==1448216 and 72*stock-mass==1936
assert sum(k*n for k,n in sources.items())==sum(k*n for k,n in final['histogram'].items())==W.v*23
profile=dict(baseline,R=R,active_virtual_R=R+baseline['reused_registers'],W_per_vertex=stock,rank_per_vertex=mass,child_histogram=compact(child),physical_internal_histogram=compact(local),physical_source_histogram=compact(sources),physical_target_histogram=compact(final['histogram']),physical_original_sources_borrowed=493,source_backed_new_rank2_gauges=45,source_backed_shared_rank4_gauges=5,target_aggregation_groups=82,target_aggregation_targets=316,target_transformed_compensation_reads=140,equal_response_pivot_reads=92,target_basis_scalar_gates=690)
# Exact arithmetic prime admission for every newly introduced source and inverse frame.
pcode=(P/'extra/boundary.py').read_text();tree=ast.parse(pcode);defs=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in('determinant','prime_record')];exec(compile(ast.Module(body=defs,type_ignores=[]),'<independent-primes>','exec'),globals())
frames={g['frame']for g in gs}|{g['frame']for g in rankgroups}|{g['frame']for g in echelon}|{W.gauge[r['role']]['frame']for r in extra}|{r['mix_frame']for r in extra};primes=[dict(frame=f,basis=C.B[f],annihilator=C.A[f],primal=prime_record(C.B[f]),dual=prime_record(C.A[f],True))for f in sorted(frames)]
# Exact local integer matrices for all equal and multi-pivot groups.
def vector_add(a,c,b):
 z=a.copy()
 for k,v in b.items():
  z[k]=z.get(k,0)+c*v
  if not z[k]:del z[k]
 return z
def local_transfer(ts,dep,prefix,mutation=None):
 for sign in(1,-1):
  y={t:{('Y',t):1}for t in ts};want={t:v.copy()for t,v in y.items()}
  for t,cs in dep.items():
   for p,c in cs.items():
    if mutation!='omit_setup':y[t]=vector_add(y[t],-c,y[p])
  for role in prefix:
   z={('Z',role):1}
   for t in ts:
    c=m.adj[role].get(t,0);want[t]=vector_add(want[t],-sign*c,z)
    if t not in dep or mutation=='repeat_dependent':y[t]=vector_add(y[t],-sign*c,z)
  for t,cs in dep.items():
   for p,c in cs.items():
    if mutation!='omit_inverse':y[t]=vector_add(y[t],c,y[p])
  assert y==want
for g in gs:local_transfer(g['targets'],{t:{g['pivot']:1}for t in g['targets']if t!=g['pivot']},g['roles'])
for g in rankgroups:local_transfer(g['targets'],g['dependent'],g['roles'])
localcontrols=[]
for mutation in('omit_setup','omit_inverse','repeat_dependent'):
 g=rankgroups[0]
 try:local_transfer(g['targets'],g['dependent'],g['roles'],mutation)
 except AssertionError:localcontrols.append(mutation)
 else:raise AssertionError('Local matrix corruption accepted')
# Independent arbitrary-variable signed integer transfers and determinant-one matrices.
def echelon_transfer(g,mutation=None):
 for sign in(1,-1):
  ts=g['targets'];moves=g['moves'];R={int(t):{int(s):c for s,c in a.items()}for t,a in g['transformed_response'].items()}
  y={t:{('Y',t):1}for t in ts};want={t:a.copy()for t,a in y.items()}
  if mutation!='omit_setup':
   for t,p,c in moves:y[t]=vector_add(y[t],c,y[p])
  for role in g['prefix_roles']:
   z={('Z',role):1}
   for t in ts:
    want[t]=vector_add(want[t],-sign*m.adj[role].get(t,0),z);c=R[t].get(role,0)
    if mutation=='flip_sign'and c<0:c=-c
    y[t]=vector_add(y[t],-sign*c,z)
  if mutation!='omit_inverse':
   for t,p,c in reversed(moves):y[t]=vector_add(y[t],-c,y[p])
  assert y==want
transforms=[]
for g in setup.echelonselection['groups']:
 echelon_transfer(g);ts=g['targets'];U={t:{p:int(t==p)for p in ts}for t in ts};V={t:a.copy()for t,a in U.items()}
 for t,p,c in g['moves']:U[t]=vector_add(U[t],c,U[p])
 for t,p,c in reversed(g['moves']):V[t]=vector_add(V[t],-c,V[p])
 A=[[U[t].get(p,0)for p in ts]for t in ts];B=[[V[t].get(p,0)for p in ts]for t in ts];assert determinant(A)==1
 assert all(sum(A[i][k]*B[k][j]for k in range(len(ts)))==int(i==j)for i in range(len(ts))for j in range(len(ts)))
 transforms.append(dict(targets=ts,matrix=A,inverse=B,determinant=1))
echeloncontrols=[]
for mutation in('omit_setup','omit_inverse','flip_sign'):
 try:echelon_transfer(setup.echelonselection['groups'][0],mutation)
 except AssertionError:echeloncontrols.append(mutation)
 else:raise AssertionError('Echelon local corruption accepted:'+mutation)
profile.update(target_echelon_groups=4,target_echelon_targets=20,target_echelon_basis_scalar_gates=48,target_echelon_signed_compensation_reads=48,target_echelon_compensation_unit_adds=56,partially_lifted_source_gauges=3)
profile['source_owned_gauge_entrances']=53;profile['source_owned_gauge_rank_histogram']={'2':45,'4':5,'19':3};profile['all_gauge_entrances']=2332;profile['all_gauge_rank_histogram']={'2':45,'4':5,'12':18,'13':48,'18':13,'19':3,'20':2200}
profile['target_rank_compression_groups']=7;profile['target_rank_compression_targets']=56;profile['target_rank_compression_dependent_rows']=27;profile['target_aggregation_basis_scalar_gates']=468;profile['target_rank_basis_scaled_add_gates']=174;profile['target_basis_scalar_gates']=690;profile['target_basis_expanded_unit_adds']=702
setupcalls=sum(len(g['targets'])-1 for g in gs);assert setupcalls==234
out=dict(status='PASS_SOURCE493_82_PLUS7_PLUS4_INDEPENDENT_ALL_CHANGED_SOURCE_TARGET_LEDGERS_TRANSFER_PROFILE_AND_PRIMES',selected=22,source_heads=493,groups=82,targets=316,source_local_delta=compact(source_delta),target_local_delta=compact(target_delta),complete_local_delta=compact(totaldelta),raw_W=stock,raw_R=R,raw_rank=mass,raw_deficit=1936,profile=profile,source_rows=rows,target_restores=final['restores'],source_events=final['source_events'],source_paths=final['source_paths'],pivot_reads=final['pivotreads'],setup_calls=setupcalls,inverse_calls=setupcalls,removed_compensation_reads=final['removedreads'],prime_witnesses=primes,maximum_prime_residual=max(z[k]['remaining_factor']for z in primes for k in('primal','dual')),all_new_source_paths_reflected=True,all_target_paths_reflected=True,scope='Independent full actual changed source and target event chronology, former auxiliary complete alias paths, both reflected ledgers, full paid profile and dual prime admission. Whole scalar word owned by parent; complete banks and exact assembly remain separate.',input_pins=pins)
out.update(old_complete_target_histogram=compact(base['histogram']),new_complete_target_histogram=compact(final['histogram']),reflected_target_histogram=compact(final['reflected']),rank_target_delta=compact(rankdelta),rank_restores=final['rank_restores'],rank_removed_reads=final['rank_removed'],local_transfer_controls_rejected=localcontrols,all_local_integer_transfers_both_signs=True,echelon_restores=final['echelon_restores'],echelon_reads=final['echelon_reads'],echelon_local_controls_rejected=echeloncontrols,echelon_transforms=transforms)
assert all(sha(Path(p))==h for p,h in pins.items())
(D/'boundary.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS source493 geometry and full profile',dict(W=stock,R=R,rank=mass,local_delta=compact(totaldelta)),flush=True)
