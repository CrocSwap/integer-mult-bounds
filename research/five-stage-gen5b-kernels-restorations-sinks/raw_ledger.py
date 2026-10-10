"""Independent fresh gen5 physical path census, including both reflections.
Derived from the source527 census (eumemic); constants rebound to the gen5 word.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
No saved receipt, search script, or historical profile is consumed.
"""
from collections import Counter,defaultdict
from types import SimpleNamespace

def run(context):
 m=SimpleNamespace(**context);W=m.W;C=m.C;chosen=m.pair_selection;fresh=m.fresh;pair_byalias=m.pair_byalias;pair_bydirty=m.pair_bydirty
 compact=lambda h:{str(k):v for k,v in sorted(h.items())if v}
 zero=W.register([]);compact=lambda h:{str(k):v for k,v in sorted(h.items())if v}
 # Exact raw event sequence, with every actual extra source included.
 events=[]
 for j,op in enumerate(W.rest):
  for s in m.at[j]:events.append(dict(kind='gauge',ref=s,frame=W.gauge[s]['frame'],targets=list(m.adj[s])))
  if op in m.bywrite:events.append(dict(kind='terminalwrite',ref=op,frame=W.opframe[op],targets=[m.bywrite[op]['pivot']]))
  if op in m.afterwrite:events.append(dict(kind='terminalread',ref=op,frame=m.afterwrite[op]['root_frame'],targets=m.afterwrite[op]['targets']))
 for s in m.at[len(W.rest)]:events.append(dict(kind='gauge',ref=s,frame=W.gauge[s]['frame'],targets=list(m.adj[s])))
 endgauge=len(events)
 for j,r in enumerate(W.g['roots']):
  if r['kind']=='side'and j not in m.deletedroots:events.append(dict(kind='root',ref=j,frame=W.w['root_frame'][j],targets=r['targets']))
  for e in m.deliveries[j]:events.append(dict(kind='K',ref=e['passive'],frame=e['deliver_frame'],targets=e['receivers']))
 for t in range(W.v):events.append(dict(kind='endpoint',ref=t,frame=W.register(W.module.kernel([C.cov[t]],W.h)[0]),targets=[t]))
 
 def histogram(t,path):
  h=Counter();rev=Counter();assert path[0]==zero and C.dimf[path[-1]]==W.h-1
  for f in path:assert C.nondeg(f)and all(W.module.dot(C.cov[t],b)==0 for b in C.B[f]),('cap/nondeg',t,f)
  for a,b in zip(path,path[1:]):
   assert C.sub(a,b),('forward inclusion',t,a,b)
   d=C.dimf[b]-C.dimf[a];assert d>=0
   if d:h[d]+=1
  for a,b in zip(reversed(path),list(reversed(path))[1:]):
   assert all(W.module.dot(x,y)==0 for x in C.A[a]for y in C.B[b]),('reflected inclusion',t,a,b)
   d=len(C.A[b])-len(C.A[a]);assert d>=0
   if d:rev[d]+=1
  assert h==rev and sum(k*v for k,v in h.items())==W.h-1
  return h
 
 def paths(agg,readframes,echelon,rankgroups):
  rankowner={t:k for k,g in enumerate(rankgroups)for t in g['targets']}
  out=[[zero]for _ in range(W.v)];owner={t:k for k,g in enumerate(agg)for t in g['targets']};roles=defaultdict(list)
  for k,g in enumerate(agg):
   for s in g['roles']:roles[s].append(k)
  active=set(range(len(agg)));rankactive=set(range(len(rankgroups)));echactive=set(range(len(echelon)));seen=[set()for _ in echelon];restores=[]
  for j,e in enumerate(events):
   if j>=endgauge:assert not active and not rankactive and not echactive
   s=e['ref'];T=set(e['targets'])
   if e['kind']=='gauge':
    if s in pair_byalias:continue
    if s in fresh:
     for t,c in fresh[s]['transformed_response'].items():
      if c:out[int(t)].append(W.gauge[s]['frame'])
     continue
    skip=set()
    for k,g in enumerate(echelon):
     if k not in echactive:continue
     if s not in g['roles']:
      if T&set(g['targets']):
       assert seen[k]==g['roles'];restores.append(dict(group=k,before_role=s,event=j))
       for t in g['targets']:out[t].append(g['frame'])
       echactive.remove(k)
      continue
     seen[k].add(s);skip.update(g['targets'])
     for t,a in g['response'].items():
      if a.get(s,0):out[t].append(W.gauge[s]['frame'])
    for k in sorted({rankowner[t]for t in T if t in rankowner}):
     if k in rankactive and s not in rankgroups[k]['roles']:
      for t in rankgroups[k]['targets']:out[t].append(rankgroups[k]['frame'])
      rankactive.remove(k)
    for k in sorted({owner[t]for t in T if t in owner}):
     if k in active and s not in agg[k]['roles']:
      for t in agg[k]['targets']:out[t].append(agg[k]['frame'])
      active.remove(k)
    for k in roles[s]:
     assert k in active;g=agg[k];out[g['pivot']].append(readframes[s,k]);skip.update(g['targets'])
    for t in e['targets']:
     if t in skip:continue
     rk=rankowner.get(t)
     if rk in rankactive and t in rankgroups[rk]['dependent']:continue
     out[t].append(e['frame'])
   else:
    assert not(T&{t for k in active for t in agg[k]['targets']})
    assert not(T&{t for k in echactive for t in echelon[k]['targets']})
    for t in e['targets']:out[t].append(e['frame'])
  H=Counter()
  for t,p in enumerate(out):H.update(histogram(t,p))
  return out,H,restores
 
 newpaths,target,restores=paths(m.agg,m.read_frames,m.echelon,m.rankgroups)
 # Recover raw literal adjoint independently, respecting all omitted copies.
 adj=[{}for _ in range(W.R)]
 for root,role in zip(W.g['roots'],W.w['rootroles']):
  for t in root['targets']:adj[role][t]=adj[role].get(t,0)+1
 for i in reversed(W.phase1+W.rest):
  if i in m.omitted:continue
  a,b,_=W.ops[i]
  for t,c in adj[a].items():adj[b][t]=adj[b].get(t,0)+c
 assert adj==m.adj
 oldused={r[k]for r in m.selection+m.gauge_selection if r['role']not in pair_byalias for k in('source','partner')}
 assert len({r[k]for r in chosen for k in('source','partner')})==2*len(chosen)==0 and not oldused&{r[k]for r in chosen for k in('source','partner')}
 for r in chosen:
  b=r['aliased_role'];response=Counter(adj[b])
  for a,c in r['retained_dirty_coefficients'].items():
   for t,v in adj[a].items():response[t]+=c*v
  assert not any(response.values())
 # Complete physical source and auxiliary census, including all alias handoffs.
 recipient={d:b for b,d in W.pairs};roots=defaultdict(list)
 for j,s in enumerate(W.w['rootroles']):roots[s].append(W.w['root_frame'][j])
 source_role={s:n for n,s in W.source.items()};plainborrow={r['role']:r for r in m.selection};gauges={r['role']:r for r in m.gauge_selection}
 assert len(plainborrow)==0 and len(gauges)==0 and len(m.borrow)==0
 seq={s:[('op',i,W.opframe[i])for i in W.role_ops[s]]+[('root',j,f)for j,f in enumerate(roots[s])]for s in range(W.R)}
 def physical_path(s):
  a=list(seq[s])
  if s in pair_bydirty:a=[('paired-source-injection',s,pair_bydirty[s]['mix_frame'])]+a
  if s in recipient:
   b=recipient[s];a+=[('alias',b,W.gauge[b]['frame'])]+seq[b]
  return a+[('full',s,W.w['full_frame'])]
 count=0
 
 def census_hist(start,events):
  nonlocal count
  count+=1;prev=start;dim=C.dimf[start]if start is not None else 0;out=Counter();chain=[]if start is None else[start]
  for _,_,f in events:
   assert C.nondeg(f)and(prev is None or C.sub(prev,f));d=C.dimf[f]-dim;assert d>=0
   if d:out[d]+=1
   prev=f;dim=C.dimf[f];chain.append(f)
  assert dim==24;reflected=Counter()
  for a,b in zip(reversed(chain),list(reversed(chain))[1:]):
   assert all(W.module.dot(x,y)==0 for x in C.A[a]for y in C.B[b]);d=len(C.A[b])-len(C.A[a]);assert d>=0
   if d:reflected[d]+=1
  if start is None:
   d=24-len(C.A[chain[0]])
   if d:reflected[d]+=1
  assert reflected==out
  return out,chain
 internal=Counter();sources=Counter();pathrows={};sourcepaths={};dirtypaths={}
 for s in m.regs:
  start=W.gauge[s]['frame']if s in W.gauge else W.w['source_frame'][source_role[s]]if s in source_role else None
  H,chain=census_hist(start,physical_path(s))
  if s in source_role:H[1]+=1
  internal.update(H);pathrows['a'+str(s)]=compact(H)
  if s in pair_bydirty:dirtypaths[str(s)]=[zero]+chain
 for j,r in enumerate(W.g['roots']):
  if r['kind']=='center':internal[C.dimf[W.w['root_frame'][j]]]+=1
 for entry in W.k['entries']:
  carrier,n=entry['carrier'],entry['passive'];H,chain=census_hist(entry['carrier_chain'][0],[('carrier',j,f)for j,f in enumerate(entry['carrier_chain'][1:])]);sources.update(H)
  if n not in m.by_source:
   H,chain=census_hist(entry['passive_chain'][0],[('passive',j,f)for j,f in enumerate(entry['passive_chain'][1:])]);sources.update(H);pathrows['s'+str(n)]=compact(H);continue
  r=m.by_source[n];s=r['role'];events=physical_path(s)
  if s in plainborrow:
   r=plainborrow[s];events=[x for x in events if not(x[0]=='op'and x[1]==r['omit_copy'])];at=next(i for i,x in enumerate(events)if x[0]=='op'and x[1]==r['early']);events.insert(at,('mix',n,entry['mix_frame']))
  else:
   assert s in gauges;events=[('mix',n,entry['mix_frame']),('gauge',s,W.gauge[s]['frame'])]+events
  H,chain=census_hist(W.w['source_frame'][n],events);sources.update(H);pathrows['s'+str(n)]=compact(H)
  if s in m.extra_byrole:sourcepaths[str(s)]=chain
 assert count==17194 and len(sourcepaths)==0 and len(dirtypaths)==0 and sum(k*v for k,v in sources.items())==1760*23
 gauges=Counter(z['dim']for s,z in W.gauge.items()if s not in W.donor and s not in m.borrow)
 assert gauges=={20:2182,21:34,18:16,17:2}
 copies=Counter(C.dimf[W.w['root_frame'][j]]for j,r in enumerate(W.g['roots'])if r['kind']=='center');assert copies=={22:24}
 withoutcopies=internal.copy();withoutcopies.subtract(copies);assert min(withoutcopies.values())>=0
 helper=internal+sources+target;h=24;v=1760;R=len(m.regs);M=120;stock=4*v+R
 assert R==15434 and len(m.borrow)==0
 assert sum(k*n for k,n in helper.items())==h*R+2*v*(h-1)+sum(k*n for k,n in copies.items())-sum(k*n for k,n in gauges.items())
 idle=Counter({r:2*v for r in (2*h-2,h-1,2*h+2,4)});five=Counter({r:5*n for r,n in helper.items()});five.update(idle)
 for r,n in gauges.items():five[5*r]+=n
 mass=sum(k*n for k,n in five.items());assert M*stock-mass==4400
 raw=dict(schema='gen5-fresh-raw-ledger/1',source_head=context.get('source_head','gen5'),h=h,v=v,physical_R=R,source_aliases=len(m.borrow),terminal_sinks=len(m.terminal),physical_donor_recipient_identifications=len(W.pairs),physical_internal_excluding_center_copies=compact(withoutcopies),paid_center_copy_histogram=compact(copies),physical_source_histogram=compact(sources),physical_target_histogram=compact(target),one_stage_helper_histogram_including_copies=compact(helper),auxiliary_entrance_rank_histogram=compact(gauges),auxiliary_entrance_count=sum(gauges.values()),helper_rank_mass=sum(k*n for k,n in helper.items()),five_stage_profile=dict(m=M,W=stock,histogram=compact(five),idle_histogram=compact(idle),calls=sum(five.values()),rank_mass=mass,deficit=M*stock-mass,maxchild=max(five)),source_aux_paths=count,target_paths=1760,extra_source_paths=len(sourcepaths),paired_dirty_paths=len(dirtypaths),all_reflected_ledgers=True,all_zero_response_relations=True,scope='Fresh complete gen5 raw physical source/internal/target and copied-center ledger. Both reflected chains checked; no saved execution receipt consumed.')
 assert raw['five_stage_profile']['calls']==480999 and mass==2692480
 return raw

