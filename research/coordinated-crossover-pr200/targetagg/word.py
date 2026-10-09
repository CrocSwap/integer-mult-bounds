def replay(mode='F2',direction=1,bits=24,mutation=None):
 major=mode=='bound';binary=mode=='F2';v=W.v
 unit=(lambda i:1)if major else(lambda i:1<<i)if binary else(lambda i:1<<(bits*i))
 def add(x,c,y):return x+abs(c)*y if major else x^y if binary and c&1 else x if binary else x+c*y
 target_frames=[None]*v;target_paths=[[]for _ in range(v)];center_reads=[];target_hist=Counter()
 aggregation_active=[True]*len(agg);aggregation_read=[set()for _ in agg];aggregation_restores=[];aggregation_pivot_reads=0
 def target_move(t,f):
  previous=target_frames[t];assert previous is None or C.sub(previous,f),('actual target chronology',t,previous,f)
  assert all(W.module.dot(C.cov[t],b)==0 for b in C.B[f]),('actual target cap',t,f)
  d=C.dimf[f]-(0 if previous is None else C.dimf[previous]);assert d>=0
  if d:target_hist[d]+=1
  target_frames[t]=f;target_paths[t].append(f)
 X0=[unit(i)for i in range(v)];Y0=[unit(v+i)for i in range(v)];Z0={r:unit(idx[r])for r in regs};x=X0[:];y=Y0[:];z=Z0.copy();top=1;done=[]
 def track(value):
  nonlocal top
  if major:top=max(top,value)
  return value
 def value(s):
  s=W.phys[s];return x[borrow[s]]if s in borrow else z[s]
 def assign(s,val):
  s=W.phys[s]
  if s in borrow:x[borrow[s]]=track(val)
  else:z[s]=track(val)
 responses=W.adjoint() if mutation=='old_adjoint' else adj
 def aggregate_restore(k,trigger):
  if not aggregation_active[k]:return
  group=agg[k];pivot=group['pivot'];assert aggregation_read[k]==set(group['roles']),('early aggregation inverse',k,trigger,aggregation_read[k])
  for t in group['targets']:target_move(t,group['frame'])
  if mutation!='omit_aggregation_inverse' or k!=39:
   for t in group['targets']:
    if t!=pivot:y[t]=track(add(y[t],1,y[pivot]))
  aggregation_active[k]=False;aggregation_restores.append(dict(group=k,before_role=trigger,frame=group['frame']))
 def read(s):
  nonlocal aggregation_pivot_reads
  if mutation=='omit_gauge_compensation'and s==new_gauge_selection[-1]['role']:return
  if mutation=='omit_extra_compensation'and s==extra_selection[0]['role']:return
  grouped=role_groups.get(s,[])
  for k in sorted({target_group[t]for t in responses[s]if t in target_group}) if s in W.gauge else []:
   if k not in grouped:aggregate_restore(k,s)
  skipped=set()
  for k in grouped:
   group=agg[k];pivot=group['pivot'];assert aggregation_active[k]
   assert set(group['targets'])<=set(responses[s])and len({responses[s][t]for t in group['targets']})==1
   c=responses[s][pivot];target_move(pivot,W.gauge[s]['frame']);y[pivot]=track(add(y[pivot],-direction*c,value(s)))
   if mutation=='repeat_aggregation_read'and k==39:
    t=next(t for t in group['targets']if t!=pivot);target_move(t,W.gauge[s]['frame']);y[t]=track(add(y[t],-direction*c,value(s)))
   skipped.update(group['targets']);aggregation_read[k].add(s);aggregation_pivot_reads+=1
  for t,c in responses[s].items():
   if t in skipped:continue
   if s in W.gauge:target_move(t,W.gauge[s]['frame'])
   else:assert target_frames[t]is None,'initial correction leaves target atD0'
   y[t]=track(add(y[t],-direction*c,value(s)))
 def gate(i,sign):
  a,b,_=W.ops[i];assign(a,add(value(a),sign,value(b)))
 for s in range(W.R):
  if s not in W.gauge and s not in borrow and s not in removed:read(s)
 for n,s in W.source.items():assign(s,add(value(s),1,x[n]))
 for r in gauge_selection:
  if mutation=='omit_extra_mix'and r is extra_selection[0]:continue
  if mutation!='omit_gauge_mix' or r is not new_gauge_selection[-1]:x[r['partner']]=track(add(x[r['partner']],1,x[r['source']]))
 def forward(i):
  if i not in omitted:gate(i,1);done.append(i)
 for k in schedule['center_prefix_events']:
  event=schedule['events'][k];i=event['op']
  if event['kind']=='early_mix':
   r=early[i];a,b=r['partner'],r['source']
   if mutation!='omit_early_mix' or r is not selection[0]:x[a]=track(add(x[a],1,x[b]))
  else:forward(i)
 for r,s in zip(W.g['roots'],W.w['rootroles']):
  if r['kind']=='center':
   for t in r['targets']:
    assert all(f is None for f in target_frames),'copied centers scatter before any nonzero target movement'
    center_reads.append((s,t));y[t]=track(add(y[t],direction,value(s)))
 for k,group in enumerate(agg):
  assert all(target_frames[t]is None for t in group['targets']), 'aggregation setup after all D0 center scatters'
  if mutation!='omit_aggregation_setup'or k!=39:
   for t in group['targets']:
    if t!=group['pivot']:y[t]=track(add(y[t],-1,y[group['pivot']]))
 for e in terminal:
  assert all(target_frames[t]is None for t in e['targets']),'terminal setup afterD0center scatter'
  for t in e['targets']:
   if t!=e['pivot']:y[t]=track(add(y[t],-1,y[e['pivot']]))
 for j,i in enumerate(W.rest):
  for s in at[j]:
   if mutation!='late_phase1_gauge' or s not in new_phase_roles:read(s)
  if mutation=='late_phase1_gauge'and j==168:
   for s in sorted(new_phase_roles):read(s)
  if i in bywrite:
   e=bywrite[i];a,b,n=W.ops[i];target_move(e['pivot'],W.opframe[i]);y[e['pivot']]=track(add(y[e['pivot']],direction,value(b)))
  else:forward(i)
  if i in afterwrite:
   e=afterwrite[i]
   for t in e['targets']:
    target_move(t,e['root_frame'])
    if t!=e['pivot']:y[t]=track(add(y[t],1,y[e['pivot']]))
 for s in at[len(W.rest)]:read(s)
 assert not any(aggregation_active),'all quotient inverses precede original side/K reads'
 for j,(r,s)in enumerate(zip(W.g['roots'],W.w['rootroles'])):
  if r['kind']=='side' and j not in deletedroots:
   for t in r['targets']:target_move(t,W.w['root_frame'][j]);y[t]=track(add(y[t],direction,value(s)))
  for e in deliveries[j]:
   a,b=e['carrier'],e['passive']
   if b not in by_source:x[a]=track(add(x[a],1,x[b]))
   for t in e['receivers']:target_move(t,e['deliver_frame']);y[t]=track(add(y[t],direction,x[a]))
 for e in W.k['entries']:
  if e['passive']not in by_source:x[e['carrier']]=track(add(x[e['carrier']],-1,x[e['passive']]))
 if mutation=='undo_before_restore':
  for e in W.k['entries']:
   if e['passive']in by_source:x[e['carrier']]=track(add(x[e['carrier']],-1,x[e['passive']]))
 for i in reversed(done):gate(i,-1)
 if mutation!='undo_before_restore':
  for e in W.k['entries']:
   if e['passive']in by_source:x[e['carrier']]=track(add(x[e['carrier']],-1,x[e['passive']]))
 for n,s in W.source.items():assign(s,add(value(s),-1,x[n]))
 if binary:want=[Y0[t]^X0[t]for t in range(v)]
 else:
  want=Y0[:];cache={}
  for root in W.g['roots']:
   n=root['node']
   if n not in cache:
    mask=C.sup[n];val=0
    while mask:low=mask&-mask;mask-=low;val=add(val,1,X0[low.bit_length()-1])
    cache[n]=val
   for t in root['targets']:want[t]=add(want[t],direction,cache[n])
  for e in W.k['entries']:
   val=add(X0[e['carrier']],1,X0[e['passive']])
   for t in e['receivers']:want[t]=add(want[t],direction,val)
 # Finish every local target at its codimension-one cap, then reverse the exact
 # annihilator stream. All copied-center scatters lie before these movements,
 # hence atD0 forward and atD1 after the complementary movements reverse.
 reflected=Counter()
 for t,chain in enumerate(target_paths):
  assert chain
  d=W.h-1-C.dimf[chain[-1]];assert d>=0
  if d:target_hist[d]+=1
  previous=[C.cov[t]];dimension=1
  for f in reversed(chain):
   assert all(W.module.dot(a,b)==0 for a in previous for b in C.B[f])
   basis=C.A[f];step=len(basis)-dimension;assert step>=0
   if step:reflected[step]+=1
   previous=basis;dimension=len(basis)
  if W.h>dimension:reflected[W.h-dimension]+=1
 assert reflected==target_hist
 assert len(center_reads)==sum(len(r['targets'])for r in W.g['roots']if r['kind']=='center')
 assert sum(k*n for k,n in target_hist.items())==W.v*(W.h-1)
 if major:return max(top,max(a+b for a,b in zip(y,want)),max(z[r]+Z0[r]for r in regs),max(a+b for a,b in zip(x,X0)))
 assert y==want,('wrong targets',mode,[t for t in range(v)if y[t]!=want[t]][:10])
 assert x==X0,('source restoration',mode,[s for s in range(v)if x[s]!=X0[s]][:10])
 assert z==Z0,('dirty restoration',mode)
 return dict(mode=mode,direction=direction,formal_columns=2*v+len(regs),sources=v,targets=v,dirty=len(regs),all_targets=True,all_source_and_dirty_restored=True,copied_center_target_reads=len(center_reads),all_forward_centers_at_D0=True,all_reflected_centers_at_D1=True,actual_target_histogram={str(k):n for k,n in sorted(target_hist.items())},actual_reflected_target_histogram={str(k):n for k,n in sorted(reflected.items())},aggregation_groups=len(agg),aggregation_pivot_reads=aggregation_pivot_reads,aggregation_restores=aggregation_restores)
