#!/usr/bin/env python3
"""Independent exact full-path and target-ledger audit of24 new source gauges.
No scalar claim. Prepared with OpenAI Codex assistance.
"""
from pathlib import Path
from collections import defaultdict,Counter
import importlib.util,json,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent/'joint';sp=importlib.util.spec_from_file_location('ind_newgauges',P/'joint_word.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
w=m.Candidate();C=w.C;w.exact_frames();base=w.row();selected=json.loads((D/'selection.json').read_text());co=w.adjoint();recipient={d:b for b,d in w.pairs};kpair={e['passive']:e for e in w.k['entries']};touched={s for i in w.phase1 for s in w.ops[i][:2]};roots=defaultdict(list)
for j,s in enumerate(w.w['rootroles']):roots[s].append((j,w.w['root_frame'][j]))
term=json.loads((P/'joint-replay.json').read_text())['selected'];removed={r['role']for r in term};deleted={r['root']for r in term};bywrite={i:e for e in term for i in e['writes']};after={e['writes'][-1]:e for e in term};tt={t for e in term for t in e['targets']};source_roles=set(w.source.values())
old=json.loads((D.parent/'borrow/selection.json').read_text())+json.loads((D.parent/'gaugeb/selection.json').read_text());old_sources={r['source']for r in old};old_roles={r['role']for r in old};old_members=old_sources|{r['partner']for r in old}
assert not old_members&({r['source']for r in selected}|{r['partner']for r in selected})
assert len({r['source']for r in selected})==len(selected)==25
assert not(old_sources&{r['source']for r in selected})and not(old_roles&{r['role']for r in selected})
assert len({r['role']for r in selected})==25
assert sum(len(r['targets'])for r in selected)==100 and len({t for r in selected for t in r['targets']})==96
local_delta=Counter();endpoint_rows=[];gframes={};prime_records=[]
from prime_witnesses import det,factor_witness,validate_factor
def H(chain,start_dim):
 out=Counter();previous=None;d=start_dim
 for f in chain:
  assert previous is None or C.sub(previous,f)
  n=C.dimf[f];assert n>=d
  if n>d:out[n-d]+=1
  previous=f;d=n
 return out
for r in selected:
 s,n=r['role'],r['source'];e=kpair[n];mix=e['mix_frame'];f=w.register(r['gauge_basis'])if 'gauge_basis'in r else mix;gframes[s]=f;assert mix==r['mix_frame']and e['carrier']==r['partner']and C.sub(mix,f)
 assert s not in touched|source_roles|removed|set(w.donor)|set(w.gauge)
 assert sorted(co[s])==r['targets']and not(set(r['targets'])&tt)
 chain=[w.opframe[i]for i in w.role_ops[s]]+[g for j,g in roots[s]]
 if s in recipient:
  b=recipient[s];chain += [w.gauge[b]['frame']]+[w.opframe[i]for i in w.role_ops[b]]+[g for j,g in roots[b]]
 chain.append(w.w['full_frame']);assert C.sub(f,chain[0])
 new=[w.w['source_frame'][n],mix,f]+chain;assert all(C.nondeg(g)for g in set(new))and all(C.sub(a,b)for a,b in zip(new,new[1:]))
 old_aux=H(chain,0);old_source=H([mix,w.w['full_frame']],1);new_source=H(new[1:],1)
 delta=Counter(new_source);delta.subtract(old_aux);delta.subtract(old_source);delta={d:c for d,c in delta.items()if c}
 assert sum(d*c for d,c in delta.items())==-24
 # Reflected annihilator path has precisely reversed nested frame inclusions.
 for a,b in zip(new,new[1:]):assert C.sub(a,b)and all(w.module.dot(x,y)==0 for x in C.A[b]for y in C.B[a])
 reflected=Counter(C.dimf[b]-C.dimf[a]for a,b in zip(new,new[1:])if C.dimf[b]>C.dimf[a]);assert reflected==new_source
 local_delta.update(delta);endpoint_rows.append(dict(role=s,source=n,alias_recipient=recipient.get(s),source_line=C.dimf[new[0]],K_mix=C.dimf[mix],source_gauge=C.dimf[f],final_dimension=C.dimf[new[-1]],auxiliary_delta=delta,old_aux_histogram=dict(old_aux),old_source_histogram=dict(old_source),complete_source_histogram=dict(new_source),reflected_equal=True))
# Complete actual target chronology, including all terminal substitutions and K.
at=defaultdict(list)
for s in w.order:at[w.readtime[s]].append(s)
deliv=defaultdict(list)
for e in w.k['entries']:deliv[e['deliver_after_root']].append(e)
def target_hist(extra):
 current=[None]*w.v;hist=Counter();events=0
 def move(t,f):
  nonlocal events
  previous=current[t];assert previous is None or C.sub(previous,f),('target nesting',t,previous,f)
  assert all(w.module.dot(C.cov[t],x)==0 for x in C.B[f]),('target cap',t,f)
  d=C.dimf[f]-(0 if previous is None else C.dimf[previous]);assert d>=0
  if d:hist[d]+=1
  current[t]=f;events+=1
 if extra:
  for r in selected:
   for t in r['targets']:move(t,gframes[r['role']])
 for j,i in enumerate(w.rest):
  for s in at[j]:
   for t in w.gauge[s]['targets']:move(t,w.gauge[s]['frame'])
  if i in bywrite:move(bywrite[i]['pivot'],w.opframe[i])
  if i in after:
   for t in after[i]['targets']:move(t,after[i]['root_frame'])
 for s in at[len(w.rest)]:
  for t in w.gauge[s]['targets']:move(t,w.gauge[s]['frame'])
 for j,r in enumerate(w.g['roots']):
  if r['kind']=='side'and j not in deleted:
   for t in r['targets']:move(t,w.w['root_frame'][j])
  for e in deliv[j]:
   for t in e['receivers']:move(t,e['deliver_frame'])
 for t,f in enumerate(current):
  d=w.h-1-C.dimf[f]
  if d:hist[d]+=1
 assert sum(d*c for d,c in hist.items())==w.v*(w.h-1)
 return hist,events
Y0,e0=target_hist(False);Y1,e1=target_hist(True);ydelta=Counter(Y1);ydelta.subtract(Y0);local_delta.update(ydelta)
compact=lambda c:{str(d):n for d,n in sorted(c.items())if n}
assert sum(d*c for d,c in local_delta.items())==-25*24
for f in sorted(set(gframes.values())):
 B=C.B[f];ss=list(map(sum,B));gram=[[9*sum(a*b for a,b in zip(x,y))-ss[i]*ss[j]for j,y in enumerate(B)]for i,x in enumerate(B)]
 determinant=det(gram);powers,residual=factor_witness(determinant);validate_factor(determinant,powers,residual)
 prime_records.append(dict(frame=f,dimension=len(B),basis=B,cleared_gram_determinant=determinant,small_prime_powers=powers,remaining_factor=residual))
assert any(r['dimension']==4 for r in prime_records)
res=dict(status='PASS_EXACT_25_SHARED_SOURCE_GAUGE_PATHS_TARGETS_AND_PRIMES',scope='Complete physical source paths, donor-recipient chains, reflected annihilator nesting, complete terminal/gauge/root/K target chronology, all exact paid local deltas. Whole scalar replay and global assembly owned separately.',selected=25,touched_targets=96,additional_target_events=e1-e0,target_delta=compact(ydelta),old_complete_target_histogram=compact(Y0),new_complete_target_histogram=compact(Y1),local_delta=compact(local_delta),local_rank_delta=sum(d*c for d,c in local_delta.items()),W_delta=-25,shared_rank_delta=3*sum(d*c for d,c in local_delta.items()),deficit_delta=-25*72-3*sum(d*c for d,c in local_delta.items()),endpoint_rows=endpoint_rows,source_gauge_prime_witnesses=prime_records)
(D/'boundary.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({k:v for k,v in res.items()if k not in ('endpoint_rows','source_gauge_prime_witnesses')},indent=2),flush=True)