def rebind_parity(raw,receipt):
 """Bind the fresh required-use census to the retained producer source ledger."""
 from copy import deepcopy
 def hist(x):return Counter({int(r):n for r,n in x.items()if n})
 assert receipt['status']=='PASS_FRESH_PARITY_FUSION_AND_INDEPENDENT_REQUIRED_FRAME_CENSUS'
 assert receipt['both_reflected_ledgers']and receipt['unchanged_all_input_output_frames']
 source=hist(receipt['source_histogram']);target=hist(receipt['target_histogram']);internal=hist(receipt['internal_histogram_including_copies']);copies=hist(receipt['copied_center_histogram'])
 assert source==hist(raw['physical_source_histogram'])
 assert internal==hist(raw['physical_internal_excluding_center_copies'])+copies
 delta=target.copy();delta.subtract(hist(raw['physical_target_histogram']));assert {r:n for r,n in delta.items()if n}=={}
 producer=deepcopy(raw);helper=source+target+internal;five=Counter({r:5*n for r,n in helper.items()});five.update(hist(raw['five_stage_profile']['idle_histogram']))
 for a,n in hist(raw['auxiliary_entrance_rank_histogram']).items():five[5*a]+=n
 assert sum(five.values())==480999 and sum(r*n for r,n in five.items())==2692480
 raw['schema']='gen5-parity-fused-fresh-raw-ledger/1';raw['producer_ledger']=producer
 raw['physical_target_histogram']={str(r):n for r,n in sorted(target.items())};raw['one_stage_helper_histogram_including_copies']={str(r):n for r,n in sorted(helper.items())}
 raw['five_stage_profile'].update(histogram={str(r):n for r,n in sorted(five.items())},calls=sum(five.values()))
 raw['parity_transform']=receipt;raw['scope']='Fresh gen5 producer ledger plus independently rebuilt actual surviving-use ledger after F2 payload identity elision and same-stream nested MOVE fusion. Both reflected endpoint inclusions checked. No address arithmetic reduced modulo2.'
 return raw

