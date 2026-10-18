"""Clean source527 preparation from pinned source471 inputs and explicit selectors.
Preserves source notices, with substantial OpenAI Codex assistance.
No old PASS receipt is consumed and no payload execution occurs here.
"""
from pathlib import Path
from collections import Counter,defaultdict
from types import SimpleNamespace
import hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def prepare():
 S=HERE/'source527'
 p=HERE/'loader/source_loader.py';spec=importlib.util.spec_from_file_location('portable527_source471_loader',p);loader=importlib.util.module_from_spec(spec);spec.loader.exec_module(loader)
 context=loader.prepare(HERE/'loader/source_inputs/pr210',HERE/'loader/source_inputs/base_bit')
 m=SimpleNamespace(**context);W=m.W;C=m.C
 # Apply the nineteen PR230 operation-frame improvements retained by source527.
 # The active full witness differs from PR230's raw search output at retained
 # predecessor choices; its source493 manifest and provenance pin both forms.
 framepath=S/'pr230/active-opframe-bases.json'
 assert hashlib.sha256(framepath.read_bytes()).hexdigest()=='9a2bba5c72aebc9ee4f21e59b10ce810b2da98a1fa1748fbc44c50a080e584ff'
 changed=[]
 for operation,rows in json.loads(framepath.read_text()):
  target_frame=W.register(rows)
  if C.B[W.opframe[operation]]!=C.B[target_frame]:changed.append(operation)
  W.opframe[operation]=target_frame
 assert changed==[18750,23544,23545,23591,23592,23638,23639,23685,23686,23732,23733,27900,27904,27908,27912,28052,28056,28060,28064],changed
 W.changed_frames=[i for i,(a,b)in enumerate(zip(W.original_opframe,W.opframe))if a!=b]
 W.endframe={r:W.opframe[ii[-1]]for r,ii in W.role_ops.items()}
 W.exact_frames();m.pr230_operation_changes=changed
 extra=json.loads((S/'extra/selection.json').read_text());oldborrow=m.borrow.copy();used={s for r in m.selection+m.gauge_selection for s in[r['source'],r['partner']]};assert len(oldborrow)==471
 for r in extra:
  role,n=r['role'],r['source'];e=m.kpair[n];assert e['carrier']==r['partner'];assert not({n,r['partner']}&used);used.update([n,r['partner']])
  assert role not in m.borrow and role not in m.W.gauge and role not in m.W.donor and role not in m.removed and role not in m.W.source.values()
  assert set(m.adj[role])==set(r['targets'])and set(m.adj[role].values())=={1}
  assert role not in {s for i in m.W.phase1 for s in m.W.ops[i][:2]};f=m.W.register(r['split_gauge_basis'])if'split_gauge_basis'in r else e['mix_frame'];assert m.C.dimf[f]in(2,4) and m.C.nondeg(f)and m.C.sub(f,m.W.opframe[m.W.role_ops[role][0]])
  assert all(all(m.W.module.dot(m.C.cov[t],b)==0 for b in m.C.B[f])for t in r['targets'])
  z=dict(role=role,frame=f,dim=m.C.dimf[f],targets=r['targets']);m.W.gauge[role]=z;m.W.w['gauges'].append(z);m.W.readtime[role]=0;m.W.w['reads'][str(role)]=len(m.W.phase1)
  m.borrow[role]=n;m.by_source[n]=r;m.gauge_borrow[role]=n;m.gauge_selection.append(r)
 m.W.order=[r['role']for r in extra]+m.W.order
 # The third ordered rank4 source entrance follows all retained new-source gauges.
 m.W.readtime[14073]=168;m.W.w['reads']['14073']=len(m.W.phase1)+168
 m.W.order.remove(14073);at_index=max(m.W.order.index(r['role'])for r in m.new_gauge_selection)+1;m.W.order.insert(at_index,14073)
 m.at=defaultdict(list)
 for role in m.W.order:m.at[m.W.readtime[role]].append(role)
 m.regs=sorted(set(m.W.phys.values())-set(m.borrow)-m.removed);m.idx={r:2*m.W.v+j for j,r in enumerate(m.regs)};assert len(m.borrow)==493 and len(m.regs)==16621
 assert all(0<=m.W.readtime[s]<=m.W.first[s]for s in m.W.gauge);m.W.exact_frames()
 m.extra_roles={r['role']for r in extra};m.extra_selection=extra
 
 groups=json.loads((S/'targetagg/selection.json').read_text())['groups'];agg=[];role_groups=defaultdict(list);owner={}
 for k,g in enumerate(groups):
  F=W.register(g['frame_basis']);ts=g['targets'];assert C.nondeg(F)and g['pivot']in ts
  for t in ts:assert t not in owner;owner[t]=k
  for s in g['roles']:
   assert set(ts)<=set(m.adj[s])and len({m.adj[s][t]for t in ts})==1 and C.sub(W.gauge[s]['frame'],F);role_groups[s].append(k)
  agg.append(dict(targets=ts,pivot=g['pivot'],roles=g['roles'],frame=F))
 assert len(agg)==82 and len(owner)==316
 byrole={r['role']:r for r in extra};rf={}
 for k,g in enumerate(agg):
  for role in g['roles']:
   r=byrole.get(role);f=W.gauge[role]['frame']
   if r and'split_gauge_basis'in r and r['early_role']not in g['roles']:f=r['mix_frame']
   assert C.sub(f,g['frame']);rf[role,k]=f
 for role,ks in role_groups.items():ks.sort(key=lambda k:C.dimf[rf[role,k]])
 m.agg=agg;m.role_groups=role_groups;m.target_group=owner;m.read_frames=rf;m.extra_byrole=byrole
 rankselection=json.loads((S/'rank/selection.json').read_text());rankgroups=[];rankowner={}
 for k,g in enumerate(rankselection['groups']):
  F=W.register(g['frame_basis']);dep={int(t):{int(p):c for p,c in cs.items()}for t,cs in g['dependent'].items()};assert not(set(dep)&{p for cs in dep.values()for p in cs})
  for t in g['targets']:assert t not in owner and t not in rankowner;rankowner[t]=k;assert all(W.module.dot(C.cov[t],b)==0 for b in C.B[F])
  for s in g['prefix_roles']:
   assert C.sub(W.gauge[s]['frame'],F)
   for t,cs in dep.items():assert m.adj[s].get(t,0)==sum(c*m.adj[s].get(p,0)for p,c in cs.items())
  rankgroups.append(dict(targets=g['targets'],dependent=dep,roles=set(g['prefix_roles']),frame=F))
 assert len(rankgroups)==7 and len(rankowner)==56 and sum(len(g['dependent'])for g in rankgroups)==27
 m.rankgroups=rankgroups;m.rankowner=rankowner
 
 echelonselection=json.loads((S/'echelon/selection.json').read_text());echelon=[];eowner={}
 def addrow(a,c,b):
  z=a.copy()
  for s,v in b.items():
   z[s]=z.get(s,0)+c*v
   if not z[s]:del z[s]
  return z
 for k,r in enumerate(echelonselection['groups']):
  F=W.register(r['frame_basis']);R={int(t):{int(s):c for s,c in a.items()}for t,a in r['transformed_response'].items()};moves=[tuple(v)for v in r['moves']]
  A={t:{s:m.adj[s].get(t,0)for s in r['prefix_roles']if m.adj[s].get(t,0)}for t in r['targets']}
  for t,p,c in moves:assert t!=p;A[t]=addrow(A[t],c,A[p])
  assert A==R and C.nondeg(F)
  for t in r['targets']:assert t not in owner and t not in rankowner and t not in eowner;eowner[t]=k;assert all(W.module.dot(C.cov[t],b)==0 for b in C.B[F])
  for s in r['prefix_roles']:assert C.sub(W.gauge[s]['frame'],F)
  echelon.append(dict(targets=r['targets'],roles=set(r['prefix_roles']),response=R,moves=moves,frame=F))
 assert len(echelon)==4 and len(eowner)==20
 m.echelon=echelon;m.eowner=eowner
 
 selection=json.loads((S/'fresh/selection.json').read_text());chosen=[];fresh={}
 used={r[k]for r in m.selection+m.gauge_selection for k in('source','partner')};newused=set()
 for raw in selection:
  r=dict(raw);role,n=r['role'],r['source'];entry=m.kpair[n]
  assert entry['carrier']==r['partner']and not({n,r['partner']}&(used|newused));newused.update((n,r['partner']))
  assert role not in W.gauge and role not in m.borrow and n not in m.by_source
  f=entry['mix_frame'];q=W.register(r['mix_basis']);assert C.sub(f,q)and C.sub(q,f)and C.dimf[f]==2
  assert W.role_ops[role][0]==r['first_operation']and C.sub(f,W.opframe[r['first_operation']])and C.nondeg(f)
  r['mix_frame']=f;chosen.append(r);fresh[role]=r
  z=dict(role=role,frame=f,dim=2,targets=sorted(m.adj[role]));W.gauge[role]=z;W.w['gauges'].append(z);W.readtime[role]=0;W.w['reads'][str(role)]=len(W.phase1)
  m.borrow[role]=n;m.by_source[n]=r;m.gauge_borrow[role]=n;m.gauge_selection.append(r);m.extra_byrole[role]=r
 assert len(chosen)==3 and len(newused)==6
 W.order=list(fresh)+W.order;m.at=defaultdict(list)
 for role in W.order:m.at[W.readtime[role]].append(role)
 m.regs=sorted(set(W.phys.values())-set(m.borrow)-m.removed);m.idx={r:2*W.v+j for j,r in enumerate(m.regs)}
 assert len(m.borrow)==496 and len(m.regs)==16618 and len(m.extra_byrole)==25
 W.exact_frames();m.fresh=fresh
 
 chosen=json.loads((S/'paired-selection.json').read_text());pair_byalias={r['aliased_role']:r for r in chosen};pair_bydirty={int(a):r for r in chosen for a in r['retained_dirty_coefficients']}
 for r in chosen:
  b,n=r['aliased_role'],r['source'];f=m.kpair[n]['mix_frame'];r['mix_frame']=f;anchors={int(a):c for a,c in r['retained_dirty_coefficients'].items()};r['retained_dirty_coefficients']=anchors
  response=Counter(m.adj[b])
  for a,c in anchors.items():
   for t,v in m.adj[a].items():response[t]+=c*v
  assert not any(response.values()),('nonzero combined response',r)
  assert b not in W.gauge and b not in m.borrow and n not in m.by_source
  assert all(a not in W.gauge and a not in m.borrow for a in anchors)
  canonical=W.register(r['mix_basis']);assert m.kpair[n]['carrier']==r['partner'] and C.dimf[f]==2 and C.sub(f,canonical)and C.sub(canonical,f)
  assert all(C.sub(f,W.opframe[W.role_ops[a][0]])for a in [b]+list(anchors))and C.nondeg(f)
  z=dict(role=b,frame=f,dim=2,targets=[]);W.gauge[b]=z;W.w['gauges'].append(z);W.readtime[b]=0;W.w['reads'][str(b)]=len(W.phase1)
  q=dict(r,role=b);m.borrow[b]=n;m.by_source[n]=q;m.gauge_borrow[b]=n;m.gauge_selection.append(q);m.extra_byrole[b]=q
 W.order=list(pair_byalias)+W.order;m.at=defaultdict(list)
 for role in W.order:m.at[W.readtime[role]].append(role)
 m.regs=sorted(set(W.phys.values())-set(m.borrow)-m.removed);m.idx={r:2*W.v+j for j,r in enumerate(m.regs)};assert len(m.borrow)==527 and len(m.regs)==16587
 W.exact_frames();m.pair_byalias=pair_byalias;m.pair_bydirty=pair_bydirty;m.pair_selection=chosen;m.zero=W.register([])

 m.SOURCE_TEXT=(S/'word.py').read_text()
 assert hashlib.sha256(m.SOURCE_TEXT.encode()).hexdigest()=='e675d4eb9d90ff0b44279fae0b46f1a8b39f65421cc38454b70a6b75d0e10b42'
 m.input_pins={}
 m.portable_source_pins={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()for p in S.rglob('*')if p.is_file()}
 return dict(m.__dict__)
