"""Scalar prototype: source471 with168 frame-preserving commuting operations retimed after centers.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,sys,importlib.util,time,gc,hashlib
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;D=HERE.parent/'joint';spec=importlib.util.spec_from_file_location('source82',D/'joint_word.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
W=m.Candidate();C=W.C
W.changed_frames=[i for i,(a,b)in enumerate(zip(W.original_opframe,W.opframe))if a!=b]
W.endframe={s:W.opframe[xs[-1]]for s,xs in W.role_ops.items()}
C.decoder();C.geometry();selection=json.loads((HERE.parent/'borrow/selection.json').read_text());new_gauge_selection=json.loads((HERE/'selection.json').read_text());new_gauge_selection=new_gauge_selection['selection']if isinstance(new_gauge_selection,dict)else new_gauge_selection;gauge_selection=json.loads((HERE.parent/'gaugeb/selection.json').read_text())+new_gauge_selection
schedule=json.loads((HERE/'schedule.json').read_text())
original_phase1=W.phase1[:];original_rest=W.rest[:];omitted_for_schedule={r['omit_copy']for r in selection};deferred=schedule['deferred_ops'];assert len(deferred)==168
W.phase1=schedule['new_phase1'];W.rest=deferred+original_rest
assert set(W.phase1)|set(W.rest)|omitted_for_schedule==set(range(len(W.ops)))
assert not(set(W.phase1)&set(W.rest))and not(set(W.phase1+W.rest)&omitted_for_schedule)
W.role_ops=defaultdict(list)
for i in W.phase1+W.rest:
 for role in W.ops[i][:2]:W.role_ops[role].append(i)
pos={i:j for j,i in enumerate(W.rest)};W.first={role:pos.get(ii[0],-1)for role,ii in W.role_ops.items()};W.last={role:pos.get(ii[-1],-1)for role,ii in W.role_ops.items()};W.position={i:j for j,i in enumerate(W.phase1+W.rest)}
W.endframe={role:W.opframe[ii[-1]]for role,ii in W.role_ops.items()}
W.readtime={role:t+168 for role,t in W.readtime.items()};new_phase_roles={8584,9424}
assert new_phase_roles<=set(schedule['new_untouched_roles'])
for role,t in W.readtime.items():W.w['reads'][str(role)]=len(W.phase1)+t
knew={e['passive']:e for e in W.k['entries']};raw_response=W.adjoint();newroles=[];target_frames={};touched={s for i in W.phase1 for s in W.ops[i][:2]}
for r in new_gauge_selection:
 role,source=r['role'],r['source'];mix=knew[source]['mix_frame'];f=W.register(r['gauge_basis'])if 'gauge_basis'in r else mix;targets=sorted(raw_response[role]);assert targets==r['targets'] and mix==r['mix_frame'] and C.sub(mix,f)
 assert role not in W.gauge and role not in W.donor and role not in W.source.values() and role not in touched
 assert C.dimf[f]in(2,4) and C.nondeg(f) and C.sub(f,W.opframe[W.role_ops[role][0]])
 assert all(t not in target_frames or C.sub(target_frames[t],f) and C.sub(f,target_frames[t])for t in targets);target_frames.update({t:f for t in targets})
 assert all(all(W.module.dot(C.cov[t],b)==0 for b in C.B[f])for t in targets)
 z=dict(role=role,frame=f,dim=C.dimf[f],targets=targets);W.gauge[role]=z;W.w['gauges'].append(z);W.readtime[role]=0 if role in new_phase_roles else 168;W.w['reads'][str(role)]=len(W.phase1)+W.readtime[role];newroles.append(role)
W.order=newroles+W.order
W.exact_frames()
assert all(0<=W.readtime[s]<=W.first[s]for s in W.gauge)
assert all(W.last[d]<W.readtime[b]and C.sub(W.endframe[d],W.gauge[b]['frame'])for b,d in W.pairs)
assert all(not(set(W.gauge)&set(W.ops[i][:2]))for i in W.phase1)
print('PASS scalar schedule timing, all gauge/alias readtimes, new source prefix inclusions; independent target/reflected ledger required',flush=True)
borrow={r['role']:r['source']for r in selection};by_source={r['source']:r for r in selection};omitted={r['omit_copy']for r in selection};early={r['early']:r for r in selection};assert len(early)==len(borrow)==len(selection)==440
gauge_borrow={r['role']:r['source']for r in gauge_selection};kpair={e['passive']:e for e in W.k['entries']};used_sources=set(by_source)|{r['partner']for r in selection}
assert len(gauge_borrow)==len(gauge_selection) and len(set(gauge_borrow.values()))==len(gauge_selection)
for r in gauge_selection:
 assert r['source']in kpair and r['partner']==kpair[r['source']]['carrier']
 assert r['role']in W.gauge and r['role']not in W.donor and r['role']not in borrow
 assert r['source']not in used_sources and r['partner']not in used_sources
 used_sources.update([r['source'],r['partner']])
borrow.update(gauge_borrow);by_source.update({r['source']:r for r in gauge_selection})
input_paths=[*W.input_paths,W.framepath,D/'joint_word.py',D/'joint-selection.json',D/'pairs.json',Path(W.module.__file__),D/'joint-replay.json',(HERE/'selection.json'),(HERE.parent/'gaugeb/selection.json'),Path(__file__),HERE/'schedule.json',(HERE.parent/'borrow/selection.json')]
input_pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in input_paths}
adj=[{}for _ in range(W.R)]
for r,s in zip(W.g['roots'],W.w['rootroles']):
 for t in r['targets']:adj[s][t]=adj[s].get(t,0)+1
for i in reversed(W.phase1+W.rest):
 if i in omitted:continue
 a,b,_=W.ops[i]
 for t,c in adj[a].items():adj[b][t]=adj[b].get(t,0)+c
oldadj=W.adjoint()
assert all(all(0<c<=oldadj[s].get(t,0)for t,c in row.items())for s,row in enumerate(adj))
assert all(adj[s]==oldadj[s]for s in W.gauge), 'all gauge reads and paid target supports retained exactly'
assert len(by_source)==440+len(gauge_selection) and all(r['early'] in r['windows']for r in selection)
# The formal column layout excludes each actual borrowed dirty slot, retaining
# distinct original X columns and every other arbitrary dirty input.
terminal=json.loads((D/'joint-replay.json').read_text())['selected'];removed={e['role']for e in terminal};deletedroots={e['root']for e in terminal};bywrite={i:e for e in terminal for i in e['writes']};afterwrite={e['writes'][-1]:e for e in terminal};assert not(set(early)&set(bywrite)) and not(set(borrow)&removed)
regs=sorted(set(W.phys.values())-set(borrow)-removed);idx={r:2*W.v+j for j,r in enumerate(regs)}
assert not set(borrow)&set(W.donor)
at=defaultdict(list)
for b in W.order:at[W.readtime[b]].append(b)
deliveries=defaultdict(list)
for e in W.k['entries']:deliveries[e['deliver_after_root']].append(e)

def replay(mode='F2',direction=1,bits=24,mutation=None):
 major=mode=='bound';binary=mode=='F2';v=W.v
 unit=(lambda i:1)if major else(lambda i:1<<i)if binary else(lambda i:1<<(bits*i))
 def add(x,c,y):return x+abs(c)*y if major else x^y if binary and c&1 else x if binary else x+c*y
 target_frames=[None]*v;target_paths=[[]for _ in range(v)];center_reads=[];target_hist=Counter()
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
 def read(s):
  if mutation=='omit_gauge_compensation' and s==new_gauge_selection[-1]['role']:return
  for t,c in responses[s].items():
   if s in W.gauge:target_move(t,W.gauge[s]['frame'])
   else:assert target_frames[t]is None,'initial correction leaves target atD0'
   y[t]=track(add(y[t],-direction*c,value(s)))
 def gate(i,sign):
  a,b,_=W.ops[i];assign(a,add(value(a),sign,value(b)))
 for s in range(W.R):
  if s not in W.gauge and s not in borrow and s not in removed:read(s)
 for n,s in W.source.items():assign(s,add(value(s),1,x[n]))
 for r in gauge_selection:
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
 return dict(mode=mode,direction=direction,formal_columns=2*v+len(regs),sources=v,targets=v,dirty=len(regs),all_targets=True,all_source_and_dirty_restored=True,copied_center_target_reads=len(center_reads),all_forward_centers_at_D0=True,all_reflected_centers_at_D1=True,actual_target_histogram={str(k):n for k,n in sorted(target_hist.items())},actual_reflected_target_histogram={str(k):n for k,n in sorted(reflected.items())})
if __name__=='__main__':
 start=time.monotonic();out=dict(status='PASS_SCALAR_SOURCE471_RETIMED_PHASE1_GAUGES',selection=selection,gauge_selection=gauge_selection,new_gauge_selection=new_gauge_selection,geometry_and_paid_admission=False)
 out['F2']=replay();print('PASS F2',out['F2'],'seconds',time.monotonic()-start,flush=True)
 bound=replay('bound');bits=8*((bound.bit_length()+2+7)//8);out['bound']=bound;out['bits']=bits;out['terminal_sinks']=len(terminal);print('bound',bound,'bits',bits,flush=True)
 out['integer']=[]
 if True:
  for direction in(1,-1):out['integer'].append(replay('Z',direction,bits));gc.collect();print('PASS integer',direction,'seconds',time.monotonic()-start,flush=True)
 out['controls']={}
 for mutation in ['omit_early_mix','old_adjoint','undo_before_restore','omit_gauge_mix','omit_gauge_compensation','late_phase1_gauge']:
  try:replay(mutation=mutation)
  except AssertionError as error:out['controls'][mutation]=dict(status='REJECTED',error=str(error))
  else:raise AssertionError('Invalid mutation accepted: '+mutation)
 assert (1<<bits)>2*bound
 assert input_pins=={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in input_paths}
 out['input_pins']=input_pins
 (HERE/'replay.json').write_text(json.dumps(out,indent=2)+'\n')
 print('PASS actual471 source word, both integer signs, all columns and six controls',flush=True)