def rebind_descent(raw,receipt):
 """Recount the complete word after the concave-descent frame retiming of selected ADD gates."""
 from copy import deepcopy
 hist=lambda x:Counter({int(r):n for r,n in x.items()if n})
 compact=lambda x:{str(r):n for r,n in sorted(x.items())if n}
 assert receipt['status']=='PASS_CONCAVE_DESCENT_RETIMING_AND_BOTH_REFLECTED_LEDGERS'
 assert receipt['both_reflected_ledgers']and receipt['unchanged_all_input_output_frames']and receipt['unchanged_copy_lifetimes']and receipt['operand_source_spans_contained']
 assert receipt['selected_gate_count']==904 and receipt['remaining_payload_additions']==753472 and receipt['removed_calls']==880
 source=hist(receipt['source_histogram']);target=hist(receipt['target_histogram']);internal=hist(receipt['internal_histogram_including_copies']);copies=hist(receipt['copied_center_histogram'])
 assert copies==hist(raw['paid_center_copy_histogram'])=={22:24}
 helper=source+target+internal;delta=helper.copy();delta.subtract(hist(raw['one_stage_helper_histogram_including_copies']))
 assert {r:n for r,n in delta.items()if n}=={1:-1760,2:880,6:24,7:-48,8:24,20:-880,21:1760,22:-880}
 assert {r:n for r,n in delta.items()if n}==hist(receipt['local_histogram_delta'])
 # Source, target and internal paths may each regroup; every endpoint mass is retained exactly.
 assert sum(r*n for r,n in source.items())==sum(r*n for r,n in hist(raw['physical_source_histogram']).items())==1760*23
 assert sum(r*n for r,n in target.items())==sum(r*n for r,n in hist(raw['physical_target_histogram']).items())==1760*23
 assert sum(r*n for r,n in helper.items())==407228 and sum(helper.values())==sum(hist(raw['one_stage_helper_histogram_including_copies']).values())-880
 original=deepcopy(raw);gauges=hist(raw['auxiliary_entrance_rank_histogram']);assert gauges=={20:2182,21:34,18:16,17:2}
 five=Counter({r:5*n for r,n in helper.items()});five.update(hist(raw['five_stage_profile']['idle_histogram']))
 for a,n in gauges.items():five[5*a]+=n
 assert sum(five.values())==476599 and sum(r*n for r,n in five.items())==2692480
 withoutcopies=internal.copy();withoutcopies.subtract(copies);assert min(withoutcopies.values())>=0
 raw['schema']='gen5-parity-descent-fresh-raw-ledger/1';raw['parity_fused_ledger']=original
 raw['physical_source_histogram']=compact(source);raw['physical_target_histogram']=compact(target);raw['physical_internal_excluding_center_copies']=compact(withoutcopies)
 raw['one_stage_helper_histogram_including_copies']=compact(helper);raw['helper_rank_mass']=407228
 raw['five_stage_profile'].update(histogram=compact(five),calls=sum(five.values()))
 raw['descent_transform']=receipt;raw['scope']='Fresh actual gen5 word after the concave-descent retiming of 904 ADD gate frames. Every scalar column, operand source span, required frame path, reflected inclusion, data endpoint and copied-center lifetime is checked; 880 local recursive calls disappear at unchanged rank mass.'
 return raw

def rebind_kernel(raw,receipt):
 """Complete physical census after the per-pair-cut kernel rewrite (adapted from #268's rebind_kernel)."""
 from copy import deepcopy
 from pins import pin
 hist=lambda x:Counter({int(k):v for k,v in x.items()if v})
 compact=lambda x:{str(k):v for k,v in sorted(x.items())if v}
 assert receipt['status']=='PASS_GEN4_PER_ENTRY_CUT_KERNEL_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS'
 assert receipt['both_reflected_ledgers']and receipt['unchanged_data_input_output_and_dirty_output_frames']and receipt['unchanged_copy_lifetimes']
 pairs=pin('kernel_pairs',receipt['selected_pairs']);pin('kernel_entries',receipt['selected_entries']);ranks=hist(receipt['proof']['entrance_rank_histogram']);assert receipt['rank_drop']==sum(r*c for r,c in ranks.items())==pin('kernel_entrance_rank',receipt['rank_drop']) and receipt['proof']['source_context_preserved']
 source=hist(receipt['source_histogram']);target=hist(receipt['target_histogram']);internal=hist(receipt['internal_histogram_including_copies']);copies=hist(receipt['copied_center_histogram'])
 assert source==hist(raw['physical_source_histogram'])and target==hist(raw['physical_target_histogram'])and copies=={22:24}
 helper=source+target+internal;delta=helper.copy();delta.subtract(hist(raw['one_stage_helper_histogram_including_copies']))
 assert {k:v for k,v in delta.items()if v}==hist(receipt['local_histogram_delta'])==hist(pin('kernel_local_delta',{k:v for k,v in delta.items()if v}))
 pin('kernel_helper_rank_mass',sum(k*v for k,v in helper.items()))
 before=deepcopy(raw);gauges=hist(raw['auxiliary_entrance_rank_histogram']);gauges.update(ranks)
 pin('entrance_rank_histogram',dict(gauges))
 five=Counter({r:5*n for r,n in helper.items()});five.update(hist(raw['five_stage_profile']['idle_histogram']))
 for a,n in gauges.items():five[5*a]+=n
 pin('five_stage_calls',sum(five.values()));pin('five_stage_rank_mass',sum(r*n for r,n in five.items()))
 without=internal.copy();without.subtract(copies);assert min(without.values())>=0
 raw.update(schema='gen4-kernel-pairs-fresh-ledger/1',parity_ledger=before,physical_internal_excluding_center_copies=compact(without),one_stage_helper_histogram_including_copies=compact(helper),helper_rank_mass=sum(k*v for k,v in helper.items()),auxiliary_entrance_rank_histogram=compact(gauges),auxiliary_entrance_count=sum(gauges.values()),kernel_transform=receipt)
 raw['five_stage_profile'].update(histogram=compact(five),calls=sum(five.values()),rank_mass=sum(r*n for r,n in five.items()))
 raw['scope']='Fresh complete actual gen4 kernel-pair word, all scalar columns and both reflected ledgers; the rank-one pivot entrances are tracked beside the gen4 entrances.'
 return raw

def rebind_restore(raw,receipt,completions):
 """Complete physical census after the early-restoration rewrite: helper histogram from the fresh path census;
 entrances unchanged; five-stage completions charged at dim(sigma)+24-dim(endpoint) (P_sigma + I - P_E)."""
 from copy import deepcopy
 from pins import pin
 hist=lambda x:Counter({int(k):v for k,v in x.items()if v})
 compact=lambda x:{str(k):v for k,v in sorted(x.items())if v}
 assert receipt['status']=='PASS_GEN5_EARLY_RESTORATION_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS'
 assert receipt['both_reflected_ledgers']and receipt['unchanged_data_input_output_frames']and receipt['unchanged_copy_lifetimes']
 pin('restore_helpers',receipt['selected']);saving=pin('restore_endpoint_saving',receipt['endpoint_rank_saving'])
 source=hist(receipt['source_histogram']);target=hist(receipt['target_histogram']);internal=hist(receipt['internal_histogram_including_copies']);copies=hist(receipt['copied_center_histogram'])
 assert source==hist(raw['physical_source_histogram'])and target==hist(raw['physical_target_histogram'])and copies=={22:24}
 helper=source+target+internal;delta=helper.copy();delta.subtract(hist(raw['one_stage_helper_histogram_including_copies']))
 assert {k:v for k,v in delta.items()if v}==hist(receipt['local_histogram_delta'])==hist(pin('restore_local_delta',{k:v for k,v in delta.items()if v}))
 assert sum(k*v for k,v in helper.items())==raw['helper_rank_mass']-saving
 gauges=hist(raw['auxiliary_entrance_rank_histogram']);completions=Counter(completions)
 assert sum(completions.values())==sum(gauges.values()) and sum(r*n for r,n in completions.items())==sum(r*n for r,n in gauges.items())+saving
 pin('completion_rank_histogram',dict(completions))
 five=Counter({r:5*n for r,n in helper.items()});five.update(hist(raw['five_stage_profile']['idle_histogram']))
 for c,n in completions.items():five[5*c]+=n
 assert sum(r*n for r,n in five.items())==raw['five_stage_profile']['rank_mass'],'early restoration keeps the five-stage deficit'
 pin('restore_five_stage_calls',sum(five.values()));pin('restore_five_stage_rank_mass',sum(r*n for r,n in five.items()))
 without=internal.copy();without.subtract(copies);assert min(without.values())>=0
 before=deepcopy(raw)
 raw.update(schema='gen5-early-restoration-fresh-ledger/1',kernel_ledger=before,physical_internal_excluding_center_copies=compact(without),one_stage_helper_histogram_including_copies=compact(helper),helper_rank_mass=sum(k*v for k,v in helper.items()),completion_rank_histogram=compact(completions),restore_transform=receipt)
 raw['five_stage_profile'].update(histogram=compact(five),calls=sum(five.values()),rank_mass=sum(r*n for r,n in five.items()))
 raw['scope']='Fresh complete actual gen5 word after kernel entries and early helper restoration; helper endpoints below FULL are completed by P_sigma + I - P_E.'
 return raw

def rebind_sink(raw,receipt,completions):
 """Complete physical census after terminal sinks: removed zero-to-full helpers free their whole 24-rank path; the
 register count, the stock and the five-stage profile are recomputed and the deficit 4400 is rechecked."""
 from copy import deepcopy
 from pins import pin
 hist=lambda x:Counter({int(k):v for k,v in x.items()if v})
 compact=lambda x:{str(k):v for k,v in sorted(x.items())if v}
 assert receipt['status']=='PASS_GEN5_TERMINAL_SINKS_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS'
 assert receipt['both_reflected_ledgers']and receipt['unchanged_surviving_input_output_frames']and receipt['unchanged_copy_lifetimes']
 k=pin('sink_count',receipt['selected']);R=receipt['physical_R'];assert R==raw['physical_R']-k
 source=hist(receipt['source_histogram']);target=hist(receipt['target_histogram']);internal=hist(receipt['internal_histogram_including_copies']);copies=hist(receipt['copied_center_histogram'])
 assert source==hist(raw['physical_source_histogram'])and copies=={22:24}
 assert sum(r*n for r,n in target.items())==1760*23
 helper=source+target+internal;delta=helper.copy();delta.subtract(hist(raw['one_stage_helper_histogram_including_copies']))
 assert {a:b for a,b in delta.items()if b}==hist(receipt['local_histogram_delta'])==hist(pin('sink_local_delta',{a:b for a,b in delta.items()if b}))
 assert sum(a*b for a,b in helper.items())==raw['helper_rank_mass']-24*k
 completions=Counter(completions);assert completions==hist(raw['completion_rank_histogram']),'sinks are plain helpers: entrances unchanged'
 five=Counter({r:5*n for r,n in helper.items()});five.update(hist(raw['five_stage_profile']['idle_histogram']))
 for c,n in completions.items():five[5*c]+=n
 stock=4*1760+R;mass=sum(r*n for r,n in five.items());assert 120*stock-mass==4400,'terminal sinks keep the five-stage deficit'
 pin('sink_five_stage_calls',sum(five.values()));pin('sink_five_stage_rank_mass',mass)
 without=internal.copy();without.subtract(copies);assert min(without.values())>=0
 before=deepcopy(raw)
 raw.update(schema='gen5-terminal-sinks-fresh-ledger/1',restore_ledger=before,physical_R=R,terminal_sinks=k,physical_target_histogram=compact(target),physical_internal_excluding_center_copies=compact(without),one_stage_helper_histogram_including_copies=compact(helper),helper_rank_mass=sum(a*b for a,b in helper.items()),sink_transform=receipt)
 raw['five_stage_profile'].update(W=stock,histogram=compact(five),calls=sum(five.values()),rank_mass=mass,deficit=120*stock-mass)
 raw['scope']='Fresh complete actual gen5 word after kernel entries, early restoration and terminal sinks.'
 return raw

def rebind_descent2(raw,receipt,completions):
 """Complete physical census after the post-sink concave-descent retiming: rank mass, registers, stock, entrances and
 endpoints are unchanged; only the one-stage histogram regroups, so the five-stage deficit 4400 is rechecked."""
 from copy import deepcopy
 from pins import pin
 hist=lambda x:Counter({int(k):v for k,v in x.items()if v})
 compact=lambda x:{str(k):v for k,v in sorted(x.items())if v}
 assert receipt['status']=='PASS_POST_SINK_CONCAVE_DESCENT_RETIMING_AND_BOTH_REFLECTED_LEDGERS'
 assert receipt['both_reflected_ledgers']and receipt['unchanged_all_input_output_frames']and receipt['unchanged_helper_endpoints']and receipt['unchanged_copy_lifetimes']and receipt['operand_source_spans_contained']
 assert raw['schema']=='gen5-terminal-sinks-fresh-ledger/1'and 'sink_transform'in raw
 pin('descent2_selected_gates',receipt['selected_gate_count']);pin('descent2_removed_calls',receipt['removed_calls']);pin('descent2_new_bases',receipt['new_bases'])
 assert receipt['scalar']['forward']['all_sources_and_dirty_restored']and receipt['scalar']['inverse']['all_sources_and_dirty_restored']
 source=hist(receipt['source_histogram']);target=hist(receipt['target_histogram']);internal=hist(receipt['internal_histogram_including_copies']);copies=hist(receipt['copied_center_histogram'])
 assert copies==hist(raw['paid_center_copy_histogram'])=={22:24}
 helper=source+target+internal;delta=helper.copy();delta.subtract(hist(raw['one_stage_helper_histogram_including_copies']))
 assert {a:b for a,b in delta.items()if b}==hist(receipt['local_histogram_delta'])==hist(pin('descent2_local_delta',{a:b for a,b in delta.items()if b}))
 # Source, target and internal paths may each regroup; every endpoint mass and the total rank mass are retained exactly.
 assert sum(r*n for r,n in source.items())==sum(r*n for r,n in hist(raw['physical_source_histogram']).items())==1760*23
 assert sum(r*n for r,n in target.items())==sum(r*n for r,n in hist(raw['physical_target_histogram']).items())==1760*23
 assert sum(a*b for a,b in helper.items())==raw['helper_rank_mass']and sum(helper.values())==sum(hist(raw['one_stage_helper_histogram_including_copies']).values())-receipt['removed_calls']
 completions=Counter(completions);assert completions==hist(raw['completion_rank_histogram']),'retiming keeps every entrance'
 five=Counter({r:5*n for r,n in helper.items()});five.update(hist(raw['five_stage_profile']['idle_histogram']))
 for c,n in completions.items():five[5*c]+=n
 stock=4*1760+raw['physical_R'];mass=sum(r*n for r,n in five.items());assert stock==raw['five_stage_profile']['W'] and mass==raw['five_stage_profile']['rank_mass'] and 120*stock-mass==4400,'retiming keeps the five-stage deficit'
 pin('descent2_five_stage_calls',sum(five.values()))
 without=internal.copy();without.subtract(copies);assert min(without.values())>=0
 before=deepcopy(raw)
 raw.update(schema='gen5-post-sink-descent-fresh-ledger/1',sink_ledger=before,physical_source_histogram=compact(source),physical_target_histogram=compact(target),physical_internal_excluding_center_copies=compact(without),one_stage_helper_histogram_including_copies=compact(helper),descent2_transform=receipt)
 raw['five_stage_profile'].update(histogram=compact(five),calls=sum(five.values()))
 raw['scope']='Fresh complete actual gen5 word after kernel entries, early restoration, terminal sinks and a second (post-sink) concave-descent retiming.'
 return raw

def rebind_reorder(raw,receipt,completions,tag='reorder'):
 """Complete physical census after the reordering stage: the same registers, endpoints and rank mass; only the split
 of the paid paths changes. The five-stage profile is recomputed and the deficit 4400 is rechecked."""
 from copy import deepcopy
 from pins import pin
 hist=lambda x:Counter({int(k):v for k,v in x.items()if v})
 compact=lambda x:{str(k):v for k,v in sorted(x.items())if v}
 assert receipt['status']=='PASS_GEN5_REORDER_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS'
 assert receipt['tag']==tag and receipt['all_gate_frames_contain_operand_source_spans'] and receipt['both_reflected_ledgers']and receipt['unchanged_endpoints']and receipt['unchanged_copy_lifetimes']and receipt['integer_replay']['identical']
 k=pin(tag+'_count',receipt['selected']);R=raw['physical_R']
 source=hist(receipt['source_histogram']);target=hist(receipt['target_histogram']);internal=hist(receipt['internal_histogram_including_copies']);copies=hist(receipt['copied_center_histogram'])
 assert copies=={22:24}
 assert sum(r*n for r,n in target.items())==1760*23
 helper=source+target+internal;delta=helper.copy();delta.subtract(hist(raw['one_stage_helper_histogram_including_copies']))
 assert {a:b for a,b in delta.items()if b}==hist(receipt['local_histogram_delta'])==hist(pin(tag+'_local_delta',{a:b for a,b in delta.items()if b}))
 assert sum(a*b for a,b in helper.items())==raw['helper_rank_mass'],'reordering keeps the rank mass'
 completions=Counter(completions);assert completions==hist(raw['completion_rank_histogram']),'reordering keeps every entrance and endpoint'
 five=Counter({r:5*n for r,n in helper.items()});five.update(hist(raw['five_stage_profile']['idle_histogram']))
 for c,n in completions.items():five[5*c]+=n
 stock=4*1760+R;mass=sum(r*n for r,n in five.items());assert 120*stock-mass==4400,'reordering keeps the five-stage deficit'
 pin(tag+'_five_stage_calls',sum(five.values()));pin(tag+'_five_stage_rank_mass',mass)
 without=internal.copy();without.subtract(copies);assert min(without.values())>=0
 before=deepcopy(raw)
 raw.update(schema='gen5-'+tag+'-fresh-ledger/1',**{'before_'+tag+'_ledger':before,tag+'_transform':receipt},physical_source_histogram=compact(source),physical_target_histogram=compact(target),physical_internal_excluding_center_copies=compact(without),one_stage_helper_histogram_including_copies=compact(helper),helper_rank_mass=sum(a*b for a,b in helper.items()))
 raw['five_stage_profile'].update(W=stock,histogram=compact(five),calls=sum(five.values()),rank_mass=mass,deficit=120*stock-mass)
 raw['scope']='Fresh complete actual gen5 word after kernel entries, early restoration, terminal sinks, post-sink descent and reordering.'
 return raw
